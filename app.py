from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import datetime
# Importar la base de datos unificada
from database import PortfolioDatabase

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación principal del Portafolio
Punto de entrada único para todos los proyectos
"""

# Configuración de la aplicación
app = Flask(__name__, template_folder='.')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tu_clave_secreta_aqui')
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
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[4]
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

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Cerrar sesión"""
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Sesión cerrada'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def me():
    """Obtener usuario actual de la sesión"""
    try:
        if 'user_id' in session:
            return jsonify({
                'success': True,
                'user': {
                    'id': session.get('user_id'),
                    'username': session.get('username'),
                    'role': session.get('role')
                }
            })
        return jsonify({'success': False, 'error': 'No autenticado'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# NUEVO: Registro de usuarios
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Registrar un nuevo usuario (admin o cliente)"""
    try:
        data = request.get_json() or {}
        username = (data.get('username') or '').strip()
        email = (data.get('email') or '').strip()
        password = (data.get('password') or '').strip()
        role = (data.get('role') or 'customer').strip()
        # Normaliza rol desde español a sistema
        role_map = {'cliente': 'customer', 'client': 'customer', 'admin': 'admin', 'usuario': 'user', 'user': 'user'}
        role = role_map.get(role.lower(), 'customer')

        if not username or not email or not password:
            return jsonify({'success': False, 'error': 'username, email y password requeridos'}), 400
        if len(username) < 3:
            return jsonify({'success': False, 'error': 'Usuario demasiado corto (mínimo 3)'}), 400
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Contraseña demasiado corta (mínimo 6)'}), 400
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'success': False, 'error': 'Email inválido'}), 400

        # Validaciones previas: case-insensitive y con trim
        if db.get_user_by_username_ci(username):
            return jsonify({'success': False, 'error': 'Usuario ya existe'}), 409
        if db.get_user_by_email_ci(email):
            return jsonify({'success': False, 'error': 'Email ya está en uso'}), 409

        user_id = db.create_user(username, email, password, role)
        if user_id:
            return jsonify({'success': True, 'data': {'id': user_id}}), 201
        else:
            return jsonify({'success': False, 'error': 'No se pudo crear la cuenta'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Genera una contraseña temporal y la asigna al usuario por email"""
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip()
        if not email:
            return jsonify({'success': False, 'error': 'Email requerido'}), 400
        user = db.get_user_by_email_ci(email)
        if not user:
            return jsonify({'success': False, 'error': 'No existe usuario con ese email'}), 404
        import secrets, string
        alphabet = string.ascii_letters + string.digits
        temp = ''.join(secrets.choice(alphabet) for _ in range(10))
        ok = db.set_user_password_by_email(email, temp)
        if not ok:
            return jsonify({'success': False, 'error': 'No se pudo actualizar la contraseña'}), 500
        # En un sistema real, se enviaría por correo. Aquí devolvemos la temporal para el entorno demo.
        return jsonify({'success': True, 'message': 'Se generó una contraseña temporal', 'data': {'temporary_password': temp}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


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
        data = request.get_json() or {}
        
        # Validaciones
        required_fields = ['user_id', 'amount', 'type', 'category_id', 'transaction_date']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {field}'
                }), 400
        
        # Validar tipo de transacción
        if data.get('type') not in ['income', 'expense']:
            return jsonify({
                'success': False,
                'error': 'El tipo debe ser "income" o "expense"'
            }), 400
        
        # Validar monto
        try:
            amount = float(data.get('amount'))
        except (TypeError, ValueError):
            return jsonify({
                'success': False,
                'error': 'El monto debe ser un número válido'
            }), 400
        if amount <= 0:
            return jsonify({
                'success': False,
                'error': 'El monto debe ser mayor a 0'
            }), 400
        
        # Validar category_id
        try:
            category_id = int(data.get('category_id'))
        except (TypeError, ValueError):
            return jsonify({
                'success': False,
                'error': 'category_id inválido'
            }), 400
        if category_id <= 0:
            return jsonify({
                'success': False,
                'error': 'category_id debe ser mayor a 0'
            }), 400
        
        # Validar fecha
        try:
            datetime.strptime(data.get('transaction_date'), '%Y-%m-%d')
        except Exception:
            return jsonify({
                'success': False,
                'error': 'transaction_date debe tener formato YYYY-MM-DD'
            }), 400
        
        transaction_id = db.add_transaction(
            user_id=data['user_id'],
            amount=amount,
            transaction_type=data['type'],
            category_id=category_id,
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

@app.route('/api/finance/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction_route(transaction_id):
    """Actualizar una transacción del usuario"""
    try:
        data = request.get_json() or {}
        user_id = request.args.get('user_id', type=int)
        if not user_id or user_id <= 0:
            return jsonify({'success': False, 'error': 'user_id requerido'}), 400

        # Validaciones opcionales
        if 'type' in data and data['type'] not in ['income', 'expense']:
            return jsonify({'success': False, 'error': 'El tipo debe ser "income" o "expense"'}), 400
        if 'amount' in data:
            try:
                data['amount'] = float(data['amount'])
            except (TypeError, ValueError):
                return jsonify({'success': False, 'error': 'El monto debe ser un número válido'}), 400
            if data['amount'] <= 0:
                return jsonify({'success': False, 'error': 'El monto debe ser mayor a 0'}), 400
        if 'category_id' in data:
            try:
                data['category_id'] = int(data['category_id'])
            except (TypeError, ValueError):
                return jsonify({'success': False, 'error': 'category_id inválido'}), 400
            if data['category_id'] <= 0:
                return jsonify({'success': False, 'error': 'category_id debe ser mayor a 0'}), 400
        if 'transaction_date' in data:
            try:
                datetime.strptime(data['transaction_date'], '%Y-%m-%d')
            except Exception:
                return jsonify({'success': False, 'error': 'transaction_date debe tener formato YYYY-MM-DD'}), 400

        success = db.update_transaction(transaction_id, user_id, data)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Transacción no encontrada o sin cambios'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/finance/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Eliminar una transacción del usuario"""
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id or user_id <= 0:
            return jsonify({'success': False, 'error': 'user_id requerido'}), 400
        deleted = db.delete_transaction(transaction_id, user_id)
        if deleted:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Transacción no encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
        },
        {
            'id': 3,
            'name': 'Mini E-commerce',
            'description': 'Tienda básica con carrito y pedidos',
            'status': 'active',
            'path': '/projects/mini-ecommerce'
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

@app.route('/projects/employee-manager/frontend/')
def employee_manager_frontend():
    return render_template('projects/employee-manager/frontend/index.html')

@app.route('/projects/personal-finance-tracker/')
def personal_finance_tracker_detail():
    """Página de detalles del proyecto Personal Finance Tracker"""
    return render_template('projects/personal-finance-tracker/personal_finance_tracker.html')

@app.route('/projects/personal-finance-tracker/personal_finance_tracker.html')
def personal_finance_tracker_html():
    """Ruta específica para el archivo HTML del Personal Finance Tracker"""
    return render_template('projects/personal-finance-tracker/personal_finance_tracker.html')

@app.route('/projects/personal-finance-tracker/frontend/')
def personal_finance_tracker_frontend():
    return render_template('projects/personal-finance-tracker/frontend/index.html')

# Servir archivos estáticos del frontend (CSS, imágenes, etc.)
@app.route('/projects/personal-finance-tracker/frontend/<path:filename>')
def personal_finance_frontend_static(filename):
    base_dir = os.path.join(os.getcwd(), 'projects', 'personal-finance-tracker', 'frontend')
    return send_from_directory(base_dir, filename)

# Mini E-commerce
@app.route('/projects/mini-ecommerce/')
def mini_ecommerce_detail():
    """Página de detalles del proyecto Mini E-commerce"""
    return render_template('projects/mini-ecommerce/mini_ecommerce.html')

@app.route('/projects/mini-ecommerce/mini_ecommerce.html')
def mini_ecommerce_html():
    """Ruta específica para el archivo HTML del Mini E-commerce"""
    return render_template('projects/mini-ecommerce/mini_ecommerce.html')

# NUEVO: Pantalla de login/registro para Mini E-commerce
@app.route('/projects/mini-ecommerce/login/')
def mini_ecommerce_login():
    return render_template('projects/mini-ecommerce/login/index.html')

@app.route('/projects/mini-ecommerce/admin/')
def mini_ecommerce_admin():
    """Panel admin para Mini E-commerce"""
    return render_template('projects/mini-ecommerce/admin/index.html')

# NUEVO: Catálogo de cliente para Mini E-commerce
@app.route('/projects/mini-ecommerce/frontend/')
def mini_ecommerce_frontend():
    """Catálogo del cliente para Mini E-commerce"""
    return render_template('projects/mini-ecommerce/frontend/index.html')

# ==================== RUTAS API PARA MINI E-COMMERCE ====================

def _require_admin():
    """Verifica que el usuario de la sesión sea admin"""
    role = session.get('role')
    if role == 'admin':
        return True, None
    return False, 'Debe iniciar sesión como administrador'

@app.route('/api/ecommerce/products', methods=['GET'])
def ecommerce_list_products():
    """Listar productos con filtros opcionales: q, category y id"""
    try:
        q = request.args.get('q')
        category = request.args.get('category')
        product_id = request.args.get('id', type=int)
        if product_id:
            product = db.get_product_by_id(product_id)
            products = [product] if product else []
        else:
            products = db.get_products(q, category)
        return jsonify({'success': True, 'data': products})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ecommerce/admin/products', methods=['POST'])
def ecommerce_create_product():
    try:
        data = request.get_json()
        ok, err = _require_admin()
        if not ok:
            return jsonify({'success': False, 'error': err}), 401

        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        stock = data.get('stock', 0)
        image_url = data.get('image_url')
        category = data.get('category')
        if not name or price is None:
            return jsonify({'success': False, 'error': 'name y price son requeridos'}), 400
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            return jsonify({'success': False, 'error': 'price debe ser numérico y stock entero'}), 400

        product_id = db.create_product(name, description, price, stock, image_url, category)
        if not product_id:
            return jsonify({'success': False, 'error': 'No se pudo crear el producto'}), 500
        return jsonify({'success': True, 'data': {'id': product_id}}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ecommerce/admin/products/<int:product_id>', methods=['PUT'])
def ecommerce_update_product(product_id):
    try:
        data = request.get_json()
        ok, err = _require_admin()
        if not ok:
            return jsonify({'success': False, 'error': err}), 401

        # Parsear y validar valores si vienen
        kwargs = {}
        for key in ['name', 'description', 'image_url', 'category']:
            if key in data:
                kwargs[key] = data[key]
        if 'price' in data:
            try:
                kwargs['price'] = float(data['price'])
            except ValueError:
                return jsonify({'success': False, 'error': 'price debe ser numérico'}), 400
        if 'stock' in data:
            try:
                kwargs['stock'] = int(data['stock'])
            except ValueError:
                return jsonify({'success': False, 'error': 'stock debe ser entero'}), 400

        updated = db.update_product(product_id, **kwargs)
        if not updated:
            return jsonify({'success': False, 'error': 'No se pudo actualizar el producto'}), 400
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ecommerce/admin/products/<int:product_id>', methods=['DELETE'])
def ecommerce_delete_product(product_id):
    try:
        ok, err = _require_admin()
        if not ok:
            return jsonify({'success': False, 'error': err}), 401
        deleted = db.delete_product(product_id)
        return jsonify({'success': deleted})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Órdenes (solo admin)
@app.route('/api/ecommerce/admin/orders', methods=['GET'])
def ecommerce_list_orders():
    try:
        ok, err = _require_admin()
        if not ok:
            return jsonify({'success': False, 'error': err}), 401
        orders = db.get_orders()
        return jsonify({'success': True, 'data': orders})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ecommerce/admin/orders/<int:order_id>', methods=['GET'])
def ecommerce_get_order(order_id):
    try:
        ok, err = _require_admin()
        if not ok:
            return jsonify({'success': False, 'error': err}), 401
        order = db.get_order(order_id)
        if not order:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        return jsonify({'success': True, 'data': order})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# -------- Carrito en sesión --------
def _get_cart():
    cart = session.get('cart')
    if not cart:
        cart = {}
        session['cart'] = cart
    return cart

@app.route('/api/ecommerce/cart', methods=['GET'])
def ecommerce_get_cart():
    try:
        cart = _get_cart()
        # Construir items con detalles de producto
        items = []
        subtotal = 0.0
        for pid_str, qty in cart.items():
            pid = int(pid_str)
            product = db.get_product_by_id(pid)
            if product:
                line_total = float(product['price']) * int(qty)
                subtotal += line_total
                items.append({
                    'product_id': product['id'],
                    'name': product['name'],
                    'price': float(product['price']),
                    'quantity': int(qty),
                    'stock': int(product['stock']),
                    'image_url': product['image_url'],
                    'line_total': round(line_total, 2)
                })
        return jsonify({'success': True, 'data': {'items': items, 'subtotal': round(subtotal, 2)}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ecommerce/cart/add', methods=['POST'])
def ecommerce_cart_add():
    try:
        data = request.get_json()
        pid = int(data.get('product_id'))
        qty = int(data.get('quantity', 1))
        if qty <= 0:
            return jsonify({'success': False, 'error': 'Cantidad inválida'}), 400
        product = db.get_product_by_id(pid)
        if not product:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        if qty > int(product['stock']):
            return jsonify({'success': False, 'error': 'Stock insuficiente'}), 400
        cart = _get_cart()
        cart[str(pid)] = cart.get(str(pid), 0) + qty
        session['cart'] = cart
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ecommerce/cart/update', methods=['POST'])
def ecommerce_cart_update():
    try:
        data = request.get_json()
        pid = int(data.get('product_id'))
        qty = int(data.get('quantity', 1))
        cart = _get_cart()
        if qty <= 0:
            cart.pop(str(pid), None)
        else:
            product = db.get_product_by_id(pid)
            if not product:
                return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
            if qty > int(product['stock']):
                return jsonify({'success': False, 'error': 'Stock insuficiente'}), 400
            cart[str(pid)] = qty
        session['cart'] = cart
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ecommerce/cart/remove', methods=['POST'])
def ecommerce_cart_remove():
    try:
        data = request.get_json()
        pid = int(data.get('product_id'))
        cart = _get_cart()
        cart.pop(str(pid), None)
        session['cart'] = cart
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ecommerce/checkout', methods=['POST'])
def ecommerce_checkout():
    try:
        data = request.get_json() or {}
        customer_name = data.get('customer_name')
        customer_email = data.get('customer_email')
        cart = _get_cart()
        if not cart:
            return jsonify({'success': False, 'error': 'Carrito vacío'}), 400

        items = [{'product_id': int(pid), 'quantity': int(qty)} for pid, qty in cart.items()]
        order_id, total = db.create_order(items, customer_name, customer_email)
        if not order_id:
            return jsonify({'success': False, 'error': 'No se pudo crear el pedido'}), 400
        # Vaciar carrito
        session['cart'] = {}
        return jsonify({'success': True, 'data': {'order_id': order_id, 'total': round(total, 2)}})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Verificar que la base de datos esté inicializada
    print("Inicializando base de datos...")
    db.init_database()
    # Seeding deshabilitado para evitar inserciones repetidas de productos
    # db.insert_sample_data()
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