import sqlite3
import os
from datetime import datetime

class PortfolioDatabase:
    def __init__(self, db_path="portfolio.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Obtiene una conexión a la base de datos"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializa las tablas de la base de datos para Employee Manager y Personal Finance Tracker"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla para el sistema de autenticación
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(50),
                last_name VARCHAR(50),
                role VARCHAR(20) DEFAULT 'user',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla para el sistema de empleados (Employee Manager)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id VARCHAR(20) UNIQUE NOT NULL,
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                department VARCHAR(50),
                position VARCHAR(100),
                salary DECIMAL(10,2),
                hire_date DATE,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla para categorías de transacciones (Personal Finance Tracker)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) NOT NULL,
                type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
                color VARCHAR(7) DEFAULT '#007bff',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Índice único para evitar duplicación de categorías por nombre y tipo
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_categories_name_type
            ON categories (name, type)
        ''')
        
        # Tabla para transacciones (Personal Finance Tracker)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount DECIMAL(10,2) NOT NULL CHECK (amount > 0),
                type VARCHAR(20) NOT NULL CHECK (type IN ('income', 'expense')),
                category_id INTEGER NOT NULL,
                description TEXT,
                transaction_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Base de datos inicializada correctamente para Employee Manager y Personal Finance Tracker.")
    
    def insert_sample_data(self):
        """Insertar datos de ejemplo"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Insertar usuario administrador por defecto
            cursor.execute('''
                INSERT OR IGNORE INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', 'admin@portfolio.com', 'admin123', 'admin'))
            
            # Insertar empleados de ejemplo para Employee Manager
            sample_employees = [
                ('EMP001', 'Juan', 'Pérez', 'juan.perez@empresa.com', '123456789', 'IT', 'Desarrollador', 50000, '2023-01-15'),
                ('EMP002', 'María', 'García', 'maria.garcia@empresa.com', '987654321', 'Diseño', 'Diseñadora', 45000, '2023-02-01'),
                ('EMP003', 'Carlos', 'López', 'carlos.lopez@empresa.com', '555666777', 'Administración', 'Gerente', 70000, '2022-12-01')
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO employees (employee_id, first_name, last_name, email, phone, department, position, salary, hire_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_employees)
            
            # Insertar categorías de ejemplo para Personal Finance Tracker
            sample_categories = [
                ('Salario', 'income', '#28a745'),
                ('Freelance', 'income', '#17a2b8'),
                ('Inversiones', 'income', '#6f42c1'),
                ('Alimentación', 'expense', '#dc3545'),
                ('Transporte', 'expense', '#fd7e14'),
                ('Vivienda', 'expense', '#6c757d'),
                ('Entretenimiento', 'expense', '#e83e8c'),
                ('Salud', 'expense', '#20c997'),
                ('Educación', 'expense', '#007bff'),
                ('Compras', 'expense', '#ffc107')
            ]
            
            cursor.executemany('''
                INSERT OR IGNORE INTO categories (name, type, color)
                VALUES (?, ?, ?)
            ''', sample_categories)
            
            conn.commit()
            conn.close()
            print("Datos de ejemplo insertados correctamente")
            
        except sqlite3.Error as e:
            print(f"Error al insertar datos de ejemplo: {e}")
    
    # ==================== MÉTODOS PARA EMPLEADOS (EMPLOYEE MANAGER) ====================
    
    def get_all_employees(self):
        """Obtener todos los empleados"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, employee_id, first_name, last_name, email, phone, department, position, salary, hire_date, COALESCE(status, 'active') AS status, created_at
                FROM employees
                ORDER BY first_name, last_name
            ''')
            
            columns = [description[0] for description in cursor.description]
            employees = []
            
            for row in cursor.fetchall():
                employee = dict(zip(columns, row))
                employees.append(employee)
            
            conn.close()
            return employees
            
        except sqlite3.Error as e:
            print(f"Error al obtener empleados: {e}")
            return []
    
    def get_employee_by_email(self, email):
        """Verificar si existe un empleado con el email dado"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, employee_id, first_name, last_name, email
                FROM employees
                WHERE email = ?
            ''', (email,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
            
        except sqlite3.Error as e:
            print(f"Error al buscar empleado por email: {e}")
            return None
    
    def get_employee_by_employee_id(self, employee_id):
        """Verificar si existe un empleado con el employee_id dado"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, employee_id, first_name, last_name, email
                FROM employees
                WHERE employee_id = ?
            ''', (employee_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            return None
            
        except sqlite3.Error as e:
            print(f"Error al buscar empleado por employee_id: {e}")
            return None
    
    def add_employee(self, employee_id, first_name, last_name, email, phone=None, department=None, position=None, salary=0, hire_date=None, status='active'):
        """Agregar un nuevo empleado"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if hire_date is None:
                hire_date = datetime.now().strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT INTO employees (employee_id, first_name, last_name, email, phone, department, position, salary, hire_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (employee_id, first_name, last_name, email, phone, department, position, salary, hire_date, status))
            
            conn.commit()
            employee_db_id = cursor.lastrowid
            conn.close()
            return employee_db_id
            
        except sqlite3.Error as e:
            print(f"Error al agregar empleado: {e}")
            raise e
    
    def update_employee(self, employee_id, data):
        """Actualizar un empleado"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Construir la consulta dinámicamente basada en los campos proporcionados
            fields = []
            values = []
            
            allowed_fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone', 'department', 'position', 'salary', 'hire_date', 'status']
            
            for field in allowed_fields:
                if field in data:
                    fields.append(f"{field} = ?")
                    values.append(data[field])
            
            if not fields:
                conn.close()
                return False
            
            values.append(employee_id)
            
            query = f'''
                UPDATE employees 
                SET {', '.join(fields)}
                WHERE id = ?
            '''
            
            cursor.execute(query, values)
            conn.commit()
            result = cursor.rowcount > 0
            conn.close()
            
            return result
            
        except sqlite3.Error as e:
            print(f"Error al actualizar empleado: {e}")
            return False
    
    def delete_employee(self, employee_id):
        """Eliminar un empleado"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
            conn.commit()
            result = cursor.rowcount > 0
            conn.close()
            
            return result
            
        except sqlite3.Error as e:
            print(f"Error al eliminar empleado: {e}")
            return False
    
    # ==================== MÉTODOS PARA AUTENTICACIÓN ====================
    
    def authenticate_user(self, username, password):
        """Autenticar usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, password_hash, role
                FROM users
                WHERE username = ? AND password_hash = ?
            ''', (username, password))
            
            result = cursor.fetchone()
            conn.close()
            return result
            
        except sqlite3.Error as e:
            print(f"Error al autenticar usuario: {e}")
            return None
    
    def get_user_by_id(self, user_id):
        """Obtener usuario por ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, role, created_at
                FROM users
                WHERE id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            return result
            
        except sqlite3.Error as e:
            print(f"Error al obtener usuario: {e}")
            return None
    
    # ==================== MÉTODOS PARA PERSONAL FINANCE TRACKER ====================
    
    def get_all_categories(self):
        """Obtener todas las categorías"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, type, color, created_at
                FROM categories
                ORDER BY type, name
            ''')
            
            categories = []
            for row in cursor.fetchall():
                categories.append({
                    'id': row[0],
                    'name': row[1],
                    'type': row[2],
                    'color': row[3],
                    'created_at': row[4]
                })
            
            conn.close()
            return categories
            
        except sqlite3.Error as e:
            print(f"Error al obtener categorías: {e}")
            return []
    
    def add_transaction(self, user_id, amount, transaction_type, category_id, description, transaction_date):
        """Agregar una nueva transacción"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (user_id, amount, type, category_id, description, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, amount, transaction_type, category_id, description, transaction_date))
            
            transaction_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return transaction_id
            
        except sqlite3.Error as e:
            print(f"Error al agregar transacción: {e}")
            return None
    
    def get_transactions_by_user(self, user_id, start_date=None, end_date=None, category_id=None):
        """Obtener transacciones de un usuario con filtros opcionales"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT t.id, t.amount, t.type, t.category_id, t.description, t.transaction_date, t.created_at,
                       c.name as category_name, c.color as category_color
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ?
            '''
            params = [user_id]
            
            if start_date:
                query += ' AND t.transaction_date >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND t.transaction_date <= ?'
                params.append(end_date)
            
            if category_id:
                query += ' AND t.category_id = ?'
                params.append(category_id)
            
            query += ' ORDER BY t.transaction_date DESC, t.created_at DESC'
            
            cursor.execute(query, params)
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    'id': row[0],
                    'amount': float(row[1]),
                    'type': row[2],
                    'category_id': row[3],
                    'description': row[4],
                    'transaction_date': row[5],
                    'created_at': row[6],
                    'category_name': row[7],
                    'category_color': row[8]
                })
            
            conn.close()
            return transactions
            
        except sqlite3.Error as e:
            print(f"Error al obtener transacciones: {e}")
            return []
    
    def get_monthly_summary(self, user_id, year, month):
        """Obtener resumen mensual de ingresos y gastos"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Calcular totales por tipo
            cursor.execute('''
                SELECT type, SUM(amount) as total
                FROM transactions
                WHERE user_id = ? 
                AND strftime('%Y', transaction_date) = ? 
                AND strftime('%m', transaction_date) = ?
                GROUP BY type
            ''', (user_id, str(year), f"{month:02d}"))
            
            summary = {'income': 0, 'expense': 0, 'balance': 0}
            for row in cursor.fetchall():
                summary[row[0]] = float(row[1])
            
            summary['balance'] = summary['income'] - summary['expense']
            
            # Obtener gastos por categoría
            cursor.execute('''
                SELECT c.name, c.color, SUM(t.amount) as total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ? 
                AND t.type = 'expense'
                AND strftime('%Y', t.transaction_date) = ? 
                AND strftime('%m', t.transaction_date) = ?
                GROUP BY c.id, c.name, c.color
                ORDER BY total DESC
            ''', (user_id, str(year), f"{month:02d}"))
            
            expenses_by_category = []
            for row in cursor.fetchall():
                expenses_by_category.append({
                    'category': row[0],
                    'color': row[1],
                    'amount': float(row[2])
                })
            
            summary['expenses_by_category'] = expenses_by_category
            
            conn.close()
            return summary
            
        except sqlite3.Error as e:
            print(f"Error al obtener resumen mensual: {e}")
            return {'income': 0, 'expense': 0, 'balance': 0, 'expenses_by_category': []}

    def update_transaction(self, transaction_id, user_id, data):
        """Actualizar una transacción de un usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            fields = []
            values = []
            for field in ['amount', 'type', 'category_id', 'description', 'transaction_date']:
                if field in data and data[field] is not None:
                    fields.append(f"{field} = ?")
                    values.append(data[field])
            if not fields:
                conn.close()
                return False
            values.extend([transaction_id, user_id])
            query = f'''
                UPDATE transactions
                SET {', '.join(fields)}
                WHERE id = ? AND user_id = ?
            '''
            cursor.execute(query, values)
            updated = cursor.rowcount
            conn.commit()
            conn.close()
            return updated > 0
        except sqlite3.Error as e:
            print(f"Error al actualizar transacción: {e}")
            return False

    def delete_transaction(self, transaction_id, user_id):
        """Eliminar transacción por id del usuario"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transactions WHERE id = ? AND user_id = ?', (transaction_id, user_id))
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            return deleted > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar transacción: {e}")
            return False

if __name__ == "__main__":
    # Inicializar la base de datos
    db = PortfolioDatabase()
    db.insert_sample_data()