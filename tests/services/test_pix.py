import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.services.pix import Pix
from src.models.payment import Payment


class TestPix(unittest.TestCase):
    """Test cases for PIX service."""

    @patch('src.services.pix.db')
    @patch('src.services.pix.qrcode')
    @patch('src.services.pix.os.makedirs')
    @patch('src.services.pix.os.path.join')
    def test_create_payment_success(self, mock_path_join, mock_makedirs, mock_qrcode, mock_db):
        """Test successful payment creation."""
        # Arrange
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_path_join.return_value = '/tmp/qr_code.png'
        mock_qr_image = MagicMock()
        mock_qrcode.make.return_value = mock_qr_image
        
        pix_service = Pix()
        data = {'value': 100.0}
        
        # Act
        result = pix_service.create_payment(data)
        
        # Assert
        self.assertEqual(result['status_code'], 201)
        self.assertEqual(result['message'], 'Payment created successfully!')
        self.assertIn('payment', result)
        self.assertIn('location', result)
        
        # Verify method calls
        mock_makedirs.assert_called_once()
        mock_qrcode.make.assert_called_once()
        mock_qr_image.save.assert_called_once_with('/tmp/qr_code.png')
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_create_payment_no_value(self):
        """Test payment creation without value field."""
        # Arrange
        pix_service = Pix()
        data = {}
        
        # Act
        result = pix_service.create_payment(data)
        
        # Assert
        if isinstance(result, tuple):
            result, status_code = result
            self.assertEqual(status_code, 400)
            self.assertEqual(result['error'], 'Missing value field')
        else:
            self.assertEqual(result['status_code'], 400)
            self.assertEqual(result['error'], 'Missing value field')

    def test_create_payment_invalid_value_type(self):
        """Test payment creation with invalid value type."""
        # Arrange
        pix_service = Pix()
        data = {'value': 'invalid'}
        
        # Act
        result = pix_service.create_payment(data)
        
        # Assert
        if isinstance(result, tuple):
            result, status_code = result
            self.assertEqual(status_code, 400)
            self.assertEqual(result['error'], 'Invalid value type')
        else:
            self.assertEqual(result['status_code'], 400)
            self.assertEqual(result['error'], 'Invalid value type')

    @patch('src.services.pix.db')
    @patch('src.services.pix.qrcode')
    @patch('src.services.pix.os.makedirs')
    @patch('src.services.pix.os.path.join')
    def test_create_payment_db_error(self, mock_path_join, mock_makedirs, mock_qrcode, mock_db):
        """Test payment creation with database error."""
        # Arrange
        mock_session = MagicMock()
        mock_session.commit.side_effect = Exception('DB error')
        mock_db.session = mock_session
        mock_path_join.return_value = '/tmp/qr_code.png'
        mock_qr_image = MagicMock()
        mock_qrcode.make.return_value = mock_qr_image
        
        pix_service = Pix()
        data = {'value': 100.0}
        
        # Act
        result = pix_service.create_payment(data)
        
        # Assert
        if isinstance(result, tuple):
            result, status_code = result
            self.assertEqual(status_code, 500)
            self.assertEqual(result['error'], 'Database error')
            self.assertIn('details', result)
        else:
            self.assertEqual(result['status_code'], 500)
            self.assertEqual(result['error'], 'Database error')
            self.assertIn('details', result)
        
        mock_session.rollback.assert_called_once()

    def test_create_payment_zero_value(self):
        """Test payment creation with zero value."""
        # Arrange
        pix_service = Pix()
        data = {'value': 0}
        
        # Act
        result = pix_service.create_payment(data)
        
        # Assert
        if isinstance(result, tuple):
            result, status_code = result
            self.assertEqual(status_code, 400)
        else:
            self.assertEqual(result['status_code'], 400)

    def test_create_payment_negative_value(self):
        """Test payment creation with negative value."""
        # Arrange
        pix_service = Pix()
        data = {'value': -100.0}
        
        # Act
        result = pix_service.create_payment(data)
        
        # Assert
        if isinstance(result, tuple):
            result, status_code = result
            self.assertEqual(status_code, 400)
        else:
            self.assertEqual(result['status_code'], 400)


if __name__ == '__main__':
    unittest.main()
