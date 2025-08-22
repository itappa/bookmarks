from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey

User = get_user_model()


class Category(MPTTModel):
    """カテゴリ（階層構造）"""
    name = models.CharField('カテゴリ名', max_length=100)
    description = models.TextField('説明', blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'カテゴリ'
        verbose_name_plural = 'カテゴリ'

    def __str__(self):
        return self.name


class Inquiry(models.Model):
    """問い合わせ"""
    STATUS_CHOICES = [
        ('new', '新規'),
        ('in_progress', '対応中'),
        ('waiting', '保留'),
        ('resolved', '解決済み'),
        ('closed', '完了'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '緊急'),
    ]

    title = models.CharField('件名', max_length=200)
    content = models.TextField('内容')
    customer_name = models.CharField('顧客名', max_length=100)
    customer_email = models.EmailField('顧客メールアドレス')
    customer_phone = models.CharField('顧客電話番号', max_length=20, blank=True)
    
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField('優先度', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='カテゴリ')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='担当者')
    
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    resolved_at = models.DateTimeField('解決日時', null=True, blank=True)
    
    tags = models.CharField('タグ', max_length=500, blank=True, help_text='カンマ区切りで入力')
    
    class Meta:
        verbose_name = '問い合わせ'
        verbose_name_plural = '問い合わせ'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        super().save(*args, **kwargs)


class Response(models.Model):
    """対応履歴"""
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='responses', verbose_name='問い合わせ')
    responder = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='対応者')
    content = models.TextField('対応内容')
    is_internal = models.BooleanField('内部メモ', default=False, help_text='顧客には表示されない内部メモ')
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    
    class Meta:
        verbose_name = '対応履歴'
        verbose_name_plural = '対応履歴'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.inquiry.title} - {self.responder}"


class Knowledge(models.Model):
    """ナレッジベース"""
    title = models.CharField('タイトル', max_length=200)
    content = models.TextField('内容')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='カテゴリ')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作成者')
    
    is_public = models.BooleanField('公開', default=True)
    view_count = models.PositiveIntegerField('閲覧回数', default=0)
    
    related_inquiries = models.ManyToManyField(Inquiry, blank=True, verbose_name='関連問い合わせ')
    
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)
    
    tags = models.CharField('タグ', max_length=500, blank=True, help_text='カンマ区切りで入力')
    
    class Meta:
        verbose_name = 'ナレッジ'
        verbose_name_plural = 'ナレッジ'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


class Attachment(models.Model):
    """添付ファイル"""
    inquiry = models.ForeignKey(Inquiry, on_delete=models.CASCADE, related_name='attachments', verbose_name='問い合わせ')
    file = models.FileField('ファイル', upload_to='inquiry_attachments/')
    filename = models.CharField('ファイル名', max_length=255)
    uploaded_at = models.DateTimeField('アップロード日時', auto_now_add=True)
    
    class Meta:
        verbose_name = '添付ファイル'
        verbose_name_plural = '添付ファイル'

    def __str__(self):
        return self.filename