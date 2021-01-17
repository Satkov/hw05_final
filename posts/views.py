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
          'paginator': paginator,}
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
    form = CommentForm
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
    if request.method == "POST"and form.is_valid():
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
    follow_list = []
    follow_list_id = Follow.objects.filter(user=request.user).in_bulk()
    # нагло украдено и работает супер медленно.
    # внизу файла прикреплю свою идею, которую не могу реализовать.
    # Извиняюсь, что закидываю вопросами!
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
          'paginator': paginator,}
    )

@login_required(login_url='/auth/login/')
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author or Follow.objects.filter(user=request.user, author=author).exists():
        return redirect(reverse('profile', kwargs={'username': username}))
    Follow.objects.create(user=request.user, author=author).save()
    return redirect(reverse('follow_index'))

@login_required(login_url='/auth/login/')
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author or not Follow.objects.filter(user=request.user, author=author).exists():
        return redirect(reverse('profile', kwargs={'username': username}))
    Follow.objects.filter(user=request.user, author=author).update(author=None)
    return redirect(reverse('follow_index'))


'''
Вряд ли этот вопрос решаем, но всё же.
Хочу добавить в модель Post строку со списком людей, которые подписаны на автора поста,
чтобы когда человек подписывается на автора, то у постов этого автора в строке users_follow_author добавлялся 
подписавшийся на него пользователь, и хотел сделать это через .update.

Однако, закономерно возникла проблема: если на автора подписывается другой пользователь, 
то он перезапишет свой username и сотрёт username предыдущего подписчика. 
Из-за этого я не могу использовать метод update.

Собственно вопрос: знаете ли вы способ, который был бы похож на append, 
чтобы он добавлял пользователя в список, который бы сохранялся в бд, 
и также чтобы была возможность удалить этого пользователя по имени?

Ну или любой другой способ, который позволит обновляться постам на странице follow
Меньше чем за 10-20 секунд¯\_(ツ)_/¯

#Models
class Post(models.Model):

	...

    users_follow_author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='followers',
    )

#views
@login_required(login_url='/auth/login/')
def profile_follow(request, username):
    ...
    #вот тут записываю инфу в модель Post при подписке на автора
    Post.objects.filter(author=author).update(user_follow_authors=request.user)

    #Вот так собирался делать при отписке
    Post.objects.filter(author=author).update(user_follow_authors=None)
'''