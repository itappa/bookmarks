from django.urls import path
from . import views

app_name = 'inquiry'

urlpatterns = [
    # ダッシュボード
    path('', views.dashboard, name='dashboard'),
    
    # 問い合わせ管理
    path('inquiries/', views.InquiryListView.as_view(), name='inquiry_list'),
    path('inquiries/create/', views.InquiryCreateView.as_view(), name='inquiry_create'),
    path('inquiries/<int:pk>/', views.InquiryDetailView.as_view(), name='inquiry_detail'),
    path('inquiries/<int:pk>/edit/', views.InquiryUpdateView.as_view(), name='inquiry_update'),
    path('inquiries/<int:pk>/delete/', views.InquiryDeleteView.as_view(), name='inquiry_delete'),
    
    # AJAX用
    path('inquiries/<int:pk>/status/', views.inquiry_status_update, name='inquiry_status_update'),
    path('inquiries/<int:pk>/assign/', views.inquiry_assign, name='inquiry_assign'),
    
    # ナレッジ管理
    path('knowledge/', views.KnowledgeListView.as_view(), name='knowledge_list'),
    path('knowledge/create/', views.KnowledgeCreateView.as_view(), name='knowledge_create'),
    path('knowledge/<int:pk>/', views.KnowledgeDetailView.as_view(), name='knowledge_detail'),
    path('knowledge/<int:pk>/edit/', views.KnowledgeUpdateView.as_view(), name='knowledge_update'),
    path('knowledge/<int:pk>/delete/', views.KnowledgeDeleteView.as_view(), name='knowledge_delete'),
]