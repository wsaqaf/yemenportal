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

def get_source_default_category_id(source_id: int):
    cache_key = f"source_dominant_category_{source_id}"
    cat_id = cache.get(cache_key)
    if cat_id is not None:
        return cat_id

    top_cat = (
        Post.objects.filter(source_id=source_id, categories__isnull=False)
        .values('categories__id')
        .annotate(cnt=Count('id'))
        .order_by('-cnt')
        .first()
    )
    cat_id = top_cat['categories__id'] if top_cat else None
    cache.set(cache_key, cat_id, timeout=86400 * 7)  # 7 days TTL
    return cat_id

def get_matching_category(entry, default_cat_id=None):
    tags = [t.get('term', '') for t in entry.get('tags', []) if t.get('term')]
    if entry.get('category'):
        tags.append(entry.get('category'))

    if tags:
        for tag in tags:
            tag_clean = tag.strip()
            cat = Category.objects.filter(name__iexact=tag_clean).first()
            if cat:
                return cat.id

    return default_cat_id

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
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
    source_cat_id = get_source_default_category_id(source.id)

    for entry in feed.entries:
        if not Post.objects.filter(link=entry.link).exists():
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = make_aware(datetime.fromtimestamp(mktime(entry.published_parsed)))
            else:
                published_at = timezone.now()

            post = Post.objects.create(
                title=entry.title,
                description=entry.get('summary', entry.get('description', '')),
                link=entry.link,
                published_at=published_at,
                source=source,
                image_url=extract_image_url(entry),
                state=Post.State.APPROVED
            )

            target_cat_id = get_matching_category(entry, default_cat_id=source_cat_id)
            if target_cat_id:
                post.categories.add(target_cat_id)

            new_posts_count += 1

    SourceLog.objects.create(source=source, state="Success", posts_count=new_posts_count)
    return new_posts_count
