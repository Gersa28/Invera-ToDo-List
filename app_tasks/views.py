"""
Vistas para la gestión de tareas en la aplicación ToDo List

Este archivo contiene vistas basadas en clases (CBVs) para gestionar tareas, como listar, crear, actualizar y eliminar. Todas las vistas requieren que el usuario esté autenticado, utilizando el mixin `LoginRequiredMixin`.

Vistas:
- TaskListView: Lista de tareas con soporte para búsqueda y filtrado.
- TaskCreateView: Permite a los usuarios autenticados crear nuevas tareas.
- TaskUpdateView: Permite a los usuarios autenticados actualizar tareas existentes.
- TaskDeleteView: Permite a los usuarios autenticados eliminar sus propias tareas.
"""

from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Tasks
from .forms import TaskForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.dateparse import parse_date
from django.db.models import Q
import logging

logger = logging.getLogger('app_tasks')


class TaskListView(LoginRequiredMixin, ListView):
    """
    Vista para listar las tareas del usuario autenticado, con soporte para búsquedas y filtrado por fechas.

    - Filtra las tareas del usuario autenticado por nombre, descripción y fecha de creación.
    - Sobrescribe el método `post` para manejar la búsqueda.
    """
    model = Tasks
    template_name = "app_tasks/task_list.html"
    context_object_name = "tasks"

    def post(self, request, *args, **kwargs):
        """
        Sobrescribir el método POST para manejar la lógica de búsqueda y filtrado.
        """
        self.object_list = self.get_queryset()  # Obtener el queryset con los filtros aplicados
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_queryset(self):
        """
        Sobrescribir `get_queryset` para obtener las tareas del usuario autenticado y aplicar los filtros de búsqueda.
        """
        queryset = Tasks.objects.filter(user=self.request.user)

        # Parámetros de búsqueda (nombre, descripción y fechas)
        search_query = self.request.POST.get("q", "")
        date_from = self.request.POST.get("date_from", "")
        date_to = self.request.POST.get("date_to", "")

        # Filtrar por contenido (nombre o descripción)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        # Filtrar por fecha de creación (desde)
        if date_from:
            date_from_parsed = parse_date(date_from)
            if date_from_parsed:
                queryset = queryset.filter(created_at__date__gte=date_from_parsed)

        # Filtrar por fecha de creación (hasta)
        if date_to:
            date_to_parsed = parse_date(date_to)
            if date_to_parsed:
                queryset = queryset.filter(created_at__date__lte=date_to_parsed)

        return queryset


class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    Vista para crear una nueva tarea.

    - Asigna automáticamente el usuario autenticado a la tarea.
    - Sobrescribe los métodos `form_valid` y `form_invalid` para registrar logs en caso de éxito o fallo.
    """
    model = Tasks
    form_class = TaskForm
    template_name = "app_tasks/create_task.html"
    success_url = reverse_lazy("tasks_list")

    def form_valid(self, form):
        """
        Sobrescribir `form_valid` para asignar el usuario autenticado a la tarea y registrar la acción.
        """
        form.instance.user = self.request.user
        logger.info(f"Tarea creada por {self.request.user}")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Sobrescribir `form_invalid` para registrar un warning en caso de fallo en la creación de la tarea.
        """
        logger.warning(f"Error al crear la tarea por {self.request.user}")
        return super().form_invalid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vista para actualizar una tarea existente.
    
    - Permite a los usuarios autenticados actualizar únicamente sus tareas.
    """
    model = Tasks
    form_class = TaskForm
    template_name = "app_tasks/update_task.html"
    success_url = reverse_lazy("tasks_list") # Redirige a la lista de tareas después de actualizar


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    """
    Vista para eliminar una tarea existente.

    - Asegura que solo el propietario de la tarea pueda eliminarla.
    """
    model = Tasks
    template_name = "app_tasks/delete_task.html"
    success_url = reverse_lazy("tasks_list")

    def get_queryset(self):
        """
        Sobrescribir `get_queryset` para asegurar que el usuario autenticado solo pueda eliminar sus propias tareas.
        """
        return Tasks.objects.filter(user=self.request.user)
