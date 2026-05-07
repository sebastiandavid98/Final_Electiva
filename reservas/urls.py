from django.urls import path
from .views import ReservaListView, ReservaCreateView, ReservaUpdateView, ReservaDeleteView

urlpatterns = [
    path('', ReservaListView.as_view(), name='lista_reservas'),
    path('crear/', ReservaCreateView.as_view(), name='crear_reserva'),
    path('editar/<int:pk>/', ReservaUpdateView.as_view(), name='editar_reserva'),
    path('eliminar/<int:pk>/', ReservaDeleteView.as_view(), name='eliminar_reserva'),
]