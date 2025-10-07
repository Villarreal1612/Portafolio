import csv
import io
from openpyxl import Workbook
from datetime import datetime
from models import Employee

def import_employees_from_csv(csv_content):
    """Importar empleados desde contenido CSV"""
    try:
        # Leer CSV desde string
        df = pd.read_csv(io.StringIO(csv_content))
        
        # Validar columnas requeridas
        required_columns = ['nombre', 'documento', 'cargo', 'fecha_ingreso']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return {
                'success': False,
                'error': f'Columnas faltantes: {", ".join(missing_columns)}'
            }
        
        employee_model = Employee()
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Preparar datos del empleado
                employee_data = {
                    'nombre': str(row['nombre']).strip(),
                    'documento': str(row['documento']).strip(),
                    'cargo': str(row['cargo']).strip(),
                    'fecha_ingreso': str(row['fecha_ingreso']).strip(),
                    'estado': str(row.get('estado', 'activo')).strip(),
                    'salario': float(row['salario']) if pd.notna(row.get('salario')) else None,
                    'telefono': str(row.get('telefono', '')).strip() if pd.notna(row.get('telefono')) else None,
                    'email': str(row.get('email', '')).strip() if pd.notna(row.get('email')) else None,
                    'direccion': str(row.get('direccion', '')).strip() if pd.notna(row.get('direccion')) else None,
                    'notas': str(row.get('notas', '')).strip() if pd.notna(row.get('notas')) else None
                }
                
                # Validar fecha
                try:
                    datetime.strptime(employee_data['fecha_ingreso'], '%Y-%m-%d')
                except ValueError:
                    try:
                        # Intentar formato dd/mm/yyyy
                        date_obj = datetime.strptime(employee_data['fecha_ingreso'], '%d/%m/%Y')
                        employee_data['fecha_ingreso'] = date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        errors.append(f'Fila {index + 2}: Formato de fecha inválido')
                        continue
                
                # Crear empleado
                result = employee_model.create(employee_data)
                if result['success']:
                    imported_count += 1
                else:
                    errors.append(f'Fila {index + 2}: {result["error"]}')
                    
            except Exception as e:
                errors.append(f'Fila {index + 2}: Error procesando datos - {str(e)}')
        
        return {
            'success': True,
            'imported_count': imported_count,
            'total_rows': len(df),
            'errors': errors
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error procesando CSV: {str(e)}'
        }

def export_employees_to_excel(employees_data):
    """Exportar empleados a Excel"""
    try:
        # Crear DataFrame
        df = pd.DataFrame(employees_data)
        
        # Reordenar columnas
        column_order = [
            'id', 'nombre', 'documento', 'cargo', 'fecha_ingreso', 
            'estado', 'salario', 'telefono', 'email', 'direccion', 
            'notas', 'created_at', 'updated_at'
        ]
        
        # Filtrar solo las columnas que existen
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Empleados', index=False)
            
            # Ajustar ancho de columnas
            worksheet = writer.sheets['Empleados']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        return None

def generate_csv_template():
    """Generar plantilla CSV para importación"""
    template_data = {
        'nombre': ['Juan Pérez', 'María García'],
        'documento': ['12345678', '87654321'],
        'cargo': ['Desarrollador', 'Analista'],
        'fecha_ingreso': ['2024-01-15', '2024-02-01'],
        'estado': ['activo', 'activo'],
        'salario': [50000, 45000],
        'telefono': ['555-1234', '555-5678'],
        'email': ['juan@company.com', 'maria@company.com'],
        'direccion': ['Calle 123', 'Avenida 456'],
        'notas': ['Empleado ejemplar', 'Nueva contratación']
    }
    
    output = io.StringIO()
    df = pd.DataFrame(template_data)
    df.to_csv(output, index=False)
    return output.getvalue()

def validate_employee_data(data):
    """Validar datos de empleado"""
    errors = []
    
    # Campos requeridos
    required_fields = ['employee_id', 'first_name', 'last_name', 'email', 'position', 'hire_date']
    for field in required_fields:
        if not data.get(field) or str(data[field]).strip() == '':
            errors.append(f'El campo {field} es requerido')
    
    # Validar formato de fecha
    if data.get('hire_date'):
        try:
            datetime.strptime(data['hire_date'], '%Y-%m-%d')
        except ValueError:
            errors.append('Formato de fecha inválido (use YYYY-MM-DD)')
    
    # Validar estado
    if data.get('status') and data['status'] not in ['active', 'inactive']:
        errors.append('Estado debe ser "active" o "inactive"')
    
    # Validar salario
    if data.get('salary'):
        try:
            float(data['salary'])
        except (ValueError, TypeError):
            errors.append('Salario debe ser un número válido')
    
    # Validar email
    if data.get('email') and data['email'].strip():
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            errors.append('Formato de email inválido')
    
    return errors