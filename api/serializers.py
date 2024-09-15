"""
Serializadores para la API RESTful de la aplicación ToDo List

Este archivo contiene los serializadores para validar y transformar los datos en el formato adecuado,
que luego serán usados por las vistas de la API. 
Estos serializadores manejan el registro de usuarios,inicio de sesión, gestión de tareas y cierre de sesión.

Clases de serializadores:
- UserSerializer: Serializador para registrar nuevos usuarios.
- LoginSerializer: Serializador para autenticar usuarios.
- TasksSerializer: Serializador para la gestión de tareas.
- LogoutSerializer: Serializador para cerrar sesión (sin datos adicionales).
"""

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from django.contrib.auth import authenticate
from app_tasks.models import Tasks
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializador para registrar nuevos usuarios.
    
    Campos:
    - username: Debe ser único, validado por `UniqueValidator`.
    - password: La contraseña debe cumplir con las validaciones de Django.
    - password2: Campo adicional para confirmar la contraseña.

    Validaciones:
    - Se asegura de que las contraseñas coincidan antes de crear el usuario.
    """

    username = serializers.CharField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirmar contraseña")

    class Meta:
        model = User
        fields = ('username', 'password', 'password2')

    def validate(self, attrs):
        """
        Validar que ambas contraseñas coincidan.
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        """
        Crear un nuevo usuario después de validar los datos.
        - Encripta la contraseña usando `set_password`.
        """
        user = User.objects.create(username=validated_data['username'])
        user.set_password(validated_data['password'])  # Encripta la contraseña
        user.save()
        return user


class LoginSerializer(serializers.ModelSerializer):
    """
    Serializador para el inicio de sesión de usuarios.
    
    Campos:
    - username: Nombre de usuario.
    - password: Contraseña del usuario (solo escritura).

    Validaciones:
    - Verifica que ambos campos (username y password) estén presentes.
    - Autentica al usuario utilizando el método `authenticate` de Django.
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, data):
        """
        Validar que los campos username y password sean correctos.
        - Si la autenticación falla, lanza un error de validación.
        """
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Credenciales inválidas.")
        else:
            raise serializers.ValidationError("Debe proporcionar nombre de usuario y contraseña.")

        data['user'] = user
        return data


class TasksSerializer(ModelSerializer):
    """
    Serializador para la gestión de tareas.

    Campos:
    - id: Identificador único de la tarea (solo lectura).
    - user: Usuario propietario de la tarea (solo lectura).
    - name: Nombre de la tarea.
    - description: Descripción de la tarea.
    - status: Estado de la tarea (ej. en progreso, completado).
    - created_at: Fecha de creación de la tarea (solo lectura).
    - updated_at: Fecha de última actualización de la tarea (solo lectura).

    Los campos `user`, `created_at` y `updated_at` son de solo lectura.
    """

    class Meta:
        model = Tasks
        fields = ["id", "user", "name", "description", "status", "created_at", "updated_at"]
        read_only_fields = ("user", "created_at", "updated_at")


class LogoutSerializer(serializers.ModelSerializer):
    """
    Serializador para el cierre de sesión de usuarios.

    Este serializador no tiene campos, ya que el cierre de sesión no requiere datos adicionales.
    """

    class Meta:
        model = User
        fields = []
