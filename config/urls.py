from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('seguridad/', include('apps.seguridad.urls', namespace='seguridad')),
    path('programacion/', include('apps.programacion.urls', namespace='programacion')),
    path('modelsext/', include('apps.modelsext.urls', namespace='modelsext')),
]
