# Sistema de Agencia de Viajes

## Contexto

Plataforma para la reservación de paquetes turísticos, vuelos y hoteles con integración a proveedores externos.

## Actores

- **Cliente:** Busca y reserva servicios turísticos.
- **Agente:** Asesora y gestiona reservas complejas.
- **Proveedor:** Hoteles/aerolíneas que actualizan disponibilidad.

## Requerimientos Funcionales

| ID   | Requerimiento                          | Criterios de Validación                                   |
|------|----------------------------------------|----------------------------------------------------------|
| RF1  | Búsqueda                               | Filtros combinados (destino, fecha, precio).             |
| RF2  | Reservas                               | Proceso en 3 pasos con pago integrado.                   |
| RF3  | Promociones                            | Descuentos por temporada o paquetes.                     |
| RF4  | Dashboard                              | Métricas de ventas y ocupación.                          |
| RF5  | Autenticación                          | Roles diferenciados (Cliente, Agente, Proveedor).         |

## Casos de Uso Profundos

### CU1: Reservar Paquete Turístico

1. **Cliente** selecciona destino y fechas.
2. **Sistema** muestra opciones disponibles.
3. **Cliente** selecciona hotel y vuelo.
4. **Sistema** calcula total con impuestos.
5. **Cliente** completa datos y pago.
6. **Sistema** emite voucher electrónico.

**Flujo alternativo:** Si el pago es rechazado, el sistema libera la reserva temporalmente y notifica al cliente.

### CU2: Actualizar Disponibilidad

1. **Proveedor** autentica en la API.
2. **Proveedor** envía datos actualizados en formato JSON.
3. **Sistema** valida y procesa los cambios.
4. **Sistema** retorna confirmación o errores en el procesamiento.

## Estructura del Proyecto

