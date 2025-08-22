from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Inquiry, Response, Knowledge, Attachment
from django.utils import timezone


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'parent', 'created_at']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'description': ('name',)}


class ResponseInline(admin.TabularInline):
    model = Response
    extra = 0
    fields = ['responder', 'content', 'is_internal', 'created_at']
    readonly_fields = ['created_at']


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 0
    fields = ['file', 'filename', 'uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'customer_name', 'status', 'priority', 
        'category', 'assigned_to', 'created_at', 'days_since_created'
    ]
    list_filter = ['status', 'priority', 'category', 'assigned_to', 'created_at']
    search_fields = ['title', 'content', 'customer_name', 'customer_email', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'resolved_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('基本情報', {
            'fields': ('title', 'content', 'category', 'tags')
        }),
        ('顧客情報', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('管理情報', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('日時情報', {
            'fields': ('created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ResponseInline, AttachmentInline]
    
    def days_since_created(self, obj):
        days = (timezone.now() - obj.created_at).days
        if days == 0:
            return "今日"
        elif days == 1:
            return "昨日"
        else:
            return f"{days}日前"
    days_since_created.short_description = '経過日数'


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['inquiry', 'responder', 'is_internal', 'created_at']
    list_filter = ['responder', 'is_internal', 'created_at']
    search_fields = ['content', 'inquiry__title']
    readonly_fields = ['created_at']


@admin.register(Knowledge)
class KnowledgeAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_public', 'view_count', 'updated_at']
    list_filter = ['category', 'author', 'is_public', 'created_at']
    search_fields = ['title', 'content', 'tags']
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('title', 'content', 'category', 'tags')
        }),
        ('管理情報', {
            'fields': ('author', 'is_public', 'view_count')
        }),
        ('関連情報', {
            'fields': ('related_inquiries',),
            'classes': ('collapse',)
        }),
        ('日時情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'inquiry', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['filename', 'inquiry__title']
    readonly_fields = ['uploaded_at']