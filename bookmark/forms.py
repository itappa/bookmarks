from django import forms

from .models import Item


class BookmarkForm(forms.ModelForm):
    new_category = forms.CharField(required=False)
    new_tags = forms.CharField(required=False)
    
    # OGP関連の隠しフィールド
    og_title = forms.CharField(widget=forms.HiddenInput(), required=False)
    og_description = forms.CharField(widget=forms.HiddenInput(), required=False)
    og_image = forms.CharField(widget=forms.HiddenInput(), required=False)
    og_type = forms.CharField(widget=forms.HiddenInput(), required=False)
    og_site_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    favicon_url = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Item
        fields = ("url", "title", "category", "tags", "description")
