from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Reserva


class ReservasFlowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.estudiante = User.objects.create_user(
            username='estudiante.reservas',
            password='Prueba12345!',
            rol='estudiante',
        )
        self.otro = User.objects.create_user(
            username='otro.reservas',
            password='Prueba12345!',
            rol='estudiante',
        )
        self.docente = User.objects.create_user(
            username='docente.reservas',
            password='Prueba12345!',
            rol='docente',
        )
        self.admin = User.objects.create_user(
            username='admin.reservas',
            password='Prueba12345!',
            rol='administrativo',
        )
        self.fecha = date.today() + timedelta(days=1)

    def crear_reserva(self, usuario=None, **extra):
        data = {
            'usuario': usuario or self.estudiante,
            'laboratorio': 'Lab 1',
            'fecha': self.fecha,
            'hora_inicio': time(8, 0),
            'hora_fin': time(10, 0),
            'motivo': 'Clase practica',
        }
        data.update(extra)
        return Reserva.objects.create(**data)

    def test_crear_reserva_asigna_usuario_autenticado(self):
        self.client.force_login(self.estudiante)
        response = self.client.post(
            reverse('reservas:crear_reserva'),
            {
                'laboratorio': 'Lab 2',
                'fecha': self.fecha.isoformat(),
                'hora_inicio': '09:00',
                'hora_fin': '11:00',
                'motivo': 'Investigacion',
            },
        )

        self.assertRedirects(response, reverse('reservas:mis_reservas'))
        reserva = Reserva.objects.get(laboratorio='Lab 2')
        self.assertEqual(reserva.usuario, self.estudiante)
        self.assertEqual(reserva.estado, 'pendiente')

    def test_no_permite_conflicto_horario(self):
        self.crear_reserva()

        with self.assertRaises(ValidationError):
            self.crear_reserva(
                usuario=self.otro,
                hora_inicio=time(9, 0),
                hora_fin=time(11, 0),
            )

    def test_no_permite_editar_reserva_ajena(self):
        reserva = self.crear_reserva(usuario=self.otro)
        self.client.force_login(self.estudiante)

        response = self.client.get(
            reverse('reservas:editar_reserva', kwargs={'pk': reserva.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_no_permite_editar_reserva_aprobada(self):
        reserva = self.crear_reserva(estado='aprobada')
        self.client.force_login(self.estudiante)

        response = self.client.get(
            reverse('reservas:editar_reserva', kwargs={'pk': reserva.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_docente_puede_aprobar_reserva(self):
        reserva = self.crear_reserva()
        self.client.force_login(self.docente)

        response = self.client.post(
            reverse('reservas:aprobar', kwargs={'pk': reserva.pk})
        )

        self.assertRedirects(response, reverse('reservas:todas'))
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, 'aprobada')

    def test_estudiante_no_puede_aprobar_reserva(self):
        reserva = self.crear_reserva()
        self.client.force_login(self.estudiante)

        response = self.client.post(
            reverse('reservas:aprobar', kwargs={'pk': reserva.pk})
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_puede_exportar_csv(self):
        self.crear_reserva()
        self.client.force_login(self.admin)

        response = self.client.get(reverse('reservas:exportar_csv'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('reservas.csv', response['Content-Disposition'])

    def test_admin_puede_exportar_pdf(self):
        self.crear_reserva()
        self.client.force_login(self.admin)

        response = self.client.get(reverse('reservas:exportar_pdf'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('reservas.pdf', response['Content-Disposition'])
        self.assertTrue(response.content.startswith(b'%PDF'))
