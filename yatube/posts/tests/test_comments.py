from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Post, User

TEST_TEXT = 'Редактируемый текст'


class CommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='comment')
        cls.post = Post.objects.create(
            text=TEST_TEXT,
            author=cls.test_user,
            pk=101
        )
        cls.comment_url = reverse('posts:add_comment', args=[cls.post.pk])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)

    def test_authorized_client_comment(self):
        """Авторизированный пользователь может
        комментировать и создается новый комментарий."""
        count_comments = Comment.objects.count()
        self.authorized_client.post(CommentTests.comment_url,
                                    data={'text': TEST_TEXT}
                                    )
        comment = Comment.objects.filter(post=CommentTests.post).last()
        self.assertEqual(comment.author, CommentTests.test_user)
        self.assertEqual(comment.text, TEST_TEXT)
        self.assertEqual(comment.post, CommentTests.post)
        self.assertEqual(count_comments + 1, Comment.objects.count())

    def test_guest_client_comment_redirect_login(self):
        """Не авторизированный пользователь не может комментировать."""
        text_comment = 'Тестовый комментарий'
        count_comments = Comment.objects.count()
        self.guest_client.post(CommentTests.comment_url,
                               data={'text': text_comment}
                               )
        self.assertEqual(count_comments, Comment.objects.count())