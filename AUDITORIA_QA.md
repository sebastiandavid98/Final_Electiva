# Auditoria QA Actualizada - Sistema Django

Fecha: 2026-05-07
Proyecto: Sistema de Gestion de Reservas de Laboratorios
Estado general: FUNCIONAL EN ENTORNO LOCAL, CON RIESGOS RESIDUALES PARA PRODUCCION

## 1. Resumen ejecutivo

El sistema fue re-auditado despues de las correcciones de integracion. El estado actual ya no corresponde al diagnostico anterior: la app `reservas` esta conectada, tiene migraciones aplicadas, rutas reales, CRUD basico, validaciones de negocio, API REST, exportacion CSV/PDF y pruebas automatizadas.

La aplicacion funciona en entorno local y supera las verificaciones principales de Django. Aun no debe considerarse produccion final sin una revision de alcance funcional, limpieza de artefactos antiguos, pruebas manuales de navegador y configuracion real de `.env`/infraestructura.

## 2. Evidencia ejecutada

| Prueba | Resultado | Evidencia |
|---|---:|---|
| Dependencias | Cumple | Entorno `.venv` instalado con `requirements.txt` |
| `python manage.py check` | Cumple | Sin issues |
| `python manage.py makemigrations --check --dry-run` | Cumple | No changes detected |
| `python manage.py showmigrations` | Cumple | `reservas` aparece con `0001`, `0002`, `0003` aplicadas |
| `python manage.py test -v 1` | Cumple | 12 tests OK |
| `python manage.py collectstatic --noinput --dry-run` | Cumple | Copia simulada de 154 archivos |
| `python manage.py check --deploy` | Cumple con env productivo simulado | Sin issues usando `DJANGO_DEBUG=False`, `SECRET_KEY` segura y `ALLOWED_HOSTS` |
| Rutas por rol | Cumple | Estudiante, docente y administrativo redirigen a rutas 200 |
| Crear reserva | Cumple | POST a `/reservas/crear/` crea reserva y redirige |
| Conflicto horario | Cumple | Form invalido con mensaje de conflicto |
| Aprobar reserva | Cumple | Docente aprueba y cambia estado a `aprobada` |
| API REST | Cumple parcial | `/reservas/api/reservas/` responde 200 autenticado |
| Exportaciones | Cumple parcial | CSV y PDF responden 200 |

## 3. Modulos detectados

### accounts

| Componente | Estado |
|---|---|
| Modelo `Usuario` custom | Funcional |
| Roles estudiante/docente/administrativo | Funcional |
| Login/logout | Funcional |
| Perfil y cambio de contrasena | Funcional |
| Password reset | Parcial, rutas/templates existen; no se probo envio real por email |
| Middleware de permisos | Funcional, pero requiere mantenimiento al agregar rutas |
| Signals de grupos/permisos | Funcional en migraciones/tests |
| Tests | Cubren login, bloqueo, logout, cambio contrasena y acceso a usuarios |

### reservas

| Componente | Estado |
|---|---|
| Modelo `Reserva` | Funcional con `settings.AUTH_USER_MODEL` |
| Admin | Registrado |
| CRUD web | Funcional |
| Templates CRUD | Existen bajo `reservas/templates/reservas/` |
| Validaciones | Implementadas: fecha pasada, rango horario, conflicto |
| Estados | Pendiente, aprobada, rechazada |
| Aprobacion/rechazo | Funcional para docente/administrativo |
| Filtros | Basicos por estado/laboratorio en vista de todas |
| Exportacion CSV | Funcional |
| Exportacion PDF | Funcional basico, sin motor PDF avanzado |
| API REST | Funcional basica con DRF |
| Tests | 8 pruebas de flujo/reservas dentro de 12 totales |

## 4. Hallazgos actuales

| Severidad | Hallazgo | Modulo | Impacto | Evidencia | Recomendacion |
|---|---|---|---|---|---|
| Alto | No hay `.env.example` ni configuracion real documentada para produccion | Configuracion | Riesgo de despliegue incorrecto | `settings.py` depende de env para `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` | Crear `.env.example` y documentar variables |
| Alto | Se usa SQLite por defecto | Base de datos | No recomendado para produccion real multiusuario | `DATABASES` apunta a `db.sqlite3` | Agregar soporte env `DATABASE_URL` para PostgreSQL |
| Medio | Template antiguo `SistemaGestionReservasLaboratorios/templates/app/dashboard.html` esta roto aunque no conectado | Templates | Si alguien lo conecta, fallara por campos/URLs inexistentes | Referencia `reserva.laboratorio.nombre`, `reserva.inicio`, `cambiar_estado_reserva` | Eliminarlo o reescribirlo con modelo actual |
| Medio | PDF es generacion manual simple | Reportes | Sirve como descarga basica, no como reporte robusto | `_generar_pdf_simple` en `reservas/views.py` | Usar WeasyPrint/ReportLab si el parcial exige PDF formal |
| Medio | Validacion de conflictos considera todas las reservas, incluso rechazadas | Reservas | Puede impedir reservar un horario liberado por rechazo | `Reserva.clean()` no filtra por estado | Decidir regla y filtrar por `pendiente/aprobada` si aplica |
| Medio | `save(update_fields=['estado'])` ejecuta `full_clean()` completo | Reservas | Aprobar reservas vencidas podria fallar por fecha pasada | `Reserva.save()` siempre llama `full_clean()` | Separar validaciones de creacion/edicion vs cambio de estado |
| Medio | API REST no tiene pruebas especificas de permisos, POST/PUT/DELETE | API | Riesgo de regresiones no cubiertas | Tests actuales solo validan GET indirecto/manual | Agregar tests API por rol y casos negativos |
| Bajo | Documentacion README/DOCS aun describe estado anterior en partes | Docs | Puede confundir al equipo | DOCS dice vistas pendientes/API planificada | Actualizar documentacion |
| Bajo | Textos con encoding defectuoso en docs/templates antiguos | Calidad | Mala presentacion | `ConfiguraciÃ³n`, `contrasena` | Normalizar UTF-8 y copy UI |

## 5. Matriz de cumplimiento

| Requerimiento | Cumple | Parcial | No cumple | Evidencia |
|---|---:|---:|---:|---|
| Login usuario/password | Si |  |  | Tests OK y rutas 200 |
| Logout | Si |  |  | Tests OK |
| Identificacion de rol | Si |  |  | Redireccion por rol validada |
| Dashboard/landing por rol |  | Si |  | Redirige a paginas reales, pero no hay dashboard administrativo dedicado |
| Perfil usuario | Si |  |  | Tests OK |
| Cambio de contrasena | Si |  |  | Tests OK |
| Recuperar contrasena |  | Si |  | Rutas/templates existen; falta prueba email real |
| Permisos por rol | Si |  |  | Middleware y tests de accesos prohibidos |
| Bloqueo por intentos fallidos | Si |  |  | Tests OK |
| CRUD reservas | Si |  |  | Crear/editar/eliminar/listar implementado |
| Mis reservas | Si |  |  | Ruta y template implementados |
| Todas las reservas | Si |  |  | Ruta protegida y filtro basico |
| Aprobacion/rechazo | Si |  |  | Docente aprueba en prueba funcional |
| Conflictos horarios | Si |  |  | Form invalido validado |
| Fechas/horas invalidas | Si |  |  | `Reserva.clean()` |
| Filtros/busqueda |  | Si |  | Estado/laboratorio solamente |
| Exportacion CSV | Si |  |  | Responde 200 |
| Exportacion PDF |  | Si |  | PDF simple, no motor formal |
| API REST |  | Si |  | GET autenticado 200; faltan pruebas completas |
| Static/collectstatic | Si |  |  | `collectstatic --dry-run` OK |
| Seguridad deploy check | Si |  |  | OK con variables productivas simuladas |
| Produccion real |  | Si |  | Falta `.env`, PostgreSQL/infra y prueba manual `runserver`/servidor real |

## 6. Riesgos de entrega

- La suite automatizada esta verde, pero aun es pequena para un sistema de reservas real.
- La API existe, pero no se valido exhaustivamente con pruebas automatizadas.
- El PDF cumple como archivo descargable, pero su implementacion es minima.
- La configuracion de produccion depende de variables que aun no estan documentadas en un `.env.example`.
- La documentacion historica ya no representa completamente el codigo actual.

## 7. Plan recomendado antes de entrega final

1. Crear `.env.example` con `DJANGO_DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `EMAIL_BACKEND` y futura `DATABASE_URL`.
2. Actualizar README/DOCS con rutas reales, comandos reales y alcance actual.
3. Decidir regla de conflictos: si reservas rechazadas liberan horario, ajustar `Reserva.clean()`.
4. Separar validaciones de creacion/edicion de validaciones de cambio de estado.
5. Agregar pruebas API para GET/POST/PUT/DELETE, permisos por rol y acceso a reservas ajenas.
6. Eliminar o corregir `SistemaGestionReservasLaboratorios/templates/app/dashboard.html`.
7. Hacer prueba manual en navegador con `runserver`: login, crear, editar, aprobar, exportar.
8. Para produccion real, migrar de SQLite a PostgreSQL y configurar servidor WSGI/ASGI.

## 8. Diagnostico final

Estado actual: funcional localmente y apto para una entrega academica si el alcance acepta CRUD, permisos, validaciones y reportes basicos.

Nivel estimado actual:

- Accounts/autenticacion: 85%
- Reservas/CRUD/reglas: 80%
- API REST: 55%
- Exportaciones/reportes: 65%
- Configuracion produccion: 70%
- Documentacion: 45%

Porcentaje global estimado: 75% - 85%.

Conclusion: los errores criticos de integracion detectados en la primera auditoria fueron corregidos. El sistema ya funciona en pruebas locales, pero para produccion real quedan pendientes de robustez, documentacion, base de datos productiva, pruebas API y limpieza de artefactos antiguos.
