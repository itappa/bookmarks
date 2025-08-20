from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .forms import BookmarkForm
from .models import Category, Item, Tag


class ItemListView(LoginRequiredMixin, ListView):
    template_name = "bookmark/index.html"
    model = Item
    context_object_name = "items"
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_common_data())
        paginator = context["paginator"]
        page = context["page_obj"]
        context["page_range"] = paginator.get_elided_page_range(page.number, on_each_side=1, on_ends=1)
        return context


def table(request):
    context = {
        "items": Item.objects.all(),
    }
    context.update(get_common_data())
    return render(request, "bookmark/tables.html", context)


def list(request):
    context = {
        "items": Item.objects.all(),
    }
    context.update(get_common_data())
    return render(request, "bookmark/list.html", context)


def item_list_by_category(request, str):
    context = {
        "items": Item.objects.filter(category__name=str),
    }
    context.update(get_common_data())
    return render(request, "bookmark/index.html", context)


def add_bookmark(request):
    initial_data = {}
    if "url" in request.GET:
        initial_data["url"] = request.GET["url"]
    if "title" in request.GET:
        initial_data["title"] = request.GET["title"]

    if request.method == "POST":
        form = BookmarkForm(request.POST)
        if form.is_valid():
            bookmark = form.save()

            # 新規カテゴリの処理
            new_category = form.cleaned_data.get("new_category")
            if new_category:
                category, created = Category.objects.get_or_create(name=new_category)
                bookmark.category = category

            # tagsの処理
            tags = form.cleaned_data.get("tags")
            if tags:
                bookmark.tags.set(tags)

            # 新規タグの処理
            new_tags = form.cleaned_data.get("new_tags")
            if new_tags:
                tags = [tag.strip() for tag in new_tags.split(",")]
                for tag_name in tags:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    bookmark.tags.add(tag)
            bookmark.save()

            return redirect("bookmark:index")
    else:
        form = BookmarkForm(initial=initial_data)

    context = {"form": form}
    context.update(get_common_data())
    return render(request, "bookmark/add_bookmark.html", context)


def edit_view(request, pk):
    obj = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        form = BookmarkForm(request.POST, instance=obj)
        if form.is_valid():
            bookmark = form.save()

            # 新規カテゴリの処理
            new_category = form.cleaned_data.get("new_category")
            if new_category:
                category, created = Category.objects.get_or_create(name=new_category)
                bookmark.category = category

            # 新規タグの処理
            new_tags = form.cleaned_data.get("new_tags")
            if new_tags:
                tags = [tag.strip() for tag in new_tags.split(",")]
                for tag_name in tags:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    bookmark.tags.add(tag)
            bookmark.save()
            return redirect("bookmark:index")
    else:
        form = BookmarkForm(instance=obj)

    context = {"form": form, "object": obj}
    context.update(get_common_data())
    return render(request, "bookmark/detail.html", context)


def delete_view(request, pk):
    obj = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        obj.delete()
        return redirect("bookmark:index")
    context = {"object": obj}
    context.update(get_common_data())
    return render(request, "delete_confirm_template.html", context)


def get_common_data():
    category_list = Category.objects.all()
    return {"category_list": category_list}


@csrf_exempt
def fetch_ogp_data(request):
    """URLからOGP情報を取得するAPI"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            url = data.get('url')
            
            if not url:
                return JsonResponse({'error': 'URL is required'}, status=400)
            
            # URLの正規化
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # メタデータを取得
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 基本情報
            title = soup.find('title')
            title_text = title.get_text() if title else ''
            
            # OGP情報
            og_data = {}
            og_tags = [
                'og:title', 'og:description', 'og:image', 'og:type', 
                'og:site_name', 'og:url'
            ]
            
            for tag in og_tags:
                meta = soup.find('meta', property=tag)
                if meta and meta.get('content'):
                    og_data[tag.replace('og:', '')] = meta.get('content')
            
            # ファビコン
            favicon = soup.find("link", rel="icon") or soup.find("link", rel="shortcut icon")
            favicon_url = ''
            if favicon and favicon.get('href'):
                favicon_url = urljoin(url, favicon['href'])
            
            # 説明文（OGP descriptionがない場合はmeta descriptionを使用）
            description = og_data.get('description', '')
            if not description:
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    description = meta_desc.get('content', '')
            
            result = {
                'url': url,
                'title': og_data.get('title', title_text),
                'description': description,
                'image': og_data.get('image', ''),
                'type': og_data.get('type', ''),
                'site_name': og_data.get('site_name', ''),
                'favicon_url': favicon_url,
                'success': True
            }
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e), 'success': False}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def quick_add_bookmark(request):
    """URLのみ入力できるブックマーク登録ページ"""
    if request.method == 'POST':
        form = BookmarkForm(request.POST)
        if form.is_valid():
            bookmark = form.save()

            # 新規カテゴリの処理
            new_category = form.cleaned_data.get("new_category")
            if new_category:
                category, created = Category.objects.get_or_create(name=new_category)
                bookmark.category = category

            # tagsの処理
            tags = form.cleaned_data.get("tags")
            if tags:
                bookmark.tags.set(tags)

            # 新規タグの処理
            new_tags = form.cleaned_data.get("new_tags")
            if new_tags:
                tags = [tag.strip() for tag in new_tags.split(",")]
                for tag_name in tags:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    bookmark.tags.add(tag)
            bookmark.save()

            return redirect("bookmark:index")
    else:
        form = BookmarkForm()

    context = {"form": form}
    context.update(get_common_data())
    return render(request, "bookmark/quick_add_bookmark.html", context)
