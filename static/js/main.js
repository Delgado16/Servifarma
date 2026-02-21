// ========================
// UTILIDADES GLOBALES
// ========================

/**
 * Cierra modales al hacer clic fuera de ellos
 */
window.addEventListener('click', (event) => {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});

/**
 * Cerrar modal con tecla ESC
 */
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
    }
});

/**
 * Formatear moneda dominicana
 */
function formatearDinero(cantidad) {
    return new Intl.NumberFormat('es-DO', {
        style: 'currency',
        currency: 'DOP'
    }).format(cantidad);
}

/**
 * Formatear fecha
 */
function formatearFecha(fecha) {
    return new Date(fecha).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

/**
 * Mostrar notificación
 */
function mostrarNotificacion(mensaje, tipo = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${tipo}`;
    alertDiv.textContent = mensaje;
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '80px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '10000';
    alertDiv.style.width = '350px';
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 4000);
}

/**
 * Validar formulario
 */
function validarFormulario(formElement) {
    if (!formElement.checkValidity()) {
        formElement.reportValidity();
        return false;
    }
    return true;
}

/**
 * Confirmar acción
 */
function confirmar(mensaje) {
    return confirm(mensaje);
}

/**
 * API Call wrapper
 */
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('[v0] API Error:', error);
        mostrarNotificacion('Error en la solicitud: ' + error.message, 'danger');
        throw error;
    }
}

/**
 * Cargar template con datos
 */
function renderTemplate(templateString, data) {
    return templateString.replace(/\{\{(\w+)\}\}/g, (match, key) => {
        return data[key] || '';
    });
}

// ========================
// FUNCIONES ADMIN
// ========================

/**
 * Editar producto
 */
function editarProducto(productoId) {
    apiCall(`/api/productos/${productoId}`)
        .then(producto => {
            console.log('[v0] Producto cargado para edición:', producto);
            // TODO: Implementar lógica de edición
            alert('Funcionalidad de edición en desarrollo');
        });
}

/**
 * Eliminar producto
 */
function eliminarProducto(productoId) {
    if (confirmar('¿Está seguro que desea eliminar este producto?')) {
        apiCall(`/api/productos/${productoId}`, {
            method: 'DELETE'
        })
        .then(result => {
            mostrarNotificacion('Producto eliminado exitosamente');
            location.reload();
        });
    }
}

/**
 * Ver detalles de compra
 */
function verCompra(compraId) {
    apiCall(`/api/compras/${compraId}`)
        .then(compra => {
            console.log('[v0] Compra:', compra);
            alert(`Compra #${compra.numero_documento} - Total: RD$ ${compra.total_costo}`);
        });
}

/**
 * Eliminar proveedor
 */
function eliminarProveedor(proveedorId) {
    if (confirmar('¿Está seguro que desea eliminar este proveedor?')) {
        apiCall(`/api/proveedores/${proveedorId}`, {
            method: 'DELETE'
        })
        .then(result => {
            mostrarNotificacion('Proveedor eliminado exitosamente');
            location.reload();
        });
    }
}

/**
 * Editar proveedor
 */
function editarProveedor(proveedorId) {
    console.log('[v0] Editando proveedor:', proveedorId);
    alert('Funcionalidad de edición en desarrollo');
}

// ========================
// FUNCIONES VENDEDOR
// ========================

/**
 * Incrementar cantidad en carrito
 */
function incrementarCantidad(indice) {
    const input = document.querySelector(`[data-item-index="${indice}"] .item-cantidad`);
    if (input) {
        input.value = parseInt(input.value) + 1;
        input.dispatchEvent(new Event('change'));
    }
}

/**
 * Decrementar cantidad en carrito
 */
function decrementarCantidad(indice) {
    const input = document.querySelector(`[data-item-index="${indice}"] .item-cantidad`);
    if (input && parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1;
        input.dispatchEvent(new Event('change'));
    }
}

/**
 * Aplicar descuento
 */
function aplicarDescuento(porcentaje) {
    const total = parseFloat(document.getElementById('total')?.textContent.replace('RD$ ', '') || 0);
    const descuento = total * (porcentaje / 100);
    const nuevoTotal = total - descuento;
    
    console.log('[v0] Descuento aplicado:', descuento);
    console.log('[v0] Nuevo total:', nuevoTotal);
}

/**
 * Imprimir comprobante
 */
function imprimirComprobante(ventaId) {
    apiCall(`/api/ventas/${ventaId}`)
        .then(venta => {
            const contenido = `
                <h2>COMPROBANTE DE VENTA</h2>
                <p>Transacción #${venta.numero_comprobante}</p>
                <p>Total: RD$ ${venta.total_venta}</p>
                <p>Fecha: ${formatearFecha(venta.fecha_venta)}</p>
            `;
            const ventana = window.open('', '', 'width=400,height=600');
            ventana.document.write(contenido);
            ventana.document.close();
            ventana.print();
        });
}

// ========================
// FUNCIONES DE REPORTES
// ========================

/**
 * Generar reporte de ganancias
 */
function generarReporteGanancias() {
    const fechaInicio = document.getElementById('fechaInicio')?.value || '';
    const fechaFin = document.getElementById('fechaFin')?.value || '';
    
    const params = new URLSearchParams();
    if (fechaInicio) params.append('fecha_inicio', fechaInicio);
    if (fechaFin) params.append('fecha_fin', fechaFin);
    
    apiCall(`/api/reportes/ganancia?${params}`)
        .then(data => {
            console.log('[v0] Reporte de ganancias:', data);
            // TODO: Mostrar datos en tabla
        });
}

/**
 * Exportar a CSV
 */
function exportarCSV(datos, nombreArchivo) {
    if (!datos || datos.length === 0) {
        alert('No hay datos para exportar');
        return;
    }
    
    const headers = Object.keys(datos[0]);
    const csv = [
        headers.join(','),
        ...datos.map(fila => headers.map(h => JSON.stringify(fila[h])).join(','))
    ].join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${nombreArchivo}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    console.log('[v0] Archivo CSV exportado:', nombreArchivo);
}

/**
 * Imprimir tabla
 */
function imprimirTabla(tablaId) {
    const tabla = document.getElementById(tablaId);
    if (!tabla) {
        alert('Tabla no encontrada');
        return;
    }
    
    const ventana = window.open('', '', 'width=900,height=600');
    ventana.document.write(tabla.outerHTML);
    ventana.document.close();
    ventana.print();
}

// ========================
// VALIDACIONES
// ========================

/**
 * Validar stock antes de venta
 */
function validarStock(productoId, cantidad) {
    // Esta función sería llamada desde el servidor
    console.log(`[v0] Validando stock para producto ${productoId}: ${cantidad}`);
    return true;
}

/**
 * Validar forma de pago
 */
function validarFormaPago(efectivo, tarjeta, transferencia, total) {
    const pagado = parseFloat(efectivo || 0) + parseFloat(tarjeta || 0) + parseFloat(transferencia || 0);
    
    if (pagado < total) {
        mostrarNotificacion('El monto pagado es menor al total', 'danger');
        return false;
    }
    
    return true;
}

/**
 * Validar cantidad mínima en carrito
 */
function validarCarrito(carrito) {
    if (!carrito || carrito.length === 0) {
        mostrarNotificacion('El carrito está vacío', 'warning');
        return false;
    }
    
    return true;
}

// ========================
// INICIALIZACIÓN
// ========================

document.addEventListener('DOMContentLoaded', () => {
    console.log('[v0] Aplicación FarmaControl inicializada');
    
    // Establecer fecha actual en inputs de fecha
    const hoy = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(input => {
        if (!input.value) input.value = hoy;
    });
});

// Prevenir envío duplicado de formularios
let enviandoFormulario = false;

document.addEventListener('submit', (e) => {
    if (enviandoFormulario) {
        e.preventDefault();
        return;
    }
    
    const form = e.target;
    if (!form.checkValidity()) {
        e.preventDefault();
        console.log('[v0] Formulario inválido');
    } else {
        enviandoFormulario = true;
        setTimeout(() => {
            enviandoFormulario = false;
        }, 3000);
    }
});
