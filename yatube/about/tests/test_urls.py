from http import HTTPStatus

from django.test import TestCase, Client

from .constants import STATIC_URLS_VIEWS


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exist_at_desired_location(self):
        for page_name, page_attributes in STATIC_URLS_VIEWS.items():
            with self.subTest(page_name=page_name):
                response = self.guest_client.get(page_attributes['page_url'])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        for page_name, page_attributes in STATIC_URLS_VIEWS.items():
            with self.subTest(page_name=page_name):
                response = self.guest_client.get(page_attributes['page_url'])
                template = page_attributes['template']
                self.assertTemplateUsed(response, template)
