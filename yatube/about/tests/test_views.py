from http import HTTPStatus

from django.test import TestCase, Client

from .constants import STATIC_URLS_VIEWS


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_accessible_by_name(self):
        for page_name, page_attributes in STATIC_URLS_VIEWS.items():
            with self.subTest(page_name=page_name):
                response = self.guest_client.get(
                    page_attributes['reversed_name']
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_use_correct_templates(self):
        for page_name, page_attributes in STATIC_URLS_VIEWS.items():
            with self.subTest(page_name=page_name):
                response = self.guest_client.get(
                    page_attributes['reversed_name']
                )
                template = page_attributes['template']
                self.assertTemplateUsed(response, template)
