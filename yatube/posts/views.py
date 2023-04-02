from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User
from .forms import PostForm


POSTS_ON_PAGE = 10


def index(request):
    post_list = Post.objects.select_related('author').all()
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.posts.all()
    paginator = Paginator(posts_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts_list,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_count = author.posts.count()
    title = f'Профиль пользователя {author}'

    paginator = Paginator(author.posts.all(), POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'author': author,
        'title': title,
        'posts_count': posts_count,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.all().count()
    context = {
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    title = 'Новый пост'
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    return render(request, 'posts/post_create.html', context={'form': form,
                                                              'title': title})


@login_required
def post_edit(request, post_id):
    is_form_edit = True
    post = get_object_or_404(Post, id=post_id)
    title = 'Редактирование поста'
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post_id)

    return render(request, 'posts/post_create.html',
                  context={'form': form,
                           'is_form_edit': is_form_edit,
                           'post': post,
                           'title': title})
