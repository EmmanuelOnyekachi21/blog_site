from django.shortcuts import render, get_object_or_404
from .models import Post
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank
)
from .forms import SearchForm

# Create your views here.

def post_list(request, tag_slug=None):
    """
    FBV: post_list view
    Sends Published list as response.
    """
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
        
    # Pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        # If page number is out of range, get last page of result
        posts = paginator.page(paginator.num_pages)

    context = {'posts': posts, 'tag': tag}
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
    
    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for the user to comment
    form = CommentForm()
    
    # List of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post, 'comments': comments, 'form': form, 'similar_posts': similar_posts})

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

@require_POST
def post_comment(request, post_id):
    """
    View to allow user to comment on a post
    """
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None

    # A comment was posted
    form = CommentForm(data=request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save comment to database
        comment.save()
        
    context = {'post': post, 'form': form, 'comment': comment}

    return render(request, 'blog/post/comment.html', context)

def post_search(request):
    form = SearchForm()
    query = None
    results = []
    
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', 'body')
            search_query = SearchQuery(query)
            results = (
                Post.published.annotate(
                    search=search_vector,
                    rank = SearchRank(search_vector, search_query)
                ).filter(search=search_query).order_by('-rank')
            )
    context = {'form': form, 'query': query, 'results': results}
    return render(request, 'blog/post/search.html', context)