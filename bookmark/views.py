from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

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
