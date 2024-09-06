import re
from django.conf import settings
from django.http import (
    HttpResponseForbidden
)
from django.conf import settings

from django.views.generic import View
from django.views.generic.base import ContextMixin


from apps.seguridad.api.views import CustomAuthentication
# from apps.common.constants import (ID_DB_ROL_RRHH, ID_DB_ROL_TRABAJADOR, ID_DB_ROL_ROTACION, ID_DB_ROL_DEPENDENCIA)


class LoginRequiredView(ContextMixin, View):
    username = ''
    numero_documento = ''
    codigo_trabajador = ''
    id_aplicacion = ''
    codigo_dependencia = ''
    nombre_dependencia = ''
    auth_roles = None
    doesnt_need_role = False

    def __init__(self):
        super().__init__()
        self.doesnt_need_role = False

    def dispatch(self, request, *args, **kwargs):
        _, data_auth = CustomAuthentication.get_auth_datos(request)
        self.__set_defaults(data_auth)
        return super().dispatch(request, *args, **kwargs)

    def __set_defaults(self, data):
        self.username = data.get('username', '')
        self.numero_documento = data.get('numero_documento', '')
        self.codigo_trabajador = data.get('codigo_trabajador', '')
        self.id_aplicacion = data.get('id_aplicacion', '')
        self.codigo_dependencia = data.get('codigo_dependencia', '')
        self.nombre_dependencia = data.get('nombre_dependencia', '')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = {
            'username': self.username,
            'roles': self.get_roles(),
            'id_aplicacion': self.id_aplicacion,
            'codigo_trabajador': self.codigo_trabajador,
            'nombre_dependencia': self.nombre_dependencia,
            'numero_documento': self.numero_documento
        }
        context['user'] = user
        return context

    def get_roles(self):
        roles = []
        if self.auth_roles:
            for rol in self.auth_roles:
                roles.append(rol)
        return roles


class SoloUsuarioView(LoginRequiredView):

    def __init__(self):
        super(LoginRequiredView, self).__init__()
        self.doesnt_need_role = True
