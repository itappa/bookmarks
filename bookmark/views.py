from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.base import ContentFile
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .forms import BookmarkForm
from .models import Category, Item, Tag


class ItemListView(LoginRequiredMixin, ListView):
    template_name = "bookmark/view_card.html"
    model = Item
    context_object_name = "items"
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_common_data())
        paginator = context["paginator"]
        page = context["page_obj"]
        context["page_range"] = paginator.get_elided_page_range(
            page.number, on_each_side=1, on_ends=1
        )
        return context


def list(request):
    context = {
        "items": Item.objects.all(),
    }
    context.update(get_common_data())
    return render(request, "bookmark/view_list.html", context)


def item_list_by_category(request, str):
    context = {
        "items": Item.objects.filter(category__name=str),
    }
    context.update(get_common_data())
    return render(request, "bookmark/view_list.html", context)


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
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            url = data.get("url")

            if not url:
                return JsonResponse({"error": "URL is required"}, status=400)

            # URLの正規化
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            # メタデータを取得
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, timeout=10, verify=False, headers=headers)

            # エンコーディングを適切に処理
            if response.encoding == "ISO-8859-1":
                # ISO-8859-1の場合はUTF-8として扱うことが多い
                response.encoding = "utf-8"

            # エンコーディングが不明な場合はUTF-8を試す
            if not response.encoding or response.encoding.lower() == "iso-8859-1":
                try:
                    content = response.content.decode("utf-8")
                except UnicodeDecodeError:
                    # UTF-8でデコードできない場合は、他のエンコーディングを試す
                    for encoding in ["shift_jis", "euc-jp", "iso-2022-jp", "cp932"]:
                        try:
                            content = response.content.decode(encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        # すべて失敗した場合はUTF-8で強制デコード（エラーを無視）
                        content = response.content.decode("utf-8", errors="ignore")
            else:
                content = response.text

            soup = BeautifulSoup(content, "html.parser", from_encoding="utf-8")

            # 基本情報
            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else ""

            # OGP情報
            og_data = {}
            og_tags = [
                "og:title",
                "og:description",
                "og:image",
                "og:type",
                "og:site_name",
                "og:url",
            ]

            for tag in og_tags:
                meta = soup.find("meta", property=tag)
                if meta and meta.get("content"):
                    content = meta.get("content", "").strip()
                    if content:
                        og_data[tag.replace("og:", "")] = content

            # ファビコン
            favicon = soup.find("link", rel="icon") or soup.find(
                "link", rel="shortcut icon"
            )
            favicon_url = ""
            if favicon and favicon.get("href"):
                favicon_url = urljoin(url, favicon["href"])

            # 説明文（OGP descriptionがない場合はmeta descriptionを使用）
            description = og_data.get("description", "").strip()
            if not description:
                meta_desc = soup.find("meta", attrs={"name": "description"})
                if meta_desc:
                    description = meta_desc.get("content", "").strip()

            result = {
                "url": url,
                "title": og_data.get("title", title_text),
                "description": description,
                "image": og_data.get("image", ""),
                "type": og_data.get("type", ""),
                "site_name": og_data.get("site_name", ""),
                "favicon_url": favicon_url,
                "success": True,
            }

            return JsonResponse(result)

        except Exception as e:
            return JsonResponse({"error": str(e), "success": False}, status=500)

    return JsonResponse({"error": "Method not allowed"}, status=405)


def quick_add_bookmark(request):
    initial_data = {}
    if "url" in request.GET:
        initial_data["url"] = request.GET["url"]
    if "title" in request.GET:
        initial_data["title"] = request.GET["title"]

    if request.method == "POST":
        form = BookmarkForm(request.POST)
        if form.is_valid():
            bookmark = form.save(commit=False)

            # OGP情報を設定
            bookmark.og_title = form.cleaned_data.get("og_title", "")
            bookmark.og_description = form.cleaned_data.get("og_description", "")
            bookmark.og_type = form.cleaned_data.get("og_type", "")
            bookmark.og_site_name = form.cleaned_data.get("og_site_name", "")
            bookmark.favicon_url = form.cleaned_data.get("favicon_url", "")

            # OGP画像の処理
            og_image_url = form.cleaned_data.get("og_image", "")
            if og_image_url:
                try:
                    import requests
                    from urllib.parse import urljoin
                    from django.core.files.base import ContentFile

                    # 画像URLを絶対URLに変換
                    if not og_image_url.startswith(("http://", "https://")):
                        og_image_url = urljoin(bookmark.url, og_image_url)

                    # 画像をダウンロードして保存
                    response = requests.get(og_image_url, timeout=10, verify=False)
                    if response.status_code == 200:
                        image_name = og_image_url.split("/")[-1]
                        if not image_name or "." not in image_name:
                            image_name = "og_image.jpg"
                        bookmark.og_image.save(
                            image_name, ContentFile(response.content), save=False
                        )
                except Exception as e:
                    print(f"Error downloading OGP image: {e}")

            bookmark.save()

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
    return render(request, "bookmark/quick_add_bookmark.html", context)
