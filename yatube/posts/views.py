from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
# from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import PostForm, CommentForm
from .models import Group, Post, Follow
from yatube.settings import NUM_POSTS_ON_PAGE

User = get_user_model()


@login_required
def create_post(request):
    """Creates a new post. Only for authorized users."""
    template = 'posts/create_post.html'
    post = Post()
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        username = request.user.username
        author = User.objects.get(username=username)
        form.instance.author = author
        form.save()
        return redirect(
            reverse('posts:profile', args=[username])
        )
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    """Editing an existing post. Only for the author."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect(reverse('posts:post_detail', args=[post_id]))

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        return redirect(reverse('posts:post_detail', args=[post_id]))

    context = {
        'form': form,
        'is_edit': True,
        'post_id': post_id
    }
    return render(request, template, context)


def index(request):
    """Main page."""
    template = 'posts/index.html'
    post_list = Post.objects.all()
    # post_list = cache.get('index_page')
    # if post_list is None:
    #     post_list = Post.objects.all()
    #     cache.set('index_page', post_list, timeout=20)
    paginator = Paginator(post_list, NUM_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'index': True
    }
    return render(request, template, context)


@login_required
def follow_index(request):
    """Posts list of authors the user is following."""
    template = 'posts/follow.html'
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, NUM_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'follow': True
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Posts by group."""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, NUM_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """User profile."""
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    user = request.user
    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(
            author=author,
            user=user
        ).exists():
            following = True
    paginator = Paginator(author_posts, NUM_POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Add subscription to the post author."""
    author = get_object_or_404(User, username=username)
    user = request.user
    if not Follow.objects.filter(
        author=author,
        user=user
    ).exists() and user != author:
        new_follow = Follow(author=author, user=user)
        new_follow.save()
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Delete subscription to author from DB."""
    author = get_object_or_404(User, username=username)
    user = request.user
    try:
        follow = Follow.objects.get(
            author=author,
            user=user
        )
    except ObjectDoesNotExist:
        follow = None
    if follow:
        follow.delete()
        return redirect('posts:profile', username=username)
    return redirect('posts:profile', username=username)


def post_detail(request, post_id):
    """Post details."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    comment_form = CommentForm()
    title = 'Пост ' + post.__str__()
    context = {
        'title': title,
        'post': post,
        'form': comment_form
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
