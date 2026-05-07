"""
Configuración del panel de administración para la aplicación reservas.

Este módulo registra los modelos en el sitio de administración de Django,
permitiendo gestionar las reservas desde la interfaz administrativa.
"""

from django.contrib import admin
from .models import Reserva

# Registro del modelo Reserva en el admin
admin.site.register(Reserva)
