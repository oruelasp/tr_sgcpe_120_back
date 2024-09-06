from rest_framework import serializers

from apps.modelsext.models import (
    SiPersona, Departamento, Provincia, Distrito, Nacionalidad, TipoDocumento,
    SiDependencia, SiRegional, SiZonal, SiCargo, SiEscala, SitbPliego)
from apps.common import constants


class SitbPliegoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SitbPliego
        fields ='__all__'

class SiPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiPersona
        fields = (
            'codigo_personal',
            'apellido_paterno',
            'apellido_materno',
            'nombres',
            'flag',
        )


class DepartamentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Departamento
        fields = '__all__'


class ProvinciaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Provincia
        fields = '__all__'


class DistritoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Distrito
        fields = '__all__'


class NacionalidadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Nacionalidad
        fields = ['codigo_nacionalidad', 'descripcion_nacionalidad', 'codigo_iso_nacionalidad']


class TipoDocumentoSerializer(serializers.ModelSerializer):
    longitud_min = serializers.SerializerMethodField()
    longitud_max = serializers.SerializerMethodField()

    def get_longitud_min(self, obj):
        codigo_tipo_documento = obj.codigo
        if codigo_tipo_documento in constants.TIPO_DOCUMENTO_LENGTH:
            return constants.TIPO_DOCUMENTO_LENGTH[codigo_tipo_documento][0]
        return 0

    def get_longitud_max(self, obj):
        codigo_tipo_documento = obj.codigo
        if codigo_tipo_documento in constants.TIPO_DOCUMENTO_LENGTH:
            return constants.TIPO_DOCUMENTO_LENGTH[codigo_tipo_documento][1]
        return 30

    class Meta:
        model = TipoDocumento
        fields = ['codigo', 'descripcion', 'abreviatura', 'flag', 'longitud_min', 'longitud_max']


class SiDependenciaSerializer(serializers.ModelSerializer):
    codigo_dependencia = serializers.IntegerField(required=False)
    dependencia = serializers.CharField(required=False)
    siglas = serializers.CharField(required=False)
    codigo_zona = serializers.CharField(required=False)
    codigo_region = serializers.CharField(required=False)

    class Meta:
        model = SiDependencia
        fields = ['codigo_dependencia', 'dependencia', 'siglas', 'codigo_zona', 'codigo_region']


class SiRegionalSerializer(serializers.ModelSerializer):

    class Meta:
        model = SiRegional
        fields = ['codigo_region', 'nombre_region', 'codigo_departamento']


class SiZonalSerializer(serializers.ModelSerializer):

    class Meta:
        model = SiZonal
        fields = '__all__'


class SiCargoSerializer(serializers.ModelSerializer):

    class Meta:
        model = SiCargo
        fields = '__all__'


class SiEscalaSerializer(serializers.ModelSerializer):

    class Meta:
        model = SiEscala
        fields = '__all__'
