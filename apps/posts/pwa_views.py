import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def pwa_manifest(request):
    """Serves the Web App Manifest with application/manifest+json MIME type."""
    manifest_path = settings.BASE_DIR / "static" / "manifest.json"
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        response = JsonResponse(data, json_dumps_params={"ensure_ascii": False})
        response["Content-Type"] = "application/manifest+json; charset=utf-8"
        response["Cache-Control"] = "public, max-age=86400"
        return response
    except Exception:
        fallback = {
            "name": "يمن بورتال - محرك بحث إخباري يمني",
            "short_name": "يمن بورتال",
            "start_url": "/?source=pwa",
            "scope": "/",
            "display": "standalone",
            "theme_color": "#1779ba",
            "background_color": "#0f172a",
            "lang": "ar",
            "dir": "rtl",
        }
        response = JsonResponse(fallback, json_dumps_params={"ensure_ascii": False})
        response["Content-Type"] = "application/manifest+json; charset=utf-8"
        return response


@require_GET
def pwa_service_worker(request):
    """Serves the Service Worker at root scope with Service-Worker-Allowed header."""
    sw_path = settings.BASE_DIR / "static" / "js" / "sw.js"
    try:
        with open(sw_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        content = "self.addEventListener('fetch', () => {});"

    response = HttpResponse(content, content_type="application/javascript; charset=utf-8")
    response["Service-Worker-Allowed"] = "/"
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


@require_GET
def pwa_offline(request):
    """Serves the offline fallback page."""
    return render(request, "offline.html")
