# Register your models here.
from django.contrib import admin
from .models import Tasks


class TasksAdmin(admin.ModelAdmin):
    model = Tasks
    list_display = ["id", "name", "user", "status", "description", "created_at", "updated_at"]
    search_fields = ["name", "created_at"]  # Filtros de búsqueda


admin.site.register(Tasks, TasksAdmin)  # Parámetros: El Modelo y su Clase Registradora
