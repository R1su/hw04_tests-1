from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test',
            slug='test-slug',
            description='test-description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            pk=101,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_access(self):
        template_list = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.post.author}/',
            f'/posts/{self.post.pk}/',

        ]
        for url in template_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_unexisting_page(self):
        """Несуществующая страница возвращает 404"""
        response = self.guest_client.get('/posts/vot_tak_vot/')
        self.assertEqual(response.status_code, 404)

    def test_redirect_404_page(self):
        """Несуществующая страница возвращает 404"""
        response = self.guest_client.get('/posts/vot_tak_vot/')
        self.assertTemplateUsed(response, 'core/404.html')

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_uses_correct_template(self):
        post_detail = reverse('posts:post_detail', args=[self.post.pk])
        post_edit = reverse('posts:post_edit', args=[self.post.pk])
        template_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.post.author}/': 'posts/profile.html',
            post_detail: 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            post_edit: 'posts/create_post.html',
        }
        for url, template in template_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)