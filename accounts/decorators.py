from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def requerir_rol(*roles):
    """Exige que el usuario autenticado tenga uno de los roles indicados."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser or request.user.rol in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied('No tienes permisos para acceder a esta seccion')

        return wrapper

    return decorator


def requerir_permiso(permiso):
    """Exige un permiso Django, aceptando codename corto o app.codename."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')

            permiso_completo = permiso
            if not permiso_completo.startswith('accounts.'):
                permiso_completo = f'accounts.{permiso}'

            if request.user.is_superuser or request.user.has_perm(permiso_completo):
                return view_func(request, *args, **kwargs)
            raise PermissionDenied(f'Se requiere permiso: {permiso}')

        return wrapper

    return decorator
