"""
Vistas para API aplicación de Programacion.

Copyright (C) 2022 PRODUCE.

Authors:
    Omar Ruelas Principe <ddf_temp57@produce.gob.pe>
"""
import hashlib
import base64
from datetime import datetime, timedelta, date
import holidays
import os
import re
import io
import json
import qrcode
import base64
from io import BytesIO
import logging
import pandas as pd
import numpy as np
from rest_framework import status
from unidecode import unidecode
from django.utils import timezone
import xlsxwriter

from django.conf import settings
from django.db import connection, models
from django.db.models import Q
from django.http import HttpResponse
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    UpdateAPIView,
    RetrieveUpdateAPIView, GenericAPIView
)
from rest_framework.views import APIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.dateparse import parse_date

from apps.seguridad.api.use_cases import UsuarioInvitacionUseCase
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_208_ALREADY_REPORTED,
    HTTP_206_PARTIAL_CONTENT
)

from apps.common import constants
from apps.common.functions import ServiciosInternos as si, get_url_archivo_absoluta, pdf_to_base64
from apps.common.utils import CustomPagination, convertir_parametro_insensible, get_consulta_directa
from apps.common.utils import StandardResultsSetPagination, working_daterange, calendar_daterange
from apps.programacion.api.serializers import (
    SedeSerializer, SolicitudSerializer, SolicitudDetalleSerializer, MotivoSerializer, ArchivoSerializer,
    SolicitudListaSerializer, SolicitudEditarSerializer, PlantillaSerializer, PlantillaListaSerializer,
    AudienciaSerializer, InvitacionSerializer, AudienciaEditarSerializer, SolicitudReporteSerializer,
    AudienciaListaSerializer, AudienciaReporteSerializer, AudienciaHistoricoSerializer, PlanillaSerializer,
    QuintaCategoriaSerializer
)
from apps.programacion.models import (
    Sede, SolicitudDetalle, Solicitud, Motivo, Plantilla, Audiencia,
    SolicitudHistorico, AudienciaHistorico)
from apps.modelsext.models import SiDependencia as HDependencia, SiTrabajador, SiRegimen as HRegimen, SiGenero, \
    SiPersona as HPersona, TPersonal
from apps.seguridad.models import User as Usuario
from apps.seguridad.auth import CustomAuthenticationTemporal, CustomAuthenticationConfidencial, \
    CustomAuthenticationValidacion

logger = logging.getLogger(__name__)


def get_usuario_id(codigo_trabajador):
    usuario = Usuario.objects.filter(codigo_trabajador=codigo_trabajador)
    if usuario.exists():
        usuario_id = usuario.first().pk
    else:
        usuario_id = None
    return usuario_id


def set_usuario_id(codigo_trabajador, id_dependencia):
    usuario = Usuario.objects.filter(codigo_trabajador=codigo_trabajador)
    if usuario.exists():
        usuario_id = usuario.first().pk
    else:
        usuario, _ = Usuario.objects.get_or_create(
            codigo_trabajador=codigo_trabajador,
            id_dependencia_programacion=id_dependencia
        )
        usuario_id = usuario.pk
    return usuario_id


def get_dependencia_ids(nombre_dependencia=None, codigo_dependencia=None):
    dependencia_ids = []
    if nombre_dependencia:
        dependencia_ids = HDependencia.objects.filter(
            Q(dependencia__icontains=nombre_dependencia) |
            Q(codigo_dependencia=codigo_dependencia)
        ).values_list(
            'codigo_dependencia', flat=True)
        return dependencia_ids
    return dependencia_ids


def get_trabajador_ids(list_init_ids, nombres=None, apellidos=None, numero_documento=None,
                       dependencia_ids=[], codigo_trabajador=None, sexo=None, id_regimen=None):
    if nombres or apellidos or numero_documento or dependencia_ids or codigo_trabajador or sexo or id_regimen:
        datos = {}
        if nombres:
            datos.update({'nombres_trabajador': nombres})
        if apellidos:
            datos.update({'apellidos_trabajador': apellidos})
        if numero_documento:
            datos.update({'dni': numero_documento})
        if id_regimen:
            datos.update({'id_regimen': id_regimen})
        if dependencia_ids:
            for dependencia_id in dependencia_ids:
                datos.update({'codigo_dependencia': dependencia_id})
        if codigo_trabajador:
            datos.update({'codigo_trabajador': codigo_trabajador})
        trabajador_ids = SiTrabajador.objects.filter(codigo_trabajador__in=list_init_ids)
        trabajador_ids = trabajador_ids.filter(**datos)
        # trabajador_values_ids = trabajador_ids.values_list('codigo_trabajador', 'dni', flat=True)
        # trabajador_nro_documentos = SiTrabajador.objects.filter(codigo_trabajador__in=list_init_ids)
        # trabajador_nro_documentos = trabajador_nro_documentos.filter(**datos).values_list('dni', flat=True)
        if sexo:
            nro_documento_personas = []
            for trabajador_nro_documento in trabajador_ids:
                persona = HPersona.objects.filter(nro_docpernatural=trabajador_nro_documento.dni, cod_genero=sexo)
                nro_documento_persona = persona.first().nro_docpernatural if persona.exists() else None
                if nro_documento_persona:
                    nro_documento_personas.append(nro_documento_persona)
            trabajador_ids = trabajador_ids.filter(dni__in=nro_documento_personas).values_list('codigo_trabajador',
                                                                                               flat=True)
        return trabajador_ids
    else:
        trabajador_ids = SiTrabajador.objects.filter(codigo_trabajador__in=list_init_ids).values_list(
            'codigo_trabajador', flat=True)
    return trabajador_ids


def get_sexo(numero_documento_persona):
    persona = HPersona.objects.filter(nro_docpernatural=numero_documento_persona)
    codigo_sexo = persona.first().cod_genero if persona.exists() else None
    genero = SiGenero.objects.filter(codigo_sexo=codigo_sexo)
    nombre_genero = genero.first().col002 if genero.exists() else None
    return nombre_genero


class SedeAPIView(ListCreateAPIView):
    serializer_class = SedeSerializer
    http_method_names = ['get', 'post']

    def get_object(self):
        query_set = Sede.objects.filter(pk_sede=self.kwargs.get('pk_sede'))
        if not query_set.exists():
            return None
        return query_set.first()

    def get_queryset(self):
        data = self.request.query_params.copy()
        query_set = Sede.objects.all()
        if data.get('codigo_sede'):
            query_set = query_set.filter(codigo_sede=data.get('codigo_sede'))
        if data.get('codigo_region'):
            query_set = query_set.filter(codigo_region=data.get('codigo_region'))
        if data.get('codigo_zona'):
            query_set = query_set.filter(codigo_zona=data.get('codigo_zona'))
        if data.get('descripcion_sede'):
            query_set = query_set.filter(
                descripcion_sede__icontains=convertir_parametro_insensible(data.get('descripcion_sede')))
        return query_set

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class MotivoAPIView(ListCreateAPIView):
    queryset = Motivo.objects.all()
    serializer_class = MotivoSerializer

    def get_queryset(self):
        data = self.request.query_params.copy()
        query_set = Motivo.objects.all()
        if data.get('pk_motivo'):
            query_set = query_set.filter(pk_motivo=data.get('pk_motivo'))
        if data.get('codigo_motivo'):
            query_set = query_set.filter(codigo_motivo=data.get('codigo_motivo'))
        if data.get('descripcion_motivo'):
            query_set = query_set.filter(descripcion_motivo__icontains=data.get('descripcion_motivo'))
        return query_set

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class ConsultaPlanillaView(APIView):
    pagination_class = CustomPagination
    authentication_classes =[]

    def post(self, request, *args, **kwargs):
        # Seteo de todas las variables de entrada
        data = {
            "numero_expediente": request.data.get("numero_expediente"),
            "tipo_documento": request.data.get("tipo_documento"),
            "numero_documento": request.data.get("numero_documento"),
            "fecha_inicio": request.data.get("fecha_inicio"),
            "fecha_fin": request.data.get("fecha_fin"),
            "pk_motivo": request.data.get("pk_motivo"),
            "tipo_categoria": request.data.get("tipo_categoria"),
            "consolidado": request.data.get("consolidado"),
            "numero_ruc": request.data.get("numero_ruc"),
        }

        # Restricciones de seguridad
        # if data.get('consolidado') == constants.SI_CHAR_BINARY and data.get('numero_ruc') and data.get('tipo_categoria') == constants.QUINTA_CATEGORIA:
        #     message = 'No debe indicarse el número de ruc si la búsqueda en consolidada para la quinta categoría'
        #     return Response({'error': message}, status=HTTP_400_BAD_REQUEST)
        # elif data.get('consolidado') == constants.NO_CHAR_BINARY and not data.get('numero_ruc') and data.get('tipo_categoria') == constants.QUINTA_CATEGORIA:
        #     message = 'Debe indicarse el número de ruc si la búsqueda en detallada para la quinta categoría'
        #     return Response({'error': message}, status=HTTP_400_BAD_REQUEST)

        # En caso consolidado = 0, numero_ruc exista y tipo_categoria = 'quinta',
        # entonces la cantidad de registros en el resultado será de 1 en 1.
        # Caso contrario, será 10 en 10.
        # if data.get('consolidado') == constants.NO_CHAR_BINARY and data.get('numero_ruc') and data.get('tipo_categoria') == constants.QUINTA_CATEGORIA:  # noqa
        #     self.pagination_class.default_limit = 1

        # ToDo: Desarrollar la lógica en utils para obtener la información de las tablas de PLANELE
        response_data = get_consulta_directa(data)
        # Serialización del response
        serializer = QuintaCategoriaSerializer(data=response_data, many=True)
        return Response(response_data, status=status.HTTP_200_OK)
        # if serializer.is_valid():
        # paginated_response = self.paginate_queryset(response_data.data, request, view=self)
        # return self.get_paginated_response(paginated_response)
        # return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class SolicitudAPIView(ListCreateAPIView):
    pagination_class = CustomPagination
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        self.pagination_class.default_limit = 10
        page = self.paginate_queryset(queryset)
        if page is not None:
            if bool(int(request.query_params.get('consolidado', '0'))):
                serializer = SolicitudListaSerializer(page, many=True)
            else:
                serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        data = self.request.query_params.copy()
        query_set = Solicitud.objects.all()
        if data.get('pk_solicitud'):
            query_set = query_set.filter(pk_solicitud=data.get('pk_solicitud'))
        if data.get('codigo_solicitud'):
            audiencias = Audiencia.objects.filter(
                Q(codigo_inicial=data.get('codigo_solicitud')) |
                Q(solicitud__codigo_solicitud=data.get('codigo_solicitud'))
            )
            if audiencias.exists():
                pk_solicitudes = audiencias.values_list('solicitud__pk_solicitud', flat=True)
                query_set = query_set.filter(pk_solicitud__in=pk_solicitudes)
            else:
                query_set = query_set.filter(codigo_solicitud=data.get('codigo_solicitud'))
        if data.get('q_solicitante'):
            query_set = query_set.filter(
                Q(numero_documento_solicitante=data.get('q_solicitante')) |
                Q(nombre_solicitante__icontains=convertir_parametro_insensible(data.get('q_solicitante'))) |
                Q(apellido_paterno_solicitante__icontains=convertir_parametro_insensible(data.get('q_solicitante'))) |
                Q(apellido_materno_solicitante__icontains=convertir_parametro_insensible(data.get('q_solicitante')))
            )
        if data.get('numero_documento_solicitante'):
            query_set = query_set.filter(numero_documento_solicitante=data.get('numero_documento_solicitante'))
        if data.get('numero_documento_invitado'):
            query_set = query_set.filter(numero_documento_invitado=data.get('numero_documento_invitado'))
        if data.get('codigo_sede'):
            query_set = query_set.filter(usuario__sede__codigo_sede=data.get('codigo_sede'))
        if data.get('numero_documento_rl'):
            query_set = query_set.filter(numero_documento_rl=data.get('numero_documento_rl'))
        if data.get('estado_list'):
            estado_list = data.get('estado_list').split(',')
            query_set = query_set.filter(estado__in=estado_list)
        if data.get('estado'):
            query_set = query_set.filter(estado=data.get('estado'))
        return query_set.order_by('-pk_solicitud')

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data = {key: value for key, value in data.items() if value}
        departamento_solicitante = data.pop('departamento_solicitante')
        provincia_solicitante = data.pop('provincia_solicitante')
        distrito_solicitante = data.pop('distrito_solicitante')
        ubigeo_solicitante_vals = si.get_ubigeo(departamento_solicitante, provincia_solicitante, distrito_solicitante)
        departamento_invitado = data.pop('departamento_invitado')
        provincia_invitado = data.pop('provincia_invitado')
        distrito_invitado = data.pop('distrito_invitado')
        ubigeo_invitado_vals = si.get_ubigeo(departamento_invitado, provincia_invitado, distrito_invitado)

        # Validar Codigo de Solicitud
        try:
            codigo_solicitud = data.get('codigo_solicitud')
            solicitudes = Solicitud.objects.filter(codigo_solicitud=codigo_solicitud)
            if solicitudes.exists():
                message = 'El código de solicitud: {} ya existe'.format(codigo_solicitud)
                return Response({'error': message}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Crear Registro Cabecera
        try:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            instance = serializer.instance
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Agregar Detalle de motivos (SolicitudDetalle)
        try:
            motivo_list = []
            usuario = instance.usuario
            if usuario and not data.get('sede_id'):
                instance.sede = usuario.sede
            if data.get('motivo_list'):
                motivo_list = data.pop('motivo_list')
            for motivo_item in motivo_list:
                motivo = Motivo.objects.filter(codigo_motivo=motivo_item[0])
                if not motivo.exists():
                    continue
                motivo = motivo.first()
                if motivo.codigo_motivo != constants.CODIGO_MOTIVO_OTROS:
                    descripcion = motivo.descripcion_motivo
                else:
                    if not motivo_item[1]:
                        message = 'Debe especificar la descripción del motivo en caso elija: Otros'
                        return Response({'error': message}, status=HTTP_400_BAD_REQUEST)
                    descripcion = motivo_item[1]
                solicitud_motivo, _ = SolicitudDetalle.objects.get_or_create(
                    solicitud=instance, motivo=motivo, descripcion=descripcion, flag=constants.SI_CHAR_BINARY
                )
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Actualizar usuario y ubigeo
        try:
            if not data.get('usuario_id'):
                usuario = si.get_usuario_token(self.request)
                instance.usuario = usuario
            instance.departamento_solicitante = ubigeo_solicitante_vals.get('departamento').get('instance')
            instance.provincia_solicitante = ubigeo_solicitante_vals.get('provincia').get('instance')
            instance.distrito_solicitante = ubigeo_solicitante_vals.get('distrito').get('instance')
            instance.departamento_invitado = ubigeo_invitado_vals.get('departamento').get('instance')
            instance.provincia_invitado = ubigeo_invitado_vals.get('provincia').get('instance')
            instance.distrito_invitado = ubigeo_invitado_vals.get('distrito').get('instance')
            instance.save()
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Crear Registro de Histórico
        try:
            vals = {
                'usuario': instance.usuario,
                'solicitud': instance,
                'fecha_registro': data.get('fecha_registro', '') if data.get('fecha_registro', '') else datetime.now(),
                'estado': instance.estado,
            }
            if data.get('observacion', ''):
                vals.update({'observacion': data.get('observacion', ''), })
            if data.get('url_anexo'):
                vals.update({'url_anexo': data.get('url_anexo', '')})
            if data.get('url_sustento'):
                vals.update({'url_sustento': data.get('url_sustento', '')})
            solicitud_historico, _ = SolicitudHistorico.objects.get_or_create(**vals)
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class SolicitudUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer

    def get_queryset_historicos(self, pk_solicitud, pk_usuario=None):
        historicos = SolicitudHistorico.objects.filter(solicitud__pk=pk_solicitud)
        return historicos if historicos.exists() else None

    def get_object(self):
        query_set = Solicitud.objects.filter(pk_solicitud=self.kwargs.get('pk_solicitud'))
        if not query_set.exists():
            return None
        return query_set.first()

    def put(self, request, *args, **kwargs):
        query_set = Solicitud.objects.filter(pk=self.kwargs.get('pk_solicitud'))
        data = request.data.copy()
        if query_set.exists():
            if data.get('estado') in (constants.ESTADO_SOLICITUD_FINALIZADA, constants.ESTADO_SOLICITUD_ANULADA):
                return Response(
                    {'error': ('La solicitud no puede ser editada porque se encuentra en estado',)},
                    HTTP_400_BAD_REQUEST,
                )
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        if not instance:
            return Response(
                {'error': ('Solicitud no encontrada',)},
                HTTP_404_NOT_FOUND,
            )
        predata_estado = instance.estado
        predata_historicos = SolicitudHistorico.objects.filter(
            estado=predata_estado, solicitud=instance
        )
        predata_historico = (
            predata_historicos.last() if predata_historicos.exists() else None
        )
        if data.get('fecha_nacimiento_solicitante') == '':
            _ = data.pop('fecha_nacimiento_solicitante')

        # Editar Solicitud Cabecera
        try:
            serializer = SolicitudEditarSerializer(instance=instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        # Agregar Detalle de motivos (SolicitudDetalle)
        try:
            detalle = SolicitudDetalle.objects.filter(solicitud=instance)
            if detalle.exists():
                detalle.update(flag=constants.NO_CHAR_BINARY)
            motivo_list = []
            if data.get('motivo_list'):
                motivo_list = data.pop('motivo_list')
            for motivo_item in motivo_list:
                motivo = Motivo.objects.filter(codigo_motivo=motivo_item[0])
                if not motivo.exists():
                    continue
                motivo = motivo.first()
                if motivo.codigo_motivo != constants.CODIGO_MOTIVO_OTROS:
                    descripcion = motivo.descripcion_motivo
                else:
                    if not motivo_item[1]:
                        message = 'Debe especificar la descripción del motivo en caso elija: Otros'
                        return Response({'error': message}, status=HTTP_400_BAD_REQUEST)
                    descripcion = motivo_item[1]
                solicitud_motivo, _ = SolicitudDetalle.objects.get_or_create(
                    solicitud=instance, motivo=motivo, descripcion=descripcion, flag=constants.SI_CHAR_BINARY
                )
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Actualizar histórico y documentos de la iteración respectiva
        try:
            predata_fecha_vencimiento = None
            if data.get('estado') not in (
                constants.ESTADO_SOLICITUD_FINALIZADA,
                constants.ESTADO_SOLICITUD_ANULADA,
            ):
                if predata_historico and predata_historico.fecha_vencimiento:
                    predata_fecha_vencimiento = predata_historico.fecha_vencimiento
            historicos = self.get_queryset_historicos(self.kwargs.get('pk_solicitud'))
            ultimo_historico = None
            if historicos:
                historicos = historicos.filter(
                    estado=data.get('estado'),
                )
                ultimo_historico = historicos.order_by('-fecha_registro').first() if historicos else None
            if not ultimo_historico:
                if data.get('estado'):
                    estado = data.get('estado')
                else:
                    estado = (
                        historicos.order_by('-fecha_registro').first().estado
                        if historicos
                        else None
                    )
                if not estado:
                    return Response(
                        {
                            'error': 'Se debe registrar el estado actual o uno nuevo para actualizar una solicitud'
                        },
                        status=HTTP_400_BAD_REQUEST,
                    )
                usuario = si.get_usuario_token(self.request)

                if data.get('codigo_expediente', '00') == '02' and not data.get(
                    'mensaje_expediente', ''
                ):
                    return Response(
                        {
                            'error': 'Si el código de expediente no es exitoso, '
                                     'debe enviar un mensaje relacionado al error'
                            # noqa
                        },
                        status=HTTP_400_BAD_REQUEST,
                    )
                vals = {
                    'usuario': usuario,
                    'solicitud': instance,
                    'fecha_registro': datetime.now(),
                    'observacion': data.get('observacion', ''),
                    'fecha_vencimiento': predata_fecha_vencimiento if predata_fecha_vencimiento else None,
                    'estado': estado,
                }
                if data.get('url_anexo'):
                    vals.update({'url_anexo': data.get('url_anexo', '')})
                if data.get('url_sustento'):
                    vals.update({'url_sustento': data.get('url_sustento', '')})
                solicitud_historico, _ = SolicitudHistorico.objects.get_or_create(
                    **vals
                )
            else:
                solicitud_historico = ultimo_historico
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Construir data de respuesta de actualización
        try:
            response_data = serializer.data.copy()
            status_code = HTTP_200_OK
            if data.get('codigo_expediente', '00') == '02':
                mensaje_interno = (
                    'Se produjo un error al enviar la solicitud al '
                    'Sistema de Trámite Documentario. Por favor, intentar nuevamente.'
                )
                status_code = HTTP_206_PARTIAL_CONTENT
            elif data.get('codigo_expediente', '00') == '01':
                mensaje_interno = (
                    'Envío de solicitud al Sistema de Trámite Documentario exitoso.'
                )
            else:
                mensaje_interno = ''
            response_data.update(
                {
                    'codigo_expediente': data.get('codigo_expediente', '00'),
                    'mensaje_expediente': mensaje_interno,
                }
            )
            # ToDo: Agregar motivo_list
            # if data.get('estandar_list'):
            #    response_data.update({'estandares': estandares})
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        return Response(response_data, status=status_code)


class SolicitudDetalleAPIView(ListCreateAPIView):
    queryset = SolicitudDetalle.objects.all()
    serializer_class = SolicitudDetalleSerializer

    def get_queryset(self):
        data = self.request.query_params.copy()
        query_set = SolicitudDetalle.objects.all()
        if data.get('codigo_solicitud'):
            query_set = query_set.filter(
                solicitud__codigo_solicitud=data.get('codigo_solicitud'))
        if data.get('numero_documento_solicitante'):
            query_set = query_set.filter(
                solicitud__numero_documento_solicitante=data.get('numero_documento_solicitante'))
        if data.get('numero_documento_invitado'):
            query_set = query_set.filter(
                solicitud__numero_documento_invitado=data.get('numero_documento_invitado'))
        if data.get('numero_documento_invitado_rl'):
            query_set = query_set.filter(
                solicitud__numero_documento_invitado_rl=data.get('numero_documento_invitado_rl'))
        if data.get('estado'):
            query_set = query_set.filter(
                solicitud__estado=data.get('estado'))
        return query_set

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class SolicitudDetalleUpdateAPIView(RetrieveUpdateAPIView):
    queryset = SolicitudDetalle.objects.all()
    serializer_class = SolicitudDetalleSerializer

    def get_object(self):
        query_set = SolicitudDetalle.objects.filter(pk_solicitud_detalle=self.kwargs.get('pk_solicitud_detalle'))
        if not query_set.exists():
            return None
        return query_set.first()


class SolicitudEstadoAPIView(APIView):

    def get(self, request, *args, **kwargs):
        solicitud_estados = constants.ESTADO_SOLICITUD_CHOICES
        estado_list = []
        data = self.request.query_params.copy()
        for solicitud_estado in solicitud_estados:
            estado_list.append({'codigo_estado': solicitud_estado[0], 'nombre_estado': solicitud_estado[1]})
        if data.get('codigo_estado'):
            q_list = []
            for estado in estado_list:
                if estado.get('codigo_estado') == data.get('codigo_estado'):
                    q_list.append(
                        {'codigo_estado': estado.get('codigo_estado'), 'nombre_estado': estado.get('nombre_estado')})
                    break
            estado_list = q_list
        if data.get('nombre_estado'):
            q_list = []
            for estado in estado_list:
                if data.get('nombre_estado') in estado.get('nombre_estado'):
                    q_list.append(
                        {'codigo_estado': estado.get('codigo_estado'), 'nombre_estado': estado.get('nombre_estado')})
            estado_list = q_list
        return Response(estado_list, status=HTTP_200_OK)


class AudienciaEstadoAPIView(APIView):

    def get(self, request, *args, **kwargs):
        audiencia_estados = constants.ESTADO_AUDIENCIA_CHOICES
        estado_list = []
        data = self.request.query_params.copy()
        for audiencia_estado in audiencia_estados:
            estado_list.append({'codigo_estado': audiencia_estado[0], 'nombre_estado': audiencia_estado[1]})
        if data.get('codigo_estado'):
            q_list = []
            for estado in estado_list:
                if estado.get('codigo_estado') == data.get('codigo_estado'):
                    q_list.append(
                        {'codigo_estado': estado.get('codigo_estado'), 'nombre_estado': estado.get('nombre_estado')})
                    break
            estado_list = q_list
        if data.get('nombre_estado'):
            q_list = []
            for estado in estado_list:
                if data.get('nombre_estado') in estado.get('nombre_estado'):
                    q_list.append(
                        {'codigo_estado': estado.get('codigo_estado'), 'nombre_estado': estado.get('nombre_estado')})
            estado_list = q_list
        return Response(estado_list, status=HTTP_200_OK)


class GuardarArchivoAPIView(APIView):
    def post(self, request):
        try:
            serializer = ArchivoSerializer(data=request.data)
            if serializer.is_valid():
                ruta_archivo = serializer.save()
                return Response(
                    {
                        'mensaje': 'Registrado satisfactoriamente',
                        'archivo': ruta_archivo,
                    }
                )
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'mensaje': f'Error al registrar el archivo, detalle: {str(e)}'},
                status=HTTP_400_BAD_REQUEST,
            )


class DescargarArchivoAPIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            data = self.request.query_params.copy()
            ruta_archivo = data.get('archivo_url')
            response = get_url_archivo_absoluta(ruta_archivo)
            if type(response) == str:
                return Response(
                    {'mensaje': f'Error al descargar el archivo, detalle: {response}'},
                    status=HTTP_400_BAD_REQUEST,
                )
            return response
        except Exception as e:
            return Response(
                {'mensaje': f'Error al descargar el archivo, detalle: {str(e)}'},
                status=HTTP_400_BAD_REQUEST,
            )


class DescargarArchivoB64APIView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            data = self.request.query_params.copy()
            ruta_archivo = data.get('archivo_url')
            ruta_archivo_b64 = pdf_to_base64(ruta_archivo)
            return Response(
                {'archivo_url_base64': ruta_archivo_b64, 'archivo_url': ruta_archivo},
                status=HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {'mensaje': f'Error al descargar el archivo, detalle: {str(e)}'},
                status=HTTP_400_BAD_REQUEST,
            )


class GuardarInvitacionAPIView(APIView):
    def post(self, request):
        try:
            serializer = InvitacionSerializer(data=request.data)
            if serializer.is_valid():
                ruta_archivo = serializer.save()
                return Response(
                    {
                        'mensaje': 'Invitación registrada satisfactoriamente',
                        'archivo': ruta_archivo,
                    }
                )
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'mensaje': f'Error al registrar la invitacion, detalle: {str(e)}'},
                status=HTTP_400_BAD_REQUEST,
            )


class PlantillaAPIView(ListCreateAPIView, RetrieveUpdateAPIView):
    queryset = Plantilla.objects.all()
    pagination_class = CustomPagination
    serializer_class = PlantillaSerializer

    def get_queryset(self):
        data = self.request.query_params.copy()
        query_set = Plantilla.objects.all()
        if data.get('estado'):
            query_set = query_set.filter(estado=data.get('estado'))
        if data.get('codigo'):
            query_set = query_set.filter(codigo=data.get('codigo'))
        if data.get('pk_plantilla'):
            query_set = query_set.filter(pk_plantilla=data.get('pk_plantilla'))
        return query_set

    def get_object(self):
        query_set = Plantilla.objects.filter(pk_plantilla=self.kwargs.get('pk_plantilla'))
        if not query_set.exists():
            return None
        return query_set.first()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        self.pagination_class.default_limit = 10
        page = self.paginate_queryset(queryset)
        if page is not None:
            if request.query_params.get('consolidado') and bool(int(request.query_params.get('consolidado'))):
                serializer = PlantillaListaSerializer(page, many=True)
            else:
                serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # Verificar si se proporcionó un archivo en la solicitud
        archivo = data.pop('archivo', None)

        # Si se proporcionó un archivo, leer su contenido y asignarlo al campo "codigo"
        if archivo:
            try:
                with archivo[0].open() as file:
                    contenido = file.read()
                data['descripcion'] = contenido
            except Exception as e:
                return Response(
                    {'error': 'No se pudo leer el archivo. {}'.format(str(e))}, status=HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class AudienciaCodigoAPIView(APIView):

    def get(self, request):
        try:
            audiencias = Audiencia.objects.exclude(estado=constants.ESTADO_AUDIENCIA_ANULADA).order_by('-pk_audiencia')
            if audiencias.exists():
                sgte_numero = len(audiencias) + 1
                codigo_inicial = str(sgte_numero).rjust(4, '0')
                return Response(
                    {
                        'siguiente_codigo': codigo_inicial,
                        'ultima_audiencia_id': audiencias.first().pk_audiencia,
                    }
                )
            return Response(
                {
                    'siguiente_codigo': str(0).rjust(4, '0'),
                    'ultima_audiencia_id': '',
                }
            )
        except Exception as e:
            return Response(
                {'detail': f'Error buscar el siguiente código de audiencia, detalle: {str(e)}'},
                status=HTTP_400_BAD_REQUEST,
            )


class AudienciaAPIView(ListCreateAPIView):
    queryset = Audiencia.objects.all()
    pagination_class = CustomPagination
    serializer_class = AudienciaSerializer
    http_method_names = ['get', 'post']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        self.pagination_class.default_limit = 10
        page = self.paginate_queryset(queryset)
        if page is not None:
            if bool(int(request.query_params.get('consolidado', '0'))):
                serializer = AudienciaListaSerializer(page, many=True)
            elif bool(int(request.query_params.get('historico', '0'))):
                serializer = AudienciaHistoricoSerializer(page, many=True)
            else:
                serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        data = self.request.query_params.copy()
        query_set = Audiencia.objects.all()

        fecha_inicio_str = data.get('fecha_inicio', None)
        fecha_fin_str = data.get('fecha_fin', None)

        # Convertir las fechas a objetos datetime si se proporcionan
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d %H:%M:%S') if fecha_inicio_str else None
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d %H:%M:%S') if fecha_fin_str else None

        if data.get('pk_audiencia'):
            query_set = query_set.filter(pk_audiencia=data.get('pk_audiencia'))
        if fecha_inicio:
            query_set = query_set.filter(fecha_inicio__gte=fecha_inicio)
        if fecha_fin:
            query_set = query_set.filter(fecha_inicio__lte=fecha_fin)
        if data.get('codigo_solicitud'):
            query_set = query_set.filter(
                Q(codigo_inicial=data.get('codigo_solicitud')) |
                Q(solicitud__codigo_solicitud=data.get('codigo_solicitud'))
            )
        if data.get('codigo_sede'):
            query_set = query_set.filter(solicitud__usuario__sede__codigo_sede=data.get('codigo_sede'))
        if data.get('q_solicitante'):
            query_set = query_set.filter(
                Q(solicitud__numero_documento_solicitante=data.get('q_solicitante')) |
                Q(solicitud__nombre_solicitante__icontains=convertir_parametro_insensible(data.get('q_solicitante'))) |
                Q(solicitud__apellido_paterno_solicitante__icontains=convertir_parametro_insensible(
                    data.get('q_solicitante'))) |
                Q(solicitud__apellido_materno_solicitante__icontains=convertir_parametro_insensible(
                    data.get('q_solicitante')))
            )
        if data.get('numero_documento_solicitante'):
            query_set = query_set.filter(
                solicitud__numero_documento_solicitante=data.get('numero_documento_solicitante'))
        if data.get('numero_documento_invitado'):
            query_set = query_set.filter(solicitud__numero_documento_invitado=data.get('numero_documento_invitado'))
        if data.get('numero_documento_invitado_solicitante'):
            query_set = query_set.filter(
                Q(solicitud__numero_documento_invitado=data.get('numero_documento_invitado')) |
                Q(solicitud__numero_documento_invitado=data.get('numero_documento_invitado'))
            )
        if data.get('numero_documento_rl'):
            query_set = query_set.filter(solicitud__numero_documento_rl=data.get('numero_documento_rl'))
        if data.get('estado_solicitud'):
            query_set = query_set.filter(solicitud__estado=data.get('estado_solicitud'))
        if data.get('estado_list'):
            estado_list = data.get('estado_list').split(',')
            query_set = query_set.filter(estado__in=estado_list)
        if data.get('estado'):
            query_set = query_set.filter(estado=data.get('estado'))
        return query_set.order_by('fecha_inicio')

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # Crear Cabecera
        try:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            instance = serializer.instance
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Asignar el codigo inicial de la audiencia
        try:
            audiencias = Audiencia.objects.exclude(estado=constants.ESTADO_AUDIENCIA_ANULADA)
            if not data.get('codigo_inicial'):
                sgte_numero = len(audiencias) + 1
                instance.codigo_inicial = str(sgte_numero).rjust(4, '0')
                instance.save()
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Actualizar el estado y usuario de la solicitud relacionada
        try:
            if not data.get('usuario_id'):
                usuario = si.get_usuario_token(self.request)
                instance.usuario = usuario
                instance.save()
            solicitud = instance.solicitud
            solicitud.estado = constants.ESTADO_SOLICITUD_PROGRAMADA
            solicitud.save()
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Crear Registro de Histórico
        try:
            vals = {
                'usuario': instance.usuario,
                'audiencia': instance,
                'fecha_registro': data.get('fecha_registro', '') if data.get('fecha_registro', '') else datetime.now(),
                'estado': instance.estado,
            }
            if data.get('observacion', ''):
                vals.update({'observacion': data.get('observacion', ''), })
            if data.get('observacion_solicitante', ''):
                vals.update({'observacion_solicitante': data.get('observacion_solicitante', ''), })
            if data.get('observacion_invitado', ''):
                vals.update({'observacion_invitado': data.get('observacion_invitado', ''), })
            if data.get('comentario', ''):
                vals.update({'comentario': data.get('comentario', ''), })
            if data.get('url_anexo'):
                vals.update({'url_anexo': data.get('url_anexo', '')})
            if data.get('url_sustento'):
                vals.update({'url_sustento': data.get('url_sustento', '')})
            historico, _ = AudienciaHistorico.objects.get_or_create(**vals)
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        return Response(serializer.data, status=HTTP_201_CREATED, headers=headers)


class AudienciaUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Audiencia.objects.all()
    serializer_class = AudienciaEditarSerializer
    http_method_names = ['put']

    def get_queryset_historicos(self, pk, pk_usuario=None):
        historicos = AudienciaHistorico.objects.filter(audiencia__pk=pk)
        return historicos if historicos.exists() else None

    def get_object(self):
        query_set = Audiencia.objects.filter(pk_audiencia=self.kwargs.get('pk_audiencia'))
        if not query_set.exists():
            return None
        return query_set.first()

    def put(self, request, *args, **kwargs):
        query_set = Audiencia.objects.filter(pk=self.kwargs.get('pk_audiencia'))
        data = request.data.copy()

        return self.update(request, *args, **kwargs)

    def update_vals_historico(self, vals, data):
        if data.get('url_anexo'):
            vals.update({'url_anexo': data.get('url_anexo', '')})
        if data.get('url_sustento'):
            vals.update({'url_sustento': data.get('url_sustento', '')})
        if data.get('observacion_solicitante', ''):
            vals.update({'observacion_solicitante': data.get('observacion_solicitante', ''), })
        if data.get('observacion_invitado', ''):
            vals.update({'observacion_invitado': data.get('observacion_invitado', ''), })
        if data.get('comentario', ''):
            vals.update({'comentario': data.get('comentario', ''), })
        if data.get('resultado'):
            vals.update({'resultado': data.get('resultado', '')})
        return vals

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        data = request.data.copy()

        if not instance:
            return Response(
                {'error': ('Audiencia no encontrada',)},
                HTTP_404_NOT_FOUND,
            )
        predata_estado = instance.estado
        predata_historicos = AudienciaHistorico.objects.filter(estado=predata_estado, audiencia=instance)
        predata_historico = predata_historicos.last() if predata_historicos.exists() else None

        # Evaluar si la Audiencia ya ha sido justificada por la misma entidad
        try:
            audiencia_anterior = instance.audiencia
            if audiencia_anterior:
                if data.get('justificacion_invitado', '') and bool(int(data.get('justificacion_invitado', ''))):
                    justificacion_invitado_anterior = audiencia_anterior.justificacion_invitado
                    if justificacion_invitado_anterior == data.get('justificacion_invitado', ''):
                        return Response({
                            'error': 'El invitado ya ha justificado su inasistencia en la audiencia anterior',
                            'detail': 'El invitado ya ha justificado su inasistencia en la audiencia anterior'},
                            status=HTTP_400_BAD_REQUEST)
                    else:
                        audiencia_preliminar = audiencia_anterior.audiencia
                        if audiencia_preliminar:
                            justificacion_invitado_preliminar = audiencia_preliminar.justificacion_invitado
                            if justificacion_invitado_preliminar == data.get('justificacion_invitado', ''):
                                return Response({
                                    'error': 'El invitado ya ha justificado su inasistencia en una audiencia anterior',
                                    'detail': 'El invitado ya ha justificado su inasistencia en una audiencia anterior'},
                                    status=HTTP_400_BAD_REQUEST)
                if data.get('justificacion_solicitante', '') and bool(int(data.get('justificacion_solicitante', ''))):
                    justificacion_solicitante_anterior = audiencia_anterior.justificacion_solicitante
                    if justificacion_solicitante_anterior == data.get('justificacion_solicitante', ''):
                        return Response({
                            'error': 'El solicitante ya ha justificado su inasistencia en la audiencia anterior',
                            'detail': 'El solicitante ya ha justificado su inasistencia en la audiencia anterior'},
                            status=HTTP_400_BAD_REQUEST)
                    else:
                        audiencia_preliminar = audiencia_anterior.audiencia
                        if audiencia_preliminar:
                            justificacion_solicitante_preliminar = audiencia_preliminar.justificacion_solicitante
                            if justificacion_solicitante_preliminar == data.get('justificacion_solicitante', ''):
                                return Response({
                                    'error': 'El solicitante ya ha justificado su inasistencia en una audiencia anterior',
                                    'detail': 'El solicitante ya ha justificado su inasistencia en una audiencia anterior'
                                },
                                    status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Editar Audiencia Cabecera
        try:
            update_data = request.data.copy()
            if data.get('reinvindicacion', ''):
                _ = update_data.pop('reinvindicacion')

            serializer = AudienciaEditarSerializer(
                instance=instance, data=update_data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        # Obtener el numero de duracion a partir de la fecha fin
        try:
            numero_duracion = 0
            if data.get('fecha_fin'):
                try:
                    fecha_fin = datetime.strptime(data.get('fecha_fin'), '%Y-%m-%d %H:%M:%S')
                except Exception:
                    fecha_fin = datetime.strptime(data.get('fecha_fin'), '%Y-%m-%dT%H:%M:%S')
                fecha_inicio = instance.fecha_inicio
                numero_duracion = (fecha_fin - fecha_inicio).total_seconds() / 60
            if numero_duracion > 0:
                instance.numero_duracion = numero_duracion
                instance.save()
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Actualizar información de la solicitud a partir de la audiencia
        try:
            if data.get('responsable_id'):
                responsable_id = data.get('responsable_id')
                instance.estado = constants.ESTADO_AUDIENCIA_ASIGNADA
                instance.save()
                solicitud = instance.solicitud
                solicitud.responsable_id = responsable_id
                solicitud.estado = constants.ESTADO_SOLICITUD_ASIGNADA
                solicitud.save()
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Actualizar la audiencia cabecera a partir de la audiencia
        try:
            if instance.estado == constants.ESTADO_AUDIENCIA_ATENDIDA:
                if data.get('resultado') in (
                    constants.RESULTADO_AUDIENCIA_ACUERDO_TOTAL, constants.RESULTADO_AUDIENCIA_ACUERDO_PARCIAL):
                    correlativo_audiencia = Audiencia.objects.filter(
                        estado=constants.ESTADO_AUDIENCIA_ATENDIDA,
                        resultado__in=(constants.RESULTADO_AUDIENCIA_ACUERDO_TOTAL,
                                       constants.RESULTADO_AUDIENCIA_ACUERDO_PARCIAL)
                    )
                    instance.codigo_audiencia = '{}-{}'.format(
                        str(correlativo_audiencia.count()).rjust(4, '0'), str(datetime.now().year))
                    instance.save()
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Anular la solicitud a partir de la audiencia anulada
        try:
            if data.get('estado') == constants.ESTADO_AUDIENCIA_ANULADA:
                solicitud = instance.solicitud
                solicitud.estado = constants.ESTADO_SOLICITUD_ANULADA
                solicitud.save()
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Actualizar histórico de audiencia respectiva
        try:
            # Si hay asistencia unitaria, estado Audiencia Atendida
            asistencia_unitaria = data.get('asistencia_unitaria')
            if asistencia_unitaria and bool(int(asistencia_unitaria)) and data.get(
                'estado', '') == constants.ESTADO_AUDIENCIA_ATENDIDA:
                fecha_vencimiento = None

            predata_fecha_vencimiento = None
            if data.get('estado') not in (
                constants.ESTADO_AUDIENCIA_ATENDIDA,
                constants.ESTADO_AUDIENCIA_ANULADA,
            ):
                if predata_historico and predata_historico.fecha_vencimiento:
                    predata_fecha_vencimiento = predata_historico.fecha_vencimiento
            historicos = self.get_queryset_historicos(self.kwargs.get('pk_audiencia'))
            ultimo_historico = None
            if historicos:
                historicos = historicos.filter(
                    estado=data.get('estado'),
                )
                ultimo_historico = historicos.order_by('-fecha_registro').first() if historicos else None
            usuario = si.get_usuario_token(self.request)
            if not ultimo_historico:
                if data.get('estado'):
                    estado = data.get('estado')
                else:
                    estado = (
                        historicos.order_by('-fecha_registro').first().estado
                        if historicos
                        else None
                    )
                if not estado:
                    return Response(
                        {'error': 'Se debe indicar el estado para el nuevo registro; caso contrario, '
                                  'se debe tener al menos un último histórico con un estado previo'},
                        status=HTTP_400_BAD_REQUEST,
                    )
                vals = {
                    'usuario': usuario,
                    'audiencia': instance,
                    'fecha_registro': datetime.now(),
                    'observacion': data.get('observacion', ''),  # Justificacion
                    'fecha_vencimiento': predata_fecha_vencimiento if predata_fecha_vencimiento else None,
                    'estado': estado,
                }
                vals = self.update_vals_historico(vals, data)

                audiencia_historico, _ = AudienciaHistorico.objects.get_or_create(
                    **vals
                )
            else:
                audiencia_historico = ultimo_historico
                reinvindicacion = data.get('reinvindicacion', '')
                if reinvindicacion and bool(int(reinvindicacion)):
                    vals = {
                        'usuario': usuario,
                        'audiencia': instance,
                        'fecha_registro': datetime.now(),
                        'observacion': data.get('observacion', ''),
                        'fecha_vencimiento': predata_fecha_vencimiento if predata_fecha_vencimiento else None,
                        'estado': audiencia_historico.estado,
                    }
                    vals = self.update_vals_historico(vals, data)
                    audiencia_historico, _ = AudienciaHistorico.objects.get_or_create(**vals)
                else:
                    if data.get('url_sustento'):
                        audiencia_historico.url_sustento = data.get('url_sustento')
                    if data.get('url_anexo'):
                        audiencia_historico.url_anexo = data.get('url_anexo')
                    if data.get('observacion'):
                        audiencia_historico.observacion = data.get('observacion')
                    if data.get('observacion_solicitante'):
                        audiencia_historico.observacion_solicitante = data.get('observacion_solicitante')
                    if data.get('observacion_invitado'):
                        audiencia_historico.observacion_invitado = data.get('observacion_invitado')
                    audiencia_historico.save()
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Generar fecha límite para el histórica
        try:
            # pk_grupo, nombre_grupo = si.get_perfil_usuario(usuario.pk_usuario)
            if instance.fecha_fin:
                start_date_solicitud = instance.fecha_fin
            else:
                start_date_solicitud = datetime.now()
            if (instance.asistencia_unitaria
                and bool(int(instance.asistencia_unitaria))
                and audiencia_historico.estado in [constants.ESTADO_AUDIENCIA_ATENDIDA]):
                fecha_limite = si.get_fecha_limite_solicitudes(
                    pd, holidays, {'plazo_dias': 4}, start_date_solicitud=start_date_solicitud
                )
                audiencia_historico.fecha_vencimiento = fecha_limite
                audiencia_historico.save()
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)

        # Construir data de respuesta de actualización
        try:
            response_data = serializer.data.copy()
            status_code = HTTP_200_OK
        except Exception as e:
            return Response({'error': (str(e),), 'detail': (str(e),)}, status=HTTP_400_BAD_REQUEST)
        return Response(response_data, status=status_code)


class EnviarInvitacionAPIView(APIView):
    authentication_classes = [
        CustomAuthenticationValidacion,
    ]

    def post(self, request, *args, **kwargs):
        data_auth = request.auth.copy()
        data_request = self.request.data.copy()
        try:
            use_case = UsuarioInvitacionUseCase()
            # usuario, tipo_verificacion = use_case.validar_data_enviar_verificacion(data_auth, data_request)
            response = use_case.crear_invitacion_adjunto(
                data_request.get('correo'),
                tipo_verificacion=data_request.get('tipo'),
                adjunto_url=data_request.get('adjunto_url'),
                fecha_solicitud=data_request.get('fecha_inicio'),
                codigo_solicitud=data_request.get('codigo_solicitud'),
                datos_solicitante=data_request.get('datos_solicitante')
            )
            return Response(status=HTTP_200_OK, data=response.to_dict())  # type: ignore
        except Exception as e:
            return Response(
                status=HTTP_400_BAD_REQUEST,
                data={
                    'mensaje': f'Error al enviar la invitación. Detalle: {str(e)}'
                },
            )


class DescargarExcelSolicitudes(APIView):

    def get_solicitudes_list(self, request):
        query_set = Solicitud.objects.all()
        data = request.query_params

        # Filtro por IDs de solicitudes
        if data.get('solicitud_ids'):
            solicitud_ids = data.get('solicitud_ids').split(',')
            query_set = query_set.filter(pk_solicitud__in=solicitud_ids)

        # Filtros según los parámetros de usuario
        if data.get('codigo_institucion'):
            query_set = query_set.filter(usuario__codigo_institucion=data.get('codigo_institucion'))
        if data.get('codigo_region'):
            query_set = query_set.filter(usuario__codigo_region=data.get('codigo_region'))
        if data.get('tipo_documento'):
            query_set = query_set.filter(usuario__tipo_documento=data.get('tipo_documento'))
        if data.get('numero_documento'):
            query_set = query_set.filter(usuario__pk_usuario=data.get('numero_documento'))
        if data.get('username'):
            query_set = query_set.filter(usuario__username=data.get('username'))

        # Filtro de rango de fechas
        fecha_inicial = data.get('fecha_inicial', None)
        fecha_final = data.get('fecha_final', None)

        if fecha_inicial:
            fecha_inicial = datetime.strptime(fecha_inicial, '%Y-%m-%d')
            query_set = query_set.filter(fecha_solicitud__gte=fecha_inicial)
        if fecha_final:
            fecha_final = datetime.strptime(fecha_final, '%Y-%m-%d')
            query_set = query_set.filter(fecha_solicitud__lte=fecha_final)

        return query_set.order_by('-fecha_solicitud')

    def post(self, request, format=None):
        solicitudes = self.get_solicitudes_list(request)

        if not solicitudes.exists():
            data = {'mensaje': 'No se encontraron solicitudes con los parámetros proporcionados.'}
            return Response(data, status=400)

        # Crear el archivo Excel
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Solicitudes')

        # Definir formatos
        formato_encabezado = workbook.add_format({'bold': True, 'bg_color': '#00FF00', 'border': 1})
        formato_bordes = workbook.add_format({'border': 1})

        # Definir los encabezados
        encabezados = [
            'Username', 'Código Región', 'Código Institución', 'Fecha Solicitud',
            'Número Documento Solicitante', 'Nombre Solicitante', 'Apellido Paterno Solicitante',
            'Apellido Materno Solicitante', 'Descripción Motivo', 'IP Modificación'
        ]

        # Escribir los encabezados
        for col_num, encabezado in enumerate(encabezados):
            worksheet.write(0, col_num, encabezado, formato_encabezado)

        # Escribir los datos de las solicitudes
        for row_num, solicitud in enumerate(solicitudes, start=1):
            worksheet.write(row_num, 0, solicitud.usuario.username, formato_bordes)
            worksheet.write(row_num, 1, solicitud.usuario.codigo_region, formato_bordes)
            worksheet.write(row_num, 2, solicitud.usuario.codigo_institucion, formato_bordes)
            worksheet.write(row_num, 3, solicitud.fecha_solicitud.strftime('%Y-%m-%d'), formato_bordes)
            worksheet.write(row_num, 4, solicitud.numero_documento_solicitante, formato_bordes)
            worksheet.write(row_num, 5, solicitud.nombre_solicitante, formato_bordes)
            worksheet.write(row_num, 6, solicitud.apellido_paterno_solicitante, formato_bordes)
            worksheet.write(row_num, 7, solicitud.apellido_materno_solicitante, formato_bordes)
            worksheet.write(row_num, 8, solicitud.descripcion_motivo, formato_bordes)
            worksheet.write(row_num, 9, solicitud.ip_modificacion, formato_bordes)

        workbook.close()
        output.seek(0)

        # Preparar el archivo en base64
        base64_output = base64.b64encode(output.getvalue()).decode('utf-8')

        return Response({'file_base64': base64_output})


class GuardarSolicitudApiView(APIView):

    def post(self, request, *args, **kwargs):
        # Recibir todos los datos necesarios para crear la solicitud
        numero_documento = request.data.get('numero_documento')
        tipo_documento = request.data.get('tipo_documento')
        nombre_solicitante = request.data.get('nombre_solicitante')
        apellido_paterno_solicitante = request.data.get('apellido_paterno_solicitante')
        apellido_materno_solicitante = request.data.get('apellido_materno_solicitante')
        pk_motivo = request.data.get('pk_motivo')
        descripcion_motivo = request.data.get('descripcion_motivo')
        codigo_solicitud = request.data.get('numero_expediente')
        usuario_id = request.data.get('usuario_id')  # Asumo que envías el ID del usuario responsable

        # Validación de entrada
        if not numero_documento or not tipo_documento or not nombre_solicitante:
            return Response({'error': 'Faltan parámetros requeridos'}, status=HTTP_400_BAD_REQUEST)

        # Generar el código hash con SHA256 para autenticación
        fecha_consulta = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        hash_input = f"{numero_documento}{fecha_consulta}{codigo_solicitud}"
        observacion_autenticacion = hashlib.sha256(hash_input.encode()).hexdigest()
        # motivo = Motivo.objects.get(pk=pk_motivo)

        # Crear la instancia de Solicitud
        solicitud = Solicitud(
            codigo_solicitud=codigo_solicitud,
            fecha_solicitud=timezone.now().date(),
            estado=constants.ESTADO_SOLICITUD_FINALIZADA,
            motivo_id=pk_motivo,
            descripcion_motivo=descripcion_motivo,
            tipo_documento_solicitante=tipo_documento,
            numero_documento_solicitante=numero_documento,
            nombre_solicitante=nombre_solicitante,
            apellido_paterno_solicitante=apellido_paterno_solicitante,
            apellido_materno_solicitante=apellido_materno_solicitante,
            usuario_id=usuario_id,
            responsable_id=usuario_id,
            observacion_autenticacion=observacion_autenticacion
        )
        solicitud.save()

        # Generar el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(observacion_autenticacion)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        # Devolver la respuesta con el código QR en base64 y los detalles de la solicitud
        return Response({
            'qr_code_base64': img_str,
            'codigo_autenticacion': observacion_autenticacion,
            'solicitud_id': solicitud.pk_solicitud  # Devuelve el ID de la solicitud creada
        }, status=HTTP_200_OK)


class SolicitudViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Solicitud.objects.all()
    serializer_class = SolicitudSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = [
        'usuario__codigo_institucion',
        'usuario__codigo_region',
        'usuario__tipo_documento',
        'usuario__pk_usuario',
        'usuario__codigo_cargo',
        'usuario__username'
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros de fecha inicial y final
        fecha_inicial = self.request.query_params.get('fecha_inicial', None)
        fecha_final = self.request.query_params.get('fecha_final', None)

        if fecha_inicial:
            fecha_inicial = parse_date(fecha_inicial)
            queryset = queryset.filter(fecha_solicitud__gte=fecha_inicial)

        if fecha_final:
            fecha_final = parse_date(fecha_final)
            queryset = queryset.filter(fecha_solicitud__lte=fecha_final)

        return queryset
