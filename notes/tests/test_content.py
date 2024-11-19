from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
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

    def test_public_notes_for_two_users(self):
        """Публикация заметок пользователей."""
        users_attempt_connect = (
            (self.user_client, True),
            (self.user2_client, False),
        )
        for client, result in users_attempt_connect:
            with self.subTest(client=client, result=result):
                response = client.get(self.LIST_URL)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), result)

    def test_form_in_pages_add_edit(self):
        """Формы передаются на страницы добавления и редактирования."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for target, arg in urls:
            with self.subTest(target=target, arg=arg):
                url = reverse(target, args=arg)
                response = self.user_client.get(url)
                self.assertIn('form', response.context)
