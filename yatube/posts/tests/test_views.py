import shutil
import time

from django import forms
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import User, Group, Post, Comment, Follow
from posts.tests.constants import (
    POSTS_PAGES_TEST_ATTRIBUTES,
    TEST_AUTHOR,
    TEST_POST,
    TEST_GROUP,
    TEST_COMMENT,
    TEST_UPLOADED,
    TEMP_MEDIA_ROOT
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pages_attribs = POSTS_PAGES_TEST_ATTRIBUTES
        cls.image_folder = Post.image.field.upload_to

        cls.user_author = User.objects.create_user(
            username=TEST_AUTHOR['username']
        )
        cls.user_author_2 = User.objects.create_user(username='SecondAuthor')

        cls.group_1 = Group.objects.create(
            title=TEST_GROUP['title'],
            slug=TEST_GROUP['slug'],
            description=TEST_GROUP['description']
        )
        cls.group_2 = Group.objects.create(
            title=(TEST_GROUP['title'] + ' 2'),
            slug=(TEST_GROUP['slug'] + '_2'),
            description=(TEST_GROUP['description'] + ' 2')
        )

        cls.post_1 = Post.objects.create(
            author=cls.user_author,
            text=TEST_POST['text'],
            group=cls.group_1
        )
        time.sleep(1)
        cls.post_2 = Post.objects.create(
            author=cls.user_author,
            text=(TEST_POST['text'] + ' 2'),
            group=None
        )
        time.sleep(1)
        cls.post_3 = Post.objects.create(
            author=cls.user_author_2,
            text=(TEST_POST['text'] + ' 3'),
            group=cls.group_2
        )
        time.sleep(1)
        # Пост с картинкой. Этот пост будет первым на страницах.
        # На нём проверяем post_detail и post_edit.
        cls.post_4 = Post.objects.create(
            author=cls.user_author,
            text=(TEST_POST['text'] + ' 4'),
            group=cls.group_1,
            image=TEST_UPLOADED
        )

        cls.comment_1 = Comment.objects.create(
            author=cls.user_author,
            post=cls.post_4,
            text=TEST_COMMENT['text']
        )

        cls.post_4_id = Post.objects.get(
            text=TEST_POST['text'] + ' 4'
        ).id
        cls.pages_attribs['post_detail'] = {
            'reversed_name': reverse(
                'posts:post_detail', kwargs={'post_id': cls.post_4_id}
            ),
            'template': 'posts/post_detail.html'
        }
        cls.pages_attribs['post_edit'] = {
            'reversed_name': reverse(
                'posts:post_edit', kwargs={'post_id': cls.post_4_id}
            ),
            'template': 'posts/create_post.html'
        }
        cls.pages_attribs['add_comment'] = {
            'reversed_name': reverse(
                'posts:add_comment', kwargs={'post_id': cls.post_4_id}
            )
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user_author)
        self.author_2_client = Client()
        self.author_2_client.force_login(self.user_author_2)

    def test_pages_use_correct_templates(self):
        """URL names correspond to templates."""
        for page_name, page_attributes in self.pages_attribs.items():
            with self.subTest(page_name=page_name):
                reversed_name = page_attributes.get('reversed_name')
                if reversed_name:
                    response = self.author_client.get(
                        page_attributes['reversed_name']
                    )
                    template = page_attributes.get('template')
                    if template:
                        self.assertTemplateUsed(response, template)

    # Testing Index page
    def test_index_page_shows_correct_context(self):
        """Index page shows correct context. (Test_DB has 4 posts)."""
        response = self.author_client.get(
            self.pages_attribs['index']['reversed_name']
        )
        first_post_on_page = response.context['page_obj'][0]
        self.assertEqual(first_post_on_page.text, 'Тестовый пост 4')
        self.assertEqual(first_post_on_page.group, self.group_1)
        self.assertEqual(first_post_on_page.author, self.user_author)
        self.assertEqual(
            first_post_on_page.image, self.image_folder + TEST_UPLOADED.name
        )

        third_post_on_page = response.context['page_obj'][2]
        self.assertEqual(third_post_on_page.group, None)

        self.assertEqual(len(response.context['page_obj']), 4)

    # Testing Group_list page
    def test_group_list_page_shows_correct_context(self):
        """Group_list page shows correct context. (Group_1 has 2 posts)"""
        response = self.author_client.get(
            self.pages_attribs['group_list']['reversed_name']
        )
        first_post_on_page = response.context['page_obj'][0]
        self.assertEqual(
            first_post_on_page.text, 'Тестовый пост 4',
            'Неправильное содержание/порядок постов на странице group_list.'
        )
        self.assertEqual(
            first_post_on_page.image, self.image_folder + TEST_UPLOADED.name,
            'Картинка из поста не передается на страницу group_list.'
        )
        self.assertEqual(
            len(response.context['page_obj']), 2,
            'Неверное количество постов на странице group_list.'
        )

    def test_group_list_page_shows_posts_of_correct_group(self):
        """
        Group_list page shows only posts of correct group.
        (Group_1 page shows only posts with group_1).
        """
        response = self.author_client.get(
            self.pages_attribs['group_list']['reversed_name']
        )
        posts_list = response.context['page_obj']
        num_posts = len(posts_list)
        for i in range(0, num_posts):
            with self.subTest(post_number=i):
                post_group = posts_list[i].group
                self.assertEqual(post_group, self.group_1)

    # Testing Profile page
    def test_profile_page_shows_correct_context(self):
        """Profle page shows correct context."""
        response = self.author_client.get(
            self.pages_attribs['profile']['reversed_name']
        )
        first_post_on_page = response.context['page_obj'][0]
        self.assertEqual(
            first_post_on_page.text, 'Тестовый пост 4',
            'Неправильное содержание или порядок постов на странице profile.'
        )
        self.assertEqual(
            first_post_on_page.image, self.image_folder + TEST_UPLOADED.name,
            'Картинка из поста не передается на страницу profile.'
        )
        self.assertEqual(
            len(response.context['page_obj']), 3,
            'Неверное количество постов на странице profile.'
        )

    def test_profile_page_shows_posts_of_correct_author(self):
        """Profile page shows only posts of chosen author."""
        response = self.author_client.get(
            self.pages_attribs['profile']['reversed_name']
        )
        post_list = response.context['page_obj']
        num_posts = len(post_list)
        for i in range(0, num_posts):
            with self.subTest(post_number=i):
                post_author = post_list[i].author
                self.assertEqual(post_author, self.user_author)

    # Testing Create_post and Post_edit pages
    def test_create_and_edit_post_pages_correct_form_field_types(self):
        """Create_post and Post_edit pages show correct form field types."""
        pages = [
            'create_post',
            'post_edit'
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for page_name in pages:
            with self.subTest(page_name=page_name):
                response = self.author_client.get(
                    self.pages_attribs[page_name]['reversed_name']
                )
                for field, expected_type in form_fields.items():
                    with self.subTest(field=field):
                        self.assertIsInstance(
                            response.context.get('form').fields[field],
                            expected_type
                        )

    def test_post_edit_page_shows_correct_context(self):
        """Post_edit page shows correct context. (Testing on post_4)."""
        response = self.author_client.get(
            self.pages_attribs['post_edit']['reversed_name']
        )
        form_fields_filled = {
            'text': self.post_4.text,
            'group': self.post_4.group.id
        }
        for field_name, expected_value in form_fields_filled.items():
            with self.subTest(field_name=field_name):
                self.assertEqual(
                    response.context.get('form')[field_name].value(),
                    expected_value
                )

    # Testing Post_detail page and Add_comment function
    def test_post_detail_page_shows_correct_context(self):
        """Post_detail page shows correct context. (Testing on post_4)."""
        response = self.author_client.get(
            self.pages_attribs['post_detail']['reversed_name']
        )
        self.assertEqual(
            response.context.get('post').id,
            self.post_4_id,
            'Страница post_detail показывает неверный пост.'
        )
        self.assertEqual(
            response.context.get('post').image,
            self.image_folder + TEST_UPLOADED.name,
            'Страница post_detail показывает неверную картинкку.'
        )
        first_comment = response.context.get('comments')[0]
        self.assertEqual(
            first_comment.text,
            TEST_COMMENT['text'],
            'Страница post_detail показывает неверный комментарий.'
        )

    def test_added_comment_shows_on_post_detail_page(self):
        new_comment_text = 'Ещё один комментарий.'
        data_form = {
            'text': new_comment_text,
            'post': self.post_4
        }
        response = self.author_2_client.post(
            self.pages_attribs['add_comment']['reversed_name'],
            data=data_form,
            follow=True
        )
        new_comment = Comment.objects.get(
            post=self.post_4,
            text=new_comment_text,
            author=self.user_author_2
        )
        comments_on_page = response.context.get('comments')
        self.assertTrue(new_comment in comments_on_page)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pages_attribs = POSTS_PAGES_TEST_ATTRIBUTES

        cls.user_author = User.objects.create_user(
            username=TEST_AUTHOR['username']
        )
        cls.user_2 = User.objects.create_user(
            username='User 2'
        )
        cls.user_3 = User.objects.create_user(
            username='User 3'
        )

        cls.follow_1_2 = Follow.objects.create(
            user=cls.user_author,
            author=cls.user_2
        )

    def setUp(self):
        self.guest_client = Client()
        self.user_author_client = Client()
        self.user_author_client.force_login(self.user_author)
        self.user_2_client = Client()
        self.user_2_client.force_login(self.user_2)

    def test_authorized_user_can_follow_unfollow(self):
        """
        Test that authorized user can subscribe
        and unsubscribe from other users.
        """
        self.user_author_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_3.username}
        ))
        self.assertTrue(Follow.objects.filter(
            user=self.user_author,
            author=self.user_3
        ).exists())

        self.user_author_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_3.username}
        ))
        self.assertFalse(Follow.objects.filter(
            user=self.user_author,
            author=self.user_3
        ).exists())

    def test_follow_index_page_shows_correct_content(self):
        new_post_user_2 = Post.objects.create(
            text='Новый пост автора 2',
            author=self.user_2
        )
        response = self.user_author_client.get(
            self.pages_attribs['follow_index']['reversed_name']
        )
        try:
            first_post_on_page_id = response.context['page_obj'][0].id
        except IndexError:
            first_post_on_page_id = None
        self.assertEqual(new_post_user_2.id, first_post_on_page_id)

        response = self.user_2_client.get(
            self.pages_attribs['follow_index']['reversed_name']
        )
        try:
            first_post_on_page_id = response.context['page_obj'][0].id
        except IndexError:
            first_post_on_page_id = None
        self.assertNotEqual(new_post_user_2.id, first_post_on_page_id)


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pages_attribs = POSTS_PAGES_TEST_ATTRIBUTES

        cls.user_author = User.objects.create_user(
            username=TEST_AUTHOR['username']
        )
        cls.group_1 = Group.objects.create(
            title=TEST_GROUP['title'],
            slug=TEST_GROUP['slug'],
            description=TEST_GROUP['description']
        )

        cls.post_num = 15
        posts_list = []
        for i in range(1, cls.post_num + 1):
            post = Post(
                author=cls.user_author,
                text=(TEST_POST['text'] + str(i)),
                group=cls.group_1
            )
            posts_list.append(post)
        Post.objects.bulk_create(posts_list)

        cls.pages_to_be_tested = [
            'index',
            'group_list',
            'profile'
        ]

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user_author)

    def test_pages_contain_correct_number_of_records(self):
        """
        First page should contain 10 posts.
        Second page should contain 5 posts.
        """
        for page_name in self.pages_to_be_tested:
            with self.subTest(page_name=page_name):
                response = self.author_client.get(
                    self.pages_attribs[page_name]['reversed_name']
                )
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.author_client.get(
                    self.pages_attribs[page_name]['reversed_name'] + '?page=2'
                )
                self.assertEqual(len(response.context['page_obj']), 5)


class CashTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pages_attribs = POSTS_PAGES_TEST_ATTRIBUTES

        cls.user_author = User.objects.create_user(
            username=TEST_AUTHOR['username']
        )
        cls.group_1 = Group.objects.create(
            title=TEST_GROUP['title'],
            slug=TEST_GROUP['slug'],
            description=TEST_GROUP['description']
        )
        cls.post_1 = Post.objects.create(
            author=cls.user_author,
            text=TEST_POST['text'],
            group=cls.group_1
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.user_author)

    def test_index_page_cash(self):
        """Index_page cashes post list."""
        response_1 = self.author_client.get(
            self.pages_attribs['index']['reversed_name']
        )
        content_1 = response_1.content
        first_post_1 = response_1.context['page_obj'][0]

        Post.objects.get(id=first_post_1.id).delete()

        response_2 = self.author_client.get(
            self.pages_attribs['index']['reversed_name']
        )
        content_2 = response_2.content

        self.assertEqual(
            content_1, content_2,
            'Кэширование index page не работает спустя <1 сек.'
        )

        cache.clear()
        response_3 = self.author_client.get(
            self.pages_attribs['index']['reversed_name']
        )
        content_3 = response_3.content

        self.assertNotEqual(
            content_1, content_3,
            'Кэш index page не обновился после очистки кэша.')
