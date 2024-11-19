from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='User')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.user2 = User.objects.create(username='User2')
        cls.user2_client = Client()
        cls.user2_client.force_login(cls.user2)
        cls.note = Note.objects.create(
            title='Note_1',
            text='Note is first',
            slug='adress',
            author=cls.user
        )

    def test_pages_availability_for_anonymous_client(self):
        """Доступность страниц анонимному клиенту."""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for target in urls:
            with self.subTest(target=target):
                url = reverse(target)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_authorized_client(self):
        """Доступность страниц авторизованному клиенту."""
        urls = (
            'notes:home',
            'notes:list',
            'notes:success',
            'notes:add',
            'users:signup',
            'users:login',
            'users:logout',
        )
        for target in urls:
            with self.subTest(target=target):
                url = reverse(target)
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_two_users(self):
        """Доступность страниц заметок автору и другому пользователю."""
        clients_statuses = (
            (self.user_client, HTTPStatus.OK),
            (self.user2_client, HTTPStatus.NOT_FOUND),
        )
        urls = ('notes:edit', 'notes:detail', 'notes:delete')
        for clnt, status in clients_statuses:
            for target in urls:
                with self.subTest(clnt=clnt, target=target, status=status):
                    url = reverse(target, args=(self.note.slug,))
                    response = clnt.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Переадресация анонимного клиента на страницу логина."""
        login_url = reverse('users:login')
        urls_args = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for target, arg in urls_args:
            with self.subTest(target=target, arg=arg):
                url = reverse(target, args=arg)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
