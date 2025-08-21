import os
from urllib.parse import urljoin
from uuid import uuid4

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone

# urllib3.disable_warnings(InsecureRequestWarning)


class Category(models.Model):
    name = models.CharField("カテゴリ", max_length=200, unique=True)

    class Meta:
        verbose_name_plural = "カテゴリ"

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField("タグ", max_length=200, unique=True)

    class Meta:
        verbose_name_plural = "タグ"

    def __str__(self) -> str:
        return self.name
    
def upload_to_factory(folder):
    def upload_to(instance, filename):
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        filename = f"{uuid4()}{ext}"
        return f"media/images/bookmark/{folder}/{filename}"
    return upload_to

class Item(models.Model):
    url = models.URLField(max_length=2000)
    title = models.CharField(verbose_name="タイトル", max_length=512)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, verbose_name="カテゴリ", on_delete=models.SET_NULL, blank=True, null=True)
    tags = models.ManyToManyField(Tag, verbose_name="タグ", related_name="tags", blank=True)
    created_at = models.DateTimeField("登録日時", auto_now_add=True)

    # ファビコン関連
    favicon = models.ImageField(upload_to=upload_to_factory("favicons"), blank=True, null=True)
    favicon_url = models.URLField(max_length=255, blank=True)

    # OGP関連
    og_title = models.CharField(max_length=512, blank=True)
    og_description = models.TextField(blank=True)
    og_image = models.ImageField(upload_to=upload_to_factory("og_images"), blank=True, null=True)
    og_type = models.CharField(max_length=50, blank=True)
    og_site_name = models.CharField(max_length=512, blank=True)

    last_metadata_update = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "アイテム"
        ordering = ("-id",)

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.last_metadata_update or (timezone.now() - self.last_metadata_update).days >= 7:
            self.fetch_metadata()
            self.last_metadata_update = timezone.now()
        super().save(*args, **kwargs)

    def fetch_metadata(self):
        try:
            response = requests.get(self.url, verify=False)
            soup = BeautifulSoup(response.text, "html.parser")

            # ファビコンの取得と保存
            favicon = soup.find("link", rel="icon") or soup.find("link", rel="shortcut icon")
            print(favicon)
            if favicon:
                favicon_url = urljoin(self.url, favicon["href"])
                favicon_response = requests.get(favicon_url)
                if favicon_response.status_code == 200:
                    favicon_name = favicon_url.split("/")[-1]
                    self.favicon.save(favicon_name, ContentFile(favicon_response.content), save=False)

            # OGP情報の取得
            og_title = soup.find("meta", property="og:title")
            if og_title:
                self.og_title = og_title["content"]

            og_description = soup.find("meta", property="og:description")
            if og_description:
                self.og_description = og_description["content"]

            og_image = soup.find("meta", property="og:image")
            print(og_image)
            if og_image:
                og_image_url = urljoin(self.url, og_image["content"])
                og_image_response = requests.get(og_image_url)
                if og_image_response.status_code == 200:
                    og_image_name = og_image_url.split("/")[-1]
                    self.og_image.save(og_image_name, ContentFile(og_image_response.content), save=False)

            og_type = soup.find("meta", property="og:type")
            if og_type:
                self.og_type = og_type["content"]

            og_site_name = soup.find("meta", property="og:site_name")
            if og_site_name:
                self.og_site_name = og_site_name["content"]

        except Exception as e:
            print(f"Error fetching metadata: {e}")
