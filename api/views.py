"""
Vistas para la API RESTful de la aplicación ToDo List

Este archivo contiene los `ViewSets` que manejan el registro, login, logout y CRUD de tareas. Se utiliza Django Rest Framework (DRF) para la creación de estas vistas.

Clases:
- RegisterViewSet: Vista para registrar nuevos usuarios.
- LoginViewSet: Vista para iniciar sesión de usuarios.
- TaskViewSet: Vista para la gestión de tareas (listar, crear, actualizar y eliminar).
- LogoutViewSet: Vista para cerrar sesión de usuarios.

Autenticación:
- Se soportan múltiples clases de autenticación como `SessionAuthentication` para navegadores y `BasicAuthentication` para herramientas como Postman.
"""

from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .serializers import LoginSerializer, LogoutSerializer, UserSerializer, TasksSerializer
from django.contrib.auth.models import User
from app_tasks.models import Tasks
from django.db.models import Q
from django.utils.dateparse import parse_date
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.authentication import SessionAuthentication
import logging


logger = logging.getLogger('api')  # Logger para registrar acciones dentro de la API


class RegisterViewSet(viewsets.ModelViewSet):
    """
    Vista para registrar nuevos usuarios.
    
    Atributos:
        - queryset: Lista de todos los usuarios en la base de datos.
        - serializer_class: Utiliza `UserSerializer` para validar y crear usuarios.
        - authentication_classes: No se requiere autenticación para registrar un nuevo usuario.
        - permission_classes: Permite acceso a cualquier usuario (autenticado o no).
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = []  # No se requiere autenticación para el registro
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Método sobrescrito para registrar un nuevo usuario.
        Verifica que el serializer sea válido antes de crear el usuario.
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response({'user': serializer.data}, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginViewSet(viewsets.ModelViewSet):
    """
    Vista para el inicio de sesión de usuarios.

    Atributos:
        - serializer_class: Utiliza `LoginSerializer` para validar las credenciales de login.
        - http_method_names: Solo permite el método `POST`.
        - authentication_classes: No requiere autenticación para iniciar sesión.
        - permission_classes: Permite acceso a cualquier usuario.
    """

    serializer_class = LoginSerializer
    http_method_names = ['post']
    authentication_classes = [] # No se requiere autenticación para el Login
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Método sobrescrito para manejar el inicio de sesión.
        Verifica las credenciales y autentica al usuario si son válidas.
        """
        if request.user.is_authenticated: # Si hay algún usuario autenticado, lo deslogueamos primero
            logout(request)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(User, username=serializer.validated_data['username'])
            if user.check_password(serializer.validated_data['password']):
                login(request, user)
                return Response({
                    "message": "Login exitoso",
                    "Username": user.username,
                }, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskViewSet(viewsets.ModelViewSet):
    """
    Vista para la gestión de tareas (CRUD).

    Atributos:
        - serializer_class: Utiliza `TasksSerializer` para validar y gestionar las tareas.
        - permission_classes: Solo permite el acceso a usuarios autenticados.
        - authentication_classes: Soporta `SessionAuthentication` y `BasicAuthentication` dependiendo de la solicitud.
    """

    serializer_class = TasksSerializer
    permission_classes = [IsAuthenticated]
    # authentication_classes = [SessionAuthentication] # Para el navegador
    # authentication_classes = [BasicAuthentication] # Aparece PopUp en Navegador # Para clientes como Postman
    # authentication_classes = [SessionAuthentication, BasicAuthentication]  # Combinar ambas

    def get_authenticators(self):
        """
        Método sobrescrito para determinar la clase de autenticación a usar según el encabezado de la solicitud.
        """        
        if self.request.headers.get('Authorization'): # Si la solicitud contiene el encabezado Authorization, usar BasicAuthentication
            return [BasicAuthentication()]
        else: # De lo contrario, usar SessionAuthentication para el navegador
            return [SessionAuthentication()] 

    def get_queryset(self):
        """
        Sobrescribe el método para obtener las tareas del usuario autenticado.
        También permite filtrar por nombre, descripción y fecha de creación.
        """
        queryset = Tasks.objects.filter(user=self.request.user)
        search_query = self.request.GET.get('q', '')
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')

        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query))

        if date_from:
            date_from_parsed = parse_date(date_from)
            if date_from_parsed:
                queryset = queryset.filter(created_at__date__gte=date_from_parsed)

        if date_to:
            date_to_parsed = parse_date(date_to)
            if date_to_parsed:
                queryset = queryset.filter(created_at__date__lte=date_to_parsed)

        return queryset

    def perform_create(self, serializer):
        """
        Método sobrescrito para asociar la tarea creada con el usuario autenticado.
        También registra la acción en los logs.
        """
        if serializer.is_valid():
            logger.info(f"Tarea creada por el usuario: {self.request.user}")
            serializer.save(user=self.request.user)
        else:
            logger.error(f"Error al crear la tarea: {serializer.errors}")


class LogoutViewSet(viewsets.ModelViewSet):
    """
    Vista para cerrar sesión de usuarios.

    Atributos:
        - serializer_class: Utiliza `LogoutSerializer` para validar la acción de logout.
        - http_method_names: Permite los métodos `GET` y `POST` para cerrar sesión.
        - permission_classes: Solo permite el acceso a usuarios autenticados.
    """

    serializer_class = LogoutSerializer
    http_method_names = ['get', 'post']
    permission_classes = [IsAuthenticated]

    def get_authenticators(self):
        """
        Método sobrescrito para determinar la clase de autenticación a usar según el encabezado de la solicitud.
        """
        if self.request.headers.get('Authorization'): # Si la solicitud contiene el encabezado Authorization, usar BasicAuthentication
            return [BasicAuthentication()]
        else: # De lo contrario, usar SessionAuthentication para el navegador            
            return [SessionAuthentication()]

    def create(self, request, *args, **kwargs): # El método create se ejecuta cuando se realiza una solicitud POST al endpoint
        """
        Cierra la sesión del usuario actual usando `POST`.
        """
        logout(request)
        return Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs): # El método list se ejecuta cuando se realiza una solicitud GET al endpoint
        """
        Permite el cierre de sesión usando `GET`.
        """
        logout(request)
        return Response({"message": "Logout exitoso (GET)"}, status=status.HTTP_200_OK)
