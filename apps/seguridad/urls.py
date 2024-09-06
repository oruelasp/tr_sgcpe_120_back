from django.urls import include, path


app_name = 'seguridad'

urlpatterns = [
    path('api/', include('apps.seguridad.api.urls', namespace='api')),
]
