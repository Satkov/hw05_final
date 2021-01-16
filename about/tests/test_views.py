from django.test import TestCase, Client
from django.urls import reverse


class StaticAuthorViewTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.html_templates_name = {
            reverse('about:author'): 'author.html',
            reverse('about:tech'): 'tech.html',
        }
    def test_html_templates_name(self):
        for url_name, template in self.html_templates_name.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url_name)
                self.assertTemplateUsed(response, template)

