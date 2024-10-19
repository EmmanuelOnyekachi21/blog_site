from django.shortcuts import render, get_object_or_404
from .models import Post
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import send_mail

# Create your views here.

def post_list(request):
    """
    FBV: post_list view
    Sends Published list as response.
    """
    posts_list = Post.published.all()
    # Pagination with 3 posts per page
    paginator = Paginator(posts_list, 3)
    page_number = request.GET.get('page', 1)
    
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        # If page number is out of range, get last page of result
        posts = paginator.page(paginator.num_pages)

    context = {'posts': posts}
    return render(request, 'blog/post/list.html', context)

class PostListView(ListView):
    """CBV: post_list view"""
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

# def post_detail(request, id):
#     """Displays a single post"""
#     try:
#         post = Post.published.get(id=id)
#     except Post.DoesNotExist:
#         raise Http404("No post found.")
#     return render(request, 'blog/post/detail.html', {'post': post})
def post_detail(request, year, month, day, post):
    """Using get_object_or_404 instead of the try/except in the above code."""
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day
    )
    return render(request, 'blog/post/detail.html', {'post': post})

def post_share(request, post_id):
    """View function for sharing a post.

    Args:
        request (_type_): _description_
        post_id (_type_): _description_
    """
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    
    if request == 'GET':
        form = EmailPostForm()
        
    else:
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommends you read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}\'s comments: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']],
            )
            sent = True
    context = {'post': post, 'form': form, 'sent':sent}

    return render(request, 'blog/post/share.html', context)