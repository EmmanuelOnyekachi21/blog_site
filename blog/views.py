from django.shortcuts import render, get_object_or_404
from .models import Post
from django.http import Http404
# Create your views here.

def post_list(request):
    """Sends Published list as response."""
    posts = Post.published.all()
    context = {'posts': posts}
    return render(request, 'blog/post/list.html', context)

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