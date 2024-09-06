from rest_framework import serializers

from apps.common import constants
from apps.seguridad.models import User, Group, Menu, MenuGroup
from apps.programacion.models import Sede
from apps.modelsext.models import TPersonal, SiDependencia, SiRegional, SiZonal, SiCargo, SiEscala, SiUsuPerfil

from config.settings.base import CODIGO_SISTEMA


class UserUpdateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=False)
    celular = serializers.CharField(required=False)
    flag = serializers.CharField(required=False)
    compartir_datos = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('email', 'celular', 'flag', 'compartir_datos')


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    tipo_documento_str = serializers.SerializerMethodField('get_tipo_documento_str')
    nombres = serializers.SerializerMethodField('get_nombres')
    apellido_paterno = serializers.SerializerMethodField('get_apellido_paterno')
    apellido_materno = serializers.SerializerMethodField('get_apellido_materno')
    codigo_cargo = serializers.SerializerMethodField('get_codigo_cargo')
    pk_grupo = serializers.SerializerMethodField('get_pk_grupo')
    nombre_escala = serializers.SerializerMethodField('get_nombre_escala')
    nombre_grupo = serializers.SerializerMethodField('get_nombre_grupo')
    celular = serializers.CharField(required=False)

    def get_tipo_documento_str(self, obj):
        return constants.TIPO_DOCUMENTO.get(obj.tipo_documento)

    def get_nombres(self, obj):
        personal = TPersonal.objects.filter(codigo_personal=obj.pk_usuario)
        return personal.first().nombres if personal.exists() else None

    def get_apellido_paterno(self, obj):
        personal = TPersonal.objects.filter(codigo_personal=obj.pk_usuario)
        return personal.first().apellido_paterno if personal.exists() else None

    def get_apellido_materno(self, obj):
        personal = TPersonal.objects.filter(codigo_personal=obj.pk_usuario)
        return personal.first().apellido_materno if personal.exists() else None

    def get_codigo_dependencia(self, obj):
        personal = TPersonal.objects.filter(codigo_personal=obj.pk_usuario)
        return personal.first().codigo_dependencia if personal.exists() else None


    def get_dependencia(self, obj):
        personal = TPersonal.objects.filter(codigo_personal=obj.pk_usuario)
        dependencia = SiDependencia.objects.none()
        if personal.exists():
            codigo_dependencia = personal.first().codigo_dependencia
            dependencia = SiDependencia.objects.filter(codigo_dependencia=codigo_dependencia)
        return dependencia

    def get_nombre_dependencia(self, obj):
        dependencia = self.get_dependencia(obj)
        return dependencia.first().dependencia if dependencia.exists() else None

    def get_nombre_region(self, obj):
        if not obj.sede_id:
            return '-'
        codigo_region = obj.sede.codigo_region
        region = SiRegional.objects.filter(codigo_region=codigo_region)
        return region.first().nombre_region if region.exists() else None

    def get_nombre_zona(self, obj):
        if not obj.sede_id:
            return '-'
        codigo_zona = obj.sede.codigo_zona
        zona = SiZonal.objects.filter(codigo_zona=codigo_zona)
        return zona.first().nombre_zona if zona.exists() else None

    def get_nombre_escala(self, obj):
        personal = TPersonal.objects.filter(codigo_personal=obj.pk_usuario)
        codigo_escala = personal.first().codigo_escala if personal.exists() else None
        escala = SiEscala.objects.filter(codigo=codigo_escala)
        return escala.first().descripcion if escala.exists() else None

    def get_nombre_cargo(self, obj):
        personal = TPersonal.objects.filter(codigo_personal=obj.pk_usuario)
        codigo_cargo = personal.first().codigo_cargo if personal.exists() else None
        cargo = SiCargo.objects.filter(codigo=codigo_cargo)
        return cargo.first().desc_cargo if cargo.exists() else None

    def get_nombre_grupo(self, obj):
        usuario_perfil = SiUsuPerfil.objects.filter(
            codigo_usuario=obj.username,
            codigo_sistema=CODIGO_SISTEMA,
            flag='S'
        )
        codigo_perfil = usuario_perfil.first().codigo_perfil if usuario_perfil.exists() else None
        grupo = Group.objects.filter(pk_grupo=codigo_perfil)
        return grupo.first().nombre if grupo.exists() else None

    def get_codigo_cargo(self, obj):
        personal = TPersonal.objects.filter(codigo_personal=obj.pk_usuario)
        codigo_cargo = personal.first().codigo_cargo if personal.exists() else None
        cargo = SiCargo.objects.filter(codigo=codigo_cargo)
        return cargo.first().codigo if cargo.exists() else None

    def get_pk_grupo(self, obj):
        usuario_perfil = SiUsuPerfil.objects.filter(
            codigo_usuario=obj.username,
            codigo_sistema=CODIGO_SISTEMA,
            flag='S'
        )
        codigo_perfil = usuario_perfil.first().codigo_perfil if usuario_perfil.exists() else None
        grupo = Group.objects.filter(pk_grupo=codigo_perfil)
        return grupo.first().pk_grupo if grupo.exists() else None

    def validate_celular(self, value):
        if len(value) != 9:
            raise serializers.ValidationError('El celular debe tener 9 dígitos.')
        return value

    class Meta:
        model = User
        exclude = ['groups', 'password', 'usuario_creacion', 'usuario_modificacion',
                   'host_registro', 'ip_registro', 'fecha_creacion', 'fecha_modificacion']


class GrupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class MenuSerializer(serializers.ModelSerializer):
    n_idparent = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['id', 'nombre', 'url', 'parent']

    def get_n_idparent(self, obj):
        if obj.parent:
            return MenuSerializer(obj.parent).data
        else:
            return None


class GrupoMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuGroup
        fields = '__all__'


class UserGroupSerializer(serializers.Serializer):
    menu_list = serializers.ListField(child=serializers.IntegerField())
    usuario_list = serializers.ListField(child=serializers.CharField(max_length=10))
