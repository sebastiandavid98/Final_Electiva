# reservas/views.py
"""
Vistas para la aplicación de reservas de laboratorios.

Este módulo contiene las vistas basadas en clases para manejar
las operaciones CRUD de reservas de laboratorios.
"""

from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Reserva
from django.contrib.auth.mixins import LoginRequiredMixin


class ReservaCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear nuevas reservas de laboratorio.

    Requiere autenticación de usuario. Permite crear reservas
    asignando automáticamente el usuario logueado.

    Attributes:
        model: Modelo Reserva
        fields: Campos del formulario
        template_name: Plantilla para el formulario
        success_url: URL de redirección después de crear
    """

    model = Reserva
    fields = ['laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'motivo']
    template_name = 'reserva_form.html'
    success_url = reverse_lazy('reserva_list')

    def form_valid(self, form):
        """
        Valida el formulario y asigna el usuario logueado.

        Args:
            form: Formulario con los datos de la reserva

        Returns:
            HttpResponse: Respuesta con redirección si es válido
        """
        form.instance.usuario = self.request.user  # Asigna el usuario logueado
        return super().form_valid(form)