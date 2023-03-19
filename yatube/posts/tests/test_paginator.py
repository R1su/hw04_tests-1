from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post, Group
from django.conf import settings

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # Создадим запись в БД,
        super().setUpClass()
        cls.offset = 3
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test',
            slug='test-slug',
            description='test description',
        )
        cls.group2 = Group.objects.create(
            title='test',
            slug='test-slug2',
            description='test description',
        )
        # Создадим запись в БД,
        for p in range(settings.POSTS_PER_PAGE + cls.offset):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text='Тестовый текст',
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_contains_constant_posts(self):
        template_urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user]),
        ]
        for url in template_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.POSTS_PER_PAGE)

    def test_second_page_contains_offset_posts(self):
        template_urls = [
            reverse('posts:index') + '?page=2',
            reverse('posts:group_list', args=[self.group.slug]) + '?page=2',
            reverse('posts:profile', args=[self.user]) + '?page=2',
        ]
        for url in template_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(len(response.context['page_obj']),
                                 self.offset)

    def test_additional_index_post_create(self):
        Post.objects.create(
            author=self.user,
            group=self.group,
            text='Новый пост для проверки',
        )
        template_url = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user]),

        ]
        for url in template_url:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                response_post = response.context['page_obj'][0]
                self.assertEqual(response_post.text, 'Новый пост для проверки')

    def test_additional_wrong_group_post_create(self):
        """Дополнительная проверка, что этот пост не попал в группу,
        для которой не был предназначен.
        """
        Post.objects.create(
            author=self.user,
            group=self.group2,
            text='Тестовый текст',
        )
        response = self.guest_client.get(
            reverse('posts:group_list', args=[self.group.slug]) + '?page=2')
        profile_posts = len(response.context['page_obj'])
        self.assertEqual(profile_posts, self.offset)