import base64
import json
import os
from datetime import datetime

import requests
import tenacity
from django.http import HttpResponse
from django.conf import settings
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from apps.common import constants
from apps.modelsext.models import (
    Nacionalidad,
    Departamento,
    Provincia,
    Distrito,
    SiUsuario,
    SiUsuPerfil,
)
from apps.seguridad.models import Group, Parametro, User, UserGroup
from config.settings.base import (
    CODIGO_SISTEMA_WS,
    LDR_HOST_API,
    LDR_PATH_API,
    WSM_HOST_API,
    WSM_PATH_API,
    WSR_PASSWORD_API,
    WSR_PATH_API,
    WSR_RP_PATH_API,
    WSR_SEC_PATH_API,
    WSR_USERNAME_API,
)

REGASLAB_CACHE_KEY = 'regaslab-access-token'
WSR_USERNAME = WSR_USERNAME_API
WSR_PASSWORD = WSR_PASSWORD_API


class ServiciosExternos:
    @staticmethod
    def generar_basic_token(username=WSR_USERNAME, password=WSR_PASSWORD):
        if username == WSR_USERNAME_API and password == WSR_PASSWORD_API:
            token = base64.b64encode(f'{username}:{password}'.encode()).decode()
            return token
        else:
            return None

    @staticmethod
    def generar_token_cache(token_externo):
        token = cache.get(REGASLAB_CACHE_KEY)
        if token is None:
            cache.set(REGASLAB_CACHE_KEY, token_externo, 60 * 60 * 1)
        return True

    @tenacity.retry(stop=tenacity.stop_after_delay(5))
    def get_url_timeout_response(self, url, ruc=False):
        token = self.generar_basic_token()
        try:
            if ruc:
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Basic {token}',
                    'Auth': '',
                }
            else:
                headers = {'Content-Type': 'application/json'}
            response = requests.request(
                'GET', url, headers=headers, timeout=5, verify=False
            )
            return response
        except tenacity.RetryError:
            return None

    def obtener_ubigeo_nombre(self, ubigeo_nombre):
        ubigeo_list = ubigeo_nombre.split(',')
        item_list = []
        for item in ubigeo_list:
            item_list.append(item.strip())
        try:
            dep_nombre, pro_nombre, dis_nombre = item_list[0], item_list[1], item_list[2]
        except Exception:
            dep_nombre = ''
            pro_nombre = ''
            dis_nombre = ''
        return dep_nombre, pro_nombre, dis_nombre

    def update_ubigeo_migraciones(self, data, response):
        ubigeo_nombre = response.json()['datosPersonales']['ubiactual']
        dep_nombre, pro_nombre, dis_nombre = self.obtener_ubigeo_nombre(ubigeo_nombre)
        result_ubigeo = ServiciosInternos.get_ubigeo(dep_nombre, pro_nombre, dis_nombre)
        codigo_departamento = result_ubigeo.get('departamento', {}).get('codigo')
        codigo_provincia = result_ubigeo.get('provincia', {}).get('codigo')
        codigo_distrito = result_ubigeo.get('distrito', {}).get('codigo')
        data.update({
            'codigo_departamento': codigo_departamento,
            'codigo_provincia': codigo_provincia,
            'codigo_distrito': codigo_distrito,
            'descripcion_departamento': dep_nombre,
            'descripcion_provincia': pro_nombre,
            'descripcion_distrito': dis_nombre,
        })
        return data

    def verificar_identidad_reniec(self, nro_documento):
        try:
            url = fr'{LDR_HOST_API}/{LDR_PATH_API}/{nro_documento}/{CODIGO_SISTEMA_WS}'
            response = self.get_url_timeout_response(url)
            if not response.json().get('personaBean'):
                return False, 'Hubo un error con la conexión del servicio de Consultas.'
            if response.json()['personaBean'] or response.json()['codigo'] == '200':
                pais_nacimiento = None
                pais_nacimiento_str = response.json()['personaBean']['paisNac']
                pais_nacimiento_str = 'PERÚ' if pais_nacimiento_str == 'PERU' else pais_nacimiento_str
                nacionalidad = Nacionalidad.objects.filter(descripcion_nacionalidad=pais_nacimiento_str)
                if nacionalidad.exists():
                    pais_nacimiento = nacionalidad.last().codigo_nacionalidad
                result_ubigeo = ServiciosInternos.get_ubigeo_reniec(
                    response.json()['personaBean']['coddep'],
                    response.json()['personaBean']['codpro'],
                    response.json()['personaBean']['coddist']
                )
                fecha_caducidad = datetime.strptime(response.json()['personaBean']['fechaCaducidad'], '%Y%m%d').strftime('%d/%m/%Y')
                fecha_emision = datetime.strptime(response.json()['personaBean']['fechaExpedicion'], '%Y%m%d').strftime('%d/%m/%Y')
                fecha_nacimiento = datetime.strptime(response.json()['personaBean']['fechaNacimiento'], '%Y%m%d').strftime('%d/%m/%Y')
                data = {
                    'apellido_paterno': response.json()['personaBean'][
                        'apellidoPaterno'
                    ],
                    'apellido_materno': response.json()['personaBean'][
                        'apellidoMaterno'
                    ],
                    'nombres': response.json()['personaBean']['nombres'],
                    'sexo': response.json()['personaBean']['genero'],
                    'direccion': response.json()['personaBean']['direccion'],
                    'estado_civil': response.json()['personaBean']['estadoCivil'],
                    'numero_documento': nro_documento,
                    'tipo_documento': constants.TIPO_DOCUMENTO_DNI,
                    'pais_nacimiento': pais_nacimiento,
                    'codigo_departamento_ren': response.json()['personaBean']['coddep'],
                    'codigo_provincia_ren': response.json()['personaBean']['codpro'],
                    'codigo_distrito_ren': response.json()['personaBean']['coddist'],
                    'codigo_departamento': result_ubigeo.get('departamento', {}).get('codigo'),
                    'codigo_provincia': result_ubigeo.get('provincia', {}).get('codigo'),
                    'codigo_distrito': result_ubigeo.get('distrito', {}).get('codigo'),
                    'descripcion_departamento': result_ubigeo.get('departamento', {}).get('descripcion'),
                    'descripcion_provincia': result_ubigeo.get('provincia', {}).get('descripcion'),
                    'descripcion_distrito': result_ubigeo.get('distrito', {}).get('descripcion'),
                    'fecha_caducidad': fecha_caducidad,  # noqa
                    'fecha_emision': fecha_emision,  # noqa
                    'fecha_nacimiento': fecha_nacimiento,  # noqa
                    'codigo': response.json()['codigo'],
                }
                return True, data
            else:
                return False, response.json()['mensaje']
        except tenacity.RetryError:
            return (
                False,
                'Hubo un error en el tiempo de respuesta con el servicio de Consultas.',
            )
        except Exception as e:
            return False, str(e)

    def verificar_identidad_ce(self, ce):
        try:
            url = fr'{WSM_HOST_API}/{WSM_PATH_API}/ce/{ce}'
            response = self.get_url_timeout_response(url)
            if response.json().get('datosPersonales', ''):
                estado_civil_str = response.json()['datosPersonales']['estcivil']
                if estado_civil_str in ('SOLTERO', 'SOLTERO(A)'):
                    estado_civil = '1'
                elif estado_civil_str in ('CASADO', 'CASADO(A)'):
                    estado_civil = '2'
                elif estado_civil_str in ('VIUDO', 'VIUDO(A)'):
                    estado_civil = '3'
                elif estado_civil_str in ('DIVORCIADO', 'DIVORCIADO(A)'):
                    estado_civil = '4'
                else:
                    estado_civil = ''
                pais_nacimiento = ''
                pais_nacimiento_str = response.json()['datosPersonales']['painacimiento']
                nacionalidad = Nacionalidad.objects.filter(descripcion_nacionalidad=pais_nacimiento_str)
                if nacionalidad.exists():
                    pais_nacimiento = nacionalidad.last().codigo_nacionalidad
                data = {
                    'apellido_paterno': response.json()['datosPersonales'][
                        'apepaterno'
                    ],
                    'apellido_materno': response.json()['datosPersonales'][
                        'apematerno'
                    ],
                    'nombres': response.json()['datosPersonales']['nombres'],
                    'tipo_documento': constants.TIPO_DOCUMENTO_CE,
                    'numero_documento': ce,
                    'pais_nacimiento': pais_nacimiento,
                    'sexo': '2' if response.json()['datosPersonales']['genero'] == 'FEMENINO' else '1',
                    'estado_civil': estado_civil,
                    'fecha_caducidad': response.json()['datosPersonales'][
                        'feccaducidad'
                    ],
                    'fecha_nacimiento': response.json()['datosPersonales'][
                        'fecnacimiento'
                    ],
                    'direccion': response.json()['datosPersonales']['domactual'],
                    'fecha_emision': response.json()['datosPersonales']['fecemision'],
                    'codigo': response.json()['codRespuesta'],
                }
                data = self.update_ubigeo_migraciones(data, response)
                return True, data
            elif response.json().get('desRespuesta'):
                return False, response.json().get('desRespuesta')
            elif response.json().get('status') in ('404', 404):
                return False, 'No se pudo encontrar el resultado de la consulta. Contactar al administrador. Detalle: {}'.format(
                    response.json().get('error', 'Error en la consulta del servicio')
                )
            else:
                return False, str(response.json())
        except tenacity.RetryError:
            return (
                False,
                'Hubo un error en el tiempo de respuesta con el servicio de Consultas.',
            )
        except Exception as e:
            return False, str(e)

    def verificar_identidad_ptp(self, ptp):
        try:
            url = fr'{WSM_HOST_API}/{WSM_PATH_API}/ptp/{ptp}'
            response = self.get_url_timeout_response(url)
            if response.json().get('datosPersonales'):
                estado_civil_str = response.json()['personaBean']['estadoCivil']
                if estado_civil_str in ('SOLTERO', 'SOLTERO(A)'):
                    estado_civil = '1'
                elif estado_civil_str in ('CASADO', 'CASADO(A)'):
                    estado_civil = '2'
                elif estado_civil_str in ('VIUDO', 'VIUDO(A)'):
                    estado_civil = '3'
                elif estado_civil_str in ('DIVORCIADO', 'DIVORCIADO(A)'):
                    estado_civil = '4'
                else:
                    estado_civil = None
                pais_nacimiento = None
                pais_nacimiento_str = response.json()['datosPersonales']['painacimiento']
                nacionalidad = Nacionalidad.objects.filter(descripcion_nacionalidad=pais_nacimiento_str)

                if nacionalidad.exists():
                    pais_nacimiento = nacionalidad.last().codigo_nacionalidad
                data = {
                    'apellido_paterno': response.json()['datosPersonales'][
                        'apepaterno'
                    ],
                    'apellido_materno': response.json()['datosPersonales'][
                        'apematerno'
                    ],
                    'nombres': response.json()['datosPersonales']['nombres'],
                    'tipo_documento': constants.TIPO_DOCUMENTO_PTP,
                    'numero_documento': ptp,
                    'pais_nacimiento': pais_nacimiento,
                    'fecha_caducidad': response.json()['datosPersonales'][
                        'feccaducidad'
                    ],
                    'fecha_nacimiento': response.json()['datosPersonales'][
                        'fecnacimiento'
                    ],
                    'sexo': '2' if response.json()['datosPersonales']['genero'] == 'FEMENINO' else '1',
                    'estado_civil': estado_civil,
                    'fecha_emision': response.json()['datosPersonales']['fecemision'],
                    'direccion': response.json()['datosPersonales']['domactual'],
                    'codigo': response.json()['codRespuesta'],
                }
                data = self.update_ubigeo_migraciones(data, response)
                return True, data
            elif response.json().get('desRespuesta'):
                return False, response.json().get('desRespuesta')
            elif response.json().get('status') in ('404', 404):
                return False, 'No se pudo encontrar el resultado de la consulta. Contactar al administrador. Detalle: {}'.format(
                    response.json().get('error', 'Error en la consulta del servicio')
                )
            else:
                return False, str(response.json())
        except tenacity.RetryError:
            return (
                False,
                'Hubo un error en el tiempo de respuesta con el servicio de Consultas.',
            )
        except Exception as e:
            return False, str(e)

    def verificar_identidad_cpp(self, cpp):
        try:
            url = fr'{WSM_HOST_API}/{WSM_PATH_API}/cpp/{cpp}'
            response = self.get_url_timeout_response(url)
            if response.json().get('datosPersonales'):
                estado_civil_str = response.json()['personaBean']['estadoCivil']
                if estado_civil_str in ('SOLTERO', 'SOLTERO(A)'):
                    estado_civil = '1'
                elif estado_civil_str in ('CASADO', 'CASADO(A)'):
                    estado_civil = '2'
                elif estado_civil_str in ('VIUDO', 'VIUDO(A)'):
                    estado_civil = '3'
                elif estado_civil_str in ('DIVORCIADO', 'DIVORCIADO(A)'):
                    estado_civil = '4'
                else:
                    estado_civil = None
                pais_nacimiento = None
                pais_nacimiento_str = response.json()['datosPersonales']['painacimiento']
                nacionalidad = Nacionalidad.objects.filter(descripcion_nacionalidad=pais_nacimiento_str)
                if nacionalidad.exists():
                    pais_nacimiento = nacionalidad.last().codigo_nacionalidad
                data = {
                    'apellido_paterno': response.json()['datosPersonales'][
                        'apepaterno'
                    ],
                    'apellido_materno': response.json()['datosPersonales'][
                        'apematerno'
                    ],
                    'nombres': response.json()['datosPersonales']['nombres'],
                    'tipo_documento': constants.TIPO_DOCUMENTO_CPP,
                    'numero_documento': cpp,
                    'pais_nacimiento': pais_nacimiento,
                    'fecha_caducidad': response.json()['datosPersonales'][
                        'feccaducidad'
                    ],
                    'fecha_nacimiento': response.json()['datosPersonales'][
                        'fecnacimiento'
                    ],
                    'sexo': '2' if response.json()['datosPersonales']['genero'] == 'FEMENINO' else '1',
                    'estado_civil': estado_civil,
                    'fecha_emision': response.json()['datosPersonales']['fecemision'],
                    'direccion': response.json()['datosPersonales']['domactual'],
                    'codigo': response.json()['codRespuesta'],
                }
                data = self.update_ubigeo_migraciones(data, response)
                return True, data
            elif response.json().get('desRespuesta'):
                return False, response.json().get('desRespuesta')
            elif response.json().get('status') in ('404', 404):
                return False, 'No se pudo encontrar el resultado de la consulta. Contactar al administrador. Detalle: {}'.format(
                    response.json().get('error', 'Error en la consulta del servicio')
                )
            else:
                return False, str(response.json())
        except tenacity.RetryError:
            return (
                False,
                'Hubo un error en el tiempo de respuesta con el servicio de Consultas.',
            )
        except Exception as e:
            return False, str(e)

    def verificar_identidad_ruc(self, ruc):
        try:
            url = fr'{WSM_HOST_API}/{WSR_PATH_API}/{CODIGO_SISTEMA_WS}/{ruc}'
            response = self.get_url_timeout_response(url, ruc=True)
            ddp_numruc = response.json().get('ddp_numruc', '')
            if not ddp_numruc:
                return False, 'No se obtuvo resultados de la consulta'
            if response.json() and ddp_numruc:
                es_activo = (
                    constants.SI_CHAR_BINARY
                    if bool(response.json()['esActivo'])
                    else constants.NO_CHAR_BINARY
                )
                es_habido = (
                    constants.SI_CHAR_BINARY
                    if bool(response.json()['esHabido'])
                    else constants.NO_CHAR_BINARY
                )
                nombre_via = response.json()['ddp_nomvia'].strip()
                numero_via = response.json()['ddp_numer1'].strip()
                nombre_distrito = response.json()['desc_dist'].strip()
                direccion = '{} {}, {}'.format(nombre_via, numero_via, nombre_distrito)
                codigo_ubigeo = response.json()['ddp_ubigeo'].strip()
                codigo_departamento = codigo_ubigeo[0:2]
                codigo_provincia = codigo_ubigeo[2:4]
                codigo_distrito = codigo_ubigeo[4:6]
                data = {
                    'razon_social': response.json()['ddp_nombre'].strip(),
                    'nombres': response.json()['ddp_nombre'].strip(),
                    'es_activo': es_activo,  # noqa
                    'es_habido': es_habido,  # noqa
                    'ruc': ruc,
                    'tipo_documento': constants.TIPO_DOCUMENTO_RUC,
                    'tipo': response.json()['ddp_identi'],
                    'estado': response.json()['desc_estado'].strip(),
                    'flag': response.json()['desc_flag22'].strip(),
                    'descripcion_ciiu': response.json()['desc_ciiu'].strip(),
                    'codigo_ubigeo': codigo_ubigeo,
                    'codigo_departamento': codigo_departamento,
                    'codigo_provincia': codigo_provincia,
                    'codigo_distrito': codigo_distrito,
                    'descripcion_departamento': response.json()['desc_dep'].strip(),
                    'descripcion_provincia': response.json()['desc_prov'].strip(),
                    'descripcion_distrito': response.json()['desc_dist'].strip(),
                    'direccion': direccion,
                    'codigo_ciiu': response.json()['ddp_ciiu'].strip(),
                    'codigo': '',
                }
                return True, data
            else:
                return False, 'El número de RUC buscado no existe'
        except tenacity.RetryError:
            return (
                False,
                'Hubo un error en el tiempo de respuesta con el servicio de Consultas.',
            )
        except Exception as e:
            return False, str(e)

    def verificar_datos_secundarios_ruc(self, ruc):
        try:
            url = fr'{WSM_HOST_API}/{WSR_SEC_PATH_API}/{CODIGO_SISTEMA_WS}/{ruc}'
            response = self.get_url_timeout_response(url, ruc=True)
            ddp_numruc = response.json().get('dds_numruc', '')
            if not ddp_numruc:
                return False, 'No se obtuvo resultados de la consulta'
            if response.json() and ddp_numruc:
                data = {
                    'ruc': ruc,
                    'ficha_ruc': response.json()['dds_ficha'].strip(),
                    'fecha_inicio': datetime.strptime(
                        response.json()['dds_inicio'], '%d/%m/%Y'
                    ).strftime('%d/%m/%Y'),
                    'fecha_constitucion': datetime.strptime(
                        response.json()['dds_consti'], '%d/%m/%Y'
                    ).strftime('%d/%m/%Y'),
                }
                return True, data
            else:
                return False, 'El número de RUC buscado no existe'
        except tenacity.RetryError:
            return (
                False,
                'Hubo un error en el tiempo de respuesta con el servicio de Consultas.',
            )
        except Exception as e:
            return False, str(e)

    def verificar_representate_legal_ruc(self, ruc, tipo_documento, numero_documento):
        try:
            url = fr'{WSM_HOST_API}/{WSR_RP_PATH_API}/{CODIGO_SISTEMA_WS}/{ruc}'
            response = self.get_url_timeout_response(url, ruc=True)
            tipo_doc_eq = constants.TIPO_DOCUMENTO_EQ.get(tipo_documento)
            mensaje = 'Hubo un error de conexión con el servicio de Consultas'
            encontrado = False
            if response.json():
                mensaje = 'No se encontró al representante legal con Nro. documento {} para el RUC {}'.format(
                    numero_documento, ruc
                )
                valor = False
                if type(response.json()) != list:
                    if response.json().get('code', None) is None:
                        return valor, response.json().get('mensaje', None).title()
                nombre_completo = ''
                codigo_cargo = ''
                for data_rp in response.json():
                    if (
                        data_rp.get('rso_docide').rstrip() == tipo_doc_eq
                        and numero_documento == data_rp.get('rso_nrodoc').rstrip()
                    ):
                        encontrado = True
                        mensaje = 'El representante legal con Nro. documento {} sí pertenece al RUC {}'.format(
                            numero_documento, ruc
                        )
                        valor = True
                        nombre_completo = data_rp['rso_nombre'].split()
                        codigo_cargo = data_rp['cod_cargo']
                        break
                if not encontrado:
                    return False, mensaje

                data = {
                    'ruc': ruc,
                    'tipo_documento': tipo_documento,
                    'nombres': ' '.join(nombre_completo[2:]),
                    'apellido_paterno': nombre_completo[0],
                    'apellido_materno': nombre_completo[1],
                    'numero_documento': numero_documento,
                    'codigo_cargo': codigo_cargo,
                    'mensaje': mensaje,
                    'encontrado': encontrado,
                }
                return valor, data
            else:
                return False, mensaje
        except tenacity.RetryError:
            return (
                False,
                'Hubo un error en el tiempo de respuesta con el servicio de Consultas.',
            )
        except Exception as e:
            return False, str(e)

    def consultar_usuario(self, tipo_usuario, tipo_documento, username):
        if tipo_usuario == constants.TIPO_USUARIO_PERSONA:
            if tipo_documento == constants.TIPO_DOCUMENTO_DNI:
                results = self.verificar_identidad_reniec(username)
            elif tipo_documento == constants.TIPO_DOCUMENTO_CE:
                results = self.verificar_identidad_ce(username)
            elif tipo_documento == constants.TIPO_DOCUMENTO_PTP:
                results = self.verificar_identidad_ptp(username)
            elif tipo_documento == constants.TIPO_DOCUMENTO_CPP:
                results = self.verificar_identidad_cpp(username)
            elif tipo_documento == constants.TIPO_DOCUMENTO_RUC:
                results = self.verificar_identidad_ruc(username)
            elif tipo_documento in (
                constants.TIPO_DOCUMENTO_PASAPORTE,
                constants.TIPO_DOCUMENTO_CSR,
                constants.TIPO_DOCUMENTO_CEDULA_IDENTIDAD,
            ):
                results = (False, tipo_documento)
            else:
                results = (False, constants.TIPO_DOCUMENTO_NA)
        elif tipo_usuario == constants.TIPO_USUARIO_EMPRESA:
            results = self.verificar_identidad_ruc(username)
        else:
            results = (False, constants.TIPO_USUARIO_NA)
        return results


class ServiciosInternos:
    @staticmethod
    def get_ubigeo(codigo_departamento, codigo_provincia=None, codigo_distrito=None):
        values = {}
        if not codigo_departamento:
            return values
        departamento = Departamento.objects.filter(
            Q(codigo_departamento=codigo_departamento) |
            Q(descripcion_departamento__icontains=codigo_departamento)
        )

        if departamento.exists():
            departamento = departamento.last()
            codigo_departamento = departamento.codigo_departamento
            if codigo_provincia:
                provincia = Provincia.objects.filter(
                    Q(codigo_departamento=codigo_departamento),
                    Q(codigo_provincia=codigo_provincia) |
                    Q(descripcion_provincia__icontains=codigo_provincia)
                )
            else:
                provincia = Provincia.objects.none()
            if provincia.exists():
                provincia = provincia.last()
                codigo_provincia = provincia.codigo_provincia
                if codigo_distrito:
                    distrito = Distrito.objects.filter(
                        Q(codigo_departamento=codigo_departamento),
                        Q(codigo_provincia=codigo_provincia),
                        Q(codigo_distrito=codigo_distrito) |
                        Q(descripcion_distrito__icontains=codigo_distrito)
                    )
                else:
                    distrito = Distrito.objects.none()
                if distrito.exists():
                    distrito = distrito.last()
                    codigo_distrito = distrito.codigo_distrito
                else:
                    distrito = None
            else:
                provincia = None
                distrito = None
        else:
            departamento = None
            provincia = None
            distrito = None

        if departamento:
            values.update({
                'departamento': {
                    'codigo': codigo_departamento,
                    'instance': departamento,
                    'descripcion': departamento.descripcion_departamento
                }
            })
        if provincia:
            values.update({
                'provincia': {
                    'codigo': codigo_provincia,
                    'instance': provincia,
                    'descripcion': provincia.descripcion_provincia
                }
            })
        if distrito:
            values.update({
                'distrito': {
                    'codigo': codigo_distrito,
                    'instance': distrito,
                    'descripcion': distrito.descripcion_distrito
                }
            })

        return values

    @staticmethod
    def get_ubigeo_reniec(codigo_departamento, codigo_provincia=None, codigo_distrito=None):
        values = {}
        if not codigo_departamento:
            return values
        departamento = Departamento.objects.filter(
            Q(codigo_departamento_ren=codigo_departamento) |
            Q(descripcion_departamento__icontains=codigo_departamento)
        )

        if departamento.exists():
            departamento = departamento.last()
            codigo_departamento = departamento.codigo_departamento
            if codigo_provincia:
                provincia = Provincia.objects.filter(
                    Q(codigo_departamento=codigo_departamento),
                    Q(codigo_provincia_ren=codigo_provincia) |
                    Q(descripcion_provincia__icontains=codigo_provincia)
                )
            else:
                provincia = Provincia.objects.none()
            if provincia.exists():
                provincia = provincia.last()
                codigo_provincia = provincia.codigo_provincia
                if codigo_distrito:
                    distrito = Distrito.objects.filter(
                        Q(codigo_departamento=codigo_departamento),
                        Q(codigo_provincia=codigo_provincia),
                        Q(codigo_distrito_ren=codigo_distrito) |
                        Q(descripcion_distrito__icontains=codigo_distrito)
                    )
                else:
                    distrito = Distrito.objects.none()
                if distrito.exists():
                    distrito = distrito.last()
                    codigo_distrito = distrito.codigo_distrito
                else:
                    distrito = None
            else:
                provincia = None
                distrito = None
        else:
            departamento = None
            provincia = None
            distrito = None

        if departamento:
            values.update({
                'departamento': {
                    'codigo': codigo_departamento,
                    'instance': departamento,
                    'descripcion': departamento.descripcion_departamento
                }
            })
        if provincia:
            values.update({
                'provincia': {
                    'codigo': codigo_provincia,
                    'instance': provincia,
                    'descripcion': provincia.descripcion_provincia
                }
            })
        if distrito:
            values.update({
                'distrito': {
                    'codigo': codigo_distrito,
                    'instance': distrito,
                    'descripcion': distrito.descripcion_distrito
                }
            })

        return values

    @staticmethod
    def get_perfil_usuario(pk_usuario):
        user = User.objects.filter(pk_usuario=pk_usuario)
        if user.exists() and user.last().password:
            pass
        usuario = SiUsuario.objects.filter(codigo_personal=pk_usuario)
        if not usuario.exists():
            return None, None
        codigo_usuario = usuario.last().codigo_usuario
        usuario_perfiles = SiUsuPerfil.objects.filter(
            codigo_usuario=codigo_usuario
        ).order_by('-codigo_perfil')
        if not usuario_perfiles.exists():
            return None, None
        # Solo 1 perfil por usuario
        pk_grupo = None
        nombre_grupo = None
        for usuario_perfil in usuario_perfiles:
            grupo = Group.objects.filter(pk_grupo=usuario_perfil.codigo_perfil)
            if grupo.exists():
                pk_grupo = grupo.first().pk_grupo
                nombre_grupo = grupo.first().nombre
                break
            else:
                continue
        return pk_grupo, nombre_grupo.lower()

    @staticmethod
    def get_usuario_token(request):
        token = request.META.get('HTTP_AUTHORIZATION', '')
        if not token:
            return None
        if token.find('Bearer ') >= 0:
            token = token.replace('Bearer ', '')
        parametro = Parametro.objects.filter(valor=token)
        pk_usuario = parametro.first().codigo if parametro.exists() else None
        user = User.objects.filter(Q(pk_usuario=pk_usuario) | Q(username=pk_usuario))
        return user.first() if user.exists() else None

    @staticmethod
    def get_grupo_usuario(pk_usuario):
        queryset = UserGroup.objects.filter(usuario__pk_usuario=pk_usuario)
        menu_list = []
        pk_grupo = None
        menu_usuario = False
        for grupo_usuario in queryset:
            pk_grupo = grupo_usuario.grupo.pk_grupo
            menu_list.append(grupo_usuario.menu.pk_menu)
        if menu_list:
            menu_usuario = True
        return menu_usuario, menu_list, pk_grupo

    @staticmethod
    def matches(raw_password, encoded_password):
        return raw_password == encoded_password

    @staticmethod
    def getAscii(valor):
        j = ord(valor[0])
        return j

    @staticmethod
    def total_segundos():
        from datetime import datetime

        now = datetime.now()
        cant = (now.hour * 3600) + (now.minute * 60) + now.second
        return cant

    @staticmethod
    def completa_codigo(codigo, tamanio):
        ncodigo = ''
        if len(codigo) >= tamanio:
            for i in range(tamanio):
                ncodigo += codigo[i]
        else:
            for i in range(tamanio - len(codigo)):
                ncodigo += '0'
            ncodigo += codigo
        return ncodigo

    @staticmethod
    def ascii_to_string(i):
        return chr(i)

    def encode(self, username, password):
        li_Cont = 0
        li_Magia = 0
        li_Long = 0
        li_Char = 0
        li_Ascii1 = 0
        li_Ascii2 = 0
        li_Signo = 0
        ls_Login = ''
        ls_Clave = ''
        ls_Cripto = ''
        ls_Result = ''
        pLogin = username
        pClave = password

        if len(pLogin.strip()) > len(pClave.strip()):
            ls_Login = pLogin
            temp = pClave + pClave + pClave + pClave
            ls_Clave = temp[: len(ls_Login)]
        else:
            ls_Clave = pClave
            temp = pLogin + pLogin + pLogin + pLogin
            ls_Login = temp[: len(ls_Clave)]

        li_Long = len(ls_Login)

        for li_Cont in range(li_Long):
            li_Magia = (
                (li_Magia + self.getAscii(ls_Login[li_Cont : li_Cont + 1])) % 255
            ) + 1
        li_Magia = ((li_Magia + self.total_segundos()) % 255) + 1

        for li_Cont in range(li_Long):
            li_Ascii1 = self.getAscii(ls_Login[li_Cont : li_Cont + 1])
            li_Ascii2 = self.getAscii(ls_Clave[li_Cont : li_Cont + 1])
            li_Char = li_Ascii2 + li_Ascii1 + li_Magia
            ls_Cripto = ls_Cripto + self.completa_codigo(str(li_Char), 3)
        ls_Cripto = (
            ls_Cripto
            + self.completa_codigo(str(li_Magia), 3)
            + self.completa_codigo(str(len(pClave)), 2)
        )

        for li_Cont in range(1, len(ls_Cripto) + 1):
            if li_Cont % 2 == 0:
                li_Signo = 1
            else:
                li_Signo = -1
            li_Char = self.getAscii(ls_Cripto[li_Cont - 1 : li_Cont])
            ls_Result = ls_Result + self.ascii_to_string(li_Char + (li_Long * li_Signo))

        return ls_Result

    def get_siusuario_password(self, pk_usuario):
        si_usuario = SiUsuario.objects.filter(codigo_personal=pk_usuario)
        decoded_password = None
        if si_usuario.exists():
            password = si_usuario.first().password_usuario
            username = si_usuario.first().codigo_usuario
            decoded_password = self.decode(username, password)
        return decoded_password

    def decode(self, username, password):
        li_Cont = 0
        li_Magia = 0
        li_Long = 0
        li_Ascii1 = 0
        li_Ascii2 = 0
        li_Char = 0
        li_Signo = 0
        ls_Login = ''
        ls_Cripto = ''
        pLogin = username
        pCripto = password
        li_Long = (len(pCripto) - 5) // 3
        for li_Cont in range(1, len(pCripto) + 1):
            if (li_Cont % 2) == 0:
                li_Signo = 1
            else:
                li_Signo = -1
            li_Char = self.getAscii(pCripto[li_Cont - 1 : li_Cont])
            ls_Cripto += self.ascii_to_string(li_Char - (li_Long * li_Signo))

        li_Long = int(ls_Cripto[len(ls_Cripto) - 2 : len(ls_Cripto)])
        pLogin = pLogin + pLogin + pLogin + pLogin
        pLogin = pLogin[0:li_Long]

        li_Magia = int(ls_Cripto[len(ls_Cripto) - 5 : len(ls_Cripto) - 2])

        for li_Cont in range(1, li_Long + 1):
            li_Ascii1 = self.getAscii(pLogin[li_Cont - 1 : li_Cont])
            li_Ascii2 = int(ls_Cripto[(li_Cont * 3) - 3 : li_Cont * 3])
            ls_Login += self.ascii_to_string(li_Ascii2 - li_Ascii1 - li_Magia)
        return ls_Login

    @staticmethod
    def get_mensaje(mensaje, valido=True, estado='N/A', code_status=None, datos={}):
        data = {'mensaje': f'{mensaje}', 'estado': estado}
        json.dumps(data, cls=DjangoJSONEncoder)
        if valido:
            status = HTTP_200_OK
        else:
            if code_status == 404:
                status = HTTP_404_NOT_FOUND
            else:
                status = HTTP_400_BAD_REQUEST
        if datos:
            data.update({'datos': datos})
        return Response(data, status=status)

    @staticmethod
    def get_fecha_limite_solicitudes(pd, holidays, notificacion_grupo, start_date_solicitud=datetime.now()):
        # Obtener el número de días hábiles (días laborales) a partir del plazo
        plazo_dias = notificacion_grupo.get('plazo_dias')
        start_date = pd.to_datetime(start_date_solicitud).date()  # Fecha de la solicitud

        # Obtener los días festivos de la librería holidays para Perú
        feriados_peru_lib = holidays.Peru(years=int(constants.ANHO_FISCAL))
        feriados_peru_lib_dates = list(
            feriados_peru_lib.keys()
        )  # Obtener las fechas de los días festivos

        # Obtener los días festivos de la API
        api_url = 'https://date.nager.at/api/v3/publicholidays/{}/{}'.format(
            constants.ANHO_FISCAL, constants.CODIGO_PAIS
        )

        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Lanzar excepción si hay un error en la respuesta HTTP
            feriados_peru_api = response.json()
            feriados_peru_api_dates = [
                pd.to_datetime(h['date']).date() for h in feriados_peru_api
            ]  # Obtener las fechas de los días festivos
        except requests.exceptions.RequestException as e:
            print('Error en la consulta al API:', str(e))
            feriados_peru_api_dates = []  # En caso de error, establecer una lista vacía

        # Combinar las fechas de los días festivos de la librería y la API
        feriados_peru_combined_dates = feriados_peru_lib_dates + feriados_peru_api_dates

        # Crear un objeto pd.offsets.CustomBusinessDay con los días festivos combinados
        calendario_peru = pd.offsets.CustomBusinessDay(
            holidays=feriados_peru_combined_dates
        )
        # Calcular fecha límite sumando los días hábiles considerando los días no laborales de Perú
        end_date = start_date + plazo_dias * calendario_peru

        # Ajustar fecha límite al siguiente día hábil si es necesario
        fecha_limite = end_date + pd.offsets.BDay(0)
        fecha_limite = fecha_limite.replace(
            hour=16,
            minute=30,
            second=0,
        )
        return fecha_limite


def get_nombres_apellidos_por_usuario(usuario):
    resultados = ServiciosExternos.consultar_usuario(
        ServiciosExternos(),
        tipo_usuario=constants.SI_CHAR_BINARY,
        tipo_documento=usuario.tipo_documento,
        username=usuario.pk_usuario,
    )
    nombres_apellidos = ''
    if resultados[0]:
        nombres_apellidos = f"{resultados[1].get('nombres')} {resultados[1].get('apellido_paterno')} {resultados[1].get('apellido_materno')}"  # noqa
    return nombres_apellidos


def get_nombres_apellidos_separados_por_usuario(tipo_documento, numero_documento):
    resultados = ServiciosExternos.consultar_usuario(
        ServiciosExternos(),
        tipo_usuario=constants.SI_CHAR_BINARY,
        tipo_documento=tipo_documento,
        username=numero_documento,
    )
    apellido_paterno = ''
    apellido_materno = ''
    nombres = ''
    if resultados[0]:
        apellido_paterno = resultados[1].get('apellido_paterno')
        apellido_materno = resultados[1].get('apellido_materno')
        nombres = resultados[1].get('nombres')
    return {
        'apellido_paterno': apellido_paterno,
        'apellido_materno': apellido_materno,
        'nombres': nombres,
    }


def convert_datetime_to_str(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()


def get_ubigeo_por_usuario(tipo_documento, numero_documento):
    resultados = ServiciosExternos.consultar_usuario(
        ServiciosExternos(),
        tipo_usuario=constants.SI_CHAR_BINARY,
        tipo_documento=tipo_documento,
        username=numero_documento,
    )
    cod_departamento = ''
    cod_provincia = ''
    cod_distrito = ''
    if resultados[0]:
        cod_departamento = resultados[1].get('codigo_departamento_ren')
        cod_provincia = resultados[1].get('codigo_provincia_ren')
        cod_distrito = resultados[1].get('codigo_distrito_ren')
    try:
        dep = Departamento.objects.filter(
            codigo_departamento_ren=cod_departamento
        ).first()
        prov = Provincia.objects.filter(
            codigo_departamento_ren=cod_departamento, codigo_provincia_ren=cod_provincia
        ).first()
        dist = Distrito.objects.filter(
            codigo_distrito_ren=cod_distrito,
            codigo_departamento_ren=cod_departamento,
            codigo_provincia_ren=cod_distrito,
        ).first()
        return {
            'departamento': dep,
            'provincia': prov,
            'distrito': dist,
        }
    except Exception as e:  # noqa
        return {
            'departamento': None,
            'provincia': None,
            'distrito': None,
        }


def get_ubigeo_por_usuario_evaluadores(evaluador):
    try:
        dep = Departamento.objects.filter(
            descripcion_departamento__icontains=evaluador.departamento
        ).first()
        prov = Provincia.objects.filter(
            descripcion_provincia__icontains=evaluador.provincia
        ).first()
        dist = Distrito.objects.filter(
            descripcion_distrito__icontains=evaluador.distrito
        ).first()
        return {
            'departamento': dep,
            'provincia': prov,
            'distrito': dist,
        }
    except Exception as e:  # noqa
        return {
            'departamento': None,
            'provincia': None,
            'distrito': None,
        }


def get_ubigeo_por_usuario_centros(centros):
    try:
        dep = Departamento.objects.filter(
            descripcion_departamento__icontains=centros.departamento
        ).first()
        dist = Distrito.objects.filter(
            descripcion_distrito__icontains=centros.distrito_sede_central
        ).first()
        return {
            'departamento': dep,
            'provincia': None,
            'distrito': dist,
        }
    except Exception as e:  # noqa
        return {
            'departamento': None,
            'provincia': None,
            'distrito': None,
        }


def pdf_to_base64(url_archivo):
    try:
        url_archivo_absoluta = os.path.join(settings.BASE_DIR, url_archivo[1:])
        with open(url_archivo_absoluta, 'rb') as file:
            pdf_content = file.read()
            base64_content = base64.b64encode(pdf_content).decode('utf-8')
            return base64_content
    except Exception as e:  # noqa:
        return ''


def get_url_archivo_absoluta(url_archivo):
    try:
        url_archivo_absoluta = os.path.join(settings.BASE_DIR, url_archivo[1:])
        with open(url_archivo_absoluta, 'rb') as archivo:
            response = HttpResponse(archivo.read(), content_type='application/octet-stream')
            nombre_archivo = os.path.basename(url_archivo_absoluta)
            response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
            return response
    except Exception as e:  # noqa:
        return str(e)
