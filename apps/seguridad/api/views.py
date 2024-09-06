import json
from datetime import datetime

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from rest_framework.exceptions import Throttled
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_204_NO_CONTENT,
    HTTP_208_ALREADY_REPORTED,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_201_CREATED
)
from rest_framework.views import APIView

from apps.common import constants
from apps.common.functions import ServiciosExternos
from apps.common.functions import ServiciosInternos as si
from apps.common.utils import CustomPagination, convertir_parametro_insensible
# from apps.modelsext.api.serializers import SiPersonaSerializer
from apps.modelsext.models import (
    SiPersona, SiPerfil, Departamento, Provincia, SiUsuPerfil,
    Distrito, TPersonal, SiDependencia, SiUsuario, SiRegional, SiZonal, SiTrabajador, SiEmpresa, SiGenero
)
from apps.programacion.models import Sede, Solicitud, SolicitudDetalle, Motivo
from apps.seguridad.api.use_cases import UsuarioVerificcionnUseCase, UsuarioCredencialesUseCase, \
    UsuarioInvitacionUseCase
from apps.seguridad.api.serializers import UserSerializer, GrupoSerializer, UserGroupSerializer, UserUpdateSerializer
from apps.seguridad.auth import (
    CustomAuthentication, CustomAuthenticationTemporal,
    CustomAuthenticationValidacion, CustomAuthenticationConfidencial
)
from apps.seguridad.models import Parametro, User, Group, MenuGroup, Menu, UserGroup

from config.settings.base import (CODIGO_SISTEMA, SKIP_VALIDAR_VERIFICACION)
from apps.seguridad.api.throttle import UserLoginRateThrottle


class AccesoAPIView(APIView):
    authentication_classes = [CustomAuthentication]
    throttle_classes = (UserLoginRateThrottle,)

    def post(self, request, *args, **kwargs):
        response_data = request.auth.copy()
        vals = {
            'codigo': response_data.get('numero_documento'),
            'nombre': 'Token Temporal',
            'valor': response_data.get('token_cache'),
        }
        parametro, _ = Parametro.objects.get_or_create(**vals)
        response_data.update(
            {'pk_parametro': parametro.pk, 'nuevo': response_data.get('nuevo')}
        )
        if response_data.get('nuevo'):
            status = HTTP_200_OK
        else:
            status = HTTP_208_ALREADY_REPORTED
            response_data.update({'mensaje': 'El usuario ya se encuentra registrado.'})
        return Response(response_data, status=status)

    def throttled(self, request, wait):
        raise Throttled(detail={
            "message": "RECAPTCHA es requerido.",
        })


class CierreAPIView(APIView):
    def post(self, request, *args, **kwargs):
        response_data = request.auth.copy()
        parametro = Parametro.objects.filter(pk=response_data.get('token_id'))
        if parametro.exists():
            parametro.first().valor = '-'
            parametro.first().save()
        return Response(response_data, status=HTTP_204_NO_CONTENT)


class GrupoAPIView(APIView):
    authentication_classes = [CustomAuthenticationTemporal]

    def get(self, request):
        data = self.request.query_params.copy()
        query_set = Group.objects.all()
        try:
            if data.get('pk_grupo'):
                query_set = query_set.filter(pk_grupo=data.get('pk_grupo'))
            if data.get('nombre'):
                query_set = query_set.filter(nombre__icontains=data.get('nombre'))
            serializer = GrupoSerializer(instance=query_set, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)

    def post(self, request):
        profile_codes = request.data.get('grupos', [])
        profiles = SiPerfil.objects.filter(
            codigo_perfil__in=profile_codes, codigo_sistema=CODIGO_SISTEMA
        )

        groups_data = []
        for profile in profiles:
            try:
                group = Group.objects.get(pk_grupo=profile.codigo_perfil)
                group_data = {
                    'pk_grupo': profile.codigo_perfil,
                    'nombre': profile.nombre_perfil,
                    'flagact': group.flagact,
                }
            except Group.DoesNotExist:
                group_data = {
                    'pk_grupo': profile.codigo_perfil,
                    'nombre': profile.nombre_perfil,
                    'flagact': '1',
                }
            groups_data.append(group_data)
        serializer = GrupoSerializer(data=groups_data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class MenuAPIView(APIView):
    authentication_classes = [CustomAuthenticationConfidencial]

    def post(self, request):
        data = request.data.copy()  # Lista de diccionarios con los datos de los menús
        menus = data.get('menu_data')
        existing_menus = []
        new_menus = []
        eliminar = data.get('eliminar')

        if eliminar == '1':
            menues_borrar = Menu.objects.filter(pk_menu__in=data.get('eliminar_list'))
            if menues_borrar.exists():
                pass

        for menu_data in menus:
            url = menu_data.get('url')
            menu = Menu.objects.filter(url=url)

            if menu.exists():
                menu = menu.first()
                # Actualizar menú existente
                for key, value in menu_data.items():
                    if (
                        key == 'parent_id'
                        and Menu.objects.filter(pk_menu=value).exists()
                    ):
                        setattr(menu, key, value)
                    elif key == 'pk_menu' and data.get('pk') == '1':
                        setattr(menu, key, value)
                    elif key not in ('pk_menu', 'parent_id'):
                        setattr(menu, key, value)
                menu.save()
                existing_menus.append(menu)
            else:
                # Crear nuevo menú
                new_menu = Menu(**menu_data)
                new_menu.save()
                new_menus.append(new_menu)

        all_menus = Menu.objects.all()
        menus_data = [
            {'pk_menu': menu.pk_menu, 'nombre': menu.nombre, 'url': menu.url}
            for menu in all_menus
        ]

        return Response({'menues': menus_data})


class GrupoMenuAPIView(APIView):
    authentication_classes = [CustomAuthenticationConfidencial]

    def post(self, request):
        grupomenu_data = request.data.get('grupomenu_data')
        response_data = []
        for data in grupomenu_data:

            grupo_id = data.get('pk_grupo')
            menu_list = data.get('menu_list')
            update = bool(int(data.get('update', '0')))
            grupo = Group.objects.get(pk=grupo_id)
            if update:
                MenuGroup.objects.filter(grupo=grupo).delete()

            for pk_menu in menu_list:
                menu = Menu.objects.get(pk=pk_menu)
                grupo_menus = MenuGroup.objects.filter(grupo=grupo, menu=menu)
                if grupo_menus.exists():
                    grupo_menu = grupo_menus.first()
                    response_data.append(
                        {
                            'nuevo': '0',
                            'pk_grupo': grupo_menu.grupo.pk,
                            'nombre_grupo': grupo_menu.grupo.nombre,
                            'pk_menu': grupo_menu.menu.pk,
                            'nombre_menu': grupo_menu.menu.nombre,
                        }
                    )
                    continue
                grupo_menu, _ = MenuGroup.objects.get_or_create(
                    grupo=grupo, menu=menu
                )
                response_data.append(
                    {
                        'nuevo': '1',
                        'pk_grupo': grupo_menu.grupo.pk,
                        'nombre_grupo': grupo_menu.grupo.nombre,
                        'pk_menu': grupo_menu.menu.pk,
                        'nombre_menu': grupo_menu.menu.nombre,
                    }
                )

        return Response(response_data, status=HTTP_200_OK)


class GrupoUsuarioAPIView(APIView):
    authentication_classes = [CustomAuthenticationConfidencial]

    def post(self, request):
        serializer = UserGroupSerializer(data=request.data)
        if serializer.is_valid():
            menu_list = serializer.validated_data['menu_list']
            usuario_list = serializer.validated_data['usuario_list']

            created_usergroups = []

            for menu_id in menu_list:
                for usuario_id in usuario_list:
                    pk_grupo, nombre_grupo = si.get_perfil_usuario(usuario_id)
                    usuario = User.objects.get(pk_usuario=usuario_id)
                    menu = Menu.objects.get(pk_menu=menu_id)
                    grupo = Group.objects.get(pk_grupo=pk_grupo)
                    usergroup = UserGroup.objects.create(
                        usuario=usuario,
                        menu=menu,
                        grupo=grupo,
                        flag=constants.SI_CHAR_BINARY,
                    )
                    created_usergroups.append(usergroup.pk_usugru)

            return Response(
                {'pk_grupo_usuarios': created_usergroups}, status=HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ParametroAPIView(APIView):
    authentication_classes = [CustomAuthenticationConfidencial]

    def post(self, request):
        codigo = request.data.get('codigo')
        nombre = request.data.get('nombre')
        valor = request.data.get('valor')
        if Parametro.objects.filter(valor=valor).exists():
            return Response({'message': 'Parámetro ya existente'}, status=208)
        Parametro.objects.create(codigo=codigo, nombre=nombre, valor=valor)
        return Response({'message': 'Parámetro creado exitosamente'}, status=201)


class ValidacionAPIView(APIView):

    def verificar_identidad_siempresa(self, codigo_empresa):
        siempresa = SiEmpresa.objects.filter(ruc=codigo_empresa)
        if not siempresa.exists():
            return False, {}
        siempresa = siempresa.last()
        result = si.get_ubigeo(siempresa.codigo_departamento, siempresa.codigo_provincia, siempresa.codigo_distrito)
        data = {
            'simintra': constants.SI_CHAR_BINARY,
            'razon_social': siempresa.razon_social,
            'nombres': siempresa.razon_social,
            'es_activo': str(siempresa.flag),  # noqa
            'es_habido': constants.SI_CHAR_BINARY,  # noqa
            'ruc': siempresa.ruc,
            'tipo': '02' if siempresa.tipo == 'J' else '01',
            'estado': 'ACTIVA',
            'flag': str(siempresa.flag),
            'descripcion_ciiu': '-',
            'codigo_ciiu': siempresa.codigo_ciiu,
            'codigo': '',
            'codigo_departamento': siempresa.codigo_departamento,
            'codigo_provincia': siempresa.codigo_provincia,
            'codigo_distrito': siempresa.codigo_distrito,
            'descripcion_departamento': result.get('departamento').get('descripcion'),
            'descripcion_provincia': result.get('provincia').get('descripcion'),
            'descripcion_distrito': result.get('distrito').get('descripcion'),
            'direccion': '{} {}'.format(siempresa.nombre_direccion, siempresa.numero_direccion),
        }

        return True, data

    def verificar_identidad_sipersona(self, tipo_documento, codigo_personal):
        sipersona = SiPersona.objects.filter(tipo_documento=tipo_documento, codigo_personal=codigo_personal)
        if not sipersona.exists():
            return False, {}
        sipersona = sipersona.last()
        fecha_caducidad = None
        if sipersona.fecha_caducidad:
            fecha_caducidad = sipersona.fecha_caducidad.strftime('%d/%m/%Y')
        fecha_nacimiento = None
        if sipersona.fecha_nacimiento:
            fecha_nacimiento = sipersona.fecha_nacimiento.strftime('%d/%m/%Y')
        result = si.get_ubigeo(sipersona.codigo_departamento, sipersona.codigo_provincia, sipersona.codigo_distrito)
        data_persona = {
            'simintra': constants.SI_CHAR_BINARY,
            'apellido_paterno': sipersona.apellido_paterno,
            'apellido_materno': sipersona.apellido_materno,
            'nombres': sipersona.nombres,
            'tipo_documento': sipersona.tipo_documento,
            'codigo_personal': codigo_personal,
            'codigo_pais': sipersona.codigo_pais,
            'codigo_departamento': sipersona.codigo_departamento,
            'codigo_provincia': sipersona.codigo_provincia,
            'codigo_distrito': sipersona.codigo_distrito,
            'descripcion_departamento': result.get('departamento', {}).get('descripcion'),
            'descripcion_provincia': result.get('provincia', {}).get('descripcion'),
            'descripcion_distrito': result.get('distrito', {}).get('descripcion'),
            'fecha_caducidad': fecha_caducidad,
            'fecha_nacimiento': fecha_nacimiento,
            'sexo': sipersona.sexo
        }
        return True, data_persona

    def post(self, request, *args, **kwargs):
        data = self.request.data.copy()
        valido = False

        def update_data_persona(servicio_ext, data_persona):
            if valido and not (data_persona.get('direccion')
                               or data_persona.get('codigo_departamento')
                               or data_persona.get('codigo_provincia')
                               or data_persona.get('codigo_distrito')
            ):
                valido_ext, data_persona_ext = servicio_ext(
                    ServiciosExternos(), data.get('numero_documento')
                )
                if not valido_ext:
                    return data_persona
                if not data_persona.get('direccion'):
                    data_persona.update({'direccion': data_persona_ext.get('direccion')})
                if not data_persona.get('codigo_departamento'):
                    data_persona.update({'codigo_departamento': data_persona_ext.get('codigo_departamento')})
                    data_persona.update({'descripcion_departamento': data_persona_ext.get('descripcion_departamento')})
                if not data_persona.get('codigo_provincia'):
                    data_persona.update({'codigo_provincia': data_persona_ext.get('codigo_provincia')})
                    data_persona.update({'descripcion_provincia': data_persona_ext.get('descripcion_provincia')})
                if not data_persona.get('codigo_distrito'):
                    data_persona.update({'codigo_distrito': data_persona_ext.get('codigo_distrito')})
                    data_persona.update({'descripcion_distrito': data_persona_ext.get('descripcion_distrito')})
            return data_persona

        try:
            easy_data = bool(int(data.get('easy_data', '0')))
            data_persona = {}
            tipo_documento_len_list = constants.TIPO_DOCUMENTO_LENGTH.get(data.get('tipo_documento'))
            if not (tipo_documento_len_list[0] <= len(data.get('numero_documento')) <= tipo_documento_len_list[1]):
                return si.get_mensaje(
                    'El Tipo de documento no tiene la longitud requerida. Entre {} y {}'.format(
                        tipo_documento_len_list[0], tipo_documento_len_list[1]
                    ),
                    False,
                    code_status=404,
                )
            if data.get('tipo_documento') == constants.TIPO_DOCUMENTO_DNI:
                valido, data_persona = self.verificar_identidad_sipersona(
                    data.get('tipo_documento'), data.get('numero_documento')
                )
                if not valido:
                    valido, data_persona = ServiciosExternos.verificar_identidad_reniec(
                        ServiciosExternos(), data.get('numero_documento')
                    )
                    if type(data_persona) == str or data_persona.get('codigo') != '200':
                        return si.get_mensaje(
                            'El número de documento {} no existe.'.format(data.get('numero_documento')),
                            False,
                        )
                data_persona = update_data_persona(ServiciosExternos.verificar_identidad_reniec, data_persona)

            elif data.get('tipo_documento') == constants.TIPO_DOCUMENTO_CE:
                valido, data_persona = self.verificar_identidad_sipersona(
                    data.get('tipo_documento'), data.get('numero_documento')
                )
                if not valido:
                    valido, data_persona = ServiciosExternos.verificar_identidad_ce(
                        ServiciosExternos(), data.get('numero_documento')
                    )
                    if type(data_persona) == str or data_persona.get('codigo') != '0000':
                        return si.get_mensaje(
                            'El número de documento {} no existe.'.format(
                                data.get('numero_documento')
                            ),
                            False,
                        )
                data_persona = update_data_persona(ServiciosExternos.verificar_identidad_ce, data_persona)

            elif data.get('tipo_documento') == constants.TIPO_DOCUMENTO_CPP:
                valido, data_persona = self.verificar_identidad_sipersona(
                    data.get('tipo_documento'), data.get('numero_documento')
                )
                if not valido:
                    valido, data_persona = ServiciosExternos.verificar_identidad_cpp(
                        ServiciosExternos(), data.get('numero_documento')
                    )
                    if type(data_persona) == str or data_persona.get('codigo') != '0000':
                        return si.get_mensaje(
                            'El número de documento {} no existe.'.format(
                                data.get('numero_documento')
                            ),
                            False,
                        )
                data_persona = update_data_persona(ServiciosExternos.verificar_identidad_cpp, data_persona)

            elif data.get('tipo_documento') == constants.TIPO_DOCUMENTO_RUC:
                valido, data_persona = self.verificar_identidad_siempresa(data.get('numero_documento'))
                if not valido:
                    valido, data_persona = ServiciosExternos.verificar_identidad_ruc(
                        ServiciosExternos(), data.get('numero_documento')
                    )
                    if type(data_persona) == str:
                        return si.get_mensaje(data_persona, False)
                data_persona = update_data_persona(ServiciosExternos.verificar_identidad_cpp, data_persona)

            if not valido:
                return si.get_mensaje(f'Error en la validación: {data_persona}', False)

            usuario = User.objects.filter(pk_usuario=data.get('numero_documento'))
            if usuario.exists() and not bool(int(data.get('datos', '0'))):
                return si.get_mensaje(
                    'El usuario con número de documento: {} ya existe.'.format(
                        data.get('numero_documento')
                    ),
                    False,
                )

            if valido and not data_persona.get('simintra'):
                if data.get('tipo_documento') == constants.TIPO_DOCUMENTO_RUC:
                    vals_persona = {
                        'ruc': data_persona.get('ruc'),
                        'numero_ruc': data_persona.get('ruc'),
                        'razon_social': data_persona.get('razon_social'),
                        'codigo_ciiu': data_persona.get('codigo_ciiu'),
                        'tipo': 'J' if data_persona.get('tipo') == '02' else 'N',
                        'codigo_departamento': data_persona.get('codigo_departamento'),
                        'codigo_provincia': data_persona.get('codigo_provincia'),
                        'codigo_distrito': data_persona.get('codigo_distrito'),
                        'usuario_creacion': 'ATCOADLASYS',
                        'usuario_modificacion': 'ATCOADLASYS',
                        'fecha_creacion': datetime.now(),
                        'fecha_modificacion': datetime.now(),
                        'host_registro': request.META.get('HTTP_HOST'),
                        'host_modificacion': request.META.get('HTTP_HOST'),
                        'flag': 1
                    }
                    siempresa, _ = SiEmpresa.objects.get_or_create(**vals_persona)
                else:
                    codigo_provincia = None
                    codigo_distrito = None
                    departamento = Departamento.objects.filter(
                        Q(codigo_departamento=data_persona.get('codigo_departamento')) |
                        Q(codigo_departamento_ren=data_persona.get('codigo_departamento_ren'))
                    )
                    if departamento.exists():
                        departamento = departamento.last()
                        codigo_departamento = departamento.codigo_departamento
                        provincia = Provincia.objects.filter(
                            Q(codigo_departamento=codigo_departamento),
                            Q(codigo_provincia=data_persona.get('codigo_provincia')) |
                            Q(codigo_provincia_ren=data_persona.get('codigo_provincia_ren'))
                        )
                        if provincia.exists():
                            provincia = provincia.last()
                            codigo_provincia = provincia.codigo_provincia
                            distrito = Distrito.objects.filter(
                                Q(codigo_departamento=codigo_departamento),
                                Q(codigo_provincia=codigo_provincia),
                                Q(codigo_distrito=data_persona.get('codigo_distrito')) |
                                Q(codigo_distrito_ren=data_persona.get('codigo_distrito_ren'))
                            )
                            if distrito.exists():
                                distrito = distrito.last()
                                codigo_distrito = distrito.codigo_distrito

                        vals_persona = {
                            'tipo_documento': data_persona.get('tipo_documento'),
                            'codigo_personal': data_persona.get('numero_documento'),
                            'apellido_paterno': data_persona.get('apellido_paterno'),
                            'apellido_materno': data_persona.get('apellido_materno'),
                            'nombres': data_persona.get('nombres'),
                            'codigo_pais': data_persona.get('pais_nacimiento'),
                            'codigo_departamento': codigo_departamento,
                            'codigo_provincia': codigo_provincia,
                            'codigo_distrito': codigo_distrito,
                            'fecha_nacimiento': datetime.strptime(data_persona.get('fecha_nacimiento'), '%d/%m/%Y'),
                            'fecha_caducidad': datetime.strptime(data_persona.get('fecha_caducidad'), '%d/%m/%Y'),
                            'sexo': data_persona.get('sexo'),
                            'estado_civil': data_persona.get('estado_civil'),
                            'usuario_creacion': 'ATCOADLASYS',
                            'usuario_modificacion': 'ATCOADLASYS',
                            'fecha_creacion': datetime.now(),
                            'fecha_modificacion': datetime.now(),
                            'host_registro': request.META.get('HTTP_HOST'),
                            'host_modificacion': request.META.get('HTTP_HOST'),
                            'sistema_registro': CODIGO_SISTEMA,
                            'sistema_modificacion': CODIGO_SISTEMA,
                            'flag': '1'
                        }
                        sipersona, _ = SiPersona.objects.get_or_create(**vals_persona)
            elif not valido and not data_persona.get('simintra'):
                return si.get_mensaje(
                    'Hubo un problema al momento de validar la información.',
                    False,
                    'N/A',
                    code_status=400
                )
        except Exception as e:
            return si.get_mensaje(str(e), False, 'N/A', code_status=400)

        if bool(int(data.get('datos', '0'))):
            codigo_sexo = data_persona.get('sexo', '')
            genero = SiGenero.objects.filter(codigo_sexo=codigo_sexo)
            descripcion_sexo = None
            if genero.exists():
                descripcion_sexo = genero.first().descripcion_sexo
            response_data = {
                'nombres': data_persona.get('nombres', ''),
                'apellido_paterno': data_persona.get('apellido_paterno', ''),
                'apellido_materno': data_persona.get('apellido_materno', ''),
                'direccion': data_persona.get('direccion', ''),
                'codigo_departamento': data_persona.get('codigo_departamento', ''),
                'descripcion_departamento': data_persona.get('descripcion_departamento', ''),
                'codigo_provincia': data_persona.get('codigo_provincia', ''),
                'descripcion_provincia': data_persona.get('descripcion_provincia', ''),
                'codigo_distrito': data_persona.get('codigo_distrito', ''),
                'descripcion_distrito': data_persona.get('descripcion_distrito', ''),
                'sexo': data_persona.get('sexo', ''),
                'descripcion_sexo': descripcion_sexo,
                'fecha_nacimiento': data_persona.get('fecha_nacimiento', ''),
            }
            response_easy_data = {
                'nombres': data_persona.get('nombres', ''),
                'apellido_paterno': data_persona.get('apellido_paterno', ''),
                'apellido_materno': data_persona.get('apellido_materno', ''),
            }
            if easy_data:
                datos = response_easy_data
            else:
                datos = response_data
            return si.get_mensaje(
                'Validación de identidad correcta.',
                True,
                'N/A',
                code_status=200,
                datos=datos,
            )
        return si.get_mensaje(
            'Validación de identidad correcta.', True, 'N/A', code_status=200
        )


class UserAPIView(ListAPIView, UpdateAPIView):
    pagination_class = CustomPagination
    serializer_class = UserSerializer
    http_method_names = ['get', 'put']

    def set_password_simintra(self, username, password):
        password_encoded = si.encode(si(), username, password)
        usuario = SiUsuario.objects.filter(codigo_usuario=username)
        if usuario.exists():
            usuario = usuario.first()
            usuario.password_usuario = password_encoded
            usuario.save()
            return True
        return False

    def get_object(self):
        query_set = User.objects.filter(pk=self.kwargs.get('pk_usuario'))
        if not query_set.exists():
            return None
        return query_set.first()

    def put(self, request, *args, **kwargs):
        query_set = User.objects.filter(pk=self.kwargs.get('pk_usuario'))
        data = request.data.copy()
        data_auth = request.auth.copy()
        if query_set.exists():
            instance = query_set.first()
            if data.get('estado') == constants.NO_CHAR_BINARY and instance.pk_usuario == data_auth.get('pk_usuario'):
                return Response(
                    {'error': ('El usuario no puede inhabilitarse a sí mismo.',)},
                    HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {'error': ('No se pudo encontrar el usuario registrado.',)},
                HTTP_404_NOT_FOUND,
            )
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = False
        instance = self.get_object()
        data = request.data.copy()
        if data.get('celular') and data.get('celular') == '':
            celular = data.pop('celular')
        if data.get('password_usuario', None):
            password_usuario = data.pop('password_usuario')
            _ = self.set_password_simintra(instance.username, password_usuario)
        flag = data.get('flag', constants.NA_CHAR_BINARY)
        if flag == constants.SI_CHAR_BINARY and instance.compartir_datos == constants.NO_CHAR_BINARY:
            data.update({'compartir_datos': constants.SI_CHAR_BINARY})
        elif flag == constants.NO_CHAR_BINARY and instance.compartir_datos == constants.NO_CHAR_BINARY:
            data.update({'compartir_datos': constants.NO_CHAR_BINARY})
        elif flag == constants.NO_CHAR_BINARY:
            data.update({'compartir_datos': constants.SI_CHAR_BINARY})

        # ToDo: Control de que la sede y la dependencia pertenezcan a la misma zona y region
        codigo_sede = None
        codigo_dependencia = None
        codigo_cargo = None
        codigo_escala = None
        personal = TPersonal.objects.filter(codigo_personal=instance.pk_usuario)
        if not personal.exists():
            return Response(
                {'error': ('El usuario no se encuentra registrado como Personal.',)},
                HTTP_400_BAD_REQUEST,
            )
        personal = personal.first()
        if data.get('codigo_sede', None):
            codigo_sede = data.pop('codigo_sede')
            sede = Sede.objects.get(codigo_sede=codigo_sede)
            instance.sede = sede
            instance.save()
        if data.get('codigo_dependencia', None):
            codigo_dependencia = data.pop('codigo_dependencia')
            personal.codigo_dependencia = codigo_dependencia
            personal.save()
        if data.get('codigo_cargo', None):
            codigo_cargo = data.pop('codigo_cargo')
            personal.codigo_cargo = codigo_cargo
            personal.save()
        if data.get('codigo_escala', None):
            codigo_escala = data.pop('codigo_escala')
            personal.codigo_escala = codigo_escala
            personal.save()
        if data.get('pk_grupo', None):
            pk_grupo = data.pop('pk_grupo')
            usuario_todos_perfiles = SiUsuPerfil.objects.filter(
                codigo_usuario=instance.username,
                codigo_sistema=CODIGO_SISTEMA)
            # No existe ningun usuarioxperfil
            if not usuario_todos_perfiles.exists():
                usuario_perfil, _ = SiUsuPerfil.objects.get_or_create(
                    codigo_usuario=instance.username,
                    codigo_sistema=CODIGO_SISTEMA,
                    codigo_perfil=str(pk_grupo).rjust(3, '0'),
                    flag='S'
                )
            else:
                usuario_perfiles = usuario_todos_perfiles.filter(codigo_perfil=str(pk_grupo).rjust(3, '0'))
                if not usuario_perfiles.exists():
                    usuario_perfil, _ = SiUsuPerfil.objects.get_or_create(
                        codigo_usuario=instance.username,
                        codigo_sistema=CODIGO_SISTEMA,
                        codigo_perfil=str(pk_grupo).rjust(3, '0'),
                        flag='S'
                    )
                else:
                    usuario_perfiles.update(flag='S')
                usuario_otros_perfiles = usuario_todos_perfiles.exclude(codigo_perfil=str(pk_grupo).rjust(3, '0'))
                usuario_otros_perfiles.update(flag='E')
        serializer = UserUpdateSerializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        response_data = serializer.data.copy()
        response_data.update({
            'codigo_sede': codigo_sede,
            'codigo_dependencia': codigo_dependencia,
            'codigo_escala': codigo_escala,
            'codigo_cargo': codigo_cargo,
        })
        return Response(response_data, status=HTTP_200_OK)

    def get_queryset(self):
        data = self.request.query_params.copy()
        query_set = User.objects.all()
        if data.get('numero_documento'):
            query_set = query_set.filter(Q(pk_usuario__icontains=data.get('numero_documento')))
        if data.get('pk_usuario'):
            query_set = query_set.filter(Q(pk_usuario__icontains=data.get('pk_usuario')))
        if data.get('username'):
            query_set = query_set.filter(Q(username__icontains=data.get('username')))
        if data.get('codigo_region'):
            query_set = query_set.filter(Q(codigo_region=data.get('codigo_region')))
        if data.get('codigo_cargo'):
            query_set = query_set.filter(Q(codigo_cargo=data.get('codigo_cargo')))
        if data.get('codigo_institucion'):
            query_set = query_set.filter(Q(codigo_institucion=data.get('codigo_institucion')))
        personales = TPersonal.objects.none()
        if data.get('q_persona'):
            personales = TPersonal.objects.filter(
                Q(nombres__icontains=convertir_parametro_insensible(data.get('q_persona'))) |
                Q(apellido_paterno__icontains=convertir_parametro_insensible(data.get('q_persona'))) |
                Q(apellido_materno__icontains=convertir_parametro_insensible(data.get('q_persona')))
            )
        if data.get('q_dependencia'):
            if data.get('q_dependencia', '').isdigit():
                dependencia = SiDependencia.objects.filter(
                    Q(codigo_dependencia=data.get('q_dependencia'))
                )
            else:
                dependencia = SiDependencia.objects.filter(
                    Q(dependencia__icontains=convertir_parametro_insensible(data.get('q_dependencia')))
                )
            codigo_dependencias = dependencia.values_list('codigo_dependencia', flat=True)
            personales = TPersonal.objects.filter(
                Q(codigo_dependencia__in=codigo_dependencias)
            )

        if personales.exists():
            pk_usuario_list = [per.codigo_personal for per in personales]
            query_set = query_set.filter(Q(pk_usuario__in=pk_usuario_list))
        elif not personales.exists() and (data.get('q_persona') or data.get('q_dependencia')):
            query_set = query_set.none()
        query_set = query_set.order_by('-fecha_modificacion')
        return query_set


class EnviarVerificacionAPIView(APIView):
    authentication_classes = [
        CustomAuthenticationValidacion,
    ]

    def post(self, request, *args, **kwargs):
        data_auth = request.auth.copy()
        data_request = self.request.data.copy()
        try:
            use_case = UsuarioVerificcionnUseCase()
            usuario, tipo_verificacion = use_case.validar_data_enviar_verificacion(
                data_auth, data_request
            )
            response = use_case.crear_codigo_verificacion(usuario, tipo_verificacion)
            return Response(status=HTTP_200_OK, data=response.to_dict())  # type: ignore
        except Exception as e:
            return Response(
                status=HTTP_400_BAD_REQUEST,
                data={
                    'mensaje': f'Error al enviar el código de verificación, detalle: {str(e)}'
                },
            )


class ValidarVerificacionAPIView(APIView):
    authentication_classes = [
        CustomAuthenticationValidacion,
    ]

    def post(self, request, *args, **kwargs):
        data_auth = request.auth.copy()
        data_request = self.request.data.copy()
        try:
            usuario = User.objects.filter(pk_usuario=data_auth.get('pk_usuario'))
            if data_request.get('skip') == '1' and SKIP_VALIDAR_VERIFICACION == '1':
                usuario = usuario.last()
                usuario.flag = constants.SI_CHAR_BINARY
                usuario.save()
                return si.get_mensaje(
                    'Verificación correcta.', True, estado=usuario.flag
                )
            use_case = UsuarioVerificcionnUseCase()
            codigo_validado, msj = use_case.validar_codigo_verificacion(
                data_auth, data_request
            )

            flag = usuario.last().flag if usuario.exists() else None
            if codigo_validado:
                usuario = usuario.last()
                usuario.flag = constants.SI_CHAR_BINARY
                usuario.save()
                return si.get_mensaje(msj, True, estado=usuario.flag)
            else:
                return si.get_mensaje(msj, False, estado=flag)
        except Exception as e:
            return si.get_mensaje(str(e))


class EnviarCredencialesAPIView(APIView):
    authentication_classes = [
        CustomAuthenticationValidacion,
    ]

    def post(self, request, *args, **kwargs):
        data_auth = request.auth.copy()
        data_request = self.request.data.copy()
        try:
            use_case = UsuarioCredencialesUseCase()
            usuario, tipo_verificacion = use_case.validar_data_enviar_verificacion(data_auth, data_request)
            response = use_case.crear_credenciales(usuario, tipo_verificacion)

            return Response(status=HTTP_200_OK, data=response.to_dict())  # type: ignore
        except Exception as e:
            return Response(
                status=HTTP_400_BAD_REQUEST,
                data={
                    'mensaje': f'Error al enviar las credenciales. Detalle: {str(e)}'
                },
            )
