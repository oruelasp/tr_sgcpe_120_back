from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.db import models
from apps.common.constants import (
    CHOICES_ESTADO_ACTIVIDAD, CHOICES_ESTADO_PROGRAMACION,
    ESTADO_ACTIVIDAD_BORRADOR, ESTADO_PROGRAMACION_NUEVO, NUEVO, CHOICES_ASISTENCIA,
    ESTADO_ACTIVIDAD_ENVIADO, ESTADO_ACTIVIDAD_OBSERVADO, ESTADO_ACTIVIDAD_FIRMADO,
    CHOICES_ESTADO_ROTACION, ESTADO_ROTACION_PENDIENTE, ESTADO_ACTIVIDAD_ATRASADO,
    ESTADO_ACTIVIDAD_ENCURSO, TIPO_DIAS, TIPO_CALENDARIO, ESTADO_PENDIENTE_PAPELETA,
    CHOICES_ESTADO_PAPELETA, FALTA, ASISTIDO, TARDANZA, TIPO_CONCEPTO
)
from apps.common import constants
from apps.common.models import TimeStampedModel, AuditableModel
# from apps.seguridad.models import User
from apps.modelsext.models import Departamento, Provincia, Distrito


class Sede(TimeStampedModel, AuditableModel):
    pk_sede = models.IntegerField(
        db_column='PK_IDSEDE',
        primary_key=True
    )
    codigo_zona = models.CharField(
        max_length=2,
        db_column='V_CODZON',
        null=True,
        blank=True
    )
    codigo_region = models.CharField(
        max_length=2,
        db_column='V_CODREG',
        null=True,
        blank=True
    )
    codigo_sede = models.CharField(
        max_length=2,
        db_column='V_CODSEDE',
        null=True,
        blank=True
    )
    descripcion_sede = models.CharField(
        max_length=200,
        db_column='V_DESSEDE',
        null=True,
        blank=True
    )
    flag = models.CharField(
        max_length=1,
        db_column='V_FLGACT',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.descripcion_sede

    class Meta:
        managed = False
        verbose_name = 'sede'
        verbose_name_plural = 'sedes'
        db_table = constants.get_tabla_tbx('SEDE')


class Solicitud(AuditableModel, TimeStampedModel):
    pk_solicitud = models.AutoField(primary_key=True, db_column='N_IDSOLICITUD')
    fecha_solicitud = models.DateField(db_column='D_FECSOLICITUD')
    codigo_solicitud = models.CharField('Código de Solicitud', db_column='V_CODSOLICITUD', max_length=100, blank=True, null=True)
    estado = models.CharField('Flag de Estado', db_column='C_FLGESTADO', max_length=1)
    motivo = models.ForeignKey('Motivo', on_delete=models.SET_NULL, null=True, db_column='N_IDMOTIVO')
    descripcion_motivo = models.CharField(max_length=500, db_column='V_DESMOTIVO')
    url_primer_adjunto = models.CharField('URL del Primer Adjunto', db_column='V_URLPRIMERADJ', max_length=500, blank=True, null=True)
    tipo_solicitante = models.CharField('Tipo de Solicitante', db_column='C_CODTIPOSOLI', max_length=2, blank=True, null=True)
    tipo_documento_solicitante = models.CharField('Tipo de Documento de Solicitante', db_column='C_CODDOCSOLI', max_length=2, blank=True, null=True)
    numero_documento_solicitante = models.CharField('Número de Documento de Solicitante', db_column='V_NUMDOCSOLI', max_length=20, blank=True, null=True)
    nombre_solicitante = models.CharField('Nombre del Solicitante', db_column='V_DESNOMSOLI', max_length=255, blank=True, null=True)
    apellido_paterno_solicitante = models.CharField('Apellido Paterno del Solicitante', db_column='V_DESAPPATSOLI', max_length=30, blank=True, null=True)
    apellido_materno_solicitante = models.CharField('Apellido Materno del Solicitante', db_column='V_DESAPMATSOLI', max_length=30, blank=True, null=True)
    usuario = models.ForeignKey(
        'seguridad.User', db_column='N_IDUSUARIO', related_name='usuario_solicitudes', blank=True, null=True, on_delete=models.CASCADE
    )
    observacion_autenticacion = models.CharField(
        'Observación de autenticación', db_column='V_DESOBSERVACION', max_length=400, blank=True, null=True)

    class Meta:
        managed = False
        db_table = constants.get_tabla_mvc('SOLICITUD')
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'

    def __str__(self):
        return str(self.pk_solicitud)


class Motivo(AuditableModel, TimeStampedModel):
    pk_motivo = models.AutoField(primary_key=True, db_column='N_IDMOTIVO')  # Actualizado
    codigo_motivo = models.CharField(max_length=3, db_column='V_CODMOTIVO')
    descripcion_motivo = models.CharField(max_length=500, db_column='V_DESMOTIVO')
    flag = models.CharField(max_length=1, db_column='C_FLGESTADO')  # Actualizado

    class Meta:
        managed = False
        db_table = constants.get_tabla_tbx('MOTIVO')
        verbose_name = 'Motivo'
        verbose_name_plural = 'Motivos'

    def __str__(self):
        return str(self.pk_motivo)


class SolicitudDetalle(AuditableModel, TimeStampedModel):
    pk_solicitud_detalle = models.AutoField(primary_key=True, db_column='PK_IDSOLIDET')
    solicitud = models.ForeignKey(Solicitud, on_delete=models.CASCADE, db_column='N_IDSOLICITUD')
    motivo = models.ForeignKey(Motivo, on_delete=models.SET_NULL, null=True, db_column='N_IDMOTIVO')
    descripcion = models.CharField(max_length=500, db_column='V_DESMOTIVO')
    flag = models.CharField(max_length=1, db_column='V_FLGESTADO')

    class Meta:
        managed = False
        db_table = constants.get_tabla_mvd('SOLICITUD')
        verbose_name = 'Solicitud-Detalle'
        verbose_name_plural = 'Solicitudes-detalle'

    def __str__(self):
        return str(self.pk_solicitud_detalle)


class Plantilla(AuditableModel, TimeStampedModel):
    pk_plantilla = models.AutoField(primary_key=True, db_column='PK_IDPLANTILLA')
    descripcion = models.TextField(db_column='CL_DESPLANTILLA')
    encabezado = models.CharField(
        max_length=90000, db_column='CL_DESENCABEZADO')
    pie_pagina = models.CharField(
        max_length=90000, db_column='CL_DESPIEPAGINA')
    estado = models.CharField(max_length=1, db_column='V_FLGESTADO')
    codigo = models.CharField(max_length=2, db_column='V_CODPLANTILLA')

    class Meta:
        managed = False
        db_table = constants.get_tabla_tbx('PLANTILLA')
        verbose_name = 'Plantilla'
        verbose_name_plural = 'Plantillas'


class Audiencia(AuditableModel, TimeStampedModel):
    pk_audiencia = models.AutoField(primary_key=True, db_column='PK_IDAUDIENCIA')
    descripcion_audiencia = models.CharField('Descripción de la audiencia', db_column='V_DESAUDIENCIA', max_length=255, blank=True, null=True)
    estado = models.CharField('Estado', db_column='V_FLGESTADO', max_length=1, blank=True, null=True)
    codigo_audiencia = models.CharField('Código de audiencia', db_column='V_CODAUDIENCIA', max_length=30, blank=True, null=True)
    codigo_inicial = models.CharField(
        'Código inicial', db_column='V_CODINICIAL', max_length=30, blank=True, null=True)
    audiencia = models.ForeignKey(
        'programacion.Audiencia',
        db_column='N_IDAUDIENCIA',
        related_name='audiencia_audiencias',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    solicitud = models.ForeignKey(
        'programacion.Solicitud',
        db_column='N_IDSOLICITUD',
        related_name='solicitud_audiencias',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    responsable = models.ForeignKey(
        'seguridad.User',
        db_column='N_IDRESPONSABLE',
        related_name='responsable_audiencias',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    fecha_inicio = models.DateTimeField('Fecha y hora de inicio', db_column='T_FECINICIO', blank=True, null=True)
    numero_duracion = models.IntegerField('Número de duración', db_column='N_NUMDURACION', blank=True, null=True)
    fecha_fin = models.DateTimeField('Fecha y hora de finalización', db_column='T_FECFIN', blank=True, null=True)
    url_solicitante_adjunto = models.CharField('URL del Solicitante Adjunto', db_column='V_URLSOLIADJ', max_length=500,
                                          blank=True, null=True)
    url_invitado_adjunto = models.CharField('URL del Invitado Adjunto', db_column='V_URLINVIADJ', max_length=500,
                                           blank=True, null=True)
    asistencia_total = models.CharField('Asistencia Total', db_column='V_FLGASISTOTAL', max_length=1, blank=True, null=True)
    asistencia_unitaria = models.CharField('Asistencia unitaria', db_column='V_FLGASISUNIT', max_length=1, blank=True, null=True)
    asistencia_entidad = models.CharField('Asistencia entidad', db_column='V_FLGASISENT', max_length=1, blank=True,
                                           null=True)
    modalidad = models.CharField('Modalidad', db_column='V_FLGMODALIDAD', max_length=1, blank=True, null=True)
    envio_invitacion = models.CharField('Envío de invitación', db_column='V_FLGENVIO', max_length=1, blank=True, null=True)
    resultado = models.CharField(
        'Resultado de audiencia', db_column='V_FLGRESULTADO', max_length=1, blank=True, null=True)
    justificacion_solicitante = models.CharField(
        'Justificacion solicitante', db_column='V_FLGJUSTSOLI', max_length=1, blank=True, null=True)
    justificacion_invitado = models.CharField(
        'Justificacion invitado', db_column='V_FLGJUSTINVI', max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = constants.get_tabla_mvc('AUDIENCIA')
        verbose_name = 'Audiencia'
        verbose_name_plural = 'Audiencias'

    def __str__(self):
        return 'PK: {}'.format(self.pk_audiencia)


class SolicitudHistorico(AuditableModel, TimeStampedModel):
    pk_solicitud_hist = models.AutoField(
        db_column='PK_IDSOLICITUDHIST', primary_key=True
    )
    estado = models.CharField(db_column='V_FLGESTADO', max_length=1)
    usuario = models.ForeignKey(
        'seguridad.User', db_column='N_IDUSUARIO', blank=True, null=True, on_delete=models.CASCADE
    )
    fecha_registro = models.DateTimeField(db_column='T_FECREGISTRO', null=True)
    observacion = models.CharField(
        db_column='V_DESOBSERVACION', max_length=4000, null=True
    )
    solicitud = models.ForeignKey(
        Solicitud,
        db_column='N_IDSOLICITUD',
        related_name='historicos',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    url_anexo = models.CharField(
        db_column='V_URLANEXO', max_length=300, blank=True, null=True
    )
    fecha_vencimiento = models.DateTimeField(db_column='T_FECVENCIMIENTO', null=True)
    acuse_recibo = models.CharField(
        db_column='V_FLGACUSERECIBO', max_length=1, blank=True, null=True
    )
    url_sustento = models.CharField(
        db_column='V_URLSUSTENTO', max_length=300, blank=True, null=True
    )

    def __str__(self):
        return f'PK{self.pk_solicitud_hist}-EST{self.estado}'

    class Meta:
        managed = False
        db_table = constants.get_tabla_mvc('SOLICITUD_HIST')
        verbose_name = 'Solicitud Histórico'
        verbose_name_plural = 'Solicitud Históricos'


class AudienciaHistorico(AuditableModel, TimeStampedModel):
    pk_audiencia_hist = models.AutoField(
        db_column='PK_IDAUDIENCIAHIST', primary_key=True
    )
    estado = models.CharField(db_column='V_FLGESTADO', max_length=1)
    usuario = models.ForeignKey(
        'seguridad.User', db_column='N_IDUSUARIO', blank=True, null=True, on_delete=models.CASCADE
    )
    fecha_registro = models.DateTimeField(db_column='T_FECREGISTRO', null=True)
    observacion = models.CharField(
        db_column='V_DESOBSERVACION', max_length=4000, null=True, blank=True
    )
    comentario = models.CharField(
        db_column='V_DESCOMENTARIO', max_length=500, null=True, blank=True
    )
    observacion_solicitante = models.CharField(
        db_column='V_DESOBSSOLI', max_length=800, null=True, blank=True
    )
    observacion_invitado = models.CharField(
        db_column='V_DESOBSINVI', max_length=800, null=True, blank=True
    )
    audiencia = models.ForeignKey(
        Audiencia,
        db_column='N_IDAUDIENCIA',
        related_name='historicos',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    url_anexo = models.CharField(
        db_column='V_URLANEXO', max_length=300, blank=True, null=True
    )
    fecha_vencimiento = models.DateTimeField(db_column='T_FECVENCIMIENTO', null=True)
    url_sustento = models.CharField(
        db_column='V_URLSUSTENTO', max_length=300, blank=True, null=True
    )
    resultado = models.CharField(
        'Resultado de audiencia', db_column='V_FLGRESULTADO', max_length=1, blank=True, null=True)

    def __str__(self):
        return f'PK{self.pk_audiencia_hist}-EST{self.estado}'

    class Meta:
        managed = False
        db_table = constants.get_tabla_mvc('AUDIENCIA_HIST')
        verbose_name = 'Audiencia Histórico'
        verbose_name_plural = 'Audiencia Históricos'
