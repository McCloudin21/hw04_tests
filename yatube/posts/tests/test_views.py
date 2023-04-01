from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import (Post,
                          Group,
                          )

TEST_OF_POST: int = 13
User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        self.post = Post.objects.create(
            author=self.user,
            text='Текст',
            group=self.group
        )

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/post_create.html',
        }
        for adress, template in templates_pages_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                error_name: str = f'Ошибка: {adress} ожидал шаблон {template}'
                self.assertTemplateUsed(response, template, error_name)

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context.get('page_obj')[0]
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_author_0, 'StasBasov')
        self.assertEqual(post_text_0, 'Текст')
        self.assertEqual(post_group_0, 'Тестовая группа')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUp(self):
        self.user = User.objects.create_user(username='StasBasov')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(title='Тестовая группа',
                                          slug='test_group')
        bilk_post: list = []
        for i in range(TEST_OF_POST):
            bilk_post.append(Post(text=f'Тестовый текст {i}',
                                  group=self.group,
                                  author=self.user))
        Post.objects.bulk_create(bilk_post)

    def test_first_page_contains_ten_records(self):
        pages = {
            '/': 10,
            f'/group/{self.group.slug}/': 10,
            f'/profile/{self.user}/': 10,
        }
        for adress, expected_value in pages.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(len(response.context['page_obj']),
                                 expected_value)

    def test_second_page_contains_three_records(self):
        pages = {
            '/': 3,
            f'/group/{self.group.slug}/': 3,
            f'/profile/{self.user}/': 3,
        }
        for adress, expected_value in pages.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(str(adress) + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 expected_value)
