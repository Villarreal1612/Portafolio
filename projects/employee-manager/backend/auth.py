from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from models import User

def generate_token(user_data):
    """Generar token JWT para el usuario"""
    payload = {
        'user_id': user_data['id'],
        'username': user_data['username'],
        'role': user_data['role'],
        'exp': datetime.utcnow() + timedelta(hours=24)  # Token válido por 24 horas
    }
    
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """Verificar y decodificar token JWT"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorador para rutas que requieren autenticación"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Buscar token en headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Token inválido'}), 401
        
        if not token:
            return jsonify({'message': 'Token requerido'}), 401
        
        try:
            data = verify_token(token)
            if data is None:
                return jsonify({'message': 'Token inválido o expirado'}), 401
            
            current_user = data
            
        except Exception as e:
            return jsonify({'message': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorador para rutas que requieren rol de administrador"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token inválido'}), 401
        
        if not token:
            return jsonify({'message': 'Token requerido'}), 401
        
        try:
            data = verify_token(token)
            if data is None:
                return jsonify({'message': 'Token inválido o expirado'}), 401
            
            if data['role'] != 'admin':
                return jsonify({'message': 'Permisos de administrador requeridos'}), 403
            
            current_user = data
            
        except Exception as e:
            return jsonify({'message': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def login_user(username, password):
    """Función para autenticar usuario y generar token"""
    user_model = User()
    user = user_model.authenticate(username, password)
    
    if user:
        token = generate_token(user)
        return {
            'success': True,
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }
    else:
        return {'success': False, 'message': 'Credenciales inválidas'}

def register_user(username, email, password, role='user'):
    """Función para registrar nuevo usuario"""
    user_model = User()
    result = user_model.create_user(username, email, password, role)
    
    if result['success']:
        # Autenticar automáticamente después del registro
        return login_user(username, password)
    else:
        return result