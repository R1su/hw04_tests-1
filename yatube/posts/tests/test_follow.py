from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Post, Follow, Group


User = get_user_model()


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username='author'
        )
        cls.user_2 = User.objects.create_user(
            username='follower'
        )
        cls.follow = Follow.objects.create(
            author=cls.user,
            user=cls.user_2
        )
        # Создали первую группу
        cls.group_1 = Group.objects.create(
            title='Название группы для теста_1',
            slug='test-slug_1',
            description='Описание группы для теста_1'
        )
        # Создали вторую группу
        cls.group_2 = Group.objects.create(
            title='Название группы для теста_2',
            slug='test-slug_2',
            description='Описание группы для теста_2'
        )
        # Создали пост
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста для теста',
            group=cls.group_1,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Отлично',
            author=cls.user
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_follow_another_user(self):
        """Авторизованный пользователь,
        может подписываться на других пользователей
        """
        follow_count = Follow.objects.count()
        self.authorized_client.get(reverse('posts:profile_follow',
                                           kwargs={'username': self.user_2}))
        self.assertTrue(Follow.objects.filter(user=self.user,
                                              author=self.user_2).exists())
        self.assertEqual(Follow.objects.count(), follow_count + 1)

    def test_unfollow_another_user(self):
        """Авторизованный пользователь
        может удалять других пользователей из подписок
        """
        Follow.objects.create(user=self.user, author=self.user_2)
        follow_count = Follow.objects.count()
        self.assertTrue(Follow.objects.filter(user=self.user,
                                              author=self.user_2).exists())
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_2}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.user_2
            ).exists()
        )
        self.assertEqual(Follow.objects.count(), follow_count - 1)

    def test_new_post_follow(self):
        """ Новая запись пользователя будет в ленте у тех,
         кто на него подписан.
        """
        following = User.objects.create(username='following')
        Follow.objects.create(user=self.user, author=following)
        post = Post.objects.create(author=following, text=self.post.text)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'].object_list)

    def test_new_post_unfollow(self):
        """ Новая запись пользователя не будет видна у тех,
        кто не подписан на него.
        """
        self.client.logout()
        User.objects.create_user(
            username='somebody_temp',
            password='pass'
        )
        self.client.login(username='somebody_temp')
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(
            self.post.text,
            response.context['page_obj'].object_list
        )

    def test_nothing_changed_if_self_follow(self):
        """В БД ничего не меняется,
        когда юзер пытается подписаться сам на себя.
        """
        following = User.objects.create(username='following')
        Follow.objects.create(user=following, author=following)
        post = Post.objects.create(author=following, text=self.post.text)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'].object_list)

    def test_nothing_changed_if_double_follow(self):
        """В БД ничего не меняется, когда юзер пытается подписаться
        на кого-то второй раз.
        """
        Follow.objects.create(user=self.user, author=self.user_2)
        self.assertTrue(Follow.objects.filter(user=self.user,
                                              author=self.user_2).exists())
        Follow.objects.create(user=self.user, author=self.user_2)
        self.assertTrue(Follow.objects.filter(user=self.user,
                                              author=self.user_2).exists())

    def test_nothing_changed_if_unsubscribe_unfollower(self):
        """В БД ничего не меняется,
        когда юзер пытается отписаться без подписки.
        """
        follow_count = Follow.objects.count()
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user_2}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count)