from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .api import ReservaViewSet

app_name = 'reservas'

router = DefaultRouter()
router.register('reservas', ReservaViewSet, basename='api-reservas')

urlpatterns = [
    path('', views.ReservaListView.as_view(), name='lista_reservas'),
    path('dashboard/', views.DashboardAdministrativoView.as_view(), name='dashboard'),
    path('lista-laboratorios/', views.ListaLaboratoriosView.as_view(), name='lista_laboratorios'),
    path('mis-reservas/', views.MisReservasView.as_view(), name='mis_reservas'),
    path('todas/', views.TodasReservasView.as_view(), name='todas'),
    path('crear/', views.ReservaCreateView.as_view(), name='crear_reserva'),
    path('editar/<int:pk>/', views.ReservaUpdateView.as_view(), name='editar_reserva'),
    path('eliminar/<int:pk>/', views.ReservaDeleteView.as_view(), name='eliminar_reserva'),
    path('aprobar/<int:pk>/', views.AprobarReservaView.as_view(), name='aprobar'),
    path('rechazar/<int:pk>/', views.RechazarReservaView.as_view(), name='rechazar'),
    path('exportar/csv/', views.ExportarReservasCSVView.as_view(), name='exportar_csv'),
    path('exportar/pdf/', views.ExportarReservasPDFView.as_view(), name='exportar_pdf'),
    path('api/', include(router.urls)),
]
