# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class SitbPliego(models.Model):
    codpli = models.CharField(max_length=18, primary_key=True, db_column='N_CODPLI')
    despli = models.CharField(max_length=250, blank=True, null=True, db_column='V_DESPLI')
    flgact = models.CharField(max_length=1, blank=True, null=True, db_column='V_FLGACT')
    sector = models.CharField(db_column='N_CODSEC', max_length=2)
    codnivel = models.IntegerField(db_column='N_CODNIVEL')

    class Meta:
        db_table = 'SIMINTRA1"."SITB_PLIEGO'


class SiDependencia(models.Model):
    codigo_dependencia = models.IntegerField(db_column='N_NUMDEP', primary_key=True)
    coddep_principal = models.IntegerField(db_column='N_NUMDEPSUP', blank=True, null=True)
    siglas = models.CharField(db_column='V_CODDEP', max_length=30, db_collation='Modern_Spanish_CI_AS', blank=True,
                              null=True)
    dependencia = models.CharField(db_column='V_DESDEP', max_length=150, db_collation='Modern_Spanish_CI_AS',
                                   blank=True, null=True)
    nivel = models.CharField(db_column='V_CODNIVEL', max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True,
                             null=True)
    codigo_zona = models.CharField(db_column='V_CODZON', max_length=2, db_collation='Modern_Spanish_CI_AS', blank=True,
                                   null=True)
    codigo_region = models.CharField(db_column='V_CODREG', max_length=2, db_collation='Modern_Spanish_CI_AS', blank=True,
                                   null=True)
    flag = models.CharField(db_column='N_FLGACTIVO', max_length=1, db_collation='Modern_Spanish_CI_AS', blank=True,
                            null=True)
    piso = models.CharField(db_column='V_PISO', max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True,
                            null=True)

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."TDTBC_DEPENDENCIA'


class SiPerfil(models.Model):
    codigo_perfil = models.IntegerField(db_column='V_CODPER', primary_key=True)
    codigo_sistema = models.IntegerField(db_column='V_CODSIS')
    nombre_perfil = models.CharField(
        db_column='V_DESPER', max_length=50, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_PERFIL'


class SiUsuarioManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(flag='S')


class SiUsuario(models.Model):
    codigo_usuario = models.CharField(
        db_column='V_CODUSU', max_length=255, primary_key=True
    )
    codigo_personal = models.CharField(
        db_column='V_CODPERSONAL',
        max_length=255,
    )
    password_usuario = models.CharField(
        db_column='V_PASSUSU',
        max_length=255,
    )
    flag = models.CharField(
        db_column='V_FLGACT', max_length=1, blank=True, null=True
    )

    objects = SiUsuarioManager()

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_USUARIO'


class SiUsuarioTotal(models.Model):
    codigo_usuario = models.CharField(
        db_column='V_CODUSU', max_length=255, primary_key=True
    )
    codigo_personal = models.CharField(
        db_column='V_CODPERSONAL',
        max_length=255,
    )
    password_usuario = models.CharField(
        db_column='V_PASSUSU',
        max_length=255,
    )
    flag = models.CharField(
        db_column='V_FLGACT', max_length=1, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_USUARIO'


class SiUsuSistemaManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(flag='S')


class SiUsuSistema(models.Model):
    codigo_usuario = models.CharField(
        db_column='V_CODUSU', max_length=15, primary_key=True
    )
    codigo_sistema = models.CharField(
        db_column='V_CODSIS', max_length=3, blank=True, null=True
    )
    flag = models.CharField(
        db_column='V_FLGACT', max_length=1, blank=True, null=True
    )
    objects = SiUsuSistemaManager()

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_USUXSIST'

    def __str__(self):
        return f'{self.codigo_usuario}-{self.codigo_sistema}'


class SiUsuPerfilManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(flag='S')


class SiUsuPerfil(models.Model):
    codigo_usuario = models.CharField(
        db_column='V_CODUSU', max_length=15, primary_key=True
    )
    codigo_perfil = models.CharField(
        db_column='V_CODPER', max_length=3
    )
    codigo_sistema = models.CharField(
        db_column='V_CODSIS', max_length=3
    )
    flag = models.CharField(
        db_column='V_FLGACT', max_length=1, blank=True, null=True
    )
    # objects = SiUsuPerfilManager()

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_USUXPERFIL'

    def __str__(self):
        return f'{self.codigo_usuario}-{self.codigo_perfil}'


class SiRegimen(models.Model):
    id_regimen = models.CharField(db_column='V_CODREGLAB', primary_key=True, max_length=2)
    descripcion = models.CharField(db_column='V_DESREGLAB', max_length=60, blank=True, null=True)
    abreviacion = models.CharField(db_column='V_ABRREGLAB', max_length=40, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_REGIMLABORAL'


class SiPersonaManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(flag='1')


class SiPersona(models.Model):
    tipo_documento = models.CharField(
        db_column='V_CODTDOCIDE',
        max_length=2,
        blank=True,
        null=True,
    )
    codigo_personal = models.CharField(
        db_column='V_NUMDOC',
        max_length=15,
        primary_key=True,
    )
    apellido_paterno = models.CharField(
        db_column='V_APEPATER', max_length=40, blank=True, null=True
    )
    apellido_materno = models.CharField(
        db_column='V_APEMATER', max_length=40, blank=True, null=True
    )
    nombres = models.CharField(
        db_column='V_NOMBRES', max_length=100, blank=True, null=True
    )
    codigo_pais = models.CharField(
        db_column='V_CODNACION', max_length=6, blank=True, null=True
    )
    codigo_departamento = models.CharField(
        db_column='V_CODDEPNAC', max_length=2, blank=True, null=True
    )
    codigo_provincia = models.CharField(
        db_column='V_CODPRONAC', max_length=2, blank=True, null=True
    )
    codigo_distrito = models.CharField(
        db_column='V_CODDISNAC', max_length=2, blank=True, null=True
    )
    fecha_nacimiento = models.DateField(
        db_column='D_FECNAC', blank=True, null=True
    )
    fecha_caducidad = models.DateField(
        db_column='D_FECCAD', blank=True, null=True
    )
    sexo = models.CharField(
        db_column='C_CODSEXO', max_length=1, blank=True, null=True
    )
    estado_civil = models.CharField(
        db_column='C_ESTCIVIL', max_length=1, blank=True, null=True
    )
    usuario_creacion = models.CharField(
        'creado por',
        db_column='V_NOMUSUREG',
        max_length=30,
        editable=False,
    )
    usuario_modificacion = models.CharField(
        'modificado por',
        max_length=30,
        db_column='V_NOMUSUMOD',
        editable=False,
    )
    fecha_creacion = models.DateTimeField(
        'fecha de creación',
        db_column='D_FECREG',
        auto_now_add=True,
        editable=False,
    )
    fecha_modificacion = models.DateTimeField(
        'fecha de modificación',
        db_column='D_FECMOD',
        auto_now=True,
        editable=False,
    )
    host_registro = models.CharField(
        'Host Registro',
        max_length=50,
        db_column='V_HOSTREG',
        editable=False,
    )
    host_modificacion = models.CharField(
        'Host Modificación',
        max_length=50,
        db_column='V_HOSTMOD',
        editable=False,
    )
    sistema_registro = models.CharField(
        'Sistema Registro',
        max_length=3,
        db_column='V_CODSISREG',
        editable=False,
    )
    sistema_modificacion = models.CharField(
        'Sistema Modificación',
        max_length=3,
        db_column='V_CODSISMOD',
        editable=False,
    )
    flag = models.CharField(db_column='C_ESTACT', max_length=1, blank=True, null=True)

    objects = SiPersonaManager()

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_PERSONA'


class SiEmpresaManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(flag=1)


class SiEmpresa(models.Model):
    ruc = models.CharField(
        db_column='V_CODEMP',
        max_length=11,
        blank=True,
        null=True,
        primary_key=True,
    )
    numero_ruc = models.CharField(
        db_column='V_NUMRUC',
        max_length=11,
        blank=True,
        null=True
    )
    razon_social = models.CharField(
        db_column='V_RAZSOC', max_length=500, blank=True, null=True
    )
    nombre_direccion = models.CharField(
        db_column='V_DIREMP', max_length=255, blank=True, null=True
    )
    numero_direccion = models.CharField(
        db_column='V_NUMEMP', max_length=60, blank=True, null=True
    )
    codigo_departamento = models.CharField(
        db_column='V_CODDEP', max_length=2, blank=True, null=True
    )
    codigo_provincia = models.CharField(
        db_column='V_CODPRO', max_length=2, blank=True, null=True
    )
    codigo_distrito = models.CharField(
        db_column='V_CODDIS', max_length=2, blank=True, null=True
    )
    codigo_ciiu = models.CharField(
        db_column='V_CODCIIU', max_length=10, blank=True, null=True
    )

    tipo = models.CharField(
        db_column='V_FLGEMP', max_length=1, blank=True, null=True
    )
    usuario_creacion = models.CharField(
        'creado por',
        db_column='V_CODUSUREG',
        max_length=15,
        editable=False,
    )
    usuario_modificacion = models.CharField(
        'modificado por',
        max_length=15,
        db_column='V_CODUSUMOD',
        editable=False,
    )
    fecha_creacion = models.DateTimeField(
        'fecha de creación',
        db_column='D_FECREG',
        auto_now_add=True,
        editable=False,
    )
    fecha_modificacion = models.DateTimeField(
        'fecha de modificación',
        db_column='D_FECMOD',
        auto_now=True,
        editable=False,
    )
    host_registro = models.CharField(
        'Host Registro',
        max_length=30,
        db_column='V_HOSTREG',
        editable=False,
    )
    host_modificacion = models.CharField(
        'Host Registro',
        max_length=30,
        db_column='V_HOSTMOD',
        editable=False,
    )
    flag = models.IntegerField(db_column='N_FLGACTIVO', blank=True, null=True)

    objects = SiEmpresaManager()

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_EMPLEADOR'


class SiCargo(models.Model):
    codigo = models.CharField(db_column='V_CODCARGO', max_length=2,
                              db_collation='Modern_Spanish_CI_AS', primary_key=True)
    desc_cargo = models.CharField(db_column='V_NOMCARGO', max_length=50,
                                  db_collation='Modern_Spanish_CI_AS', blank=True,
                                  null=True)
    flag = models.CharField(db_column='V_FLGACT', max_length=1,
                            db_collation='Modern_Spanish_CI_AS', blank=True,
                            null=True)

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_PERCARGO'


class SiEscala(models.Model):
    codigo = models.CharField(db_column='V_CODESCALA', max_length=3,
                              db_collation='Modern_Spanish_CI_AS', primary_key=True)
    abreviatura = models.CharField(db_column='V_ABRVESCALA', max_length=15,
                                   db_collation='Modern_Spanish_CI_AS', blank=True,
                                   null=True)
    nombre = models.CharField(db_column='V_NOMESCALA', max_length=80,
                              db_collation='Modern_Spanish_CI_AS', blank=True,
                              null=True)
    descripcion = models.CharField(db_column='V_DESESCALA', max_length=500,
                                   db_collation='Modern_Spanish_CI_AS', blank=True,
                                   null=True)
    flag = models.CharField(db_column='V_FLGACT', max_length=1,
                            db_collation='Modern_Spanish_CI_AS', blank=True,
                            null=True)

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_ESCALAREMUN'


class TPersonal(models.Model):
    codigo_personal = models.CharField(db_column='V_CODPERSONAL', max_length=50,
                                       primary_key=True)  # Field name made lowercase.
    codigo_dependencia = models.IntegerField(db_column='N_NUMDEP',
                                          blank=True, null=True)  # Field name made lowercase.
    codigo_cargo = models.CharField(db_column='V_CODCARGO', max_length=50,
                                    blank=True, null=True)  # Field name made lowercase.
    codigo_escala = models.CharField(db_column='V_CODESCALAREMUN', max_length=50,
                                    blank=True, null=True)  # Field name made lowercase.
    apellido_paterno = models.CharField(db_column='V_DESAPEPAT', max_length=60,
                                        db_collation='Modern_Spanish_CI_AS', blank=True,
                                        null=True)  # Field name made lowercase.
    apellido_materno = models.CharField(db_column='V_DESAPEMAT', max_length=60,
                                        db_collation='Modern_Spanish_CI_AS', blank=True,
                                        null=True)  # Field name made lowercase.
    nombres = models.CharField(db_column='V_DESNOMBRES', max_length=40,
                               db_collation='Modern_Spanish_CI_AS', blank=True,
                               null=True)  # Field name made lowercase.
    email = models.CharField(db_column='V_CORREOE', max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.
    flag = models.CharField(db_column='N_FLGACTIVO', max_length=1,
                            db_collation='Modern_Spanish_CI_AS', blank=True,
                            null=True)

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."PRTBC_PERSONAL'


class Nacionalidad(models.Model):
    codigo_nacionalidad = models.CharField(db_column='v_codnacion', primary_key=True, max_length=2, null=True,
                                           blank=True, verbose_name='Código de nacionalidad')
    descripcion_nacionalidad = models.CharField(db_column='v_desnacion', max_length=100, null=True, blank=True,
                                                verbose_name='Descripción de nacionalidad')
    codigo_iso_nacionalidad = models.CharField(db_column='v_codisonac', max_length=3, null=True, blank=True,
                                               verbose_name='Código ISO de nacionalidad')

    # flag = models.CharField(db_column='v_flgact', max_length=1, null=True, blank=True, verbose_name='Flag')

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_NACIONALIDAD'
        verbose_name_plural = 'Nacionalidades'


class Departamento(models.Model):
    codigo_departamento = models.CharField(db_column='V_CODDEP', primary_key=True, max_length=2, null=True, blank=True,
                                           verbose_name='Código de departamento')
    descripcion_departamento = models.CharField(db_column='V_DESDEP', max_length=100, null=True, blank=True,
                                                verbose_name='Descripción de departamento')
    codigo_departamento_ren = models.CharField(db_column='V_CODDEPREN', max_length=2, null=True, blank=True,
                                               verbose_name='Código de departamento REN')
    flag = models.CharField(db_column='V_FLGACT', max_length=1, null=True, blank=True, verbose_name='Flag')

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_DEPARTAMENTO'
        verbose_name_plural = 'Departamentos'

    def __str__(self):
        return f'{self.codigo_departamento}-{self.descripcion_departamento}'


class Provincia(models.Model):
    codigo_provincia = models.CharField(db_column='v_codpro', primary_key=True, max_length=2, null=True, blank=True,
                                        verbose_name='Código de provincia')
    codigo_provincia_ren = models.CharField(db_column='v_codproren', max_length=2, null=True, blank=True,
                                            verbose_name='Código de provincia')
    descripcion_provincia = models.CharField(db_column='v_despro', max_length=100, null=True, blank=True,
                                             verbose_name='Descripción de provincia')
    codigo_departamento = models.CharField(db_column='v_coddep', max_length=2, null=True, blank=True,
                                           verbose_name='Código de departamento')
    codigo_departamento_ren = models.CharField(db_column='V_CODDEPREN', max_length=2, null=True, blank=True,
                                               verbose_name='Código de departamento REN')
    flag = models.CharField(db_column='v_flgact', max_length=1, null=True, blank=True, verbose_name='Flag')

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_PROVINCIA'
        verbose_name_plural = 'Provincias'


class Distrito(models.Model):
    codigo_distrito = models.CharField(db_column='v_coddis', primary_key=True, max_length=4, null=True, blank=True,
                                       verbose_name='Código de distrito')
    codigo_distrito_ren = models.CharField(db_column='v_coddisren', max_length=4, null=True, blank=True,
                                           verbose_name='Código de distrito REN')
    descripcion_distrito = models.CharField(db_column='v_desdis', max_length=100, null=True, blank=True,
                                            verbose_name='Descripción de distrito')
    codigo_provincia = models.CharField(db_column='v_codpro', max_length=2, null=True, blank=True,
                                        verbose_name='Código de provincia')
    codigo_provincia_ren = models.CharField(db_column='v_codproren', max_length=2, null=True,
                                            blank=True,
                                            verbose_name='Código de provincia')
    codigo_departamento = models.CharField(db_column='v_coddep', max_length=2, null=True, blank=True,
                                           verbose_name='Código de departamento')
    codigo_departamento_ren = models.CharField(db_column='V_CODDEPREN', max_length=2, null=True, blank=True,
                                               verbose_name='Código de departamento REN')
    flag = models.CharField(db_column='v_flgact', max_length=1, null=True, blank=True, verbose_name='Flag')

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_DISTRITO'
        verbose_name_plural = 'Distritos'


class SiTrabajadorManager(models.Manager):
    def get_queryset(self):
        return super(SiTrabajadorManager, self).get_queryset().filter(
            estado='ACTIVO',
            id_regimen__in=(1, 2, 3),
        ).exclude(condicion__in=('GENERAL', 'GENERICO'))


class SiTrabajador(models.Model):
    codigo_trabajador = models.CharField(db_column='V_CODTRA', max_length=50,
                                         primary_key=True)  # Field name made lowercase.
    tipo_documento = models.CharField(db_column='V_CODTDOCIDE', max_length=2, db_collation='Modern_Spanish_CI_AS',
                                      blank=True, null=True)  # Field name made lowercase.
    codigo_departamento = models.CharField(db_column='V_CODDEP', max_length=2, db_collation='Modern_Spanish_CI_AS',
                                           blank=True, null=True)
    codigo_provincia = models.CharField(db_column='V_CODPRO', max_length=2, db_collation='Modern_Spanish_CI_AS',
                                        blank=True, null=True)
    codigo_distrito = models.CharField(db_column='V_CODDIS', max_length=2, db_collation='Modern_Spanish_CI_AS',
                                       blank=True, null=True)
    apellido_paterno = models.CharField(db_column='V_APEPATTRA', max_length=60,
                                        db_collation='Modern_Spanish_CI_AS', blank=True,
                                        null=True)  # Field name made lowercase.
    apellido_materno = models.CharField(db_column='V_APEMATTRA', max_length=60,
                                        db_collation='Modern_Spanish_CI_AS', blank=True,
                                        null=True)  # Field name made lowercase.
    nombres = models.CharField(db_column='V_NOMTRA', max_length=40,
                               db_collation='Modern_Spanish_CI_AS', blank=True,
                               null=True)  # Field name made lowercase.
    genero = models.CharField(db_column='V_GENTRA', max_length=2,
                              db_collation='Modern_Spanish_CI_AS', blank=True,
                              null=True)  # Field name made lowercase.
    fecha_nacimiento = models.DateField(db_column='D_FECNACTRA', blank=True, null=True)  # Field name made lowercase.
    direccion = models.CharField(db_column='V_DIRTRA', max_length=60, db_collation='Modern_Spanish_CI_AS', blank=True,
                                 null=True)
    codigo_nacion = models.CharField(db_column='V_CODNACION', max_length=60, db_collation='Modern_Spanish_CI_AS',
                                     blank=True, null=True)
    email = models.CharField(db_column='V_EMAIL', max_length=50, db_collation='Modern_Spanish_CI_AS', blank=True,
                             null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_TRABAJADOR'


class SiGenero(models.Model):
    codigo_sexo = models.CharField(db_column='V_CODSEXO', primary_key=True, max_length=1,
                                   db_collation='Modern_Spanish_CI_AS')
    descripcion_sexo = models.CharField(db_column='V_DESSEXO', max_length=50, db_collation='Modern_Spanish_CI_AS',
                                        blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_SEXO'


class TipoDocumento(models.Model):
    codigo = models.CharField(db_column='V_CODTDOCIDE', primary_key=True, max_length=2, null=True, blank=True,
                              verbose_name='Código')
    descripcion = models.CharField(db_column='V_DESTDOCIDE', max_length=200, null=True, blank=True,
                                   verbose_name='Descripción')
    abreviatura = models.CharField(db_column='V_DESABR', max_length=3, null=True, blank=True,
                                   verbose_name='Abreviatura')
    flag = models.IntegerField(db_column='N_FLGESTDOC', null=True, blank=True, verbose_name='Flag')

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_TDOCIDE'
        verbose_name_plural = 'Tipo de Documentos'


class SiRegional(models.Model):
    codigo_region = models.CharField(db_column='V_CODREG', primary_key=True, max_length=2)
    nombre_region = models.CharField(db_column='V_NOMREG', max_length=100, blank=True, null=True)
    codigo_departamento = models.CharField(db_column='V_CODEP', max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_REGIONAL'


class SiZonal(models.Model):
    codigo_region = models.CharField(db_column='V_CODREG', max_length=2)
    codigo_zona = models.CharField(db_column='V_CODZON', primary_key=True, max_length=2)
    nombre_zona = models.CharField(db_column='V_NOMZON', max_length=100, blank=True, null=True)
    flag = models.CharField(db_column='V_ESTRETCC', max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'SIMINTRA1"."SITB_ZONAL'
