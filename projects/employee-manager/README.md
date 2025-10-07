# Employee Manager / HR Dashboard

Sistema completo de gestión de empleados con funcionalidades CRUD, autenticación, importación/exportación de datos y interfaz responsive.

## Características

- **CRUD completo de empleados**: Crear, leer, actualizar y eliminar registros de empleados
- **Búsqueda y filtros avanzados**: Buscar empleados por nombre, cargo, estado, etc.
- **Paginación**: Navegación eficiente a través de grandes listas de empleados
- **Importación CSV**: Cargar múltiples empleados desde archivos CSV
- **Exportación Excel**: Descargar datos de empleados en formato Excel
- **Autenticación**: Sistema de registro y login seguro
- **Autorización**: Roles de administrador y usuario
- **Interfaz responsive**: Diseño adaptativo para todos los dispositivos

## Tecnologías Utilizadas

- **Backend**: Python con Flask
- **Base de datos**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Autenticación**: JWT (JSON Web Tokens)
- **Procesamiento de datos**: pandas, openpyxl
- **Estilos**: Bootstrap 5

## Estructura del Proyecto

```
employee-manager/
├── backend/
│   ├── app.py              # Aplicación principal Flask
│   ├── models.py           # Modelos de base de datos
│   ├── auth.py             # Autenticación y autorización
│   ├── routes/             # Rutas de la API
│   └── utils/              # Utilidades (CSV, Excel)
├── frontend/
│   ├── index.html          # Página principal
│   ├── login.html          # Página de login
│   ├── dashboard.html      # Dashboard principal
│   ├── css/                # Estilos CSS
│   └── js/                 # Scripts JavaScript
├── database/
│   └── employees.db        # Base de datos SQLite
└── README.md
```

## Instalación y Uso

1. Instalar dependencias:
```bash
pip install flask flask-jwt-extended pandas openpyxl sqlite3
```

2. Ejecutar la aplicación:
```bash
cd backend
python app.py
```

3. Abrir en el navegador: `http://localhost:5000`

## Funcionalidades

### Gestión de Empleados
- Agregar nuevos empleados con información completa
- Editar datos existentes
- Eliminar empleados
- Ver historial y detalles

### Búsqueda y Filtros
- Búsqueda por nombre, documento o cargo
- Filtros por estado (activo/inactivo)
- Filtros por fecha de ingreso
- Ordenamiento por diferentes campos

### Importación/Exportación
- Importar empleados desde archivos CSV
- Validación de datos durante la importación
- Exportar lista completa o filtrada a Excel
- Plantillas CSV para facilitar la importación

### Seguridad
- Autenticación con JWT
- Roles de usuario (admin/usuario)
- Protección de rutas sensibles
- Validación de datos en frontend y backend