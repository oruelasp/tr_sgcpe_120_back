"""
URLs para API aplicación de Programacion.

Copyright (C) 2022 PRODUCE.

Authors:
    Omar Ruelas Principe <ddf_temp57@produce.gob.pe>
"""
from django.urls import path


from apps.programacion.api import views

app_name = 'programacion_api'

urlpatterns = [
    # Sede
    path('sede/', views.SedeAPIView.as_view(), name='sede'),
    path('motivo/', views.MotivoAPIView.as_view(), name='motivo'),
    path('detallesolicitud/', views.SolicitudDetalleAPIView.as_view(), name='detallesolicitud'),
    path('detallesolicitud/<int:pk_solicitud_detalle>/', views.SolicitudDetalleUpdateAPIView.as_view(), name='detallesolicitud-id'),
    path('solicitud/', views.SolicitudAPIView.as_view(), name='solicitud'),
    path('solicitud-estado/', views.SolicitudEstadoAPIView.as_view(), name='solicitud-estado'),
    path('solicitud/<int:pk_solicitud>/', views.SolicitudUpdateAPIView.as_view(), name='solicitud-id'),
    path('guardar-archivo/', views.GuardarArchivoAPIView.as_view(), name='guardar-archivo'),
    path('descargar-archivo/', views.DescargarArchivoAPIView.as_view(), name='descargar-archivo'),
    path('descargar-archivo-base64/', views.DescargarArchivoB64APIView.as_view(), name='descargar-archivo-base64'),
    path('guardar-invitacion/', views.GuardarInvitacionAPIView.as_view(), name='guardar-invitacion'),
    path('plantilla/', views.PlantillaAPIView.as_view(), name='plantilla'),
    path('plantilla/<int:pk_plantilla>/', views.PlantillaAPIView.as_view(), name='plantilla-id'),
    path('audiencia/', views.AudienciaAPIView.as_view(), name='audiencia'),
    path('audiencia-codigo/', views.AudienciaCodigoAPIView.as_view(), name='audiencia-codigo'),
    path('audiencia/<int:pk_audiencia>/', views.AudienciaUpdateAPIView.as_view(), name='audiencia-id'),
    path('audiencia-estado/', views.AudienciaEstadoAPIView.as_view(), name='audiencia-estado'),
    path('enviar-invitacion/', views.EnviarInvitacionAPIView.as_view(), name='enviar-invitacion'),
    path('descargar-excel-solicitud/', views.DescargarExcelSolicitudes.as_view(), name='descargar-excel-solicitud'),
    path('consultasPlanillas/', views.ConsultaPlanillaView.as_view(), name='consultas-planilla'),
    path('auditoria/', views.SolicitudViewSet.as_view({'get': 'list'}), name='auditoria'),
    path('guardar-consulta/', views.GuardarSolicitudApiView.as_view(), name='guardar-consulta'),
]
