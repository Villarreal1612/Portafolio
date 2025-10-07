from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
import io
from models import Employee, User, Database
from auth import token_required, admin_required, login_user, register_user
from utils import import_employees_from_csv, export_employees_to_excel, generate_csv_template, validate_employee_data

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Habilitar CORS para todas las rutas
CORS(app)

# Inicializar base de datos
db = Database()

# Rutas de autenticación
@app.route('/api/auth/login', methods=['POST'])
def login():
    """Endpoint para login de usuario"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Username y password requeridos'}), 400
    
    result = login_user(data['username'], data['password'])
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Endpoint para registro de usuario"""
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'message': 'Username, email y password requeridos'}), 400
    
    result = register_user(
        data['username'], 
        data['email'], 
        data['password'], 
        data.get('role', 'user')
    )
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

# Rutas de empleados
@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Obtener lista de empleados con paginación y filtros"""
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    search = request.args.get('search', '')
    filter_estado = request.args.get('estado', '')
    
    employee_model = Employee()
    result = employee_model.get_all(page, per_page, search, filter_estado)
    
    return jsonify(result), 200

@app.route('/api/employees/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    """Obtener un empleado específico"""
    employee_model = Employee()
    employee = employee_model.get_by_id(employee_id)
    
    if employee:
        return jsonify(employee), 200
    else:
        return jsonify({'message': 'Empleado no encontrado'}), 404

@app.route('/api/employees', methods=['POST'])
def create_employee():
    """Crear nuevo empleado"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Datos requeridos'}), 400
    
    # Validar datos
    errors = validate_employee_data(data)
    if errors:
        return jsonify({'message': 'Errores de validación', 'errors': errors}), 400
    
    employee_model = Employee()
    result = employee_model.create(data)
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """Actualizar empleado existente"""
    data = request.get_json()
    
    if not data:
        return jsonify({'message': 'Datos requeridos'}), 400
    
    # Validar datos
    errors = validate_employee_data(data)
    if errors:
        return jsonify({'message': 'Errores de validación', 'errors': errors}), 400
    
    employee_model = Employee()
    result = employee_model.update(employee_id, data)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Eliminar empleado (solo administradores)"""
    employee_model = Employee()
    result = employee_model.delete(employee_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 404

# Rutas de importación/exportación
@app.route('/api/employees/import', methods=['POST'])
@admin_required
def import_employees(current_user):
    """Importar empleados desde CSV"""
    if 'file' not in request.files:
        return jsonify({'message': 'Archivo requerido'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'Archivo requerido'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'message': 'Solo archivos CSV permitidos'}), 400
    
    try:
        csv_content = file.read().decode('utf-8')
        result = import_employees_from_csv(csv_content)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'message': f'Error procesando archivo: {str(e)}'}), 400

@app.route('/api/employees/export', methods=['GET'])
@token_required
def export_employees(current_user):
    """Exportar empleados a Excel"""
    # Obtener parámetros de filtro
    search = request.args.get('search', '')
    filter_estado = request.args.get('estado', '')
    
    employee_model = Employee()
    # Obtener todos los empleados que coincidan con los filtros
    result = employee_model.get_all(page=1, per_page=10000, search=search, filter_estado=filter_estado)
    
    if not result['employees']:
        return jsonify({'message': 'No hay empleados para exportar'}), 404
    
    excel_data = export_employees_to_excel(result['employees'])
    
    if excel_data:
        # Crear archivo en memoria
        output = io.BytesIO(excel_data)
        output.seek(0)
        
        filename = f'empleados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
    else:
        return jsonify({'message': 'Error generando archivo Excel'}), 500

@app.route('/api/employees/template', methods=['GET'])
@token_required
def download_template(current_user):
    """Descargar plantilla CSV para importación"""
    template_content = generate_csv_template()
    
    output = io.StringIO(template_content)
    output.seek(0)
    
    return send_file(
        io.BytesIO(template_content.encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='plantilla_empleados.csv'
    )

# Ruta para servir archivos estáticos del frontend
@app.route('/')
def serve_frontend():
    """Servir página principal del frontend"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Servir archivos estáticos del frontend"""
    return send_from_directory('../frontend', path)

# Ruta de información de la API
@app.route('/api/info', methods=['GET'])
def api_info():
    """Información básica de la API"""
    return jsonify({
        'name': 'Employee Manager API',
        'version': '1.0.0',
        'description': 'API REST para gestión de empleados',
        'endpoints': {
            'auth': [
                'POST /api/auth/login',
                'POST /api/auth/register'
            ],
            'employees': [
                'GET /api/employees',
                'GET /api/employees/<id>',
                'POST /api/employees',
                'PUT /api/employees/<id>',
                'DELETE /api/employees/<id>'
            ],
            'import_export': [
                'POST /api/employees/import',
                'GET /api/employees/export',
                'GET /api/employees/template'
            ]
        }
    }), 200

# Manejo de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    # Crear directorio de base de datos si no existe
    os.makedirs('../database', exist_ok=True)
    
    # Ejecutar aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)