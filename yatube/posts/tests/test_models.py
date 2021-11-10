from django.test import TestCase

from posts.models import Comment, Follow, Group, Post, User
from posts.tests.constants import TEST_AUTHOR, TEST_COMMENT, TEST_GROUP


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=TEST_AUTHOR['username']
        )
        cls.user_2 = User.objects.create_user(
            username='SecondUser'
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
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_2,
            text=TEST_COMMENT['text']
        )
        cls.follow = Follow.objects.create(
            user=cls.user_2,
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        follow = PostModelTest.follow
        expected_names = {
            post: 'Тестовый пост п',
            group: TEST_GROUP['title'],
            comment: (
                f'Комментарий {comment.author.username}'
                f' к посту {comment.post.id}'
            ),
            follow: (
                f'Подписка {follow.user.username}'
                f' на автора {follow.author.username}'
            )
        }
        for model, name in expected_names.items():
            with self.subTest(model=model):
                self.assertEqual(
                    str(model), name,
                    f'В модели {model} некорректно работает метод __str__.'
                )

    # Протестировать в словаре имена для других моделей
    def test_models_verbose_names(self):
        post = PostModelTest.post
        group = PostModelTest.group
        comment = PostModelTest.comment
        follow = PostModelTest.follow
        expected_verbose_names = {
            post: {
                'text': 'Текст поста',
                'pub_date': 'Дата публикации',
                'author': 'Автор',
                'group': 'Группа',
            },
            group: {
                'title': 'Название группы',
                'slug': 'URL группы',
                'description': 'Описание группы',
            },
            comment: {
                'post': 'Пост',
                'author': 'Автор',
                'text': 'Текст комментария',
                'created': 'Дата и время комментария',
            },
            follow: {
                'user': 'Подписчик',
                'author': 'Подписан на',
            }
        }
        for model, verbose_names in expected_verbose_names.items():
            with self.subTest(model=model):
                for field, expected_text in verbose_names.items():
                    with self.subTest(field=field):
                        self.assertEqual(
                            model._meta.get_field(field).verbose_name,
                            expected_text,
                            f'В модели {model} некорректные verbose_name.'
                        )

    def test_models_help_text(self):
        post = PostModelTest.post
        comment = PostModelTest.comment
        expected_help_texts = {
            post: {
                'text': 'Введите текст поста',
                'group': 'Выберите группу',
            },
            comment: {
                'text': 'Введите текст комментария',
            }
        }
        for model, help_texts in expected_help_texts.items():
            with self.subTest(model=model):
                for field, expected_text in help_texts.items():
                    with self.subTest(field=field):
                        self.assertEqual(
                            model._meta.get_field(field).help_text,
                            expected_text,
                            f'В модели {model} некорректные help_text.'
                        )
