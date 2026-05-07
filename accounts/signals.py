import logging

from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate, post_save, pre_save
from django.dispatch import receiver

from .models import Usuario
from .permissions import GestorPermisos

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def configurar_permisos_y_grupos(sender, **kwargs):
    if sender.name != 'accounts':
        return
    GestorPermisos.configurar_grupos_por_rol()
    logger.info('Permisos y grupos de accounts configurados')


@receiver(post_save, sender=Usuario)
def asignar_grupo_segun_rol(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        grupo = Group.objects.get(name=instance.rol)
        instance.groups.add(grupo)
        logger.info(
            'Usuario %s asignado al grupo %s',
            instance.username,
            instance.rol,
        )
    except Group.DoesNotExist:
        logger.error('Grupo %s no existe', instance.rol)


@receiver(pre_save, sender=Usuario)
def actualizar_grupo_si_cambia_rol(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = Usuario.objects.get(pk=instance.pk)
    except Usuario.DoesNotExist:
        return

    if old_instance.rol == instance.rol:
        return

    try:
        old_group = Group.objects.get(name=old_instance.rol)
        instance.groups.remove(old_group)
    except Group.DoesNotExist:
        pass

    try:
        new_group = Group.objects.get(name=instance.rol)
        instance.groups.add(new_group)
        logger.info('Usuario %s cambio de rol', instance.username)
    except Group.DoesNotExist:
        logger.error('Grupo %s no existe', instance.rol)
