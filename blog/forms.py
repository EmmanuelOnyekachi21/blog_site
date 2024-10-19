"""
Creating forms with django
"""

from django import forms

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