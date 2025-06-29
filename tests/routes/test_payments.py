import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app
from src.repository.database import db
from src.extensions import socketio
from src.models.payment import Payment


class TestPaymentsRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('src.routes.payments.pix_service.create_payment')
    def test_create_payment_pix_success(self, mock_create_payment):
        """Test successful PIX payment creation."""
        # Arrange
        mock_create_payment.return_value = {
            'message': 'Payment created successfully!',
            'payment': {'id': 1, 'value': 100.0, 'qr_code': 'test.png'},
            'status_code': 201,
            'location': '/payments/pix/1'
        }
        
        # Act
        response = self.client.post(
            '/payments/pix', 
            data=json.dumps({'value': 100.0}), 
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.location, '/payments/pix/1')
        json_data = response.get_json()
        self.assertEqual(json_data['message'], 'Payment created successfully!')

    @patch('src.routes.payments.pix_service.create_payment')
    def test_create_payment_pix_error(self, mock_create_payment):
        """Test PIX payment creation with invalid data."""
        # Arrange
        mock_create_payment.return_value = {
            'error': 'Invalid data', 
            'status_code': 400
        }
        
        # Act
        response = self.client.post(
            '/payments/pix', 
            data=json.dumps({}), 
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 400)
        json_data = response.get_json()
        self.assertEqual(json_data['error'], 'Invalid data')

    @patch('src.routes.payments.db.session.query')
    @patch('src.routes.payments.send_file')
    @patch('os.path.exists')
    def test_get_qr_code_success(self, mock_exists, mock_send_file, mock_query):
        """Test successful QR code retrieval."""
        # Arrange
        mock_payment = MagicMock()
        mock_query.return_value.filter_by.return_value.first.return_value = mock_payment
        mock_send_file.return_value = 'file_sent'
        mock_exists.return_value = True
        
        # Act
        response = self.client.get('/payments/pix/qr_code/test.png')
        
        # Assert
        self.assertEqual(response, 'file_sent')

    def test_get_qr_code_not_found(self):
        """Test QR code retrieval for non-existent file."""
        # Act
        response = self.client.get('/payments/pix/qr_code/non_existent.png')
        
        # Assert
        self.assertEqual(response.status_code, 404)

    @patch.object(socketio, 'emit')
    def test_confirm_payment_pix_success(self, mock_emit):
        """Test successful PIX payment confirmation."""
        # Arrange
        payment = Payment(bank_payment_id='123', value=100.0, paid=False)
        db.session.add(payment)
        db.session.commit()
        
        # Act
        response = self.client.post(
            '/payments/pix/confirmation', 
            data=json.dumps({'bank_payment_id': '123', 'value': 100.0}), 
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertEqual(json_data['message'], 'Payment confirmed successfully!')
        mock_emit.assert_called_once_with('Payment_confirmed', {'payment_id': payment.id})

    def test_confirm_payment_pix_not_found(self):
        """Test PIX payment confirmation for non-existent payment."""
        # Act
        response = self.client.post(
            '/payments/pix/confirmation', 
            data=json.dumps({'bank_payment_id': '456'}), 
            content_type='application/json'
        )
        
        # Assert
        self.assertEqual(response.status_code, 404)

    def test_get_payment_pix_paid(self):
        """Test retrieval of paid PIX payment."""
        # Arrange
        payment = Payment(id=1, paid=True, qr_code='test.png')
        db.session.add(payment)
        db.session.commit()
        
        # Act
        response = self.client.get('/payments/pix/1')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'confirmed_payment.html', response.data)

    def test_get_payment_pix_not_paid(self):
        """Test retrieval of unpaid PIX payment."""
        # Arrange
        payment = Payment(id=2, paid=False, value=150.0, qr_code='test2.png')
        db.session.add(payment)
        db.session.commit()
        
        # Act
        response = self.client.get('/payments/pix/2')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'payment.html', response.data)


if __name__ == '__main__':
    unittest.main()
