from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, User


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='cache')
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user,
        )

    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        """Кэширование данных на главной странице работает корректно."""
        response = self.guest_client.get(reverse('posts:index'))
        cached_response = response.content
        Post.objects.create(text='Второй пост', author=self.test_user)
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(cached_response, response.content)
        cache.clear()
        response = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(cached_response, response.content)