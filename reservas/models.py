# reservas/models.py
"""
Modelos de datos para la aplicación de reservas de laboratorios.

Este módulo define los modelos principales del sistema de gestión de reservas,
incluyendo la entidad Reserva que representa las solicitudes de uso de laboratorios.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Reserva(models.Model):
    """
    Modelo que representa una reserva de laboratorio.

    Una reserva contiene información sobre el usuario que la solicita,
    el laboratorio reservado, fechas y horas, estado de aprobación,
    y motivo de la reserva.

    Attributes:
        usuario (ForeignKey): Usuario que realiza la reserva
        laboratorio (CharField): Nombre del laboratorio a reservar
        fecha (DateField): Fecha de la reserva
        hora_inicio (TimeField): Hora de inicio de la reserva
        hora_fin (TimeField): Hora de fin de la reserva
        estado (CharField): Estado actual de la reserva
        motivo (TextField): Motivo o descripción de la reserva
        fecha_creacion (DateTimeField): Fecha y hora de creación automática
    """

    ESTADOS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Usuario que realiza la reserva"
    )
    laboratorio = models.CharField(
        max_length=100,
        help_text="Nombre del laboratorio a reservar"
    )
    fecha = models.DateField(
        help_text="Fecha de la reserva"
    )
    hora_inicio = models.TimeField(
        help_text="Hora de inicio de la reserva"
    )
    hora_fin = models.TimeField(
        help_text="Hora de fin de la reserva"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_CHOICES,
        default='pendiente',
        help_text="Estado actual de la reserva"
    )
    motivo = models.TextField(
        help_text="Motivo o descripción detallada de la reserva"
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de creación de la reserva"
    )

    class Meta:
        """
        Metadatos del modelo Reserva.
        """
        ordering = ['-fecha_creacion']
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

    def clean(self):
        if self.fecha and self.fecha < timezone.localdate():
            raise ValidationError('No se pueden crear reservas en fechas pasadas.')

        if self.hora_inicio and self.hora_fin and self.hora_fin <= self.hora_inicio:
            raise ValidationError('La hora final debe ser mayor que la hora inicial.')

        if self.laboratorio and self.fecha and self.hora_inicio and self.hora_fin:
            conflictos = Reserva.objects.filter(
                laboratorio__iexact=self.laboratorio,
                fecha=self.fecha,
                hora_inicio__lt=self.hora_fin,
                hora_fin__gt=self.hora_inicio,
            ).exclude(pk=self.pk)
            if conflictos.exists():
                raise ValidationError('Ya existe una reserva para ese laboratorio en ese horario.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def puede_modificarse(self):
        return self.estado == 'pendiente'

    def __str__(self):
        """
        Representación en cadena del objeto Reserva.

        Returns:
            str: Cadena con ID, laboratorio y fecha de la reserva
        """
        return f"Reserva {self.id} - {self.laboratorio} - {self.fecha}"
