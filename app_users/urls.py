from django.contrib.auth.views import LoginView, LogoutView
from .views import UsersRegisterView
from django.urls import path

urlpatterns = [
    path("login/", LoginView.as_view(template_name="app_users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UsersRegisterView.as_view(), name="register"),
]
