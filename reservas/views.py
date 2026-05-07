import csv

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import models
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, TemplateView

from accounts.models import Usuario

from .forms import ReservaForm
from .models import Reserva


class ReservaQuerysetMixin:
    model = Reserva
    context_object_name = 'reservas'

    def get_queryset(self):
        queryset = Reserva.objects.select_related('usuario')
        user = self.request.user
        if user.is_superuser or user.rol == Usuario.ADMINISTRATIVO:
            return queryset
        return queryset.filter(usuario=user)


class ReservaListView(LoginRequiredMixin, ReservaQuerysetMixin, ListView):
    template_name = 'reservas/lista_reservas.html'


class ListaLaboratoriosView(LoginRequiredMixin, ListView):
    template_name = 'reservas/lista_laboratorios.html'
    context_object_name = 'laboratorios'

    def get_queryset(self):
        return (
            Reserva.objects.order_by('laboratorio')
            .values_list('laboratorio', flat=True)
            .distinct()
        )


class MisReservasView(LoginRequiredMixin, ReservaQuerysetMixin, ListView):
    template_name = 'reservas/mis_reservas.html'


class TodasReservasView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Reserva
    context_object_name = 'reservas'
    template_name = 'reservas/todas_reservas.html'

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.rol in {Usuario.DOCENTE, Usuario.ADMINISTRATIVO}

    def get_queryset(self):
        queryset = Reserva.objects.select_related('usuario')
        if self.request.user.rol == Usuario.DOCENTE:
            queryset = queryset.filter(estado='pendiente')
        estado = self.request.GET.get('estado')
        laboratorio = self.request.GET.get('laboratorio')
        if estado:
            queryset = queryset.filter(estado=estado)
        if laboratorio:
            queryset = queryset.filter(laboratorio__icontains=laboratorio)
        return queryset


class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas/reserva_form.html'
    success_url = reverse_lazy('reservas:mis_reservas')

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Reserva creada correctamente.')
        return super().form_valid(form)


class ReservaUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'reservas/reserva_form.html'
    success_url = reverse_lazy('reservas:mis_reservas')

    def test_func(self):
        reserva = self.get_object()
        user = self.request.user
        es_dueno = reserva.usuario_id == user.id
        es_admin = user.is_superuser or user.rol == Usuario.ADMINISTRATIVO
        return reserva.puede_modificarse and (es_dueno or es_admin)

    def form_valid(self, form):
        messages.success(self.request, 'Reserva actualizada correctamente.')
        return super().form_valid(form)


class ReservaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Reserva
    template_name = 'reservas/eliminar_reserva.html'
    success_url = reverse_lazy('reservas:mis_reservas')

    def test_func(self):
        reserva = self.get_object()
        user = self.request.user
        es_dueno = reserva.usuario_id == user.id
        es_admin = user.is_superuser or user.rol == Usuario.ADMINISTRATIVO
        return reserva.puede_modificarse and (es_dueno or es_admin)

    def form_valid(self, form):
        messages.success(self.request, 'Reserva eliminada correctamente.')
        return super().form_valid(form)


class CambiarEstadoReservaView(LoginRequiredMixin, UserPassesTestMixin, View):
    estado = None

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.rol in {Usuario.DOCENTE, Usuario.ADMINISTRATIVO}

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        if reserva.estado != 'pendiente':
            messages.error(request, 'Solo se pueden cambiar reservas pendientes.')
            return redirect('reservas:todas')
        reserva.estado = self.estado
        reserva.save(update_fields=['estado'])
        messages.success(request, f'Reserva {self.estado} correctamente.')
        if request.user.rol == Usuario.DOCENTE:
            return redirect('reservas:todas')
        return redirect('reservas:todas')


class AprobarReservaView(CambiarEstadoReservaView):
    estado = 'aprobada'


class RechazarReservaView(CambiarEstadoReservaView):
    estado = 'rechazada'


class ExportarReservasCSVView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.rol == Usuario.ADMINISTRATIVO

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reservas.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Usuario', 'Laboratorio', 'Fecha', 'Inicio', 'Fin', 'Estado', 'Motivo'])
        for reserva in Reserva.objects.select_related('usuario').order_by('fecha', 'hora_inicio'):
            writer.writerow([
                reserva.id,
                reserva.usuario.username,
                reserva.laboratorio,
                reserva.fecha,
                reserva.hora_inicio,
                reserva.hora_fin,
                reserva.estado,
                reserva.motivo,
            ])
        return response


def _pdf_escape(text):
    return str(text).replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')


def _generar_pdf_simple(lineas):
    stream_lines = ['BT', '/F1 10 Tf', '50 780 Td']
    for index, linea in enumerate(lineas[:45]):
        if index:
            stream_lines.append('0 -16 Td')
        stream_lines.append(f'({_pdf_escape(linea)}) Tj')
    stream_lines.append('ET')
    stream = '\n'.join(stream_lines).encode('latin-1', errors='replace')

    objects = [
        b'1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n',
        b'2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n',
        b'3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] '
        b'/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n',
        b'4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n',
        b'5 0 obj << /Length ' + str(len(stream)).encode('ascii') + b' >> stream\n'
        + stream + b'\nendstream endobj\n',
    ]
    pdf = bytearray(b'%PDF-1.4\n')
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)
    xref_offset = len(pdf)
    pdf.extend(f'xref\n0 {len(objects) + 1}\n'.encode('ascii'))
    pdf.extend(b'0000000000 65535 f \n')
    for offset in offsets[1:]:
        pdf.extend(f'{offset:010d} 00000 n \n'.encode('ascii'))
    pdf.extend(
        f'trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n'
        f'startxref\n{xref_offset}\n%%EOF\n'.encode('ascii')
    )
    return bytes(pdf)


class ExportarReservasPDFView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.rol == Usuario.ADMINISTRATIVO

    def get(self, request):
        lineas = ['Reporte de reservas', '']
        for reserva in Reserva.objects.select_related('usuario').order_by('fecha', 'hora_inicio'):
            lineas.append(
                f'{reserva.id} | {reserva.fecha} | {reserva.laboratorio} | '
                f'{reserva.hora_inicio}-{reserva.hora_fin} | {reserva.estado} | '
                f'{reserva.usuario.username}'
            )
        response = HttpResponse(_generar_pdf_simple(lineas), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reservas.pdf"'
        return response


class DashboardAdministrativoView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Vista del dashboard administrativo.
    Muestra estadísticas generales de reservas.
    Solo accesible para administrativo y superuser.
    """
    template_name = 'reservas/dashboard.html'

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.rol == Usuario.ADMINISTRATIVO

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservas = Reserva.objects.all()
        context['total_reservas'] = reservas.count()
        context['reservas_pendientes'] = reservas.filter(estado='pendiente').count()
        context['reservas_aprobadas'] = reservas.filter(estado='aprobada').count()
        context['reservas_rechazadas'] = reservas.filter(estado='rechazada').count()
        context['ultimas_reservas'] = reservas.order_by('-fecha_creacion')[:5]
        context['laboratorios_populares'] = (
            reservas.values('laboratorio')
            .annotate(count=models.Count('id'))
            .order_by('-count')[:5]
        )
        return context
