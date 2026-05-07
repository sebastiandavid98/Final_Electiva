from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Reserva
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'reservas/lista_reservas.html'

class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    fields = ['laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'motivo']
    template_name = 'reservas/crear_reserva.html'

class ReservaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reserva
    fields = ['laboratorio', 'fecha', 'hora_inicio', 'hora_fin', 'motivo']
    template_name = 'reservas/editar_reserva.html'

    def test_func(self):
        reserva = self.get_object()
        return reserva.estado == 'pendiente'

class ReservaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Reserva
    template_name = 'reservas/eliminar_reserva.html'
    success_url = reverse_lazy('reservas:lista_reservas')

    def test_func(self):
        reserva = self.get_object()
        return reserva.estado == 'pendiente'