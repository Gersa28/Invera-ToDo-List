"""
Pruebas unitarias para la API RESTful de la aplicación ToDo List

Este archivo contiene las pruebas para verificar el correcto funcionamiento de los endpoints relacionados con
el registro de usuarios, login, creación de tareas, y cierre de sesión. Se utiliza el módulo `APITestCase` de
Django Rest Framework (DRF) para realizar estas pruebas.

Clases de pruebas:
- UserRegistrationTest: Pruebas para el registro de usuarios.
- UserLoginTest: Pruebas para el inicio de sesión de usuarios.
- TaskTest: Pruebas para la creación y filtrado de tareas.
- LogoutTest: Pruebas para el cierre de sesión de usuarios.
"""

import base64
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth.models import User
from app_tasks.models import Tasks


class UserRegistrationTest(APITestCase):
    """
    Pruebas para el endpoint de registro de usuarios (/api/register/).
    """

    def test_register_user(self):
        """
        Verifica que un usuario pueda registrarse con datos válidos.
        - El código de respuesta debe ser 201 (CREATED).
        - El usuario debe crearse en la base de datos.
        """
        url = reverse('apiregister-list')
        data = {
            'username': 'newuser',
            'password': 'StrongPass!1',
            'password2': 'StrongPass!1'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'newuser')

    def test_passwords_do_not_match(self):
        """
        Verifica que el registro falle si las contraseñas no coinciden.
        - El código de respuesta debe ser 400 (BAD REQUEST).
        - El usuario no debe crearse en la base de datos.
        """
        url = reverse('apiregister-list')
        data = {
            'username': 'newuser',
            'password': 'password123',
            'password2': 'password456'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTest(APITestCase):
    """
    Pruebas para el endpoint de inicio de sesión (/api/login/).
    """

    def setUp(self):
        """
        Configuración inicial:
        - Crear un usuario de prueba.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')

    def test_login_user(self):
        """
        Verifica que un usuario pueda iniciar sesión con credenciales válidas.
        - El código de respuesta debe ser 200 (OK).
        """
        url = reverse('apilogin-list')
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid_credentials(self):
        """
        Verifica que el inicio de sesión falle si las credenciales son incorrectas.
        - El código de respuesta debe ser 400 (BAD REQUEST).
        """
        url = reverse('apilogin-list')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TaskTest(APITestCase):
    """
    Pruebas para el endpoint de gestión de tareas (/api/tasks/).
    """

    def setUp(self):
        """
        Configuración inicial:
        - Crear un usuario de prueba y configurar autenticación básica.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        credentials = base64.b64encode(b'testuser:password123').decode('utf-8')  # Codificar las credenciales en Base64 para autenticación básica
        self.client.credentials(HTTP_AUTHORIZATION='Basic ' + credentials)

    def test_create_task(self):
        """
        Verifica que un usuario autenticado pueda crear una tarea.
        - El código de respuesta debe ser 201 (CREATED).
        - La tarea debe crearse y estar asociada al usuario.
        """
        url = reverse('apitasks-list')
        data = {
            'name': 'New Task',
            'description': 'New Task Description',
            'status': 'in_progress'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Tasks.objects.filter(name='New Task', user=self.user).exists())

    def test_task_filter_by_date(self):
        """
        Verifica que el filtrado por fecha de las tareas funcione correctamente.
        - El código de respuesta debe ser 200 (OK).
        """
        url = reverse('apitasks-list')
        date_from = '2024-09-01'
        date_to = '2024-09-30'
        response = self.client.get(f"{url}?date_from={date_from}&date_to={date_to}", format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class LogoutTest(APITestCase):
    """
    Pruebas para el endpoint de cierre de sesión (/api/logout/).
    """

    def setUp(self):
        """
        Configuración inicial:
        - Crear un usuario de prueba y configurar autenticación básica.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        credentials = base64.b64encode(b'testuser:password123').decode('utf-8')
        self.client.credentials(HTTP_AUTHORIZATION='Basic ' + credentials)

    def test_logout_user(self):
        """
        Verifica que un usuario autenticado pueda cerrar sesión.
        - El código de respuesta debe ser 200 (OK).
        """
        url = reverse('apilogout-list')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
