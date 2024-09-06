"""
URLs para aplicación de Programación.

Copyright (C) 2022 PRODUCE.

Authors:
    Omar Ruelas Principe dff_temp57@produce.gob.pe>
"""
from django.urls import include, path

app_name = 'programacion'

urlpatterns = [
    path('api/', include('apps.programacion.api.urls', namespace='api')),
]
