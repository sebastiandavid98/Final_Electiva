from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AccountsFlowTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.estudiante = self.User.objects.create_user(
            username='estudiante.test',
            password='Prueba12345!',
            rol='estudiante',
        )
        self.docente = self.User.objects.create_user(
            username='docente.test',
            password='Prueba12345!',
            rol='docente',
        )
        self.admin = self.User.objects.create_user(
            username='admin.test',
            password='Prueba12345!',
            rol='administrativo',
        )

    def test_login_redirecciona_por_rol(self):
        casos = [
            (self.estudiante.username, '/reservas/lista-laboratorios/'),
            (self.docente.username, '/reservas/mis-reservas/'),
            (self.admin.username, '/dashboard/admin/'),
        ]

        for username, esperado in casos:
            with self.subTest(username=username):
                response = self.client.post(
                    reverse('accounts:login'),
                    {'username': username, 'password': 'Prueba12345!'},
                )
                self.assertRedirects(
                    response,
                    esperado,
                    fetch_redirect_response=False,
                )
                self.client.get(reverse('accounts:logout'))

    def test_perfil_logout_y_cambio_contrasena(self):
        self.client.force_login(self.docente)
        self.assertEqual(self.client.get(reverse('accounts:perfil')).status_code, 200)

        response = self.client.post(
            reverse('accounts:cambiar_contrasena'),
            {
                'old_password': 'Prueba12345!',
                'new_password1': 'Prueba12345!!',
                'new_password2': 'Prueba12345!!',
            },
        )
        self.assertRedirects(response, reverse('accounts:perfil'))
        self.docente.refresh_from_db()
        self.assertTrue(self.docente.check_password('Prueba12345!!'))

        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))

    def test_bloqueo_por_cinco_intentos_fallidos(self):
        for _ in range(5):
            self.client.post(
                reverse('accounts:login'),
                {'username': self.estudiante.username, 'password': 'incorrecta'},
            )

        self.estudiante.refresh_from_db()
        self.assertEqual(self.estudiante.intentos_fallidos, 5)
        self.assertTrue(self.estudiante.esta_bloqueado())

    def test_solo_administrativo_lista_usuarios(self):
        self.client.force_login(self.estudiante)
        self.assertEqual(
            self.client.get(reverse('accounts:lista_usuarios')).status_code,
            403,
        )

        self.client.force_login(self.admin)
        self.assertEqual(
            self.client.get(reverse('accounts:lista_usuarios')).status_code,
            200,
        )

# Create your tests here.
