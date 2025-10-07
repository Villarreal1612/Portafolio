// Employee Manager - Frontend JavaScript

// Configuración de la API
const API_BASE_URL = 'http://localhost:5000/api';

// Variables globales
let currentUser = { username: 'demo', role: 'admin' };
let currentPage = 1;
let currentPerPage = 10;
let currentSearch = '';
let currentEstadoFilter = '';

// Datos simulados para el demo
let mockEmployees = [
    {
        id: 1,
        nombre: 'Juan',
        apellido: 'Pérez',
        email: 'juan.perez@empresa.com',
        telefono: '+1234567890',
        departamento: 'Desarrollo',
        puesto: 'Desarrollador Senior',
        fecha_ingreso: '2022-01-15',
        salario: 75000,
        estado: 'activo'
    },
    {
        id: 2,
        nombre: 'María',
        apellido: 'García',
        email: 'maria.garcia@empresa.com',
        telefono: '+1234567891',
        departamento: 'Recursos Humanos',
        puesto: 'Gerente de RRHH',
        fecha_ingreso: '2021-03-10',
        salario: 85000,
        estado: 'activo'
    },
    {
        id: 3,
        nombre: 'Carlos',
        apellido: 'López',
        email: 'carlos.lopez@empresa.com',
        telefono: '+1234567892',
        departamento: 'Marketing',
        puesto: 'Especialista en Marketing',
        fecha_ingreso: '2023-06-01',
        salario: 60000,
        estado: 'activo'
    },
    {
        id: 4,
        nombre: 'Ana',
        apellido: 'Martínez',
        email: 'ana.martinez@empresa.com',
        telefono: '+1234567893',
        departamento: 'Finanzas',
        puesto: 'Analista Financiero',
        fecha_ingreso: '2022-09-20',
        salario: 65000,
        estado: 'inactivo'
    },
    {
        id: 5,
        nombre: 'Roberto',
        apellido: 'Sánchez',
        email: 'roberto.sanchez@empresa.com',
        telefono: '+1234567894',
        departamento: 'Desarrollo',
        puesto: 'Desarrollador Junior',
        fecha_ingreso: '2023-11-15',
        salario: 45000,
        estado: 'activo'
    }
];

// Elementos del DOM
const loginPanel = document.getElementById('login-panel');
const registerPanel = document.getElementById('register-panel');
const mainPanel = document.getElementById('main-panel');
const userInfo = document.getElementById('user-info');
const usernameSpan = document.getElementById('username');
const logoutBtn = document.getElementById('logout-btn');

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

// Inicializar aplicación
function initializeApp() {
    // En modo demo, ir directamente al panel principal
    showMainPanel();
}

// Configurar event listeners
function setupEventListeners() {
    // Formularios de autenticación
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    
    // Enlaces para cambiar entre login y registro
    document.getElementById('show-register').addEventListener('click', (e) => {
        e.preventDefault();
        showRegisterPanel();
    });
    
    document.getElementById('show-login').addEventListener('click', (e) => {
        e.preventDefault();
        showLoginPanel();
    });
    
    // Logout
    logoutBtn.addEventListener('click', handleLogout);
    
    // Formulario de empleado
    document.getElementById('employee-form').addEventListener('submit', (e) => e.preventDefault());
    document.getElementById('save-employee-btn').addEventListener('click', handleSaveEmployee);
    
    // Búsqueda y filtros
    document.getElementById('search-btn').addEventListener('click', handleSearch);
    document.getElementById('clear-btn').addEventListener('click', handleClearFilters);
    document.getElementById('search-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    
    // Cambio de elementos por página
    document.getElementById('per-page-select').addEventListener('change', (e) => {
        currentPerPage = parseInt(e.target.value);
        currentPage = 1;
        loadEmployees();
    });
    
    // Importación/Exportación
    document.getElementById('import-btn').addEventListener('click', () => {
        document.getElementById('csv-file-input').click();
    });
    document.getElementById('csv-file-input').addEventListener('change', handleImportCSV);
    document.getElementById('export-btn').addEventListener('click', handleExportExcel);
    document.getElementById('template-btn').addEventListener('click', handleDownloadTemplate);
    
    // Modal de empleado
    const employeeModal = document.getElementById('employeeModal');
    employeeModal.addEventListener('hidden.bs.modal', clearEmployeeForm);
}

// Funciones de autenticación
async function handleLogin(e) {
    e.preventDefault();
    
    // En modo demo, cualquier login es válido
    showAlert('Modo demo activado', 'success');
    showMainPanel();
}

async function handleRegister(e) {
    e.preventDefault();
    
    // En modo demo, el registro siempre es exitoso
    showAlert('Registro exitoso en modo demo', 'success');
    showLoginPanel();
}

async function verifyToken(token) {
    try {
        const response = await fetch(`${API_BASE_URL}/employees?page=1&per_page=1`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            // Token válido
            showMainPanel();
        } else {
            // Token inválido
            localStorage.removeItem('token');
            showLoginPanel();
        }
    } catch (error) {
        localStorage.removeItem('token');
        showLoginPanel();
    }
}

function handleLogout() {
    localStorage.removeItem('token');
    currentUser = null;
    showLoginPanel();
    showAlert('Sesión cerrada exitosamente', 'info');
}

// Funciones de navegación
function showLoginPanel() {
    loginPanel.style.display = 'block';
    registerPanel.style.display = 'none';
    mainPanel.style.display = 'none';
    userInfo.style.display = 'none';
    logoutBtn.style.display = 'none';
}

function showRegisterPanel() {
    loginPanel.style.display = 'none';
    registerPanel.style.display = 'block';
    mainPanel.style.display = 'none';
    userInfo.style.display = 'none';
    logoutBtn.style.display = 'none';
}

function showMainPanel() {
    loginPanel.style.display = 'none';
    registerPanel.style.display = 'none';
    mainPanel.style.display = 'block';
    userInfo.style.display = 'block';
    logoutBtn.style.display = 'block';
    
    if (currentUser) {
        usernameSpan.textContent = currentUser.username;
    }
    
    loadDashboardStats();
    loadEmployees();
}

// Función para cargar estadísticas del dashboard
async function loadDashboardStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/employees?page=1&per_page=1`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Actualizar estadísticas
        document.querySelector('.stat-card:nth-child(1) .stat-number').textContent = data.total;
        
        // Calcular empleados activos
        const activeResponse = await fetch(`${API_BASE_URL}/employees?status=active&page=1&per_page=1`);
        if (activeResponse.ok) {
            const activeData = await activeResponse.json();
            document.querySelector('.stat-card:nth-child(2) .stat-number').textContent = activeData.total;
        }
        
        // Para departamentos y salario promedio, necesitaríamos endpoints específicos
        // Por ahora, los dejamos como están o calculamos desde los datos existentes
        
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        // En caso de error, mantener los valores por defecto
    }
}

// Funciones de empleados
async function loadEmployees() {
    showLoading(true);
    
    try {
        // Construir URL con parámetros de búsqueda
        const params = new URLSearchParams({
            page: currentPage,
            per_page: currentPerPage
        });
        
        if (currentSearch) {
            params.append('search', currentSearch);
        }
        
        if (currentEstadoFilter) {
            params.append('status', currentEstadoFilter);
        }
        
        const response = await fetch(`${API_BASE_URL}/employees?${params}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        const pagination = {
            page: data.page,
            per_page: data.per_page,
            total: data.total,
            pages: data.total_pages,
            has_prev: data.page > 1,
            has_next: data.page < data.total_pages
        };
        
        displayEmployees(data.employees);
        displayPagination(pagination);
        updateResultsInfo(pagination);
        
    } catch (error) {
        console.error('Error loading employees:', error);
        showAlert('Error cargando empleados', 'danger');
    } finally {
        showLoading(false);
    }
}

function displayEmployees(employees) {
    const tbody = document.getElementById('employees-table-body');
    
    if (employees.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="text-center py-4">
                    <div class="empty-state">
                        <i class="fas fa-users"></i>
                        <p>No se encontraron empleados</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = employees.map(employee => `
        <tr>
            <td>${employee.employee_id}</td>
            <td>${employee.first_name} ${employee.last_name}</td>
            <td>${employee.email}</td>
            <td>${employee.department}</td>
            <td>${employee.position}</td>
            <td>${formatCurrency(employee.salary)}</td>
            <td>
                <span class="badge badge-estado estado-${employee.status}">
                    ${employee.status.charAt(0).toUpperCase() + employee.status.slice(1)}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-primary btn-action" onclick="editEmployee(${employee.id})" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-info btn-action" onclick="viewEmployee(${employee.id})" title="Ver">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-danger btn-action" onclick="deleteEmployee(${employee.id})" title="Eliminar">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function displayPagination(pagination) {
    const paginationEl = document.getElementById('pagination');
    
    if (pagination.total_pages <= 1) {
        paginationEl.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // Botón anterior
    if (pagination.current_page > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="changePage(${pagination.current_page - 1})">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
    }
    
    // Páginas
    const startPage = Math.max(1, pagination.current_page - 2);
    const endPage = Math.min(pagination.total_pages, pagination.current_page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        paginationHTML += `
            <li class="page-item ${i === pagination.current_page ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            </li>
        `;
    }
    
    // Botón siguiente
    if (pagination.current_page < pagination.total_pages) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="changePage(${pagination.current_page + 1})">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
    }
    
    paginationEl.innerHTML = paginationHTML;
}

function updateResultsInfo(pagination) {
    const resultsInfo = document.getElementById('results-info');
    const start = (pagination.current_page - 1) * pagination.per_page + 1;
    const end = Math.min(start + pagination.per_page - 1, pagination.total);
    
    resultsInfo.textContent = `Mostrando ${start}-${end} de ${pagination.total} empleados`;
}

function changePage(page) {
    currentPage = page;
    loadEmployees();
}

// Funciones de búsqueda y filtros
function handleSearch() {
    currentSearch = document.getElementById('search-input').value;
    currentEstadoFilter = document.getElementById('estado-filter').value;
    currentPage = 1;
    loadEmployees();
}

function handleClearFilters() {
    document.getElementById('search-input').value = '';
    document.getElementById('estado-filter').value = '';
    currentSearch = '';
    currentEstadoFilter = '';
    currentPage = 1;
    loadEmployees();
}

// Funciones CRUD de empleados
async function handleSaveEmployee() {
    const employeeId = document.getElementById('employee-id').value;
    const employeeData = {
        nombre: document.getElementById('employee-nombre').value,
        apellido: document.getElementById('employee-apellido').value,
        email: document.getElementById('employee-email').value,
        telefono: document.getElementById('employee-telefono').value,
        departamento: document.getElementById('employee-departamento').value,
        puesto: document.getElementById('employee-puesto').value,
        fecha_ingreso: document.getElementById('employee-fecha-ingreso').value,
        salario: parseFloat(document.getElementById('employee-salario').value),
        estado: document.getElementById('employee-estado').value
    };
    
    try {
        if (employeeId) {
            // Actualizar empleado existente
            const index = mockEmployees.findIndex(emp => emp.id === parseInt(employeeId));
            if (index !== -1) {
                mockEmployees[index] = { ...mockEmployees[index], ...employeeData };
                showAlert('Empleado actualizado exitosamente', 'success');
            }
        } else {
            // Crear nuevo empleado
            const newId = Math.max(...mockEmployees.map(emp => emp.id)) + 1;
            mockEmployees.push({ id: newId, ...employeeData });
            showAlert('Empleado creado exitosamente', 'success');
        }
        
        bootstrap.Modal.getInstance(document.getElementById('employeeModal')).hide();
        loadEmployees();
    } catch (error) {
        showAlert('Error guardando empleado', 'danger');
    }
}

async function editEmployee(id) {
    try {
        const employee = mockEmployees.find(emp => emp.id === parseInt(id));
        if (employee) {
            fillEmployeeForm(employee);
            document.getElementById('employeeModalTitle').innerHTML = 
                '<i class="fas fa-edit me-2"></i>Editar Empleado';
            new bootstrap.Modal(document.getElementById('employeeModal')).show();
        } else {
            showAlert('Empleado no encontrado', 'danger');
        }
    } catch (error) {
        showAlert('Error cargando empleado', 'danger');
    }
}

async function viewEmployee(id) {
    try {
        const employee = mockEmployees.find(emp => emp.id === parseInt(id));
        if (employee) {
            document.getElementById('view-nombre').textContent = `${employee.nombre} ${employee.apellido}`;
            document.getElementById('view-email').textContent = employee.email;
            document.getElementById('view-telefono').textContent = employee.telefono;
            document.getElementById('view-departamento').textContent = employee.departamento;
            document.getElementById('view-puesto').textContent = employee.puesto;
            document.getElementById('view-fecha-ingreso').textContent = formatDate(employee.fecha_ingreso);
            document.getElementById('view-salario').textContent = `$${employee.salario.toLocaleString()}`;
            document.getElementById('view-estado').textContent = employee.estado;
            
            const modal = new bootstrap.Modal(document.getElementById('viewEmployeeModal'));
            modal.show();
        } else {
            showAlert('Empleado no encontrado', 'danger');
        }
    } catch (error) {
        showAlert('Error cargando empleado', 'danger');
    }
}

async function deleteEmployee(id) {
    if (!confirm('¿Estás seguro de que deseas eliminar este empleado?')) {
        return;
    }
    
    try {
        const index = mockEmployees.findIndex(emp => emp.id === parseInt(id));
        if (index !== -1) {
            mockEmployees.splice(index, 1);
            showAlert('Empleado eliminado exitosamente', 'success');
            loadEmployees();
        } else {
            showAlert('Empleado no encontrado', 'danger');
        }
    } catch (error) {
        showAlert('Error eliminando empleado', 'danger');
    }
}

function fillEmployeeForm(employee) {
    document.getElementById('employee-id').value = employee.id || '';
    document.getElementById('employee-nombre').value = employee.nombre || '';
    document.getElementById('employee-documento').value = employee.documento || '';
    document.getElementById('employee-cargo').value = employee.cargo || '';
    document.getElementById('employee-fecha-ingreso').value = employee.fecha_ingreso || '';
    document.getElementById('employee-estado').value = employee.estado || '';
    document.getElementById('employee-notas').value = employee.notas || '';
}

function clearEmployeeForm() {
    document.getElementById('employee-form').reset();
    document.getElementById('employee-id').value = '';
    
    // Rehabilitar todos los campos
    const form = document.getElementById('employee-form');
    const inputs = form.querySelectorAll('input, select, textarea');
    inputs.forEach(input => input.disabled = false);
    
    document.getElementById('employeeModalTitle').innerHTML = 
        '<i class="fas fa-user me-2"></i>Nuevo Empleado';
    document.getElementById('save-employee-btn').style.display = 'block';
}

// Funciones de importación/exportación
async function handleImportCSV(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`${API_BASE_URL}/employees/import`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert(`Importación exitosa: ${data.imported} empleados importados`, 'success');
            loadEmployees();
        } else {
            showAlert(data.message || 'Error en la importación', 'danger');
        }
    } catch (error) {
        showAlert('Error de conexión', 'danger');
    }
    
    // Limpiar el input
    e.target.value = '';
}

async function handleExportExcel() {
    try {
        // Filtrar empleados según búsqueda y estado
        let filteredEmployees = mockEmployees;
        
        if (currentSearch) {
            const searchLower = currentSearch.toLowerCase();
            filteredEmployees = filteredEmployees.filter(emp => 
                emp.nombre.toLowerCase().includes(searchLower) ||
                emp.apellido.toLowerCase().includes(searchLower) ||
                emp.email.toLowerCase().includes(searchLower) ||
                emp.departamento.toLowerCase().includes(searchLower) ||
                emp.puesto.toLowerCase().includes(searchLower)
            );
        }
        
        if (currentEstadoFilter) {
            filteredEmployees = filteredEmployees.filter(emp => emp.estado === currentEstadoFilter);
        }
        
        // Crear CSV con formato correcto
        const headers = ['ID', 'Nombre', 'Apellido', 'Email', 'Teléfono', 'Departamento', 'Puesto', 'Fecha Ingreso', 'Salario', 'Estado'];
        const csvContent = [
            headers.join(','),
            ...filteredEmployees.map(emp => [
                emp.id,
                `"${emp.nombre}"`,
                `"${emp.apellido}"`,
                `"${emp.email}"`,
                `"${emp.telefono}"`,
                `"${emp.departamento}"`,
                `"${emp.puesto}"`,
                emp.fecha_ingreso,
                emp.salario,
                `"${emp.estado}"`
            ].join(','))
        ].join('\n');
        
        // Crear y descargar archivo
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `empleados_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        showAlert('Archivo exportado exitosamente', 'success');
    } catch (error) {
        showAlert('Error exportando archivo', 'danger');
    }
}

async function handleDownloadTemplate() {
    try {
        const response = await fetch(`${API_BASE_URL}/employees/template`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'plantilla_empleados.csv';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showAlert('Plantilla descargada exitosamente', 'success');
        } else {
            showAlert('Error descargando plantilla', 'danger');
        }
    } catch (error) {
        showAlert('Error de conexión', 'danger');
    }
}

// Funciones de utilidad
function showLoading(show) {
    const loading = document.getElementById('loading');
    loading.style.display = show ? 'block' : 'none';
}

function showAlert(message, type) {
    const alertsContainer = document.getElementById('alerts-container');
    const alertId = 'alert-' + Date.now();
    
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertsContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // Auto-dismiss después de 5 segundos
    setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            const alert = bootstrap.Alert.getOrCreateInstance(alertElement);
            alert.close();
        }
    }, 5000);
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES');
}

function formatCurrency(amount) {
    if (!amount) return '$0';
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}