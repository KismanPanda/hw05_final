from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import Group, Post, User
from posts.tests.constants import (
    LOGIN_PAGE_URL,
    POSTS_PAGES_TEST_ATTRIBUTES,
    TEST_AUTHOR,
    TEST_POST,
    TEST_GROUP
)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pages_attribs = POSTS_PAGES_TEST_ATTRIBUTES

        cls.user_author = User.objects.create_user(
            username=TEST_AUTHOR['username']
        )

        cls.group = Group.objects.create(
            title=TEST_GROUP['title'],
            slug=TEST_GROUP['slug'],
            description=TEST_GROUP['description']
        )

        cls.post = Post.objects.create(
            author=cls.user_author,
            text=TEST_POST['text'],
            group=cls.group
        )
        post_id = Post.objects.get(
            text=TEST_POST['text']
        ).id
        cls.pages_attribs['post_detail'] = {
            'page_url': f'/posts/{post_id}/',
            'template': 'posts/post_detail.html'
        }
        cls.pages_attribs['post_edit'] = {
            'page_url': f'/posts/{post_id}/edit/',
            'template': 'posts/create_post.html'
        }
        cls.pages_attribs['add_comment'] = {
            'page_url': f'/posts/{post_id}/comment/'
        }

    def setUp(self):
        self.guest_client = Client()
        self.user_second = User.objects.create_user(username='SecondUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_second)
        self.author_client = Client()
        self.author_client.force_login(self.user_author)

        self.users_access_rights = {
            'anonymous': {
                'client': self.guest_client,
                'page_list': [
                    'index',
                    'group_list',
                    'profile',
                    'post_detail'
                ]
            },
            'logged_in': {
                'client': self.authorized_client,
                'page_list': [
                    'follow_index',
                    'create_post'
                ]
            },
            'author': {
                'client': self.author_client,
                'page_list': [
                    'post_edit'
                ]
            }
        }

    def test_pages_urls_exist_at_desired_location(self):
        """User can access pages according to his permissions."""
        for user_type, user_attributes in (self.users_access_rights.items()):
            with self.subTest(user_type=user_type):
                for page_name in user_attributes['page_list']:
                    with self.subTest(page_name=page_name):
                        response = user_attributes['client'].get(
                            PostURLTests.pages_attribs[page_name]['page_url']
                        )
                        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_wrong_urls_not_found(self):
        wrong_urls = {
            'nonexistent_group_slug': '/group/wrong_slug/',
            'nonexistent__profile': '/profile/WrongUser/',
            'nonexistent_post_detail': '/posts/100/',
            'non_integer_post_id': '/posts/wrong/',
            'nonexistent_post_edit': '/posts/100/edit/'
        }
        for url_name, url_address in wrong_urls.items():
            with self.subTest(url_name=url_name):
                response = self.author_client.get(url_address)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_login_requiring_pages_redirect_anonymous(self):
        """Pages that require authorization redirect
        anonymous user to Login page."""
        page_list = [
            'create_post',
            'post_edit',
            'add_comment',
            'profile_follow',
            'profile_unfollow',
        ]
        for page_name in page_list:
            with self.subTest(page_name=page_name):
                page_url = PostURLTests.pages_attribs[page_name]['page_url']
                redirect_url = f'{LOGIN_PAGE_URL}?next={page_url}'
                response = self.guest_client.get(page_url, follow=True)
                self.assertRedirects(response, (redirect_url))

    def test_post_edit_url_redirects_authorized_not_author(self):
        """Post_edit page redirects not-author authorized
        user to Post_detail page."""
        post_edit_url = PostURLTests.pages_attribs['post_edit']['page_url']
        redirect_url = PostURLTests.pages_attribs['post_detail']['page_url']
        response = self.authorized_client.get(post_edit_url, follow=True)
        self.assertRedirects(response, (redirect_url))

    def test_post_urls_use_correct_templates(self):
        """Urls of posts app use correct templates."""
        for page_name, page_attributes in PostURLTests.pages_attribs.items():
            with self.subTest(page_name=page_name):
                response = self.author_client.get(page_attributes['page_url'])
                template = page_attributes.get('template')
                if template:
                    self.assertTemplateUsed(response, template)
