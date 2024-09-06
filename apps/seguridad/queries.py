from datetime import datetime

from django.db.models import Q

from apps.common.constants import NO_CHAR_BINARY, SI_CHAR_BINARY
from apps.common.functions import ServiciosInternos as si
from apps.seguridad.models import User, UserVerification
from apps.modelsext.models import SiUsuario


def get_user(pk_usuario: str) -> User:
    return User.objects.filter(pk_usuario=pk_usuario).last()


def verificar_codigo(user, codigo):
    return UserVerification.objects.filter(
        user=user,
        codigo=codigo,
        estado=SI_CHAR_BINARY,
        fecha_expiracion__gte=datetime.now(),
    ).exists()


def desactivar_codigo_usuario_verificacion(user: User, codigo: str = None) -> None:  # type: ignore
    query = Q(codigo=codigo) if codigo else Q()
    UserVerification.objects.filter(query, user=user, estado=SI_CHAR_BINARY).update(
        estado=NO_CHAR_BINARY
    )
