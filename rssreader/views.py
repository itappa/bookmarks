from typing import Any, Dict, List

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
import requests
from xml.etree import ElementTree as ET


def parse_feed(url: str) -> Dict[str, Any]:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    content = response.content

    root = ET.fromstring(content)

    # Try RSS 2.0
    channel = root.find("channel")
    if channel is not None:
        title = (channel.findtext("title") or "").strip()
        description = (channel.findtext("description") or "").strip()
        items: List[Dict[str, str]] = []
        for item in channel.findall("item"):
            items.append(
                {
                    "title": (item.findtext("title") or "").strip(),
                    "link": (item.findtext("link") or "").strip(),
                    "description": (item.findtext("description") or "").strip(),
                }
            )
        return {"title": title, "description": description, "items": items}

    # Try Atom
    if root.tag.endswith("feed"):
        ns_title = root.findtext("{http://www.w3.org/2005/Atom}title") or root.findtext("title") or ""
        items = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            link_href = ""
            link_el = entry.find("{http://www.w3.org/2005/Atom}link")
            if link_el is not None:
                link_href = link_el.attrib.get("href", "")
            items.append(
                {
                    "title": (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip(),
                    "link": link_href,
                    "description": (entry.findtext("{http://www.w3.org/2005/Atom}summary") or "").strip(),
                }
            )
        return {"title": ns_title.strip(), "description": "", "items": items}

    return {"title": "", "description": "", "items": []}


def index(request: HttpRequest) -> HttpResponse:
    context: Dict[str, Any] = {"feed": None, "error": None}
    if request.method == "POST":
        url = request.POST.get("url", "").strip()
        if url:
            try:
                context["feed"] = parse_feed(url)
            except Exception as exc:  # noqa: BLE001
                context["error"] = str(exc)
    return render(request, "rssreader/index.html", context)

