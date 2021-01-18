from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm


def is_subscribed(user, author):
    follow_status = Follow.objects.filter(user=user, author=author).exists()
    return follow_status


def index(request):
    post_list = Post.objects.select_related('group', 'author')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'index.html',
         {'page': page,
          'paginator': paginator}
     )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'page': page,
         'posts': posts,
         'paginator': paginator,
         'group': group})


@login_required(login_url='/auth/login/')
def new_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('index')

    return render(request, 'new_post.html', {'form': form})


@login_required(login_url='/auth/login/')
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=user, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if request.user == post.author:
        if request.method == "POST":
            if form.is_valid():
                post = form.save(commit=False)
                post.save()
                return redirect('post', username=username, post_id=post_id)
        else:
            return render(request, 'new_post.html', {'form': form,
                                                     'post': post,
                                                     'is_edit': True})
    return redirect('post', username=username, post_id=post_id)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    is_following = False
    if request.user.is_authenticated:
        is_following = is_subscribed(request.user, author)
    context = {
        'page': page,
        'author': author,
        'post_count': paginator.count,
        'paginator': paginator,
        'is_following': is_following,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    context = {
        'author': author,
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'post.html', context)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required(login_url='/auth/login/')
def add_comment(request, username, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, id=post_id, author=username)
    if request.method == "POST" and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('post', username=username, post_id=post_id)

    return redirect('post', username=username, post_id=post_id)


@login_required(login_url='/auth/login/')
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user) 
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'follow.html',
         {'page': page,
          'paginator': paginator}
    )


@login_required(login_url='/auth/login/')
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author or is_subscribed(request.user, author):
        return redirect('profile', username=username)
    Follow.objects.create(user=request.user, author=author)
    return redirect('follow_index')


@login_required(login_url='/auth/login/')
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author or not is_subscribed(request.user, author):
        return redirect('profile', username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('follow_index')
