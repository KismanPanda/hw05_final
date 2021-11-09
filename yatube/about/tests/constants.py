from django.urls import reverse

STATIC_URLS_VIEWS = {
    'author': {
        'page_url': '/about/author/',
        'reversed_name': reverse('about:author'),
        'template': 'about/author.html'
    },
    'tech': {
        'page_url': '/about/tech/',
        'reversed_name': reverse('about:tech'),
        'template': 'about/tech.html'
    }
}
