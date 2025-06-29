import hashlib
import uuid
import qrcode
import os
from datetime import datetime, timedelta
from src.models.payment import Payment
from src.repository.database import db

class Pix:
    def __init__(self):
        pass

    def create_payment(self, data):
        # Verifica se o campo 'value' existe
        if 'value' not in data:
            return {'error': 'Missing value field'}, 400
        # Verifica se o valor é numérico
        try:
            value = float(data['value'])
        except (ValueError, TypeError):
            return {'error': 'Invalid value type'}, 400
        # Verifica se o valor é positivo
        if value <= 0:
            return {'error': 'Value must be greater than zero'}, 400

        expiration_date = datetime.now() + timedelta(minutes=30)

        # Generate a unique identifier using UUID and hash
        hash_id = str(uuid.uuid4())
        hash_object = hashlib.sha256(hash_id.encode())
        qr_data = hash_object.hexdigest()

        # Generate QR code
        qr = qrcode.make(qr_data)

        # Define the file path for saving the QR code
        static_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'img')
        os.makedirs(static_dir, exist_ok=True)
        qr_code_filename = f"{hash_id}.png"
        qr_code_path = os.path.join(static_dir, qr_code_filename)

        # Save the QR code to a file
        qr.save(qr_code_path)

        
        new_payment = Payment(
            value=value,
            bank_payment_id=data.get('bank_payment_id'),
            qr_code=qr_code_filename,
            expiration_date=expiration_date
        )

        try:
            db.session.add(new_payment)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'error': 'Database error', 'details': str(e)}, 500

        return {
            'message': 'Payment created successfully!',
            'payment': new_payment.to_dict(),
            'status_code': 201,
            'location': f'/pix/{new_payment.id}'
        }