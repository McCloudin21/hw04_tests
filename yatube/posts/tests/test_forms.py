import shutil
import tempfile

from posts.forms import PostForm
from ..models import Post, Group
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='Test')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.group = Group.objects.create(
            title='test-group',
            slug='first',
            description='test-description'
        )
        self.posts = Post.objects.create(
            text='Тестовый текст',
            group=self.group,
            author=self.user
        )

    def test_create_form(self):
        """Валидная форма создает запись в post."""
        posts_count = Post.objects.count()
        test_text = ('Test_text')
        form_data = {
            'text': test_text,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
        )
        self.assertRedirects(response, reverse('posts:profile',
                                               args=[self.posts.author]))
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertTrue(
            Post.objects.filter(
                text=test_text,
                group=self.group.id,
            ).exists()
        )


class PostEditFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='Test')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def setUp(self):
        self.group = Group.objects.create(
            title='test-group',
            slug='first',
            description='test-description'
        )
        self.posts = Post.objects.create(
            text='Тестовый текст',
            group=self.group,
            author=self.user
        )

    def test_edit_form(self):
        """Валидная форма редактирует запись в post."""
        test_text = ('Test_text2')
        form_data = {
            'text': test_text,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.posts.id]),
            data=form_data,
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                                               args=[self.posts.id]))
        self.assertTrue(
            Post.objects.filter(
                text=test_text,
            ).exists()
        )
