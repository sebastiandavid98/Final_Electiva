import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout,
    update_session_auth_hash,
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone

from .decorators import requerir_permiso
from .forms import LoginForm, PerfilForm
from .models import Usuario

logger = logging.getLogger(__name__)


def _redirect_por_rol(user):
    if user.rol == Usuario.ESTUDIANTE:
        return redirect('reservas:lista_laboratorios')
    if user.rol == Usuario.DOCENTE:
        return redirect('reservas:mis_reservas')
    if user.rol == Usuario.ADMINISTRATIVO:
        return redirect('reservas:todas')
    return redirect(settings.LOGIN_REDIRECT_URL)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:perfil')

    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        ip = request.META.get('REMOTE_ADDR', '')
        cache_key = f'login_attempts_{ip}'
        attempts = cache.get(cache_key, 0)

        if attempts >= 10:
            messages.error(request, 'Demasiados intentos. Espera 5 minutos.')
            logger.warning('Demasiados intentos desde IP: %s', ip)
            return render(request, 'accounts/login.html', {'form': form})

        try:
            user_obj = Usuario.objects.get(username=username)
            if user_obj.esta_bloqueado():
                messages.error(
                    request,
                    f'Cuenta bloqueada hasta {user_obj.bloqueado_hasta:%H:%M}',
                )
                logger.warning(
                    'Intento de acceso a cuenta bloqueada: %s',
                    username,
                )
                return render(request, 'accounts/login.html', {'form': form})
        except Usuario.DoesNotExist:
            user_obj = None

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            user.resetear_intentos()
            user.fecha_ultimo_acceso = timezone.now()
            user.save(
                update_fields=[
                    'fecha_ultimo_acceso',
                    'intentos_fallidos',
                    'bloqueado_hasta',
                ]
            )
            cache.delete(cache_key)
            logger.info(
                'Login exitoso: %s - Rol: %s',
                username,
                user.get_rol_display(),
            )

            next_url = request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return _redirect_por_rol(user)

        cache.set(cache_key, attempts + 1, 300)
        if user_obj is not None:
            user_obj.registrar_intento_fallido()
            logger.warning('Login fallido para usuario existente: %s', username)
        else:
            logger.warning('Login fallido - usuario inexistente: %s', username)
        messages.error(request, 'Usuario o contrasena incorrectos')

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logger.info('Logout: %s', request.user.username)
    logout(request)
    messages.success(request, 'Sesion cerrada correctamente')
    return redirect('accounts:login')


@login_required
def perfil_view(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('accounts:perfil')
    else:
        form = PerfilForm(instance=request.user)

    return render(
        request,
        'accounts/perfil.html',
        {'form': form, 'usuario': request.user},
    )


@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contrasena actualizada correctamente')
            logger.info('Cambio de contrasena: %s', request.user.username)
            return redirect('accounts:perfil')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/cambiar_contrasena.html', {'form': form})


@login_required
@requerir_permiso('puede_gestionar_usuarios')
def lista_usuarios(request):
    usuarios = Usuario.objects.all().order_by('rol', 'username')
    return render(request, 'accounts/lista_usuarios.html', {'usuarios': usuarios})

# Create your views here.
