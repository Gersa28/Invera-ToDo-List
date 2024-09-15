from django.urls import path
from .views import TaskListView, TaskCreateView, TaskUpdateView, TaskDeleteView

urlpatterns = [
    path("listar/", TaskListView.as_view(), name="tasks_list"),
    path("crear/", TaskCreateView.as_view(), name="tasks_create"),
    path("actualizar/<int:pk>/", TaskUpdateView.as_view(), name="tasks_update"),
    path("eliminar/<int:pk>/", TaskDeleteView.as_view(), name="tasks_delete"),  
]