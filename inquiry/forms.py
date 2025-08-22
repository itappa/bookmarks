from django import forms
from django.contrib.auth import get_user_model
from .models import Inquiry, Response, Knowledge, Category

User = get_user_model()


class InquiryForm(forms.ModelForm):
    """問い合わせフォーム"""
    class Meta:
        model = Inquiry
        fields = [
            'title', 'content', 'customer_name', 'customer_email', 
            'customer_phone', 'category', 'priority', 'tags'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'カンマ区切りで入力'}),
        }


class InquiryUpdateForm(forms.ModelForm):
    """問い合わせ更新フォーム"""
    class Meta:
        model = Inquiry
        fields = [
            'title', 'content', 'customer_name', 'customer_email', 
            'customer_phone', 'category', 'status', 'priority', 
            'assigned_to', 'tags'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'カンマ区切りで入力'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)


class ResponseForm(forms.ModelForm):
    """対応履歴フォーム"""
    class Meta:
        model = Response
        fields = ['content', 'is_internal']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class KnowledgeForm(forms.ModelForm):
    """ナレッジフォーム"""
    class Meta:
        model = Knowledge
        fields = ['title', 'content', 'category', 'is_public', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tags': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'カンマ区切りで入力'}),
        }


class InquirySearchForm(forms.Form):
    """問い合わせ検索フォーム"""
    q = forms.CharField(
        label='キーワード検索',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'タイトル、内容、顧客名で検索'})
    )
    status = forms.ChoiceField(
        label='ステータス',
        choices=[('', 'すべて')] + Inquiry.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    priority = forms.ChoiceField(
        label='優先度',
        choices=[('', 'すべて')] + Inquiry.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    category = forms.ModelChoiceField(
        label='カテゴリ',
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    assigned_to = forms.ModelChoiceField(
        label='担当者',
        queryset=User.objects.filter(is_staff=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        label='作成日（開始）',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        label='作成日（終了）',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )


class KnowledgeSearchForm(forms.Form):
    """ナレッジ検索フォーム"""
    q = forms.CharField(
        label='キーワード検索',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'タイトル、内容で検索'})
    )
    category = forms.ModelChoiceField(
        label='カテゴリ',
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    author = forms.ModelChoiceField(
        label='作成者',
        queryset=User.objects.filter(is_staff=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_public = forms.ChoiceField(
        label='公開状態',
        choices=[('', 'すべて'), ('True', '公開'), ('False', '非公開')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )