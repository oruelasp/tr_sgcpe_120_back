import jwt
import secrets
import string
import random
import json
import re
from datetime import date, datetime, timedelta

from django.contrib.auth.models import AnonymousUser
import requests
from django.core.cache import cache
from django.db.models import Q, F, OuterRef, Subquery, ExpressionWrapper, DateTimeField
from django.db.models.functions import Now
from rest_framework import authentication, exceptions
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_401_UNAUTHORIZED
)

from apps.common import constants
from apps.common.functions import ServiciosExternos, ServiciosInternos
from apps.modelsext.models import (SiPerfil, SiUsuario, SiUsuarioTotal,
                                   SiUsuPerfil, SiUsuSistema, SiDependencia, TPersonal, SiPersona,
                                   SiTrabajador, Departamento, Provincia, Distrito, Nacionalidad, SiZonal, SiRegional,
                                   SitbPliego)
from apps.programacion.models import Sede
from apps.seguridad.models import Group, MenuGroup, Parametro, PermissionsGroup, User, Regla, UserGroup, Menu
from config.settings.base import CODIGO_SISTEMA

SCALVIR_CACHE_KEY = 'scalvir-access-token'


class CustomAuthentication(authentication.BaseAuthentication):
    @staticmethod
    def get_auth_datos(request):
        # ToDo: Pending to refactor
        objse = ServiciosExternos()
        token = request.META.get('HTTP_AUTHORIZATION')
        results = objse.verificar_identidad_reniec(token)
        if results[0]:
            username = (
                results[1]
                .get(
                    'Value',
                )
                .get('userName')
            )
            id_aplicacion = (
                results[1]
                .get(
                    'Value',
                )
                .get('appId')
            )
            dni = (
                results[1]
                .get(
                    'Value',
                )
                .get('dni')
            )
            pk_usuario = None
            try:
                trabajador = SiUsuario.objects.filter(dni=dni)
                if trabajador.exists():
                    trabajador = trabajador.last()
                    pk_usuario, codigo_dependencia = (
                        trabajador.pk_usuario,
                        trabajador.codigo_dependencia,
                    )
            except Exception as e:  # noqa
                pk_usuario, codigo_dependencia = None, None  # noqa
            datos = {
                'pk_usuario': pk_usuario,
                'username': username,
                'numero_documento': dni,
                'id_aplicacion': id_aplicacion,
            }
            return True, datos
        else:
            return False, {}

    def set_usuario_local(self, codigo_personal, username, tipo_usuario, celular, email,
                          codigo_sede=None, codigo_dependencia=None,
                          compartir_datos=None,codigo_region=None,codigo_institucion=None,
                          siusuario_existe=False, super_admin=False):
        data_usuario = {
            'pk_usuario': codigo_personal,
            # 'compartir_datos':compartir_datos,
            # 'codigo_region':codigo_region,
            # 'codigo_institucion':codigo_institucion
        }
        usuarios = User.objects.filter(**data_usuario)
        if usuarios.exists():
            usuario = usuarios.first()
        else:
            data_usuario.update({
                'username': username,
                'compartir_datos':compartir_datos,
                'codigo_region':codigo_region,
                'codigo_institucion':codigo_institucion
            })
            usuario, nuevo = User.objects.get_or_create(**data_usuario)
        usuario.tipo_usuario = tipo_usuario
        # if codigo_sede:
        #     sedes = Sede.objects.filter(codigo_sede=codigo_sede)
        #     sede = sedes.first() if sedes.exists() else None
        #     usuario.sede = sede
        # if codigo_dependencia:
        #     dependencias = SiDependencia.objects.filter(codigo_dependencia=codigo_dependencia)
        #     dependencia = dependencias.first() if dependencias.exists() else None
        #     usuario.dependencia = dependencia
        if celular:
            usuario.celular = celular
        if email:
            usuario.email = email
        if super_admin:
            usuario.super_admin = constants.SI_CHAR_BINARY
        elif not super_admin and usuario.super_admin and not bool(int(usuario.super_admin)):
            usuario.super_admin = constants.NO_CHAR_BINARY
        usuario.save()
        return usuario

    def validar_persona_simintra(self, tipo_documento, codigo_personal):
        sipersona = SiPersona.objects.filter(tipo_documento=tipo_documento, codigo_personal=codigo_personal)
        existe = False
        data = {}
        if sipersona.exists():
            existe = True
            sipersona = sipersona.last()
            fecha_caducidad = None
            if sipersona.fecha_caducidad:
                fecha_caducidad = sipersona.fecha_caducidad.strftime('%d/%m/%Y')
            fecha_nacimiento = None
            if sipersona.fecha_nacimiento:
                fecha_nacimiento = sipersona.fecha_nacimiento.strftime('%d/%m/%Y')
            data = {
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
                'fecha_caducidad': fecha_caducidad,
                'fecha_nacimiento': fecha_nacimiento
            }
        return existe, data

    def set_persona_simintra(self, datos_se):
        if not datos_se:
            return datos_se
        codigo_departamento = None
        codigo_provincia = None
        codigo_distrito = None
        departamento = Departamento.objects.filter(
            codigo_departamento_ren=datos_se.get('codigo_departamento_ren'))
        if departamento.exists():
            departamento = departamento.last()
            codigo_departamento = departamento.codigo_departamento
            provincia = Provincia.objects.filter(
                codigo_departamento=codigo_departamento,
                codigo_provincia_ren=datos_se.get('codigo_provincia_ren')
            )
            if provincia.exists():
                provincia = provincia.last()
                codigo_provincia = provincia.codigo_provincia
                distrito = Distrito.objects.filter(
                    codigo_departamento=codigo_departamento,
                    codigo_provincia=codigo_provincia,
                    codigo_distrito_ren=datos_se.get('codigo_distrito_ren')
                )
                if distrito.exists():
                    distrito = distrito.last()
                    codigo_distrito = distrito.codigo_distrito

        vals_persona = {
            'tipo_documento': datos_se.get('tipo_documento'),
            'codigo_personal': datos_se.get('numero_documento'),
            'apellido_paterno': datos_se.get('apellido_paterno'),
            'apellido_materno': datos_se.get('apellido_materno'),
            'nombres': datos_se.get('nombres'),
            'codigo_pais': datos_se.get('pais_nacimiento'),
            'codigo_departamento': codigo_departamento,
            'codigo_provincia': codigo_provincia,
            'codigo_distrito': codigo_distrito,
            'fecha_nacimiento': datetime.strptime(datos_se.get('fecha_nacimiento'), '%d/%m/%Y'),
            'fecha_caducidad': datetime.strptime(datos_se.get('fecha_caducidad'), '%d/%m/%Y'),
            'sexo': datos_se.get('sexo'),
            'estado_civil': datos_se.get('estado_civil'),
            'usuario_creacion': 'ATCOADLASYS',
            'usuario_modificacion': 'ATCOADLASYS',
            'fecha_creacion': datetime.now(),
            'fecha_modificacion': datetime.now(),
            # 'host_registro': self.request.META.get('HTTP_HOST'),
            # 'host_modificacion': self.request.META.get('HTTP_HOST'),
            'sistema_registro': CODIGO_SISTEMA,
            'sistema_modificacion': CODIGO_SISTEMA,
            'flag': '1'
        }
        sipersona, _ = SiPersona.objects.get_or_create(**vals_persona)
        return vals_persona

    def validar_trabajador_simintra(self, codigo_personal):
        sitrabajador = SiTrabajador.objects.filter(codigo_trabajador=codigo_personal)
        existe = False
        data = {}
        if sitrabajador.exists():
            existe = True
            sitrabajador = sitrabajador.last()
            fecha_nacimiento = None
            if sitrabajador.fecha_nacimiento:
                fecha_nacimiento = sitrabajador.fecha_nacimiento.strftime('%d/%m/%Y')
            data = {
                'simintra': constants.SI_CHAR_BINARY,
                'tipo_documento': sitrabajador.tipo_documento,
                'codigo_trabajador': codigo_personal,
                'nombres': sitrabajador.nombres,
                'apellido_paterno': sitrabajador.apellido_paterno,
                'apellido_materno': sitrabajador.apellido_materno,
                'codigo_departamento': sitrabajador.codigo_departamento,
                'codigo_provincia': sitrabajador.codigo_provincia,
                'codigo_distrito': sitrabajador.codigo_distrito,
                'genero': sitrabajador.genero,
                'fecha_nacimiento': fecha_nacimiento,
                'email': sitrabajador.email,
                'codigo_nacion': sitrabajador.codigo_nacion,
                'direccion': sitrabajador.direccion
            }
        return existe, data

    def set_trabajador_simintra(self, data_persona, email):
        nacionalidades = Nacionalidad.objects.filter(codigo_nacionalidad=data_persona.get('codigo_pais'))
        codigo_nacion = False
        genero = 'M' if data_persona.get('sexo') == '1' else 'F'
        if nacionalidades.exists():
            nacionalidad = nacionalidades.first()
            codigo_nacion = nacionalidad.codigo_nacionalidad
        try:
            departamento = Departamento.objects.get(codigo_departamento_ren=data_persona.get('codigo_departamento'))
            codigo_departamento = departamento.codigo_departamento
        except Exception:
            codigo_departamento = None
        try:
            provincia = Provincia.objects.get(
                codigo_departamento_ren=data_persona.get('codigo_departamento'),
                codigo_provincia_ren=data_persona.get('codigo_provincia')
            )
            codigo_provincia = provincia.codigo_provincia
        except Exception:
            codigo_provincia = None
        try:
            distrito = Distrito.objects.get(
                codigo_departamento_ren=data_persona.get('codigo_departamento'),
                codigo_provincia_ren=data_persona.get('codigo_provincia'),
                codigo_distrito_ren=data_persona.get('codigo_distrito')
            )
            codigo_distrito = distrito.codigo_distrito
        except Exception:
            codigo_distrito = None
        try:
            fecha_nacimiento = datetime.strptime(data_persona.get('fecha_nacimiento'), '%d/%m/%Y').strftime('%Y-%m-%d')
        except:
            fecha_nacimiento = data_persona.get('fecha_nacimiento')
        vals = {
            'tipo_documento': data_persona.get('tipo_documento'),
            'codigo_trabajador': data_persona.get('codigo_personal'),
            'nombres': data_persona.get('nombres'),
            'apellido_paterno': data_persona.get('apellido_paterno'),
            'apellido_materno': data_persona.get('apellido_materno'),
            'genero': genero,
            'fecha_nacimiento': fecha_nacimiento,
            'email': email,
            'direccion': '-'
        }
        if codigo_nacion:
            vals.update({'codigo_nacion': codigo_nacion, })
        if codigo_departamento:
            vals.update({'codigo_departamento': codigo_departamento, })
        if codigo_provincia:
            vals.update({'codigo_provincia': codigo_provincia, })
        if codigo_distrito:
            vals.update({'codigo_distrito': codigo_distrito, })
        trabajador, _ = SiTrabajador.objects.get_or_create(**vals)
        return vals

    def validar_personal_simintra(self, codigo_personal):
        tpersonal = TPersonal.objects.filter(codigo_personal=codigo_personal)
        existe = False
        data = {}
        if tpersonal.exists():
            existe = True
            tpersonal = tpersonal.last()
            data = {
                'simintra': constants.SI_CHAR_BINARY,
                'codigo_personal': tpersonal.codigo_personal,
                'codigo_dependencia': tpersonal.codigo_dependencia,
                'codigo_cargo': tpersonal.codigo_cargo,
                'codigo_escala': tpersonal.codigo_escala,
                'apellido_paterno': tpersonal.apellido_paterno,
                'apellido_materno': tpersonal.apellido_materno,
                'nombres': tpersonal.nombres,
                'email': tpersonal.email,
                'flag': tpersonal.flag,
            }
        return existe, data

    def set_personal_simintra(self, data, email, codigo_dependencia, codigo_cargo, codigo_escala):
        vals = {
            'codigo_personal': data.get('codigo_personal'),
            'codigo_dependencia': codigo_dependencia,
            'nombres': data.get('nombres'),
            'codigo_cargo': codigo_cargo,
            'codigo_escala': codigo_escala,
            'apellido_paterno': data.get('apellido_paterno'),
            'apellido_materno': data.get('apellido_materno'),
            'email': email,
            'flag': constants.SI_CHAR_BINARY
        }
        tpersonal, _ = TPersonal.objects.get_or_create(**vals)
        return vals

    def verificar_usuario_servicio_consultas(self, tipo_usuario, tipo_documento, numero_documento):
        if tipo_usuario == constants.TIPO_USUARIO_PERSONA:
            if tipo_documento == constants.TIPO_DOCUMENTO_DNI:
                results = ServiciosExternos.verificar_identidad_reniec(ServiciosExternos(), numero_documento)
            elif tipo_documento == constants.TIPO_DOCUMENTO_CE:
                results = ServiciosExternos.verificar_identidad_ce(ServiciosExternos(), numero_documento)
            elif tipo_documento == constants.TIPO_DOCUMENTO_PTP:
                results = ServiciosExternos.verificar_identidad_ptp(ServiciosExternos(), numero_documento)
            elif tipo_documento == constants.TIPO_DOCUMENTO_CPP:
                results = ServiciosExternos.verificar_identidad_cpp(ServiciosExternos(), numero_documento)
            elif tipo_documento in (
                constants.TIPO_DOCUMENTO_PASAPORTE,
                constants.TIPO_DOCUMENTO_CSR,
                constants.TIPO_DOCUMENTO_CEDULA_IDENTIDAD
            ):
                results = (False, tipo_documento)
            else:
                results = (False, constants.TIPO_DOCUMENTO_NA)
        elif tipo_usuario == constants.TIPO_USUARIO_EMPRESA:
            results = ServiciosExternos.verificar_identidad_ruc(ServiciosExternos(), numero_documento)
            # secundarios = ServiciosExternos.verificar_datos_secundarios_ruc(numero_documento)
        else:
            results = (False, constants.TIPO_USUARIO_NA)
        return results

    def get_usuario_id(
        self,
        username,
        password,
        celular=None,
        email=None,
        terminos_condiciones=constants.NO_CHAR_BINARY,
        compartir_datos=constants.NO_CHAR_BINARY,
        tipo_usuario=constants.NO_CHAR_BINARY,
        usuario_interno=None,
        activo=False,
        skip_password=False,
        reset_password=False,
        auto_password=False,
        admin_creation=False,
        tipo_documento=None,
        numero_documento=None,
        pk_grupo=False,
        codigo_dependencia=None,
        codigo_sede=None,
        codigo_institucion=None,
        codigo_region=None,
        codigo_cargo=None,
        codigo_escala=None,
        super_admin=False,
        usuario_creador=None
    ):
        nuevo = False
        try:
            usuario = User.objects.filter(
                Q(pk_usuario=username) | Q(username=username)
            )
            if activo:
                usuario_activo = usuario.filter(flag=constants.SI_CHAR_BINARY)
                usuario_inactivo = usuario.filter(flag=constants.NO_CHAR_BINARY)
                if usuario_activo.exists():
                    usuario_activo = usuario_activo.first()
                    return usuario_activo.pk, 'Usuario existe y está activo', nuevo
                elif usuario_inactivo.exists():
                    usuario_inactivo = usuario_inactivo.first()
                    return usuario_inactivo.pk, 'Usuario existe pero no está activo', nuevo
                else:
                    return None, 'Usuario no existe y no está activo', nuevo
            if username.isdigit() and usuario.exists() and not usuario.last().password and usuario_interno == constants.SI_CHAR_BINARY:
                return None, f'El usuario es un especialista', False
            si_usuario = SiUsuario.objects.filter(
                Q(codigo_personal=username) | Q(codigo_usuario=username)
            )
            valido, datos = self.verificar_usuario_servicio_consultas(tipo_usuario, tipo_documento, username)
            # valido, datos = ServiciosExternos.verificar_identidad_reniec(ServiciosExternos(), username)
            si_usuario = si_usuario.filter(password_usuario__isnull=False)
            if si_usuario.exists():
                si_pass = ServiciosInternos.decode(
                    ServiciosInternos(),
                    si_usuario.last().codigo_usuario,
                    si_usuario.last().password_usuario,
                )
                if not reset_password and not skip_password and password != si_pass and not auto_password:
                    return None, f'El usuario existe y su contraseña no es válida.', nuevo
                codigo_usuario = username
                if admin_creation:
                    if valido:
                        codigo_usuario = '{}{}'.format(datos['nombres'][0], datos['apellido_paterno'])
                usuario = self.set_usuario_local(
                    si_usuario.first().codigo_personal, codigo_usuario, tipo_usuario,
                    celular, email, codigo_sede=codigo_sede, codigo_dependencia=codigo_dependencia,
                    siusuario_existe=True, super_admin=super_admin,codigo_region=codigo_region,
                    codigo_institucion=codigo_institucion,compartir_datos=compartir_datos)
                if reset_password and password != si_pass:
                    siusuario = si_usuario.last()
                    coded_pass = ServiciosInternos.encode(
                        ServiciosInternos(), siusuario.codigo_usuario, password
                    )
                    siusuario.password_usuario = coded_pass
                    siusuario.save()
                    usuario.flag = constants.SI_CHAR_BINARY if usuario else constants.NO_CHAR_BINARY
                    usuario.compartir_datos = constants.SI_CHAR_BINARY
                    usuario.save()
                # else:
                #     return None, f'La contraseña no debe ser la misma', nuevo
            else:
                usuario = User.objects.filter(pk_usuario=username)
                # if usuario_creador:
                #     region = SiRegional.objects.filter(codigo_region=codigo_region)
                if not usuario.exists():
                    if skip_password:
                        return None, f'El usuario no existe.', nuevo
                    codigo_usuario = username
                    if valido:
                        # Se construye el username para el usuario
                        if not datos.get('apellido_paterno'):
                            return None, f'El Usuario no ha sido identificado en el sistema para acceder. Comprobar si ha sido registrado.', nuevo
                        codigo_usuario = '{}{}'.format(datos['nombres'][0], datos['apellido_paterno'])
                        sufijo_usuario = '{}'.format((datos.get('apellido_materno') or ['X'])[0])
                        usuario_coincidente = SiUsuarioTotal.objects.filter(
                            codigo_usuario=codigo_usuario.replace('Ñ', 'N'))
                        if usuario_coincidente.exists():
                            codigo_usuario = '{}{}'.format(codigo_usuario, sufijo_usuario)
                    else:
                        datos = {}
                    coded_pass = ServiciosInternos.encode(ServiciosInternos(), codigo_usuario, password)
                    if not admin_creation:
                        return (
                            None,
                            f'El usuario no existe, debe primero registrarse.',
                            nuevo,
                        )
                    if not email:
                        return (
                            None,
                            f'El Email es un dato obligatorio para crear el usuario.',
                            nuevo,
                        )
                    # Usuario SIMINTRA
                    if usuario_interno == constants.NO_CHAR_BINARY:

                        # Buscar/Crear Persona en SIMINTRA1
                        numero_documento = numero_documento or username
                        existe_persona, data_persona = self.validar_persona_simintra(tipo_documento, numero_documento)
                        if not existe_persona:
                            data_persona = self.set_persona_simintra(datos_se=datos)
                        else:
                            if codigo_usuario == username:
                                codigo_usuario = '{}{}'.format(data_persona['nombres'][0], data_persona['apellido_paterno'])
                                sufijo_usuario = '{}'.format((data_persona.get('apellido_materno') or ['X'])[0])
                                usuario_coincidente = SiUsuarioTotal.objects.filter(
                                    codigo_usuario=codigo_usuario.replace('Ñ', 'N')
                                )
                                if usuario_coincidente.exists():
                                    codigo_usuario = '{}{}'.format(codigo_usuario, sufijo_usuario)
                            else:
                                usuario_coincidente = SiUsuarioTotal.objects.filter(
                                    codigo_usuario=codigo_usuario.replace('Ñ', 'N')
                                )
                                sufijo_usuario = '{}'.format((data_persona.get('apellido_materno') or ['X'])[0])
                                if usuario_coincidente.exists():
                                    codigo_usuario = '{}{}'.format(codigo_usuario, sufijo_usuario)

                        # Si pese a ello no hay data de persona
                        if not data_persona:
                            return (
                                None,
                                f'El usuario con numero de documento {numero_documento} NO se encuentra',
                                nuevo,
                            )

                        # Buscar/Crear Trabajador en SIMINTRA1
                        existe_trabajador, data_trabajador = self.validar_trabajador_simintra(numero_documento)
                        if not existe_trabajador:
                            if not data_persona.get('codigo_pais'):
                                data_persona.update({'codigo_pais': datos.get('pais_nacimiento')})
                            if not data_persona.get('codigo_departamento'):
                                data_persona.update({'codigo_departamento': datos.get('codigo_departamento_ren')})
                            if not data_persona.get('codigo_provincia'):
                                data_persona.update({'codigo_provincia': datos.get('codigo_provincia_ren')})
                            if not data_persona.get('codigo_distrito'):
                                data_persona.update({'codigo_distrito': datos.get('codigo_distrito_ren')})
                            data_trabajador = self.set_trabajador_simintra(data_persona=data_persona, email=email)

                        # Buscar/Crear Personal en SIMINTRA1
                        existe_personal, data_personal = self.validar_personal_simintra(numero_documento)
                        if not existe_personal:
                            codigo_dependencia = codigo_dependencia or 152
                            if not data_trabajador.get('apellido_materno'):
                                data_trabajador.update({
                                    'apellido_materno': '.'
                                })
                            data_trabajador.update({
                                'codigo_personal': data_trabajador.get('codigo_trabajador')
                            })
                            personal = self.set_personal_simintra(
                                data=data_trabajador, email=email, codigo_dependencia=codigo_dependencia,
                                codigo_cargo=codigo_cargo, codigo_escala=codigo_escala
                            )

                        # Crear usuario en el SIMINTRA1
                        usuario = SiUsuarioTotal.objects.filter(
                            codigo_usuario=codigo_usuario.replace('Ñ', 'N')
                        )
                        if usuario.exists():
                            usuario = usuario.filter(
                                codigo_usuario=codigo_usuario.replace('Ñ', 'N')
                            )
                            # Validamos que no sea el mismo usuario pero desactivado
                            if usuario.exists():
                                usuario = usuario.filter(flag='N')
                                if usuario.exists():
                                    return (
                                        None,
                                        f'El usuario existe en la BD del SIMINTRA pero está inactivo',
                                        nuevo,
                                    )
                                else:
                                    usuario = usuario.first()
                            else:

                                sufijo_usuario_2 = '{}'.format((data_persona.get('apellido_materno') or ['X'])[1])
                                codigo_usuario = '{}{}'.format(codigo_usuario.replace('Ñ', 'N'), sufijo_usuario_2)
                                usuarios_disponibles = SiUsuarioTotal.objects.filter(
                                    codigo_usuario__icontains=codigo_usuario
                                )

                                codigo_usuario = self.generar_codigo_unico(
                                    codigo_usuario, usuarios_disponibles)

                                data_usuario = {
                                    'codigo_usuario': codigo_usuario,
                                    'codigo_personal': username,
                                    'password_usuario': coded_pass,
                                    'flag': 'S'
                                }
                                si_usuarios = SiUsuarioTotal.objects.filter(
                                    codigo_usuario=codigo_usuario,
                                    codigo_personal=username
                                )
                                if si_usuarios.exists():
                                    nuevo = False
                                    if si_usuarios.last().flag == 'N':
                                        return (
                                            None,
                                            f'El usuario {codigo_usuario} '
                                            f'está en la BD del SIMINTRA1 pero está inactivo.',
                                            nuevo,
                                        )
                                    usuario = si_usuarios.last()
                                else:
                                    usuario, nuevo = SiUsuario.objects.get_or_create(**data_usuario)

                        else:

                            data_usuario = {
                                'codigo_usuario': codigo_usuario.replace('Ñ', 'N'),
                                'codigo_personal': username,
                                'password_usuario': coded_pass,
                                'flag': 'S'
                                # ToDo: Colocar los datos de host e ip de registro
                            }
                            si_usuarios = SiUsuario.objects.filter(
                                codigo_usuario=codigo_usuario.replace('Ñ', 'N'),
                                codigo_personal=username
                            )
                            if si_usuarios.exists():
                                nuevo = False
                                usuario = si_usuarios.last()
                            else:
                                usuario, nuevo = SiUsuario.objects.get_or_create(**data_usuario)

                            # Crear usuario en SCALVIR
                            self.set_usuario_local(
                                codigo_personal=usuario.codigo_personal, username=usuario.codigo_usuario,
                                codigo_sede=codigo_sede,compartir_datos=compartir_datos,codigo_region=codigo_region,
                                codigo_institucion=codigo_institucion,tipo_usuario=tipo_usuario, celular=celular,
                                email=email, super_admin=super_admin)

                            # Crear UsuarioxSistema
                            data_ususist = {
                                'codigo_usuario': usuario.codigo_usuario,
                                'codigo_sistema': CODIGO_SISTEMA,
                                'flag': 'S'
                                # ToDo: Colocar los datos de host e ip de registro
                            }
                            ususistema, nuevo = SiUsuSistema.objects.get_or_create(**data_ususist)

                        # Crear/Modificar UsuarioxPerfil
                        if pk_grupo:
                            data_usuperfil = {
                                'codigo_usuario': usuario.codigo_usuario,
                                'codigo_sistema': CODIGO_SISTEMA,
                                'flag': 'S',
                                'codigo_perfil': str(pk_grupo).rjust(3, '0')
                                # ToDo: Colocar los datos de host e ip de registro
                            }
                            usu_perfiles = SiUsuPerfil.objects.filter(
                                codigo_sistema=CODIGO_SISTEMA,
                                codigo_usuario=usuario.codigo_usuario
                            )
                            if usu_perfiles.exists():
                                usu_perfiles = usu_perfiles.filter(codigo_perfil=str(pk_grupo).rjust(3, '0'))
                                if not usu_perfiles.exists():
                                    usu_perfiles.update(flag='E')
                                    usuperfil, nuevo = SiUsuPerfil.objects.get_or_create(**data_usuperfil)
                                else:
                                    usu_perfiles.exclude(codigo_perfil=str(pk_grupo).rjust(3, '0')).update(flag='E')
                            else:
                                usuperfil, nuevo = SiUsuPerfil.objects.get_or_create(**data_usuperfil)
                        # return None, 'El usuario no existe', nuevo
                    else:
                        data_usuario = {
                            'pk_usuario': username,
                            'username': codigo_usuario,
                            'password': coded_pass,
                            'email': email,
                            'codigo_region': codigo_region,
                            'codigo_institucion': codigo_institucion,
                            'celular': celular,
                            'terminos_condiciones': terminos_condiciones,
                            'compartir_datos': compartir_datos,
                            # ToDo: Colocar los datos de host e ip de registro
                        }
                        usuario, nuevo = User.objects.get_or_create(**data_usuario)
                        usuario.tipo_usuario = tipo_usuario
                        usuario.save()
                else:
                    usuario = usuario.first()
                    if usuario_interno == constants.NO_CHAR_BINARY and str(usuario.pk_usuario) == username:
                        return (
                            None,
                            f'El usuario es un usuario interno, no un especialista',
                            nuevo,
                        )
                    if not usuario.password:
                        return (
                            None,
                            f'El usuario no se encuentra en la BD del SIMINTRA.',
                            nuevo,
                        )
                    decoded_pass = ServiciosInternos.decode(
                        ServiciosInternos(), str(usuario.pk_usuario), usuario.password
                    )
                    if password != decoded_pass and reset_password:
                        coded_pass = ServiciosInternos.encode(
                            ServiciosInternos(), username, password
                        )
                        usuario.password = coded_pass
                        usuario.save()
                    elif password != decoded_pass and not skip_password:
                        return (
                            None,
                            f'Contraseña no es válida.',
                            nuevo,
                        )
            try:
                if super_admin:
                    usuario.super_admin = constants.SI_CHAR_BINARY
                elif not super_admin and usuario.super_admin and not bool(int(usuario.super_admin)):
                    usuario.super_admin = constants.NO_CHAR_BINARY
                usuario.save()
            except Exception:
                usuario.save()
            try:
                pk_user = usuario.pk_usuario
            except Exception:
                pk_user = usuario.codigo_personal
            return pk_user, 'Usuario encontrado.', nuevo
        except Exception as e:
            return None, str(e), nuevo

    def generar_codigo_unico(self, codigo_original, queryset_disponibles):
        while True:
            # Generar un sufijo aleatorio
            sufijo_aleatorio = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

            # Concatenar el sufijo aleatorio al código original
            nuevo_codigo = '{}{}'.format(codigo_original, sufijo_aleatorio)

            # Verificar si el nuevo código ya existe en el queryset
            if not queryset_disponibles.filter(codigo_usuario=nuevo_codigo).exists():
                return nuevo_codigo


    def get_method(self, request):
        metodo = request._request.method
        return metodo

    def get_usuario_perfil(self, pk_usuario, id_aplicacion):
        codigo_usuario = (
            SiUsuario.objects.filter(codigo_personal=pk_usuario).first().codigo_usuario
        )
        usuario_perfiles = SiUsuPerfil.objects.filter(
            codigo_usuario=codigo_usuario, codigo_sistema=id_aplicacion, flag='S'
        )
        if not usuario_perfiles.exists():
            return None
        codigo_perfil = usuario_perfiles.first().codigo_perfil
        for usuario_perfil in usuario_perfiles:
            perfiles = SiPerfil.objects.filter(
                codigo_sistema=id_aplicacion, codigo_perfil=usuario_perfil.codigo_perfil
            )
            if perfiles.exists():
                # Solo 1 rol por usuario
                codigo_perfil = perfiles.first().codigo_perfil
                break
            else:
                codigo_perfil = usuario_perfil.codigo_perfil
        usuario_perfil = usuario_perfiles.filter(codigo_perfil=codigo_perfil).first()
        return usuario_perfil

    def get_grupo_usuario(self, pk_usuario):
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

    def get_rol_menues(self, usuario, id_aplicacion):
        pk_usuario = usuario.first().pk if usuario.exists() else None
        perfil_menu = {}
        usuario_perfil = self.get_usuario_perfil(pk_usuario, id_aplicacion)
        codigo_perfil = usuario_perfil.codigo_perfil if usuario_perfil else None
        grupos = Group.objects.filter(pk=codigo_perfil)
        if not grupos.exists():
            return None, {}
        grupo_menus = MenuGroup.objects.filter(grupo=grupos.first())
        if not grupo_menus.exists():
            return grupos.first().pk, {}

        # Evaluar si el Usuario tiene un Set de Menues específico
        menu_usuario, menu_list, pk_grupo = self.get_grupo_usuario(pk_usuario)
        list_submenues = []
        if menu_usuario:
            menus = Menu.objects.filter(pk_menu__in=menu_list).order_by('pk_menu')
            menus = menus.filter(url='/inicio/')
            if not menus.exists():
                return grupos.first().pk, perfil_menu
            menu = menus.first()
            vals = {
                'id': menu.pk_menu,
                'url': menu.url,
                'nombre': menu.nombre,
            }
            submenus = Menu.objects.filter(
                parent=menu.pk_menu,
                pk_menu__in=menu_list
            ).order_by('pk_menu')
            for submenu in submenus:
                val_submenu = {
                    'id': submenu.pk_menu,
                    'url': submenu.url,
                    'nombre': submenu.nombre,
                }
                list_submenues.append(val_submenu)
                inframenus = Menu.objects.filter(
                    parent=submenu.pk_menu,
                    pk_menu__in=menu_list
                ).order_by('pk_menu')
                list_inframenues = []
                for inframenu in inframenus:
                    val_inframenu = {
                        'id': inframenu.pk_menu,
                        'url': inframenu.url,
                        'nombre': inframenu.nombre,
                    }
                    list_inframenues.append(val_inframenu)
                val_submenu.update({'menues': list_inframenues})
                # ToDo: Agregar ultimo Nivel de Menues. Acciones.
        else:
            # Solo 1 grupo_menu por grupo de rol
            grupo_menus = grupo_menus.order_by('menu__pk_menu')
            grupo_menus = grupo_menus.filter(menu__url='/inicio/')
            if not grupo_menus.exists():
                return grupos.first().pk, perfil_menu
            grupo_menu = grupo_menus.first()
            vals = {
                'id': grupo_menu.menu.pk_menu,
                'url': grupo_menu.menu.url,
                'nombre': grupo_menu.menu.nombre,
            }
            grupo_submenus = MenuGroup.objects.filter(
                grupo=grupo_menu.grupo,
                menu__parent=grupo_menu.menu
            )
            for grupo_submenu in grupo_submenus:
                val_submenu = {
                    'id': grupo_submenu.menu.pk_menu,
                    'url': grupo_submenu.menu.url,
                    'nombre': grupo_submenu.menu.nombre,
                }
                list_submenues.append(val_submenu)
                grupo_inframenus = MenuGroup.objects.filter(
                    grupo=grupo_menu.grupo,
                    menu__parent=grupo_submenu.menu,
                )
                list_inframenues = []
                for grupo_inframenu in grupo_inframenus:
                    val_inframenu = {
                        'id': grupo_inframenu.menu.pk_menu,
                        'url': grupo_inframenu.menu.url,
                        'nombre': grupo_inframenu.menu.nombre,
                    }
                    list_inframenues.append(val_inframenu)

                    grupo_acciones = MenuGroup.objects.filter(
                        grupo=grupo_menu.grupo,
                        menu__parent=grupo_inframenu.menu,
                    )
                    list_acciones = []
                    for grupo_accion in grupo_acciones:
                        val_accion = {
                            'id': grupo_accion.menu.pk_menu,
                            'url': grupo_accion.menu.url,
                            'nombre': grupo_accion.menu.nombre,
                        }
                        list_acciones.append(val_accion)
                    val_inframenu.update({'menues': list_acciones})

                val_submenu.update({'menues': list_inframenues})

        vals.update({'menues': list_submenues})
        perfil_menu.update(vals)
        return grupos.first().pk, perfil_menu

    def validar_token_publico(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            return False
        if token.find('Bearer ') >= 0:
            token = token.replace('Bearer ', '')
        if self.is_sha256(token):
            vals = {
                'codigo': constants.ANONYMOUS_USER,
                'valor': f'{token}',
            }
            parametros = Parametro.objects.filter(**vals)
            if not parametros.exists():
                return False
            return True

    def generate_random_password(self, length=8):
        characters = string.ascii_letters + string.digits
        password = ''.join(random.choice(characters) for _ in range(length))
        return password

    def validar_token_general(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token and token.find('Bearer ') >= 0:
            token = token.replace('Bearer ', '')
        parametro = Parametro.objects.filter(valor=token)
        if not parametro.exists():
            return False
        return True

    def authenticate(self, request):
        valido_token_general = self.validar_token_general(request)
        if not valido_token_general:
            raise exceptions.AuthenticationFailed(
                'Las credenciales públicas o privadas no existen o expiraron.'
            )
        objse = ServiciosExternos()
        username = request.data.get('username')
        password = request.data.get('password')
        tipo_usuario = request.data.get('tipo_usuario')
        tipo_documento = request.data.get('tipo_documento')
        usuario_interno = request.data.get('usuario_interno')

        admin_creation = False
        if request.data.get('admin_creation', ''):
            if bool(int(request.data.get('admin_creation', '0'))):
                admin_creation = True

        auto_password = False
        if request.data.get('auto_password', ''):
            if bool(int(request.data.get('auto_password', '0'))):
                auto_password = True

        skip_password = False
        if request.data.get('skip_password', ''):
            if bool(int(request.data.get('skip_password', '0'))):
                skip_password = True

        reset_password = False
        if request.data.get('reset_password', ''):
            if bool(int(request.data.get('reset_password', '0'))):
                reset_password = True

        super_admin = False
        if request.data.get('super_admin', ''):
            if bool(int(request.data.get('super_admin', '0'))):
                super_admin = True

        results = False, {}  # type: ignore

        if not username and not admin_creation:
            raise exceptions.NotAcceptable('Ingresar datos del usuario.')
        if not password and auto_password:
            password = self.generate_random_password(length=8)
        elif not skip_password and not password and not auto_password:
            raise exceptions.NotAcceptable('Ingresar la contraseña.')
        if not tipo_usuario:
            raise exceptions.NotAcceptable('Ingresar el Tipo de Usuario.')
        # if not tipo_documento:
        #    raise exceptions.NotAcceptable('Ingresar el tipo de documento.')
        if tipo_usuario == constants.TIPO_USUARIO_EMPRESA and tipo_documento != constants.TIPO_DOCUMENTO_RUC:
            raise exceptions.NotAcceptable('Si el tipo de usuario es Empresa, el Tipo de documento debe ser RUC.')
        if tipo_usuario == constants.TIPO_USUARIO_PERSONA and tipo_documento == constants.TIPO_DOCUMENTO_RUC:
            raise exceptions.NotAcceptable('Si el tipo de usuario es Persona, el Tipo de documento No puede ser RUC.')

        if usuario_interno == constants.SI_CHAR_BINARY or (usuario_interno == constants.NO_CHAR_BINARY and skip_password):
            numero_documento = username
        elif usuario_interno == constants.NO_CHAR_BINARY and not admin_creation:
            si_usuario = SiUsuario.objects.filter(codigo_usuario=username)
            numero_documento = (
                si_usuario.last().codigo_personal if si_usuario.exists() else None
            )
        elif usuario_interno == constants.NO_CHAR_BINARY and admin_creation:
            numero_documento = username
        else:
            numero_documento = username

        # Evaluar si el usuario ya existe o está activo
        usuario_id, mssg, nuevo_usuario = self.get_usuario_id(
            username,
            password,
            tipo_usuario=tipo_usuario,
            usuario_interno=usuario_interno,
            activo=True,
            tipo_documento=tipo_documento,
            numero_documento=numero_documento
        )
        skip_results = False
        if usuario_id:
            usuario_scalvir = User.objects.get(pk=usuario_id)
            tipo_documento = usuario_scalvir.tipo_documento
        elif not tipo_documento and not usuario_id:
            raise exceptions.NotAcceptable('Ingresar el tipo de documento para registrar al usuario.')
        if usuario_id and not nuevo_usuario:
            skip_results = True

        secundarios = (False, '')
        if tipo_usuario == constants.TIPO_USUARIO_PERSONA:
            if tipo_documento == constants.TIPO_DOCUMENTO_DNI:
                results = objse.verificar_identidad_reniec(numero_documento)
            elif tipo_documento == constants.TIPO_DOCUMENTO_CE:
                results = objse.verificar_identidad_ce(numero_documento)
            elif tipo_documento == constants.TIPO_DOCUMENTO_PTP:
                results = objse.verificar_identidad_ptp(numero_documento)
            elif tipo_documento == constants.TIPO_DOCUMENTO_CPP:
                results = objse.verificar_identidad_cpp(numero_documento)
            elif tipo_documento in (
                constants.TIPO_DOCUMENTO_PASAPORTE,
                constants.TIPO_DOCUMENTO_CSR,
                constants.TIPO_DOCUMENTO_CEDULA_IDENTIDAD
            ):
                results = (False, tipo_documento)
            else:
                results = (False, constants.TIPO_DOCUMENTO_NA)
        elif tipo_usuario == constants.TIPO_USUARIO_EMPRESA:
            results = objse.verificar_identidad_ruc(numero_documento)
            secundarios = objse.verificar_datos_secundarios_ruc(numero_documento)
        else:
            results = (False, constants.TIPO_USUARIO_NA)

        usuario_creador = ServiciosInternos.get_usuario_token(request)
        usuario_id, mssg, nuevo = self.get_usuario_id(
            username,
            password,
            celular=request.data.get('celular'),
            email=request.data.get('email'),
            compartir_datos=request.data.get('compartir_datos'),
            terminos_condiciones=request.data.get('terminos_condiciones'),
            tipo_usuario=tipo_usuario,
            codigo_region= request.data.get('codigo_region'),
            usuario_interno=usuario_interno,
            pk_grupo=request.data.get('pk_grupo'),
            codigo_dependencia=request.data.get('codigo_dependencia'),
            # codigo_sede=request.data.get('codigo_sede'),
            codigo_cargo=request.data.get('codigo_cargo'),
            codigo_escala=request.data.get('codigo_escala'),
            codigo_institucion= request.data.get('codigo_institucion'),
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            skip_password=skip_password,
            reset_password=reset_password,
            auto_password=auto_password,
            admin_creation=admin_creation,
            super_admin=super_admin,
            usuario_creador=usuario_creador
        )
        if not usuario_id:
            raise exceptions.AuthenticationFailed(
                detail=f'Las credenciales no son correctas o no existen: {mssg}',
                code=HTTP_401_UNAUTHORIZED)

        usuario = User.objects.filter(pk_usuario=usuario_id)
        token = self.generar_token(username=usuario.last().username, hours=24)
        # token = secrets.token_urlsafe(160)
        cache.set(SCALVIR_CACHE_KEY, token, 60 * 1 * 1)
        id_aplicacion = CODIGO_SISTEMA

        if cache.get(SCALVIR_CACHE_KEY):
            token_cache = cache.get(SCALVIR_CACHE_KEY)
        else:
            token_cache = None

        pk_grupo, perfil_menu = self.get_rol_menues(
            usuario, id_aplicacion
        )
        if usuario.exists():
            usuario_object = usuario.last()
            usuario_object.tipo_documento = tipo_documento
            usuario_object.save()

        grupos = Group.objects.filter(pk_grupo=pk_grupo)
        nombre_grupo = grupos.first().nombre if grupos.exists() else '-'

        personal = TPersonal.objects.filter(codigo_personal=usuario.last().pk_usuario)
        codigo_dependencia = None
        nombre_dependencia = None
        # if personal.exists():
            # codigo_dependencia = personal.first().codigo_dependencia
            # dependencia = SiDependencia.objects.filter(codigo_dependencia=codigo_dependencia)
            # nombre_dependencia = dependencia.first().dependencia if dependencia.exists() else None
        try:
            codigo_sede = usuario.last().sede.codigo_sede if usuario.last().sede else ''
            nombre_sede = usuario.last().sede.descripcion_sede if usuario.last().sede else ''
        except Exception:
            codigo_sede = None
            nombre_sede = None
        try:
            codigo_region = self.get_codigo_region(usuario.last())
            nombre_region = self.get_nombre_region(usuario.last())
        except Exception:
            codigo_region = None
            nombre_region = None
        try:
            codigo_institucion = self.get_codigo_institucion(usuario.last())
            nombre_institucion = self.get_nombre_institucion(usuario.last())
        except Exception:
            codigo_institucion = None
            nombre_institucion = None
        try:
            codigo_zona = self.get_codigo_zona(usuario.last())
            nombre_zona = self.get_nombre_zona(usuario.last())
        except Exception:
            codigo_zona = None
            nombre_zona = None
        flag = usuario.last().flag
        compartir_datos = usuario.last().compartir_datos
        if compartir_datos == constants.NO_CHAR_BINARY and flag == constants.NO_CHAR_BINARY:
            nuevo = True
        elif compartir_datos == constants.SI_CHAR_BINARY and flag == constants.SI_CHAR_BINARY:
            nuevo = False
        elif compartir_datos == constants.SI_CHAR_BINARY and flag == constants.NO_CHAR_BINARY:
            nuevo = False
        else:
            nuevo = nuevo
        if results[0]:
            datos = {
                'tipo_documento': usuario.last().tipo_documento,
                'numero_documento': usuario.last().pk_usuario,
                'codigo_trabajador': usuario.last().pk_usuario,
                'username': usuario.last().username,
                'codigo_region': codigo_region,
                'nombre_region': nombre_region,
                'codigo_institucion':codigo_institucion,
                'nombre_institucion': nombre_institucion,
                'nombres': results[1].get(
                    'nombres', results[1].get('razon_social', '')
                ),
                'apellido_paterno': results[1].get('apellido_paterno', ''),
                'apellido_materno': results[1].get('apellido_materno', ''),
                'id_aplicacion': id_aplicacion,
                'pk_grupo': pk_grupo,
                'nombre_grupo': nombre_grupo,
                'rol_menues': perfil_menu,
                'token_cache': f'{token_cache}',
                'nuevo': nuevo,
                'estado': flag,
                'tipo_usuario': usuario.last().tipo_usuario,
                'usuario_interno': usuario_interno,
                'celular': usuario.last().celular,
                'email': usuario.last().email,
                'compartir_datos': compartir_datos,
                'terminos_condiciones': usuario.last().terminos_condiciones,
                'consulta_offline': False,
                'super_admin': usuario.last().super_admin
            }
            if secundarios[0]:
                datos.update({
                    'fecha_inicio': secundarios[1].get('fecha_inicio')
                })
            return True, datos
        else:
            if tipo_documento in (
                constants.TIPO_DOCUMENTO_PASAPORTE,
                constants.TIPO_DOCUMENTO_CSR,
                constants.TIPO_DOCUMENTO_CEDULA_IDENTIDAD
            ):
                datos = {
                    'tipo_documento': usuario.last().tipo_documento,
                    'numero_documento': usuario.last().pk_usuario,
                    'codigo_trabajador': usuario.last().pk_usuario,
                    'username': username,
                    'codigo_region': codigo_region,
                    'nombre_region': nombre_region,
                    'codigo_institucion':codigo_institucion,
                    'nombre_institucion': nombre_institucion,
                    'nombres': username,
                    'apellido_paterno': username,
                    'apellido_materno': username,
                    'id_aplicacion': id_aplicacion,
                    'pk_grupo': pk_grupo,
                    'nombre_grupo': nombre_grupo,
                    'rol_menues': perfil_menu,
                    'token_cache': f'{token_cache}',
                    'nuevo': nuevo,
                    'estado': flag,
                    'tipo_usuario': usuario.last().tipo_usuario,
                    'usuario_interno': usuario_interno,
                    'email': usuario.last().email,
                    'compartir_datos': usuario.last().compartir_datos,
                    'terminos_condiciones': usuario.last().terminos_condiciones,
                    'consulta_offline': skip_results,
                    'super_admin': usuario.last().super_admin
                }
                return True, datos
            elif skip_results:
                datos = {
                    'tipo_documento': usuario.last().tipo_documento,
                    'numero_documento': usuario.last().pk_usuario,
                    'codigo_trabajador': usuario.last().pk_usuario,
                    'username': username,
                    'codigo_region': codigo_region,
                    'nombre_region': nombre_region,
                    'codigo_institucion':codigo_institucion,
                    'nombre_institucion': nombre_institucion,
                    'nombres': username,
                    'apellido_paterno': username,
                    'apellido_materno': username,
                    'id_aplicacion': id_aplicacion,
                    'pk_grupo': pk_grupo,
                    'nombre_grupo': nombre_grupo,
                    'rol_menues': perfil_menu,
                    'token_cache': f'{token_cache}',
                    'nuevo': nuevo,
                    'estado': flag,
                    'tipo_usuario': usuario.last().tipo_usuario,
                    'usuario_interno': usuario_interno,
                    'email': usuario.last().email,
                    'compartir_datos': usuario.last().compartir_datos,
                    'terminos_condiciones': usuario.last().terminos_condiciones,
                    'consulta_offline': skip_results,
                    'tipo_acceso':compartir_datos,
                    'super_admin': usuario.last().super_admin
                }
                print('Entre al envio de api3')
                if compartir_datos == '0':
                    print('Entre a la api de reco')
                    urlIdPeru = 'http://192.168.110.36:8080/idPeruPlanillas/idPeru/obtener-url/'
                    # urlIdPeru = 'http://localhost:8080/idPeruPlanillas/idPeru/obtener-url/'
                    try:
                        response = requests.post(urlIdPeru, json=datos)
                        response.raise_for_status()
                        return True, datos
                    except requests.exceptions.HTTPError as http_err:
                        # if response.status_code == 500 or response.status_code == 502 \
                        #     or response.status_code == 503 or response.status_code == 504:
                        #     pass
                        return False, f'Http error: {http_err}'

                return True, datos

            else:
                raise exceptions.AuthenticationFailed(
                    f'Error al validar el usuario: {results[1]}'
                )

    def generar_token(self, username, hours=24):
        tiempo_vigencia = datetime.utcnow() + timedelta(hours=hours)
        payload = {
            'username': username,
            'exp': tiempo_vigencia
        }
        token = jwt.encode(payload, 'secreto', algorithm='HS256')
        return token

    def get_nombre_region(self, obj):
        codigo_region = obj.codigo_region
        region = SiRegional.objects.filter(codigo_region=codigo_region)
        return region.first().nombre_region if region.exists() else None

    def get_nombre_zona(self, obj):
        codigo_zona = obj.sede.codigo_zona
        zona = SiZonal.objects.filter(codigo_zona=codigo_zona)
        return zona.first().nombre_zona if zona.exists() else None

    def get_codigo_region(self, obj):
        codigo_region = obj.codigo_region
        region = SiRegional.objects.filter(codigo_region=codigo_region)
        return region.first().codigo_region if region.exists() else None

    def get_codigo_institucion(self, obj):
        codigo_institucion = obj.codigo_institucion
        institucion = SitbPliego.objects.filter(codpli=codigo_institucion)
        return institucion.first().codpli if institucion.exists() else None

    def get_nombre_institucion(self, obj):
        codigo_institucion = obj.codigo_institucion
        institucion = SitbPliego.objects.filter(codpli=codigo_institucion)
        return institucion.first().despli if institucion.exists() else None

    def get_codigo_zona(self, obj):
        codigo_zona = obj.sede.codigo_zona
        zona = SiZonal.objects.filter(codigo_zona=codigo_zona)
        return zona.first().codigo_zona if zona.exists() else None


class CustomAuthenticationTemporal(authentication.BaseAuthentication):

    def validar_token(self, token):
        parametro_confidencial = Parametro.objects.filter(codigo='123454321', valor=token)
        if parametro_confidencial.exists():
            return True
        try:
            payload = jwt.decode(token, 'secreto', algorithms=['HS256'])
            if datetime.utcfromtimestamp(payload['exp']) < datetime.utcnow():
                return False  # Token vencido
            return True
        except jwt.ExpiredSignatureError:
            return False  # Token vencido
        except jwt.InvalidTokenError:
            return False  # Token inválido

    def get_perfil_usuario(self, pk_usuario):
        user = User.objects.filter(pk_usuario=pk_usuario)
        if user.exists() and user.last().password:
            return None
        usuario = SiUsuario.objects.filter(
            codigo_personal=pk_usuario
        )
        if not usuario.exists():
            return None
        codigo_usuario = usuario.last().codigo_usuario
        usuario_perfiles = SiUsuPerfil.objects.filter(codigo_usuario=codigo_usuario)
        if not usuario_perfiles.exists():
            return None
        # Solo 1 perfil por usuario
        pk_grupo = None
        for usuario_perfil in usuario_perfiles:
            grupo = Group.objects.filter(pk_grupo=usuario_perfil.codigo_perfil)
            if grupo.exists():
                pk_grupo = grupo.first().pk_grupo
                break
            else:
                continue
        return pk_grupo

    def get_permiso(
        self, request, codigo_perfil=None, codigo_personal=None, model=None, method=None
    ):
        if codigo_perfil and codigo_personal and model and method:
            grupo = Group.objects.filter(pk_grupo=codigo_perfil)
            # 1 Grupo por Perfil
            grupo = grupo.first() if grupo.exists() else None
            grupo_permiso = PermissionsGroup.objects.filter(
                n_idgrupo=grupo, n_idpermiso__c_modelo=model, n_flagact=True
            )
            # 1 GrupoPermiso por Grupo y Modelo
            permiso = (
                grupo_permiso.first().n_idpermiso if grupo_permiso.exists() else None
            )
            if method == 'GET':
                permiso_ok = permiso.n_flaglee if permiso else True
            elif method == 'POST':
                permiso_ok = permiso.n_flagcrea if permiso else True
            elif method == 'PUT':
                permiso_ok = permiso.n_flagedita if permiso else True
            elif method == 'PATCH':
                permiso_ok = permiso.n_flagedita if permiso else True
            else:
                permiso_ok = False
            return permiso_ok
        # ToDo: Verificar en desarrollo la diferencia
        return True

    def get_regla(
        self, request, codigo_perfil=None, codigo_personal=None, model=None, method=None
    ):
        if codigo_perfil and codigo_personal and model and method:
            usuario = User.objects.filter(
                Q(pk_usuario=codigo_personal) |
                Q(username=codigo_personal)
            )
            usuario = usuario.first() if usuario.exists() else None
            grupo = Group.objects.filter(pk_grupo=codigo_perfil)
            # 1 Grupo por Perfil
            grupo = grupo.first() if grupo.exists() else None
            reglas = Regla.objects.filter(
                grupo=grupo, modelo=model, flag=constants.SI_CHAR_BINARY, metodo=method
            )
            regla = reglas.first() if reglas.exists() else None
            valor = regla.valor if regla else '{"usuario__pk": "{pk_usuario}", "estado__in": ["1", "2"]}'.format(
                pk_usuario=usuario.pk)
            valor_dict = json.loads(valor)
            return valor_dict
        return {}

    def authenticate(self, request):
        if request.META.get('HTTP_AUTHORIZATION'):
            token = request.META.get('HTTP_AUTHORIZATION')
            if token.find('Bearer ') >= 0:
                token = token.replace('Bearer ', '')
            token_valido = self.validar_token(token=token)
            if not token_valido:
                raise exceptions.AuthenticationFailed(
                    'Las credenciales temporales no existen o han expirado.'
                )
            parametro = Parametro.objects.filter(valor=token)
            if not parametro.exists():
                raise exceptions.AuthenticationFailed(
                    'Las credenciales temporales no existe.'
                )
            parametro = parametro.first()
            if parametro.codigo in (constants.ANONYMOUS_USER, constants.CONFIDENCIAL_USER):
                datos = {
                    'token_id': parametro.pk,
                    'token_valor': f'{parametro.valor}',
                    'pk_usuario': parametro.codigo
                }
                return True, datos
            usuarios = User.objects.filter(pk_usuario=parametro.codigo)
            if not usuarios.exists():
                raise exceptions.AuthenticationFailed(
                    'El usuario no existe para el token de acceso.'
                )
            usuario = usuarios.first()
            if usuario.flag != constants.SI_CHAR_BINARY:
                raise exceptions.AuthenticationFailed(
                    'El usuario que intenta ingresar no está activo.'
                )
            codigo_perfil = self.get_perfil_usuario(parametro.codigo)
            path = request._request.path
            method = request._request.method
            try:
                model = path.split('/api/')[1].split('/')[0]
            except Exception:
                model = path.split('/seguridad/')[1].split('/')[0]
            permiso_ok = self.get_permiso(
                request, codigo_perfil, parametro.codigo, model, method
            )
            if not permiso_ok:
                raise exceptions.AuthenticationFailed(
                    f'El usuario no tiene permiso {method} para el registro'
                )
            regla_dict = {}  # self.get_regla(request, codigo_perfil, parametro.c_codigo, model, method)
            datos = {
                'token_id': parametro.pk,
                'token_valor': f'{parametro.valor}',  # ToDo: Sin Bearer
                'pk_usuario': parametro.codigo,
                'id_rol': codigo_perfil,
                'regla': regla_dict
            }
            return True, datos
        else:
            raise exceptions.AuthenticationFailed(
                'Las credenciales temporales no existen o expiraron.'
            )


class CustomAuthenticationValidacion(authentication.BaseAuthentication):
    def get_perfil_usuario(self, pk_usuario):
        user = User.objects.filter(pk_usuario=pk_usuario)
        if user.exists() and user.last().password:
            return None
        usuario = SiUsuario.objects.filter(
            codigo_personal=pk_usuario
        )
        if not usuario.exists():
            return None
        codigo_usuario = usuario.last().codigo_usuario
        usuario_perfiles = SiUsuPerfil.objects.filter(codigo_usuario=codigo_usuario)
        if not usuario_perfiles.exists():
            return None
        # Solo 1 perfil por usuario
        pk_grupo = None
        for usuario_perfil in usuario_perfiles:
            grupo = Group.objects.filter(pk_grupo=usuario_perfil.codigo_perfil)
            if grupo.exists():
                pk_grupo = grupo.first().pk_grupo
                break
            else:
                continue
        return pk_grupo

    def get_permiso(
        self, request, codigo_perfil=None, codigo_personal=None, model=None, method=None
    ):
        if codigo_perfil and codigo_personal and model and method:
            grupo = Group.objects.filter(pk_grupo=codigo_perfil)
            # 1 Grupo por Perfil
            grupo = grupo.first() if grupo.exists() else None
            grupo_permiso = PermissionsGroup.objects.filter(
                n_idgrupo=grupo, n_idpermiso__c_modelo=model, n_flagact=True
            )
            # 1 GrupoPermiso por Grupo y Modelo
            permiso = (
                grupo_permiso.first().n_idpermiso if grupo_permiso.exists() else None
            )
            if method == 'GET':
                permiso_ok = permiso.n_flaglee if permiso else True
            elif method == 'POST':
                permiso_ok = permiso.n_flagcrea if permiso else True
            elif method == 'PUT':
                permiso_ok = permiso.n_flagedita if permiso else True
            elif method == 'DELETE':
                permiso_ok = permiso.n_flagborra if permiso else True
            else:
                permiso_ok = False
            return permiso_ok
        # ToDo: Verificar en desarrollo la diferencia
        return True

    def get_regla(
        self, request, codigo_perfil=None, codigo_personal=None, model=None, method=None
    ):
        if codigo_perfil and codigo_personal and model and method:
            usuario = User.objects.filter(
                Q(pk_usuario=codigo_personal) |
                Q(username=codigo_personal)
            )
            usuario = usuario.first() if usuario.exists() else None
            grupo = Group.objects.filter(pk_grupo=codigo_perfil)
            # 1 Grupo por Perfil
            grupo = grupo.first() if grupo.exists() else None
            reglas = Regla.objects.filter(
                grupo=grupo, modelo=model, flag=constants.SI_CHAR_BINARY, metodo=method
            )
            regla = reglas.first() if reglas.exists() else None
            valor = regla.valor if regla else '{"usuario__pk": "{pk_usuario}", "estado__in": ["1", "2"]}'.format(
                pk_usuario=usuario.pk)
            valor_dict = json.loads(valor)
            return valor_dict
        return {}

    def authenticate(self, request):
        if request.META.get('HTTP_AUTHORIZATION'):
            token = request.META.get('HTTP_AUTHORIZATION')
            if token.find('Bearer ') >= 0:
                token = token.replace('Bearer ', '')
            parametro = Parametro.objects.filter(valor=token)
            if not parametro.exists():
                raise exceptions.AuthenticationFailed(
                    'Las credenciales temporales no existen o expiraron.'
                )
            parametro = parametro.first()
            usuarios = User.objects.filter(pk_usuario=parametro.codigo)
            if not usuarios.exists():
                raise exceptions.AuthenticationFailed(
                    'El usuario no existe para el token de acceso.'
                )
            codigo_perfil = self.get_perfil_usuario(parametro.codigo)
            path = request._request.path
            method = request._request.method
            try:
                model = path.split('/api/')[1].split('/')[0]
            except Exception:
                model = path.split('/seguridad/')[1].split('/')[0]
            permiso_ok = self.get_permiso(
                request, codigo_perfil, parametro.codigo, model, method
            )
            if not permiso_ok:
                raise exceptions.AuthenticationFailed(
                    f'El usuario no tiene permiso {method} para el registro'
                )
            regla_dict = {}  # self.get_regla(request, codigo_perfil, parametro.c_codigo, model, method)
            datos = {
                'token_id': parametro.pk,
                'token_valor': f'{parametro.valor}',  # ToDo: Sin Bearer
                'pk_usuario': parametro.codigo,
                'id_rol': codigo_perfil,
                'regla': regla_dict
            }
            return True, datos
        else:
            raise exceptions.AuthenticationFailed(
                'Las credenciales temporales no existen o expiraron.'
            )


class CustomAuthenticationAnonymousUser(authentication.BaseAuthentication):
    def authenticate(self, request):
        if request.method == 'GET':
            return AnonymousUser(), None
        if request.META.get('HTTP_ACCESS_CONTROL_ALLOW_ORIGIN') == '*':
            # TODO: Modificar * por la url del front con una variable para dev y prod
            return AnonymousUser(), None
        raise exceptions.AuthenticationFailed(
            'Las credenciales temporales no existen o expiraron.'
        )


class CustomAuthenticationPublico(authentication.BaseAuthentication):
    @staticmethod
    def is_sha256(token):
        # Verificar si el token tiene una longitud válida
        if len(token) != 64:
            return False

        # Verificar si el token está en formato hexadecimal
        if not re.match(r'^[0-9a-fA-F]+$', token):
            return False

        return True

    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            raise exceptions.AuthenticationFailed(
                'Las credenciales públicas no existen o expiraron.'
            )
        if token.find('Bearer ') >= 0:
            token = token.replace('Bearer ', '')
        if self.is_sha256(token):
            vals = {
                'codigo': constants.ANONYMOUS_USER,
                'nombre': 'Token Público',
                'valor': f'{token}',
            }
            parametro, _ = Parametro.objects.get_or_create(**vals)
            datos = {
                'token_id': parametro.pk_parametro,
            }
            return AnonymousUser(), datos
        raise exceptions.AuthenticationFailed(
            'Las credenciales públicas no existen o expiraron.'
        )


class CustomAuthenticationConfidencial(authentication.BaseAuthentication):
    @staticmethod
    def is_sha256(token):
        # Verificar si el token tiene una longitud válida
        if len(token) != 64:
            return False

        # Verificar si el token está en formato hexadecimal
        if not re.match(r'^[0-9a-fA-F]+$', token):
            return False

        return True

    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            raise exceptions.AuthenticationFailed(
                'La credencial confidencial no existe.'
            )
        if token.find('Bearer ') >= 0:
            token = token.replace('Bearer ', '')
        if self.is_sha256(token):
            vals = {
                'codigo': constants.CONFIDENCIAL_USER,
                'valor': f'{token}',
            }
            parametros = Parametro.objects.filter(**vals)
            if not parametros.exists():
                raise exceptions.AuthenticationFailed(
                    'La credencial confidencial no existe.'
                )
            parametro = parametros.first()
            datos = {
                'token_id': parametro.pk_parametro,
            }
            return AnonymousUser(), datos
        raise exceptions.AuthenticationFailed(
            'La credencial confidencial no existe.'
        )




