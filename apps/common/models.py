from datetime import datetime
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models
from .middleware import get_current_request


class AuditableModel(models.Model):
    usuario_creacion = models.CharField(
        'creado por',
        db_column='V_DESUSUREG',
        max_length=255,
        editable=False,
    )
    usuario_modificacion = models.CharField(
        'modificado por',
        max_length=255,
        db_column='V_DESUSUMOD',
        editable=False,
    )
    host_registro = models.CharField(
        'Host Registro',
        max_length=255,
        db_column='V_DESHOSTREG',
        editable=False,
    )
    ip_registro = models.CharField(
        'IP Registro',
        max_length=255,
        db_column='V_DESIPREG',
        editable=False,
    )

    class Meta:
        abstract = True


@receiver(pre_save, sender=AuditableModel)
def set_audit_fields(sender, instance, **kwargs):
    # Obtener el request actual usando el middleware
    request = get_current_request()

    if instance._state.adding:  # Si es una instancia nueva (creación)
        if request:
            instance.usuario_creacion = request.user.username
            instance.host_registro = request.get_host()
            instance.ip_registro = request.META.get('REMOTE_ADDR')
        else:
            # Si no hay request (posiblemente ejecución fuera de un request)
            instance.usuario_creacion = 'System'
            instance.host_registro = 'Unknown'
            instance.ip_registro = '10.10.1.0'
    else:  # Si es una actualización (modificación)
        if request:
            instance.usuario_modificacion = request.user.username
        else:
            instance.usuario_modificacion = 'System'


class TimeStampedModel(models.Model):
    fecha_creacion = models.DateTimeField(
        'fecha de creación',
        db_column='D_FECREGIS',
        auto_now_add=True,
        editable=False,
    )
    fecha_modificacion = models.DateTimeField(
        'fecha de modificación',
        db_column='D_FECMODIF',
        auto_now=True,
        editable=False,
    )

    class Meta:
        abstract = True

    def update_modified(self):
        self.fecha_modificacion = datetime.now()


class PermissionsMixin(models.Model):  # noqa: D205, D212, D400, D415
    groups = models.ManyToManyField(
        'seguridad.Group',
        verbose_name='groups',
        through='seguridad.UserGroup',
        blank=True,
        related_name='user_set',
        related_query_name='user',
    )

    class Meta:
        abstract = True

