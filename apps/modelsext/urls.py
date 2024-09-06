from django.urls import include, path


app_name = 'modelsext'

urlpatterns = [
    path('api/', include('apps.modelsext.api.urls', namespace='api')),
]
