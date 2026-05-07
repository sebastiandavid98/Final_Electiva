#!/usr/bin/env python
"""
Crea usuarios de demostracion con roles especificos.

Uso:
    python manage.py shell < crear_usuarios_demo.py
"""

import django
import os

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'SistemaGestionReservasLaboratorios.settings',
)
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

from accounts.permissions import GestorPermisos  # noqa: E402


Usuario = get_user_model()
PASSWORD_DEMO = 'Admon1234*'


def crear_usuario(username, email, rol, **extra):
    user, created = Usuario.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'rol': rol,
            **extra,
        },
    )
    if created:
        user.set_password(PASSWORD_DEMO)
        user.save()
        print(f'OK creado: {username}')
    else:
        print(f'INFO ya existe: {username}')
    return user


GestorPermisos.configurar_grupos_por_rol()
print('OK permisos y grupos configurados')

admin_user, created = Usuario.objects.get_or_create(
    username='admin123',
    defaults={
        'email': 'admin@universidad.edu',
        'rol': 'administrativo',
        'is_staff': True,
        'is_superuser': True,
    },
)
if created:
    admin_user.set_password(PASSWORD_DEMO)
    admin_user.save()
    print('OK superusuario creado: admin123')
else:
    print('INFO superusuario ya existe: admin123')

crear_usuario(
    'estudiante',
    'estudiante@universidad.edu',
    'estudiante',
    carrera='Ingenieria en Sistemas',
)
crear_usuario(
    'docente',
    'docente@universidad.edu',
    'docente',
    departamento='Departamento de Ingenieria',
)
crear_usuario(
    'administrativo',
    'administrativo@universidad.edu',
    'administrativo',
    departamento='Administracion',
)

print('\n' + '=' * 50)
print('CREDENCIALES PARA DEMO')
print('=' * 50)
print(f'admin123 / {PASSWORD_DEMO} / administrativo superuser')
print(f'estudiante / {PASSWORD_DEMO} / estudiante')
print(f'docente / {PASSWORD_DEMO} / docente')
print(f'administrativo / {PASSWORD_DEMO} / administrativo')
print('Acceso: http://127.0.0.1:8000/accounts/login/')
print('=' * 50)
