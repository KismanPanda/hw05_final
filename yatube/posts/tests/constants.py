import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse

POSTS_PAGES_TEST_ATTRIBUTES = {
    'index': {
        'page_url': '/',
        'reversed_name': reverse('posts:index'),
        'template': 'posts/index.html'
    },
    'group_list': {
        'page_url': '/group/test_slug/',
        'reversed_name': reverse(
            'posts:group_list', kwargs={'slug': 'test_slug'}
        ),
        'template': 'posts/group_list.html'
    },
    'profile': {
        'page_url': '/profile/Author/',
        'reversed_name': reverse(
            'posts:profile', kwargs={'username': 'Author'}
        ),
        'template': 'posts/profile.html'
    },
    'create_post': {
        'page_url': '/create/',
        'reversed_name': reverse('posts:create_post'),
        'template': 'posts/create_post.html'
    },
    'follow_index': {
        'page_url': '/follow/',
        'reversed_name': reverse('posts:follow_index'),
        'template': 'posts/follow.html'
    },
    'profile_follow': {
        'page_url': '/profile/Author/follow/'
    },
    'profile_unfollow': {
        'page_url': '/profile/Author/unfollow/'
    },
}

LOGIN_PAGE_URL = '/auth/login/'

TEST_POST = {
    'text': 'Тестовый пост'
}

TEST_GROUP = {
    'title': 'Тестовая группа',
    'slug': 'test_slug',
    'description': 'Тестовое описание'
}

TEST_AUTHOR = {
    'username': 'Author'
}

TEST_COMMENT = {
    'text': 'Тестовый комментарий'
}

TEST_SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
TEST_UPLOADED = SimpleUploadedFile(
    name='small.gif',
    content=TEST_SMALL_GIF,
    content_type='image/gif'
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
