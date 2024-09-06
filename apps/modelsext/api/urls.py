from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'modelsext_api'


urlpatterns = [
    path('departamento/', views.DepartamentoList.as_view(), name='departamento-list'),
    path('provincia/', views.ProvinciaList.as_view(), name='provincia-list'),
    path('distrito/', views.DistritoList.as_view(), name='distrito-list'),
    path('nacionalidad/', views.NacionalidadList.as_view(), name='nacionalidad-list'),
    path('tipo_documento/', views.TipoDocumentoList.as_view(), name='tipodocumento-list'),
    path('dependencia/', views.DependenciaAPIView.as_view(), name='dependencia-list'),
    path('regional/', views.RegionalAPIView.as_view(), name='regional-list'),
    path('zonal/', views.ZonalAPIView.as_view(), name='zonal-list'),
    path('cargo/', views.CargoAPIView.as_view(), name='cargo-list'),
    path('escala/', views.EscalaAPIView.as_view(), name='escala-list'),
    path('institucion/', views.InstitucionList.as_view(), name='institucion-list'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
