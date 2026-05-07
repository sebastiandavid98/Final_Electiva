"""
Configuración de URLs para el proyecto SistemaGestionReservasLaboratorios.

La lista `urlpatterns` enruta las URLs a las vistas. Para más información, ver:
https://docs.djangoproject.com/en/5.2/topics/http/urls/

Ejemplos:
- Vistas funcionales: path('', views.home, name='home')
- Vistas basadas en clases: path('', Home.as_view(), name='home')
- Incluir otras URLconfs: path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

# Configuración de patrones URL principales del proyecto
urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # Aquí se pueden agregar más rutas principales según sea necesario
    # Ejemplos:
    # path('reservas/', include('reservas.urls')),
    # path('api/', include('rest_framework.urls')),
]

