TIPO_DOCUMENTO_DNI = '03'
TIPO_DOCUMENTO_CE = '06'
TIPO_DOCUMENTO_PASAPORTE = '08'
TIPO_DOCUMENTO_RUC = '09'
TIPO_DOCUMENTO_CSR = '17'
TIPO_DOCUMENTO_PTP = '18'
TIPO_DOCUMENTO_CEDULA_IDENTIDAD = '19'
TIPO_DOCUMENTO_CPP = '26'
TIPO_DOCUMENTO_NA = '99'

TIPO_DOCUMENTO = {
    TIPO_DOCUMENTO_DNI: 'DNI',
    TIPO_DOCUMENTO_CE: 'Carné de Extranjería',
    TIPO_DOCUMENTO_PASAPORTE: 'Pasaporte',
    TIPO_DOCUMENTO_CPP: 'Carné Permiso de Permanencia',
    TIPO_DOCUMENTO_RUC: 'RUC',
    TIPO_DOCUMENTO_CSR: 'Carné de Solicitud de Refugio',
    TIPO_DOCUMENTO_PTP: 'Permiso Temporal de Permanencia',
    TIPO_DOCUMENTO_CEDULA_IDENTIDAD: 'Cédula de Identidad',
    TIPO_DOCUMENTO_NA: 'No se Conoce',
}

TIPO_DOCUMENTO_LENGTH = {
    TIPO_DOCUMENTO_DNI: [8, 8],
    TIPO_DOCUMENTO_CE: [9, 13],
    TIPO_DOCUMENTO_PASAPORTE: [7, 9],
    TIPO_DOCUMENTO_CPP: [7, 9],
    TIPO_DOCUMENTO_RUC: [11, 11],
    TIPO_DOCUMENTO_CSR: [7, 11],
    TIPO_DOCUMENTO_PTP: [7, 9],
    TIPO_DOCUMENTO_CEDULA_IDENTIDAD: [7, 11],
    TIPO_DOCUMENTO_NA: [0, 15],
}

ESTADO_PROGRAMACION_NUEVO = '0'

ESTADO_PROGRAMACION_BORRADOR = '1'

ESTADO_PROGRAMACION_CREADO = '2'

ESTADO_PROGRAMACION_REGULARIZAR = '3'

ESTADO_PROGRAMACION_CERRADO = 'CERRADO'

ESTADO_PROGRAMACION_ATRASADO = 'ATRASADO'

CHOICES_ESTADO_PROGRAMACION = (
    (ESTADO_PROGRAMACION_NUEVO, 'NUEVO'),
    (ESTADO_PROGRAMACION_BORRADOR, 'BORRADOR'),
    (ESTADO_PROGRAMACION_CREADO, 'CREADO'),
    (ESTADO_PROGRAMACION_REGULARIZAR, 'POR REGULARIZAR'),
)


ESTADO_ACTIVIDAD_BORRADOR = '1'

ESTADO_ACTIVIDAD_ENVIADO = '2'

ESTADO_ACTIVIDAD_ATRASADO = '3'

ESTADO_ACTIVIDAD_ENCURSO = '4'

ESTADO_ACTIVIDAD_OBSERVADO = '5'

ESTADO_ACTIVIDAD_FIRMADO = '6'

CHOICES_ESTADO_ACTIVIDAD = (
    (ESTADO_ACTIVIDAD_BORRADOR, 'BORRADOR'),
    (ESTADO_ACTIVIDAD_ENVIADO, 'ENVIADO'),
    (ESTADO_ACTIVIDAD_ATRASADO, 'POR REGULARIZAR'),
    (ESTADO_ACTIVIDAD_ENCURSO, 'EN CURSO'),
    (ESTADO_ACTIVIDAD_OBSERVADO, 'OBSERVADO'),
    (ESTADO_ACTIVIDAD_FIRMADO, 'FIRMADO'),
)

ESTADO_ROTACION_PENDIENTE = '1'

ESTADO_ROTACION_RECHAZADO = '2'

ESTADO_ROTACION_VERIFICADO = '3'

CHOICES_ESTADO_ROTACION = (
    (ESTADO_ROTACION_PENDIENTE, 'PENDIENTE'),
    (ESTADO_ROTACION_RECHAZADO, 'RECHAZADO'),
    (ESTADO_ROTACION_VERIFICADO, 'VERIFICADO'),
)

DIA_LUNES = '1'
DIA_MARTES = '2'
DIA_MIERCOLES = '3'
DIA_JUEVES = '4'
DIA_VIERNES = '5'

CHOICES_DIAS = (
    (DIA_LUNES, 'LUNES'),
    (DIA_MARTES, 'MARTES'),
    (DIA_MIERCOLES, 'MIERCOLES'),
    (DIA_JUEVES, 'JUEVES'),
    (DIA_VIERNES, 'VIERNES'),
)

NUEVO = '0'
ASISTIDO = '1'
TARDANZA = '2'
FALTA = '3'
EN_CURSO = '4'
INACTIVO = '5'

CHOICES_ASISTENCIA = (
    (NUEVO, 'NUEVO'),
    (ASISTIDO, 'ASISTIDO'),
    (TARDANZA, 'TARDANZA'),
    (FALTA, 'FALTA'),
    (EN_CURSO, 'EN CURSO'),
    (INACTIVO, 'INACTIVO')
)

#ID_DB_ROL_DEPENDENCIA = '760'
#ID_DB_ROL_ROTACION = '762'
#ID_DB_ROL_TRABAJADOR = '758'
#ID_DB_ROL_RRHH = '761'


TIPO_CALENDARIO = '1'
TIPO_HABIL = '2'

TIPO_DIAS = (
    (TIPO_CALENDARIO, 'CALENDARIO'),
    (TIPO_HABIL, 'HABIL'),
)

ESTADO_PENDIENTE_PAPELETA = '1'
ESTADO_APROBADA_PAPELETA = '2'
ESTADO_RECHAZADA_PAPELETA = '3'
ESTADO_OBSERVADA_PAPELETA = '4'
ESTADO_VERIFICADA_PAPELETA = '5'
ESTADO_DENEGADA_PAPELETA = '6'
ESTADO_RETENIDA_PAPELETA = '7'

TIPO_ONOMASTICO = '0013'
TIPO_CITA = '0003'
TIPO_COMISION = '0008'
TIPO_ASUNTO = '0050'
TIPO_COMPENSACION = '0025'
TIPO_OMISION = '0029'
TIPO_JUDICIAL = '0059'
TIPO_PERMISO = '0062'
TIPO_INGRESO = '0012'
TIPO_ASISTENCIA = '0067'

TIPO_CONCEPTO = (
    (TIPO_ONOMASTICO, 'ONOMASTICO'),
    (TIPO_CITA, 'CITA MÉDICA'),
    (TIPO_COMISION, 'COMISION DE SERVICIO'),
    (TIPO_ASUNTO, 'ASUNTOS PARTICULARES'),
    (TIPO_COMPENSACION, 'COMPENSACIÓN POR DESCANSO MÉDICO'),
    (TIPO_OMISION, 'OMISIÓN DE MARCADO'),
    (TIPO_JUDICIAL, 'CITACIÓN JUDICIAL O POLICIAL'),
    (TIPO_PERMISO, 'PERMISOS SINDICALES'),
    (TIPO_INGRESO, 'AUTORIZACIÓN DE INGRESO'),
    (TIPO_ASISTENCIA, 'ASISTENCIA REMOTA')
)

CHOICES_ESTADO_PAPELETA = (
    (ESTADO_PENDIENTE_PAPELETA, 'PENDIENTE'),
    (ESTADO_APROBADA_PAPELETA, 'APROBADA'),
    (ESTADO_RECHAZADA_PAPELETA, 'RECHAZADA'),
    (ESTADO_OBSERVADA_PAPELETA, 'OBSERVADA'),
    (ESTADO_VERIFICADA_PAPELETA, 'VERIFICADA'),
    (ESTADO_DENEGADA_PAPELETA, 'DENEGADA'),
    (ESTADO_RETENIDA_PAPELETA, 'RETENIDA')
)

LIMITE_DIAS_PAPELETAS = 3

CODIGO_DIARIO = '3'
CODIGO_MENSUAL = '2'
CODIGO_ANUAL = '1'

HORARIOS_REGIMENES = {
    '1': 8.5,
    '2': 9.25,
    '3': 9,
}

HORA_SALIDA_REGIMEN = {
    '1': '16:45:00',
    '2': '17:30:00',
    '3': '17:15:00'
}

ID_REGIMEN_1 = '01'
ID_REGIMEN_2 = '02'
ID_REGIMEN_3 = '03'

ID_MODALIDAD_MIXTO = 3

NO_CHAR_BINARY = '0'
SI_CHAR_BINARY = '1'
NA_CHAR_BINARY = '2'
SI_CHAR_TEXT = 'Sí'
NO_CHAR_TEXT = 'No'

CATEGORIA = 'cuarta'
CATEGORIA_5TA = 'quinta'

ESQUEMA_NOMBRE = 'SGCPESYS'
ESQUEMA_SIGLAS = 'GCPE'

TIPO_TABLA_NATURALEZA = {
    'mantenimiento': 'TB',
    'movimiento': 'MV'
}

TIPO_TABLA_ESTRUCTURA = {
    'cabecera': 'C',
    'detalle': 'D',
    'subdetalle': 'S',
    'no_pertenece': 'X'
}


def get_tabla_tbx(modelo):
    return '{}"."{}{}{}_{}'.format(
        ESQUEMA_NOMBRE,
        ESQUEMA_SIGLAS,
        TIPO_TABLA_NATURALEZA.get('mantenimiento'),
        TIPO_TABLA_ESTRUCTURA.get('no_pertenece'),
        modelo
    )


def get_tabla_mvc(modelo):
    return '{}"."{}{}{}_{}'.format(
        ESQUEMA_NOMBRE,
        ESQUEMA_SIGLAS,
        TIPO_TABLA_NATURALEZA.get('movimiento'),
        TIPO_TABLA_ESTRUCTURA.get('cabecera'),
        modelo
    )


def get_tabla_mvd(modelo):
    return '{}"."{}{}{}_{}'.format(
        ESQUEMA_NOMBRE,
        ESQUEMA_SIGLAS,
        TIPO_TABLA_NATURALEZA.get('movimiento'),
        TIPO_TABLA_ESTRUCTURA.get('detalle'),
        modelo
    )


def get_tabla_mvs(modelo):
    return '{}"."{}{}{}_{}'.format(
        ESQUEMA_NOMBRE,
        ESQUEMA_SIGLAS,
        TIPO_TABLA_NATURALEZA.get('movimiento'),
        TIPO_TABLA_ESTRUCTURA.get('subdetalle'),
        modelo
    )


def get_tabla_mvx(modelo):
    return '{}"."{}{}{}_{}'.format(
        ESQUEMA_NOMBRE,
        ESQUEMA_SIGLAS,
        TIPO_TABLA_NATURALEZA.get('movimiento'),
        TIPO_TABLA_ESTRUCTURA.get('no_pertenece'),
        modelo
    )


TIPO_USUARIO_EMPRESA = '2'
TIPO_USUARIO_PERSONA = '1'
TIPO_USUARIO_NA = '99'

USUARIO_INTERNO = 'usuario_interno'
USUARIO_EXTERNO = 'usuario_externo'

TIPO_DOCUMENTO_EQ = {
    TIPO_DOCUMENTO_DNI: '1',
    TIPO_DOCUMENTO_CE: '4',
    TIPO_DOCUMENTO_RUC: '6',
}

ANONYMOUS_USER = '99999999'
CODIGO_PAIS = 'PE'
ANHO_FISCAL = '2023'
CONFIDENCIAL_USER = '123454321'

ESTADO_SI_AUTORIZADO = 'S'
ESTADO_NO_AUTORIZADO = 'E'

CORREO_VERIFICACION = '2'
CELULAR_VERIFICACION = '1'

CHOICES_TIPO_VERIFIFACION = (
    (CORREO_VERIFICACION, 'Correo'),
    (CELULAR_VERIFICACION, 'Celular'),
)

ESTADO_SOLICITUD_ARCHIVADO = '0'
ESTADO_SOLICITUD_PENDIENTE = '1'
ESTADO_SOLICITUD_PROGRAMADA = '2'
ESTADO_SOLICITUD_ASIGNADA = '3'
ESTADO_SOLICITUD_FINALIZADA = '4'
ESTADO_SOLICITUD_REPROGRAMADA = '5'
ESTADO_SOLICITUD_ANULADA = '6'

ESTADO_SOLICITUD_CHOICES = (
    (ESTADO_SOLICITUD_ARCHIVADO, 'Archivado'),
    (ESTADO_SOLICITUD_PENDIENTE, 'Pendiente'),
    (ESTADO_SOLICITUD_PROGRAMADA, 'Programada'),
    (ESTADO_SOLICITUD_ASIGNADA, 'Asignada'),
    (ESTADO_SOLICITUD_FINALIZADA, 'Atendida'),
    (ESTADO_SOLICITUD_REPROGRAMADA, 'Reprogramada'),
    (ESTADO_SOLICITUD_ANULADA, 'Anulada'),
)

DICT_ESTADO_SOLICITUD = {
    ESTADO_SOLICITUD_ARCHIVADO: 'Archivado',
    ESTADO_SOLICITUD_PENDIENTE: 'Pendiente',
    ESTADO_SOLICITUD_PROGRAMADA: 'Programada',
    ESTADO_SOLICITUD_ASIGNADA: 'Asignada',
    ESTADO_SOLICITUD_FINALIZADA: 'Finalizada',
    ESTADO_SOLICITUD_REPROGRAMADA: 'Reprogramada',
    ESTADO_SOLICITUD_ANULADA: 'Anulada',
}

ESTADO_AUDIENCIA_PENDIENTE = '1'
ESTADO_AUDIENCIA_ASIGNADA = '2'
ESTADO_AUDIENCIA_ATENDIDA = '3'
ESTADO_AUDIENCIA_ANULADA = '4'

ESTADO_AUDIENCIA_CHOICES = (
    (ESTADO_AUDIENCIA_PENDIENTE, 'Pendiente'),
    (ESTADO_AUDIENCIA_ASIGNADA, 'Asignada'),
    (ESTADO_AUDIENCIA_ATENDIDA, 'Atendida'),
    (ESTADO_AUDIENCIA_ANULADA, 'Anulada')
)

ASISTENCIA_ENTIDAD_NA = '0'
ASISTENCIA_ENTIDAD_SOLICITANTE = '1'
ASISTENCIA_ENTIDAD_INVITADO = '2'

ASISTENCIA_AUDIENCIA_NULA = '0'
ASISTENCIA_AUDIENCIA_TOTAL = '1'
ASISTENCIA_AUDIENCIA_SOLICITANTE = '2'
ASISTENCIA_AUDIENCIA_INVITADO = '3'
ASISTENCIA_AUDIENCIA_NA = '4'


ASISTENCIA_AUDIENCIA_CHOICES = (
    (ASISTENCIA_AUDIENCIA_NULA, 'Inasistencia total'),
    (ASISTENCIA_AUDIENCIA_TOTAL, 'Asistencia Total'),
    (ASISTENCIA_AUDIENCIA_SOLICITANTE, 'Asistió Solo Solicitante'),
    (ASISTENCIA_AUDIENCIA_INVITADO, 'Asistió Solo Invitado'),
)

ASISTENCIA_AUDIENCIA_DICT = {
    ASISTENCIA_AUDIENCIA_NULA: 'Inasistencia total',
    ASISTENCIA_AUDIENCIA_TOTAL: 'Asistencia Total',
    ASISTENCIA_AUDIENCIA_SOLICITANTE: 'Asistió Solicitante',
    ASISTENCIA_AUDIENCIA_INVITADO: 'Asistió Invitado',
    ASISTENCIA_AUDIENCIA_NA: 'NA'
}

RESULTADO_AUDIENCIA_DESACUERDO = '0'
RESULTADO_AUDIENCIA_ACUERDO_TOTAL = '1'
RESULTADO_AUDIENCIA_ACUERDO_PARCIAL = '2'
RESULTADO_AUDIENCIA_ACUERDO_POSTERGACION = '3'
RESULTADO_AUDIENCIA_ACUERDO_NA = '4'


RESULTADO_AUDIENCIA_CHOICES = (
    (RESULTADO_AUDIENCIA_DESACUERDO, 'Desacuerdo'),
    (RESULTADO_AUDIENCIA_ACUERDO_TOTAL, 'Acuerdo Total'),
    (RESULTADO_AUDIENCIA_ACUERDO_PARCIAL, 'Acuerdo Parcial'),
    (RESULTADO_AUDIENCIA_ACUERDO_POSTERGACION, 'Para postergación'),
    (RESULTADO_AUDIENCIA_ACUERDO_NA, 'Sin Resultado de audiencia')
)

RESULTADO_AUDIENCIA_DICT = {
    RESULTADO_AUDIENCIA_DESACUERDO: 'Falta de acuerdo',
    RESULTADO_AUDIENCIA_ACUERDO_TOTAL: 'Acuerdo Total',
    RESULTADO_AUDIENCIA_ACUERDO_PARCIAL: 'Acuerdo Parcial',
    RESULTADO_AUDIENCIA_ACUERDO_POSTERGACION: 'Para postergación',
    RESULTADO_AUDIENCIA_ACUERDO_NA: 'Sin Resultado de audiencia'
}

CODIGO_MOTIVO_OTROS = '99'

CODIGO_SEXO_M = '1'
CODIGO_SEXO_F = '2'
CODIGO_GENERO_M = 'M'
CODIGO_GENERO_F = 'F'

DICT_SEXO_GENERO = {
    CODIGO_SEXO_M: CODIGO_GENERO_M,
    CODIGO_SEXO_F: CODIGO_GENERO_F
}

DICT_GENERO_SEXO = {
    CODIGO_GENERO_M: CODIGO_SEXO_M,
    CODIGO_GENERO_F: CODIGO_SEXO_F
}

CODIGO_PLANTILLA_ACTA = '1'
CODIGO_PLANTILLA_POSTERGACION = '2'
CODIGO_PLANTILLA_ASISTENCIA_UNIT = '3'
CODIGO_PLANTILLA_DESACUERDO = '4'
CODIGO_PLANTILLA_INASISTENCIA = '5'
CODIGO_PLANTILLA_INVITACION = '6'
CODIGO_PLANTILLA_REPROGRAMACION = '7'

DICT_CODIGO_PLANTILLA = {
    CODIGO_PLANTILLA_ACTA: 'Acta de Conciliación',
    CODIGO_PLANTILLA_POSTERGACION: 'Acta de postergación de audiencia',
    CODIGO_PLANTILLA_ASISTENCIA_UNIT: 'Acta de asistencia de una de las partes',
    CODIGO_PLANTILLA_DESACUERDO: 'Constancia sin acuerdo de partes',
    CODIGO_PLANTILLA_INASISTENCIA: 'Informe de inasistencia de partes',
    CODIGO_PLANTILLA_INVITACION: 'Invitación para conciliación',
    CODIGO_PLANTILLA_REPROGRAMACION: 'Invitación para conciliar-reprogramación',
}

ETAPA_VIDA_NINEZ = [0, 11]
ETAPA_VIDA_ADOLESCENCIA = [12, 17]
ETAPA_VIDA_JUVENTUD = [18, 29]
ETAPA_VIDA_ADULTEZ = [30, 59]
ETAPA_VIDA_VEJEZ = [60, 120]

CODIGO_NINEZ = '1'
CODIGO_ADOLESCENCIA = '2'
CODIGO_JUVENTUD = '3'
CODIGO_ADULTEZ = '4'
CODIGO_VEJEZ = '5'

DICT_ETAPA_VIDA = {
    CODIGO_NINEZ: {
        'rango':  ETAPA_VIDA_NINEZ,
        'descripcion': 'Niñez'
    },
    CODIGO_ADOLESCENCIA: {
        'rango':  ETAPA_VIDA_ADOLESCENCIA,
        'descripcion': 'Adolescencia'
    },
    CODIGO_JUVENTUD: {
        'rango':  ETAPA_VIDA_JUVENTUD,
        'descripcion': 'Juventud'
    },
    CODIGO_ADULTEZ: {
        'rango':  ETAPA_VIDA_ADULTEZ,
        'descripcion': 'Adultez'
    },
    CODIGO_VEJEZ: {
        'rango':  ETAPA_VIDA_VEJEZ,
        'descripcion': 'Vejez'
    },
}

MODALIDAD_PRESENCIAL = '0'
MODALIDAD_VIRTUAL = '1'
MODALIDAD_NA = '2'

DICT_MODALIDAD = {
    MODALIDAD_PRESENCIAL: 'Presencial',
    MODALIDAD_VIRTUAL: 'Virtual',
    MODALIDAD_NA: 'N/A'
}


# HS019-2: Solicitud Detallada por Empresa
RESPONSE_DETALLADO_EMPRESA_EXAMPLE = [
    {
        "tipo_categoria": "Quinta",
        "fecha_de_pago": "",
        "fecha_de_emision": "",
        "tipo_de_contrato_o_comprobante": "A PLAZO INDETERMINADO - D LEG 728",
        "numero_de_contrato_o_comprobante": "",
        "ocupacion": "OCUPACION NO ESPECIFICADA",
        "categoria_ocupacional": "EMPLEADO",
        "situacion_especial": "NINGUNA",
        "periodo_tributario": "202401",
        "periodo_inicio": "03/08/2015",
        "periodo_fin": "31/12/2017",
        "razon_social": "ASOCIACION DE BANCOS DEL PERU",
        "ruc": "20100123330",
        "ingreso": [
            {"concepto": "0107 - TRABAJO EN DIA DE FERIADO O DIA DE DESCANSO", "monto_de_pago": 316.67},
            {"concepto": "0121 - REMUNERACION O JORNAL BASICO", "monto_de_pago": 2300.00},
            {"concepto": "0201 - ASIGNACION FAMILIAR", "monto_de_pago": 75.00}
        ],
        "descuentos": [{"concepto": "0701 - ADELANTADO", "monto_de_pago": 0}],
        "aportaciones_trabajador": [
            {"concepto": "0601 - SISTEMA PRIVADO DE PENSIONES COMISION PORCENTUAL", "monto_de_pago": 45.49},
            {"concepto": "0605 - RENTA QUINTA CATEGORÍA RETENCIONES", "monto_de_pago": 73.67}
        ],
        "aportaciones_empleador": [
            {"concepto": "0804 - ESSALUD", "monto_de_pago": 242.25}
        ],
        "otros_conceptos": [{"concepto": "-", "monto_de_pago": "-"}],
        "regimen_publico": [{"concepto": "-", "monto_de_pago": "-"}]
    },
    {
        "tipo_categoria": "Quinta",
        "fecha_de_pago": "",
        "fecha_de_emision": "",
        "tipo_de_contrato_o_comprobante": "A PLAZO INDETERMINADO - D LEG 728",
        "numero_de_contrato_o_comprobante": "",
        "ocupacion": "OCUPACION NO ESPECIFICADA",
        "categoria_ocupacional": "EMPLEADO",
        "situacion_especial": "NINGUNA",
        "periodo_tributario": "202403",
        "periodo_inicio": "03/08/2015",
        "periodo_fin": "31/12/2017",
        "razon_social": "ASOCIACION DE BANCOS DEL PERU",
        "ruc": "20100123330",
        "ingreso": [
            {"concepto": "0107 - TRABAJO EN DIA DE FERIADO O DIA DE DESCANSO", "monto_de_pago": 816.67},
            {"concepto": "0121 - REMUNERACION O JORNAL BASICO", "monto_de_pago": 1300.00},
            {"concepto": "0201 - ASIGNACION FAMILIAR", "monto_de_pago": 105.00}
        ],
        "descuentos": [{"concepto": "0701 - ADELANTADO", "monto_de_pago": 0}],
        "aportaciones_trabajador": [
            {"concepto": "0601 - SISTEMA PRIVADO DE PENSIONES COMISION PORCENTUAL", "monto_de_pago": 15.49},
            {"concepto": "0605 - RENTA QUINTA CATEGORÍA RETENCIONES", "monto_de_pago": 93.67}
        ],
        "aportaciones_empleador": [
            {"concepto": "0804 - ESSALUD", "monto_de_pago": 242.25}
        ],
        "otros_conceptos": [{"concepto": "-", "monto_de_pago": "-"}],
        "regimen_publico": [{"concepto": "-", "monto_de_pago": "-"}]
    }
]

# HS019-3: Solicitud Detallada General
RESPONSE_DETALLADO_GENERAL_EXAMPLE = [
    {
        "tipo_categoria": "Cuarta",
        "fecha_de_pago": "03/08/2015",
        "fecha_de_emision": "30/08/2015",
        "tipo_de_contrato_o_comprobante": "RECIBO POR HONORARIOS",
        "numero_de_contrato_o_comprobante": "E12-000423",
        "ocupacion": "",
        "categoria_ocupacional": "",
        "situacion_especial": "",
        "periodo_tributario": "202401",
        "periodo_inicio": "03/08/2015",
        "periodo_fin": "31/09/2015",
        "razon_social": "ASOCIACION DE BANCOS DEL PERU",
        "ruc": "20100123330",
        "ingreso": [
            {
                "concepto": "000 - RECIBO POR HONORARIOS",
                "monto_de_pago": 3106.67
            }
        ],
        "descuentos": [
            {
                "concepto": "",
                "monto_de_pago": 0
            }
        ],
        "aportaciones_trabajador": [
            {
                "concepto": "",
                "monto_de_pago": 0.0
            },
            {
                "concepto": "",
                "monto_de_pago": 0.0
            }
        ],
        "aportaciones_empleador": [
            {
                "concepto": "",
                "monto_de_pago": 0.0
            }
        ],
        "otros_conceptos": [
            {
                "concepto": "",
                "monto_de_pago": 0.0
            }
        ],
        "regimen_publico": [
            {
                "concepto": "",
                "monto_de_pago": 0.0
            }
        ]
    },
    {
        "tipo_categoria": "Cuarta",
        "fecha_de_pago": "03/08/2015",
        "fecha_de_emision": "30/08/2015",
        "tipo_de_contrato_o_comprobante": "RECIBO POR HONORARIOS",
        "numero_de_contrato_o_comprobante": "E12-000426",
        "ocupacion": "",
        "categoria_ocupacional": "",
        "situacion_especial": "",
        "periodo_tributario": "201601",
        "periodo_inicio": "03/08/2016",
        "periodo_fin": "31/09/2016",
        "razon_social": "ASOCIACION DE BANCOS DEL PERU",
        "ruc": "20100123330",
        "ingreso": [
            {
                "concepto": "000 - RECIBO POR HONORARIOS",
                "monto_de_pago": 5106.67
            }
        ],
        "descuentos": [
            {
                "concepto": "",
                "monto_de_pago": 0
            }
        ],
        "aportaciones_trabajador": [
            {
                "concepto": "",
                "monto_de_pago": 0.0
            },
            {
                "concepto": "",
                "monto_de_pago": 0.0
            }
        ],
        "aportaciones_empleador": [
            {
                "concepto": "",
                "monto_de_pago": 0.0
            }
        ],
        "otros_conceptos": [
            {
                "concepto": "",
                "monto_de_pago": 0.0
            }
        ],
        "regimen_publico": [
            {
                "concepto": "",
                "monto_de_pago": 0.0
            }
        ]
    }
]
# HS019-1: Solicitud Consolidada por Empresa
RESPONSE_CONSOLIDADO_EMPRESA_EXAMPLE = [
    {
        "tipo_categoria": "Quinta Categoría",
        "razon_social": "DELOSI S.A.",
        "ruc": "20100123330",
    },
    {
        "tipo_categoria": "Quinta Categoría",
        "razon_social": "MINISTERIO DE JUSTICIA",
        "ruc": "20120123313",
    }
]
