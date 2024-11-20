from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

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
        cls.add_data = {
            'title': 'Note_2',
            'text': 'Note is two',
            'slug': 'adress_2'
        }

    def test_anonymous_user_can_not_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        url = reverse('notes:add')
        self.assertEqual(Note.objects.count(), 1)
        self.client.post(url, data=self.add_data)
        self.assertEqual(Note.objects.count(), 1)

    def test_authorized_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        url = reverse('notes:add')
        self.assertEqual(Note.objects.count(), 1)
        self.user_client.post(url, data=self.add_data)
        self.assertEqual(Note.objects.count(), 2)

    def test_slug(self):
        """Невозможность создания двух заметок с одинаковым slug."""
        url = reverse('notes:add')
        add_data_dublicate_slug = {
            'title': 'Note_3',
            'text': 'Note is three',
            'slug': 'adress'
        }
        self.assertEqual(Note.objects.count(), 1)
        self.user_client.post(url, data=add_data_dublicate_slug)
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Создание slug при его отсутствии с помощью slugify."""
        url = reverse('notes:add')
        add_data_is_not_slug = {
            'title': 'Note_3',
            'text': 'Note is three'
        }
        self.user_client.post(url, data=add_data_is_not_slug)
        note_with_slug = Note.objects.last()
        slugify_slug = slugify(add_data_is_not_slug['title'])
        self.assertEqual(note_with_slug.slug, slugify_slug)

    def test_author_can_delete_his_note(self):
        """Автор может удалить свою заметку."""
        url = reverse('notes:delete', args=(self.note.slug,))
        self.assertEqual(Note.objects.count(), 1)
        self.user_client.post(url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_not_delete_not_his_note(self):
        """Пользователь не может удалить чужую заметку."""
        url = reverse('notes:delete', args=(self.note.slug,))
        self.assertEqual(Note.objects.count(), 1)
        self.user2_client.post(url)
        self.assertEqual(Note.objects.count(), 1)

    def test_user_can_edit_his_note(self):
        """Автор может отредактировать свою заметку."""
        url = reverse('notes:edit', args=(self.note.slug,))
        self.user_client.post(url, self.add_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.author, self.user)
        self.assertEqual(self.note.title, self.add_data['title'])
        self.assertEqual(self.note.text, self.add_data['text'])
        self.assertEqual(self.note.slug, self.add_data['slug'])

    def test_user_cant_edit_not_his_note(self):
        """Пользователь может отредактировать чужую заметку."""
        url = reverse('notes:edit', args=(self.note.slug,))
        self.user2_client.post(url, self.add_data)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.author, self.user2)
        self.assertNotEqual(self.note.title, self.add_data['title'])
        self.assertNotEqual(self.note.text, self.add_data['text'])
        self.assertNotEqual(self.note.slug, self.add_data['slug'])
