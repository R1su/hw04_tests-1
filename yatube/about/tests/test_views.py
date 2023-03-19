from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_exists_at_desired_location(self):
        """Проверка доступности адреса /page/about/."""
        urls_list = [
            'about:author',
            'about:tech',
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.guest_client.get(reverse(url))
                self.assertEqual(response.status_code, 200)

    def test_url_uses_correct_template(self):
        """Проверка шаблона для адреса /page/about/."""
        urls_dict = {
            'about:author': 'about/author.html',
            'about:tech': 'about/tech.html',
        }
        for url, expected in urls_dict.items():
            with self.subTest(url=url):
                response = self.guest_client.get(reverse(url))
                self.assertTemplateUsed(response, expected)