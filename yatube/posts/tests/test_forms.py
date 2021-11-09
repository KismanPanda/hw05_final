import shutil
from http import HTTPStatus

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User
from .constants import (
    POSTS_PAGES_TEST_ATTRIBUTES,
    TEST_AUTHOR,
    TEST_GROUP,
    TEST_POST,
    TEST_UPLOADED,
    TEMP_MEDIA_ROOT
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pages_attribs = POSTS_PAGES_TEST_ATTRIBUTES
        cls.image_folder = Post.image.field.upload_to

        cls.user_author = User.objects.create_user(
            username=TEST_AUTHOR['username']
        )
        cls.group = Group.objects.create(
            title=TEST_GROUP['title'],
            slug=TEST_GROUP['slug'],
            description=TEST_GROUP['description']
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user_author)

    def test_create_post(self):
        """
        Created post from Create-post page is in DB.
        If success, user is redirected to Profile page.
        """
        posts_count = Post.objects.count()
        form_data = {
            'text': TEST_POST['text'],
            'group': self.group.id,
            'image': TEST_UPLOADED
        }
        response = self.author_client.post(
            self.pages_attribs['create_post']['reversed_name'],
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(
            response, self.pages_attribs['profile']['reversed_name']
        )
        self.assertTrue(
            Post.objects.filter(
                text=TEST_POST['text'],
                group=self.group,
                image=self.image_folder + TEST_UPLOADED.name
            ).exists()
        )

    def test_cant_create_empty_post(self):
        """Post with empty test can not be created."""
        posts_count = Post.objects.count()
        form_data = {
            'text': '',
            'group': ''
        }
        response = self.author_client.post(
            self.pages_attribs['create_post']['reversed_name'],
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFormError(
            response,
            'form',
            'text',
            'Обязательное поле.'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostEditFormTests(TestCase):
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
        cls.post_1 = Post.objects.create(
            text=TEST_POST['text'],
            group=cls.group,
            author=cls.user_author
        )

        cls.post_1_id = Post.objects.get(
            text=TEST_POST['text']
        ).id
        cls.pages_attribs['post_detail'] = {
            'reversed_name': reverse(
                'posts:post_detail', kwargs={'post_id': cls.post_1_id}
            ),
            'template': 'posts/post_detail.html'
        }
        cls.pages_attribs['post_edit'] = {
            'reversed_name': reverse(
                'posts:post_edit', kwargs={'post_id': cls.post_1_id}
            ),
            'template': 'posts/create_post.html'
        }

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user_author)

    def test_edit_post(self):
        """
        Edited post is saved in DB.
        User is redirected to Post_detail page.
        """
        posts_count = Post.objects.count()
        new_text = 'Новый текст'
        form_data = {
            'text': new_text,
            'group': ''
        }
        response = self.author_client.post(
            self.pages_attribs['post_edit']['reversed_name'],
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.get(id=self.post_1_id).text, new_text)
        self.assertEqual(Post.objects.get(id=self.post_1_id).group, None)
        self.assertRedirects(
            response, self.pages_attribs['post_detail']['reversed_name']
        )


class CommentFormTests(TestCase):
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
        cls.post_1 = Post.objects.create(
            text=TEST_POST['text'],
            group=cls.group,
            author=cls.user_author
        )

        cls.post_1_id = Post.objects.get(
            text=TEST_POST['text']
        ).id
        cls.pages_attribs['post_detail'] = {
            'reversed_name': reverse(
                'posts:post_detail', kwargs={'post_id': cls.post_1_id}
            ),
            'template': 'posts/post_detail.html'
        }
        cls.pages_attribs['add_comment'] = {
            'reversed_name': reverse(
                'posts:add_comment', kwargs={'post_id': cls.post_1_id}
            )
        }

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user_author)

    def test_add_comment(self):
        """New comment is saved in DB. User is redirected to post_detail."""
        comments_count = Comment.objects.count()
        new_comment_text = 'Ещё один комментарий.'
        data_form = {
            'text': new_comment_text,
            'post': self.post_1
        }
        response = self.author_client.post(
            self.pages_attribs['add_comment']['reversed_name'],
            data=data_form,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertRedirects(
            response, self.pages_attribs['post_detail']['reversed_name']
        )
        self.assertTrue(
            Comment.objects.filter(
                text=new_comment_text,
                post=self.post_1,
                author=self.user_author
            ).exists()
        )
