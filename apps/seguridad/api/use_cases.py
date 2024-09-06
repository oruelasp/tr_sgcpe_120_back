from datetime import datetime, timedelta

from apps.common.constants import CELULAR_VERIFICACION, CORREO_VERIFICACION
from apps.seguridad.api.entities import EnviarVerificacionResponse, EnviarInvitacionResponse
from apps.seguridad.api.utils import (
    enviar_codigo_verificacion,
    generar_codigo_verificacion,
    enviar_credenciales,
    enviar_adjunto
)
from apps.seguridad.models import User, UserVerification
from apps.seguridad.queries import (
    desactivar_codigo_usuario_verificacion,
    get_user,
    verificar_codigo,
)
from apps.common.functions import ServiciosInternos as si


class UsuarioVerificcionnUseCase:
    max_codigo_longitud = 5
    expiracion_minutos = 5

    def validar_data_enviar_verificacion(self, data_auth, data_request):
        usuario = get_user(data_auth.get('pk_usuario'))
        if not usuario:
            raise ValueError('No existe el usuario.')
        tipo_verificacion = data_request.get('tipo')
        if tipo_verificacion not in [CORREO_VERIFICACION, CELULAR_VERIFICACION]:
            raise ValueError('El tipo de verificacion no corresponde.')
        if tipo_verificacion == CORREO_VERIFICACION:
            if not usuario.email:
                raise ValueError(
                    'No se encuentra registrado un correo para enviarle el codigo de verificacion.'
                )
        elif tipo_verificacion == CELULAR_VERIFICACION:
            if not usuario.celular:
                raise ValueError(
                    'No se encuentra registrado un celular para enviarle el codigo de verificacion.'
                )
        return usuario, tipo_verificacion

    def validar_codigo_verificacion(self, data_auth, data_request):
        usuario = get_user(data_auth.get('pk_usuario'))
        if not usuario:
            return False, 'No existe el usuario.'
        existe_codigo = verificar_codigo(usuario, data_request.get('codigo'))
        if not existe_codigo:
            return (
                False,
                'No existe el código de verificación o ya expiró, intente generando uno nuevo.',
            )
        return True, 'Verificación correcta.'

    def crear_codigo_verificacion(self, user: User, tipo_verificacion: str) -> EnviarVerificacionResponse:
        user_verification = self.crear_usuario_verificacion(user, tipo_verificacion)
        se_envio, msj_envio = enviar_codigo_verificacion(user_verification)
        if se_envio:
            user_verification_response = EnviarVerificacionResponse(
                pk_usuario=user_verification.user.pk_usuario,
                fecha_expiracion=user_verification.fecha_expiracion,
                mensaje_envio='Se envío satisfactoriamente el código de verificación',
            )
        else:
            user_verification_response = EnviarVerificacionResponse(
                pk_usuario=user_verification.user.pk_usuario,
                se_envio=False,
                mensaje_envio=msj_envio,
            )
        return user_verification_response

    def crear_usuario_verificacion(self, user: User, tipo_verificacion: str) -> UserVerification:
        desactivar_codigo_usuario_verificacion(user)
        codigo_verificacion = generar_codigo_verificacion(
            max_digit=self.max_codigo_longitud
        )
        usuario_verificacion = UserVerification()
        usuario_verificacion.user = user
        usuario_verificacion.codigo = codigo_verificacion
        usuario_verificacion.tipo_verificacion = tipo_verificacion
        usuario_verificacion.fecha_expiracion = datetime.now() + timedelta(
            minutes=self.expiracion_minutos
        )
        usuario_verificacion.save()
        return usuario_verificacion


class UsuarioCredencialesUseCase(UsuarioVerificcionnUseCase):
    max_codigo_longitud = 5
    expiracion_minutos = 5

    def crear_credenciales(self, user: User, tipo_verificacion: str) -> EnviarVerificacionResponse:
        se_envio, msj_envio = enviar_credenciales(user, tipo_verificacion)
        if se_envio:
            user_verification_response = EnviarVerificacionResponse(
                pk_usuario=user.pk_usuario,
                mensaje_envio='Se envío las credenciales con éxito',
                password=si.get_siusuario_password(si(), user.pk_usuario)
            )
        else:
            user_verification_response = EnviarVerificacionResponse(
                pk_usuario=user.pk_usuario,
                se_envio=False,
                mensaje_envio=msj_envio,
            )
        return user_verification_response


class UsuarioInvitacionUseCase(UsuarioVerificcionnUseCase):
    max_codigo_longitud = 5
    expiracion_minutos = 5

    def crear_invitacion_adjunto(
        self, correo: str, tipo_verificacion: str, adjunto_url: str, fecha_solicitud: datetime, codigo_solicitud: str,
        datos_solicitante: str
    ) -> EnviarInvitacionResponse:
        se_envio, msj_envio = enviar_adjunto(
            correo, tipo_verificacion, adjunto_url, fecha_solicitud, codigo_solicitud, datos_solicitante)
        if se_envio:
            user_verification_response = EnviarInvitacionResponse(
                mensaje_envio='Se envío la invitación adjunta con éxito',
            )
        else:
            user_verification_response = EnviarInvitacionResponse(
                se_envio=False,
                mensaje_envio=msj_envio,
            )
        return user_verification_response
