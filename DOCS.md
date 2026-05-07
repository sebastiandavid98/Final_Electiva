# Documentación Técnica - Sistema de Gestión de Reservas de Laboratorios

## Arquitectura del Sistema

### Patrón MVT (Model-View-Template)

El proyecto sigue la arquitectura MVT de Django:

- **Modelos**: Definen la estructura de datos y lógica de negocio
- **Vistas**: Manejan la lógica de presentación y procesamiento de requests
- **Templates**: Gestionan la presentación de datos al usuario

### Estructura de Aplicaciones

#### Aplicación `reservas`

**Modelos:**
- `Reserva`: Entidad principal que representa una reserva de laboratorio

**Vistas:**
- `ReservaCreateView`: Vista para crear nuevas reservas
- `ReservaListView`: Vista para listar reservas (pendiente implementación)
- `ReservaUpdateView`: Vista para editar reservas (pendiente implementación)
- `ReservaDeleteView`: Vista para eliminar reservas (pendiente implementación)

**URLs:**
- `/`: Lista de reservas
- `/crear/`: Crear nueva reserva
- `/editar/<id>/`: Editar reserva existente
- `/eliminar/<id>/`: Eliminar reserva

## Modelo de Datos

### Diagrama Entidad-Relación

```
Usuario (Django Auth) ----1:N---- Reserva
                              |
                              |-- laboratorio: CharField
                              |-- fecha: DateField
                              |-- hora_inicio: TimeField
                              |-- hora_fin: TimeField
                              |-- estado: CharField (choices)
                              |-- motivo: TextField
                              |-- fecha_creacion: DateTimeField
```

### Restricciones y Validaciones

- **Usuario**: Obligatorio, clave foránea a User
- **Laboratorio**: Obligatorio, máximo 100 caracteres
- **Fecha**: Obligatoria, formato de fecha
- **Horas**: Obligatorias, formato de tiempo
- **Estado**: Obligatorio, valores predefinidos
- **Motivo**: Opcional, texto largo

## API REST

### Endpoints Planificados

Utilizando Django REST Framework, se implementarán los siguientes endpoints:

- `GET /api/reservas/`: Listar todas las reservas
- `POST /api/reservas/`: Crear nueva reserva
- `GET /api/reservas/{id}/`: Obtener reserva específica
- `PUT /api/reservas/{id}/`: Actualizar reserva
- `DELETE /api/reservas/{id}/`: Eliminar reserva

### Serializers

Se requerirán serializers para:
- `ReservaSerializer`: Serialización completa del modelo Reserva
- `ReservaCreateSerializer`: Serialización para creación (excluye campos automáticos)

## Seguridad

### Autenticación

- Sistema de autenticación de Django integrado
- `LoginRequiredMixin` en vistas que requieren usuario autenticado
- Asignación automática de usuario a reservas creadas

### Autorización

- Usuarios solo pueden gestionar sus propias reservas
- Administradores pueden gestionar todas las reservas
- Estados de reserva controlan permisos de modificación

## Formularios

### Crispy Forms

Se utiliza Django Crispy Forms para mejorar la presentación de formularios:

- Formulario de creación de reservas
- Estilos consistentes
- Validación del lado cliente

## Base de Datos

### Configuración Actual

- **Motor**: SQLite (desarrollo)
- **Archivo**: `db.sqlite3` en directorio raíz

### Migraciones

Las migraciones están ubicadas en `reservas/migrations/` y incluyen:
- Creación inicial del modelo Reserva
- Modificaciones futuras del esquema

## Despliegue

### Variables de Entorno

Para producción, configurar:

```bash
DEBUG=False
SECRET_KEY=clave-secreta-produccion
ALLOWED_HOSTS=dominio.com,www.dominio.com
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

### Comandos de Despliegue

```bash
# Recopilar archivos estáticos
python manage.py collectstatic

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

## Testing

### Estrategia de Pruebas

- **Unit Tests**: Pruebas de modelos y lógica de negocio
- **Integration Tests**: Pruebas de vistas y URLs
- **API Tests**: Pruebas de endpoints REST

### Ejemplos de Pruebas

```python
# Test de modelo
def test_reserva_creation(self):
    reserva = Reserva.objects.create(...)
    self.assertEqual(reserva.estado, 'pendiente')

# Test de vista
def test_reserva_create_view(self):
    response = self.client.post('/reservas/crear/', {...})
    self.assertEqual(response.status_code, 302)
```

## Monitoreo y Logs

### Configuración de Logs

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'django_errors.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

## Próximas Funcionalidades

### Funcionalidades Pendientes

1. **Implementar vistas faltantes**: ListView, UpdateView, DeleteView
2. **API REST completa**: Serializers y ViewSets
3. **Sistema de notificaciones**: Email para cambios de estado
4. **Calendario visual**: Interfaz de calendario para reservas
5. **Gestión de laboratorios**: Modelo para laboratorios disponibles
6. **Sistema de permisos**: Roles de usuario (estudiante, profesor, admin)

### Mejoras de UX/UI

1. **Plantillas responsivas**: Diseño mobile-friendly
2. **Validación en tiempo real**: JavaScript para validaciones
3. **Filtros y búsqueda**: Funcionalidades avanzadas de listado
4. **Dashboard**: Panel de control con estadísticas

## Contribución al Desarrollo

### Flujo de Trabajo Git

1. **Crear rama feature**: `git checkout -b feature/nueva-funcionalidad`
2. **Desarrollar**: Implementar cambios con commits descriptivos
3. **Testing**: Ejecutar tests y verificar funcionalidad
4. **Pull Request**: Crear PR hacia rama `dev`
5. **Code Review**: Revisión por pares
6. **Merge**: Integración a rama principal

### Estándares de Código

- **PEP 8**: Guías de estilo Python
- **Docstrings**: Documentación en funciones y clases
- **Commits**: Mensajes descriptivos en inglés
- **Nombres**: Convenciones de nomenclatura consistentes

## Soporte y Mantenimiento

### Documentación de Usuario

- Manual de usuario para estudiantes
- Guía de administración para staff
- API documentation con Swagger/OpenAPI

### Monitoreo en Producción

- Logs de errores y rendimiento
- Métricas de uso del sistema
- Alertas automáticas para issues críticos

---

*Documentación generada el 7 de mayo de 2026*