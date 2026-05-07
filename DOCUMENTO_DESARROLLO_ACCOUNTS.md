# 📋 DOCUMENTO DE DESARROLLO - APP ACCOUNTS

## 🎯 Objetivo
Implementar el módulo de autenticación y autorización para el Sistema de Gestión de Reservas de Laboratorios Universitarios, manejando tres perfiles: Estudiante, Docente y Administrativo.

---

## 📌 REQUISITOS DEL SISTEMA

### Requisitos Funcionales (RF)

| ID | Requisito |
|---|---|
| RF-01 | El sistema debe permitir iniciar sesión con nombre de usuario y contraseña |
| RF-02 | El sistema debe identificar el rol del usuario al autenticarse |
| RF-03 | El sistema debe redirigir a cada rol a un dashboard específico |
| RF-04 | El sistema debe permitir cerrar sesión |
| RF-05 | El sistema debe mostrar el perfil del usuario con sus datos |
| RF-06 | El sistema debe permitir cambiar contraseña |
| RF-07 | El sistema debe recuperar contraseña por email |
| RF-08 | El sistema debe restringir accesos según permisos por rol |
| RF-09 | El sistema debe registrar intentos de login fallidos |
| RF-10 | El sistema debe bloquear temporalmente después de 5 intentos fallidos |

### Requisitos No Funcionales (RNF)

| ID | Requisito |
|---|---|
| RNF-01 | Seguridad: Las contraseñas deben almacenarse hasheadas con PBKDF2 (por defecto Django) |
| RNF-02 | Seguridad: Las sesiones deben expirar después de 30 minutos de inactividad |
| RNF-03 | Seguridad: Todas las comunicaciones deben usar HTTPS en producción |
| RNF-04 | Rendimiento: El login no debe superar los 500ms de respuesta |
| RNF-05 | Usabilidad: El formulario de login debe ser responsive (Bootstrap 5) |
| RNF-06 | Auditoría: Todos los accesos deben quedar registrados en logs |
| RNF-07 | Disponibilidad: El módulo de autenticación debe tener 99.9% de uptime |

---

## 🏗️ CASOS DE USO

### CU-01: Login de Estudiante
```
Actor: Estudiante
Precondición: Usuario registrado con rol=estudiante
Flujo principal:
1. Estudiante ingresa a /accounts/login/
2. Ingresa usuario "juan.perez" y contraseña "****"
3. Sistema autentica y verifica rol=estudiante
4. Sistema redirige a /reservas/lista-laboratorios/
Postcondición: Estudiante ve solo laboratorios disponibles
```

### CU-02: Login de Docente
```
Actor: Docente
Precondición: Usuario registrado con rol=docente
Flujo principal:
1. Docente ingresa credenciales
2. Sistema autentica y verifica rol=docente
3. Sistema redirige a /reservas/mis-reservas/
Postcondición: Docente puede ver y aprobar reservas de sus grupos
```

### CU-03: Login de Administrativo
```
Actor: Administrativo
Precondición: Usuario registrado con rol=administrativo
Flujo principal:
1. Administrativo ingresa credenciales
2. Sistema autentica y verifica rol=administrativo
3. Sistema redirige a /dashboard/admin/
Postcondición: Administrativo tiene acceso a todas las reservas y gestión
```

### CU-04: Intento de acceso no autorizado
```
Actor: Usuario malicioso
Precondición: Usuario autenticado como estudiante
Flujo:
1. Estudiante intenta acceder a /admin/reservas/
2. Sistema verifica permisos
3. Sistema retorna HTTP 403 Forbidden
Postcondición: Acceso denegado, evento registrado en log
```

---

## 🔧 INSTRUCCIONES TÉCNICAS PASO A PASO

### FASE 1: CONFIGURACIÓN INICIAL DEL PROYECTO

#### Paso 1.1: Crear el proyecto Django
```bash
# Requisitos previos (RNF-04, RNF-07)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

pip install django==4.2 django-environ django-crispy-forms crispy-bootstrap5 django-axes

django-admin startproject SistemaGestionReservasLaboratorios
cd SistemaGestionReservasLaboratorios
python manage.py startapp accounts
```

#### Paso 1.2: Configurar variables de entorno (.env)
```python
# SistemaGestionReservasLaboratorios/.env
SECRET_KEY=tu-clave-secreta-django-64-caracteres-minimo
DEBUG=True  # False en producción (RNF-03)
DB_NAME=sistema_lab
DB_USER=postgres
DB_PASSWORD=contraseña-segura
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST_USER=noreply@universidad.edu
EMAIL_HOST_PASSWORD=pass-email
```

#### Paso 1.3: Configurar settings.py
```python
# SistemaGestionReservasLaboratorios/settings.py
import environ
from pathlib import Path

env = environ.Env()
environ.Env.read_env()

SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.universidad.edu']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'axes',
    'accounts',  # NUESTRA APP
]

AUTH_USER_MODEL = 'accounts.Usuario'

# Configuración de sesiones (RNF-02)
SESSION_COOKIE_AGE = 1800  # 30 minutos
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Seguridad (RNF-01, RNF-03)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Más seguro
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

# Para producción - HTTPS (RNF-03)
SECURE_SSL_REDIRECT = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0

# Bloqueo por intentos fallidos (RF-09, RF-10)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'axes.middleware.AxesMiddleware',  # Después de authentication
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.VerificarPermisosMiddleware',
]

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.5  # 30 minutos
AXES_LOCK_OUT_AT_FAILURE = True

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:perfil'
LOGOUT_REDIRECT_URL = 'accounts:login'
```

---

### FASE 2: MODELO DE USUARIO PERSONALIZADO

#### Paso 2.1: Crear modelo Usuario en accounts/models.py
```python
# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class Usuario(AbstractUser):
    """
    Modelo personalizado de usuario para el sistema de laboratorios
    Implementa seguridad por defecto de Django (RNF-01)
    """
    
    # Roles del sistema (RF-02)
    ROLES = (
        ('estudiante', 'Estudiante'),
        ('docente', 'Docente'),
        ('administrativo', 'Administrativo'),
    )
    
    # Campos adicionales
    rol = models.CharField(
        max_length=20, 
        choices=ROLES, 
        default='estudiante',
        db_index=True,
        help_text="Rol del usuario en el sistema"
    )
    
    telefono = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Teléfono inválido')]
    )
    
    carrera = models.CharField(max_length=100, blank=True, help_text="Para estudiantes")
    departamento = models.CharField(max_length=100, blank=True, help_text="Para docentes/administrativos")
    
    # Auditoría (RNF-06)
    fecha_ultimo_acceso = models.DateTimeField(null=True, blank=True)
    intentos_fallidos = models.IntegerField(default=0)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        permissions = [
            ('puede_reservar_laboratorio', 'Puede reservar laboratorio'),
            ('puede_aprobar_reservas', 'Puede aprobar reservas'),
            ('puede_ver_todas_reservas', 'Puede ver todas las reservas'),
            ('puede_gestionar_usuarios', 'Puede gestionar usuarios'),
            ('puede_ver_reportes', 'Puede ver reportes del sistema'),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"
    
    def esta_bloqueado(self):
        """Verifica si el usuario está temporalmente bloqueado (RF-10)"""
        if self.bloqueado_hasta and self.bloqueado_hasta > timezone.now():
            return True
        return False
    
    def registrar_intento_fallido(self):
        """Registra intento fallido de login (RF-09)"""
        self.intentos_fallidos += 1
        
        # Bloquear después de 5 intentos (RF-10)
        if self.intentos_fallidos >= 5:
            self.bloqueado_hasta = timezone.now() + timezone.timedelta(minutes=30)
        
        self.save(update_fields=['intentos_fallidos', 'bloqueado_hasta'])
    
    def resetear_intentos(self):
        """Resetea contador de intentos fallidos"""
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.save(update_fields=['intentos_fallidos', 'bloqueado_hasta'])
```

#### Paso 2.2: Ejecutar migraciones
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

---

### FASE 3: SEGURIDAD Y PERMISOS

#### Acciones Django para gestión de permisos

| Acción Django | Descripción | Uso en el sistema |
|---|---|---|
| @login_required | Decorador que requiere autenticación | Proteger vistas de reservas |
| @permission_required | Decorador que verifica permisos específicos | Controlar aprobación de reservas |
| user.has_perm() | Método para verificar permisos en tiempo real | Validar acciones en templates |
| user.get_all_permissions() | Obtener todos los permisos del usuario | Mostrar capacidades en perfil |
| user.has_module_perms() | Verificar permisos por módulo | Acceso a apps completas |
| user.is_superuser | Verificar si es superusuario | Acceso total al sistema |
| user.user_permissions.set() | Asignar permisos individuales | Otorgar permisos especiales |
| user.groups.add() | Asignar a grupos con permisos | Gestión por roles |

#### Paso 3.1: Crear gestión de permisos en accounts/permissions.py
```python
# accounts/permissions.py
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from .models import Usuario

class GestorPermisos:
    """Clase para gestionar permisos usando acciones nativas de Django"""
    
    @staticmethod
    def crear_permisos_personalizados():
        """Crea todos los permisos necesarios para el sistema"""
        content_type = ContentType.objects.get_for_model(Usuario)
        
        permisos = [
            ('puede_reservar_laboratorio', 'Puede reservar laboratorio'),
            ('puede_aprobar_reservas', 'Puede aprobar reservas'),
            ('puede_ver_todas_reservas', 'Puede ver todas las reservas'),
            ('puede_gestionar_usuarios', 'Puede gestionar usuarios'),
            ('puede_ver_reportes', 'Puede ver reportes del sistema'),
        ]
        
        for codename, name in permisos:
            Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type
            )
    
    @staticmethod
    def configurar_grupos_por_rol():
        """Configura grupos automáticamente según roles"""
        
        # Definir permisos por rol
        permisos_por_rol = {
            'estudiante': ['puede_reservar_laboratorio'],
            'docente': ['puede_reservar_laboratorio', 'puede_aprobar_reservas'],
            'administrativo': [
                'puede_reservar_laboratorio', 
                'puede_aprobar_reservas',
                'puede_ver_todas_reservas',
                'puede_gestionar_usuarios',
                'puede_ver_reportes'
            ]
        }
        
        for rol, permisos in permisos_por_rol.items():
            grupo, _ = Group.objects.get_or_create(name=rol)
            grupo.permissions.clear()
            
            for permiso_nombre in permisos:
                permiso = Permission.objects.get(codename=permiso_nombre)
                grupo.permissions.add(permiso)
    
    @staticmethod
    def verificar_acceso(user, permiso_requerido, request=None):
        """
        Verifica acceso usando métodos nativos de Django
        Retorna: bool
        """
        if not user.is_authenticated:
            return False
        
        # Superusuario tiene todos los permisos
        if user.is_superuser:
            return True
        
        # Verificar permiso específico
        return user.has_perm(f'accounts.{permiso_requerido}')
```

#### Paso 3.2: Crear decoradores personalizados
```python
# accounts/decorators.py
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test, login_required
from functools import wraps
from .models import Usuario

def requerir_rol(*roles):
    """
    Decorador que verifica rol del usuario
    Uso: @requerir_rol('docente', 'administrativo')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect('accounts:login')
            
            if request.user.rol not in roles and not request.user.is_superuser:
                raise PermissionDenied("No tienes permisos para acceder a esta sección")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def requerir_permiso(permiso):
    """
    Decorador que verifica permiso específico usando has_perm() de Django
    Uso: @requerir_permiso('puede_aprobar_reservas')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect('accounts:login')
            
            permiso_completo = f'accounts.{permiso}' if not permiso.startswith('accounts.') else permiso
            
            if not request.user.has_perm(permiso_completo) and not request.user.is_superuser:
                raise PermissionDenied(f"Se requiere permiso: {permiso}")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

---

### FASE 4: VISTAS DE AUTENTICACIÓN

#### Paso 4.1: Vista de login con seguridad mejorada
```python
# accounts/views.py
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
from .models import Usuario
from .forms import LoginForm, RegistroForm, PerfilForm
from .decorators import requerir_rol, requerir_permiso
import logging

logger = logging.getLogger(__name__)

def login_view(request):
    """
    Vista de autenticación con:
    - Bloqueo por intentos fallidos (RF-10)
    - Registro de logs (RNF-06)
    - Redirección por rol (RF-03)
    """
    if request.user.is_authenticated:
        return redirect('accounts:perfil')
    
    form = LoginForm()
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Verificar límite de intentos global por IP (con cache)
            ip = request.META.get('REMOTE_ADDR')
            cache_key = f'login_attempts_{ip}'
            attempts = cache.get(cache_key, 0)
            
            if attempts >= 10:  # 10 intentos desde la misma IP
                messages.error(request, 'Demasiados intentos. Espera 5 minutos.')
                logger.warning(f"Demasiados intentos desde IP: {ip}")
                return render(request, 'accounts/login.html', {'form': form})
            
            # Autenticar usuario
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Verificar si está bloqueado
                if user.esta_bloqueado():
                    messages.error(request, f'Cuenta bloqueada hasta {user.bloqueado_hasta.strftime("%H:%M")}')
                    logger.warning(f"Intento de acceso a cuenta bloqueada: {username}")
                    return render(request, 'accounts/login.html', {'form': form})
                
                # Login exitoso
                login(request, user)
                user.resetear_intentos()
                user.fecha_ultimo_acceso = timezone.now()
                user.save(update_fields=['fecha_ultimo_acceso', 'intentos_fallidos', 'bloqueado_hasta'])
                
                # Limpiar cache de intentos
                cache.delete(cache_key)
                
                # Registrar evento exitoso
                logger.info(f"Login exitoso: {username} - Rol: {user.get_rol_display()}")
                
                # Redirigir según rol (RF-03)
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                
                # Dashboard por rol (CU-01, CU-02, CU-03)
                if user.rol == 'estudiante':
                    return redirect('reservas:lista_laboratorios')
                elif user.rol == 'docente':
                    return redirect('reservas:mis_reservas')
                elif user.rol == 'administrativo':
                    return redirect('admin:dashboard')
                else:
                    return redirect('accounts:perfil')
            else:
                # Intento fallido
                cache.set(cache_key, attempts + 1, 300)  # 5 minutos
                
                # Registrar usuario específico si existe
                try:
                    user_obj = Usuario.objects.get(username=username)
                    user_obj.registrar_intento_fallido()
                    logger.warning(f"Login fallido para usuario existente: {username}")
                except Usuario.DoesNotExist:
                    logger.warning(f"Login fallido - usuario inexistente: {username}")
                
                messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    """Cierre de sesión con limpieza de datos"""
    logger.info(f"Logout: {request.user.username}")
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('accounts:login')

@login_required
def perfil_view(request):
    """Ver y editar perfil del usuario"""
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('accounts:perfil')
    else:
        form = PerfilForm(instance=request.user)
    
    return render(request, 'accounts/perfil.html', {
        'form': form,
        'user': request.user
    })

@login_required
def cambiar_contrasena(request):
    """Cambio de contraseña con validaciones de seguridad"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Mantener sesión
            messages.success(request, 'Contraseña actualizada correctamente')
            logger.info(f"Cambio de contraseña: {request.user.username}")
            return redirect('accounts:perfil')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/cambiar_contrasena.html', {'form': form})

@login_required
@requerir_permiso('puede_gestionar_usuarios')
def lista_usuarios(request):
    """Lista de usuarios del sistema (solo administrativos)"""
    usuarios = Usuario.objects.all().order_by('rol', 'username')
    return render(request, 'accounts/lista_usuarios.html', {'usuarios': usuarios})
```

#### Paso 4.2: Formularios con validación
```python
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import Usuario

class LoginForm(forms.Form):
    """Formulario de login con validación"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

class RegistroForm(UserCreationForm):
    """Formulario de registro de nuevos usuarios"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    telefono = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'telefono', 'rol', 'carrera', 'departamento', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'carrera': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.telefono = self.cleaned_data['telefono']
        if commit:
            user.save()
        return user

class PerfilForm(forms.ModelForm):
    """Formulario de edición de perfil"""
    class Meta:
        model = Usuario
        fields = ['email', 'telefono', 'carrera', 'departamento']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'carrera': forms.TextInput(attrs={'class': 'form-control'}),
            'departamento': forms.TextInput(attrs={'class': 'form-control'}),
        }
```

---

### FASE 5: TEMPLATES Y FRONTEND

#### Paso 5.1: Template base
```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Laboratorios - {% block title %}Universidad{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .errorlist { color: red; list-style: none; padding: 0; }
        .alert { margin-top: 1rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{% url 'accounts:perfil' %}">Laboratorios</a>
            {% if user.is_authenticated %}
            <div class="navbar-nav ms-auto">
                <span class="nav-link">Hola, {{ user.username }} ({{ user.get_rol_display }})</span>
                <a class="nav-link" href="{% url 'accounts:perfil' %}">Perfil</a>
                <a class="nav-link" href="{% url 'accounts:logout' %}">Salir</a>
            </div>
            {% endif %}
        </div>
    </nav>
    
    <div class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

#### Paso 5.2: Template de login
```html
<!-- templates/accounts/login.html -->
{% extends 'base.html' %}
{% load crispy_forms_tags %}

{% block title %}Iniciar Sesión{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0">Iniciar Sesión</h4>
            </div>
            <div class="card-body">
                <form method="post">
                    {% csrf_token %}
                    {{ form|crispy }}
                    <button type="submit" class="btn btn-primary w-100">Entrar</button>
                </form>
                <hr>
                <div class="text-center">
                    <a href="{% url 'password_reset' %}">¿Olvidaste tu contraseña?</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

### FASE 6: URLS Y MIDDLEWARE

#### Paso 6.1: Configuración de URLs
```python
# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Perfil
    path('perfil/', views.perfil_view, name='perfil'),
    path('cambiar-contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    
    # Gestión de usuarios (solo administrativos)
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    
    # Recuperación de contraseña
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
```

#### Paso 6.2: Middleware de seguridad personalizado
```python
# accounts/middleware.py
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class VerificarPermisosMiddleware(MiddlewareMixin):
    """
    Middleware que verifica permisos en cada request
    """
    
    # URLs públicas que no requieren autenticación
    PUBLIC_URLS = [
        'accounts:login',
        'accounts:password_reset',
        'accounts:password_reset_done',
        'accounts:password_reset_confirm',
        'accounts:password_reset_complete',
    ]
    
    # Mapeo de URLs por rol (accesos permitidos)
    URLS_POR_ROL = {
        'estudiante': ['reservas:lista_laboratorios', 'reservas:mi_reserva'],
        'docente': ['reservas:lista_laboratorios', 'reservas:mis_reservas', 'reservas:aprobar'],
        'administrativo': ['admin:', 'reservas:todas', 'accounts:lista_usuarios', 'reportes:'],
    }
    
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None
        
        # Obtener nombre de la vista actual
        try:
            current_url = resolve(request.path_info).url_name
            namespace = resolve(request.path_info).namespace
            full_name = f"{namespace}:{current_url}" if namespace else current_url
        except:
            return None
        
        # Superusuario puede acceder a todo
        if request.user.is_superuser:
            return None
        
        # Verificar si la URL es permitida para su rol
        urls_permitidas = self.URLS_POR_ROL.get(request.user.rol, [])
        
        acceso_permitido = False
        for url_pattern in urls_permitidas:
            if full_name and (full_name.startswith(url_pattern) or (current_url and current_url.startswith(url_pattern))):
                acceso_permitido = True
                break
        
        if not acceso_permitido and full_name not in self.PUBLIC_URLS:
            logger.warning(f"Acceso denegado: {request.user.username} intentó acceder a {full_name}")
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("No tienes permiso para acceder a esta página")
        
        return None
```

#### Paso 6.3: Registrar middleware en settings.py
```python
# Ya incluido en Paso 1.3
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'accounts.middleware.VerificarPermisosMiddleware',
]
```

---

### FASE 7: SEÑALES Y SISTEMA DE REGISTRO

#### Paso 7.1: Señales para asignación automática de grupos
```python
# accounts/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Usuario
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Usuario)
def asignar_grupo_segun_rol(sender, instance, created, **kwargs):
    """
    Asigna automáticamente al usuario al grupo correspondiente según su rol
    """
    if created:
        try:
            grupo = Group.objects.get(name=instance.rol)
            instance.groups.add(grupo)
            logger.info(f"Usuario {instance.username} asignado al grupo {instance.rol}")
        except Group.DoesNotExist:
            logger.error(f"Grupo {instance.rol} no existe.")

@receiver(pre_save, sender=Usuario)
def actualizar_grupo_si_cambia_rol(sender, instance, **kwargs):
    """
    Si cambia el rol del usuario, actualiza su grupo
    """
    if instance.pk:
        try:
            old_instance = Usuario.objects.get(pk=instance.pk)
            if old_instance.rol != instance.rol:
                # Remover del grupo anterior
                try:
                    old_group = Group.objects.get(name=old_instance.rol)
                    instance.groups.remove(old_group)
                except Group.DoesNotExist:
                    pass
                
                # Agregar al nuevo grupo
                try:
                    new_group = Group.objects.get(name=instance.rol)
                    instance.groups.add(new_group)
                    logger.info(f"Usuario {instance.username} cambió de rol")
                except Group.DoesNotExist:
                    logger.error(f"Grupo {instance.rol} no existe")
        except Usuario.DoesNotExist:
            pass
```

#### Paso 7.2: Registrar señales en apps.py
```python
# accounts/apps.py
from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        import accounts.signals
```

---

### FASE 8: CONFIGURACIÓN DE LOGGING

#### Paso 8.1: Logging en settings.py
```python
# SistemaGestionReservasLaboratorios/settings.py (agregar al final)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/sistema.log',
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/security.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'accounts': {
            'handlers': ['console', 'security_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## ✅ LISTA DE VERIFICACIÓN DE IMPLEMENTACIÓN

### Configuración Inicial
- [ ] Crear proyecto Django y app accounts
- [ ] Instalar dependencias requeridas
- [ ] Configurar variables de entorno (.env)
- [ ] Configurar settings.py con todas las apps y middleware
- [ ] Crear estructura de carpetas (templates, static, logs)

### Modelos y Base de Datos
- [ ] Implementar modelo Usuario personalizado
- [ ] Ejecutar migraciones
- [ ] Crear superusuario administrativo
- [ ] Verificar base de datos

### Seguridad y Permisos
- [ ] Crear permisos personalizados
- [ ] Crear grupos por rol
- [ ] Implementar decoradores personalizados
- [ ] Configurar middleware de permisos
- [ ] Probar control de acceso

### Vistas y Formularios
- [ ] Implementar vista de login con seguridad
- [ ] Implementar vista de logout
- [ ] Implementar vista de perfil
- [ ] Implementar cambio de contraseña
- [ ] Crear formularios con validación

### Templates
- [ ] Crear template base (base.html)
- [ ] Crear template de login
- [ ] Crear template de perfil
- [ ] Crear template de cambio de contraseña
- [ ] Crear template de lista de usuarios
- [ ] Aplicar Bootstrap 5 responsive

### Rutas y URLs
- [ ] Configurar urls.py de accounts
- [ ] Registrar en urls.py principal
- [ ] Probar todas las rutas

### Logging y Auditoría
- [ ] Configurar logging en settings.py
- [ ] Crear carpeta logs/
- [ ] Probar registro de eventos

### Señales
- [ ] Implementar señales para grupos
- [ ] Registrar en apps.py
- [ ] Probar asignación automática de grupos

### Pruebas
- [ ] Probar login con cada rol
- [ ] Probar redirecciones según rol
- [ ] Probar bloqueo por intentos fallidos
- [ ] Probar logout
- [ ] Probar cambio de contraseña
- [ ] Probar acceso a rutas sin permiso
- [ ] Verificar logs

---

## 📊 MAPA DE RUTAS

### Rutas Públicas
- `GET /accounts/login/` - Formulario de login
- `POST /accounts/login/` - Procesar login
- `GET /accounts/password-reset/` - Solicitar recuperación
- `GET /accounts/reset/<uidb64>/<token>/` - Restablecer contraseña

### Rutas Protegidas (Todos autenticados)
- `GET /accounts/perfil/` - Ver perfil
- `POST /accounts/perfil/` - Editar perfil
- `GET /accounts/cambiar-contrasena/` - Formulario cambio contraseña
- `POST /accounts/cambiar-contrasena/` - Procesar cambio
- `GET /accounts/logout/` - Cerrar sesión

### Rutas Administrativas
- `GET /accounts/usuarios/` - Lista de usuarios

---

## 🔐 MATRIZ DE PERMISOS POR ROL

| Acción | Estudiante | Docente | Administrativo |
|---|:---:|:---:|:---:|
| Iniciar sesión | ✅ | ✅ | ✅ |
| Ver perfil | ✅ | ✅ | ✅ |
| Cambiar contraseña | ✅ | ✅ | ✅ |
| Reservar laboratorio | ✅ | ✅ | ✅ |
| Ver mis reservas | ✅ | ✅ | ✅ |
| Aprobar reservas | ❌ | ✅ | ✅ |
| Ver todas reservas | ❌ | ❌ | ✅ |
| Gestionar usuarios | ❌ | ❌ | ✅ |
| Ver reportes | ❌ | ❌ | ✅ |

---

## 🚀 PRÓXIMAS FASES (DESPUÉS DE ACCOUNTS)

1. **App Reservas** - Gestión de reservas de laboratorios
2. **App Laboratorios** - Catálogo de laboratorios disponibles
3. **App Reportes** - Generación de reportes y estadísticas
4. **API REST** - Endpoints para aplicación móvil
5. **Tests Automatizados** - Suite completa de pruebas
6. **Documentación API** - Swagger/OpenAPI

---

## 📝 NOTAS IMPORTANTES

- **Seguridad**: Todas las contraseñas se almacenan hasheadas con PBKDF2 por defecto en Django
- **Sesiones**: Expiran automáticamente después de 30 minutos de inactividad
- **Auditoría**: Todos los eventos se registran en logs separados
- **Escalabilidad**: El middleware está optimizado para alto volumen de usuarios
- **Cumplimiento**: El sistema cumple con estándares OWASP y regulaciones de privacidad

---

*Documento generado: Mayo 7, 2026*
*Estado: Listo para implementación*
