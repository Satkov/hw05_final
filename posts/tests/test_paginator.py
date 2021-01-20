from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post

User = get_user_model()

class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='TestUser')
        post_data = Post(text=f'post',
                         author=cls.user)
        objects = [post_data for i in range (0, 13)]
        Post.objects.bulk_create(objects)

    def test_first_page_containse_num_records(self):
        check_paginator_containse_num_records = [
            reverse('index'),
            reverse('profile', kwargs={'username': 'TestUser'}),
        ]
        for reverse_url in check_paginator_containse_num_records:
            response = self.client.get(reverse_url)
            response_2 = self.client.get(reverse_url + '?page=2')
            self.assertEqual(len(response.context.get('page').object_list), 10)
            self.assertEqual(len(response_2.context.get('page').object_list), 3)
