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
from django.shortcuts import redirect
from django.urls import include, path

# Configuración de patrones URL principales del proyecto
urlpatterns = [
    path('', lambda request: redirect('accounts:login'), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('reservas/', include('reservas.urls')),
]

