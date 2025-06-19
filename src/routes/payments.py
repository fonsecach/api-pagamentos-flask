from flask import Blueprint, jsonify, request, send_file
from src.services.pix import Pix
from src.models.payment import Payment
from src.repository.database import db
import os

bp = Blueprint('payments', __name__)
pix_service = Pix()

@bp.route('/')
def index():
    return jsonify({'message': 'Hello from api-pagamentos-flask!'})

@bp.route('/pix', methods=['POST'])
def create_payment_pix():
    data = request.get_json()
    result = pix_service.create_payment(data)

    if 'error' in result:
        return jsonify({'error': result['error']}), result.get('status_code', 400)

    response = jsonify({
        'message': result['message'],
        'payment': result['payment']
    })
    response.status_code = result['status_code']
    response.headers['Location'] = result['location']
    return response

@bp.route('/pix/qr/<string:qr_code_filename>', methods=['GET'])
def get_qr_code(qr_code_filename):
    payment = db.session.query(Payment).filter_by(qr_code=qr_code_filename).first()
    if not payment:
        return jsonify({'error': 'File not found'}), 404

    # Construct the full file path
    file_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'img', qr_code_filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path, mimetype="image/png")

# @bp.route('/pix/confirmation', methods=['POST'])
# def confirm_payment_pix():
#     data = request.get_json()
#     payment = db.session.get(Payment, data.get('payment_id'))
#     if not payment:
#         return jsonify({'error': 'Payment not found'}), 404
#     payment.paid = True
#     payment.payment_date = datetime.utcnow()
#     db.session.commit()
#     return jsonify({'message': 'Payment confirmed successfully!'})

# @bp.route('/pix/<int:payment_id>', methods=['GET'])
# def get_payment_pix(payment_id):
#     payment = db.session.get(Payment, payment_id)
#     if not payment:
#         return jsonify({'error': 'Payment not found'}), 404
#     return jsonify({
#         'id': payment.id,
#         'value': payment.value,
#         'paid': payment.paid,
#         'bank_payment_id': payment.bank_payment_id,
#         'qr_code': payment.qr_code,
#         'payment_date': payment.payment_date.isoformat() if payment.payment_date else None,
#         'expiration_date': payment.expiration_date.isoformat() if payment.expiration_date else None
#     })
