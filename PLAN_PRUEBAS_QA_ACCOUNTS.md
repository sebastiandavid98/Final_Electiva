# 🧪 PLAN DE PRUEBAS QA - MÓDULO ACCOUNTS
## Sistema de Gestión de Reservas de Laboratorios Universitarios

**Documento:** Plan Integral de Pruebas  
**Módulo:** Autenticación y Autorización (Accounts)  
**Versión:** 1.0  
**Fecha:** Mayo 7, 2026  
**Ingeniero QA:** Especialista en Seguridad Django  

---

## 📋 TABLA DE CONTENIDOS

1. [Alcance y Objetivos](#alcance-y-objetivos)
2. [Ambiente de Pruebas](#ambiente-de-pruebas)
3. [Pruebas Funcionales](#pruebas-funcionales)
4. [Pruebas de Seguridad](#pruebas-de-seguridad)
5. [Pruebas de Autorización y Permisos](#pruebas-de-autorización-y-permisos)
6. [Pruebas de Usabilidad](#pruebas-de-usabilidad)
7. [Pruebas de Rendimiento](#pruebas-de-rendimiento)
8. [Casos de Prueba Detallados](#casos-de-prueba-detallados)
9. [Matriz de Riesgos](#matriz-de-riesgos)
10. [Checklist Final](#checklist-final)

---

## 🎯 ALCANCE Y OBJETIVOS

### Objetivo General
Validar que el módulo de autenticación y autorización cumple con:
- ✅ Todos los requisitos funcionales (RF-01 a RF-10)
- ✅ Todos los requisitos no funcionales (RNF-01 a RNF-07)
- ✅ Estándares de seguridad OWASP
- ✅ Mejores prácticas de Django 4.2

### Objetivos Específicos
1. Verificar autenticación correcta para cada rol
2. Validar control de acceso basado en roles (RBAC)
3. Identificar vulnerabilidades de seguridad
4. Verificar integridad de datos y auditoría
5. Validar experiencia de usuario
6. Medir rendimiento del sistema

### Roles a Probar
- 👨‍🎓 **Estudiante** - Acceso limitado a reservas
- 👨‍🏫 **Docente** - Acceso moderado, puede aprobar
- 👨‍💼 **Administrativo** - Acceso total del sistema

---

## 🏗️ AMBIENTE DE PRUEBAS

### Requisitos Previos
```bash
# Base de datos
Database: PostgreSQL 14+ (o SQLite para desarrollo)
Host: localhost:5432

# Python
Python: 3.10+
Django: 4.2.x
virtualenv: Activo

# Paquetes Requeridos
django-axes==5.40+
django-crispy-forms==2.0+
crispy-bootstrap5==0.7+
django-environ==0.10+
```

### Datos de Prueba Iniciales

```python
# Crear usuarios de prueba
from accounts.models import Usuario
from django.contrib.auth.models import Group, Permission

# Usuario Estudiante
usuario_estudiante = Usuario.objects.create_user(
    username='juan.perez',
    email='juan.perez@universidad.edu',
    password='Test@123456',
    rol='estudiante',
    carrera='Ingeniería en Sistemas'
)

# Usuario Docente
usuario_docente = Usuario.objects.create_user(
    username='carlos.lopez',
    email='carlos.lopez@universidad.edu',
    password='Test@123456',
    rol='docente',
    departamento='Departamento de Ingeniería'
)

# Usuario Administrativo
usuario_admin = Usuario.objects.create_user(
    username='admin.sistema',
    email='admin@universidad.edu',
    password='Test@123456',
    rol='administrativo',
    departamento='Administración'
)

# Superusuario (para testing)
superuser = Usuario.objects.create_superuser(
    username='superuser',
    email='super@universidad.edu',
    password='SuperTest@123456'
)

# Crear grupos (IMPORTANTE EJECUTAR ESTO)
from accounts.permissions import GestorPermisos
GestorPermisos.crear_permisos_personalizados()
GestorPermisos.configurar_grupos_por_rol()
```

### Variables de Entorno para Testing
```bash
# .env.test
DEBUG=True
SECRET_KEY=test-secret-key-for-testing-purposes-only-12345678
DATABASE_URL=sqlite:///test_db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1,testserver
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

## ✅ PRUEBAS FUNCIONALES

### [RF-01] Iniciar sesión con usuario y contraseña

#### TC-001: Login exitoso con credenciales válidas
```
Precondición: Usuario estudiante registrado con credenciales válidas
Pasos:
1. Navegar a /accounts/login/
2. Ingresar username: juan.perez
3. Ingresar password: Test@123456
4. Hacer clic en botón "Entrar"

Resultado Esperado:
✓ Usuario redirigido a /accounts/perfil/
✓ Mensaje de éxito visible
✓ Sesión iniciada (cookie creada)
✓ fecha_ultimo_acceso actualizada en DB

Verificar en DevTools:
- Session cookie presente y válida
- CSRF token actualizado
- No hay errores en consola
```

#### TC-002: Login fallido con contraseña incorrecta
```
Precondición: Usuario registrado
Pasos:
1. Navegar a /accounts/login/
2. Ingresar username: juan.perez
3. Ingresar password: ContraseñaIncorrecta123
4. Hacer clic en "Entrar"

Resultado Esperado:
✓ Usuario NO es autenticado
✓ Mensaje de error: "Usuario o contraseña incorrectos"
✓ Usuario permanece en /accounts/login/
✓ intentos_fallidos incrementa a 1
✓ No se crea sesión

Verificar en BD:
- Usuario.intentos_fallidos = 1
- Usuario.fecha_ultimo_acceso no se actualiza
```

#### TC-003: Login fallido - usuario no existe
```
Precondición: Ninguno
Pasos:
1. Navegar a /accounts/login/
2. Ingresar username: usuario_inexistente
3. Ingresar password: Test@123456
4. Hacer clic en "Entrar"

Resultado Esperado:
✓ Mensaje de error genérico (por seguridad)
✓ Usuario redirigido a /accounts/login/ (mismo formulario)
✓ Log registra intento con usuario inexistente
✓ No se incrementan intentos de usuario (no existe)
```

#### TC-004: Login con campo vacío
```
Precondición: Ninguno
Pasos:
1. Navegar a /accounts/login/
2. Dejar username vacío
3. Llenar password
4. Hacer clic en "Entrar"

Resultado Esperado:
✓ Validación del lado del cliente detiene envío
✓ Validación del lado del servidor muestra error
✓ Mensaje: "Este campo es requerido"
✓ Usuario permanece en formulario
```

---

### [RF-02] Identificar rol del usuario

#### TC-005: Identificación correcta de rol al autenticarse
```
Precondición: 3 usuarios con roles diferentes registrados
Pasos:
1. Login con usuario_estudiante
2. Verificar user.rol en sesión
3. Logout
4. Login con usuario_docente
5. Verificar user.rol en sesión
6. Logout
7. Login con usuario_admin
8. Verificar user.rol en sesión

Resultado Esperado:
✓ Rol correcto para cada usuario
✓ user.rol accesible desde templates
✓ user.get_rol_display() retorna nombre legible

Verificar en BD:
- Usuario.rol almacenado correctamente
- Índice de BD en campo rol funciona
```

#### TC-006: Rol persistente en toda la sesión
```
Precondición: Usuario autenticado como estudiante
Pasos:
1. Login
2. Navegar a /accounts/perfil/
3. Navegar a /accounts/cambiar-contrasena/
4. Volver a /accounts/perfil/
5. Verificar que rol no cambió

Resultado Esperado:
✓ Rol permanece igual en toda la sesión
✓ user.rol accesible en todas las vistas
```

---

### [RF-03] Redirigir a dashboard según rol

#### TC-007: Redirección de Estudiante
```
Precondición: Usuario estudiante autenticado
Pasos:
1. Login como estudiante
2. Observar URL de redirección

Resultado Esperado:
✓ Redirección a /reservas/lista-laboratorios/
✓ No se permite acceso a /dashboard/admin/
✓ Navbar muestra "Estudiante"
```

#### TC-008: Redirección de Docente
```
Precondición: Usuario docente autenticado
Pasos:
1. Login como docente
2. Observar URL de redirección

Resultado Esperado:
✓ Redirección a /reservas/mis-reservas/
✓ Puede ver botón "Aprobar reservas"
```

#### TC-009: Redirección de Administrativo
```
Precondición: Usuario admin autenticado
Pasos:
1. Login como admin
2. Observar URL de redirección

Resultado Esperado:
✓ Redirección a /dashboard/admin/
✓ Acceso a panel de administración
✓ Puede ver "Gestionar usuarios"
```

#### TC-010: Parámetro 'next' en redirección
```
Precondición: Usuario no autenticado
Pasos:
1. Acceder a /accounts/perfil/
2. Ser redirigido a /accounts/login/?next=/accounts/perfil/
3. Hacer login
4. Observar redirección final

Resultado Esperado:
✓ Después de login, redirige a /accounts/perfil/
✓ No va a dashboard, sino al URL especificado en 'next'
```

---

### [RF-04] Cerrar sesión

#### TC-011: Logout exitoso
```
Precondición: Usuario autenticado
Pasos:
1. Hacer clic en "Salir" en navbar
2. Observar redirección y mensajes

Resultado Esperado:
✓ Redirección a /accounts/login/
✓ Mensaje de confirmación: "Sesión cerrada correctamente"
✓ Session cookie eliminada/expirada
✓ User no autenticado (request.user.is_anonymous)

Verificar en BD:
- Sesión eliminada de tabla django_session
- Log registra evento de logout
```

#### TC-012: Acceso a ruta protegida post-logout
```
Precondición: Usuario hace logout
Pasos:
1. Hacer logout
2. Intentar acceder a /accounts/perfil/
3. Intentar acceder a /accounts/cambiar-contrasena/

Resultado Esperado:
✓ Redirigido a /accounts/login/
✓ Mensaje: "Debes iniciar sesión"
✓ Parámetro next preservado en URL
```

---

### [RF-05] Mostrar perfil del usuario

#### TC-013: Visualización de datos de perfil
```
Precondición: Usuario autenticado
Pasos:
1. Login
2. Navegar a /accounts/perfil/
3. Verificar datos mostrados

Resultado Esperado:
✓ Muestra username
✓ Muestra email
✓ Muestra teléfono
✓ Muestra carrera (estudiante) o departamento (otros)
✓ Muestra fecha del último acceso
✓ Muestra rol del usuario
✓ Todos los datos son correctos de BD

Verificar en Template:
- No hay datos sensibles expuestos innecesariamente
- Contraseña NO se muestra
- Tokens NO se exponen
```

#### TC-014: Edición de datos de perfil
```
Precondición: Usuario autenticado en /accounts/perfil/
Pasos:
1. Modificar email a "nuevo@email.com"
2. Modificar teléfono a "+57-3001234567"
3. Hacer clic en guardar

Resultado Esperado:
✓ Mensaje de confirmación
✓ Datos se actualizan en BD
✓ Cambios visibles inmediatamente después de guardar
✓ Otros datos no se modifican

Verificar en BD:
- Usuario.email actualizado
- Usuario.telefono actualizado
- fecha_ultimo_acceso NO se modifica (es solo lectura)
```

---

### [RF-06] Cambiar contraseña

#### TC-015: Cambio exitoso de contraseña
```
Precondición: Usuario autenticado
Pasos:
1. Navegar a /accounts/cambiar-contrasena/
2. Ingresar contraseña actual: Test@123456
3. Ingresar nueva contraseña: NewPass@789012
4. Confirmar nueva contraseña: NewPass@789012
5. Hacer clic en guardar

Resultado Esperado:
✓ Mensaje: "Contraseña actualizada correctamente"
✓ Sesión se mantiene activa (update_session_auth_hash)
✓ Nueva contraseña funciona en próximo login
✓ Contraseña anterior no funciona

Verificar en BD:
- Usuario.password hasheada y diferente
- Log registra cambio de contraseña

Verificar en Log:
- Evento: "Cambio de contraseña: [username]"
```

#### TC-016: Validación de contraseña actual incorrecta
```
Precondición: Usuario autenticado
Pasos:
1. Navegar a /accounts/cambiar-contrasena/
2. Ingresar contraseña actual: ContraseñaIncorrecta
3. Ingresar nueva contraseña: NewPass@789012
4. Hacer clic en guardar

Resultado Esperado:
✓ Error: "La contraseña actual es incorrecta"
✓ Contraseña NO se cambia
✓ Usuario permanece en formulario

Verificar en BD:
- Usuario.password sin cambios
```

#### TC-017: Validación de fortaleza de contraseña
```
Precondición: Usuario autenticado en cambiar contraseña
Pasos:
1. Ingresar nueva contraseña: "123" (débil)
2. Ver mensajes de validación

Resultado Esperado:
✓ Error: "Contraseña muy corta"
✓ Error: "Contraseña muy común"
✓ Error: "Contraseña debe contener mayúsculas, minúsculas, números"

Casos a probar:
- Contraseña muy corta: "Pass1"
- Contraseña común: "password123"
- Sin mayúsculas: "test@123456"
- Sin números: "TestPassword@"
- Solo números: "123456789"
```

#### TC-018: Validación de coincidencia de contraseñas
```
Precondición: Usuario autenticado
Pasos:
1. Ingresar nueva contraseña: NewPass@789012
2. Confirmar diferente: DifferentPass@789012
3. Hacer clic en guardar

Resultado Esperado:
✓ Error: "Las contraseñas no coinciden"
✓ Contraseña NO se cambia
```

---

### [RF-07] Recuperar contraseña por email

#### TC-019: Solicitud de recuperación de contraseña
```
Precondición: Usuario registrado
Pasos:
1. Navegar a /accounts/password-reset/
2. Ingresar email: juan.perez@universidad.edu
3. Hacer clic en "Enviar"

Resultado Esperado:
✓ Redirección a /accounts/password-reset/done/
✓ Mensaje: "Correo enviado con instrucciones"
✓ Email recibido en bandeja (test backend: console)
✓ Email contiene link de reset con token válido

Verificar en Email:
- Contiene nombre del usuario
- Contiene URL con uidb64 y token válidos
- Contiene instrucciones claras
- No expone contraseña anterior
```

#### TC-020: Reset de contraseña con token válido
```
Precondición: Email de reset recibido con token válido
Pasos:
1. Hacer clic en link del email
2. Ingresar nueva contraseña: NewPass@999888
3. Confirmar: NewPass@999888
4. Hacer clic en guardar

Resultado Esperado:
✓ Redirección a /accounts/reset/done/
✓ Mensaje: "Contraseña restablecida exitosamente"
✓ Nueva contraseña funciona para login

Verificar en BD:
- Usuario.password actualizada
- Token invalidado
```

#### TC-021: Validación de token expirado
```
Precondición: Token de reset ha expirado (>1 hora en desarrollo)
Pasos:
1. Intentar usar token expirado del URL

Resultado Esperado:
✓ Mensaje de error
✓ Link para solicitar nuevo reset
✓ Usuario puede solicitar reset nuevamente
```

#### TC-022: Email no registrado en sistema
```
Precondición: Ninguno
Pasos:
1. Navegar a /accounts/password-reset/
2. Ingresar email no registrado: noexiste@universidad.edu
3. Hacer clic en enviar

Resultado Esperado:
✓ Redirección a /accounts/password-reset/done/ (por seguridad)
✓ No se envía email
✓ No expone información de usuarios existentes
```

---

### [RF-08] Restringir accesos según permisos

#### TC-023: Acceso denegado a vista protegida
```
Precondición: Usuario estudiante autenticado
Pasos:
1. Login como estudiante
2. Intentar acceder a /accounts/usuarios/ (solo admin)

Resultado Esperado:
✓ HTTP 403 Forbidden
✓ Página de error: "No tienes permiso para acceder"
✓ Usuario se mantiene autenticado
✓ Log registra intento de acceso no autorizado
```

#### TC-024: Acceso permitido con permiso correcto
```
Precondición: Usuario admin autenticado
Pasos:
1. Login como admin
2. Acceder a /accounts/usuarios/

Resultado Esperado:
✓ HTTP 200 OK
✓ Lista de usuarios visible
✓ Puede editar/eliminar usuarios
```

#### TC-025: Acceso no autenticado
```
Precondición: Ninguno
Pasos:
1. Intentar acceder a /accounts/perfil/ sin autenticación

Resultado Esperado:
✓ Redirigido a /accounts/login/
✓ Parámetro next prefieja: /accounts/login/?next=/accounts/perfil/
✓ Mensaje opcional: "Debes iniciar sesión"
```

---

### [RF-09] Registrar intentos de login fallidos

#### TC-026: Registro de intentos fallidos
```
Precondición: Usuario existe pero no está bloqueado
Pasos:
1. Intentar login con contraseña incorrecta 1 vez
2. Verificar BD

Resultado Esperado:
✓ Usuario.intentos_fallidos = 1
✓ Log contiene: "Login fallido para usuario: juan.perez"
✓ Log contiene timestamp
✓ Log contiene detalles del intento

Repetir 3 veces más y verificar:
- Usuario.intentos_fallidos = 4 después de 4 intentos
```

#### TC-027: Log de intento exitoso resetea contador
```
Precondición: Usuario tiene intentos_fallidos = 4
Pasos:
1. Login exitoso con contraseña correcta

Resultado Esperado:
✓ Usuario.intentos_fallidos se resetea a 0
✓ Usuario.bloqueado_hasta se limpia
✓ Log registra: "Login exitoso: juan.perez - Rol: Estudiante"
```

#### TC-028: Registro por IP en cache
```
Precondición: Ninguno
Pasos:
1. Desde múltiples IPs, intentar login 11 veces en 5 minutos

Resultado Esperado:
✓ Cache mantiene count por IP: login_attempts_[IP]
✓ Después de 10 intentos desde misma IP, bloquea
✓ Log registra: "Demasiados intentos desde IP: [IP]"
```

---

### [RF-10] Bloqueo temporal después de 5 intentos

#### TC-029: Bloqueo automático después de 5 intentos
```
Precondición: Usuario tiene 0 intentos_fallidos
Pasos:
1. Intentar login fallido 5 veces (diferentes contraseñas)
2. Intentar 6to login con contraseña correcta

Resultado Esperado:
Después de intento 5:
✓ Usuario.intentos_fallidos = 5
✓ Usuario.bloqueado_hasta = NOW() + 30 minutos
✓ Message: "Cuenta bloqueada hasta [HH:MM]"

En intento 6:
✓ Mensaje de error aunque contraseña sea correcta
✓ Usuario no es autenticado
✓ Log registra: "Intento de acceso a cuenta bloqueada: juan.perez"
```

#### TC-030: Desbloqueo automático después de 30 minutos
```
Precondición: Usuario está bloqueado (bloqueado_hasta = ahora + 30 min)
Pasos:
1. Esperar 30+ minutos (o simular con freeze_time en tests)
2. Intentar login con contraseña correcta

Resultado Esperado:
✓ Usuario.esta_bloqueado() retorna False
✓ Login funciona
✓ Sesión se crea
✓ Log registra desbloqueo automático

Verificar en BD:
- Usuario.bloqueado_hasta ahora es en el pasado
```

#### TC-031: Desbloqueo manual por admin
```
Precondición: Usuario está bloqueado
Pasos:
1. Admin accede a panel de administración
2. Busca usuario bloqueado
3. Ejecuta resetear_intentos()

Resultado Esperado:
✓ Usuario.intentos_fallidos = 0
✓ Usuario.bloqueado_hasta = None
✓ Usuario puede hacer login inmediatamente
```

---

## 🔒 PRUEBAS DE SEGURIDAD

### OWASP Top 10 - Validación

#### [A01:2021] Broken Access Control

##### TC-032: Falta de autenticación no permite acceso
```
Precondición: Ninguno (no autenticado)
Pasos:
1. Intentar acceder a /accounts/perfil/
2. Intentar acceder a /accounts/cambiar-contrasena/
3. Intentar acceder a /accounts/usuarios/

Resultado Esperado:
✓ Todas las rutas redirigen a /accounts/login/
✓ El middleware intercepta requests no autenticadas
✓ No hay exposición de datos
```

##### TC-033: Middleware verifica permisos por rol
```
Precondición: Usuarios con diferentes roles autenticados
Pasos:
1. Estudiante intenta acceder a /accounts/usuarios/
2. Docente intenta acceder a /admin/
3. Admin intenta acceder a /reportes/ (aunque no existe)

Resultado Esperado:
✓ HTTP 403 para estudiante en /accounts/usuarios/
✓ HTTP 403 para docente en /admin/ (si no tiene permiso)
✓ Errores registrados en logs

Verificar Middleware:
- VerificarPermisosMiddleware funciona correctamente
- URLS_POR_ROL se respeta
```

##### TC-034: Escalación de privilegios imposible
```
Precondición: Usuario estudiante autenticado
Pasos:
1. Intentar modificar user.rol en request (inyección)
2. Intentar modificar request.user.groups
3. Intentar cambiar flag is_staff

Resultado Esperado:
✓ Cambios no se persisten
✓ BD mantiene rol original
✓ Permiso rechazado por decorador
✓ Log registra intento de escalación
```

---

#### [A02:2021] Cryptographic Failures

##### TC-035: Contraseñas hasheadas con PBKDF2
```
Precondición: Usuario registrado
Pasos:
1. Ir a BD
2. Buscar tabla de usuarios
3. Examinar campo password

Resultado Esperado:
✓ Password NO está en texto plano
✓ Password comienza con "pbkdf2_sha256$" (hash PBKDF2)
✓ Hash tiene >100k iteraciones
✓ Hash diferente al mismo en otra BD

Verificar en settings.py:
- PASSWORD_HASHERS[0] = PBKDF2PasswordHasher
```

##### TC-036: HTTPS en producción
```
Precondición: DEBUG=False en settings.py
Pasos:
1. Intentar acceder a http:// (sin SSL)

Resultado Esperado:
✓ SECURE_SSL_REDIRECT = True
✓ Request redirige a https://
✓ HSTS header presente (Strict-Transport-Security)
✓ CSRF_COOKIE_SECURE = True
✓ SESSION_COOKIE_SECURE = True

Verificar en settings:
- SECURE_HSTS_SECONDS > 0
- SECURE_SSL_REDIRECT = True
```

##### TC-037: Sesión segura (cookies)
```
Precondición: Usuario autenticado
Pasos:
1. Usar DevTools → Application → Cookies
2. Inspeccionar session cookie

Resultado Esperado:
✓ Cookie tiene flag Secure (solo HTTPS)
✓ Cookie tiene flag HttpOnly (no accesible desde JS)
✓ Cookie tiene SameSite=Strict o Lax
✓ Cookie expira en 30 minutos (1800s)

Verificar en settings:
- SESSION_COOKIE_AGE = 1800
- SESSION_COOKIE_SECURE = True
- SESSION_COOKIE_HTTPONLY = True
```

---

#### [A03:2021] Injection

##### TC-038: SQL Injection en login
```
Precondición: Formulario de login accesible
Pasos:
1. Ingresar username: admin' OR '1'='1
2. Ingresar password: test
3. Observar resultado

Resultado Esperado:
✓ Login falla (no se inyecta SQL)
✓ Mensaje: "Usuario o contraseña incorrectos"
✓ BD intacta, sin cambios
✓ ORM de Django previene SQL injection

Verificar:
- No usar raw SQL en queries
- Usar QuerySet de Django
- No concatenar strings en queries
```

##### TC-039: XSS en formularios
```
Precondición: Formulario de cambio de perfil
Pasos:
1. En campo email ingresar: <script>alert('XSS')</script>@test.com
2. En campo telefono: <img src=x onerror=alert('XSS')>
3. Guardar

Resultado Esperado:
✓ Script NO se ejecuta
✓ Datos se almacenan escapados
✓ Al renderizar, muestra como texto (no código)
✓ No hay alert() ejecutado

Verificar en template:
- {{ user.email }} no tiene |safe
- {{ user.telefono }} escapado
- Django escapa por defecto
```

##### TC-040: CSRF Protection
```
Precondición: Formulario POST en cambiar contraseña
Pasos:
1. Inspeccionar HTML del formulario
2. Buscar CSRF token
3. Intentar enviar POST sin token

Resultado Esperado:
✓ CSRF token presente en formulario: {% csrf_token %}
✓ Token único por sesión
✓ POST sin token: HTTP 403 Forbidden
✓ Mensaje: "CSRF token missing or incorrect"

Verificar en middleware:
- CsrfViewMiddleware activo
- CSRF_COOKIE_SECURE = True en producción
```

---

#### [A04:2021] Insecure Design

##### TC-041: Validación de email
```
Precondición: Registro o edición de perfil
Pasos:
1. Ingresar email inválido: "notanemail"
2. Ingresar email válido: "usuario@universidad.edu"
3. Ingresar email con dominio peligroso: "user@malicious-site.com"

Resultado Esperado:
✓ Email inválido rechazado
✓ Email válido aceptado
✓ No hay validación del dominio (por diseño)
✓ Email almacenado tal como se ingresó

Verificar en forms.py:
- EmailField con validación
- Usar django.core.validators.validate_email
```

##### TC-042: Validación de teléfono
```
Precondición: Edición de perfil
Pasos:
1. Ingresar teléfono inválido: "abc123"
2. Ingresar formato válido: "+57-3001234567"
3. Ingresar formato válido: "3001234567"

Resultado Esperado:
✓ "abc123" rechazado
✓ "+57-3001234567" aceptado
✓ "3001234567" aceptado (9-15 dígitos)
✓ Validación usa RegexValidator

Verificar Regex:
- Pattern: ^\+?1?\d{9,15}$
- Protege contra inyecciones
```

##### TC-043: Rate Limiting por IP
```
Precondición: Acceso a /accounts/login/
Pasos:
1. Enviar 11 requests POST a login desde misma IP en 5 min
2. Observar respuesta del 11to request

Resultado Esperado:
✓ Cache implementado: login_attempts_{ip}
✓ Después de 10 intentos desde IP: bloquea
✓ Mensaje: "Demasiados intentos. Espera 5 minutos"
✓ Espera 5 minutos automáticamente

Verificar en views.py:
- cache.get() y cache.set() implementados
- Timeout = 300 segundos
```

---

#### [A06:2021] Vulnerable and Outdated Components

##### TC-044: Versiones de dependencias
```
Precondición: pip list ejecutado
Pasos:
1. Verificar versiones instaladas

Resultado Esperado:
✓ django==4.2.x (versión LTS)
✓ django-axes>=5.40 (actualizado)
✓ django-crispy-forms>=2.0
✓ Ninguna versión con CVE conocido

Comando:
pip check
pip list | grep -i django
```

##### TC-045: Django Security Updates
```
Precondición: Django 4.2 instalado
Pasos:
1. Verificar que no hay warnings de Django

Resultado Esperado:
✓ ./manage.py check --deploy muestra OK
✓ Sin warnings de seguridad
✓ Sin advertencias de configuración

Comando:
python manage.py check
python manage.py check --deploy
```

---

#### [A07:2021] Identification and Authentication Failures

##### TC-046: Brute Force Attack Prevention
```
Precondición: Usuario existe
Pasos:
1. Intentar 50 requests POST con diferentes contraseñas
   en < 1 minuto desde misma IP

Resultado Esperado:
✓ Django-Axes intercepta después de 5 intentos
✓ Usuario cuenta se bloquea por 30 minutos
✓ IP cuenta se bloquea después de 10 intentos
✓ Log registra todos los intentos
✓ Admin alertado (opcional con signals)
```

##### TC-047: Session Fixation Prevention
```
Precondición: Navegador con cookie de sesión
Pasos:
1. Copiar session ID antes de login
2. Login como usuario
3. Verificar session ID después de login

Resultado Esperado:
✓ Session ID cambia después de login
✓ Antigua sesión se invalida
✓ Nueva sesión asignada a usuario autenticado

Verificar en views.py login_view:
- login(request, user) regenera sesión
```

##### TC-048: Account Enumeration Protection
```
Precondición: Formulario de password reset
Pasos:
1. Solicitar reset para email registrado
2. Solicitar reset para email no registrado
3. Comparar respuestas

Resultado Esperado:
✓ Ambas solicitudes muestran mismo mensaje
✓ Ambas redirigen a misma página
✓ No expone información de usuarios existentes
✓ Si email existe, se envía email (silenciosamente)
```

---

#### [A09:2021] Logging and Monitoring Failures

##### TC-049: Eventos de seguridad registrados
```
Precondición: Sistema en uso
Pasos:
1. Realizar login exitoso
2. Realizar login fallido
3. Intentar acceso no autorizado
4. Cambiar contraseña
5. Verificar logs

Resultado Esperado:
✓ logs/security.log contiene todos los eventos
✓ Cada evento tiene timestamp
✓ Cada evento tiene nivel: INFO, WARNING, ERROR
✓ Información sensible NO está en logs (passwords, tokens)

Eventos a verificar:
- "Login exitoso: [username] - Rol: [rol]"
- "Login fallido para usuario: [username]"
- "Intento de acceso a cuenta bloqueada: [username]"
- "Acceso denegado: [username] intentó acceder a [url]"
- "Cambio de contraseña: [username]"
- "Logout: [username]"
```

##### TC-050: Log Rotation y limpieza
```
Precondición: Logs generados por varios días
Pasos:
1. Verificar tamaño de logs/security.log
2. Verificar si existe rotación

Resultado Esperado:
✓ Logs rotan por tamaño o fecha
✓ No consume disco infinitamente
✓ Logs antiguos se archivan o eliminan

Configuración esperada:
- RotatingFileHandler con maxBytes
- Múltiples backups (security.log.1, security.log.2, etc.)
```

---

#### [A10:2021] Server-Side Request Forgery (SSRF)

##### TC-051: No se ejecutan URLs arbitrarias
```
Precondición: Login view
Pasos:
1. Intentar redirigir a URL externa en parámetro 'next'
2. next=/accounts/login/?next=http://malicious.com

Resultado Esperado:
✓ No redirige a sitio externo
✓ Redirige solo a URLs internas
✓ Validación de URL safe

Verificar en views.py:
- Usar django.shortcuts.redirect (safe)
- NO usar request.GET['next'] directamente
```

---

## 👥 PRUEBAS DE AUTORIZACIÓN Y PERMISOS

### Matriz de Pruebas por Rol

#### TC-052: Permisos de Estudiante
```
Permisos esperados:
- puede_reservar_laboratorio: ✓
- puede_aprobar_reservas: ✗
- puede_ver_todas_reservas: ✗
- puede_gestionar_usuarios: ✗
- puede_ver_reportes: ✗

Acciones permitidas:
- Ver perfil propio
- Cambiar contraseña propia
- Hacer reservas de laboratorios
- Ver solo sus reservas

Acciones denegadas:
- Ver lista de usuarios
- Aprobar reservas de otros
- Acceder a /admin/
- Ver reportes del sistema

Verificar con has_perm():
from django.contrib.auth.models import Permission
user = Usuario.objects.get(username='juan.perez')
assert user.has_perm('accounts.puede_reservar_laboratorio') == True
assert user.has_perm('accounts.puede_ver_reportes') == False
```

#### TC-053: Permisos de Docente
```
Permisos esperados:
- puede_reservar_laboratorio: ✓
- puede_aprobar_reservas: ✓
- puede_ver_todas_reservas: ✗
- puede_gestionar_usuarios: ✗
- puede_ver_reportes: ✗

Acciones permitidas:
- Todo lo de estudiante
- Aprobar/rechazar reservas de sus grupos
- Ver reservas de sus estudiantes
- Modificar disponibilidad de laboratorios (su departamento)

Acciones denegadas:
- Gestionar otros docentes
- Ver reportes de facturación
- Acceder a panel de admin

Verificar:
@requerir_permiso('puede_aprobar_reservas')
def aprobar_reservas(request):
    # Solo docentes y admin llegan aquí
```

#### TC-054: Permisos de Administrativo
```
Permisos esperados:
- puede_reservar_laboratorio: ✓
- puede_aprobar_reservas: ✓
- puede_ver_todas_reservas: ✓
- puede_gestionar_usuarios: ✓
- puede_ver_reportes: ✓
- is_staff (opcional): ✓
- admin_access: ✓

Acciones permitidas:
- TODO en el sistema
- Crear/editar/eliminar usuarios
- Aprobar todas las reservas
- Ver reportes y estadísticas
- Acceso a Django admin
- Configurar permisos de otros usuarios

Verificar:
user = Usuario.objects.get(username='admin.sistema')
assert user.has_perm('accounts.puede_gestionar_usuarios') == True
assert user.has_perm('accounts.puede_ver_todas_reservas') == True
```

#### TC-055: Grupos asignados automáticamente
```
Precondición: Usuario nuevo registrado
Pasos:
1. Crear usuario con rol='estudiante'
2. Verificar grupos asignados
3. Repetir para docente y admin

Resultado Esperado:
Señal post_save asigna automáticamente:
✓ Estudiante → Group 'estudiante'
✓ Docente → Group 'docente'
✓ Admin → Group 'administrativo'

Verificar en BD:
- Tabla auth_user_groups contiene asignaciones
- Grupo tiene permisos correctos

Código de prueba:
from accounts.models import Usuario
from django.contrib.auth.models import Group

user = Usuario.objects.create_user(
    username='test.student',
    password='test',
    rol='estudiante'
)
assert Group.objects.get(name='estudiante') in user.groups.all()
```

#### TC-056: Cambio de rol actualiza grupos
```
Precondición: Usuario es estudiante
Pasos:
1. Cambiar rol de 'estudiante' a 'docente'
2. Guardar usuario
3. Verificar grupos

Resultado Esperado:
Señal pre_save actualiza grupos:
✓ Removido de 'estudiante'
✓ Agregado a 'docente'
✓ Permisos actualizados dinámicamente

Verificar:
- Tabla auth_user_groups actualizada
- Nuevo grupo tiene permisos de docente
- Permisos antiguos removidos
```

---

### Decoradores Personalizados

#### TC-057: Decorador @requerir_rol
```
Precondición: Vista protegida con @requerir_rol('docente', 'administrativo')
Pasos:
1. Estudiante intenta acceder
2. Docente intenta acceder
3. Admin intenta acceder

Resultado Esperado:
✓ Estudiante: HTTP 403 Forbidden
✓ Docente: HTTP 200 OK
✓ Admin: HTTP 200 OK (superuser siempre pasa)

Mensaje de error esperado:
"No tienes permisos para acceder a esta sección"
```

#### TC-058: Decorador @requerir_permiso
```
Precondición: Vista con @requerir_permiso('puede_ver_reportes')
Pasos:
1. Estudiante accede
2. Docente accede
3. Admin accede

Resultado Esperado:
✓ Estudiante: HTTP 403
✓ Docente: HTTP 403 (no tiene permiso)
✓ Admin: HTTP 200 OK

Mensaje: "Se requiere permiso: puede_ver_reportes"
```

#### TC-059: @login_required + @requerir_rol
```
Precondición: Vista con @login_required y @requerir_rol
Pasos:
1. No autenticado intenta acceder
2. Estudiante intenta acceder
3. Docente accede

Resultado Esperado:
✓ No autenticado: Redirige a login
✓ Estudiante: HTTP 403
✓ Docente: HTTP 200
✓ Decoradores se aplican en orden correcto
```

---

## 🎨 PRUEBAS DE USABILIDAD

### Frontend y UX

#### TC-060: Template de login responsive
```
Precondición: Acceder a /accounts/login/
Pasos:
1. En navegador desktop (1920x1080)
2. En tablet (768x1024)
3. En móvil (375x667)

Resultado Esperado:
✓ Formulario visible y usable en todas las resoluciones
✓ Botón "Entrar" clickeable en móvil
✓ Campos de input accesibles
✓ No hay scrolling horizontal innecesario

Bootstrap 5 Classes:
- .container
- .row .justify-content-center
- .col-md-4
- .form-control (inputs)
- .btn .btn-primary
```

#### TC-061: Mensajes de error claros
```
Precondición: Intentar login fallido
Pasos:
1. Ingresar contraseña incorrecta
2. Ver mensaje de error
3. Intentar acceso bloqueado
4. Ver mensaje de bloqueo

Resultado Esperado:
✓ Mensajes comprensibles para usuario final
✓ Color rojo para errores (Bootstrap alert-danger)
✓ Color verde para éxitos (Bootstrap alert-success)
✓ Mensajes No exponen internals del sistema

Mensajes apropiados:
✓ "Usuario o contraseña incorrectos"
✗ "Usuario no encontrado en tabla de usuarios"
```

#### TC-062: Feedback visual de validación
```
Precondición: Formulario de cambio de contraseña
Pasos:
1. Campo con error debe resaltarse
2. Mensaje de error junto al campo
3. Campo válido no debe tener alerta

Resultado Esperado:
✓ Campos con error tienen clase .is-invalid
✓ Mensaje de error en .invalid-feedback
✓ Campos válidos limpios
✓ Atributos aria-* para accesibilidad

Bootstrap 5:
- .form-control.is-invalid
- .invalid-feedback
```

#### TC-063: Navegación clara y consistente
```
Precondición: Usuario autenticado
Pasos:
1. Navegar desde login a perfil
2. Navegar desde perfil a cambiar contraseña
3. Navegar desde cambiar contraseña a perfil
4. Ir a logout

Resultado Esperado:
✓ Navbar consistente en todas las páginas
✓ Usuario actual visible en navbar
✓ Rol visible en navbar
✓ Botón "Salir" siempre accesible
✓ Breadcrumbs o indicador de ubicación

Navbar esperado:
- Logo/Inicio
- Nombre de usuario | Rol
- Link a Perfil
- Link a Salir
```

#### TC-064: Formularios con validación cliente
```
Precondición: Formulario de login
Pasos:
1. Dejar campo vacío e intentar enviar
2. Ingresar email inválido en perfil

Resultado Esperado:
✓ Validación HTML5 (required, type=email)
✓ Mensaje: "Este campo es obligatorio"
✓ Email inválido rechazado antes de enviar
✓ No se envía POST al servidor

Atributos esperados:
- input type="email" required
- input type="password" required
- input minlength="8" (contraseña)
```

#### TC-065: Confirmación antes de acciones destructivas
```
Precondición: Panel de admin con opción de eliminar usuario
Pasos:
1. Hacer clic en "Eliminar" para usuario
2. Ver diálogo de confirmación

Resultado Esperado:
✓ Modal/confirmación aparecer
✓ Advertencia clara del riesgo
✓ Botones: "Cancelar" y "Confirmar"
✓ Si cancela, nada pasa
✓ Si confirma, se ejecuta acción
```

---

### Accesibilidad

#### TC-066: WCAG 2.1 Level AA Compliance
```
Precondición: Todas las páginas del módulo
Pasos:
1. Usar herramienta axe DevTools
2. Usar WAVE Browser Extension
3. Verificar colores y contraste

Resultado Esperado:
✓ Contraste de texto ≥ 4.5:1
✓ Elementos interactivos tabulables
✓ Labels asociados a inputs
✓ Jerarquía de headings correcta (h1, h2, h3...)
✓ Sin errores WCAG en herramientas

Elementos a revisar:
- Labels: <label for="id_username">
- Botones: <button type="submit">
- Contraste: Negro (#000) sobre blanco (#fff) = 21:1
```

#### TC-067: Navegación por teclado
```
Precondición: Formulario de login
Pasos:
1. Usar Solo Tab para navegar
2. Usar Tab + Shift para ir atrás
3. Usar Enter para enviar formulario

Resultado Esperado:
✓ Todos los campos navegables con Tab
✓ Botón "Entrar" es último elemento
✓ Orden de tabulación lógico
✓ Focus visible en cada elemento (outline)
✓ Forma se envía con Enter en último campo
```

#### TC-068: Lectores de pantalla
```
Precondición: Usar NVDA o JAWS
Pasos:
1. Navegar la página login
2. Llenar formulario
3. Enviar

Resultado Esperado:
✓ Lector dice: "Username, edit text"
✓ Lector dice: "Password, edit text"
✓ Lector dice: "Enter, button"
✓ Mensajes de error anunciados
✓ Rol del usuario comunicado en navbar
```

---

## ⚡ PRUEBAS DE RENDIMIENTO

#### TC-069: Tiempo de respuesta en login
```
Precondición: Usuario existe, BD poblada
Pasos:
1. Hacer 10 requests de login
2. Medir tiempo de respuesta
3. Calcular promedio

Resultado Esperado:
✓ Tiempo promedio < 500ms (RNF-04)
✓ Ningún request > 1000ms
✓ Consistencia en tiempos

Herramientas:
- Django Debug Toolbar
- Chrome DevTools Network tab
- Apache ab: ab -n 100 -c 10 http://localhost:8000/accounts/login/

Código para medir:
import time
start = time.time()
response = client.post('/accounts/login/', {...})
elapsed = time.time() - start
assert elapsed < 0.5  # 500ms
```

#### TC-070: Consultas BD en login view
```
Precondición: Vista de login
Pasos:
1. Usar django-debug-toolbar
2. Ver pestaña SQL
3. Contar queries

Resultado Esperado:
✓ Máximo 5 queries por login
- 1 para verificar usuario existe
- 1 para obtener usuario y rol
- 1-2 para permisos/grupos
- 1 para crear/actualizar sesión

NO esperado:
✗ N+1 queries problem
✗ Queries no optimizadas con select_related/prefetch_related
```

#### TC-071: Caché de intentos fallidos
```
Precondición: Múltiples intentos fallidos
Pasos:
1. Hacer 10 intentos fallidos
2. Verificar que cache reduce BD queries

Resultado Esperado:
✓ Cache (memcached/redis) usado
✓ login_attempts_[IP] cacheado 5 minutos
✓ Menos queries a BD por verificación de IP
✓ Rendimiento mejorado en high traffic

Configuración:
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

#### TC-072: Rendimiento bajo carga
```
Precondición: Herramienta de load testing (Locust/JMeter)
Pasos:
1. Simular 100 usuarios simultáneos
2. Intentar login
3. Navegar a perfil
4. Monitorear recursos

Resultado Esperado:
✓ p95 latency < 1000ms
✓ p99 latency < 2000ms
✓ Error rate < 1%
✓ CPU < 80%
✓ Memoria < 80%

Ejemplo Locust:
from locust import HttpUser, task

class LoginUser(HttpUser):
    @task
    def login(self):
        self.client.post("/accounts/login/", {
            "username": "test",
            "password": "test"
        })
```

#### TC-073: Tiempo de migración
```
Precondición: Migración de accounts
Pasos:
1. Borrar BD
2. Medir tiempo de makemigrations
3. Medir tiempo de migrate

Resultado Esperado:
✓ makemigrations < 5 segundos
✓ migrate < 10 segundos
✓ Sin errores de SQL
✓ Sin deadlocks en BD

Comando:
time python manage.py makemigrations accounts
time python manage.py migrate accounts
```

---

## 🧬 CASOS DE PRUEBA DETALLADOS

### Escenario 1: Ciclo Completo de Login - Estudiante

```gherkin
Feature: Login Flujo Completo Estudiante

Scenario: Estudiante hace login y accede a su perfil
  Given que soy un usuario no autenticado
  And estoy en la página /accounts/login/
  
  When ingreso username "juan.perez"
  And ingreso password "Test@123456"
  And hago clic en botón "Entrar"
  
  Then debo ser redirigido a /reservas/lista-laboratorios/
  And debo ver un mensaje de bienvenida
  And mi rol debe ser "Estudiante"
  And la fecha_ultimo_acceso debe actualizarse en BD
  And debo ver mi nombre en el navbar

Scenario: Estudiante intenta acceder a funcionalidad de admin
  Given que soy un estudiante autenticado
  And estoy en /reservas/lista-laboratorios/
  
  When intento acceder a /accounts/usuarios/
  
  Then recibo error HTTP 403 Forbidden
  And veo mensaje "No tienes permiso"
  And permanezco autenticado (no me hace logout)
  And el intento se registra en logs de seguridad

Scenario: Estudiante cambia contraseña y logout
  Given que soy estudiante autenticado
  And estoy en /accounts/perfil/
  
  When hago clic en "Cambiar contraseña"
  And ingreso contraseña actual: "Test@123456"
  And ingreso nueva: "NewPass@789012"
  And confirmo: "NewPass@789012"
  And hago clic en guardar
  
  Then veo mensaje "Contraseña actualizada"
  And mi sesión se mantiene activa
  And cuando hago logout
  Then veo "Sesión cerrada correctamente"
  And soy redirigido a /accounts/login/
```

### Escenario 2: Ataque de Fuerza Bruta

```gherkin
Feature: Protección Contra Ataque Brute Force

Scenario: Usuario bloqueado después de 5 intentos fallidos
  Given que usuario "carlos.lopez" existe
  
  When intento login con contraseña incorrecta 5 veces
  Then en el intento 5:
    - Usuario.intentos_fallidos = 5
    - Usuario.bloqueado_hasta = NOW() + 30 min
    
  When intento login con contraseña CORRECTA en intento 6
  Then veo error "Cuenta bloqueada hasta [HH:MM]"
  And login falla
  And log registra "Intento de acceso a cuenta bloqueada"

Scenario: Desbloqueo automático después de 30 minutos
  Given que usuario está bloqueado
  And Usuario.bloqueado_hasta = NOW() + 30 min
  
  When esperan 30+ minutos
  
  Then User.esta_bloqueado() retorna False
  And puedo hacer login con contraseña correcta
  And User.intentos_fallidos se resetea a 0
```

### Escenario 3: Recuperación de Contraseña

```gherkin
Feature: Recuperación de Contraseña por Email

Scenario: Reset exitoso de contraseña
  Given que soy usuario no autenticado
  And estoy en /accounts/password-reset/
  
  When ingreso email "juan.perez@universidad.edu"
  And hago clic en "Enviar"
  
  Then soy redirigido a /accounts/password-reset/done/
  And veo mensaje "Email enviado con instrucciones"
  And email es recibido en bandeja (console backend)
  
  When hago clic en link del email
  Then accedo a /reset/[uidb64]/[token]/
  
  When ingreso nueva contraseña "ResetPass@999888"
  And confirmo "ResetPass@999888"
  And hago clic en guardar
  
  Then veo /accounts/reset/done/
  And mensaje "Contraseña restablecida"
  
  When intento login con nueva contraseña
  Then login es exitoso
  And usuario autenticado
```

### Escenario 4: Control de Acceso por Rol

```gherkin
Feature: Control de Acceso Basado en Roles

Scenario Outline: Acceso por rol a diferentes rutas
  Given usuario con rol <rol> autenticado
  
  When intento acceder a <ruta>
  
  Then el resultado es <resultado>
  And si es 200, veo contenido de <rol>

Examples:
  | rol             | ruta                    | resultado |
  | estudiante      | /accounts/perfil/       | 200       |
  | estudiante      | /accounts/usuarios/     | 403       |
  | docente         | /accounts/perfil/       | 200       |
  | docente         | /accounts/usuarios/     | 403       |
  | administrativo  | /accounts/perfil/       | 200       |
  | administrativo  | /accounts/usuarios/     | 200       |
  | no autenticado  | /accounts/perfil/       | 302 login |

Scenario: Escalación de privilegios imposible
  Given usuario estudiante autenticado
  And estudiante intenta inyectar rol='administrativo' en BD
  
  Then cambio no persiste
  And usuario sigue teniendo rol='estudiante'
  And intento se registra en logs de seguridad
```

---

## 📊 MATRIZ DE RIESGOS

### Riesgos Identificados y Mitigación

| ID | Riesgo | Severidad | Probabilidad | Impacto | Mitigación | Estado |
|---|---|---|---|---|---|---|
| R-001 | SQL Injection en login | CRÍTICA | BAJA | CRÍTICO | Django ORM, Validación input | ✅ |
| R-002 | Fuerza Bruta efectiva | ALTA | ALTA | ALTO | django-axes, Rate limiting | ✅ |
| R-003 | XSS en formularios | ALTA | MEDIA | MEDIO | Django auto-escape, CSP | ✅ |
| R-004 | CSRF sin protección | CRÍTICA | BAJA | CRÍTICO | {% csrf_token %}, middleware | ✅ |
| R-005 | Session hijacking | ALTA | MEDIA | ALTO | HttpOnly, Secure cookies, HTTPS | ✅ |
| R-006 | Contraseña débil | MEDIA | ALTA | MEDIO | Validadores Django | ✅ |
| R-007 | Escalación de privilegios | CRÍTICA | BAJA | CRÍTICO | Middleware, decoradores | ✅ |
| R-008 | Enumeración de usuarios | MEDIA | ALTA | BAJO | Mensajes genéricos | ✅ |
| R-009 | Token predicible | CRÍTICA | BAJA | CRÍTICO | Django tokens seguros | ✅ |
| R-010 | Logs sin seguridad | MEDIA | MEDIA | MEDIO | Rotación, no almacenar secrets | ✅ |

---

## ✅ CHECKLIST FINAL DE PRUEBAS

### Fase 1: Setup y Configuración
- [ ] BD creada y migrada correctamente
- [ ] Datos de prueba insertados (3 usuarios + admin)
- [ ] Logs configurados y rotando
- [ ] Cache funcionando (Redis o Memcached)
- [ ] Email backend en console (desarrollo)
- [ ] DEBUG = True en desarrollo, False en producción

### Fase 2: Pruebas Funcionales RF-01 a RF-10
- [ ] TC-001: Login exitoso
- [ ] TC-002: Login fallido - contraseña
- [ ] TC-003: Login fallido - usuario no existe
- [ ] TC-004: Login con campo vacío
- [ ] TC-005: Rol identificado correctamente
- [ ] TC-006: Rol persistente
- [ ] TC-007 a TC-009: Redirecciones por rol
- [ ] TC-010: Parámetro next funciona
- [ ] TC-011 a TC-012: Logout funciona
- [ ] TC-013 a TC-014: Perfil muestra y edita
- [ ] TC-015 a TC-018: Cambio de contraseña
- [ ] TC-019 a TC-022: Reset de contraseña
- [ ] TC-023 a TC-025: Restricción de acceso
- [ ] TC-026 a TC-028: Registro de intentos
- [ ] TC-029 a TC-031: Bloqueo temporal

### Fase 3: Pruebas de Seguridad
- [ ] TC-032: Autenticación requerida
- [ ] TC-033: Middleware verifica permisos
- [ ] TC-034: Sin escalación de privilegios
- [ ] TC-035: PBKDF2 hashing correcto
- [ ] TC-036: HTTPS en producción
- [ ] TC-037: Cookies seguras (HttpOnly, Secure)
- [ ] TC-038: SQL Injection imposible
- [ ] TC-039: XSS escapado
- [ ] TC-040: CSRF token presente y validado
- [ ] TC-041: Validación de email
- [ ] TC-042: Validación de teléfono
- [ ] TC-043: Rate limiting por IP
- [ ] TC-044: Versiones actualizadas
- [ ] TC-045: Django check --deploy OK
- [ ] TC-046: Brute force bloqueado
- [ ] TC-047: Session regeneración
- [ ] TC-048: Sin enumeración de usuarios
- [ ] TC-049: Eventos de seguridad en logs
- [ ] TC-050: Logs rotan correctamente
- [ ] TC-051: No SSRF

### Fase 4: Pruebas de Permisos
- [ ] TC-052: Permisos estudiante correctos
- [ ] TC-053: Permisos docente correctos
- [ ] TC-054: Permisos admin correctos
- [ ] TC-055: Grupos asignados automáticamente
- [ ] TC-056: Cambio de rol actualiza grupos
- [ ] TC-057: Decorador @requerir_rol funciona
- [ ] TC-058: Decorador @requerir_permiso funciona
- [ ] TC-059: Combinación de decoradores OK

### Fase 5: Pruebas de Usabilidad
- [ ] TC-060: Login responsive (desktop, tablet, móvil)
- [ ] TC-061: Mensajes de error claros
- [ ] TC-062: Validación con feedback visual
- [ ] TC-063: Navegación consistente
- [ ] TC-064: Validación cliente (HTML5)
- [ ] TC-065: Confirmación de acciones destructivas
- [ ] TC-066: WCAG 2.1 AA compliance
- [ ] TC-067: Navegación por teclado
- [ ] TC-068: Compatible con lectores de pantalla

### Fase 6: Pruebas de Rendimiento
- [ ] TC-069: Login < 500ms
- [ ] TC-070: Max 5 queries en login
- [ ] TC-071: Cache de intentos funciona
- [ ] TC-072: Rendimiento bajo carga OK (p95 < 1s)
- [ ] TC-073: Migraciones rápidas (< 10s)

### Fase 7: Verificaciones Finales
- [ ] Código sigue PEP 8
- [ ] Sin warnings en `python manage.py check`
- [ ] Sin warnings en `python manage.py check --deploy`
- [ ] Todos los templates heredan de base.html
- [ ] Todos los formularios usan crispy forms
- [ ] Todos los estilos usan Bootstrap 5
- [ ] URLs.py registrado en proyecto principal
- [ ] Apps.py tiene señales importadas
- [ ] LOGGING configurado en settings
- [ ] MIDDLEWARE actualizado
- [ ] AUTH_USER_MODEL = 'accounts.Usuario'
- [ ] Documentación está actualizada

### Fase 8: Pruebas de Regresión
- [ ] Crear usuario nuevo - asigna grupo automáticamente
- [ ] Cambiar rol usuario - grupos actualizados
- [ ] Eliminar usuario - sesiones se limpian
- [ ] Reset BD - migraciones funcionan
- [ ] Fixture de datos - carga correctamente

---

## 📈 REPORTE DE DEFECTOS

### Formato Estándar

```
DEFECTO ID: BUG-001
TÍTULO: Login no redirige a dashboard por rol

SEVERIDAD: Alta
ESTADO: Abierto

DESCRIPCIÓN:
Al hacer login como estudiante, el usuario es redirigido a 
/accounts/perfil/ en lugar de /reservas/lista-laboratorios/

PASOS PARA REPRODUCIR:
1. Navegar a /accounts/login/
2. Ingresar: username="juan.perez", password="Test@123456"
3. Hacer clic en "Entrar"
4. Observar URL

RESULTADO ESPERADO:
Redirige a /reservas/lista-laboratorios/

RESULTADO ACTUAL:
Redirige a /accounts/perfil/

ENTORNO:
- Django 4.2.0
- Python 3.10.8
- OS: Windows 11

ASOCIADO A:
- Requisito RF-03
- Caso de Prueba TC-007

NOTAS:
- Solo ocurre con rol='estudiante'
- Otros roles funcionan correctamente
```

---

## 📚 REFERENCIAS Y HERRAMIENTAS

### Herramientas de Testing Recomendadas
- **pytest-django**: Framework de pruebas
- **django-debug-toolbar**: Debugging y profiling
- **locust**: Load testing
- **OWASP ZAP**: Escaneo de seguridad
- **axe DevTools**: Auditoría de accesibilidad
- **Coverage.py**: Cobertura de código

### Comandos Útiles
```bash
# Tests unitarios
python manage.py test accounts

# Con coverage
coverage run --source='accounts' manage.py test accounts
coverage report -m
coverage html

# Verificación de seguridad
python manage.py check --deploy

# Análisis de código
flake8 accounts/
pylint accounts/
black accounts/

# Profiling
python manage.py runserver --profile-sql
```

### Links de Referencia
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Django Security: https://docs.djangoproject.com/en/4.2/topics/security/
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
- Django-Axes: https://django-axes.readthedocs.io/

---

## 🎯 CRITERIOS DE ACEPTACIÓN FINAL

El módulo Accounts es considerado **LISTO PARA PRODUCCIÓN** si:

✅ **100% de pruebas funcionales PASADAS** (TC-001 a TC-031)  
✅ **0 vulnerabilidades CRÍTICAS** en pruebas de seguridad  
✅ **Cobertura de código ≥ 85%**  
✅ **Performance: p95 latency < 1000ms**  
✅ **WCAG 2.1 AA compliance verificado**  
✅ **Logs de auditoría funcionando**  
✅ **Documentación actualizada**  
✅ **Código review aprobado**  
✅ **Testing en ambiente similar a producción**  
✅ **Plan de rollback disponible**  

---

*Documento generado: Mayo 7, 2026*  
*Versión: 1.0*  
*Ingeniero QA: Especialista en Seguridad Django*  
*Próxima Revisión: Después de implementación del módulo*
