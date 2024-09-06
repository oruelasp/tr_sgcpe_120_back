import django_filters

from apps.modelsext.models import Departamento, Provincia, Distrito, TipoDocumento


class DepartamentoFilterSet(django_filters.FilterSet):
    codigo_departamento = django_filters.CharFilter(lookup_expr='icontains')
    descripcion_departamento = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Departamento
        fields = ['codigo_departamento', 'descripcion_departamento']


class ProvinciaFilterSet(django_filters.FilterSet):
    codigo_provincia = django_filters.CharFilter(lookup_expr='icontains')
    descripcion_provincia = django_filters.CharFilter(lookup_expr='icontains')
    codigo_departamento = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Provincia
        fields = ['codigo_provincia', 'descripcion_provincia', 'codigo_departamento']


class DistritoFilterSet(django_filters.FilterSet):
    codigo_distrito = django_filters.CharFilter(lookup_expr='icontains')
    descripcion_distrito = django_filters.CharFilter(lookup_expr='icontains')
    codigo_provincia = django_filters.CharFilter(lookup_expr='icontains')
    codigo_departamento = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Distrito
        fields = ['codigo_distrito', 'descripcion_distrito', 'codigo_provincia', 'codigo_departamento']


class TipoDocumentoFilterSet(django_filters.FilterSet):

    class Meta:
        model = TipoDocumento
        fields = ['codigo', 'abreviatura', 'flag', 'descripcion']
