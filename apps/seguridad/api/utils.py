from datetime import datetime
import logging
import secrets
import requests
from smtplib import SMTPRecipientsRefused

from django.conf import settings
from django.core.mail import send_mail, EmailMessage

from config.settings.base import FRONTEND_URL
from apps.common.constants import CELULAR_VERIFICACION, CORREO_VERIFICACION
from apps.common.functions import ServiciosInternos as si
from apps.seguridad.models import UserVerification

from apps.programacion.models import Solicitud, Audiencia

logger = logging.getLogger(__name__)


def enviar_codigo_verificacion(user_verification: UserVerification):  # type: ignore
    data = {
        'codigo': user_verification.codigo,
        'celular': user_verification.user.celular,
        'correo': user_verification.user.email,
    }
    if user_verification.tipo_verificacion == CORREO_VERIFICACION:
        return enviar_correo_codigo_verificacion(data=data)
    elif user_verification.tipo_verificacion == CELULAR_VERIFICACION:
        return enviar_celular_codigo_verificacion(data=data)


def enviar_celular_codigo_verificacion(data):
    try:
        celular = data.get('celular')  # noqa
        mensaje = f"Su codigo de verificacion para ingresar a SGC PLANILLAS es: {data.get('codigo')}"  # noqa
        # TODO: Agregar la funcion para enviar sms al celular
        # enviar_celular(mensaje, celular)
    except Exception as e:
        logger.exception(f'Error enviando el codigo al celular, detalle: {e}')


def enviar_correo_codigo_verificacion(data):
    try:
        mensaje = f"Su código de verificación para ingresar a SGCPE es: {data.get('codigo')}"  # noqa
        subject = 'Código de Verificación para SGC PLANILLAS'
        message = mensaje
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [
            data.get('correo'),
        ]
        send_mail(subject, message, email_from, recipient_list)
        return True, ''
    except SMTPRecipientsRefused as e:
        logger.exception(f'Error enviando el código al correo, detalle: {e}')
        return False, f'Error en el correo registrado, detalle: {e}'
    except Exception as e:
        logger.exception(f'Error enviando el código al correo, detalle: {e}')
        return False, f'Error enviando el codigo al correo, detalle: {e}'


def obtener_nombre_mes_espanol(mes_ingles):
    meses_espanol = {
        'January': 'enero',
        'February': 'febrero',
        'March': 'marzo',
        'April': 'abril',
        'May': 'mayo',
        'June': 'junio',
        'July': 'julio',
        'August': 'agosto',
        'September': 'septiembre',
        'October': 'octubre',
        'November': 'noviembre',
        'December': 'diciembre',
    }
    return meses_espanol.get(mes_ingles, mes_ingles)


def enviar_adjunto(
    correo, tipo_verificacion, adjunto_url, fecha_solicitud, codigo_solicitud, datos_solicitante
):
    # Obtener el día, mes y año de la fecha de solicitud
    if fecha_solicitud:
        try:
            fecha_solicitud = datetime.strptime(fecha_solicitud, '%Y-%m-%d %H:%M:%S')
        except Exception:
            fecha_solicitud = datetime.strptime(fecha_solicitud, '%d/%m/%Y %H:%M:%S')

        dia_fecha_solicitud = fecha_solicitud.day
        mes_fecha_solicitud = obtener_nombre_mes_espanol(fecha_solicitud.strftime('%B'))
        anno_fecha_solicitud = fecha_solicitud.year
    else:
        fecha_solicitud = datetime.now()
        solicitudes = Solicitud.objects.filter(codigo_solicitud=codigo_solicitud)
        if solicitudes.exists():
            solicitud = solicitudes.first()
            audiencias = Audiencia.objects.filter(solicitud=solicitud)
            if audiencias.exists():
                audiencia = audiencias.first()
                fecha_solicitud = audiencia.fecha_modificacion

        dia_fecha_solicitud = fecha_solicitud.day
        mes_fecha_solicitud = obtener_nombre_mes_espanol(fecha_solicitud.strftime('%B'))
        anno_fecha_solicitud = fecha_solicitud.year

    solicitudes = Solicitud.objects.filter(codigo_solicitud=codigo_solicitud)
    solicitud = solicitudes.first() if solicitudes.exists() else None
    datos_solicitante = '{} {}, {}'.format(
        solicitud.apellido_paterno_solicitante,
        solicitud.apellido_materno_solicitante,
        solicitud.nombre_solicitante
        )
    data = {
        'correo': correo,
        'datos_solicitante': datos_solicitante,
        'fecha_solicitud': fecha_solicitud,
        'dia_fecha_solicitud': dia_fecha_solicitud,
        'mes_fecha_solicitud': mes_fecha_solicitud,
        'anno_fecha_solicitud': anno_fecha_solicitud,
        'codigo_solicitud': codigo_solicitud,
        'solicitud': solicitud
    }
    if tipo_verificacion == CORREO_VERIFICACION:
        return enviar_correo_adjunto(data=data, adjunto_url=adjunto_url)
    elif tipo_verificacion == CELULAR_VERIFICACION:
        return enviar_correo_adjunto(data=data, adjunto_url=adjunto_url)


def enviar_correo_adjunto(data, adjunto_url=None):
    try:
        link = FRONTEND_URL
        dia_fecha_solicitud = data.get('dia_fecha_solicitud')
        mes_fecha_solicitud = data.get('mes_fecha_solicitud')
        anno_fecha_solicitud = data.get('anno_fecha_solicitud')

        solicitudes = Solicitud.objects.filter(codigo_solicitud=data.get('codigo_solicitud', 'XXX'))
        solicitud = solicitudes.first() if solicitudes.exists() else None
        data_solicitante = '{} {}, {}'.format(
            solicitud.apellido_paterno_solicitante,
            solicitud.apellido_materno_solicitante,
            solicitud.nombre_solicitante
        )
        mensaje = f"""
        Estimado Señor (a) {data_solicitante} \n
        Me dirijo a usted para saludarlo cordialmente y en atención a la solicitud de audiencia de conciliación de la referencia, \n
        este despacho ha emitido la invitación para conciliar de fecha {dia_fecha_solicitud} de {mes_fecha_solicitud} de {anno_fecha_solicitud}, \n
        la cual se adjunta al presente para los fines pertinentes. \n
        Se recuerda que la concurrencia del trabajador y el empleador a la audiencia de conciliación es de carácter obligatorio, \n
        conforme al numeral 27.2 del artículo 27 del Decreto Legislativo 910. \n
        Asimismo, es muy importante confirmar la recepción del presente correo; \n
        para lo cual deberá contestar inmediatamente con el mensaje RECIBIDO. \n
        Sin otro particular, hago propicia la oportunidad para expresarle los sentimientos de mi consideración y estima personal. \n
        Saludos Cordiales."""  # noqa
        subject = 'NOTIFICAR INVITACIÓN PARA CONCILIAR DE LA SOLICITUD DE AUDIENCIA DE CONCILIACIÓN CON DOCUMENTO N° {}'.format(data.get('codigo_solicitud', 'XXX'))  # noqa
        message = mensaje
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [data.get('correo'), ]

        if adjunto_url:
            email = EmailMessage(
                subject,
                message,
                email_from,
                recipient_list,
            )
            if adjunto_url[0] == '/':
                adjunto_url = adjunto_url[1:]
            email.attach_file(adjunto_url)

            email.send()
        else:
            send_mail(subject, message, email_from, recipient_list)

        return True, ''
    except SMTPRecipientsRefused as e:
        logger.exception(f'Error enviando credenciales al correo, detalle: {e}')
        return False, f'Error en el correo registrado, detalle: {e}'
    except Exception as e:
        logger.exception(f'Error enviando credenciales al correo, detalle: {e}')
        return False, f'Error enviando las credenciales al correo, detalle: {e}'


def generar_codigo_verificacion(max_digit: int) -> str:
    _random = secrets.SystemRandom()
    return str(_random.randint((10 ** (max_digit - 1)), ((10**max_digit) - 1)))


def enviar_credenciales(user, tipo_verificacion):  # type: ignore
    decoded_password = si.get_siusuario_password(si(), user.pk_usuario)
    data = {
        'username': user.username,
        'celular': user.celular,
        'correo': user.email,
        'password': decoded_password
    }
    if tipo_verificacion == CORREO_VERIFICACION:
        return enviar_correo_credenciales(data=data)
    elif tipo_verificacion == CELULAR_VERIFICACION:
        return enviar_correo_credenciales(data=data)


def enviar_correo_credenciales(data):
    try:
        link = FRONTEND_URL
        mensaje = f"Sus credenciales para ingresar a SGCPE son los siguientes: \n Usuario: {data.get('username')} \n Contraseña: {data.get('password')} \n Link de acceso: {link}"  # noqa
        subject = 'Credenciales de acceso para SGCPE'
        message = mensaje
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [
            data.get('correo'),
        ]
        send_mail(subject, message, email_from, recipient_list)
        return True, ''
    except SMTPRecipientsRefused as e:
        logger.exception(f'Error enviando credenciales al correo, detalle: {e}')
        return False, f'Error en el correo registrado, detalle: {e}'
    except Exception as e:
        logger.exception(f'Error enviando credenciales al correo, detalle: {e}')
        return False, f'Error enviando las credenciales al correo, detalle: {e}'


def enviar_celular_credenciales(data):
    try:
        celular = data.get('celular')  # noqa
        mensaje = f"Sus credenciales ara ingresar a SGCPE son los siguientes: \n Usuario: {data.get('username')} \n Contraseña: {data.get('password')}"  # noqa
        # TODO: Agregar la funcion para enviar sms al celular
        # enviar_celular(mensaje, celular)
    except Exception as e:
        logger.exception(f'Error enviando las credenciales al celular, detalle: {e}')


def verify_recaptcha(g_token: str) -> bool:
    data = {
        'response': g_token,
        'secret': settings.RE_CAPTCHA_SECRET_KEY
    }
    resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result_json = resp.json()
    return result_json.get('success') is True
