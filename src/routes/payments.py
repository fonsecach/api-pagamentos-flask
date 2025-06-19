from flask import Blueprint, jsonify, request
from datetime import datetime
from src.models.payment import Payment
from src.repository.database import db

bp = Blueprint('payments', __name__)

@bp.route('/')
def index():
    return jsonify({'message': 'Hello from api-pagamentos-flask!'})

@bp.route('/pix', methods=['POST'])
def create_payment_pix():
    data = request.get_json()
    payment = Payment(
        value=data['value'],
        bank_payment_id=data.get('bank_payment_id'),
        qr_code=data.get('qr_code'),
        expiration_date=datetime.strptime(data['expiration_date'], "%Y-%m-%dT%H:%M:%S") if data.get('expiration_date') else None
    )
    db.session.add(payment)
    db.session.commit()
    return jsonify({'message': 'Payment created successfully!', 'payment_id': payment.id}), 201

@bp.route('/pix/confirmation', methods=['POST'])
def confirm_payment_pix():
    data = request.get_json()
    payment = db.session.get(Payment, data.get('payment_id'))
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    payment.paid = True
    payment.payment_date = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Payment confirmed successfully!'})

@bp.route('/pix/<int:payment_id>', methods=['GET'])
def get_payment_pix(payment_id):
    payment = db.session.get(Payment, payment_id)
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    return jsonify({
        'id': payment.id,
        'value': payment.value,
        'paid': payment.paid,
        'bank_payment_id': payment.bank_payment_id,
        'qr_code': payment.qr_code,
        'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
        'expiration_date': payment.expiration_date.isoformat() if payment.expiration_date else None
    })
