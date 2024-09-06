"""
Serializadores para API aplicación de Programacion.

Copyright (C) 2022 PRODUCE.

Authors:
    Omar Ruelas Principe <ddf_temp57@produce.gob.pe>
"""
import os
import uuid
from django.core.files.storage import default_storage
from rest_framework import serializers
from unidecode import unidecode
from django.conf import settings

from apps.modelsext.models import SiDependencia as HDependencia, SiCargo, TPersonal, SiTrabajador, SiRegional
from apps.common import constants
from apps.common.functions import ServiciosInternos as si, pdf_to_base64, ServiciosExternos as se
from apps.seguridad.models import User
from apps.programacion.models import (Sede, Solicitud, SolicitudDetalle, Motivo, Plantilla, Audiencia,
                                      AudienciaHistorico)


class SedeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sede
        exclude = ('usuario_creacion', 'usuario_modificacion',
                   'host_registro', 'ip_registro', 'fecha_creacion', 'fecha_modificacion')


class MotivoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Motivo
        exclude = ('usuario_creacion', 'usuario_modificacion',
                   'host_registro', 'ip_registro', 'fecha_creacion', 'fecha_modificacion')


class SolicitudDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudDetalle
        fields = '__all__'

class IngresoSerializer(serializers.Serializer):
    concepto = serializers.CharField(max_length=100)
    monto_de_pago = serializers.FloatField()


class DescuentoSerializer(serializers.Serializer):
    concepto = serializers.CharField(max_length=100)
    monto_de_pago = serializers.FloatField()


class AportacionTrabajadorSerializer(serializers.Serializer):
    concepto = serializers.CharField(max_length=100)
    monto_de_pago = serializers.FloatField()


class AportacionEmpleadorSerializer(serializers.Serializer):
    concepto = serializers.CharField(max_length=100)
    monto_de_pago = serializers.FloatField()


class OtrosConceptosSerializer(serializers.Serializer):
    concepto = serializers.CharField(max_length=100)
    monto_de_pago = serializers.CharField(max_length=100)


class RegimenPublicoSerializer(serializers.Serializer):
    concepto = serializers.CharField(max_length=100)
    monto_de_pago = serializers.CharField(max_length=100)

class QuintaCategoriaSerializer(serializers.Serializer):
    V_CORPROC = serializers.CharField(max_length=255)
    V_DESRAZONS = serializers.CharField(max_length=255)
    V_APEPATER = serializers.CharField(max_length=255)
    V_APEMATER = serializers.CharField(max_length=255)
    V_NOMBRES = serializers.CharField(max_length=255)
    V_NUMPERIOD = serializers.CharField(max_length=255)
    V_NUMDOCIDE = serializers.CharField(max_length=255)
    V_NUMDOCAPO = serializers.CharField(max_length=255)
    V_NUMSERIE = serializers.CharField(max_length=255)
    V_NUMRECIBO = serializers.CharField(max_length=255)
    TIPO_COMP = serializers.CharField(max_length=255)
    D_FECEMSION = serializers.DateField()
    D_FECPAGO = serializers.DateField()
    PERIODO_LAB = serializers.CharField(max_length=255)
    TIPO_CONTRATO = serializers.CharField(max_length=255)
    CATEGOCUPAC = serializers.CharField(max_length=255)
    SITUACESPEC = serializers.CharField(max_length=255)
    OCUPACION = serializers.CharField(max_length=255)
class RazonSocialSerializer(serializers.Serializer):
    v_apepater = serializers.CharField()
    v_apemater = serializers.CharField()
    v_nombres = serializers.CharField()
    v_numdocide = serializers.CharField()
    v_desrazons = serializers.CharField()

    class IngresoSerializer(serializers.Serializer):
        concepto = serializers.CharField(max_length=100)
        monto_de_pago = serializers.FloatField()

    class DescuentoSerializer(serializers.Serializer):
        concepto = serializers.CharField(max_length=100)
        monto_de_pago = serializers.FloatField()

    class AportacionTrabajadorSerializer(serializers.Serializer):
        concepto = serializers.CharField(max_length=100)
        monto_de_pago = serializers.FloatField()

    class AportacionEmpleadorSerializer(serializers.Serializer):
        concepto = serializers.CharField(max_length=100)
        monto_de_pago = serializers.FloatField()

    class OtrosConceptosSerializer(serializers.Serializer):
        concepto = serializers.CharField(max_length=100)
        monto_de_pago = serializers.CharField(max_length=100)

    class RegimenPublicoSerializer(serializers.Serializer):
        concepto = serializers.CharField(max_length=100)
        monto_de_pago = serializers.CharField(max_length=100)

    class QuintaCategoriaSerializer(serializers.Serializer):
        V_CORPROC = serializers.CharField(max_length=255)
        V_DESRAZONS = serializers.CharField(max_length=255)
        V_APEPATER = serializers.CharField(max_length=255)
        V_APEMATER = serializers.CharField(max_length=255)
        V_NOMBRES = serializers.CharField(max_length=255)
        V_NUMPERIOD = serializers.CharField(max_length=255)
        V_NUMDOCIDE = serializers.CharField(max_length=255)
        V_NUMDOCAPO = serializers.CharField(max_length=255)
        V_NUMSERIE = serializers.CharField(max_length=255)
        V_NUMRECIBO = serializers.CharField(max_length=255)
        TIPO_COMP = serializers.CharField(max_length=255)
        D_FECEMSION = serializers.DateField()
        D_FECPAGO = serializers.DateField()
        PERIODO_LAB = serializers.CharField(max_length=255)
        TIPO_CONTRATO = serializers.CharField(max_length=255)
        CATEGOCUPAC = serializers.CharField(max_length=255)
        SITUACESPEC = serializers.CharField(max_length=255)
        OCUPACION = serializers.CharField(max_length=255)

    class RazonSocialSerializer(serializers.Serializer):
        v_apepater = serializers.CharField()
        v_apemater = serializers.CharField()
        v_nombres = serializers.CharField()
        v_numdocide = serializers.CharField()
        v_desrazons = serializers.CharField()

    class PlanillaSerializer(serializers.Serializer):
        tipo_categoria = serializers.CharField(max_length=100)
        fecha_de_pago = serializers.CharField(max_length=100, allow_blank=True)
        fecha_de_emision = serializers.CharField(max_length=100, allow_blank=True)
        tipo_de_contrato_o_comprobante = serializers.CharField(max_length=100)
        numero_de_contrato_o_comprobante = serializers.CharField(max_length=100, allow_blank=True)
        ocupacion = serializers.CharField(max_length=100)
        categoria_ocupacional = serializers.CharField(max_length=100)
        situacion_especial = serializers.CharField(max_length=100)
        periodo_tributario = serializers.CharField(max_length=100)
        periodo_inicio = serializers.CharField(max_length=100)
        periodo_fin = serializers.CharField(max_length=100)
        razon_social = serializers.CharField(max_length=100)
        ruc = serializers.CharField(max_length=100)
        ingreso = IngresoSerializer(many=True)
        descuentos = DescuentoSerializer(many=True)
        aportaciones_trabajador = AportacionTrabajadorSerializer(many=True)
        aportaciones_empleador = AportacionEmpleadorSerializer(many=True)
        otros_conceptos = OtrosConceptosSerializer(many=True)
        regimen_publico = RegimenPublicoSerializer(many=True)


class PlanillaSerializer(serializers.Serializer):
    tipo_categoria = serializers.CharField(max_length=100)
    fecha_de_pago = serializers.CharField(max_length=100, allow_blank=True)
    fecha_de_emision = serializers.CharField(max_length=100, allow_blank=True)
    tipo_de_contrato_o_comprobante = serializers.CharField(max_length=100)
    numero_de_contrato_o_comprobante = serializers.CharField(max_length=100, allow_blank=True)
    ocupacion = serializers.CharField(max_length=100)
    categoria_ocupacional = serializers.CharField(max_length=100)
    situacion_especial = serializers.CharField(max_length=100)
    periodo_tributario = serializers.CharField(max_length=100)
    periodo_inicio = serializers.CharField(max_length=100)
    periodo_fin = serializers.CharField(max_length=100)
    razon_social = serializers.CharField(max_length=100)
    ruc = serializers.CharField(max_length=100)
    ingreso = IngresoSerializer(many=True)
    descuentos = DescuentoSerializer(many=True)
    aportaciones_trabajador = AportacionTrabajadorSerializer(many=True)
    aportaciones_empleador = AportacionEmpleadorSerializer(many=True)
    otros_conceptos = OtrosConceptosSerializer(many=True)
    regimen_publico = RegimenPublicoSerializer(many=True)


class SolicitudSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='usuario.username', read_only=True)
    datos_solicitante = serializers.SerializerMethodField('get_datos_solicitante')
    datos_usuario = serializers.SerializerMethodField('get_datos_usuario')
    codigo_region = serializers.CharField(source='usuario.codigo_region', read_only=True)
    codigo_institucion = serializers.CharField(source='usuario.codigo_institucion', read_only=True)
    nombre_region = serializers.SerializerMethodField('get_nombre_region')
    nombre_cargo = serializers.SerializerMethodField('get_nombre_cargo')

    class Meta:
        model = Solicitud
        fields = [
            'username',
            'datos_usuario',
            'codigo_region',
            'nombre_region',
            'nombre_cargo',
            'fecha_solicitud',
            'numero_documento_solicitante',
            'nombre_solicitante',
            'apellido_paterno_solicitante',
            'apellido_materno_solicitante',
            'descripcion_motivo',
            'ip_modificacion'
        ]

    def get_datos_usuario(self, obj):
        datos = '-'
        if obj.usuario_id:
            personal = TPersonal.objects.filter(codigo_personal=obj.usuario_id)
            if not personal.exists():
                return datos
            personal = personal.first()
            datos = '{} {}, {}'.format(personal.apellido_paterno, personal.apellido_materno, personal.nombres)
        return datos

    def get_nombre_cargo(self, obj):
        datos = '-'
        if obj.usuario_id:
            cargo = SiCargo.objects.filter(pk=obj.usuario.codigo_cargo)
            if not cargo.exists():
                return datos
            datos = cargo.first().desc_cargo
        return datos

    def get_nombre_region(self, obj):
        datos = '-'
        if obj.usuario_id:
            region = SiRegional.objects.filter(pk=obj.usuario.codigo_region)
            if not region.exists():
                return datos
            datos = region.first().nombre_region
        return datos

    def get_datos_solicitante(self, obj):
        if obj.apellido_paterno_solicitante and obj.apellido_materno_solicitante and obj.nombre_solicitante:
            datos = '{} {}, {}'.format(
                obj.apellido_paterno_solicitante, obj.apellido_materno_solicitante, obj.nombre_solicitante)
        elif obj.nombre_solicitante:
            datos = '{}'.format(obj.nombre_solicitante)
        else:
            datos = 'N/A'
        return datos


class SolicitudListaSerializer(SolicitudSerializer):
    class Meta(SolicitudSerializer.Meta):
        exclude = []
        fields = (
            'pk_solicitud',
            'codigo_solicitud',
            'numero_documento_solicitante',
            'datos_solicitante',
            'datos_invitado',
            'datos_responsable',
            'nombre_sede',
            'datos_responsable',
            'responsable_id',
            'estado',
            'nombre_estado',
            'numero_audiencias',
            'fecha_inicio_audiencia',
            'audiencia_id',
            'envio_invitacion',
            'nombre_envio_invitacion',
            'url_invitado_adjunto',
            'codigo_inicial',
            'audiencia_first_id',
            'asistencia_total_first'
        )


class SolicitudEditarSerializer(serializers.ModelSerializer):
    fecha_nacimiento_solicitante = serializers.DateField(input_formats=['%Y-%m-%d', '%d/%m/%Y'], required=False)
    fecha_solicitud = serializers.DateField(input_formats=['%Y-%m-%d', '%d/%m/%Y'], required=False)

    class Meta:
        model = Solicitud
        exclude = (
            'pk_solicitud',
            'departamento_solicitante',
            'provincia_solicitante',
            'distrito_solicitante',
            'departamento_invitado',
            'provincia_invitado',
            'distrito_invitado',
            'usuario',
            'sede',
            'responsable'
        )


class SolicitudReporteSerializer(SolicitudSerializer):
    class Meta(SolicitudSerializer.Meta):
        exclude = []
        fields = (
            'codigo_solicitud',
            'tipo_documento_solicitante_str',
            'numero_documento_solicitante',
            'datos_solicitante',
            'tipo_documento_invitado_str',
            'numero_documento_invitado',
            'datos_invitado',
            'usuario_id',
            'datos_usuario',
            'responsable_id',
            'datos_responsable',
            'nombre_sede',
            'motivos',
            'nombre_estado',
        )


class ArchivoSerializer(serializers.Serializer):
    archivo = serializers.FileField()

    def save(self):
        archivo = self.validated_data['archivo']
        codigo = str(uuid.uuid4())
        subcarpeta = os.path.join('solicitud_archivos', codigo)
        nombre_archivo = unidecode(archivo.name).replace(' ', '-')
        ruta_guardado = default_storage.save(
            os.path.join(subcarpeta, nombre_archivo), archivo
        )
        return default_storage.url(ruta_guardado)


class InvitacionSerializer(serializers.Serializer):
    archivo = serializers.FileField()

    def save(self):
        archivo = self.validated_data['archivo']
        codigo = str(uuid.uuid4())
        subcarpeta = os.path.join('audiencia_invitaciones', codigo)
        nombre_archivo = unidecode(archivo.name).replace(' ', '-')
        ruta_guardado = default_storage.save(
            os.path.join(subcarpeta, nombre_archivo), archivo
        )
        return default_storage.url(ruta_guardado)


class PlantillaSerializer(serializers.ModelSerializer):
    estado = serializers.CharField(required=False)
    descripcion = serializers.CharField(required=False)
    codigo = serializers.CharField(required=False)
    nombre_codigo = serializers.SerializerMethodField()

    class Meta:
        model = Plantilla
        exclude = ('usuario_creacion', 'usuario_modificacion',
                   'host_registro', 'ip_registro', 'fecha_creacion', 'fecha_modificacion')

    def get_nombre_codigo(self, obj):
        nombre = '-'
        if obj.codigo:
            nombre = constants.DICT_CODIGO_PLANTILLA.get(obj.codigo, '-')
        return nombre


class PlantillaListaSerializer(PlantillaSerializer):
    class Meta(PlantillaSerializer.Meta):
        exclude = []
        fields = (
            'pk_plantilla',
            'codigo',
            'nombre_codigo',
            'estado',
        )


class AudienciaSerializer(serializers.ModelSerializer):
    solicitud_id = serializers.IntegerField(required=False)
    audiencia_id = serializers.IntegerField(required=False)
    responsable_id = serializers.IntegerField(required=False)
    numero_duracion = serializers.IntegerField(required=False)
    fecha_fin = serializers.DateTimeField(input_formats=['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'],
        required=False, format='%d/%m/%Y %H:%M:%S')
    fecha_inicio = serializers.DateTimeField(format='%d/%m/%Y %H:%M:%S', input_formats=['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'])
    nombre_estado_solicitud = serializers.SerializerMethodField('get_nombre_estado_solicitud')
    nombre_estado = serializers.SerializerMethodField('get_nombre_estado')
    nombre_sede = serializers.SerializerMethodField('get_nombre_sede')
    datos_responsable = serializers.SerializerMethodField('get_datos_responsable')
    datos_usuario = serializers.SerializerMethodField('get_datos_usuario')
    usuario_id = serializers.SerializerMethodField()
    numero_documento_solicitante = serializers.SerializerMethodField('get_numero_documento_solicitante')
    datos_solicitante = serializers.SerializerMethodField('get_datos_solicitante')
    email_solicitante = serializers.SerializerMethodField('get_email_solicitante')
    numero_documento_invitado = serializers.SerializerMethodField('get_numero_documento_invitado')
    datos_invitado = serializers.SerializerMethodField('get_datos_invitado')
    email_invitado = serializers.SerializerMethodField('get_email_invitado')
    codigo_solicitud = serializers.SerializerMethodField('get_codigo_solicitud')
    pk_solicitud = serializers.SerializerMethodField('get_pk_solicitud')
    nombre_asistencia = serializers.SerializerMethodField('get_nombre_asistencia')
    nombre_envio_invitacion = serializers.SerializerMethodField('get_nombre_envio_invitacion')
    url_solicitante_adjunto_base64 = serializers.SerializerMethodField('get_url_solicitante_adjunto_base64')
    url_invitado_adjunto_base64 = serializers.SerializerMethodField('get_url_invitado_adjunto_base64')
    url_sustento_base64 = serializers.SerializerMethodField('get_url_sustento_base64')
    url_sustento = serializers.SerializerMethodField('get_url_sustento')
    url_primer_adjunto_base64 = serializers.SerializerMethodField('get_url_primer_adjunto_base64')
    historico = serializers.SerializerMethodField('get_historico')
    audiencia_child_id = serializers.SerializerMethodField('get_audiencia_child_id')
    audiencia_child_asistencia_total = serializers.SerializerMethodField()
    audiencia_child_asistencia_unitaria = serializers.SerializerMethodField()
    audiencia_child_asistencia_entidad = serializers.SerializerMethodField()
    fecha_vencimiento = serializers.SerializerMethodField('get_fecha_vencimiento')
    nombre_resultado = serializers.SerializerMethodField('get_nombre_resultado')
    nombre_justificacion = serializers.SerializerMethodField('get_nombre_justificacion')
    nombre_modalidad = serializers.SerializerMethodField('get_nombre_modalidad')
    tipo_documento_solicitante_str = serializers.SerializerMethodField()
    tipo_documento_invitado_str = serializers.SerializerMethodField()
    motivos = serializers.SerializerMethodField()

    class Meta:
        model = Audiencia
        exclude = ['audiencia', 'responsable']

    def get_motivos(self, obj):
        solicitud_motivos = SolicitudDetalle.objects.filter(solicitud__pk=obj.solicitud.pk)
        response_list = []
        for sol_motivo in solicitud_motivos:
            if sol_motivo.motivo.codigo_motivo == constants.CODIGO_MOTIVO_OTROS:
                descripcion_motivo = sol_motivo.descripcion
            else:
                descripcion_motivo = sol_motivo.motivo.descripcion_motivo
            response_list.append(descripcion_motivo)
        resultado = ','.join(response_list)
        return resultado

    def get_tipo_documento_str(self, tipo_documento):
        return constants.TIPO_DOCUMENTO.get(tipo_documento)

    def get_tipo_documento_solicitante_str(self, obj):
        nombre = ''
        if obj.solicitud.tipo_documento_solicitante:
            nombre = self.get_tipo_documento_str(obj.solicitud.tipo_documento_solicitante)
        return nombre

    def get_tipo_documento_invitado_str(self, obj):
        nombre = ''
        if obj.solicitud.tipo_documento_invitado:
            nombre = self.get_tipo_documento_str(obj.solicitud.tipo_documento_invitado)
        return nombre

    def get_url_invitado_adjunto_base64(self, obj):
        base64_anexo = ''
        if self._context.get('request').query_params.get('consolidado') != constants.SI_CHAR_BINARY:
            base64_anexo = pdf_to_base64(obj.url_invitado_adjunto)
        return base64_anexo

    def get_fecha_vencimiento(self, obj):
        sol_hist = AudienciaHistorico.objects.filter(audiencia=obj)
        if not sol_hist.exists():
            return None
        ultimo_historico = (
            sol_hist.filter(estado=obj.estado).order_by('-fecha_registro').first()
        )
        if not ultimo_historico:
            return None
        if ultimo_historico.fecha_vencimiento:
            return ultimo_historico.fecha_vencimiento.strftime('%d/%m/%Y %H:%M:%S')
        return None

    def get_url_solicitante_adjunto_base64(self, obj):
        base64_anexo = pdf_to_base64(obj.url_solicitante_adjunto)
        return base64_anexo

    def get_url_sustento(self, obj):
        url_sustento = ''
        historicos = AudienciaHistorico.objects.filter(
            audiencia=obj, url_sustento__isnull=False).order_by('-fecha_registro')
        if historicos.exists():
            url_sustento = historicos.first().url_sustento
        return url_sustento

    def get_url_sustento_base64(self, obj):
        base64_sustento = ''
        historicos = AudienciaHistorico.objects.filter(
            audiencia=obj, url_sustento__isnull=False).order_by('-fecha_registro')
        if historicos.exists():
            url_sustento = historicos.first().url_sustento
            base64_sustento = pdf_to_base64(url_sustento)
        return base64_sustento

    def get_url_primer_adjunto_base64(self, obj):
        return pdf_to_base64(obj.solicitud.url_primer_adjunto)

    def get_audiencia_child_id(self, obj):
        audiencias = Audiencia.objects.filter(audiencia=obj).exclude(estado=constants.ESTADO_AUDIENCIA_ANULADA)
        audiencia_child_id = None
        if audiencias.exists():
            audiencia_child_id = audiencias.first().pk_audiencia
        return audiencia_child_id

    def get_audiencia_child_asistencia_total(self, obj):
        audiencias = Audiencia.objects.filter(audiencia=obj)
        dato = ''
        if audiencias.exists():
            dato = audiencias.first().asistencia_total
        return dato

    def get_audiencia_child_asistencia_unitaria(self, obj):
        audiencias = Audiencia.objects.filter(audiencia=obj)
        dato = ''
        if audiencias.exists():
            dato = audiencias.first().asistencia_unitaria
        return dato

    def get_audiencia_child_asistencia_entidad(self, obj):
        audiencias = Audiencia.objects.filter(audiencia=obj)
        dato = ''
        if audiencias.exists():
            dato = audiencias.first().asistencia_entidad
        return dato

    def get_nombre_envio_invitacion(self, obj):
        if obj.envio_invitacion == '1':
            nombre_envio_invitacion = 'Notificado por correo electrónico'
        elif obj.envio_invitacion == '0':
            nombre_envio_invitacion = 'No se pudo notificar por correo electrónico'
        else:
            nombre_envio_invitacion = 'Notificado de manera física'
        return nombre_envio_invitacion

    def get_codigo_solicitud(self, obj):
        codigo_solicitud = '-'
        if obj.solicitud:
            codigo_solicitud = obj.solicitud.codigo_solicitud
        return codigo_solicitud

    def get_pk_solicitud(self, obj):
        pk_solicitud = '-'
        if obj.solicitud:
            pk_solicitud = obj.solicitud.pk_solicitud
        return pk_solicitud

    def get_numero_documento_invitado(self, obj):
        if obj.solicitud.numero_documento_invitado:
            datos = obj.solicitud.numero_documento_invitado
        else:
            datos = '-'
        return datos

    def get_datos_invitado(self, obj):
        if obj.solicitud.apellido_paterno_invitado and obj.solicitud.apellido_materno_invitado and obj.solicitud.nombre_invitado:
            datos = '{} {}, {}'.format(
                obj.solicitud.apellido_paterno_invitado, obj.solicitud.apellido_materno_invitado, obj.solicitud.nombre_invitado)
        elif obj.solicitud.nombre_invitado:
            datos = '{}'.format(obj.solicitud.nombre_invitado)
        else:
            datos = 'N/A'
        return datos

    def get_email_invitado(self, obj):
        datos = '-'
        if obj.solicitud.email_invitado:
            datos = '{}'.format(obj.solicitud.email_invitado)
        return datos

    def get_numero_documento_solicitante(self, obj):
        if obj.solicitud.numero_documento_solicitante:
            datos = obj.solicitud.numero_documento_solicitante
        else:
            datos = '-'
        return datos

    def get_datos_solicitante(self, obj):
        if obj.solicitud.apellido_paterno_solicitante and obj.solicitud.apellido_materno_solicitante and obj.solicitud.nombre_solicitante:
            datos = '{} {}, {}'.format(
                obj.solicitud.apellido_paterno_solicitante, obj.solicitud.apellido_materno_solicitante, obj.solicitud.nombre_solicitante)
        elif obj.solicitud.nombre_solicitante:
            datos = '{}'.format(obj.solicitud.nombre_solicitante)
        else:
            datos = 'N/A'
        return datos

    def get_email_solicitante(self, obj):
        datos = '-'
        if obj.solicitud.email_solicitante:
            datos = '{}'.format(obj.solicitud.email_solicitante)
        return datos

    def get_datos_responsable(self, obj):
        datos = '-'
        if obj.responsable_id:
            personal = TPersonal.objects.filter(codigo_personal=obj.responsable_id)
            if not personal.exists():
                return datos
            personal = personal.first()
            datos = '{} {}, {}'.format(personal.apellido_paterno, personal.apellido_materno, personal.nombres)
        return datos

    def get_usuario_id(self, obj):
        usuario_id = ''
        if obj.solicitud.usuario_id:
            return obj.solicitud.usuario_id
        return usuario_id

    def get_datos_usuario(self, obj):
        datos = '-'
        if obj.solicitud.usuario_id:
            personal = TPersonal.objects.filter(codigo_personal=obj.solicitud.usuario_id)
            if not personal.exists():
                return datos
            personal = personal.first()
            datos = '{} {}, {}'.format(personal.apellido_paterno, personal.apellido_materno, personal.nombres)
        return datos

    def get_nombre_sede(self, obj):
        datos = '-'
        if obj.solicitud.usuario_id and obj.solicitud.usuario.sede_id:
            sede = Sede.objects.filter(pk=obj.solicitud.usuario.sede.pk_sede)
            if not sede.exists():
                return datos
            sede = sede.first()
            datos = sede.descripcion_sede
        return datos

    def get_nombre_estado_solicitud(self, obj):
        nombre_estado = '-'
        for estado_choice in constants.ESTADO_SOLICITUD_CHOICES:
            if obj.solicitud.estado == estado_choice[0]:
                nombre_estado = estado_choice[1]
                break
        return nombre_estado

    def get_nombre_estado(self, obj):
        nombre_estado = '-'
        for estado_choice in constants.ESTADO_AUDIENCIA_CHOICES:
            if obj.estado == estado_choice[0]:
                nombre_estado = estado_choice[1]
                break
        return nombre_estado

    def get_nombre_asistencia(self, obj):
        if obj.asistencia_total and bool(int(obj.asistencia_total)):
            nombre = constants.ASISTENCIA_AUDIENCIA_DICT.get(constants.ASISTENCIA_AUDIENCIA_TOTAL)
        elif obj.asistencia_unitaria and bool(int(obj.asistencia_unitaria)):
            if obj.asistencia_entidad == constants.ASISTENCIA_ENTIDAD_SOLICITANTE:
                nombre = constants.ASISTENCIA_AUDIENCIA_DICT.get(constants.ASISTENCIA_AUDIENCIA_SOLICITANTE)
            elif obj.asistencia_entidad == constants.ASISTENCIA_ENTIDAD_INVITADO:
                nombre = constants.ASISTENCIA_AUDIENCIA_DICT.get(constants.ASISTENCIA_AUDIENCIA_INVITADO)
            else:
                nombre = constants.ASISTENCIA_AUDIENCIA_DICT.get(constants.ASISTENCIA_AUDIENCIA_NA)
        else:
            nombre = constants.ASISTENCIA_AUDIENCIA_DICT.get(constants.ASISTENCIA_AUDIENCIA_NULA)
        return nombre

    def get_nombre_resultado(self, obj):
        """
        :param obj.resultado: 0: Desacuerdo, 1: Acuerdo Total, 2: Acuerdo Parcial, 3: Falta de acuerdo (para reprogramación), 4: Sin resultado de audiencia  # noqa
        :return: nombre_resultado
        """
        nombre = 'Sin Resultado de audiencia'
        if obj.resultado:
            nombre = constants.RESULTADO_AUDIENCIA_DICT.get(obj.resultado)
            if not nombre:
                nombre = 'Sin Resultado de audiencia'
        return nombre

    def get_nombre_justificacion(self, obj):
        justificacion_invitado = obj.justificacion_invitado
        justificacion_solicitante = obj.justificacion_solicitante
        if (justificacion_solicitante and bool(int(justificacion_solicitante))
                and justificacion_invitado and bool(int(justificacion_invitado))):
            nombre = 'Justificado por el Solicitante y el Invitado'
        elif justificacion_invitado and bool(int(justificacion_invitado)):
            nombre = 'Justificado por el Invitado'
        elif justificacion_solicitante and bool(int(justificacion_solicitante)):
            nombre = 'Justificado por el Solicitante'
        else:
            nombre = 'Sin Justificación'
        return nombre

    def get_nombre_modalidad(self, obj):
        nombre = ''
        if obj.modalidad:
            nombre = constants.DICT_MODALIDAD.get(obj.modalidad)
        return nombre

    def get_historico(self, obj):
        response_list = []
        if (self._context.get('request') and
            self._context.get('request').query_params.get('consolidado')
            == constants.SI_CHAR_BINARY
            and not self._context.get('request').query_params.get('historico')
            == constants.SI_CHAR_BINARY
        ):
            return response_list
        solicitudes_hist = AudienciaHistorico.objects.filter(
            audiencia__pk=obj.pk
        ).order_by('-fecha_registro')
        query_len = len(solicitudes_hist)

        i = query_len
        for sol_hist in solicitudes_hist:
            if sol_hist.fecha_vencimiento:
                fecha_vencimiento = sol_hist.fecha_vencimiento.strftime(
                    '%d/%m/%Y %H:%M:%S'
                )
            else:
                fecha_vencimiento = None
            pk_usuario = sol_hist.usuario.pk if sol_hist.usuario else None
            tipo_documento = (
                sol_hist.usuario.tipo_documento if sol_hist.usuario else None
            )
            tipo_usuario = sol_hist.usuario.tipo_usuario if sol_hist.usuario else None
            results_usuario = se.consultar_usuario(
                se(),
                username=pk_usuario,
                tipo_documento=tipo_documento,
                tipo_usuario=tipo_usuario,
            )
            nombres = None
            apellido_paterno = None
            apellido_materno = None
            if results_usuario[0]:
                nombres = results_usuario[1].get('nombres')
                apellido_paterno = results_usuario[1].get('apellido_paterno')
                apellido_materno = results_usuario[1].get('apellido_materno')
            pk_grupo, nombre_grupo = si.get_perfil_usuario(pk_usuario=pk_usuario)
            response_list.append(
                {
                    'secuencia': i,
                    'pk_solicitud_hist': sol_hist.pk,
                    'pk_usuario': pk_usuario,
                    'pk_grupo': pk_grupo,
                    'nombre_grupo': nombre_grupo.capitalize() if nombre_grupo else None,
                    'nombres': nombres,
                    'apellido_paterno': apellido_paterno,
                    'apellido_materno': apellido_materno,
                    'fecha_registro': sol_hist.fecha_registro.strftime('%d/%m/%Y %H:%M:%S'),
                    'fecha_vencimiento': fecha_vencimiento,
                    'observacion_solicitante': sol_hist.observacion_solicitante,
                    'observacion_invitado': sol_hist.observacion_invitado,
                    'observacion': sol_hist.observacion,
                    'estado': sol_hist.estado,
                    'nombre_estado': constants.DICT_ESTADO_SOLICITUD.get(
                        sol_hist.estado
                    ),
                }
            )
            i -= 1
        return response_list


class AudienciaListaSerializer(AudienciaSerializer):
    class Meta(AudienciaSerializer.Meta):
        exclude = []
        fields = (
            'pk_audiencia',
            'codigo_solicitud',
            'fecha_inicio',
            'solicitud_id',
            'pk_solicitud',
            'audiencia_id',
            'numero_documento_solicitante',
            'datos_solicitante',
            'email_solicitante',
            'numero_documento_invitado',
            'datos_invitado',
            'email_invitado',
            'datos_responsable',
            'nombre_sede',
            'datos_responsable',
            'responsable_id',
            'estado',
            'nombre_estado_solicitud',
            'nombre_estado',
            # 'url_primer_adjunto_base64',
            'audiencia_child_id',
            'audiencia_child_asistencia_total',
            'audiencia_child_asistencia_unitaria',
            'audiencia_child_asistencia_entidad',
            'envio_invitacion',
            'nombre_envio_invitacion',
            'asistencia_total',
            'asistencia_unitaria',
            'asistencia_entidad',
            'url_sustento',
            'url_invitado_adjunto',
            'codigo_inicial'
        )


class AudienciaHistoricoSerializer(AudienciaSerializer):
    class Meta(AudienciaSerializer.Meta):
        exclude = []
        fields = (
            'pk_audiencia',
            'codigo_solicitud',
            'fecha_inicio',
            'numero_duracion',
            'fecha_fin',
            'solicitud_id',
            'audiencia_id',
            'numero_documento_solicitante',
            'datos_solicitante',
            'numero_documento_invitado',
            'datos_invitado',
            'datos_responsable',
            'nombre_sede',
            'datos_responsable',
            'estado',
            'nombre_estado_solicitud',
            'nombre_estado',
            'audiencia_child_id',
            'nombre_envio_invitacion',
            'resultado',
            'asistencia_total',
            'asistencia_unitaria',
            'asistencia_entidad',
            'modalidad'
        )


class AudienciaEditarSerializer(serializers.ModelSerializer):
    solicitud_id = serializers.IntegerField(required=False)
    audiencia_id = serializers.IntegerField(required=False)
    responsable_id = serializers.CharField(required=False)
    estado = serializers.CharField(required=False)

    class Meta:
        model = Audiencia
        exclude = (
            'pk_audiencia',
            'solicitud',
            'audiencia',
            'responsable'
        )


class AudienciaReporteSerializer(AudienciaSerializer):
    class Meta(AudienciaSerializer.Meta):
        exclude = []
        fields = (
            'codigo_solicitud',
            'codigo_audiencia',
            'fecha_inicio',
            'fecha_fin',
            'tipo_documento_solicitante_str',
            'numero_documento_solicitante',
            'datos_solicitante',
            'tipo_documento_invitado_str',
            'numero_documento_invitado',
            'datos_invitado',
            'usuario_id',
            'datos_usuario',
            'responsable_id',
            'datos_responsable',
            'nombre_sede',
            'nombre_estado_solicitud',
            'motivos',
            'nombre_envio_invitacion',
            'nombre_asistencia',
            'nombre_resultado',
            'nombre_justificacion',
            'nombre_modalidad',
            'nombre_estado'
        )
