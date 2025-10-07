import sqlite3
import hashlib
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='../database/employees.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializar la base de datos con las tablas necesarias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de usuarios para autenticación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de empleados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                department TEXT,
                position TEXT NOT NULL,
                salary REAL,
                hire_date DATE NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crear usuario admin por defecto
        admin_exists = cursor.execute(
            'SELECT COUNT(*) FROM users WHERE username = ?', ('admin',)
        ).fetchone()[0]
        
        if admin_exists == 0:
            admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', 'admin@company.com', admin_password, 'admin'))
        
        # Insertar datos de muestra si no existen empleados
        employees_count = cursor.execute('SELECT COUNT(*) FROM employees').fetchone()[0]
        
        if employees_count == 0:
            sample_employees = [
                ('EMP001', 'Juan', 'Pérez', 'juan.perez@empresa.com', '+1234567890', 'Desarrollo', 'Desarrollador Senior', 75000, '2023-01-15', 'active'),
                ('EMP002', 'María', 'García', 'maria.garcia@empresa.com', '+1234567891', 'Marketing', 'Gerente de Marketing', 65000, '2023-02-01', 'active'),
                ('EMP003', 'Carlos', 'López', 'carlos.lopez@empresa.com', '+1234567892', 'Recursos Humanos', 'Especialista en RRHH', 55000, '2023-03-10', 'active'),
                ('EMP004', 'Ana', 'Martínez', 'ana.martinez@empresa.com', '+1234567893', 'Finanzas', 'Analista Financiero', 60000, '2023-04-05', 'active'),
                ('EMP005', 'Luis', 'Rodríguez', 'luis.rodriguez@empresa.com', '+1234567894', 'Desarrollo', 'Desarrollador Junior', 45000, '2023-05-20', 'active')
            ]
            
            cursor.executemany('''
                INSERT INTO employees (employee_id, first_name, last_name, email, phone, department, position, salary, hire_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_employees)
        
        conn.commit()
        conn.close()

class Employee:
    def __init__(self, db_path='../database/employees.db'):
        self.db = Database(db_path)
    
    def create(self, data):
        """Crear un nuevo empleado"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO employees (employee_id, first_name, last_name, email, phone, 
                                     department, position, salary, hire_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['employee_id'], data['first_name'], data['last_name'], 
                data['email'], data.get('phone'), data.get('department'),
                data['position'], data.get('salary'), data['hire_date'],
                data.get('status', 'active')
            ))
            
            employee_id = cursor.lastrowid
            conn.commit()
            return {'success': True, 'id': employee_id}
            
        except sqlite3.IntegrityError as e:
            if 'employee_id' in str(e):
                return {'success': False, 'error': 'El ID de empleado ya existe'}
            elif 'email' in str(e):
                return {'success': False, 'error': 'El email ya existe'}
            else:
                return {'success': False, 'error': 'Error de integridad de datos'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def get_all(self, page=1, per_page=10, search='', filter_estado=''):
        """Obtener todos los empleados con paginación y filtros"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Construir query con filtros
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append('(first_name LIKE ? OR last_name LIKE ? OR employee_id LIKE ? OR email LIKE ? OR position LIKE ?)')
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param, search_param, search_param])
        
        if filter_estado:
            where_conditions.append('status = ?')
            params.append(filter_estado)
        
        where_clause = ' WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''
        
        # Contar total de registros
        count_query = f'SELECT COUNT(*) FROM employees{where_clause}'
        total = cursor.execute(count_query, params).fetchone()[0]
        
        # Obtener registros paginados
        offset = (page - 1) * per_page
        query = f'''
            SELECT * FROM employees{where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        '''
        params.extend([per_page, offset])
        
        employees = cursor.execute(query, params).fetchall()
        
        # Convertir a diccionarios
        columns = [description[0] for description in cursor.description]
        employees_list = [dict(zip(columns, row)) for row in employees]
        
        conn.close()
        
        return {
            'employees': employees_list,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def get_by_id(self, employee_id):
        """Obtener un empleado por ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        employee = cursor.execute(
            'SELECT * FROM employees WHERE id = ?', (employee_id,)
        ).fetchone()
        
        if employee:
            columns = [description[0] for description in cursor.description]
            employee_dict = dict(zip(columns, employee))
            conn.close()
            return employee_dict
        
        conn.close()
        return None
    
    def update(self, employee_id, data):
        """Actualizar un empleado"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE employees 
                SET employee_id=?, first_name=?, last_name=?, email=?, phone=?,
                    department=?, position=?, salary=?, hire_date=?, status=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (
                data['employee_id'], data['first_name'], data['last_name'],
                data['email'], data.get('phone'), data.get('department'),
                data['position'], data.get('salary'), data['hire_date'],
                data.get('status', 'active'), employee_id
            ))
            
            if cursor.rowcount > 0:
                conn.commit()
                return {'success': True}
            else:
                return {'success': False, 'error': 'Empleado no encontrado'}
                
        except sqlite3.IntegrityError as e:
            if 'employee_id' in str(e):
                return {'success': False, 'error': 'El ID de empleado ya existe'}
            elif 'email' in str(e):
                return {'success': False, 'error': 'El email ya existe'}
            else:
                return {'success': False, 'error': 'Error de integridad de datos'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def delete(self, employee_id):
        """Eliminar un empleado"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
        
        if cursor.rowcount > 0:
            conn.commit()
            conn.close()
            return {'success': True}
        else:
            conn.close()
            return {'success': False, 'error': 'Empleado no encontrado'}

class User:
    def __init__(self, db_path='../database/employees.db'):
        self.db = Database(db_path)
    
    def create_user(self, username, email, password, role='user'):
        """Crear un nuevo usuario"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, role))
            
            user_id = cursor.lastrowid
            conn.commit()
            return {'success': True, 'id': user_id}
            
        except sqlite3.IntegrityError:
            return {'success': False, 'error': 'Usuario o email ya existe'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def authenticate(self, username, password):
        """Autenticar usuario"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        user = cursor.execute('''
            SELECT id, username, email, role FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash)).fetchone()
        
        if user:
            columns = [description[0] for description in cursor.description]
            user_dict = dict(zip(columns, user))
            conn.close()
            return user_dict
        
        conn.close()
        return None