import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms

from posts.models import Post, Group, Follow

User = get_user_model()


class StaticViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username='TestUser')
        cls.user2 = User.objects.create(username='TestFollowUser')
        cls.group = Group.objects.create(
            title='testGroup',
            slug='testSlug',
            description='lalala lalala'
        )
        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
            )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.image,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='lorem lorem lorem',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )
        cls.post_follow_user = Post.objects.create(
            text='follow test',
            author=cls.user2,
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticViewTests.user)

    def test_html_templates_name(self):
        html_templates_name = {
            'index.html': reverse('index'),
            'group.html': reverse('group_posts', kwargs={'slug': 'testSlug'}),
            'new_post.html': reverse('new_post'),
            'profile.html': reverse('profile', kwargs={'username': 'TestUser'}),
            'post.html': reverse('profile', kwargs={'username': 'TestUser'}) + '1/',
            'new_post.html': reverse('profile', kwargs={'username': 'TestUser'}) + '1/edit/',
        }
        for template, url_name in html_templates_name.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url_name)
                self.assertTemplateUsed(response, template)

    def test_some_pages_correct_context(self):
        page_name_check_context = {
            'page': reverse('index'),
            'posts': reverse('group_posts', kwargs={'slug': 'testSlug'}),
            'page': reverse('profile', kwargs={'username': 'TestUser'}),
        }
        for context_list, page_name in page_name_check_context.items():
            with self.subTest(page_name=page_name):
                response = self.authorized_client.get(page_name)
                page_post = response.context.get(context_list)[0]
                self.assertEqual(page_post.text, 'lorem lorem lorem')
                self.assertEqual(page_post.author, StaticViewTests.user)
                self.assertEqual(page_post.group, StaticViewTests.group)
                self.assertEqual(page_post.image, StaticViewTests.post.image)

    def test_new_post_page_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_posts_index(self):
        response1 = self.guest_client.get(reverse('index'))
        Post.objects.create(
            text='lorem lorem lorem',
            author=StaticViewTests.user,
        )
        response2 = self.guest_client.get(reverse('index'))
        self.assertEqual(str(response1.content), str(response2.content))

    def test_follow_another_user(self):
        self.authorized_client.get(reverse('profile_follow',
                                   kwargs={'username': 'TestFollowUser'}))
        follow_exist = Follow.objects.filter(
                   user=StaticViewTests.user,
                   author=StaticViewTests.user2).exists()
        self.assertEqual(True, follow_exist)

    def test_unfollow_another_user(self):
        response = self.authorized_client.get(
                   reverse('profile_follow',
                   kwargs={'username': 'TestFollowUser'})
        )
        response = self.authorized_client.get(
                   reverse('profile_unfollow',
                   kwargs={'username': 'TestFollowUser'})
        )
        follow_exist = Follow.objects.filter(
                       user=StaticViewTests.user,
                       author=StaticViewTests.user2).exists()
        self.assertEqual(False, follow_exist)

    def test_post_author_user_follow_exist_in_follow_page(self):
        response = self.authorized_client.get(
                   reverse('profile_follow',
                   kwargs={'username': 'TestFollowUser'})
                   )
        response = self.authorized_client.get(reverse('follow_index'))
        page_post = response.context.get('page')[0]
        self.assertEqual(page_post.text, 'follow test')
        self.assertEqual(page_post.author, StaticViewTests.user2)

    def test_post_author_user_not_follow_not_exist_in_follow_page(self):
        response = self.authorized_client.get(reverse('follow_index'))
        len_context = response.context.count('page')
        self.assertEqual(len_context, 0)
