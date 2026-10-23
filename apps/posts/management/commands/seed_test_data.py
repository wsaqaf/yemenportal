from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.posts.models import Post, Category, Topic
from apps.sources.models import Source
import random

class Command(BaseCommand):
    help = 'Seeds test data for local development'

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")
        
        # Create Categories
        cat_news, _ = Category.objects.get_or_create(name='أخبار محلية')
        cat_sports, _ = Category.objects.get_or_create(name='رياضة')
        cat_tech, _ = Category.objects.get_or_create(name='تكنولوجيا')
        
        # Create Sources
        source1, _ = Source.objects.get_or_create(
            name='المصدر أونلاين',
            link='https://almasdaronline.com/rss',
            approve_state=Source.ApproveState.APPROVED
        )
        source2, _ = Source.objects.get_or_create(
            name='عدن الغد',
            link='https://adengad.net/rss',
            approve_state=Source.ApproveState.APPROVED
        )
        
        # Create Posts
        titles = [
            "اليمن يشارك في اجتماع وزراء الثقافة العرب",
            "افتتاح مشروع مياه جديد في تعز",
            "المنتخب الوطني يستعد للمباراة القادمة",
            "انقطاع خدمة الإنترنت في عدة محافظات",
            "تطورات اقتصادية هامة في العاصمة المؤقتة عدن",
        ]
        
        for i, title in enumerate(titles):
            post = Post.objects.create(
                title=title,
                description=f"هذا وصف تجريبي للخبر رقم {i+1}. اليمن بورتال يقدم لكم تغطية شاملة.",
                link=f"https://example.com/news/{i+1}",
                published_at=timezone.now(),
                source=random.choice([source1, source2]),
                voting_result=random.randint(0, 50)
            )
            post.categories.add(random.choice([cat_news, cat_sports, cat_tech]))
            
        self.stdout.write(self.style.SUCCESS("Seeding completed!"))
