from django.utils.html import strip_tags
import feedparser
import requests
import re
from datetime import datetime
from time import mktime
from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone
from django.utils.timezone import make_aware
from apps.posts.models import Post, Category
from apps.sources.models import Source, SourceLog

def get_matching_categories(entry, title: str, description: str, link: str, source_name: str) -> list[int]:
    from apps.posts.services.categorizer import classify_post_categories

    tags = [t.get('term', '') for t in entry.get('tags', []) if t.get('term')]
    if entry.get('category'):
        tags.append(entry.get('category'))

    return classify_post_categories(
        title=title,
        description=description,
        link=link,
        source_name=source_name,
        rss_tags=tags,
    )

def extract_image_url(entry):
    if 'media_content' in entry and entry.media_content:
        return entry.media_content[0].get('url')

    if 'links' in entry:
        for link in entry.links:
            if link.get('rel') == 'enclosure' and 'image' in link.get('type', ''):
                return link.get('href')

    description = entry.get('summary', entry.get('description', ''))
    if '<img' in description:
        match = re.search(r'<img [^>]*src="([^"]+)"', description)
        if match:
            return match.group(1)

    return None

def fetch_source(source: Source):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
    }
    try:
        response = requests.get(source.link, headers=headers, timeout=15)
        response.raise_for_status()
        feed = feedparser.parse(response.content)

        if getattr(feed, 'bozo', 0) == 1 and not feed.entries:
            raise Exception(f"Feedparser bozo error: {getattr(feed, 'bozo_exception', 'Unknown')}")

    except Exception as e:
        error_msg = f"Error: {str(e)[:40]}"
        print(f"Error fetching {source.name}: {error_msg}")
        SourceLog.objects.create(source=source, state=error_msg, posts_count=0)
        return 0

    new_posts_count = 0

    for entry in feed.entries:
        entry_link = getattr(entry, 'link', None) or (entry.get('link') if hasattr(entry, 'get') else None)
        if not entry_link and hasattr(entry, 'links') and entry.links:
            try:
                entry_link = entry.links[0].get('href')
            except Exception:
                entry_link = None
        if not entry_link:
            continue

        if Post.objects.filter(link=entry_link).exists():
            continue

        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                published_at = make_aware(datetime.fromtimestamp(mktime(entry.published_parsed)))
            except Exception:
                published_at = timezone.now()
        else:
            published_at = timezone.now()

        # Cap future dates to prevent articles sticking to the top of homepage
        if published_at > timezone.now():
            published_at = timezone.now()

        title_text = getattr(entry, 'title', '') or 'بدون عنوان'
        desc_text = strip_tags(entry.get('summary', entry.get('description', '')) if hasattr(entry, 'get') else '').strip()

        post = Post.objects.create(
            title=title_text,
            description=desc_text,
            link=entry_link,
            published_at=published_at,
            source=source,
            image_url=extract_image_url(entry),
            state=Post.State.APPROVED
        )

        target_cat_ids = get_matching_categories(
            entry=entry,
            title=title_text,
            description=desc_text,
            link=entry_link,
            source_name=source.name,
        )
        if target_cat_ids:
            post.categories.add(*target_cat_ids)

        new_posts_count += 1
    SourceLog.objects.create(source=source, state="Success", posts_count=new_posts_count)
    return new_posts_count
