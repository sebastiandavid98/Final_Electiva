from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class Usuario(AbstractUser):
    """Usuario personalizado con roles para reservas de laboratorios."""

    ESTUDIANTE = 'estudiante'
    DOCENTE = 'docente'
    ADMINISTRATIVO = 'administrativo'

    ROLES = (
        (ESTUDIANTE, 'Estudiante'),
        (DOCENTE, 'Docente'),
        (ADMINISTRATIVO, 'Administrativo'),
    )

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default=ESTUDIANTE,
        db_index=True,
        help_text='Rol del usuario en el sistema',
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(r'^\+?1?\d{9,15}$', 'Telefono invalido')
        ],
    )
    carrera = models.CharField(
        max_length=100,
        blank=True,
        help_text='Para estudiantes',
    )
    departamento = models.CharField(
        max_length=100,
        blank=True,
        help_text='Para docentes/administrativos',
    )
    fecha_ultimo_acceso = models.DateTimeField(null=True, blank=True)
    intentos_fallidos = models.PositiveIntegerField(default=0)
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
        return f'{self.username} - {self.get_rol_display()}'

    def esta_bloqueado(self):
        return bool(
            self.bloqueado_hasta and self.bloqueado_hasta > timezone.now()
        )

    def registrar_intento_fallido(self):
        self.intentos_fallidos += 1
        if self.intentos_fallidos >= 5:
            self.bloqueado_hasta = timezone.now() + timezone.timedelta(
                minutes=30
            )
        self.save(update_fields=['intentos_fallidos', 'bloqueado_hasta'])

    def resetear_intentos(self):
        self.intentos_fallidos = 0
        self.bloqueado_hasta = None
        self.save(update_fields=['intentos_fallidos', 'bloqueado_hasta'])

# Create your models here.
