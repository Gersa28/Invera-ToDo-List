"""
Modelo Tasks para la aplicación de gestión de tareas

Este modelo representa una tarea que puede ser asignada a un usuario autenticado.
Cada tarea tiene un nombre, una descripción opcional, un estado y marcas de tiempo de creación y actualización.
Las tareas están vinculadas a los usuarios a través de una relación de clave foránea (ForeignKey).
"""

from django.db import models
from django.contrib.auth.models import User


class Tasks(models.Model):
    """
    Modelo que representa las tareas en el sistema.

    Atributos:
        - name: Nombre de la tarea (obligatorio).
        - description: Descripción de la tarea (opcional).
        - status: Estado de la tarea, con opciones predefinidas.
        - created_at: Fecha de creación de la tarea (automática).
        - updated_at: Fecha de última actualización de la tarea (automática).
        - user: Relación con el usuario que creó la tarea.

    Relación:
        - Cada tarea está vinculada a un usuario a través de una clave foránea (ForeignKey).
    """

    STATUS_CHOICES = [
        ("not_started", "No iniciado"),  # Tarea aún no comenzada.
        ("in_progress", "En progreso"),  # Tarea en desarrollo.
        ("completed", "Finalizado"),     # Tarea finalizada.
    ]

    name = models.TextField(max_length=100, verbose_name="nombre")
    description = models.TextField(max_length=300, verbose_name="descripción", blank=True)
    status = models.CharField( max_length=20, choices=STATUS_CHOICES, default="not_started", verbose_name="estado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="fecha de actualización")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="usuario")

    def __str__(self):
        """
        Devuelve el nombre de la tarea como representación en cadena del objeto.
        """
        return self.name

    class Meta:
        """
        Configuraciones adicionales para el modelo:
        - verbose_name: Nombre singular del modelo en la interfaz de administración.
        - verbose_name_plural: Nombre plural del modelo en la interfaz de administración.
        """
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
