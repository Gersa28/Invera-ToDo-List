"""
Rutas para la API RESTful de la aplicación ToDo List

Este archivo define las rutas para el registro de usuarios, inicio de sesión, gestión de tareas y cierre de sesión,
utilizando Django Rest Framework (DRF) y los ViewSets correspondientes.

Rutas registradas:
- /api/register/ -> Registro de usuarios
- /api/login/ -> Inicio de sesión
- /api/tasks/ -> Gestión de tareas (CRUD)
- /api/logout/ -> Cierre de sesión
- /api/docs/ -> Documentación de la API generada automáticamente

Se utiliza el `DefaultRouter` de DRF para registrar las rutas de los ViewSets.

"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.documentation import include_docs_urls
from api.views import TaskViewSet, RegisterViewSet, LoginViewSet, LogoutViewSet

# Crear el router para registrar los ViewSets de la API
router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='apiregister')  # Rutas para el registro de usuarios
router.register(r'login', LoginViewSet, basename='apilogin')  # Rutas para el inicio de sesión
router.register(r'tasks', TaskViewSet, basename='apitasks')  # Rutas para el CRUD de tareas
router.register(r'logout', LogoutViewSet, basename='apilogout')  # Rutas para el cierre de sesión

# Definición de las rutas
urlpatterns = [
    # Incluye las rutas de la API registradas en el router
    path("api/", include(router.urls)),

    # Ruta para la documentación de la API generada automáticamente por DRF
    path("api/docs/", include_docs_urls(title="API Documentation")),
]
