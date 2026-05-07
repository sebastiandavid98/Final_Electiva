# 🎯 CASOS DE PRUEBA EJECUTABLES - MÓDULO ACCOUNTS
## Sistema de Gestión de Reservas de Laboratorios Universitarios

**Documento:** Casos de Prueba Obligatorios  
**Versión:** 1.0  
**Fecha:** Mayo 7, 2026  
**Estado:** Listo para Ejecución  

---

## 🏁 OBJETIVOS DE PRUEBA

El presente documento valida que el sistema de autenticación y permisos:

1. ✅ Permite acceso solo a usuarios autorizados
2. ✅ Redirige correctamente según el rol de cada usuario
3. ✅ Bloquea intentos fallidos según política de seguridad
4. ✅ Protege recursos sensibles según permisos configurados
5. ✅ Registra todas las acciones en logs de auditoría
6. ✅ Cumple con tiempos de respuesta aceptables

---

## 📝 USUARIOS DE PRUEBA

Crear estos usuarios antes de iniciar:

```python
# Script: python manage.py shell < crear_usuarios_prueba.py
from accounts.models import Usuario
from django.contrib.auth.models import Group

# ESTUDIANTE
Usuario.objects.create_user(
    username='juan.estudiante',
    email='juan.estudiante@universidad.edu',
    password='correcta123',
    rol='estudiante',
    carrera='Ingeniería en Sistemas'
)

# DOCENTE
Usuario.objects.create_user(
    username='maria.docente',
    email='maria.docente@universidad.edu',
    password='correcta123',
    rol='docente',
    departamento='Departamento de Ingeniería'
)

# ADMINISTRATIVO
Usuario.objects.create_user(
    username='carlos.admin',
    email='carlos.admin@universidad.edu',
    password='correcta123',
    rol='administrativo',
    departamento='Administración'
)

# Ejecutar gestión de permisos
from accounts.permissions import GestorPermisos
GestorPermisos.crear_permisos_personalizados()
GestorPermisos.configurar_grupos_por_rol()
```

---

## 🟢 PRUEBAS FUNCIONALES - LOGIN

### CP-01: Login exitoso - Estudiante

**Objetivo:** Verificar que estudiante puede autenticarse y es redirigido correctamente

**Pasos:**
1. Ir a `http://localhost:8000/accounts/login/`
2. Ingresar usuario: `juan.estudiante`
3. Ingresar contraseña: `correcta123`
4. Click en botón "Entrar"

**Resultado Esperado:**
- ✅ Redirige a `/reservas/lista-laboratorios/`
- ✅ Mensaje de bienvenida visible en navbar
- ✅ Muestra "Hola, juan.estudiante (Estudiante)"
- ✅ Cookie de sesión creada

**Evidencia:**
- [ ] Screenshot de página de destino
- [ ] DevTools: Application → Cookies (sessionid presente)
- [ ] Console: Sin errores JavaScript

**Script de Automatización:**
```python
def test_cp_01_login_estudiante_exitoso(self):
    response = self.client.post('/accounts/login/', {
        'username': 'juan.estudiante',
        'password': 'correcta123'
    })
    
    # Verificar redirección
    self.assertEqual(response.status_code, 302)
    self.assertEqual(response.url, '/reservas/lista-laboratorios/')
    
    # Verificar sesión
    self.assertTrue(self.client.session['_auth_user_id'])
    
    # Verificar rol
    user = Usuario.objects.get(username='juan.estudiante')
    self.assertEqual(user.rol, 'estudiante')
    
    # Verificar timestamp
    user.refresh_from_db()
    self.assertIsNotNone(user.fecha_ultimo_acceso)
```

---

### CP-02: Login exitoso - Docente

**Objetivo:** Verificar redirección correcta para docente

**Pasos:**
1. Ir a `/accounts/login/`
2. Ingresar usuario: `maria.docente`
3. Ingresar contraseña: `correcta123`
4. Click en "Entrar"

**Resultado Esperado:**
- ✅ Redirige a `/reservas/mis-reservas/`
- ✅ Muestra "Hola, maria.docente (Docente)"
- ✅ Visible opción de "Aprobar reservas"
- ✅ Puede ver reservas de sus grupos

**Evidencia:**
- [ ] URL final: `/reservas/mis-reservas/`
- [ ] Botón/enlace "Aprobar" visible
- [ ] Página muestra reservas pendientes

**Script:**
```python
def test_cp_02_login_docente_exitoso(self):
    response = self.client.post('/accounts/login/', {
        'username': 'maria.docente',
        'password': 'correcta123'
    }, follow=True)
    
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'mis-reservas')
    self.assertIn('/reservas/mis-reservas/', response.request['PATH_INFO'])
```

---

### CP-03: Login exitoso - Administrativo

**Objetivo:** Verificar redirección a dashboard admin

**Pasos:**
1. Ir a `/accounts/login/`
2. Ingresar usuario: `carlos.admin`
3. Ingresar contraseña: `correcta123`
4. Click en "Entrar"

**Resultado Esperado:**
- ✅ Redirige a `/dashboard/admin/` o `/admin/`
- ✅ Muestra "Hola, carlos.admin (Administrativo)"
- ✅ Visible menú de "Gestión de usuarios"
- ✅ Acceso a panel completo

**Evidencia:**
- [ ] URL contiene `/dashboard/admin/` o similar
- [ ] Opción de gestionar usuarios visible
- [ ] Acceso a todas las secciones

**Script:**
```python
def test_cp_03_login_admin_exitoso(self):
    response = self.client.post('/accounts/login/', {
        'username': 'carlos.admin',
        'password': 'correcta123'
    }, follow=True)
    
    self.assertEqual(response.status_code, 200)
    user = response.wsgi_request.user
    self.assertEqual(user.rol, 'administrativo')
    self.assertTrue(user.has_perm('accounts.puede_gestionar_usuarios'))
```

---

### CP-04: Login fallido - Contraseña incorrecta

**Objetivo:** Verificar que login rechaza contraseña incorrecta

**Pasos:**
1. Ir a `/accounts/login/`
2. Ingresar usuario: `juan.estudiante`
3. Ingresar contraseña: `incorrecta123` (INCORRECTA)
4. Click en "Entrar"

**Resultado Esperado:**
- ✅ NO redirige (permanece en `/accounts/login/`)
- ✅ Mensaje de error: "Usuario o contraseña incorrectos"
- ✅ NO crea sesión
- ✅ Incrementa contador de intentos fallidos
- ✅ Campo de contraseña se limpia

**Evidencia:**
- [ ] URL sigue siendo `/accounts/login/`
- [ ] Mensaje de error visible en color rojo
- [ ] En BD: `Usuario.intentos_fallidos = 1`
- [ ] Consultar BD: `SELECT intentos_fallidos FROM accounts_usuario WHERE username='juan.estudiante';`

**Script:**
```python
def test_cp_04_login_fallido_contrasena_incorrecta(self):
    response = self.client.post('/accounts/login/', {
        'username': 'juan.estudiante',
        'password': 'incorrecta123'
    })
    
    # No redirige
    self.assertEqual(response.status_code, 200)
    
    # Muestra formulario nuevamente
    self.assertContains(response, 'login')
    self.assertContains(response, 'Usuario o contraseña incorrectos')
    
    # Sin sesión
    self.assertNotIn('_auth_user_id', self.client.session)
    
    # Incrementa intentos
    user = Usuario.objects.get(username='juan.estudiante')
    self.assertEqual(user.intentos_fallidos, 1)
```

---

### CP-05: Login fallido - Usuario inexistente

**Objetivo:** Verificar que no revela si usuario existe

**Pasos:**
1. Ir a `/accounts/login/`
2. Ingresar usuario: `usuario.fantasma` (NO EXISTE)
3. Ingresar contraseña: `alguien123`
4. Click en "Entrar"

**Resultado Esperado:**
- ✅ MISMO mensaje que CP-04: "Usuario o contraseña incorrectos"
- ✅ No diferencia si usuario existe o no
- ✅ Permanece en login
- ✅ NO incrementa contador (usuario no existe en BD)

**Evidencia:**
- [ ] Mensaje es genérico (no dice "usuario no existe")
- [ ] Logs muestran: "Login fallido - usuario inexistente"

**Script:**
```python
def test_cp_05_login_usuario_inexistente(self):
    response = self.client.post('/accounts/login/', {
        'username': 'usuario.fantasma',
        'password': 'alguien123'
    })
    
    # Mismo mensaje que contraseña incorrecta
    self.assertContains(response, 'Usuario o contraseña incorrectos')
    
    # No incrementa contador (usuario no existe)
    usuario_count = Usuario.objects.filter(
        username='usuario.fantasma',
        intentos_fallidos__gt=0
    ).count()
    self.assertEqual(usuario_count, 0)
```

---

### CP-06: Campos vacíos

**Objetivo:** Verificar validación de campos requeridos

**Pasos:**
1. Ir a `/accounts/login/`
2. Dejar usuario vacío, ingresar contraseña
3. Click en "Entrar"
4. Repetir dejando contraseña vacía

**Resultado Esperado:**
- ✅ Validación frontend (atributo `required`)
- ✅ Mensaje: "Este campo es requerido"
- ✅ Validación backend también (por seguridad)
- ✅ No llega a BD

**Evidencia:**
- [ ] Navegador muestra tooltip de validación
- [ ] Inspeccionar input: `<input required>`

**Script:**
```python
def test_cp_06_campos_vacios(self):
    # Usuario vacío
    response = self.client.post('/accounts/login/', {
        'username': '',
        'password': 'correcta123'
    })
    self.assertContains(response, 'login')
    
    # Contraseña vacía
    response = self.client.post('/accounts/login/', {
        'username': 'juan.estudiante',
        'password': ''
    })
    self.assertContains(response, 'login')
    
    # Ambos vacíos
    response = self.client.post('/accounts/login/', {
        'username': '',
        'password': ''
    })
    self.assertContains(response, 'login')
```

---

### CP-07: Caracteres especiales - SQL Injection

**Objetivo:** Verificar protección contra SQL injection

**Pasos:**
1. Ir a `/accounts/login/`
2. Ingresar usuario: `admin' OR '1'='1`
3. Ingresar contraseña: `test`
4. Click en "Entrar"

**Resultado Esperado:**
- ✅ NO autentica como admin (ni como nadie)
- ✅ Mensaje genérico: "Usuario o contraseña incorrectos"
- ✅ BD no es modificada
- ✅ No acceso a datos

**Evidencia:**
- [ ] Permanece en login
- [ ] Intento registrado en logs
- [ ] Consultar BD: Sin cambios

**Script:**
```python
def test_cp_07_sql_injection_protegido(self):
    payloads = [
        "admin' OR '1'='1",
        "admin' --",
        "' OR 1=1 --",
        "admin'; DROP TABLE users; --",
    ]
    
    for payload in payloads:
        response = self.client.post('/accounts/login/', {
            'username': payload,
            'password': 'test'
        })
        
        # No autentica
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertContains(response, 'Usuario o contraseña incorrectos')
```

---

### CP-08: Logout

**Objetivo:** Verificar que logout destruye sesión

**Pasos:**
1. Login como estudiante (CP-01)
2. Click en "Salir" en navbar
3. Verificar redirección
4. Intentar acceder a `/accounts/perfil/`

**Resultado Esperado:**
- ✅ Redirige a `/accounts/login/`
- ✅ Mensaje: "Sesión cerrada correctamente"
- ✅ Cookie de sesión destruida/expirada
- ✅ Al intentar `/accounts/perfil/`, redirige a login

**Evidencia:**
- [ ] URL es `/accounts/login/`
- [ ] Mensaje de logout visible
- [ ] DevTools: sessionid no existe
- [ ] Log contiene: "Logout: juan.estudiante"

**Script:**
```python
def test_cp_08_logout(self):
    # Login primero
    self.client.login(username='juan.estudiante', password='correcta123')
    self.assertIn('_auth_user_id', self.client.session)
    
    # Logout
    response = self.client.get('/accounts/logout/', follow=True)
    
    # Verifica redirección
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'login')
    
    # Sesión destruida
    self.assertNotIn('_auth_user_id', self.client.session)
    
    # Intenta acceder a ruta protegida
    response = self.client.get('/accounts/perfil/')
    self.assertEqual(response.status_code, 302)
    self.assertIn('/accounts/login/', response.url)
```

---

## 🔵 PRUEBAS DE PERMISOS Y ROLES

### CP-09: Estudiante accede a zona de administrativo

**Objetivo:** Verificar que estudiante NO puede acceder a gestión de usuarios

**Pasos:**
1. Login como `juan.estudiante`
2. Intentar acceder a `http://localhost:8000/accounts/usuarios/`
3. Inspeccionar respuesta

**Resultado Esperado:**
- ✅ HTTP 403 Forbidden
- ✅ Mensaje: "No tienes permiso para acceder a esta página"
- ✅ Usuario permanece autenticado (no logout)
- ✅ Intento registrado en logs

**Evidencia:**
- [ ] Código de estado: 403
- [ ] Página de error accesible
- [ ] Logs: "Acceso denegado: juan.estudiante intentó acceder a accounts:lista_usuarios"

**Script:**
```python
def test_cp_09_estudiante_acceso_denegado_usuarios(self):
    self.client.login(username='juan.estudiante', password='correcta123')
    
    response = self.client.get('/accounts/usuarios/')
    
    # HTTP 403
    self.assertEqual(response.status_code, 403)
    
    # Sigue autenticado
    self.assertIn('_auth_user_id', self.client.session)
    
    # Usuario no cambió
    user = Usuario.objects.get(username='juan.estudiante')
    self.assertEqual(user.rol, 'estudiante')
```

---

### CP-10: Estudiante intenta aprobar reserva

**Objetivo:** Verificar que estudiante NO puede ejecutar acciones de docente

**Pasos:**
1. Login como `juan.estudiante`
2. Hacer POST a `/reservas/aprobar/1/` con datos
3. Inspeccionar respuesta

**Resultado Esperado:**
- ✅ HTTP 403 Forbidden
- ✅ Reserva NO es modificada en BD
- ✅ Log registra intento no autorizado

**Evidencia:**
- [ ] BD: Reserva mantiene estado anterior
- [ ] Código 403
- [ ] Log contiene advertencia

**Script:**
```python
def test_cp_10_estudiante_no_puede_aprobar(self):
    self.client.login(username='juan.estudiante', password='correcta123')
    
    # Obtener reserva (si existe)
    # Para este test, se asume que existe reserva con ID=1
    
    response = self.client.post('/reservas/aprobar/1/', {
        'estado': 'aprobada'
    })
    
    # Acceso denegado
    self.assertEqual(response.status_code, 403)
```

---

### CP-11: Docente puede aprobar reservas

**Objetivo:** Verificar que docente tiene permiso para aprobar

**Pasos:**
1. Login como `maria.docente`
2. Acceder a `/reservas/aprobar/`
3. Verificar que botón "Aprobar" es visible
4. Hacer clic en aprobar una reserva

**Resultado Esperado:**
- ✅ Página carga correctamente (200 OK)
- ✅ Botón "Aprobar" visible
- ✅ Reserva se actualiza en BD
- ✅ Log registra aprobación

**Evidencia:**
- [ ] Botón visible en HTML
- [ ] BD: Reserva.estado cambió a 'aprobada'
- [ ] Log: "Reserva aprobada por: maria.docente"

**Script:**
```python
def test_cp_11_docente_puede_aprobar(self):
    self.client.login(username='maria.docente', password='correcta123')
    
    response = self.client.get('/reservas/aprobar/')
    
    # Acceso permitido
    self.assertEqual(response.status_code, 200)
    
    # Verifica permiso
    user = Usuario.objects.get(username='maria.docente')
    self.assertTrue(user.has_perm('accounts.puede_aprobar_reservas'))
```

---

### CP-12: Administrativo ve todos los usuarios

**Objetivo:** Verificar que admin tiene acceso a lista completa

**Pasos:**
1. Login como `carlos.admin`
2. Acceder a `/accounts/usuarios/`
3. Verificar lista

**Resultado Esperado:**
- ✅ HTTP 200 OK
- ✅ Lista contiene estudiantes, docentes y administrativos
- ✅ Puede ver correo, teléfono, rol

**Evidencia:**
- [ ] Página carga
- [ ] Tabla contiene al menos 3 usuarios
- [ ] Todos los campos visibles

**Script:**
```python
def test_cp_12_admin_ve_todos_usuarios(self):
    self.client.login(username='carlos.admin', password='correcta123')
    
    response = self.client.get('/accounts/usuarios/')
    
    # Acceso permitido
    self.assertEqual(response.status_code, 200)
    
    # Contiene usuarios
    self.assertContains(response, 'juan.estudiante')
    self.assertContains(response, 'maria.docente')
    self.assertContains(response, 'carlos.admin')
```

---

### CP-13: Usuario sin permiso ve opción oculta

**Objetivo:** Verificar que UI no muestra opciones no permitidas

**Pasos:**
1. Login como `juan.estudiante`
2. Inspeccionar HTML de navbar/menú
3. Buscar enlaces no permitidos

**Resultado Esperado:**
- ✅ NO ve enlace a `/accounts/usuarios/`
- ✅ NO ve opción "Gestión de usuarios"
- ✅ NO ve "Reportes"
- ✅ NO ve "Aprobar reservas"
- ✅ Solo ve su perfil y cambiar contraseña

**Evidencia:**
- [ ] Buscar en HTML: Sin `href="/accounts/usuarios/"`
- [ ] Buscar en HTML: Sin "Gestión de usuarios"
- [ ] DevTools: Enlace no existe

**Script:**
```python
def test_cp_13_estudiante_no_ve_opciones_admin(self):
    self.client.login(username='juan.estudiante', password='correcta123')
    
    response = self.client.get('/accounts/perfil/')
    
    # No contiene enlaces admin
    self.assertNotContains(response, '/accounts/usuarios/')
    self.assertNotContains(response, 'Gestión de usuarios')
    self.assertNotContains(response, '/dashboard/admin/')
```

---

## 🟡 PRUEBAS DE SEGURIDAD (CRÍTICAS)

### CP-14: Bloqueo por intentos fallidos

**Objetivo:** Verificar que cuenta se bloquea después de 5 intentos

**Pasos:**
1. Login como `juan.estudiante` con contraseña INCORRECTA
2. Repetir 5 veces
3. En intento 6, usar contraseña CORRECTA
4. Verificar que sigue bloqueado

**Resultado Esperado:**
- ✅ Después de intento 5: Cuenta bloqueada
- ✅ Mensaje: "Cuenta bloqueada por 30 minutos"
- ✅ Intento 6 falla aunque contraseña sea correcta
- ✅ Usuario.bloqueado_hasta = NOW() + 30 minutos

**Evidencia:**
- [ ] Consulta BD: `SELECT bloqueado_hasta, intentos_fallidos FROM accounts_usuario WHERE username='juan.estudiante';`
- [ ] bloqueado_hasta > NOW()
- [ ] intentos_fallidos = 5
- [ ] Mensaje en interfaz

**Script:**
```python
def test_cp_14_bloqueo_por_intentos_fallidos(self):
    # 5 intentos fallidos
    for i in range(5):
        self.client.post('/accounts/login/', {
            'username': 'juan.estudiante',
            'password': 'incorrecta123'
        })
    
    # Verificar bloqueo
    user = Usuario.objects.get(username='juan.estudiante')
    self.assertEqual(user.intentos_fallidos, 5)
    self.assertTrue(user.esta_bloqueado())
    
    # Intento 6 con contraseña correcta
    response = self.client.post('/accounts/login/', {
        'username': 'juan.estudiante',
        'password': 'correcta123'
    })
    
    # Sigue bloqueado
    self.assertContains(response, 'bloqueada')
    self.assertNotIn('_auth_user_id', self.client.session)
```

---

### CP-15: Desbloqueo automático

**Objetivo:** Verificar que cuenta se desbloquea después de 30 minutos

**Pasos:**
1. Ejecutar CP-14 (cuenta bloqueada)
2. Simular paso de 30+ minutos (usar `freeze_time` en tests)
3. Intentar login con contraseña correcta

**Resultado Esperado:**
- ✅ Login exitoso
- ✅ Sesión creada
- ✅ intentos_fallidos reseteado a 0
- ✅ bloqueado_hasta limpiado

**Evidencia:**
- [ ] Login exitoso
- [ ] Redirige al dashboard
- [ ] BD: intentos_fallidos = 0, bloqueado_hasta = NULL

**Script:**
```python
from freezegun import freeze_time
from datetime import timedelta

def test_cp_15_desbloqueo_automatico(self):
    # Bloquear cuenta
    user = Usuario.objects.get(username='juan.estudiante')
    user.bloqueado_hasta = timezone.now() + timedelta(minutes=30)
    user.intentos_fallidos = 5
    user.save()
    
    # Avanzar tiempo 31 minutos
    with freeze_time(timezone.now() + timedelta(minutes=31)):
        response = self.client.post('/accounts/login/', {
            'username': 'juan.estudiante',
            'password': 'correcta123'
        })
        
        # Login exitoso
        self.assertEqual(response.status_code, 302)
        
        # Verificar BD
        user.refresh_from_db()
        self.assertEqual(user.intentos_fallidos, 0)
        self.assertIsNone(user.bloqueado_hasta)
```

---

### CP-16: Protección CSRF

**Objetivo:** Verificar que POST sin CSRF token es rechazado

**Pasos:**
1. Obtener token CSRF de página de login
2. Hacer POST sin incluir token
3. Inspeccionar respuesta

**Resultado Esperado:**
- ✅ HTTP 403 Forbidden
- ✅ Mensaje: "CSRF token missing or incorrect"
- ✅ POST no se procesa

**Evidencia:**
- [ ] Código 403
- [ ] Sin sesión creada

**Script:**
```python
def test_cp_16_csrf_protection(self):
    # POST sin CSRF token (usando client.post directamente)
    # Django client lo añade automáticamente, así que deshabilitamos
    
    from django.middleware.csrf import CsrfViewMiddleware
    from django.test import Client
    
    # Client sin CSRF
    client = Client(enforce_csrf_checks=True)
    
    response = client.post('/accounts/login/', {
        'username': 'juan.estudiante',
        'password': 'correcta123'
    })
    
    # Rechazado
    self.assertEqual(response.status_code, 403)
```

---

### CP-17: Session Hijacking

**Objetivo:** Verificar que sessionid se regenera en login

**Pasos:**
1. Capturar sessionid antes de login
2. Login exitoso
3. Capturar sessionid después de login
4. Comparar

**Resultado Esperado:**
- ✅ Session ID es diferente
- ✅ Session anterior se invalida
- ✅ Nueva sesión asignada al usuario

**Evidencia:**
- [ ] session_id_1 ≠ session_id_2
- [ ] Usar session_id_1 posteriormente rechazado

**Script:**
```python
def test_cp_17_session_regeneration(self):
    # Obtener session antes de login (vacío)
    response = self.client.get('/accounts/login/')
    old_sessionid = self.client.session.session_key
    
    # Login
    self.client.login(username='juan.estudiante', password='correcta123')
    
    # Obtener session después de login
    new_sessionid = self.client.session.session_key
    
    # Debe ser diferente
    self.assertNotEqual(old_sessionid, new_sessionid)
```

---

### CP-18: Contraseña en logs

**Objetivo:** Verificar que contraseñas NO aparecen en archivos de log

**Pasos:**
1. Realizar login fallido
2. Revisar `logs/security.log`
3. Buscar contraseña

**Resultado Esperado:**
- ✅ Log contiene: "Login fallido: juan.estudiante"
- ✅ Log NO contiene: "correcta123" (contraseña)
- ✅ Log NO contiene: "incorrecta123"

**Evidencia:**
- [ ] Examinar archivo de log
- [ ] Comando: `grep -i "correcta123" logs/security.log` → Sin resultados

**Script:**
```python
def test_cp_18_no_password_in_logs(self):
    import logging
    
    # Capturar logs
    logger = logging.getLogger('accounts')
    
    with self.assertLogs('accounts', level='WARNING') as cm:
        self.client.post('/accounts/login/', {
            'username': 'juan.estudiante',
            'password': 'incorrecta123'
        })
    
    # Verificar que contraseña NO está en logs
    for log in cm.output:
        self.assertNotIn('incorrecta123', log)
        self.assertNotIn('correcta123', log)
```

---

### CP-19: HTTPS forzado (producción)

**Objetivo:** Verificar que HTTP redirige a HTTPS en producción

**Pasos:**
1. En settings: DEBUG=False
2. SECURE_SSL_REDIRECT=True
3. Acceder a `http://localhost:8000/accounts/login/`

**Resultado Esperado:**
- ✅ Redirección 301 a `https://localhost:8000/accounts/login/`
- ✅ Header: `Strict-Transport-Security`

**Evidencia:**
- [ ] Redirección presente
- [ ] DevTools: Status 301
- [ ] Location header contiene https://

**Script:**
```python
def test_cp_19_https_redirect_production(self):
    with self.settings(
        DEBUG=False,
        SECURE_SSL_REDIRECT=True,
        SECURE_HSTS_SECONDS=31536000
    ):
        # Simular request HTTP
        response = self.client.get('/accounts/login/', secure=False)
        
        # Redirige a HTTPS
        self.assertEqual(response.status_code, 301)
        self.assertIn('https://', response.url)
```

---

### CP-20: SQL Injection en login

**Objetivo:** Verificar protección contra SQL injection en campos

**Pasos:**
1. Ingresar payloads SQL en usuario y contraseña
2. Verificar que no inyecta

**Resultado Esperado:**
- ✅ Login falla (no autentica)
- ✅ Mensaje genérico
- ✅ BD intacta

**Payloads a probar:**
```
admin' OR '1'='1
admin' --
' OR 1=1 --
admin'; DROP TABLE users; --
admin' UNION SELECT * FROM accounts_usuario --
```

**Script:**
```python
def test_cp_20_sql_injection_payloads(self):
    payloads = [
        ("admin' OR '1'='1", "test"),
        ("admin' --", "test"),
        ("' OR 1=1 --", "test"),
        ("admin'; DROP TABLE users; --", "test"),
    ]
    
    for username, password in payloads:
        response = self.client.post('/accounts/login/', {
            'username': username,
            'password': password
        })
        
        # No autentica
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertContains(response, 'Usuario o contraseña incorrectos')
```

---

## 🟠 PRUEBAS DE SESIÓN

### CP-21: Timeout de sesión

**Objetivo:** Verificar que sesión expira después de 30 minutos

**Pasos:**
1. Login exitoso
2. Esperar 31 minutos (simular con `freeze_time`)
3. Recargar página o acceder a ruta protegida

**Resultado Esperado:**
- ✅ Redirección a `/accounts/login/`
- ✅ Mensaje: "Sesión expirada"
- ✅ Cookie de sesión inválida

**Evidencia:**
- [ ] URL es `/accounts/login/`
- [ ] Log: "Sesión expirada: juan.estudiante"

**Script:**
```python
from freezegun import freeze_time
from datetime import timedelta

def test_cp_21_session_timeout(self):
    # Login
    self.client.login(username='juan.estudiante', password='correcta123')
    sessionid = self.client.session.session_key
    
    # Avanzar 31 minutos
    with freeze_time(timezone.now() + timedelta(minutes=31)):
        response = self.client.get('/accounts/perfil/')
        
        # Redirige a login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
```

---

### CP-22: Sesión persistente

**Objetivo:** Verificar que sesión se destruye al cerrar navegador

**Pasos:**
1. Login exitoso
2. Cerrar todos los tabs (simular con `SESSION_EXPIRE_AT_BROWSER_CLOSE=True`)
3. Abrir navegador nuevamente

**Resultado Esperado:**
- ✅ Sesión destruida
- ✅ Debe volver a hacer login

**Configuración:**
```python
# settings.py
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

---

### CP-23: Doble sesión - mismo usuario

**Objetivo:** Verificar que múltiples sesiones del mismo usuario son permitidas

**Pasos:**
1. Cliente 1: Login como `juan.estudiante`
2. Cliente 2: Login como `juan.estudiante` (desde otro navegador/IP)
3. Ambos intentan acceder a `/accounts/perfil/`

**Resultado Esperado:**
- ✅ Ambos pueden estar autenticados simultáneamente
- ✅ Cada uno con su propia sesión

**Script:**
```python
def test_cp_23_multiple_sessions_same_user(self):
    client1 = Client()
    client2 = Client()
    
    # Ambos hacen login
    client1.login(username='juan.estudiante', password='correcta123')
    client2.login(username='juan.estudiante', password='correcta123')
    
    # Session keys diferentes
    sid1 = client1.session.session_key
    sid2 = client2.session.session_key
    self.assertNotEqual(sid1, sid2)
    
    # Ambos pueden acceder
    r1 = client1.get('/accounts/perfil/')
    r2 = client2.get('/accounts/perfil/')
    
    self.assertEqual(r1.status_code, 200)
    self.assertEqual(r2.status_code, 200)
```

---

### CP-24: Recordar sesión

**Objetivo:** Verificar que sin "Recordarme", sesión expira al cerrar navegador

**Pasos:**
1. Login SIN marcar "Recordarme"
2. Cerrar navegador
3. Abrir navegador nuevamente

**Resultado Esperado:**
- ✅ Sesión se destruye al cerrar navegador
- ✅ Django mantiene esta política por defecto

**Configuración:**
```python
# settings.py
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Por defecto True
```

---

## 🟣 PRUEBAS DE RECUPERACIÓN DE CONTRASEÑA

### CP-25: Enlace "Olvidé mi contraseña"

**Objetivo:** Verificar que usuario recibe email con enlace de reset

**Pasos:**
1. Click en "¿Olvidaste tu contraseña?" en login
2. Ingresar email: `juan.estudiante@universidad.edu`
3. Click en "Enviar"
4. Revisar email (console backend)

**Resultado Esperado:**
- ✅ Redirección a `/accounts/password-reset/done/`
- ✅ Mensaje: "Revisa tu correo electrónico"
- ✅ Email recibido con enlace
- ✅ Enlace contiene token único

**Evidencia:**
- [ ] Email visible en consola (DEBUG EMAIL_BACKEND)
- [ ] Email contiene link con estructura: `/reset/[uidb64]/[token]/`
- [ ] Token es único por usuario

**Script:**
```python
def test_cp_25_password_reset_email(self):
    from django.core import mail
    
    response = self.client.post('/accounts/password-reset/', {
        'email': 'juan.estudiante@universidad.edu'
    }, follow=True)
    
    # Redirección correcta
    self.assertContains(response, 'correo electrónico')
    
    # Email enviado
    self.assertEqual(len(mail.outbox), 1)
    email = mail.outbox[0]
    
    # Verificar contenido
    self.assertIn('juan.estudiante@universidad.edu', email.to)
    self.assertIn('reset', email.body)
```

---

### CP-26: Token de recuperación expirado

**Objetivo:** Verificar que token viejo no funciona

**Pasos:**
1. Generar token de reset
2. Esperar 24+ horas (simular)
3. Intentar usar el token

**Resultado Esperado:**
- ✅ Mensaje: "Enlace expirado o inválido"
- ✅ No permite cambiar contraseña
- ✅ Opción de solicitar nuevo reset

**Script:**
```python
from freezegun import freeze_time
from datetime import timedelta

def test_cp_26_expired_token(self):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode
    
    user = Usuario.objects.get(username='juan.estudiante')
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Esperar más de 24 horas
    with freeze_time(timezone.now() + timedelta(hours=25)):
        response = self.client.get(f'/accounts/reset/{uid}/{token}/')
        
        # Token inválido
        self.assertContains(response, 'expirado')
```

---

### CP-27: Reset con email no registrado

**Objetivo:** Verificar que no revela si email existe

**Pasos:**
1. Ir a `/accounts/password-reset/`
2. Ingresar email no registrado: `noexiste@universidad.edu`
3. Click en "Enviar"

**Resultado Esperado:**
- ✅ MISMO mensaje que CP-25: "Revisa tu correo"
- ✅ NO envía email (aunque redirige igual)
- ✅ No expone información

**Evidencia:**
- [ ] Mensaje genérico
- [ ] Sin email en outbox

**Script:**
```python
def test_cp_27_unregistered_email(self):
    from django.core import mail
    
    response = self.client.post('/accounts/password-reset/', {
        'email': 'noexiste@universidad.edu'
    }, follow=True)
    
    # Mismo mensaje
    self.assertContains(response, 'correo electrónico')
    
    # Pero NO envía email
    self.assertEqual(len(mail.outbox), 0)
```

---

### CP-28: Confirmación de cambio

**Objetivo:** Verificar que nueva contraseña funciona

**Pasos:**
1. Solicitar reset (CP-25)
2. Hacer click en enlace del email
3. Ingresar nueva contraseña: `nuevaPass@999888`
4. Confirmar: `nuevaPass@999888`
5. Click en guardar
6. Login con nueva contraseña

**Resultado Esperado:**
- ✅ Redirección a `/accounts/reset/done/`
- ✅ Mensaje: "Contraseña restablecida"
- ✅ Login exitoso con nueva contraseña
- ✅ Contraseña antigua NO funciona

**Evidencia:**
- [ ] Login con nuevaPass@999888 exitoso
- [ ] Login con correcta123 fallido

**Script:**
```python
def test_cp_28_new_password_works(self):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode
    
    user = Usuario.objects.get(username='juan.estudiante')
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Cambiar contraseña
    response = self.client.post(
        f'/accounts/reset/{uid}/{token}/',
        {
            'new_password1': 'nuevaPass@999888',
            'new_password2': 'nuevaPass@999888'
        },
        follow=True
    )
    
    # Confirmación
    self.assertContains(response, 'done')
    
    # Login con nueva contraseña funciona
    login_success = self.client.login(
        username='juan.estudiante',
        password='nuevaPass@999888'
    )
    self.assertTrue(login_success)
    
    # Login con vieja NO funciona
    login_fail = self.client.login(
        username='juan.estudiante',
        password='correcta123'
    )
    self.assertFalse(login_fail)
```

---

## 🔴 PRUEBAS NO FUNCIONALES (RENDIMIENTO)

### CP-29: Tiempo de respuesta login

**Objetivo:** Verificar que login responde en < 500ms

**Pasos:**
1. Hacer POST a `/accounts/login/`
2. Medir tiempo desde submit hasta redirección
3. Repetir 10 veces
4. Calcular promedio

**Resultado Esperado:**
- ✅ Tiempo promedio < 500ms (RNF-04)
- ✅ Máximo < 1000ms
- ✅ Consistencia

**Herramientas:**
```bash
# Usar Apache Bench
ab -n 50 -c 5 -p data.txt -T 'application/x-www-form-urlencoded' \
   http://localhost:8000/accounts/login/

# O usar locust
locust -f locustfile.py --host=http://localhost:8000
```

**Script:**
```python
import time

def test_cp_29_login_response_time(self):
    times = []
    
    for i in range(10):
        start = time.time()
        self.client.post('/accounts/login/', {
            'username': 'juan.estudiante',
            'password': 'correcta123'
        })
        elapsed = time.time() - start
        times.append(elapsed)
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    # Promedio < 500ms
    self.assertLess(avg_time, 0.5, f"Promedio: {avg_time}s")
    
    # Máximo < 1000ms
    self.assertLess(max_time, 1.0, f"Máximo: {max_time}s")
    
    print(f"Tiempo promedio: {avg_time*1000:.2f}ms")
    print(f"Tiempo máximo: {max_time*1000:.2f}ms")
```

---

### CP-30: Carga de página de login

**Objetivo:** Verificar que página carga completamente en < 2 segundos

**Pasos:**
1. Acceder a `/accounts/login/`
2. Medir tiempo hasta documento completamente cargado

**Resultado Esperado:**
- ✅ Carga completa < 2 segundos
- ✅ Recursos (CSS, JS) se cargan rápidamente

**Herramientas:**
```bash
# Chrome
lighthouse http://localhost:8000/accounts/login/ --view

# O DevTools → Performance tab
```

---

### CP-31: Manejo de concurrencia

**Objetivo:** Verificar comportamiento con 100 usuarios simultáneos

**Pasos:**
1. Usar herramienta de load testing (Locust)
2. Simular 100 usuarios intentando login
3. Monitorear recursos

**Resultado Esperado:**
- ✅ Sin caídas del servidor
- ✅ Tiempo promedio < 800ms
- ✅ Error rate < 1%

**Locustfile.py:**
```python
from locust import HttpUser, task, between

class LoginUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def login(self):
        self.client.post("/accounts/login/", {
            "username": "juan.estudiante",
            "password": "correcta123"
        })
    
    @task
    def logout(self):
        self.client.get("/accounts/logout/")
```

**Ejecución:**
```bash
locust -f locustfile.py --host=http://localhost:8000 -u 100 -r 10 -t 5m
```

---

### CP-32: Consumo de memoria

**Objetivo:** Verificar que no hay fugas de memoria

**Pasos:**
1. Hacer 1000 requests de login
2. Monitorear uso de memoria
3. Verificar que se libera correctamente

**Resultado Esperado:**
- ✅ Memoria estable (no crece continuamente)
- ✅ Sin memory leaks

**Script:**
```python
import tracemalloc

def test_cp_32_memory_leaks(self):
    tracemalloc.start()
    
    # Hacer 1000 logins
    for i in range(1000):
        self.client.post('/accounts/login/', {
            'username': 'juan.estudiante',
            'password': 'correcta123'
        })
    
    current, peak = tracemalloc.get_traced_memory()
    
    print(f"Memoria actual: {current / 1024 / 1024:.2f} MB")
    print(f"Pico de memoria: {peak / 1024 / 1024:.2f} MB")
    
    tracemalloc.stop()
```

---

### CP-33: Tiempo de migración

**Objetivo:** Verificar que migraciones son rápidas

**Pasos:**
1. Borrar BD
2. Ejecutar makemigrations
3. Ejecutar migrate
4. Medir tiempos

**Resultado Esperado:**
- ✅ makemigrations < 5 segundos
- ✅ migrate < 10 segundos
- ✅ Sin errores

**Comandos:**
```bash
time python manage.py makemigrations accounts
time python manage.py migrate accounts
```

---

## 📊 PRUEBAS DE AUDITORÍA (LOGS)

### CP-33: Login exitoso en logs

**Objetivo:** Verificar que login se registra correctamente

**Pasos:**
1. Login exitoso como `maria.docente`
2. Revisar archivo `logs/security.log`

**Resultado Esperado:**
- ✅ Log contiene: `INFO Login exitoso: maria.docente - Rol: Docente`
- ✅ Log incluye timestamp
- ✅ Sin datos sensibles

**Verificar:**
```bash
tail -20 logs/security.log | grep "maria.docente"
```

---

### CP-34: Login fallido en logs

**Objetivo:** Verificar que intento fallido se registra

**Pasos:**
1. Intentar login con contraseña incorrecta
2. Revisar `logs/security.log`

**Resultado Esperado:**
- ✅ Log contiene: `WARNING Login fallido para usuario: juan.estudiante`
- ✅ Log no contiene contraseña
- ✅ Timestamp presente

---

### CP-35: Acceso denegado en logs

**Objetivo:** Verificar que intento no autorizado se registra

**Pasos:**
1. Login como estudiante
2. Intentar acceder a `/accounts/usuarios/`
3. Revisar `logs/security.log`

**Resultado Esperado:**
- ✅ Log contiene: `WARNING Acceso denegado: juan.estudiante intentó acceder a accounts:lista_usuarios`

---

### CP-36: Bloqueo de cuenta en logs

**Objetivo:** Verificar que bloqueo por intentos se registra

**Pasos:**
1. Hacer 5 intentos fallidos
2. Revisar `logs/security.log`

**Resultado Esperado:**
- ✅ Log contiene: `WARNING Cuenta bloqueada: juan.estudiante hasta las 14:30`
- ✅ Timestamp correcto

---

## 📋 MATRIZ DE EJECUCIÓN

| ID | Caso de Prueba | Status | Fecha | Notas |
|---|---|---|---|---|
| CP-01 | Login Estudiante | ⭕ | | |
| CP-02 | Login Docente | ⭕ | | |
| CP-03 | Login Admin | ⭕ | | |
| CP-04 | Login Fallido | ⭕ | | |
| CP-05 | Usuario Inexistente | ⭕ | | |
| CP-06 | Campos Vacíos | ⭕ | | |
| CP-07 | SQL Injection | ⭕ | | |
| CP-08 | Logout | ⭕ | | |
| CP-09 | Acceso Denegado | ⭕ | | |
| CP-10 | Aprobar Sin Permiso | ⭕ | | |
| CP-11 | Docente Aprobar | ⭕ | | |
| CP-12 | Admin Ver Usuarios | ⭕ | | |
| CP-13 | Sin Opciones Admin | ⭕ | | |
| CP-14 | Bloqueo por Intentos | ⭕ | | |
| CP-15 | Desbloqueo Automático | ⭕ | | |
| CP-16 | CSRF Protection | ⭕ | | |
| CP-17 | Session Hijacking | ⭕ | | |
| CP-18 | Sin Contraseña en Logs | ⭕ | | |
| CP-19 | HTTPS Forzado | ⭕ | | |
| CP-20 | SQL Injection Avanzado | ⭕ | | |
| CP-21 | Timeout Sesión | ⭕ | | |
| CP-22 | Sesión Persistente | ⭕ | | |
| CP-23 | Doble Sesión | ⭕ | | |
| CP-24 | Recordar Sesión | ⭕ | | |
| CP-25 | Password Reset Email | ⭕ | | |
| CP-26 | Token Expirado | ⭕ | | |
| CP-27 | Email No Registrado | ⭕ | | |
| CP-28 | Nueva Contraseña | ⭕ | | |
| CP-29 | Rendimiento < 500ms | ⭕ | | |
| CP-30 | Carga < 2s | ⭕ | | |
| CP-31 | Concurrencia 100 users | ⭕ | | |
| CP-32 | Sin Memory Leaks | ⭕ | | |
| CP-33 | Login en Logs | ⭕ | | |
| CP-34 | Fallido en Logs | ⭕ | | |
| CP-35 | Denegado en Logs | ⭕ | | |
| CP-36 | Bloqueo en Logs | ⭕ | | |

**Leyenda:**
- ⭕ = No Ejecutado
- ✅ = PASS
- ❌ = FAIL
- ⚠️ = INCONCLUSO

---

## ✅ CRITERIOS DE ACEPTACIÓN

Para considerar el módulo como **APROBADO**:

- [ ] CP-01 a CP-08: Todos PASS (funcionalidad básica)
- [ ] CP-09 a CP-13: Todos PASS (permisos)
- [ ] CP-14 a CP-20: Todos PASS (seguridad)
- [ ] CP-21 a CP-28: Todos PASS (sesión y recuperación)
- [ ] CP-29 a CP-32: Todos PASS (rendimiento)
- [ ] CP-33 a CP-36: Todos PASS (auditoría)
- [ ] 0 defectos CRÍTICOS
- [ ] 0-2 defectos ALTOS (máximo)
- [ ] Cobertura de código ≥ 85%

---

## 📝 REPORTE DE DEFECTOS

**Formato para reportar FAIL:**

```
DEFECTO ID: QA-BUG-001
CASO DE PRUEBA: CP-01
SEVERITY: CRÍTICO
STATUS: Abierto

DESCRIPCIÓN:
Login de estudiante no redirige a /reservas/lista-laboratorios/

RESULTADO ACTUAL:
Permanece en /accounts/login/ después de submit

RESULTADO ESPERADO:
Redirige a /reservas/lista-laboratorios/

PASOS PARA REPRODUCIR:
1. Navegar a /accounts/login/
2. Ingresar juan.estudiante / correcta123
3. Click en "Entrar"

AMBIENTE:
Django 4.2.0, Python 3.10, Windows 11

ADJUNTOS:
- Screenshot: login_fail.png
- Log: error.log
```

---

## 🚀 EJECUCIÓN RECOMENDADA

### Día 1: Pruebas Básicas
```bash
# Ejecutar CP-01 a CP-08
python manage.py test accounts.tests.LoginTests
```

### Día 2: Permisos y Seguridad
```bash
# Ejecutar CP-09 a CP-20
python manage.py test accounts.tests.SecurityTests
```

### Día 3: Rendimiento y Logs
```bash
# Ejecutar CP-29 a CP-36
python manage.py test accounts.tests.PerformanceTests
pytest accounts/tests/test_performance.py -v
```

### Herramientas Necesarias
```bash
pip install pytest-django pytest-cov freezegun locust
```

---

*Documento generado: Mayo 7, 2026*  
*Versión: 1.0*  
*Listo para Ejecución*
