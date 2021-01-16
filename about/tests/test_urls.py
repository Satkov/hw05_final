from django.test import TestCase, Client


class StaticAboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.urls_avalible_for_guest = [
            '/about/author/',
            '/about/tech/'
        ]
        self.templates_url_names = {
            'author.html': '/about/author/',
            'tech.html': '/about/tech/',
        }
        self.status_url_checking = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }

    def test_urls_avalible_for_guest(self):
        for url in self.urls_avalible_for_guest:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_templates(self):
        for templates, url in self.templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, templates)

    def test_status_url_pages(self):
        for url, expect in self.status_url_checking.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, expect)
