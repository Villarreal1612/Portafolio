# Personal Finance Tracker 💰

Un gestor completo de finanzas personales que permite registrar ingresos y gastos, visualizar balances mensuales y generar reportes detallados con gráficas interactivas.

## 🚀 Características Principales

### 📊 Dashboard Interactivo
- **Resumen financiero**: Visualización de ingresos, gastos y balance total
- **Gráficas dinámicas**: Distribución de gastos por categoría y tendencias mensuales
- **Predicción de gastos**: Estimación de gastos futuros basada en media móvil
- **Estadísticas en tiempo real**: Actualización automática de métricas

### 💳 Gestión de Transacciones
- **Registro completo**: Fecha, monto, categoría, tipo y descripción
- **Categorías predefinidas**: Alimentación, transporte, entretenimiento, salud, etc.
- **Filtros avanzados**: Por fecha, categoría y tipo de transacción
- **Edición y eliminación**: Modificar o eliminar transacciones existentes
- **Paginación**: Navegación eficiente por grandes volúmenes de datos

### 📈 Reportes y Análisis
- **Reportes mensuales**: Análisis detallado por mes y año
- **Gráficas de distribución**: Visualización de ingresos y gastos por categoría
- **Comparativas temporales**: Tendencias y patrones de gasto
- **Exportación de datos**: Descarga de reportes en formato CSV

### 🔄 Importación/Exportación
- **Exportar a CSV**: Descarga de todas las transacciones con filtros opcionales
- **Importar desde CSV**: Carga masiva de transacciones con validación
- **Plantilla incluida**: Formato estándar para importación de datos
- **Vista previa**: Verificación de datos antes de la importación

### 👥 Sistema Multiusuario
- **Autenticación**: Sistema de usuarios independientes
- **Datos aislados**: Cada usuario maneja sus propias finanzas
- **Seguridad**: Validación y protección de datos

## 🛠️ Stack Tecnológico

### Backend
- **Python 3.8+**: Lenguaje principal
- **Flask**: Framework web ligero y flexible
- **SQLite**: Base de datos embebida
- **CSV**: Manejo de importación/exportación

### Frontend
- **HTML5**: Estructura semántica
- **CSS3**: Estilos modernos y responsivos
- **JavaScript ES6+**: Lógica del cliente
- **Bootstrap 5.3**: Framework CSS
- **Chart.js**: Gráficas interactivas
- **Font Awesome**: Iconografía

### Librerías Adicionales
- **date-fns**: Manejo de fechas
- **Papa Parse**: Procesamiento de CSV

## 📁 Estructura del Proyecto

```
personal-finance-tracker/
├── backend/
│   └── app.py              # API Flask y lógica de negocio
├── frontend/
│   ├── index.html          # Interfaz principal
│   └── styles.css          # Estilos personalizados
└── README.md               # Documentación
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd personal-finance-tracker
   ```

2. **Instalar dependencias**
   ```bash
   pip install flask
   ```

3. **Ejecutar la aplicación**
   ```bash
   cd backend
   python app.py
   ```

4. **Acceder a la aplicación**
   - Abrir navegador en: `http://localhost:5000`
   - La aplicación se iniciará automáticamente con datos de ejemplo

## 📊 Uso de la Aplicación

### 1. Dashboard Principal
- **Vista general**: Resumen de ingresos, gastos y balance
- **Gráficas**: Visualización de gastos por categoría y tendencias
- **Predicción**: Estimación de gastos del próximo mes

### 2. Gestión de Transacciones
- **Agregar**: Completar formulario con fecha, tipo, categoría, monto y descripción
- **Filtrar**: Usar controles de fecha, categoría y tipo
- **Editar**: Hacer clic en el ícono de edición en la tabla
- **Eliminar**: Usar el botón de eliminación con confirmación

### 3. Reportes Mensuales
- **Seleccionar período**: Elegir mes y año específicos
- **Generar reporte**: Ver resumen y gráficas del período
- **Analizar tendencias**: Comparar con períodos anteriores

### 4. Importar/Exportar Datos
- **Exportar**: Descargar CSV con todas las transacciones
- **Importar**: Subir archivo CSV con formato específico
- **Plantilla**: Descargar ejemplo de formato correcto

## 🔧 Funcionalidades Técnicas

### Base de Datos
- **Usuarios**: Gestión de múltiples usuarios
- **Categorías**: Sistema de categorización flexible
- **Transacciones**: Registro completo de movimientos financieros
- **Presupuestos**: Control de gastos por categoría (futuro)

### API Endpoints
- `GET /api/categories` - Obtener categorías
- `POST /api/transactions` - Crear transacción
- `GET /api/transactions` - Listar transacciones
- `PUT /api/transactions/<id>` - Actualizar transacción
- `DELETE /api/transactions/<id>` - Eliminar transacción
- `GET /api/summary/<year>/<month>` - Resumen mensual
- `GET /api/export` - Exportar datos
- `POST /api/import` - Importar datos
- `GET /api/prediction` - Predicción de gastos

### Validaciones
- **Montos**: Solo números positivos
- **Fechas**: Formato válido y rango permitido
- **Categorías**: Existencia en el sistema
- **Archivos CSV**: Formato y estructura correctos

## 🎯 Características Avanzadas

### Predicción de Gastos
- **Algoritmo**: Media móvil de los últimos 3 meses
- **Precisión**: Basada en patrones históricos
- **Visualización**: Gráfica de tendencia predictiva

### Análisis de Datos
- **Distribución por categorías**: Identificar principales áreas de gasto
- **Tendencias temporales**: Evolución de ingresos y gastos
- **Comparativas**: Análisis período a período

### Experiencia de Usuario
- **Interfaz responsiva**: Adaptable a dispositivos móviles
- **Navegación intuitiva**: Pestañas organizadas por funcionalidad
- **Feedback visual**: Alertas y confirmaciones
- **Carga rápida**: Optimización de rendimiento

## 🔮 Funcionalidades Futuras

### Próximas Implementaciones
- **Presupuestos**: Establecer límites por categoría
- **Metas de ahorro**: Objetivos financieros personalizados
- **Notificaciones**: Alertas de gastos excesivos
- **Reportes PDF**: Exportación de reportes detallados
- **Análisis IA**: Recomendaciones personalizadas
- **Sincronización**: Backup en la nube
- **Aplicación móvil**: Versión nativa para smartphones

### Mejoras Técnicas
- **Base de datos**: Migración a PostgreSQL
- **Autenticación**: JWT y OAuth2
- **API REST**: Documentación con Swagger
- **Testing**: Cobertura completa de pruebas
- **Docker**: Containerización de la aplicación
- **CI/CD**: Pipeline de despliegue automatizado

## 🤝 Contribución

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el proyecto
2. Crear una rama para la funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit los cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

Desarrollado como parte del portafolio de proyectos de desarrollo web.

---

**Personal Finance Tracker** - Toma el control de tus finanzas personales 💪