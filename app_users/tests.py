"""
Pruebas unitarias para la autenticación de usuarios en la aplicación Django

Este archivo contiene las pruebas para verificar la funcionalidad de registro, inicio de sesión y cierre de sesión
usando las vistas proporcionadas por Django. Se prueban casos exitosos y fallidos para garantizar la robustez de las vistas.

Clases:
- RegisterViewTest: Pruebas para la vista de registro de usuarios.
- LoginViewTest: Pruebas para la vista de inicio de sesión.
- LogoutViewTest: Pruebas para la vista de cierre de sesión.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class RegisterViewTest(TestCase):
    """
    Pruebas para la vista de registro de usuarios.

    Verifica que un usuario puede registrarse correctamente y maneja errores como contraseñas que no coinciden.
    """

    def test_register_user(self):
        """
        Verifica que un usuario puede registrarse con datos válidos.
        - Redirige al login después del registro exitoso.
        - El usuario se crea en la base de datos.
        """
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password1': '12345Abc!',
            'password2': '12345Abc!'
        })
        self.assertEqual(response.status_code, 302)  # Verifica la redirección tras el registro exitoso
        self.assertTrue(User.objects.filter(username='testuser').exists())  # Verifica que el usuario se creó

    def test_register_user_password_mismatch(self):
        """
        Verifica que el registro falla si las contraseñas no coinciden.
        - No redirige después de un fallo en la validación.
        - El usuario no se crea en la base de datos.
        """
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password1': '12345Abc!',
            'password2': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Verifica que sigue en la página de registro
        self.assertFalse(User.objects.filter(username='testuser').exists())  # Verifica que el usuario no se creó


class LoginViewTest(TestCase):
    """
    Pruebas para la vista de inicio de sesión.

    Verifica que un usuario puede iniciar sesión correctamente con credenciales válidas y que los intentos fallidos
    no autentican al usuario.
    """

    def setUp(self):
        """
        Configuración inicial: crear un usuario de prueba.
        """
        self.user = User.objects.create_user(username='testuser', password='12345Abc!')

    def test_login_user(self):
        """
        Verifica que un usuario puede iniciar sesión con credenciales válidas.
        - Redirige después del inicio de sesión exitoso.
        - El usuario está autenticado y la sesión está activa.
        """
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': '12345Abc!'
        })
        self.assertEqual(response.status_code, 302)  # Verifica la redirección tras el login exitoso
        self.assertIn('_auth_user_id', self.client.session)  # Verifica que el usuario está en la sesión

    def test_login_user_invalid_credentials(self):
        """
        Verifica que un usuario no puede iniciar sesión con credenciales incorrectas.
        - No redirige tras el intento fallido de inicio de sesión.
        - El usuario no está autenticado.
        """
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Verifica que sigue en la página de login
        self.assertNotIn('_auth_user_id', self.client.session)  # Verifica que el usuario no está autenticado


class LogoutViewTest(TestCase):
    """
    Pruebas para la vista de cierre de sesión.

    Verifica que un usuario autenticado pueda cerrar sesión correctamente.
    """

    def setUp(self):
        """
        Configuración inicial: crear un usuario de prueba e iniciar sesión.
        """
        self.user = User.objects.create_user(username='testuser', password='12345Abc!')
        self.client.login(username='testuser', password='12345Abc!')  # Iniciar sesión para las pruebas

    def test_logout_user(self):
        """
        Verifica que un usuario puede cerrar sesión correctamente.
        - Redirige después de cerrar sesión.
        - El usuario es desconectado y removido de la sesión.
        """
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Verifica la redirección tras el logout
        self.assertNotIn('_auth_user_id', self.client.session)  # Verifica que el usuario ha sido desconectado
