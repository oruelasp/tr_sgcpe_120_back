from django.contrib import admin

from apps.programacion.models import (
    ActividadTrabajadorDia,
    MatrizTrabajadorDia,
    Modalidad,
    ObservacionTrabajadorDia,
    Programacion,
    ProgramacionTrabajador,
    ProgramacionTrabajadorDia,
    RotacionTrabajador,
    ConceptoPapeleta,
    PeriodoPapeleta
)


class ProgramacionTrabajadorInline(admin.TabularInline):

    model = ProgramacionTrabajador
    extra = 0


class ProgramacionTrabajadorDiaInline(admin.TabularInline):

    model = ProgramacionTrabajadorDia
    extra = 0


class ObservacionTrabajadorDiaInline(admin.TabularInline):

    model = ObservacionTrabajadorDia
    extra = 0


class ActividadTrabajadorDiaInline(admin.TabularInline):

    model = ActividadTrabajadorDia
    extra = 0


class ModalidadAdmin(admin.ModelAdmin):
    list_display = (
        'id_modalidad',
        'nombre',
        'activo',
        'removed',
    )
    search_fields = ('nombre',)


class ProgramacionAdmin(admin.ModelAdmin):
    list_display = (
        'id_programacion',
        'usuario',
        'mes',
        'semana',
        'inicio_semana',
        'fin_semana',
        'id_dependencia_programacion',
        'estado',
    )
    search_fields = (
        'semana',
        'usuario_id',
        'id_dependencia_programacion'
    )

    inlines = [
        ProgramacionTrabajadorInline,
    ]


class ProgramacionTrabajadorAdmin(admin.ModelAdmin):
    list_display = (
        'id_programacion_trabajador',
        'programacion',
        'trabajador',
        'modalidad',
    )
    search_fields = ('id_programacion_trabajador',)

    inlines = [
        ProgramacionTrabajadorDiaInline,
    ]


class ProgramacionTrabajadorDiaAdmin(admin.ModelAdmin):
    list_display = (
        'id_programacion_trabajador_dia',
        'programacion_trabajador',
        'modalidad',
    )
    search_fields = ('id_programacion_trabajador_dia', 'programacion_trabajador__id')


class MatrizTrabajadorDiaAdmin(admin.ModelAdmin):
    list_display = (
        'id_matriz_trabajador_dia', 'modalidad', 'fecha_envio', 'estado',)
    search_fields = ('id_matriz_trabajador_dia', 'modalidad__nombre')

    inlines = [ActividadTrabajadorDiaInline, ObservacionTrabajadorDiaInline]


class ActividadTrabajadorDiaAdmin(admin.ModelAdmin):
    list_display = (
        'id_actividad_trabajador_dia',
        'descripcion_producto',
        'fecha_entrega',
        'comentario',
        'matriz_trabajador_dia',
    )
    search_fields = ('descripcion_producto',)


class ObservacionTrabajadorDiaAdmin(admin.ModelAdmin):
    list_display = (
        'id_observacion_trabajador_dia',
        'observacion',
        'matriz_trabajador_dia',
    )
    search_fields = ('observacion',)


class RotacionTrabajadorAdmin(admin.ModelAdmin):
    list_display = (
        'id_rotacion_trabajador',
        'trabajador',
        'estado',
        'id_dependencia_origen',
        'id_dependencia_destino',
        'fecha_inicio',
        'fecha_fin'
    )
    search_fields = ('id_rotacion_trabajador',)


class ConceptoPapeletaAdmin(admin.ModelAdmin):
    list_display = (
        'id_concepto_papeleta',
        'nombre',
        'active',
        'adjunto',
        'falta',
        'tipo_periodo',
        'cantidad_dias'
    )
    search_fields = ('nombre',)


class PeriodoPapeletaAdmin(admin.ModelAdmin):
    list_display = (
        'id_periodo_papeleta',
        'nombre',
        'codigo'
    )
    search_fields = ('nombre', 'id_periodo_papeleta')


admin.site.register(Modalidad, ModalidadAdmin)
admin.site.register(Programacion, ProgramacionAdmin)
admin.site.register(ProgramacionTrabajador, ProgramacionTrabajadorAdmin)
admin.site.register(ProgramacionTrabajadorDia, ProgramacionTrabajadorDiaAdmin)
admin.site.register(MatrizTrabajadorDia, MatrizTrabajadorDiaAdmin)
admin.site.register(ActividadTrabajadorDia, ActividadTrabajadorDiaAdmin)
admin.site.register(ObservacionTrabajadorDia, ObservacionTrabajadorDiaAdmin)
admin.site.register(RotacionTrabajador, RotacionTrabajadorAdmin)
admin.site.register(ConceptoPapeleta, ConceptoPapeletaAdmin)
admin.site.register(PeriodoPapeleta, PeriodoPapeletaAdmin)
