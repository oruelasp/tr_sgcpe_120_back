from django.contrib import admin

from apps.seguridad.models import Grupo, Usuario, Menu, GrupoMenu, Permiso, GrupoPermiso, Parametro


class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'codigo_trabajador',
        'id_dependencia_programacion'
    )
    search_fields = ('codigo_trabajador', 'id_dependencia_programacion')


class GrupoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'valor',
        'id_rol_login',
    )
    search_fields = ('nombre',)


class GrupoMenuAdmin(admin.ModelAdmin):
    list_display = (
        'grupo',
        'menu',
    )
    search_fields = ('grupo_id', 'menu_id')


class ParametroAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre',
        'valor'
    )
    search_fields = ('codigo', 'nombre', 'valor')


class PermisoAdmin(admin.ModelAdmin):
    list_display = (
        'id_permiso',
        'nombre',
        'modelo',
    )
    search_fields = ('nombre',)


class GrupoPermisoAdmin(admin.ModelAdmin):
    list_display = (
        'grupo',
        'permiso',
        'active'
    )
    search_fields = ('grupo_id', 'permiso_id')
    list_filter = ('active',)

    actions = ('activar', 'desactivar')

    def activar(self, request, queryset):
        for rec in queryset:
            grupo_permiso = GrupoPermiso.objects.filter(id=rec.id).last()
            try:
                grupo_permiso.active = True
                grupo_permiso.save()
            except GrupoPermiso.DoesNotExist:
                continue
        self.message_user(request, 'Grupos Permisos activados')

    def desactivar(self, request, queryset):
        for rec in queryset:
            grupo_permiso = GrupoPermiso.objects.filter(id=rec.id).last()
            try:
                grupo_permiso.active = False
                grupo_permiso.save()
            except GrupoPermiso.DoesNotExist:
                continue
        self.message_user(request, 'Grupos Permisos activados')


class MenuAdmin(admin.ModelAdmin):
    list_display = (
        'id_menu',
        'nombre',
        'url',
    )
    search_fields = ('nombre',)


admin.site.register(Menu, MenuAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Parametro, ParametroAdmin)
admin.site.register(Grupo, GrupoAdmin)
admin.site.register(GrupoMenu, GrupoMenuAdmin)
admin.site.register(Permiso, PermisoAdmin)
admin.site.register(GrupoPermiso, GrupoPermisoAdmin)
