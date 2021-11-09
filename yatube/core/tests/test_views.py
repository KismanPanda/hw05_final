from http import HTTPStatus

from django.test import TestCase, Client

from core.tests.constants import CORE_PAGES_TEST_ATTRIBUTES


class CoreViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pages_attribs = CORE_PAGES_TEST_ATTRIBUTES

    def setUp(self):
        self.client = Client()

    def test_error_page(self):
        request = self.client.get(self.pages_attribs['404']['page_url'])
        self.assertEqual(request.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(request, self.pages_attribs['404']['template'])
