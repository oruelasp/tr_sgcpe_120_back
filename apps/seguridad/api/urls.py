from django.urls import path

from apps.seguridad.api.views import (
    AccesoAPIView,
    ParametroAPIView,
    GrupoMenuAPIView,
    GrupoAPIView,
    GrupoUsuarioAPIView,
    MenuAPIView,
    ValidacionAPIView,
    UserAPIView,
    EnviarVerificacionAPIView,
    ValidarVerificacionAPIView,
    EnviarCredencialesAPIView,
)

app_name = 'seguridad_api'

urlpatterns = [
    # Acceso
    path('acceso/', AccesoAPIView.as_view(), name='acceso'),
    # GrupoMenu
    path('grupo-menu/', GrupoMenuAPIView.as_view(), name='grupo-menu'),
    # GrupoUsuario
    path('grupo-usuario/', GrupoUsuarioAPIView.as_view(), name='grupo-usuario'),
    # Grupo
    path('grupo/', GrupoAPIView.as_view(), name='grupo'),
    # Parametro
    path('parametro/', ParametroAPIView.as_view(), name='parametro'),
    # Menu
    path('menu/', MenuAPIView.as_view(), name='menu'),
    # Validacion
    path('validacion/', ValidacionAPIView.as_view(), name='validacion'),
    # Usuario Interno
    path('usuario/', UserAPIView.as_view(), name='usuario'),
    path('usuario/<str:pk_usuario>/', UserAPIView.as_view(), name='usuario-id'),
    # Verificacion
    path('enviar-verificacion/', EnviarVerificacionAPIView.as_view(), name='enviar-verificacion'),
    path('validar-verificacion/', ValidarVerificacionAPIView.as_view(), name='validar-verificacion'),
    # Credenciales
    path('enviar-credenciales/', EnviarCredencialesAPIView.as_view(), name='enviar-credenciales'),
]
