from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from .models import Usuario


class GestorPermisos:
    """Gestiona permisos y grupos basados en los roles del sistema."""

    PERMISOS = [
        ('puede_reservar_laboratorio', 'Puede reservar laboratorio'),
        ('puede_aprobar_reservas', 'Puede aprobar reservas'),
        ('puede_ver_todas_reservas', 'Puede ver todas las reservas'),
        ('puede_gestionar_usuarios', 'Puede gestionar usuarios'),
        ('puede_ver_reportes', 'Puede ver reportes del sistema'),
    ]

    PERMISOS_POR_ROL = {
        Usuario.ESTUDIANTE: ['puede_reservar_laboratorio'],
        Usuario.DOCENTE: [
            'puede_reservar_laboratorio',
            'puede_aprobar_reservas',
        ],
        Usuario.ADMINISTRATIVO: [
            'puede_reservar_laboratorio',
            'puede_aprobar_reservas',
            'puede_ver_todas_reservas',
            'puede_gestionar_usuarios',
            'puede_ver_reportes',
        ],
    }

    @staticmethod
    def crear_permisos_personalizados():
        content_type = ContentType.objects.get_for_model(Usuario)
        for codename, name in GestorPermisos.PERMISOS:
            Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type,
            )

    @staticmethod
    def configurar_grupos_por_rol():
        GestorPermisos.crear_permisos_personalizados()
        content_type = ContentType.objects.get_for_model(Usuario)

        for rol, permisos in GestorPermisos.PERMISOS_POR_ROL.items():
            grupo, _ = Group.objects.get_or_create(name=rol)
            grupo.permissions.clear()
            permisos_queryset = Permission.objects.filter(
                content_type=content_type,
                codename__in=permisos,
            )
            grupo.permissions.add(*permisos_queryset)

    @staticmethod
    def verificar_acceso(user, permiso_requerido):
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        permiso = permiso_requerido
        if not permiso.startswith('accounts.'):
            permiso = f'accounts.{permiso}'
        return user.has_perm(permiso)
