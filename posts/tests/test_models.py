from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()

class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        cls.post = Post.objects.create(
            text='test text lalala lalala',
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='testGroup',
            slug='testSlug',
            description='lalala lalala'
        )
    def test_verbose_name_post(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'текст',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(post._meta.get_field(value).verbose_name, expected)

    def test_help_text_post(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Введите текст новой записи',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_verbose_name_group(self):
        group = PostModelTest.group
        field_verboses = {
            'title': 'название группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text_group(self):
        group = PostModelTest.group
        field_verboses = {
            'title': 'введите название группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_object_name_in_text_field_post(self):
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post)[:15])

    def test_object_name_in_title_field_group(self):
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
