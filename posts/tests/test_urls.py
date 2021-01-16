from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()

class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.user2 = User.objects.create(username='TestEditUser')
        cls.group = Group.objects.create(
            title='testGroup',
            slug='testSlug',
            description='lalala lalala'
        )
        post_counter = 0
        while post_counter <= 12:
            post_counter += 1
            Post.objects.create(
                text=f'post № {post_counter}',
                author=cls.user,
            )
        Post.objects.create(
            text='test edit',
            author=StaticURLTests.user2,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.user)

    def test_urls_avalible_for_guest(self):
        urls_avalible_for_guest = [
            '/',
            '/group/testSlug/',
            '/TestUser/',
            '/TestUser/1/',
        ]
        for url in urls_avalible_for_guest:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_unavalible_for_guest(self):
        urls_unavalible_for_guest = [
            '/new',
        ]
        for url in urls_unavalible_for_guest:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(response, '/auth/login/?next=/new')

    def test_urls_with_auth_user(self):
        urls_with_auth_user = [
            '/',
            '/group/testSlug/',
            '/new',
            '/TestUser/',
            '/TestUser/1/',
            '/TestUser/1/edit/',
        ]
        for url in urls_with_auth_user:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_templates(self):
        templates_url_names = {
            'index.html': '/',
            'group.html': '/group/testSlug/',
            'new_post.html': '/new',
            'profile.html': '/TestUser/',
            'new_post.html': '/TestUser/1/edit/',
            'post.html': '/TestUser/1/'
        }
        for templates, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, templates)

    def test_status_url_pages(self):
        status_url_checking = {
            '/': 200,
            '/TestUser/': 200,
            '/group/testSlug/': 200,
            '/new': 200,
            '/TestUser/1/': 200,
            '/TestUser/1/edit/': 200,
            '/?page=2': 200,
            '/auth/password_change/': 200,
            '/auth/login/': 200,
            '/auth/signup/': 200,
            '/auth/logout/': 200,
            '/incorrectUser/18273/': 404,
        }
        for url, expect in status_url_checking.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, expect)

    def test_edit_redirect_for_auth_not_author(self):
        check_redirect_edit = {
            f'/{self.user2.username}/14/edit/': '/TestEditUser/14/',
        }
        for edit_url, refirect_url in check_redirect_edit.items():
            response = self.authorized_client.get(edit_url,)
            self.assertRedirects(response, refirect_url)
