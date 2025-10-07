#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación principal del Portafolio
Punto de entrada único para todos los proyectos
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
import os
import sys
from datetime import datetime

# Importar la base de datos unificada
from database import PortfolioDatabase

# Configuración de la aplicación
app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
CORS(app)

# Inicializar la base de datos
db = PortfolioDatabase()

@app.route('/')
def index():
    """Página principal del portafolio"""
    return render_template('index.html')

# ==================== RUTAS DEL EMPLOYEE MANAGER ====================

@app.route('/api/employees', methods=['GET'])
def get_employees():
    """Obtener todos los empleados"""
    try:
        employees = db.get_all_employees()
        return jsonify({
            'success': True,
            'data': employees
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/employees', methods=['POST'])
def create_employee():
    """Crear un nuevo empleado"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['employee_id', 'first_name', 'last_name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Validar formato de email
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({
                'success': False,
                'error': 'Formato de email inválido'
            }), 400
        
        # Verificar si el email ya existe
        existing_employee = db.get_employee_by_email(data['email'])
        if existing_employee:
            return jsonify({
                'success': False,
                'error': 'Ya existe un empleado con este email. Por favor, use un email diferente.'
            }), 409
        
        # Verificar si el employee_id ya existe
        existing_employee_id = db.get_employee_by_employee_id(data['employee_id'])
        if existing_employee_id:
            return jsonify({
                'success': False,
                'error': 'Ya existe un empleado con este ID. Por favor, use un ID diferente.'
            }), 409
        
        employee_db_id = db.add_employee(
            employee_id=data['employee_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data.get('phone'),
            department=data.get('department'),
            position=data.get('position'),
            salary=data.get('salary', 0),
            hire_date=data.get('hire_date', datetime.now().strftime('%Y-%m-%d')),
            status=data.get('status', 'active')
        )
        
        return jsonify({
            'success': True,
            'message': 'Empleado creado exitosamente',
            'employee_id': employee_db_id
        })
    except Exception as e:
        # Manejo específico para errores de base de datos
        error_message = str(e)
        if 'UNIQUE constraint failed: employees.email' in error_message:
            return jsonify({
                'success': False,
                'error': 'Ya existe un empleado con este email. Por favor, use un email diferente.'
            }), 409
        elif 'UNIQUE constraint failed: employees.employee_id' in error_message:
            return jsonify({
                'success': False,
                'error': 'Ya existe un empleado con este ID. Por favor, use un ID diferente.'
            }), 409
        elif 'UNIQUE constraint failed' in error_message:
            if 'email' in error_message:
                return jsonify({
                    'success': False,
                    'error': 'Ya existe un empleado con este email. Por favor, use un email diferente.'
                }), 409
            elif 'employee_id' in error_message:
                return jsonify({
                    'success': False,
                    'error': 'Ya existe un empleado con este ID. Por favor, use un ID diferente.'
                }), 409
        
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {error_message}'
        }), 500

@app.route('/api/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """Actualizar un empleado"""
    try:
        data = request.get_json()
        success = db.update_employee(employee_id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Empleado actualizado exitosamente',
                'updated_fields': list(data.keys())
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Empleado no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """Eliminar un empleado"""
    try:
        success = db.delete_employee(employee_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Empleado eliminado exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Empleado no encontrado'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== RUTAS DE AUTENTICACIÓN ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Iniciar sesión"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Usuario y contraseña son requeridos'
            }), 400
        
        user = db.authenticate_user(username, password)
        
        if user:
            return jsonify({
                'success': True,
                'message': 'Inicio de sesión exitoso',
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'email': user[2],
                    'role': user[4]
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Credenciales inválidas'
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500



# ==================== RUTAS PARA PERSONAL FINANCE TRACKER ====================

@app.route('/api/finance/categories', methods=['GET'])
def get_categories():
    """Obtener todas las categorías"""
    try:
        categories = db.get_all_categories()
        return jsonify({
            'success': True,
            'data': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/finance/transactions', methods=['POST'])
def add_transaction():
    """Agregar una nueva transacción"""
    try:
        data = request.get_json()
        
        # Validaciones
        required_fields = ['user_id', 'amount', 'type', 'category_id', 'transaction_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Validar tipo de transacción
        if data['type'] not in ['income', 'expense']:
            return jsonify({
                'success': False,
                'error': 'El tipo debe ser "income" o "expense"'
            }), 400
        
        # Validar monto positivo
        if float(data['amount']) <= 0:
            return jsonify({
                'success': False,
                'error': 'El monto debe ser mayor a 0'
            }), 400
        
        transaction_id = db.add_transaction(
            user_id=data['user_id'],
            amount=data['amount'],
            transaction_type=data['type'],
            category_id=data['category_id'],
            description=data.get('description', ''),
            transaction_date=data['transaction_date']
        )
        
        if transaction_id:
            return jsonify({
                'success': True,
                'data': {'transaction_id': transaction_id}
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error al crear la transacción'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/finance/transactions/<int:user_id>', methods=['GET'])
def get_user_transactions(user_id):
    """Obtener transacciones de un usuario con filtros opcionales"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        category_id = request.args.get('category_id')
        
        transactions = db.get_transactions_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            category_id=int(category_id) if category_id else None
        )
        
        return jsonify({
            'success': True,
            'data': transactions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/finance/summary/<int:user_id>/<int:year>/<int:month>', methods=['GET'])
def get_monthly_summary(user_id, year, month):
    """Obtener resumen mensual de un usuario"""
    try:
        # Validar mes
        if month < 1 or month > 12:
            return jsonify({
                'success': False,
                'error': 'El mes debe estar entre 1 y 12'
            }), 400
        
        summary = db.get_monthly_summary(user_id, year, month)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==================== RUTAS DE SALUD Y ESTADO ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar el estado de la aplicación"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Obtener lista de proyectos disponibles"""
    projects = [
        {
            'id': 1,
            'name': 'Employee Manager',
            'description': 'Sistema de gestión de empleados',
            'status': 'active',
            'path': '/projects/employee-manager'
        },
        {
            'id': 2,
            'name': 'Personal Finance Tracker',
            'description': 'Gestor de ingresos y gastos personales',
            'status': 'active',
            'path': '/projects/personal-finance-tracker'
        }
    ]
    
    return jsonify({
        'success': True,
        'data': projects
    })

# ==================== MANEJO DE ERRORES ====================

@app.errorhandler(404)
def not_found(error):
    # Si la ruta solicitada es una API (comienza con /api/), devolver JSON
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Endpoint no encontrado'
        }), 404
    # Para otras rutas, redirigir a la página principal
    else:
        return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500

# ==================== FUNCIÓN PRINCIPAL ====================

# ==================== RUTAS PARA PÁGINAS DE DETALLES DE PROYECTOS ====================

@app.route('/projects/employee-manager/')
def employee_manager_detail():
    """Página de detalles del proyecto Employee Manager"""
    return render_template('projects/employee-manager/employee_manager.html')

@app.route('/projects/employee-manager/employee_manager.html')
def employee_manager_html():
    """Ruta específica para el archivo HTML del Employee Manager"""
    return render_template('projects/employee-manager/employee_manager.html')

@app.route('/projects/personal-finance-tracker/')
def personal_finance_tracker_detail():
    """Página de detalles del proyecto Personal Finance Tracker"""
    return render_template('projects/personal-finance-tracker/personal_finance_tracker.html')

@app.route('/projects/personal-finance-tracker/personal_finance_tracker.html')
def personal_finance_tracker_html():
    """Ruta específica para el archivo HTML del Personal Finance Tracker"""
    return render_template('projects/personal-finance-tracker/personal_finance_tracker.html')

# ==================== RUTAS PARA APLICACIONES FUNCIONALES ====================

@app.route('/projects/employee-manager/frontend/')
def employee_manager_app():
    """Aplicación funcional Employee Manager"""
    return render_template('projects/employee-manager/frontend/index.html')

@app.route('/projects/personal-finance-tracker/frontend/')
def personal_finance_tracker_app():
    """Aplicación funcional Personal Finance Tracker"""
    return render_template('projects/personal-finance-tracker/frontend/index.html')

# Personal Finance Tracker API Routes
@app.route('/api/finance/categories')
def get_finance_categories():
    try:
        categories = get_categories()
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/finance/transactions', methods=['POST'])
def add_finance_transaction():
    try:
        data = request.get_json()
        transaction_id = add_transaction(
            data['user_id'],
            data['amount'],
            data['type'],
            data['category_id'],
            data.get('description', ''),
            data['transaction_date']
        )
        return jsonify({'id': transaction_id, 'message': 'Transacción agregada exitosamente'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/finance/transactions/<int:user_id>')
def get_finance_transactions(user_id):
    try:
        type_filter = request.args.get('type')
        category_filter = request.args.get('category')
        transactions = get_user_transactions(user_id, type_filter, category_filter)
        return jsonify(transactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/finance/summary/<int:user_id>/<int:year>/<int:month>')
def get_finance_summary(user_id, year, month):
    try:
        summary = get_monthly_summary(user_id, year, month)
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Verificar que la base de datos esté inicializada
    print("Inicializando base de datos...")
    db.init_database()
    db.insert_sample_data()
    print("Base de datos inicializada correctamente.")
    
    # Configuración del servidor
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Iniciando servidor en puerto {port}...")
    print(f"Modo debug: {debug_mode}")
    print("Aplicación disponible en: http://localhost:5000")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )