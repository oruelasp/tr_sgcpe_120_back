import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Case, When, Value, IntegerField, OuterRef, Subquery, Q, Func, F
from rest_framework import filters, generics
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from apps.common import constants
from apps.common.utils import CustomPagination
from apps.modelsext.filters import (
    DepartamentoFilterSet,
    DistritoFilterSet,
    ProvinciaFilterSet,
    TipoDocumentoFilterSet,
)
from apps.modelsext.models import (
    Departamento,
    Distrito,
    Nacionalidad,
    Provincia,
    TipoDocumento,
    SiDependencia,
    SiRegional,
    SiZonal,
    SiCargo,
    SiEscala, SitbPliego
)

from ...seguridad.auth import CustomAuthenticationAnonymousUser
from .serializers import (
    DepartamentoSerializer,
    DistritoSerializer,
    NacionalidadSerializer,
    ProvinciaSerializer,
    TipoDocumentoSerializer,
    SiDependenciaSerializer,
    SiRegionalSerializer,
    SiZonalSerializer,
    SiCargoSerializer,
    SiEscalaSerializer, SitbPliegoSerializer
)


class InstitucionList(generics.ListAPIView):
    serializer_class = SitbPliegoSerializer
    http_method_names = ['get']

    def get_queryset(self):

        queryset = SitbPliego.objects.annotate(
            codpli_stripped=Func(F('codpli'), function='TRIM')
        ).filter(
            (Q(codpli_stripped='12') | Q(codpli_stripped='4') | Q(codpli_stripped='22')) &
            ( Q(sector=12) | Q(sector=22) | Q(sector=4))
        )

        print(queryset.values('codpli', 'codpli_stripped'))
        return queryset


class DepartamentoList(generics.ListAPIView):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    http_method_names = [
        'get',
    ]
    # filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    # filterset_class = DepartamentoFilterSet
    # pagination_class = CustomPagination

    def get_queryset(self):
        data = self.request.query_params.copy()
        queryset = Departamento.objects.all()
        if data.get('codigo_departamento'):
            queryset = queryset.filter(codigo_departamento=data.get('codigo_departamento'))
        return queryset


class ProvinciaList(generics.ListAPIView):
    queryset = Provincia.objects.all()
    serializer_class = ProvinciaSerializer
    http_method_names = [
        'get',
    ]
    filterset_class = ProvinciaFilterSet
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['codigo_provincia', 'descripcion_provincia', 'codigo_departamento']


class DistritoList(generics.ListAPIView):
    queryset = Distrito.objects.all()
    serializer_class = DistritoSerializer
    http_method_names = [
        'get',
    ]
    filterset_class = DistritoFilterSet
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = [
        'codigo_distrito',
        'descripcion_distrito',
        'codigo_provincia',
        'codigo_departamento',
    ]


class NacionalidadList(generics.ListAPIView):
    queryset = Nacionalidad.objects.all()
    serializer_class = NacionalidadSerializer
    http_method_names = [
        'get',
    ]


class TipoDocumentoList(generics.ListAPIView):
    authentication_classes = []
    serializer_class = TipoDocumentoSerializer
    tipo_documento_allowed = (
        constants.TIPO_DOCUMENTO_DNI,
        constants.TIPO_DOCUMENTO_CE,
        constants.TIPO_DOCUMENTO_CPP
    )

    http_method_names = [
        'get',
    ]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = TipoDocumentoFilterSet
    search_fields = ['codigo', 'abreviatura', 'flag']

    def get_queryset(self):
        queryset = TipoDocumento.objects.filter(codigo__in=self.tipo_documento_allowed)
        return queryset


class DependenciaAPIView(generics.ListAPIView):
    serializer_class = SiDependenciaSerializer
    http_method_names = ['get', ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        data = self.request.query_params.copy()
        es_depgeneral = self.request.query_params.get('es_depgeneral', '')
        if es_depgeneral and bool(int(es_depgeneral)):
            query_set = SiDependencia.objects.filter(coddep_principal__isnull=True)
        elif es_depgeneral and not bool(int(es_depgeneral)):
            query_set = SiDependencia.objects.filter(coddep_principal__isnull=False)
        else:
            query_set = SiDependencia.objects.all()
        if data.get('codigo_region'):
            query_set = query_set.filter(codigo_region=data.get('codigo_region'))
        if data.get('codigo_zona'):
            query_set = query_set.filter(codigo_zona=data.get('codigo_zona'))
        if data.get('codigo_dependencia'):
            query_set = query_set.filter(codigo_dependencia=data.get('codigo_dependencia'))
        if data.get('dependencia'):
            query_set = query_set.filter(dependencia__icontains=data.get('dependencia'))
        if data.get('q'):
            query_set = query_set.filter(
                Q(dependencia__icontains=data.get('q')) |
                Q(codigo_dependencia__icontains=data.get('q'))
            )
        return query_set


class RegionalAPIView(generics.ListAPIView):
    serializer_class = SiRegionalSerializer
    http_method_names = ['get', ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        data = self.request.query_params.copy()
        query_set = SiRegional.objects.all()
        if data.get('codigo_region'):
            query_set = query_set.filter(codigo_region=data.get('codigo_region'))
        if data.get('nombre_region'):
            query_set = query_set.filter(nombre_region__icontains=data.get('nombre_region'))
        if data.get('codigo_departamento'):
            query_set = query_set.filter(codigo_departamento=data.get('codigo_departamento'))
        return query_set


class ZonalAPIView(generics.ListAPIView):
    serializer_class = SiZonalSerializer
    http_method_names = ['get', ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        data = self.request.query_params.copy()
        query_set = SiZonal.objects.all()
        if data.get('codigo_region'):
            query_set = query_set.filter(codigo_region=data.get('codigo_region'))
        if data.get('codigo_zona'):
            query_set = query_set.filter(codigo_zona=data.get('codigo_zona'))
        if data.get('nombre_zona'):
            query_set = query_set.filter(nombre_zona__icontains=data.get('nombre_zona'))
        return query_set


class CargoAPIView(generics.ListAPIView):
    serializer_class = SiCargoSerializer
    http_method_names = ['get', ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        data = self.request.query_params.copy()
        query_set = SiCargo.objects.all()
        if data.get('codigo'):
            query_set = query_set.filter(codigo=data.get('codigo'))
        if data.get('desc_cargo'):
            query_set = query_set.filter(desc_cargo__icontains=data.get('desc_cargo'))
        return query_set


class EscalaAPIView(generics.ListAPIView):
    serializer_class = SiEscalaSerializer
    http_method_names = ['get', ]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        data = self.request.query_params.copy()
        query_set = SiEscala.objects.all()
        if data.get('codigo'):
            query_set = query_set.filter(codigo=data.get('codigo'))
        if data.get('nombre'):
            query_set = query_set.filter(nombre__icontains=data.get('nombre'))
        if data.get('descripcion'):
            query_set = query_set.filter(descripcion__icontains=data.get('descripcion'))
        return query_set
