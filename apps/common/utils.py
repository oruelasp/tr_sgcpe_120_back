import requests
from dateutil.rrule import DAILY, rrule, MO, TU, WE, TH, FR

from django.core.cache import cache
from django.db import connection, DatabaseError, connections
from rest_framework.exceptions import APIException

from rest_framework_json_api.pagination import PageNumberPagination
from rest_framework import pagination
from unidecode import unidecode

from apps.common import constants
from apps.programacion.api.serializers import RazonSocialSerializer, QuintaCategoriaSerializer
from config.settings.base import (
    SE_HOST_API,
    SE_HOST_API_SE,
    SE_ID_APLICACION,
    SE_TOKEN_API,
    SE_TOKEN_API_SE,
)

REGAS_CACHE_KEY = 'regas-access-token'


class CustomPagination(pagination.LimitOffsetPagination):
    default_limit = 30
    limit_query_param = 'l'
    offset_query_param = 'o'
    max_limit = 50


def working_daterange(start_date, end_date):
    date_range = rrule(DAILY, dtstart=start_date, until=end_date, byweekday=(MO, TU, WE, TH, FR))
    return date_range


def calendar_daterange(start_date, end_date):
    return rrule(DAILY, dtstart=start_date, until=end_date, byweekday=(MO, TU, WE, TH, FR))


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class ServiciosExternos:

    def verificar_identidad(self, token):
        try:
            data = """{"token": "{token}"}"""
            data = data.replace('{token}', token)
            url = fr'{SE_HOST_API}/Crypto/Decrypt'
            headers = {'ApiKey': SE_TOKEN_API, 'Content-Type': 'application/json'}
            response = requests.request('POST', url, headers=headers, data=data)
            if response.json()['Success']:
                return True, response.json()
            else:
                return False, response.json()

        except Exception as e:
            return False, str(e)

    def generar_token_cache(self, token_externo):
        token = cache.get(REGAS_CACHE_KEY)
        if token is None:
            # REGAS token expires after 2 hours, we'll use 1 hour instead
            token = self.verificar_identidad(token_externo)
            cache.set(REGAS_CACHE_KEY, token, 60 * 60 * 1)
        return True

    def consulta_dni(self, dni):
        try:
            url = fr'{SE_HOST_API_SE}/api/Reniec/buscar?dni={dni}'
            headers = {'ApiKey': SE_TOKEN_API_SE, 'Content-Type': 'application/json'}
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.json()['Data']:
                return True, response.json()['Data']
            else:
                return False, response.json()['Messages']
        except Exception as e:
            return False, str(e)

    def consulta_ce(self, ce):
        try:
            url = fr'{SE_HOST_API_SE}/api/Migracion/buscar?numdoc={ce}'
            headers = {'ApiKey': SE_TOKEN_API_SE, 'Content-Type': 'application/json'}
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.json()['Data']:
                data = {
                    'apellidoPaterno': response.json()['Data']['apellidoPaterno'],
                    'apellidoMaterno': response.json()['Data']['apellidoMaterno'],
                    'nombres': response.json()['Data']['nombre'],
                    'numero_documento': ce,
                }
                return True, data
            else:
                return False, response.json()['Messages']
        except Exception as e:
            return False, str(e)

    def consulta_ruc(self, ruc):
        try:
            # import pdb; pdb.set_trace()
            url = fr'{SE_HOST_API_SE}/api/Sunat/buscar?ruc={ruc}'
            headers = {'ApiKey': SE_TOKEN_API_SE, 'Content-Type': 'application/json'}
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.json()['Data']:
                # TODO: Error en el modelo
                # distrito = (
                #     MaeDistrito.objects.using('catalogos_externos')
                #     .filter(
                #         codigo_departamento=response.json()['Data'][
                #             'codigoDepartamento'
                #         ],
                #         codigo_provincia=response.json()['Data']['codigoProvincia'],
                #         codigo_distrito=response.json()['Data']['codigoDistrito'],
                #     )
                #     .last()
                # )
                data_json = response.json()['Data']
                data = {
                    'razonSocial': data_json['razonSocial'],
                    'domicilio': data_json['domicilio'],
                    'ubigeo': data_json['ubigeo'],
                    'codigoDepartamento': data_json['codigoDepartamento'],
                    'codigoProvincia': data_json['codigoProvincia'],
                    'codigoDistrito': data_json['codigoDistrito'],
                    'ubigeo_descripcion': f'{data_json["codigoDepartamento"]}{data_json["codigoProvincia"]}{data_json["codigoDistrito"]}',
                    'numero_documento': ruc,
                }
                return True, data
            else:
                return False, response.json()['Messages']
        except Exception as e:
            return False, str(e)

    def login_administrado(self, usuario, clave):
        try:
            data = """{
            "username": "{usuario}",
            "clave": "{clave}"
            }"""
            data = data.replace('{usuario}', usuario)
            data = data.replace('{clave}', clave)
            url = fr'{SE_HOST_API_SE}/api/ProduceVirtual/autenticar/Administrado'
            headers = {'ApiKey': SE_TOKEN_API_SE, 'Content-Type': 'application/json'}
            response = requests.request(
                'POST', url, headers=headers, data=data, verify=False
            )
            if response.json()['Success']:
                return True, 'Logueo realizado con éxito'
            else:
                return False, 'Verifique sus datos de conexión'
        except Exception as e:
            return False, str(e)

    def login_funcionario(self, usuario, clave):
        try:
            data = """{
            "username": "{usuario}@produce.gob.pe",
            "clave": "{clave}"
            }"""
            data = data.replace('{usuario}', usuario)
            data = data.replace('{clave}', clave)
            url = fr'{SE_HOST_API_SE}/api/ProduceVirtual/autenticar/Funcionario'
            headers = {'ApiKey': SE_TOKEN_API_SE, 'Content-Type': 'application/json'}
            response = requests.request(
                'POST', url, headers=headers, data=data, verify=False
            )
            if response.json()['Success']:
                return True, 'Logueo realizado con éxito'
            else:
                return False, 'Verifique sus datos de conexión'
        except Exception as e:
            return False, str(e)

    def crear_cuenta(self, nro_doc, email, celular, id_rol, clave):
        try:
            data = """{
                "dni": "{dni}",
                "email": "{email}",
                "phonenumber": "{celular}",
                "userregister": "{usuario}",
                "id_rol": "{rol}",
                "asunto_mensaje": "Registro de cuenta",
                "id_aplicacion": "{aplicacion}",
                "ingresarclave": "{clave}"
            }"""

            data = data.replace('{dni}', nro_doc)
            data = data.replace('{email}', email)
            data = data.replace('{celular}', celular)
            data = data.replace('{usuario}', nro_doc)
            data = data.replace('{rol}', str(id_rol))
            data = data.replace('{aplicacion}', str(SE_ID_APLICACION))
            data = data.replace('{clave}', clave)

            url = fr'{SE_HOST_API_SE}/api/ProduceVirtual/registrar/CuentaNatural'
            headers = {'ApiKey': SE_TOKEN_API_SE, 'Content-Type': 'application/json'}
            response = requests.request(
                'POST', url, headers=headers, data=data, verify=False
            )
            if response.json()['Success']:
                return True, 'Registro realizado con éxito'
            else:
                return False, response.json()['Messages']

        except Exception as e:
            return False, str(e)

    def consultar_administrado(self, usuario):
        try:
            url = fr'{SE_HOST_API_SE}/api/ProduceVirtual/consultar/Administrado?username={usuario}'
            headers = {'ApiKey': SE_TOKEN_API_SE, 'Content-Type': 'application/json'}
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.json()['Data']:
                return True, response.json()['Data']['Id']
            else:
                return False, 'No existe el usuario'
        except Exception as e:
            return False, str(e)

    def cambiar_clave(self, usuario, clave):
        try:
            data = """{
                "username": "{usuario}",
                "clave": "{clave}"
            }"""
            data = data.replace('{usuario}', usuario)
            data = data.replace('{clave}', clave)

            url = fr'{SE_HOST_API_SE}/api/ProduceVirtual/actualizar/ContrasenaAdministrado'
            headers = {'ApiKey': SE_TOKEN_API_SE, 'Content-Type': 'application/json'}
            response = requests.request(
                'POST', url, headers=headers, data=data, verify=False
            )
            if response.json()['Success']:
                return True, 'Registro realizado con éxito'
            else:
                return False, response.json()['Messages']

        except Exception as e:
            return False, str(e)

    def crear_persona(  # noqa CCR001
        self,
        nro_doc,
        nombres,
        apellidos,
        email,
        celular,
        razon_social,
        direccion,
        dep,
        pro,
        dist,
    ):
        """
        Devuelve
            True, ID de la persona creada
            False, descripcion del error
        """
        try:
            data = """{
            "codigo_departamento": "{dep}",
            "codigo_provincia": "{pro}",
            "codigo_distrito": "{dist}",
            "nombres": "{nombres}",
            "apellidos": "{apellidos}",
            "numero_documento": "{nro_doc}",
            "id_tipo_documento": 8,
            "id_tipo_persona": 1,
            "usuario_registro": "usr_pi_audit",
            "telefono": "{celular}",
            "email": "{email}",
            "celular": "{celular}",
            "razon_social": "{razon_social}",
            "direccion": "{direccion}"
            }"""

            data = data.replace('{dep}', dep)
            data = data.replace('{pro}', pro)
            data = data.replace('{dist}', dist)
            data = data.replace('{nombres}', nombres)
            data = data.replace('{apellidos}', apellidos)
            data = data.replace('{nro_doc}', nro_doc)
            data = data.replace('{email}', email)
            data = data.replace('{celular}', celular)
            data = data.replace('{razon_social}', razon_social)
            data = data.replace('{direccion}', direccion)

            url = fr'{SE_HOST_API_SE}/api/persona/registrar'
            headers = {'ApiKey': SE_TOKEN_API_SE, 'Content-Type': 'application/json'}
            response = requests.request(
                'POST', url, headers=headers, data=data, verify=False
            )
            if response.json()['Success']:
                return True, response.json()['Value']
            else:
                return False, response.json()['Messages']

        except Exception as e:
            return False, str(e)

    def actualizar_persona(  # noqa CCR001
        self,
        id_persona,
        nro_doc,
        nombres,
        apellidos,
        email,
        celular,
        razon_social,
        direccion,
        dep,
        pro,
        dist,
    ):
        """
        Devuelve
            True, ID de la persona actualizada
            False, descripcion del error
        """
        try:
            data = """{
            "codigo_departamento": "{dep}",
            "codigo_provincia": "{pro}",
            "codigo_distrito": "{dist}",
            "nombres": "{nombres}",
            "apellidos": "{apellidos}",
            "numero_documento": "{nro_doc}",
            "id_tipo_documento": 8,
            "id_tipo_persona": 1,
            "usuario_registro": "usr_pi_audit",
            "telefono": "{celular}",
            "email": "{email}",
            "celular": "{celular}",
            "razon_social": "{razon_social}",
            "direccion": "{direccion}",
            "id_persona": "{id_persona}"
            }"""
            data = data.replace('{dep}', dep)
            data = data.replace('{pro}', pro)
            data = data.replace('{dist}', dist)
            data = data.replace('{nombres}', nombres)
            data = data.replace('{apellidos}', apellidos)
            data = data.replace('{nro_doc}', nro_doc)
            data = data.replace('{email}', email)
            data = data.replace('{celular}', celular)
            data = data.replace('{razon_social}', razon_social)
            data = data.replace('{direccion}', direccion)
            data = data.replace('{id_persona}', str(id_persona))

            url = fr'{SE_HOST_API_SE}/api/persona/actualizar'
            headers = {'ApiKey': SE_TOKEN_API_SE, 'Content-Type': 'application/json'}
            response = requests.request(
                'POST', url, headers=headers, data=data, verify=False
            )
            if response.json()['Success']:
                return True, response.json()['Value']
            else:
                return False, response.json()['Messages']

        except Exception as e:
            return False, str(e)


def convertir_parametro_insensible(a):
    if type(a) == str:
        # a = unidecode(a)
        return a.upper()
    return a


def get_consulta_directa(data):
    pv_nrodocide = data.get('numero_documento')
    pv_perioinic = data.get("fecha_inicio")
    pv_periofin = data.get("fecha_fin")
    consolidado = data.get("consolidado")
    pv_ruc = data.get("numero_ruc")
    tipo_categoria =data.get("tipo_categoria")

    try:
        if consolidado == constants.NO_CHAR_BINARY and tipo_categoria == constants.CATEGORIA_5TA:
            print('entre al primer if')
            # and data.get(
            #     'tipo_categoria') == constants.QUINTA_CATEGORIA):
            with connections['planillas'].cursor() as cursor:
                cursor.execute("""
                    select distinct
                                    per.v_apepater as v_apepater,
                                    per.v_apemater as v_apemater,per.v_nombres as v_nombres,
                                    e.c_numruc as v_numdocide,
                                    empl.v_razsoc as v_desrazons

                  from TREGPLAME.pemvx_empleador e
                 inner join SIMINTRA1.SITB_EMPLEADOR@db_oraapolo empl
                    on trim(e.c_numruc)  =  trim(empl.v_codemp)
                 inner join TREGPLAME.pemvx_vinlab v
                    on TRIM(e.c_numruc) = TRIM(v.c_numruc)
                   and e.v_corproc = v.v_corproc
                  left join tregplame.pemvc_ddjj cremu
                    on e.c_numruc = cremu.c_numruc
                 inner join tregplame.pemvd_ddjjdet detremu
                    on cremu.c_numpaq = detremu.c_numpaq
                   and cremu.c_form = detremu.c_form
                   and cremu.i_norden = detremu.i_norden
                   and TRIM(cremu.c_numruc) = TRIM(detremu.c_numruc)
                   and cremu.c_perdecla = detremu.c_perdecla
                   and detremu.v_numdocide = v.v_numdocide
                 inner join tregplame.pemvx_ingdesapo detconcept
                    on detremu.c_numpaq = detconcept.c_numpaq
                   and detremu.c_form = detconcept.c_form
                   and detremu.i_norden = detconcept.i_norden
                   and detremu.c_perdecla = detconcept.c_perdecla
                   and detremu.c_numruc = detconcept.c_numruc
                   and detremu.c_coddocide = detconcept.c_coddocide
                   and detremu.v_numdocide = detconcept.v_numdocide
                   and detremu.c_codcatpre = detconcept.c_codcatpre
                 inner join planelec.PEMVX_PERSONA per
                    on v.v_numdocide = per.v_numdoc
                    WHERE e.v_corproc = 1
                      AND v.v_flgact = 1
                      AND per.v_numdoc = %s  -- pv_nrodocide
                      AND v.c_coddocide = '03'
                      AND cremu.c_indrec = '1'
                      AND cremu.c_perdecla >= %s  -- pv_perioinic
                      AND cremu.c_perdecla <= %s  -- pv_periofin
                      AND detconcept.c_codconcep <> '0000' """, [pv_nrodocide, pv_perioinic, pv_periofin])

                resultados = cursor.fetchall()

                datos = [
                    {
                        'apellido_paterno': fila[0],
                        'apellido_materno': fila[1],
                        'nombres': fila[2],
                        'ruc':  fila[3].strip(),
                        'razon_social': fila[4]
                    }
                    for fila in resultados
                ]
                return datos
        elif consolidado == constants.SI_CHAR_BINARY and tipo_categoria == constants.CATEGORIA_5TA:
            print('entre al segundo if')
            with connections['planillas'].cursor() as cursor:
                cursor.execute("""
                    select distinct v.v_numdocide as v_numdocapo,per.v_apepater as v_apepater,
                    per.v_apemater as v_apemater,per.v_nombres as v_nombres,
                    mplelsys.pkg_consulta_tregistro_plame
                        .FNC_OBT_PERIODO_LAB_PLAME(v.c_coddocide,
                                                   v.v_numdocide,
                                                    TRIM(v.c_numruc),
                                                    v.v_corproc,
                                                    v.v_corproc1,
                                                    v.i_numcorvin,
                                                    cremu.c_perdecla) periodo_lab,
                    (select tc.v_destipcon
                     from SIMINTRA1.sitb_tipocontrato@db_oraapolo tc
                     where tc.v_codtipcon = MPLELSYS.fnc_valorindicador(
                                               v.i_numcorvin,
                                               TRIM(v.c_numruc),
                                               '0204',
                                               '02',
                                               0)) as tipo_contrato,
                    (select catOcu.v_descatocu
                     from SIMINTRA1.sitb_catocupacion@db_oraapolo catOcu
                     where catOcu.v_codcatocu = MPLELSYS.fnc_valorindicador(
                                               v.i_numcorvin,
                                               TRIM(v.c_numruc),
                                               '0201',
                                               '02',
                                               0)) as categocupac,
                    decode(MPLELSYS.fnc_valorindicador(
                                              v.i_numcorvin,
                                              TRIM(v.c_numruc),
                                              '0210','02',0),'1',
                                               'DIRECCION',
                                               '2',
                                               'CONFIANZA',
                                               '0',
                                               'NINGUNA') AS situacespec,
                    (select ocu.v_desocupac
                       from SIMINTRA1.sitb_ocupacion@db_oraapolo ocu
                      where ocu.v_codocupac =
                            MPLELSYS.fnc_valorindicador(
                                               v.i_numcorvin,
                                               TRIM(v.c_numruc),
                                               '0203',
                                               '02',
                                               0)) as ocupacion,
                    detconcept.c_codconcep as v_codintrde,
                    (select cr.v_desintrde
                       from MPLELSYS.petbx_conceptorem cr
                      where detconcept.c_codconcep = cr.v_codintrde) as concepto,
                    (select cr.v_tipo
                       from MPLELSYS.petbx_conceptorem cr
                      where detconcept.c_codconcep = cr.v_codintrde) as tipo_concepto,
                    (case
                      when (select cr.v_tipo
                              from MPLELSYS.petbx_conceptorem cr
                             where detconcept.c_codconcep = cr.v_codintrde) =
                           '0100' then
                       nvl(detconcept.n_mtopagdes, 0.0)
                      when (select cr.v_tipo
                              from MPLELSYS.petbx_conceptorem cr
                             where detconcept.c_codconcep = cr.v_codintrde) =
                           '0700' then
                       nvl(detconcept.n_mtopagdes, 0.0)
                      when (select cr.v_tipo
                              from MPLELSYS.petbx_conceptorem cr
                             where detconcept.c_codconcep = cr.v_codintrde) =
                           '0600' then
                       nvl(detconcept.n_mtoimpues, 0.0)
                      when (select cr.v_tipo
                              from MPLELSYS.petbx_conceptorem cr
                             where detconcept.c_codconcep = cr.v_codintrde) =
                           '0800' then
                       nvl(detconcept.n_mtoimpues, 0.0)
                      when (select cr.v_tipo
                              from MPLELSYS.petbx_conceptorem cr
                             where detconcept.c_codconcep = cr.v_codintrde) =
                           '1000' then
                       nvl(detconcept.n_mtopagdes, 0.0)
                      when (select cr.v_tipo
                              from MPLELSYS.petbx_conceptorem cr
                             where detconcept.c_codconcep = cr.v_codintrde) =
                           '2000' then
                       nvl(detconcept.n_mtopagdes, 0.0)
                      when (select cr.v_tipo
                              from MPLELSYS.petbx_conceptorem cr
                             where detconcept.c_codconcep = cr.v_codintrde) =
                           '0500' then
                       nvl(detconcept.n_mtopagdes, 0.0)
                      when (select cr.v_tipo
                              from MPLELSYS.petbx_conceptorem cr
                             where detconcept.c_codconcep = cr.v_codintrde) =
                           '0200' then
                       nvl(detconcept.n_mtopagdes, 0.0)
                      when (select cr.v_tipo
                              from MPLELSYS.petbx_conceptorem cr
                             where detconcept.c_codconcep = cr.v_codintrde) =
                           '0300' then
                       nvl(detconcept.n_mtopagdes, 0.0)
                      when (select cr.v_tipo
                              from MPLELSYS.petbx_conceptorem cr
                             where detconcept.c_codconcep = cr.v_codintrde) =
                           '0400' then
                       nvl(detconcept.n_mtopagdes, 0.0)
                      when (select cr.v_tipo
                              from MPLELSYS.petbx_conceptorem cr
                             where detconcept.c_codconcep = cr.v_codintrde) =
                           '0900' then
                       nvl(detconcept.n_mtopagdes, 0.0)
                    end) as n_monpagado,
                    cremu.c_perdecla as v_numperiod,
                    e.c_numruc as v_numdocide,
                    empl.v_razsoc as v_desrazons,
--                     pv_numtran as v_numtran,
--                     pn_numtran as n_numtran,
                    to_char(SYSDATE, 'YYYY') as v_anotran
              from TREGPLAME.pemvx_empleador e
             inner join SIMINTRA1.SITB_EMPLEADOR@db_oraapolo empl
                on trim(e.c_numruc)  =  trim(empl.v_codemp)
             inner join TREGPLAME.pemvx_vinlab v
                on TRIM(e.c_numruc) = TRIM(v.c_numruc)
               and e.v_corproc = v.v_corproc
              left join tregplame.pemvc_ddjj cremu
                on e.c_numruc = cremu.c_numruc
             inner join tregplame.pemvd_ddjjdet detremu
                on cremu.c_numpaq = detremu.c_numpaq
               and cremu.c_form = detremu.c_form
               and cremu.i_norden = detremu.i_norden
               and TRIM(cremu.c_numruc) = TRIM(detremu.c_numruc)
               and cremu.c_perdecla = detremu.c_perdecla
               and detremu.v_numdocide = v.v_numdocide
             inner join tregplame.pemvx_ingdesapo detconcept
                on detremu.c_numpaq = detconcept.c_numpaq
               and detremu.c_form = detconcept.c_form
               and detremu.i_norden = detconcept.i_norden
               and detremu.c_perdecla = detconcept.c_perdecla
               and detremu.c_numruc = detconcept.c_numruc
               and detremu.c_coddocide = detconcept.c_coddocide
               and detremu.v_numdocide = detconcept.v_numdocide
               and detremu.c_codcatpre = detconcept.c_codcatpre
             inner join planelec.PEMVX_PERSONA per
                on v.v_numdocide = per.v_numdoc
             WHERE
                 TRIM(e.c_numruc) = %s
               and
               e.v_corproc = 1
               and v.v_flgact = 1
               and per.v_numdoc = %s
               AND v.c_coddocide = '03'
               and cremu.c_indrec = '1'
               and cremu.c_perdecla >= %s
               and cremu.c_perdecla <= %s
               and detconcept.c_codconcep <> '0000'
             order by cremu.c_perdecla, detconcept.c_codconcep""",
                               [pv_ruc, pv_nrodocide, pv_perioinic, pv_periofin])

                resultados = cursor.fetchall()

                datos = []
                identidad_periodo_map = {}

                # identidad_map = {}

                for fila in resultados:
                    numero_identidad = fila[0]
                    periodo = fila[13]
                    key = (numero_identidad, periodo)

                    if key in identidad_periodo_map:
                        dato = identidad_periodo_map[key]
                    else:
                        # Crear un nuevo registro si no existe para este numero_identidad y periodo
                        dato = {
                            'numero_identidad': fila[0],
                            'apellido_paterno': fila[1],
                            'apellido_materno': fila[2],
                            'nombres': fila[3],
                            'periodo_laboral': fila[4],
                            'tipo_contrato': fila[5],
                            'categoria_ocupacion': fila[6],
                            'situacion_especifica': fila[7],
                            'ocupacion': fila[8],
                            'periodo': fila[13],
                            'ruc': fila[14].strip(),
                            'razon_social': fila[15],
                            'ingresos': [],
                            'descuentos': [],
                            'aportaciones_empleador': [],
                            'aportaciones_trabajador': [],
                            'regimen_publico': [],
                            'otros_conceptos': []
                        }
                        identidad_periodo_map[key] = dato
                        datos.append(dato)

                    if fila[11] == '0100':
                        dato['ingresos'].append({
                            'codigo_concepto': fila[9],
                            'tipo_concepto': fila[11],
                            'monto_pago': fila[12],
                            'concepto': fila[10],
                        })
                    elif fila[11] == '0600':
                        dato['aportaciones_trabajador'].append({
                            'codigo_concepto': fila[9],
                            'tipo_concepto': fila[11],
                            'monto_pago': fila[12],
                            'concepto': fila[10],
                        })
                    elif fila[11] == '0700':
                        dato['descuentos'].append({
                            'codigo_concepto': fila[9],
                            'tipo_concepto': fila[11],
                            'monto_pago': fila[12],
                            'concepto': fila[10],
                        })
                    elif fila[11] == '0800':
                        dato['aportaciones_empleador'].append({
                            'codigo_concepto': fila[9],
                            'tipo_concepto': fila[11],
                            'monto_pago': fila[12],
                            'concepto': fila[10],
                        })
                    elif fila[11] == '2000':
                        dato['regimen_publico'].append({
                            'codigo_concepto': fila[9],
                            'tipo_concepto': fila[11],
                            'monto_pago': fila[12],
                            'concepto': fila[10],
                        })
                    elif fila[11] == '1000':
                        dato['otros_conceptos'].append({
                            'codigo_concepto': fila[9],
                            'tipo_concepto': fila[11],
                            'monto_pago': fila[12],
                            'concepto': fila[10],
                        })

                # Ordenar los datos por 'periodo' de mayor a menor
                datos_ordenados = sorted(datos, key=lambda x: x['periodo'], reverse=True)

                return datos_ordenados
        elif tipo_categoria == constants.CATEGORIA and consolidado == constants.SI_CHAR_BINARY:
            print('entre al tercer if')
            with connections['planillas'].cursor() as cursor:
                cursor.execute("""select e.v_corproc,
                       empl.v_razsoc as v_desrazons,
                       ctacat.v_desapenom as v_apepater,
                       ' ' as v_apemater,
                       ' ' as v_nombres,
                       cremu.c_perdecla as v_numperiod,
                       TRIM(e.c_numruc) as v_numdocide,
                       (case when ctacat.c_coddocide='09' then
                           substr(ctacat.v_numdocide,3,8) else ctacat.v_numdocide end) as v_numdocapo,
                       compag.c_numserie as v_numserie,
                       compag.c_numcompro as v_numrecibo,
                       decode(compag.c_indcompag, 'R', 'RECIBO POR HONORARIO','N', 'NOTA DE CRÉDITO',
                              'D', 'DIETA', 'O', 'OTRO COMPROBANTE', compag.c_indcompag) as tipo_comp,
                       compag.n_mtoservic as n_monrecibo,
                       compag.d_fecemisio as d_fecemsion,
                       compag.d_fecpago as d_fecpago,
                       '-' as periodo_lab,
                       '-' as tipo_contrato,
                       '-' as categocupac,
                       '-' AS situacespec,
                       '-' as ocupacion
                       from
                       tregplame.pemvx_empleador e
                       inner join simintra1.SITB_EMPLEADOR@db_oraapolo empl
                       on TRIM(e.c_numruc)=TRIM(empl.v_codemp)
                       inner join tregplame.pemvc_ddjj cremu
                       on TRIM(cremu.c_numruc)=TRIM(e.c_numruc)
                       inner join tregplame.pemvx_psctacat ctacat
                       on cremu.c_numpaq=ctacat.c_numpaq
                       and cremu.c_form=ctacat.c_form
                       and cremu.i_norden=ctacat.i_norden
                       and TRIM(cremu.c_numruc)=TRIM(ctacat.c_numruc)
                       and cremu.c_perdecla=ctacat.c_perdecla
                       inner join tregplame.pemvx_compag compag
                       on compag.c_numpaq=ctacat.c_numpaq
                       and compag.c_form=ctacat.c_form
                       and compag.i_norden=ctacat.i_norden
                       and TRIM(compag.c_numruc)=TRIM(ctacat.c_numruc)
                       and compag.c_perdecla=ctacat.c_perdecla
                       and compag.c_coddocide=ctacat.c_coddocide
                       and compag.v_numdocide=ctacat.v_numdocide
                    WHERE substr(ctacat.v_numdocide,3,8) = %s
                       and e.v_corproc = 1
                       AND cremu.c_perdecla >= %s
                       and cremu.c_perdecla <= %s
                       order by cremu.c_perdecla """,[pv_nrodocide, pv_perioinic, pv_periofin])

                resultados = cursor.fetchall()
                print('entre a la 4ta')

                datos = [
                    {
                        'razon_social': fila[1],
                        'apellido_nombres': fila[2],
                        'periodo': fila[5],
                        'ruc': fila[6],
                        'documento_identidad': fila[7],
                        'numero_serie_recibo': fila[8],
                        'numero_recibo': fila[9],
                        'tipo_contrato': fila[10],
                        'pago_monto': fila[11],
                        'fecha_emision': fila[12],
                        'fecha_pago': fila[13],
                        'fecha_laboral': fila[14]
                    }
                    for fila in resultados
                ]
                return datos
    except DatabaseError as e:
        raise e
