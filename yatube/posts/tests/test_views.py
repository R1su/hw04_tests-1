import shutil
import tempfile


from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile


from posts.models import Post, Group

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()

SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='Andrew')
        cls.group = Group.objects.create(
            title='Группа с постом',
            slug='test-slug',
            description='Тестовое описание',
        )
        # Создадим запись в БД,
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый текст',
            image=cls.uploaded,
            pk=101,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list', args=[self.group.slug]):
                'posts/group_list.html',
            reverse('posts:profile', args=[self.user]):
                'posts/profile.html',
            reverse('posts:post_detail', args=[self.post.pk]):
                'posts/post_detail.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:post_edit', args=[self.post.pk]):
                'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_correct_context_image(self):
        template_urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=['test-slug']),
            reverse('posts:profile', args=[self.user]),
        ]
        for url in template_urls:
            response = self.authorized_client.get(url)
            response_post = response.context['page_obj'][0].image
            self.assertEqual(response_post, self.post.image)

    def test_urls_show_correct_context(self):
        template_urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=['test-slug']),
            reverse('posts:profile', args=[self.user]),
        ]
        for url in template_urls:
            response = self.authorized_client.get(url)
            response_post = response.context['page_obj'][0]
            self.assertEqual(response_post, self.post)

    def test_post_detail_show_correct_context_image(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.pk]))
        response_post = response.context['post']
        self.assertEqual(response_post.image, self.post.image)

    def test_post_detail_show_correct_context(self):
        """Проверка post_detail на правильный контекст."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.pk]))
        response_post = response.context['post']
        self.assertEqual(response_post, self.post)

    def test_post_create_edit_show_correct_context(self):
        template_urls = [
            reverse('posts:post_edit', args=[self.post.pk]),
            reverse('posts:post_create'),
        ]
        for url in template_urls:
            response = self.authorized_client.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)