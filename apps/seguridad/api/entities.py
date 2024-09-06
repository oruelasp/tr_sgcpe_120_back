from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class EnviarVerificacionResponse:
    pk_usuario: int
    fecha_expiracion: Optional[datetime] = None
    se_envio: Optional[bool] = True
    mensaje_envio: Optional[str] = ''
    password: Optional[str] = ''


@dataclass_json
@dataclass
class EnviarInvitacionResponse:
    se_envio: Optional[bool] = True
    mensaje_envio: Optional[str] = ''
