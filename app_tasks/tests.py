"""
Pruebas unitarias para la aplicación de tareas en Django

Este archivo contiene las pruebas unitarias para las vistas relacionadas con las tareas.
Se incluyen pruebas para verificar la lista de tareas, la creación, actualización, eliminación de tareas,
y la funcionalidad de autenticación.

Clases:
- TaskListViewTest: Pruebas para la vista de lista de tareas.
- TaskCreateViewTest: Pruebas para la creación de tareas.
- TaskUpdateViewTest: Pruebas para la actualización de tareas.
- TaskDeleteViewTest: Pruebas para la eliminación de tareas.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Tasks
from datetime import datetime

class TaskListViewTest(TestCase):
    """
    Pruebas unitarias para la vista de lista de tareas.
    Verifica que el usuario solo pueda ver sus tareas, que los atributos sean correctos, y que el filtro de búsqueda funcione.
    """

    def setUp(self):
        """
        Configuración inicial:
        - Crear un usuario de prueba y sus tareas.
        - Crear un segundo usuario con tareas diferentes.
        """
        self.user = User.objects.create_user(username='admin', password='admin')
        self.task1 = Tasks.objects.create(name='Task 1', description='Description 1', user=self.user)
        self.task2 = Tasks.objects.create(name='Task 2', description='Description 2', user=self.user)

        self.usuario_dos = User.objects.create_user(username='usuario_dos', password='123456')
        Tasks.objects.create(name='Task 3', description='Description 3', user=self.usuario_dos)

        self.usuario_tres = User.objects.create_user(username='usuario_tres', password='123456')

    def test_should_return_200(self):
        """
        Verifica que la vista de lista de tareas esté disponible para usuarios autenticados.
        """
        self.client.login(username="admin", password="admin")
        url = reverse("tasks_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_view_authenticated_user(self):
        """
        Verifica que un usuario autenticado solo vea sus propias tareas y no las de otros usuarios.
        """
        self.client.login(username='admin', password='admin')
        response = self.client.get(reverse('tasks_list'))
        self.assertContains(response, 'Task 1')
        self.assertContains(response, 'Task 2')
        self.assertNotContains(response, 'Task 3')  # No debe ver tareas de otro usuario

    def test_task_creation(self):
        """
        Verifica que las tareas creadas tengan los atributos correctos.
        """
        self.client.login(username='usuario_tres', password='123456')
        self.task = Tasks.objects.create(name='Test Task', description='This is a test task', user=self.user )
        self.assertEqual(self.task.name, 'Test Task')  # Verifica que el título de la tarea sea 'Test Task'.
        self.assertEqual(self.task.description, 'This is a test task')  # Verifica que la descripción sea la correcta.
        self.assertNotEqual(self.task.status, 'completed')  # Verifica que la tarea no esté completada.
        self.assertIsInstance(self.task.created_at, datetime)  # Verifica que el campo 'created_at' sea un datetime.
        self.assertEqual(self.task.user, self.user)  # Verifica que la tarea esté asignada al usuario correcto.

    def test_should_return_200_with_tasks(self):
        """
        Verifica que la vista devuelva al menos una tarea en el contexto.
        """
        self.client.login(username="admin", password="admin")
        Tasks.objects.create(user=self.user, name="TestTask 1", description="Tarea para el Test", status="completed")
        url = reverse("tasks_list")
        response = self.client.get(url)
        self.assertEqual(response.context["tasks"].count(), 3)  # Verifica que se crean 3 tareas

    def test_search_filter(self):
        """
        Verifica que el filtro de búsqueda funcione correctamente.
        Realizar una solicitud POST a la URL de la vista 'tasks_list', enviando un parámetro 'q' con el valor 'Task 1'.
        """
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('tasks_list'), {'q': 'Task 1'}) # El parámetro 'q' representa el término de búsqueda que el usuario ingresa en la interfaz.
        self.assertEqual(response.status_code, 200) # Verificar que la respuesta HTTP tenga un código de estado 200, lo que indica que la solicitud fue exitosa.
        self.assertContains(response, 'Task 1') # Confirma que el término de búsqueda 'Task 1' aparece en los resultados.
        self.assertNotContains(response, 'Task 2') # Asegura que otras tareas no relacionadas, como 'Task 2', no aparezcan en los resultados.

    def test_no_logged_user_should_redirect(self):
        """
        Verifica que un usuario no autenticado sea redirigido al intentar acceder a la lista de tareas.
        """
        url = reverse("tasks_list") # Hacer la petición a la URL de la lista de tareas sin iniciar sesión
        response = self.client.get(url)        
        self.assertEqual(response.status_code, 302) # Verificar que el código de respuesta es 302 (redirección)        
        self.assertTrue(response.url.startswith(reverse("login"))) # Verificar que redirige al inicio de sesión (por defecto en Django es '/accounts/login/')


class TaskCreateViewTest(TestCase):
    """
    Pruebas unitarias para la creación de tareas en la vista TaskCreateView.
    """

    def setUp(self):
        """
        Configuración inicial: Crear un usuario de prueba.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_create_task_authenticated_user(self):
        """
        Verifica que un usuario autenticado pueda crear una tarea.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('tasks_create'), {
            'name': 'New Task',
            'description': 'New description',
            'status': 'in_progress',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Tasks.objects.filter(name='New Task', user=self.user).exists())


class TaskUpdateViewTest(TestCase):
    """
    Pruebas unitarias para la actualización de tareas en la vista TaskUpdateView.
    """

    def setUp(self):
        """
        Configuración inicial: Crear un usuario de prueba y una tarea asociada.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.task = Tasks.objects.create(name='Task 1', description='Description 1', status="not_started", user=self.user)

    def test_update_task_authenticated_user(self):
        """
        Verifica que un usuario autenticado pueda actualizar una tarea existente.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('tasks_update', kwargs={'pk': self.task.pk}), {
            'name': 'Updated Task',
            'description': 'Updated description',
            'status': 'in_progress',
        })
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.name, 'Updated Task')
        self.assertEqual(self.task.description, 'Updated description')
        self.assertEqual(self.task.status, 'in_progress')


class TaskDeleteViewTest(TestCase):
    """
    Pruebas unitarias para la eliminación de tareas en la vista TaskDeleteView.
    """

    def setUp(self):
        """
        Configuración inicial: Crear usuarios de prueba y tareas asociadas.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        self.task = Tasks.objects.create(name='Task 1', description='Description 1', status="not_started", user=self.user)
        self.other_task = Tasks.objects.create(name='Task 2', description='Description 2', status="not_started", user=self.other_user)

    def test_delete_own_task(self):
        """
        Verifica que un usuario autenticado pueda eliminar su propia tarea.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('tasks_delete', kwargs={'pk': self.task.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tasks.objects.filter(pk=self.task.pk).exists())

    def test_delete_other_user_task(self):
        """
        Verifica que un usuario no pueda eliminar tareas de otros usuarios.
        """
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('tasks_delete', kwargs={'pk': self.other_task.pk}))
        self.assertEqual(response.status_code, 404)
