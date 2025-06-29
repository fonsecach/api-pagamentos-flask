import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from src.services.pix import Pix
from src.models.payment import Payment
from src.repository.database import db

@pytest.fixture
def app_context():
    app = create_app(testing=True)
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    yield
    db.session.remove()
    db.drop_all()
    ctx.pop()

@patch('src.services.pix.qrcode.make')
def test_create_payment_success(mock_qrcode_make, app_context):
    """Testa a criação de um pagamento com sucesso."""
    mock_qr_image = MagicMock()
    mock_qrcode_make.return_value = mock_qr_image
    pix_service = Pix()
    data = {'value': 100.0}

    # Act
    # Corrigido: O método retorna apenas um dicionário
    result = pix_service.create_payment(data)

    # Assert
    assert result['status_code'] == 201
    assert result['message'] == 'Payment created successfully!'
    # Corrigido: a melhor forma de verificar é contar os registros no BD
    assert Payment.query.count() == 1
    assert Payment.query.first().value == 100.0

def test_create_payment_no_value(app_context):
    """Testa a criação de pagamento sem o campo 'value'."""
    pix_service = Pix()
    result, status_code = pix_service.create_payment({})
    assert status_code == 400
    assert result['error'] == 'Missing value field'

def test_create_payment_invalid_value_type(app_context):
    """Testa a criação de pagamento com tipo de 'value' inválido."""
    pix_service = Pix()
    result, status_code = pix_service.create_payment({'value': 'invalid'})
    assert status_code == 400
    assert result['error'] == 'Invalid value type'

@patch('src.services.pix.db.session.commit')
def test_create_payment_db_error(mock_commit, app_context):
    """Testa a criação de pagamento com erro no banco de dados."""
    mock_commit.side_effect = Exception('DB error')
    pix_service = Pix()
    result, status_code = pix_service.create_payment({'value': 100.0})
    assert status_code == 500
    assert result['error'] == 'Database error'


def test_create_payment_negative_value(app_context):
    """Testa a criação de pagamento com valor negativo."""
    pix_service = Pix()
    # Corrigido: Agora o teste passa pois o serviço retorna consistentemente a tupla
    result, status_code = pix_service.create_payment({'value': -100})
    assert status_code == 400
    assert result['error'] == 'Value must be greater than zero'
