# base/tests.py
from django.test import TestCase, Client
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.cache import cache

from .models import Task
from .forms import PositionForm

class AuthTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('tasks'))
    
    def test_authenticated_redirects(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('tasks'))

class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.task = Task.objects.create(
            user=self.user,
            title='Test task',
            description='Test description'
        )

    def test_task_creation(self):
        self.assertEqual(self.task.user.username, 'testuser')
        self.assertEqual(self.task.title, 'Test task')
        self.assertFalse(self.task.complete)
        self.assertTrue(timezone.now() - self.task.created < timezone.timedelta(seconds=1))

class TaskViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.task = Task.objects.create(
            user=self.user,
            title='Test task',
            description='Test content'
        )
    
    def test_task_list_view(self):
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test task')
        self.assertEqual(response.context['count'], 1)
    
    def test_task_create_view(self):
        response = self.client.post(reverse('task-create'), {
            'title': 'New task',
            'description': 'New description',
            'complete': False
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 2)
    
    def test_task_update_view(self):
        url = reverse('task-update', args=[self.task.pk])
        response = self.client.post(url, {
            'title': 'Updated title',
            'description': 'Updated description',
            'complete': True
        })
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated title')
        self.assertTrue(self.task.complete)
    
    def test_task_delete_view(self):
        url = reverse('task-delete', args=[self.task.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 0)
    
    def test_unauthorized_access(self):
        self.client.logout()
        urls = [
            reverse('tasks'),
            reverse('task-create'),
            reverse('task-update', args=[1]),
            reverse('task-delete', args=[1]),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('login')}?next={url}")

class TaskPermissionTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.user2 = User.objects.create_user(username='user2', password='12345')
        self.task = Task.objects.create(
            user=self.user1,
            title='User1 Task',
            description='Test content'
        )
    
    def test_cross_user_access(self):
        self.client.login(username='user2', password='12345')
        
        
        response = self.client.get(reverse('task', args=[self.task.pk]))
        self.assertEqual(response.status_code, 404)
        
        
        response = self.client.post(reverse('task-update', args=[self.task.pk]), {
            'title': 'Hacked Task',
            'description': 'Malicious content',
            'complete': True
        })
        self.assertEqual(response.status_code, 404)
        
        
        response = self.client.post(reverse('task-delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Task.objects.count(), 1)

class TaskReorderTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.tasks = [
            Task.objects.create(user=self.user, title=f'Task {i}')
            for i in range(3)
        ]
    
    def test_task_reorder(self):
        task_ids = [str(t.id) for t in self.tasks]
        new_order = [task_ids[2], task_ids[0], task_ids[1]]  # [id3, id1, id2]
        response = self.client.post(
            reverse('task-reorder'),
            {'position': ','.join(new_order)}
        )
        self.assertEqual(response.status_code, 302)
        

        tasks = Task.objects.filter(user=self.user).order_by('_order')
        self.assertEqual([t.id for t in tasks], [self.tasks[2].id, self.tasks[0].id, self.tasks[1].id])

class TemplateTest(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        
        self.complete_task = Task.objects.create(
            user=self.user,
            title='Complete Task',
            description='Completed task description',
            complete=True
        )
        self.incomplete_task = Task.objects.create(
            user=self.user,
            title='Incomplete Task',
            description='Incomplete task description',
            complete=False
        )
        
       
        self.client.login(
            username='testuser',
            password='testpass123'
        )

    def test_task_list_template_content(self):
        response = self.client.get(reverse('tasks'))
        
      
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base/task_list.html')
        
        
        self.assertContains(response, 'Complete Task')
        self.assertContains(response, 'Incomplete Task')
        
        
        self.assertContains(response, 'class="task-complete-icon"', count=1)
        self.assertContains(response, 'class="task-incomplete-icon"', count=1)
        
