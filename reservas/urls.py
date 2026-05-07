"""
URLs para la aplicación de reservas.

Este módulo define las rutas URL para las operaciones CRUD
de reservas de laboratorios.
"""

from django.urls import path
from .views import ReservaListView, ReservaCreateView, ReservaUpdateView, ReservaDeleteView

# Definición de patrones URL para la aplicación de reservas
urlpatterns = [
    # Lista todas las reservas
    path('', ReservaListView.as_view(), name='lista_reservas'),

    # Crear nueva reserva
    path('crear/', ReservaCreateView.as_view(), name='crear_reserva'),

    # Editar reserva existente (requiere ID)
    path('editar/<int:pk>/', ReservaUpdateView.as_view(), name='editar_reserva'),

    # Eliminar reserva (requiere ID)
    path('eliminar/<int:pk>/', ReservaDeleteView.as_view(), name='eliminar_reserva'),
]