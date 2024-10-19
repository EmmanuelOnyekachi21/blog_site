from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse

# Creating my custom manager.
class PublishedManager(models.Manager):
    """My custom manager"""
    def get_queryset(self):
        """
        modify the default queryset 2 automatically filter for published posts
        """
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

# Create your models here.
class Post(models.Model):
    """Description of each blogpost"""
    class Status(models.TextChoices):
        """Manages the status of our blog posts."""
        DRAFT = 'DF', 'DRAFT'
        PUBLISHED = 'PB', 'Published'

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    # ForeignKey to the user model specified in settings
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT)

    # If you declare any managers for your model, 
    # but you want to keep the objects manager as well,
    # you have to add it explicitly to your model.
    objects = models.Manager()    # Default Manager
    published = PublishedManager() # My custom Manager

    class Meta:
        """Defines Metadata for the Post class"""
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """
        Returns the URL used to refer to an instance of that model.
        For example, if you have a BlogPost model,
        get_absolute_url() would return the URL to view a specific blog post.
        """
        return reverse(
            'blog:post_detail',
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug
            ]
        )

class Comment(models.Model):
    """The comment model"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]
    
    def __str__(self):
        return f"Comment by {self.name} on {self.post}"