from django import forms

from .models import Item


class BookmarkForm(forms.ModelForm):
    new_category = forms.CharField(required=False)
    new_tags = forms.CharField(required=False)

    class Meta:
        model = Item
        fields = ("url", "title", "category", "tags", "description")
