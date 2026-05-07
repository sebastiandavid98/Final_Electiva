"""
Configuración de la aplicación 'reservas'.

Este módulo contiene la configuración específica de la aplicación
de gestión de reservas de laboratorios.
"""

from django.apps import AppConfig


class ReservasConfig(AppConfig):
    """
    Configuración de la aplicación Reservas.

    Define la configuración por defecto para la aplicación
    de gestión de reservas de laboratorios.
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reservas'
    verbose_name = 'Sistema de Reservas'
