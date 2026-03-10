const API_URL = 'http://localhost:5000/api';

// Utility funciones
const utils = {
    // Formato de fecha
    formatearFecha(fecha) {
        const opciones = { year: 'numeric', month: '2-digit', day: '2-digit' };
        return new Date(fecha).toLocaleDateString('es-CO', opciones);
    },
    
    // Formato de hora
    formatearHora(hora) {
        return new Date(`2000-01-01 ${hora}`).toLocaleTimeString('es-CO', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    },
    
    // Obtener fecha y hora actual
    obtenerFechaHoraActual() {
        const ahora = new Date();
        return {
            fecha: ahora.toLocaleDateString('es-CO'),
            hora: ahora.toLocaleTimeString('es-CO')
        };
    },
    
    // Convertir a mayúsculas (excepto email)
    toUpperCase(texto) {
        return texto ? texto.toUpperCase() : '';
    },
    
    // Validar email
    validarEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email.toLowerCase());
    },
    
    // Mostrar notificación
    mostrarNotificacion(titulo, texto, tipo = 'success') {
        // Implementar sistema de notificaciones (opcional)
        alert(`${titulo}: ${texto}`);
    }
};

// API Client
const apiClient = {
    async request(url, options = {}) {
        const defaultOptions = {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        };
        
        const response = await fetch(`${API_URL}${url}`, {
            ...defaultOptions,
            ...options
        });
        
        // Si no se puede parsear JSON, retornar error
        let data;
        try {
            data = await response.json();
        } catch (e) {
            throw new Error('Error al procesar respuesta del servidor');
        }
        
        // No redirigir automáticamente - dejar que cada función maneje el error
        if (!response.ok) {
            throw new Error(data.message || 'Error en la petición');
        }
        
        return data;
    },
    
    // Auth
    auth: {
        async logout() {
            return await apiClient.request('/auth/logout', {
                method: 'POST'
            });
        },
        
        async checkSession() {
            return await apiClient.request('/auth/check-session');
        },
        
        async getCurrentUser() {
            return await apiClient.request('/auth/me');
        }
    },
    
    // Visitantes
    visitantes: {
        async buscar(tipoId, numId) {
            return await apiClient.request(`/visitantes/buscar?tipo_identificacion=${tipoId}&num_identificacion=${numId}`);
        },
        
        async buscarPorNit(nit) {
            return await apiClient.request(`/visitantes/buscar-por-nit?nit=${encodeURIComponent(nit)}`);
        },
        
        async registrar(data) {
            return await apiClient.request('/visitantes/registrar', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },
        
        async registrarIngreso(data) {
            return await apiClient.request('/visitantes/ingreso', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },
        
        async registrarSalida(logId) {
            return await apiClient.request(`/visitantes/salida/${logId}`, {
                method: 'PUT'
            });
        },
        
        async listar(params = {}) {
            const queryString = new URLSearchParams(params).toString();
            return await apiClient.request(`/visitantes/listar?${queryString}`);
        },
        
        async guardarFoto(logId, formData) {
            return await fetch(`${API_URL}/visitantes/foto/${logId}`, {
                method: 'POST',
                credentials: 'include',
                body: formData
            }).then(res => res.json());
        }
    },
    
    // Dependencias (globales para todas las sedes)
    dependencias: {
        async listar() {
            return await apiClient.request('/dependencias/');
        },
        
        async crear(data) {
            return await apiClient.request('/dependencias/', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },
        
        async actualizar(id, data) {
            return await apiClient.request(`/dependencias/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },
        
        async eliminar(id) {
            return await apiClient.request(`/dependencias/${id}`, {
                method: 'DELETE'
            });
        }
    },
    
    // Sedes
    sedes: {
        async listar() {
            return await apiClient.request('/sedes/');
        },
        
        async crear(data) {
            return await apiClient.request('/sedes/', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },
        
        async actualizar(id, data) {
            return await apiClient.request(`/sedes/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },
        
        async eliminar(id) {
            return await apiClient.request(`/sedes/${id}`, {
                method: 'DELETE'
            });
        }
    },
    
    // Usuarios
    usuarios: {
        async listar() {
            return await apiClient.request('/usuarios/');
        },
        
        async crear(data) {
            return await apiClient.request('/usuarios/', {
                method: 'POST',
                body: JSON.stringify(data)
            });
        },
        
        async actualizar(id, data) {
            return await apiClient.request(`/usuarios/${id}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
        },
        
        async resetearPassword(id, nuevaPassword) {
            return await apiClient.request(`/usuarios/${id}/resetear-password`, {
                method: 'POST',
                body: JSON.stringify({ nueva_password: nuevaPassword })
            });
        },
        
        async desbloquear(id) {
            return await apiClient.request(`/usuarios/${id}/desbloquear`, {
                method: 'POST'
            });
        }
    },
    
    // Reportes
    reportes: {
        async obtenerEstadisticas(fechaInicio, fechaFin) {
            return await apiClient.request(`/reportes/estadisticas?fecha_inicio=${fechaInicio}&fecha_fin=${fechaFin}`);
        },
        
        async generarExcel(visitasIds) {
            const response = await fetch(`${API_URL}/reportes/visitas/excel`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ visitas_ids: visitasIds })
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `reporte_visitas_${new Date().getTime()}.xlsx`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                return { success: true };
            } else {
                return { success: false, message: 'Error al generar el reporte' };
            }
        }
    },
    
    // Configuración
    configuracion: {
        async listar() {
            return await apiClient.request('/configuracion/');
        },
        
        async obtener(clave) {
            return await apiClient.request(`/configuracion/${clave}`);
        },
        
        async actualizar(clave, valor, descripcion = '', tipoDato = 'string') {
            return await apiClient.request(`/configuracion/${clave}`, {
                method: 'PUT',
                body: JSON.stringify({ valor, descripcion, tipo_dato: tipoDato })
            });
        },
        
        async actualizarBatch(configuraciones) {
            return await apiClient.request('/configuracion/batch', {
                method: 'PUT',
                body: JSON.stringify({ configuraciones })
            });
        }
    }
};

// Session manager
const sessionManager = {
    // Tiempo de inactividad en milisegundos (45 minutos)
    TIMEOUT: 45 * 60 * 1000,
    timer: null,
    
    init() {
        this.resetTimer();
        
        // Escuchar eventos de actividad del usuario
        ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'].forEach(event => {
            document.addEventListener(event, () => this.resetTimer(), true);
        });
    },
    
    resetTimer() {
        clearTimeout(this.timer);
        this.timer = setTimeout(() => this.logout(), this.TIMEOUT);
    },
    
    async logout() {
        try {
            await apiClient.auth.logout();
        } catch (error) {
            console.error('Error al cerrar sesión:', error);
        } finally {
            localStorage.removeItem('usuario');
            alert('Su sesión ha expirado por inactividad.');
            window.location.href = 'index.html';
        }
    }
};

// Validación de contraseñas
function validarPassword(password) {
    const errores = [];
    
    if (password.length < 8) {
        errores.push('Debe tener al menos 8 caracteres');
    }
    
    if (!/[A-Z]/.test(password)) {
        errores.push('Debe contener al menos una mayúscula');
    }
    
    if (!/[a-z]/.test(password)) {
        errores.push('Debe contener al menos una minúscula');
    }
    
    if (!/[0-9]/.test(password)) {
        errores.push('Debe contener al menos un número');
    }
    
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
        errores.push('Debe contener al menos un carácter especial');
    }
    
    return {
        valido: errores.length === 0,
        errores: errores
    };
}

// Tipos de identificación
const TIPOS_IDENTIFICACION = [
    { value: 'RC', label: 'RC - REGISTRO CIVIL' },
    { value: 'TI', label: 'TI - TARJETA DE IDENTIDAD' },
    { value: 'CC', label: 'CC - CEDULA CIUDADANIA' },
    { value: 'CE', label: 'CE - CEDULA EXTRANJERIA' },
    { value: 'PS', label: 'PS - PASAPORTE' },
    { value: 'CT', label: 'CT - CONTRASEÑA' }
];
