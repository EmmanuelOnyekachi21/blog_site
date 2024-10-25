"""
Creating forms with django
"""

from django import forms

from .models import Comment

class EmailPostForm(forms.Form):
    """Creating a form for user

    Args:
        forms (_type_): _description_
    """
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(
        required=False,
        widget=forms.Textarea
    )

class CommentForm(forms.ModelForm):
    """
    form to let users comment on blog posts
    """
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']


class SearchForm(forms.Form):
    query = forms.CharField()