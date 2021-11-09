from django.test import TestCase

from posts.models import Group, Post, User
from posts.tests.constants import TEST_AUTHOR, TEST_GROUP


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=TEST_AUTHOR['username']
        )
        cls.group = Group.objects.create(
            title=TEST_GROUP['title'],
            slug=TEST_GROUP['slug'],
            description=TEST_GROUP['description']
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост про Яблоки на снегу...',
            group=cls.group
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        expected_names = {
            post: 'Тестовый пост п',
            group: TEST_GROUP['title']
        }
        for model, name in expected_names.items():
            with self.subTest(model=model):
                self.assertEqual(
                    str(model), name,
                    f'В модели {model} некорректно работает метод __str__.'
                )

    def test_post_verbose_names(self):
        post = PostModelTest.post
        expected_verbose_names = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_text in expected_verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_text,
                    'В модели Post некорректные verbose_name.'
                )

    def test_post_help_text(self):
        post = PostModelTest.post
        expected_help_text = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_text in expected_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_text,
                    'В модели Post некорректные help_text.'
                )
