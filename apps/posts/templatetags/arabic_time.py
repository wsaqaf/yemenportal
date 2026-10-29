from django import template
from django.utils import timezone
import datetime

register = template.Library()

def get_arabic_plural(value, singular, dual, plural_3_10):
    if value == 1:
        return singular
    if value == 2:
        return dual
    if 3 <= (value % 100) <= 10:
        return f"{value} {plural_3_10}"
    return f"{value} {singular}"


@register.filter
def arabic_sources(value):
    try:
        n = int(value)
    except (TypeError, ValueError):
        return ""
    return get_arabic_plural(n, "مصدر", "مصدرين", "مصادر")


@register.filter
def intcomma(value):
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return value or "0"

@register.filter
def arabic_timesince(value):
    if not value:
        return ""
    
    now = timezone.now()
    diff = now - value
    
    seconds = diff.total_seconds()
    if seconds < 0:
        return "الآن"
    
    minutes = int(seconds // 60)
    hours = int(minutes // 60)
    days = int(hours // 24)
    months = int(days // 30)
    years = int(days // 365)

    if years > 0:
        return "قبل " + get_arabic_plural(years, "سنة", "سنتين", "سنوات")
    if months > 0:
        return "قبل " + get_arabic_plural(months, "شهر", "شهرين", "أشهر")
    if days > 0:
        return "قبل " + get_arabic_plural(days, "يوم", "يومين", "أيام")
    if hours > 0:
        return "قبل " + get_arabic_plural(hours, "ساعة", "ساعتين", "ساعات")
    if minutes > 0:
        return "قبل " + get_arabic_plural(minutes, "دقيقة", "دقيقتين", "دقائق")
    
    return "قبل أقل من دقيقة"
