import sqlite3
import csv
import io
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import numpy as np

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Finance Tracker Backend
Sistema completo de gestión financiera personal
"""

class PersonalFinanceDB:
    def __init__(self, db_path: str = "personal_finance.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializar la base de datos con todas las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de categorías
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                color TEXT DEFAULT '#007bff',
                icon TEXT DEFAULT 'fas fa-circle',
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Tabla de transacciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                category_id INTEGER NOT NULL,
                description TEXT,
                transaction_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # Tabla de presupuestos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_id INTEGER NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (category_id) REFERENCES categories (id),
                UNIQUE(user_id, category_id, month, year)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Insertar categorías por defecto
        self.insert_default_categories()
    
    def insert_default_categories(self):
        """Insertar categorías por defecto del sistema"""
        default_categories = [
            # Categorías de gastos
            ('Alimentación', 'expense', '#dc3545', 'fas fa-utensils'),
            ('Transporte', 'expense', '#fd7e14', 'fas fa-car'),
            ('Vivienda', 'expense', '#6f42c1', 'fas fa-home'),
            ('Salud', 'expense', '#e83e8c', 'fas fa-heartbeat'),
            ('Entretenimiento', 'expense', '#20c997', 'fas fa-gamepad'),
            ('Educación', 'expense', '#0dcaf0', 'fas fa-graduation-cap'),
            ('Ropa', 'expense', '#6610f2', 'fas fa-tshirt'),
            ('Servicios', 'expense', '#ffc107', 'fas fa-tools'),
            ('Otros Gastos', 'expense', '#6c757d', 'fas fa-ellipsis-h'),
            
            # Categorías de ingresos
            ('Salario', 'income', '#198754', 'fas fa-money-bill-wave'),
            ('Freelance', 'income', '#0d6efd', 'fas fa-laptop'),
            ('Inversiones', 'income', '#fd7e14', 'fas fa-chart-line'),
            ('Bonos', 'income', '#20c997', 'fas fa-gift'),
            ('Otros Ingresos', 'income', '#198754', 'fas fa-plus-circle'),
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for name, cat_type, color, icon in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO categories (name, type, color, icon, user_id)
                VALUES (?, ?, ?, ?, NULL)
            ''', (name, cat_type, color, icon))
        
        conn.commit()
        conn.close()
    
    def add_transaction(self, user_id: int, amount: float, transaction_type: str, 
                       category_id: int, description: str = "", transaction_date: str = None) -> int:
        """Agregar una nueva transacción"""
        if transaction_date is None:
            transaction_date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (user_id, amount, type, category_id, description, transaction_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, amount, transaction_type, category_id, description, transaction_date))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return transaction_id
    
    def get_transactions_by_user(self, user_id: int, start_date: str = None, 
                                end_date: str = None, category_id: int = None) -> List[Dict]:
        """Obtener transacciones de un usuario con filtros opcionales"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT t.id, t.amount, t.type, t.description, t.transaction_date,
                   c.name as category_name, c.color as category_color, c.icon as category_icon
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
        rows = cursor.fetchall()
        conn.close()
        
        transactions = []
        for row in rows:
            transactions.append({
                'id': row[0],
                'amount': float(row[1]),
                'type': row[2],
                'description': row[3],
                'transaction_date': row[4],
                'category_name': row[5],
                'category_color': row[6],
                'category_icon': row[7]
            })
        
        return transactions
    
    def get_monthly_summary(self, user_id: int, year: int, month: int) -> Dict:
        """Obtener resumen mensual de un usuario"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calcular totales de ingresos y gastos
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
            FROM transactions
            WHERE user_id = ? AND strftime('%Y', transaction_date) = ? AND strftime('%m', transaction_date) = ?
        ''', (user_id, str(year), f"{month:02d}"))
        
        result = cursor.fetchone()
        total_income = float(result[0]) if result[0] else 0.0
        total_expense = float(result[1]) if result[1] else 0.0
        
        # Gastos por categoría
        cursor.execute('''
            SELECT c.name, c.color, SUM(t.amount) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.type = 'expense' 
            AND strftime('%Y', t.transaction_date) = ? AND strftime('%m', t.transaction_date) = ?
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
        
        # Ingresos por categoría
        cursor.execute('''
            SELECT c.name, c.color, SUM(t.amount) as total
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND t.type = 'income' 
            AND strftime('%Y', t.transaction_date) = ? AND strftime('%m', t.transaction_date) = ?
            GROUP BY c.id, c.name, c.color
            ORDER BY total DESC
        ''', (user_id, str(year), f"{month:02d}"))
        
        income_by_category = []
        for row in cursor.fetchall():
            income_by_category.append({
                'category': row[0],
                'color': row[1],
                'amount': float(row[2])
            })
        
        conn.close()
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'expenses_by_category': expenses_by_category,
            'income_by_category': income_by_category
        }
    
    def get_all_categories(self, user_id: int = None) -> List[Dict]:
        """Obtener todas las categorías disponibles"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT id, name, type, color, icon
                FROM categories
                WHERE user_id IS NULL OR user_id = ?
                ORDER BY type, name
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT id, name, type, color, icon
                FROM categories
                WHERE user_id IS NULL
                ORDER BY type, name
            ''')
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'color': row[3],
                'icon': row[4]
            })
        
        conn.close()
        return categories
    
    def export_transactions_csv(self, user_id: int, start_date: str = None, end_date: str = None) -> str:
        """Exportar transacciones a CSV"""
        transactions = self.get_transactions_by_user(user_id, start_date, end_date)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escribir encabezados
        writer.writerow(['Fecha', 'Tipo', 'Categoría', 'Monto', 'Descripción'])
        
        # Escribir datos
        for transaction in transactions:
            writer.writerow([
                transaction['transaction_date'],
                transaction['type'],
                transaction['category_name'],
                transaction['amount'],
                transaction['description']
            ])
        
        return output.getvalue()
    
    def import_transactions_csv(self, user_id: int, csv_content: str) -> Dict:
        """Importar transacciones desde CSV"""
        try:
            # Leer CSV
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            imported_count = 0
            errors = []
            
            # Obtener categorías para mapeo
            categories = self.get_all_categories(user_id)
            category_map = {cat['name'].lower(): cat['id'] for cat in categories}
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Validar y procesar cada fila
                    date = row.get('Fecha', '').strip()
                    transaction_type = row.get('Tipo', '').strip().lower()
                    category_name = row.get('Categoría', '').strip()
                    amount = float(row.get('Monto', 0))
                    description = row.get('Descripción', '').strip()
                    
                    # Validaciones
                    if not date or not transaction_type or not category_name or amount <= 0:
                        errors.append(f"Fila {row_num}: Datos incompletos o inválidos")
                        continue
                    
                    if transaction_type not in ['income', 'expense', 'ingreso', 'gasto']:
                        errors.append(f"Fila {row_num}: Tipo de transacción inválido")
                        continue
                    
                    # Mapear tipo
                    if transaction_type in ['ingreso']:
                        transaction_type = 'income'
                    elif transaction_type in ['gasto']:
                        transaction_type = 'expense'
                    
                    # Buscar categoría
                    category_id = category_map.get(category_name.lower())
                    if not category_id:
                        errors.append(f"Fila {row_num}: Categoría '{category_name}' no encontrada")
                        continue
                    
                    # Agregar transacción
                    self.add_transaction(user_id, amount, transaction_type, category_id, description, date)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Fila {row_num}: Error al procesar - {str(e)}")
            
            return {
                'success': True,
                'imported_count': imported_count,
                'errors': errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error al procesar CSV: {str(e)}"
            }
    
    def predict_monthly_expense(self, user_id: int, months_back: int = 6) -> Dict:
        """Predicción simple de gasto mensual usando media móvil"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener gastos de los últimos meses
            cursor.execute('''
                SELECT strftime('%Y-%m', transaction_date) as month, SUM(amount) as total
                FROM transactions
                WHERE user_id = ? AND type = 'expense'
                AND transaction_date >= date('now', '-{} months')
                GROUP BY strftime('%Y-%m', transaction_date)
                ORDER BY month
            '''.format(months_back), (user_id,))
            
            monthly_expenses = cursor.fetchall()
            conn.close()
            
            if len(monthly_expenses) < 2:
                return {
                    'success': False,
                    'error': 'Datos insuficientes para predicción'
                }
            
            # Calcular media móvil
            expenses = [float(row[1]) for row in monthly_expenses]
            moving_average = np.mean(expenses)
            
            # Calcular tendencia
            x = np.arange(len(expenses))
            y = np.array(expenses)
            trend = np.polyfit(x, y, 1)[0]  # Pendiente de la línea de tendencia
            
            # Predicción para el próximo mes
            next_month_prediction = moving_average + trend
            
            return {
                'success': True,
                'current_average': round(moving_average, 2),
                'trend': round(trend, 2),
                'next_month_prediction': round(max(0, next_month_prediction), 2),
                'historical_data': [{'month': row[0], 'amount': float(row[1])} for row in monthly_expenses]
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Error en predicción: {str(e)}"
            }
    
    def delete_transaction(self, transaction_id: int, user_id: int) -> bool:
        """Eliminar una transacción"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM transactions
            WHERE id = ? AND user_id = ?
        ''', (transaction_id, user_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def update_transaction(self, transaction_id: int, user_id: int, data: Dict) -> bool:
        """Actualizar una transacción"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Construir query dinámicamente
        fields = []
        values = []
        
        for field in ['amount', 'type', 'category_id', 'description', 'transaction_date']:
            if field in data:
                fields.append(f"{field} = ?")
                values.append(data[field])
        
        if not fields:
            return False
        
        values.extend([transaction_id, user_id])
        
        query = f'''
            UPDATE transactions
            SET {', '.join(fields)}
            WHERE id = ? AND user_id = ?
        '''
        
        cursor.execute(query, values)
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
# --- Flask API server ---
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

db = PersonalFinanceDB()

@app.get('/api/finance/categories')
def api_categories():
    user_id = request.args.get('user_id', type=int)
    data = db.get_all_categories(user_id)
    return jsonify(data)

@app.get('/api/finance/transactions/<int:user_id>')
def api_get_transactions(user_id):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category_id = request.args.get('category_id', type=int)
    data = db.get_transactions_by_user(user_id, start_date, end_date, category_id)
    return jsonify({'data': data})

@app.post('/api/finance/transactions')
def api_create_transaction():
    payload = request.get_json(force=True) or {}
    required = ['user_id', 'amount', 'type', 'category_id', 'transaction_date']
    for k in required:
        if payload.get(k) is None:
            return jsonify({'success': False, 'error': f'Falta campo: {k}'}), 400
    tid = db.add_transaction(
        int(payload['user_id']),
        float(payload['amount']),
        str(payload['type']),
        int(payload['category_id']),
        str(payload.get('description', '')),
        str(payload['transaction_date'])
    )
    return jsonify({'success': True, 'id': tid})

@app.put('/api/finance/transactions/<int:transaction_id>')
def api_update_transaction(transaction_id: int):
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'success': False, 'error': 'user_id requerido'}), 400
    data = request.get_json(force=True) or {}
    success = db.update_transaction(transaction_id, user_id, data)
    return jsonify({'success': success})

@app.delete('/api/finance/transactions/<int:transaction_id>')
def api_delete_transaction(transaction_id: int):
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'success': False, 'error': 'user_id requerido'}), 400
    success = db.delete_transaction(transaction_id, user_id)
    return jsonify({'success': success})

@app.get('/api/finance/summary/<int:user_id>/<int:year>/<int:month>')
def api_monthly_summary(user_id: int, year: int, month: int):
    data = db.get_monthly_summary(user_id, year, month)
    return jsonify({'data': data})

@app.get('/api/finance/health')
def api_health():
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)