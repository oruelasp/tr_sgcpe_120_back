from django.db import models

from apps.common import constants
from apps.common.models import PermissionsMixin, AuditableModel, TimeStampedModel
from apps.programacion.models import Sede


class User(PermissionsMixin, AuditableModel, TimeStampedModel):
    pk_usuario = models.CharField(primary_key=True, max_length=30, db_column='N_IDUSUARIO')
    tipo_documento = models.CharField('Tipo de Documento', db_column='V_CODTIPODOC', max_length=2)
    email = models.EmailField('Email', db_column='V_DESEMAIL', null=True, blank=True)
    username = models.CharField('Usuario', db_column='V_CODUSERNAME', max_length=30, unique=True)
    flag = models.CharField(
        db_column='C_FLGACT', max_length=1, default=constants.NO_CHAR_BINARY
    )
    password = models.CharField('Password', db_column='V_CODPASSWORD', max_length=128)
    celular = models.CharField('Celular', db_column='V_NUMCELULAR', max_length=15, blank=True, null=True)
    compartir_datos = models.CharField(
        db_column='C_FLGDATOS', max_length=1, default=constants.NO_CHAR_BINARY
    )
    codigo_institucion = models.CharField(
        db_column='V_CODPLI', max_length=18
    )
    codigo_region = models.CharField(
        db_column='V_CODREG', max_length=2
    )
    codigo_cargo = models.CharField(
        db_column='V_CODCARGO', max_length=2
    )
    terminos_condiciones = models.CharField(
        db_column='C_FLGTERMINOS', max_length=1, default=constants.NO_CHAR_BINARY
    )
    tipo_usuario = models.CharField(
        db_column='V_CODTIPOUSU', max_length=1, default=constants.NO_CHAR_BINARY
    )

    super_admin = models.CharField(
        db_column='C_FLGSUPER', max_length=1, default=constants.NO_CHAR_BINARY
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['pk_usuario']

    class Meta:
        managed = False
        ordering = ('username',)
        db_table = constants.get_tabla_tbx('USUARIO')

    def __str__(self):
        return str(self.pk_usuario)


class Permission(models.Model):
    pk_permiso = models.AutoField(primary_key=True, db_column='N_IDPERMISO')
    c_nombre = models.CharField('name', max_length=300, db_column='N_DESNOMBRE')
    c_modelo = models.CharField('name', max_length=300, db_column='V_DESMODELO')
    c_nombreapp = models.CharField('app', max_length=300, db_column='V_DESNOMBREAPP')
    n_flagcrea = models.BooleanField(default=True, db_column='C_FLGCREA')
    n_flaglee = models.BooleanField(default=True, db_column='C_FLGLEE')
    n_flagedita = models.BooleanField(default=True, db_column='C_FLGEDITA')
    n_flagborra = models.BooleanField(default=True, db_column='C_FLGBORRA')

    class Meta:
        managed = False
        verbose_name = 'permission'
        verbose_name_plural = 'permissions'
        ordering = ['c_nombreapp', 'c_modelo', 'c_nombre']
        db_table = constants.get_tabla_tbx('PERMISO')

    def __str__(self):
        return f'{self.c_nombreapp} | {self.c_modelo} | {self.c_nombre}'


class Menu(models.Model):
    pk_menu = models.AutoField(primary_key=True, db_column='N_IDMENU')
    nombre = models.CharField('nombre', max_length=300, db_column='N_DESNOMBRE')
    url = models.CharField('url', max_length=254, db_column='V_DESURL')
    parent = models.ForeignKey(
        'Menu', db_column='N_IDPARENT', on_delete=models.CASCADE
    )

    class Meta:
        managed = False
        verbose_name = 'permission'
        verbose_name_plural = 'permissions'
        db_table = constants.get_tabla_tbx('MENU')

    def __str__(self):
        return str(self.pk_menu)


class Group(models.Model):
    pk_grupo = models.CharField(primary_key=True, max_length=20, db_column='N_IDGRUPO')
    nombre = models.CharField('name', max_length=300, unique=True, db_column='N_DESNOMBRE')
    flagact = models.BooleanField(default=True, db_column='C_FLGACT')
    permissions = models.ManyToManyField(
        Permission, verbose_name='permissions', through='PermissionsGroup', blank=True
    )
    menus = models.ManyToManyField(
        Menu, verbose_name='menus', through='MenuGroup', blank=True
    )

    class Meta:
        managed = False
        verbose_name = 'grupo'
        verbose_name_plural = 'grupos'
        db_table = constants.get_tabla_tbx('GRUPO')

    def __str__(self):
        return self.nombre


class PermissionsGroup(models.Model):
    pk_gruper = models.AutoField(primary_key=True, db_column='N_IDGRUPER')
    n_idgrupo = models.ForeignKey(Group, on_delete=models.CASCADE, db_column='N_IDGRUPO')
    n_idpermiso = models.ForeignKey(Permission, on_delete=models.CASCADE, db_column='N_IDPERMISO')
    n_flagact = models.BooleanField(default=True, db_column='C_FLGACT')

    class Meta:
        managed = False
        verbose_name = 'permisogrupo'
        verbose_name_plural = 'permisogrupos'
        db_table = constants.get_tabla_tbx('GRUPER')


class MenuGroup(models.Model):
    pk_grumen = models.AutoField(primary_key=True, db_column='N_IDGRUMEN')
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE, db_column='N_IDGRUPO')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, db_column='N_IDMENU')

    class Meta:
        managed = False
        verbose_name = 'menugrupo'
        verbose_name_plural = 'menugrupo'
        db_table = constants.get_tabla_tbx('GRUMEN')


class Parametro(models.Model):
    pk_parametro = models.AutoField(primary_key=True, db_column='N_IDPARAMETRO')
    codigo = models.CharField(max_length=100, verbose_name='Código', db_column='V_DESCODIGO')
    nombre = models.CharField(max_length=300, verbose_name='Nombre', db_column='N_DESNOMBRE')
    valor = models.CharField(max_length=600, verbose_name='Valor', db_column='V_DESVALOR')

    class Meta:
        managed = False
        verbose_name = 'parametro'
        verbose_name_plural = 'parametros'
        db_table = constants.get_tabla_tbx('PARAMETRO')

    def __str__(self):
        return self.nombre


class Regla(models.Model):
    pk_regla = models.AutoField(primary_key=True, db_column='N_IDREGLA')
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE, db_column='N_IDGRUPO')
    modelo = models.CharField(max_length=300, verbose_name='Modelo', db_column='V_DESMODELO')
    metodo = models.CharField(max_length=600, verbose_name='Valor', db_column='V_DESMETODO')
    flag = models.CharField(
        db_column='C_FLGACT', max_length=1, default=constants.SI_CHAR_BINARY
    )

    class Meta:
        managed = False
        verbose_name = 'regla'
        verbose_name_plural = 'reglas'
        db_table = constants.get_tabla_tbx('REGLA')

    def __str__(self):
        return f'{self.grupo.pk} | {self.modelo}'


class UserGroup(models.Model):
    pk_usugru = models.AutoField(primary_key=True, db_column='N_IDUSUGRU')
    usuario = models.ForeignKey('seguridad.User', on_delete=models.CASCADE, db_column='N_IDUSUARIO')
    grupo = models.ForeignKey('seguridad.Group', on_delete=models.CASCADE, db_column='N_IDGRUPO')
    menu = models.ForeignKey('seguridad.Menu', on_delete=models.CASCADE, db_column='N_IDMENU')
    flag = models.CharField(db_column='C_FLGACT', max_length=1, default=constants.SI_CHAR_BINARY)

    class Meta:
        managed = False
        verbose_name = 'usuariogrupo'
        verbose_name_plural = 'usuariogrupos'
        db_table = constants.get_tabla_tbx('USUGRU')


class UserVerification(models.Model):
    pk_usuariover = models.IntegerField(db_column='N_IDUSUVER', primary_key=True)
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='user_verification',
        db_column='N_IDUSUARIO',
    )
    codigo = models.CharField(db_column='V_CODVALIDACION', max_length=10)
    estado = models.CharField(
        db_column='C_FLGACT', max_length=1, default=constants.SI_CHAR_BINARY
    )
    tipo_verificacion = models.CharField(db_column='C_FLGTIPOVER', max_length=1)
    fecha_expiracion = models.DateTimeField(db_column='D_FECEXPIRACION')

    class Meta:
        managed = False
        verbose_name = 'verificacion'
        verbose_name_plural = 'verificaciones'
        db_table = constants.get_tabla_tbx('USUVER')

