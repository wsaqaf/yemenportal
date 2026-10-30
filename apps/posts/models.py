from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from apps.sources.models import Source

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

class Topic(models.Model):
    main_post = models.OneToOneField(
        'Post', 
        on_delete=models.CASCADE, 
        related_name='main_topic_of',
        null=True,
        blank=True
    )
    topic_size = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Topic for {self.main_post_id}"

class Post(models.Model):
    class State(models.TextChoices):
        PENDING = 'pending', _('Pending')
        APPROVED = 'approved', _('Approved')
        REJECTED = 'rejected', _('Rejected')

    title = models.TextField()
    description = models.TextField(blank=True, null=True)
    link = models.TextField(unique=True)
    published_at = models.DateTimeField()
    
    state = models.CharField(max_length=20, choices=State.choices, default=State.APPROVED)
    image_url = models.TextField(blank=True, null=True)
    
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='posts')
    categories = models.ManyToManyField(Category, related_name='posts', blank=True)
    
    # Topic clustering
    topic = models.ForeignKey(
        Topic, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='posts'
    )
    
    # Metrics
    voting_result = models.IntegerField(default=0)
    post_views_count = models.IntegerField(default=0)
    review_rating = models.IntegerField(default=0)
    
    # For search/NLP
    stemmed_text = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    @property
    def upvoted_by_user(self):
        # This is a bit inefficient for lists, but fine for now
        # Better to annotate in the queryset
        return getattr(self, '_upvoted_by_user', False)

    @property
    def downvoted_by_user(self):
        return getattr(self, '_downvoted_by_user', False)

class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='votes')
    value = models.IntegerField() # 1 for upvote, -1 for downvote
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'post')

class PostView(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='post_views'
    )
    ip_hash = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NewsletterOptOut(models.Model):
    email = models.EmailField(unique=True, db_index=True, verbose_name='البريد الملغى')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'newsletter_optout'
        verbose_name = 'إلغاء اشتراك نشرة'


class NewsletterAnnouncement(models.Model):
    STATUS_CHOICES = [('draft', 'مسودة'), ('sent', 'تم الإرسال')]
    TARGET_CHOICES = [
        ('all', 'جميع الأعضاء المشتركين (147 عضواً)'),
        ('active_and_staff', 'المتفاعلون وفريق الإدارة معاً - بدون تكرار (36 عضواً)'),
        ('active_only', 'الأعضاء المتفاعلون فقط (29 عضواً)'),
        ('staff_only', 'فريق الإدارة والمشرفين فقط (23 عضواً)'),
        ('custom', 'قائمة عناوين بريد محددة يدوياً'),
    ]

    subject = models.CharField(max_length=255, verbose_name='عنوان الرسالة')
    body = models.TextField(verbose_name='نص الرسالة / الإعلان')
    is_html = models.BooleanField(default=False, verbose_name='تفعيل كود HTML المباشر')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='الحالة')
    target_group = models.CharField(
        max_length=30,
        choices=TARGET_CHOICES,
        default='all',
        verbose_name='الفئة المستهدفة'
    )
    custom_recipients = models.TextField(
        blank=True,
        verbose_name='عناوين بريد مخصصة (اختياري)',
        help_text='إذا اخترت "قائمة مخصصة"، أدخل العناوين هنا مفصولة بفواصل أو أسطر جديدة.'
    )
    test_email = models.EmailField(
        blank=True,
        verbose_name='بريد للاختبار السريع (اختياري)',
        help_text='أدخل بريدك هنا لإرسال تجربة والتأكد من شكل الرسالة قبل الإرسال الفعلي.'
    )
    recipients_count = models.PositiveIntegerField(default=0, verbose_name='عدد المستلمين')
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الإرسال')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'newsletter_announcements'
        verbose_name = 'إعلان بريدي مخصص'
        verbose_name_plural = 'إعلانات بريدية مخصصة'
        ordering = ['-created_at']

    def __str__(self):
        return self.subject


class CurrencyRate(models.Model):
    REGION_CHOICES = [
        ('sanaa', 'صنعاء'),
        ('aden', 'عدن'),
    ]
    CURRENCY_CHOICES = [
        ('USD', 'دولار أمريكي'),
        ('SAR', 'ريال سعودي'),
        ('AED', 'درهم إماراتي'),
    ]
    region = models.CharField(max_length=20, choices=REGION_CHOICES, verbose_name='المنطقة')
    currency_code = models.CharField(max_length=10, choices=CURRENCY_CHOICES, verbose_name='العملة')
    buy_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='سعر الشراء')
    sell_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='سعر البيع')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخر تحديث')

    class Meta:
        db_table = 'posts_currency_rates'
        unique_together = ('region', 'currency_code')
        verbose_name = 'سعر صرف العملة'
        verbose_name_plural = 'أسعار صرف العملات'
        ordering = ['region', '-currency_code']

    def __str__(self):
        return f"{self.get_region_display()} - {self.get_currency_code_display()}: {self.buy_price}/{self.sell_price}"

