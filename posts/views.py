from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.urls import reverse

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.select_related('group')
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
    if request.user == post.author:
        if request.method == "POST":
            form = PostForm(request.POST, files=request.FILES or None, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.save()
                return redirect(reverse('post', kwargs={'username': username,
                                                        'post_id': post_id}))
        else:
            form = PostForm(instance=post)
            return render(request, 'new_post.html', {'form': form,
                                                     'post': post,
                                                     'is_edit': True})
    return redirect(reverse('post', kwargs={'username': username,
                                            'post_id': post_id}))


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        if Follow.objects.filter(user=request.user, author=author).exists():
            following = True
    context = {
        'page': page,
        'author': author,
        'post_count': paginator.count,
        'paginator': paginator,
        'following': following,
    }
    return render(
        request,
        'profile.html',
        context)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    all_posts_count = Post.objects.filter(author=author).select_related('author').count()
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post)
    context = {
        'author': author,
        'post': post,
        'posts_count': all_posts_count,
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
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST" and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect(reverse('post', kwargs={'username': username,
                                                'post_id': post_id}))

    return redirect(reverse('post', kwargs={'username': username,
                                            'post_id': post_id}))


@login_required(login_url='/auth/login/')
def follow_index(request):
    # украдено
    follow_list = []
    follow_list_id = Follow.objects.filter(user=request.user).in_bulk()
    for i in follow_list_id:
        follow_list.append(follow_list_id[i].author)
    post_list = Post.objects.filter(author__in=follow_list)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
         request,
         'follow.html',
         {'page': page,
          'paginator': paginator}
    )
'''
Вопрос: есть способ помимо того, что я похилит из слака, чтобы реализовать показ постов?
Очень хотелось сделать фильтрацию модели пост без всяких циклов с author id, но мои попытки
добавить дополнительную колонку в модель Post не увенчались успехом.
'''


@login_required(login_url='/auth/login/')
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author or Follow.objects.filter(
                                 user=request.user, author=author).exists():
        return redirect(reverse('profile', kwargs={'username': username}))
    Follow.objects.create(user=request.user, author=author).save()
    return redirect(reverse('follow_index'))


@login_required(login_url='/auth/login/')
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author or not Follow.objects.filter(
                                     user=request.user, author=author).exists():
        return redirect(reverse('profile', kwargs={'username': username}))
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect(reverse('follow_index'))
