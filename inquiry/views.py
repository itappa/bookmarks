from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Inquiry, Response, Knowledge, Category
from .forms import (
    InquiryForm, InquiryUpdateForm, ResponseForm, KnowledgeForm,
    InquirySearchForm, KnowledgeSearchForm
)


class InquiryListView(LoginRequiredMixin, ListView):
    """問い合わせ一覧"""
    model = Inquiry
    template_name = 'inquiry/inquiry_list.html'
    context_object_name = 'inquiries'
    paginate_by = 20

    def get_queryset(self):
        queryset = Inquiry.objects.select_related('category', 'assigned_to').prefetch_related('responses')
        
        # 検索フォームの処理
        form = InquirySearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            if q:
                queryset = queryset.filter(
                    Q(title__icontains=q) |
                    Q(content__icontains=q) |
                    Q(customer_name__icontains=q) |
                    Q(customer_email__icontains=q) |
                    Q(tags__icontains=q)
                )
            
            status = form.cleaned_data.get('status')
            if status:
                queryset = queryset.filter(status=status)
            
            priority = form.cleaned_data.get('priority')
            if priority:
                queryset = queryset.filter(priority=priority)
            
            category = form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)
            
            assigned_to = form.cleaned_data.get('assigned_to')
            if assigned_to:
                queryset = queryset.filter(assigned_to=assigned_to)
            
            date_from = form.cleaned_data.get('date_from')
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
            
            date_to = form.cleaned_data.get('date_to')
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = InquirySearchForm(self.request.GET)
        
        # 統計情報
        context['total_inquiries'] = Inquiry.objects.count()
        context['new_inquiries'] = Inquiry.objects.filter(status='new').count()
        context['in_progress_inquiries'] = Inquiry.objects.filter(status='in_progress').count()
        context['urgent_inquiries'] = Inquiry.objects.filter(priority='urgent').count()
        
        return context


class InquiryDetailView(LoginRequiredMixin, DetailView):
    """問い合わせ詳細"""
    model = Inquiry
    template_name = 'inquiry/inquiry_detail.html'
    context_object_name = 'inquiry'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['response_form'] = ResponseForm()
        context['responses'] = self.object.responses.select_related('responder').order_by('-created_at')
        
        # 担当者リストを取得
        from django.contrib.auth import get_user_model
        User = get_user_model()
        context['assignees'] = User.objects.filter(is_staff=True)
        
        return context

    def post(self, request, *args, **kwargs):
        inquiry = self.get_object()
        form = ResponseForm(request.POST)
        
        if form.is_valid():
            response = form.save(commit=False)
            response.inquiry = inquiry
            response.responder = request.user
            response.save()
            
            messages.success(request, '対応内容を追加しました。')
            return redirect('inquiry:inquiry_detail', pk=inquiry.pk)
        
        context = self.get_context_data()
        context['response_form'] = form
        return self.render_to_response(context)


class InquiryCreateView(LoginRequiredMixin, CreateView):
    """問い合わせ作成"""
    model = Inquiry
    form_class = InquiryForm
    template_name = 'inquiry/inquiry_form.html'
    success_url = reverse_lazy('inquiry:inquiry_list')

    def form_valid(self, form):
        messages.success(self.request, '問い合わせを作成しました。')
        return super().form_valid(form)


class InquiryUpdateView(LoginRequiredMixin, UpdateView):
    """問い合わせ更新"""
    model = Inquiry
    form_class = InquiryUpdateForm
    template_name = 'inquiry/inquiry_form.html'

    def get_success_url(self):
        return reverse_lazy('inquiry:inquiry_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, '問い合わせを更新しました。')
        return super().form_valid(form)


class InquiryDeleteView(LoginRequiredMixin, DeleteView):
    """問い合わせ削除"""
    model = Inquiry
    template_name = 'inquiry/inquiry_confirm_delete.html'
    success_url = reverse_lazy('inquiry:inquiry_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, '問い合わせを削除しました。')
        return super().delete(request, *args, **kwargs)


class KnowledgeListView(LoginRequiredMixin, ListView):
    """ナレッジ一覧"""
    model = Knowledge
    template_name = 'inquiry/knowledge_list.html'
    context_object_name = 'knowledge_list'
    paginate_by = 20

    def get_queryset(self):
        queryset = Knowledge.objects.select_related('category', 'author')
        
        # 検索フォームの処理
        form = KnowledgeSearchForm(self.request.GET)
        if form.is_valid():
            q = form.cleaned_data.get('q')
            if q:
                queryset = queryset.filter(
                    Q(title__icontains=q) |
                    Q(content__icontains=q) |
                    Q(tags__icontains=q)
                )
            
            category = form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)
            
            author = form.cleaned_data.get('author')
            if author:
                queryset = queryset.filter(author=author)
            
            is_public = form.cleaned_data.get('is_public')
            if is_public:
                queryset = queryset.filter(is_public=is_public)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = KnowledgeSearchForm(self.request.GET)
        return context


class KnowledgeDetailView(LoginRequiredMixin, DetailView):
    """ナレッジ詳細"""
    model = Knowledge
    template_name = 'inquiry/knowledge_detail.html'
    context_object_name = 'knowledge'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.increment_view_count()
        return obj


class KnowledgeCreateView(LoginRequiredMixin, CreateView):
    """ナレッジ作成"""
    model = Knowledge
    form_class = KnowledgeForm
    template_name = 'inquiry/knowledge_form.html'
    success_url = reverse_lazy('inquiry:knowledge_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'ナレッジを作成しました。')
        return super().form_valid(form)


class KnowledgeUpdateView(LoginRequiredMixin, UpdateView):
    """ナレッジ更新"""
    model = Knowledge
    form_class = KnowledgeForm
    template_name = 'inquiry/knowledge_form.html'

    def get_success_url(self):
        return reverse_lazy('inquiry:knowledge_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'ナレッジを更新しました。')
        return super().form_valid(form)


class KnowledgeDeleteView(LoginRequiredMixin, DeleteView):
    """ナレッジ削除"""
    model = Knowledge
    template_name = 'inquiry/knowledge_confirm_delete.html'
    success_url = reverse_lazy('inquiry:knowledge_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'ナレッジを削除しました。')
        return super().delete(request, *args, **kwargs)


@login_required
def dashboard(request):
    """ダッシュボード"""
    # 統計情報
    total_inquiries = Inquiry.objects.count()
    new_inquiries = Inquiry.objects.filter(status='new').count()
    in_progress_inquiries = Inquiry.objects.filter(status='in_progress').count()
    urgent_inquiries = Inquiry.objects.filter(priority='urgent').count()
    
    # 最近の問い合わせ
    recent_inquiries = Inquiry.objects.select_related('category', 'assigned_to')[:10]
    
    # 最近のナレッジ
    recent_knowledge = Knowledge.objects.select_related('category', 'author')[:5]
    
    # カテゴリ別統計
    category_stats = Category.objects.annotate(
        inquiry_count=Count('inquiry')
    ).order_by('-inquiry_count')[:10]
    
    # 担当者別統計
    from django.contrib.auth import get_user_model
    User = get_user_model()
    assignee_stats = User.objects.filter(is_staff=True).annotate(
        assigned_count=Count('inquiry')
    ).order_by('-assigned_count')[:10]
    
    context = {
        'total_inquiries': total_inquiries,
        'new_inquiries': new_inquiries,
        'in_progress_inquiries': in_progress_inquiries,
        'urgent_inquiries': urgent_inquiries,
        'recent_inquiries': recent_inquiries,
        'recent_knowledge': recent_knowledge,
        'category_stats': category_stats,
        'assignee_stats': assignee_stats,
    }
    
    return render(request, 'inquiry/dashboard.html', context)


@login_required
def inquiry_status_update(request, pk):
    """問い合わせステータス更新（AJAX）"""
    if request.method == 'POST':
        inquiry = get_object_or_404(Inquiry, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in dict(Inquiry.STATUS_CHOICES):
            inquiry.status = new_status
            inquiry.save()
            return JsonResponse({'success': True, 'status': inquiry.get_status_display()})
    
    return JsonResponse({'success': False})


@login_required
def inquiry_assign(request, pk):
    """問い合わせ担当者割り当て（AJAX）"""
    if request.method == 'POST':
        inquiry = get_object_or_404(Inquiry, pk=pk)
        assignee_id = request.POST.get('assignee_id')
        
        if assignee_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                assignee = User.objects.get(id=assignee_id, is_staff=True)
                inquiry.assigned_to = assignee
                inquiry.save()
                return JsonResponse({'success': True, 'assignee_name': assignee.get_full_name() or assignee.username})
            except User.DoesNotExist:
                pass
    
    return JsonResponse({'success': False})