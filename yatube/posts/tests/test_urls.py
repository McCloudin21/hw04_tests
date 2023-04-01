from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.shortcuts import reverse
from django.test import (TestCase,
                         Client,
                         )

from ..models import (Post,
                      Group,
                      )


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Test-User')
        cls.group = Group.objects.create(
            title='test-group',
            slug='test-slug',
            description='test-description'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='author')
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_homepage(self):
        """Тестирование статуса страниц"""
        pages = {
            '/': 200,
            f'/group/{self.group.slug}/': 200,
            f'/profile/{self.user}/': 200,
            f'/posts/{self.post.id}/': 200,
        }
        for adress, status_code in pages.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                error_name: str = f'Ошибка: нет доступа до страницы {adress}'
                self.assertEqual(response.status_code,
                                 HTTPStatus.OK,
                                 error_name
                                 )

    def test_unexisting_page(self):
        """Тестирование несуществующей страницы"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_create_page(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_create_page_redirect(self):
        """Страница /create/ перенаправляет анонимного пользователя."""
        response = self.guest_client.get('/create/')
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/profile/{self.user}/': 'posts/profile.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                error_name: str = f'Ошибка: {adress} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_post_edit_page_authorized_uses_correct_template(self):
        """URL-адрес post/<post_id>/edit использует соответствующий шаблон"""
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/',
        )
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_post_create_page_authorized_uses_correct_template(self):
        """URL-адрес post/create/ использует соответствующий шаблон."""
        response = self.authorized_client.get('/create/'
                                              )
        self.assertTemplateUsed(response, 'posts/post_create.html')
