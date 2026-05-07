import logging

from django.core.exceptions import PermissionDenied
from django.urls import resolve
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class VerificarPermisosMiddleware(MiddlewareMixin):
    PUBLIC_URLS = {
        'accounts:login',
        'accounts:password_reset',
        'accounts:password_reset_done',
        'accounts:password_reset_confirm',
        'accounts:password_reset_complete',
    }

    COMMON_AUTH_URLS = {
        'accounts:perfil',
        'accounts:logout',
        'accounts:cambiar_contrasena',
    }

    URLS_POR_ROL = {
        'estudiante': {
            'reservas:lista_laboratorios',
            'reservas:lista_reservas',
            'reservas:mis_reservas',
            'reservas:crear_reserva',
            'reservas:editar_reserva',
            'reservas:eliminar_reserva',
            'reservas:api-reservas',
        },
        'docente': {
            'reservas:lista_laboratorios',
            'reservas:lista_reservas',
            'reservas:mis_reservas',
            'reservas:todas',
            'reservas:crear_reserva',
            'reservas:editar_reserva',
            'reservas:eliminar_reserva',
            'reservas:aprobar',
            'reservas:rechazar',
            'reservas:api-reservas',
        },
        'administrativo': {
            'accounts:lista_usuarios',
            'reservas:lista_reservas',
            'reservas:lista_laboratorios',
            'reservas:mis_reservas',
            'reservas:todas',
            'reservas:crear_reserva',
            'reservas:editar_reserva',
            'reservas:eliminar_reserva',
            'reservas:aprobar',
            'reservas:rechazar',
            'reservas:exportar_csv',
            'reservas:exportar_pdf',
            'reservas:api-reservas',
            'reportes:',
            'admin:',
        },
    }

    def process_request(self, request):
        try:
            match = resolve(request.path_info)
        except Exception:
            return None

        namespace = match.namespace
        current_url = match.url_name
        full_name = f'{namespace}:{current_url}' if namespace else current_url

        if full_name in self.PUBLIC_URLS:
            return None

        if not request.user.is_authenticated:
            return None

        if request.user.is_superuser or full_name in self.COMMON_AUTH_URLS:
            return None

        urls_permitidas = self.URLS_POR_ROL.get(request.user.rol, set())
        acceso_permitido = any(
            full_name == pattern or full_name.startswith(pattern)
            for pattern in urls_permitidas
        )

        if not acceso_permitido and namespace not in {'', None}:
            logger.warning(
                'Acceso denegado: %s intento acceder a %s',
                request.user.username,
                full_name,
            )
            raise PermissionDenied('No tienes permiso para acceder a esta pagina')

        return None
