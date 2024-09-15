"""
URL Configuration for the ToDo List Django Application

Este archivo define las rutas principales del proyecto Django, incluyendo las aplicaciones de la página de inicio, gestión de usuarios, tareas y la API.

- app_homepage: Gestión de la página de inicio.
- app_users: Manejo del registro, login y logout de usuarios.
- app_tasks: CRUD de tareas, accesible solo para usuarios autenticados.
- API: Proporciona endpoints RESTful mediante Django Rest Framework (DRF).
- Django Admin: Consola de administración estándar de Django.

Se define el uso de archivos estáticos utilizando las configuraciones de Django.

"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Ruta para la página principal (home) de la aplicación.
    path('', include('app_homepage.urls')),

    # Rutas para la gestión de usuarios (registro, inicio/cierre de sesión).
    path("app_users/", include("app_users.urls")),

    # Rutas para la gestión de tareas, accesible solo después de autenticarse.
    path("app_tasks/", include("app_tasks.urls")),

    # Consola de administración de Django.
    path("admin/", admin.site.urls),

    # Rutas para la API RESTful, proporcionadas por Django Rest Framework.
    path("", include("api.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
