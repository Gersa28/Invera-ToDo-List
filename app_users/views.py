"""
Vista de registro de usuarios para la aplicación de Django

Esta vista permite a los nuevos usuarios registrarse en la aplicación utilizando el formulario de creación de usuarios
`UserCreationForm` proporcionado por Django. Después de un registro exitoso, el usuario es redirigido a la página de inicio de sesión.

Clase:
- UsersRegisterView: Vista para registrar nuevos usuarios.
"""

from django.contrib.auth.forms import UserCreationForm
from django.views import generic
from django.urls import reverse_lazy


class UsersRegisterView(generic.CreateView):
    """
    Vista basada en clase (CBV) para el registro de nuevos usuarios.

    Atributos:
        - form_class: Usa el formulario `UserCreationForm` para la creación de usuarios.
        - template_name: Plantilla que se renderiza para mostrar el formulario de registro.
        - success_url: URL a la que se redirige tras un registro exitoso (en este caso, a la página de login).

    El registro se realiza utilizando el formulario `UserCreationForm`, que incluye la validación de contraseñas
    y la creación del nuevo usuario.
    """
    form_class = UserCreationForm
    template_name = "app_users/register.html"
    success_url = reverse_lazy("login")  # Redirige al login tras el registro exitoso
