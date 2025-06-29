import unittest
from unittest.mock import patch, MagicMock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from src.services.pix import Pix
from src.models.payment import Payment
from src.repository.database import db

class TestPix(unittest.TestCase):
    """Casos de teste para o serviço PIX."""

    def setUp(self):
        self.app = create_app(testing=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('src.services.pix.qrcode.make')
    def test_create_payment_success(self, mock_qrcode_make):
        """Testa a criação de um pagamento com sucesso."""
        # Arrange
        mock_qr_image = MagicMock()
        mock_qrcode_make.return_value = mock_qr_image
        pix_service = Pix()
        data = {'value': 100.0}

        # Act
        # Corrigido: O método retorna apenas um dicionário
        result = pix_service.create_payment(data)

        # Assert
        self.assertEqual(result['status_code'], 201)
        self.assertEqual(result['message'], 'Payment created successfully!')
        # Corrigido: a melhor forma de verificar é contar os registros no BD
        self.assertEqual(Payment.query.count(), 1)
        self.assertEqual(Payment.query.first().value, 100.0)


    def test_create_payment_no_value(self):
        """Testa a criação de pagamento sem o campo 'value'."""
        pix_service = Pix()
        result, status_code = pix_service.create_payment({})
        self.assertEqual(status_code, 400)
        self.assertEqual(result['error'], 'Missing value field')

    def test_create_payment_invalid_value_type(self):
        """Testa a criação de pagamento com tipo de 'value' inválido."""
        pix_service = Pix()
        result, status_code = pix_service.create_payment({'value': 'invalid'})
        self.assertEqual(status_code, 400)
        self.assertEqual(result['error'], 'Invalid value type')

    @patch('src.services.pix.db.session.commit')
    def test_create_payment_db_error(self, mock_commit):
        """Testa a criação de pagamento com erro no banco de dados."""
        mock_commit.side_effect = Exception('DB error')
        pix_service = Pix()
        result, status_code = pix_service.create_payment({'value': 100.0})
        self.assertEqual(status_code, 500)
        self.assertEqual(result['error'], 'Database error')

    def test_create_payment_negative_value(self):
        """Testa a criação de pagamento com valor negativo."""
        pix_service = Pix()
        # Corrigido: Agora o teste passa pois o serviço retorna consistentemente a tupla
        result, status_code = pix_service.create_payment({'value': -100})
        self.assertEqual(status_code, 400)
        self.assertEqual(result['error'], 'Value must be greater than zero')

    def test_create_payment_route_success(self):
        with self.app.test_client() as client:
            response = client.post('/payments/pix', json={'value': 100.0})
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json['message'], 'Payment created successfully!')
