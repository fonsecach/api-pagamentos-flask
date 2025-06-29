from flask import Blueprint, jsonify, render_template, request, send_file
from src.services.pix import Pix
from src.models.payment import Payment
from src.repository.database import db
from src.extensions import socketio
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


@bp.route('/pix/qr_code/<string:qr_code_filename>', methods=['GET'])
def get_qr_code(qr_code_filename):
    payment = db.session.query(Payment).filter_by(qr_code=qr_code_filename).first()
    if not payment:
        return jsonify({'error': 'File not found'}), 404

    # Construct the full file path
    file_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'img', qr_code_filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path, mimetype="image/png")

@bp.route('/pix/confirmation', methods=['POST'])
def confirm_payment_pix():
    data = request.get_json()
    
    if 'bank_payment_id' not in data:
        return jsonify({'error': 'bank_payment_id is required'}), 400
    
    payment = Payment.query.filter_by(bank_payment_id=data.get('bank_payment_id')).first()
    if not payment or payment.paid:
        return jsonify({'error': 'Payment not found'}), 404
    
    if data.get('value')!= payment.value:
        return jsonify({'error': 'Invalid payment data'}), 400
    
    payment.paid = True
    db.session.commit()
    socketio.emit('Payment_confirmed', {'payment_id': payment.id})
    return jsonify({'message': 'Payment confirmed successfully!'})


@bp.route('/pix/<int:payment_id>', methods=['GET'])
def get_payment_pix(payment_id):
    payment = Payment.query.get(payment_id)
    
    if not payment:
        return render_template('404.html', message='Payment not found'), 404
    
    if payment.paid:
        return render_template('confirmed_payment.html', qr_code=payment.qr_code)
    
    return render_template('payment.html',
                            payment_id=payment.id,
                            value=payment.value,
                            qr_code=payment.qr_code)

# websocket event
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
