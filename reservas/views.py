# reservas/views.py
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .models import Reserva
from django.contrib.auth.mixins import LoginRequiredMixin

class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    fields = ['laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'motivo']
    template_name = 'reserva_form.html'
    success_url = reverse_lazy('reserva_list')

    def form_valid(self, form):
        form.instance.usuario = self.request.user  # Asigna el usuario logueado
        return super().form_valid(form)