from django import forms
from .models import Source

class SourceForm(forms.ModelForm):
    class Meta:
        model = Source
        fields = [
            'name',
            'link',
            'website',
            'brief_info',
            'state',
            'approve_state',
            'iframe_flag',
            'logo_url',
            'note'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'link': forms.URLInput(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'website': forms.URLInput(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'brief_info': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'state': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'approve_state': forms.Select(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'iframe_flag': forms.CheckboxInput(attrs={'class': 'rounded text-primary focus:ring-primary'}),
            'logo_url': forms.URLInput(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
        }
        labels = {
            'name': 'اسم المصدر',
            'link': 'رابط الـ RSS',
            'website': 'رابط الموقع الرسمي',
            'brief_info': 'وصف مختصر',
            'state': 'الحالة العامة',
            'approve_state': 'حالة الموافقة',
            'iframe_flag': 'تضمين في iframe؟',
            'logo_url': 'رابط الشعار',
            'note': 'ملاحظات المشرف',
        }


class SourceSuggestionForm(forms.ModelForm):
    SOURCE_TYPE_CHOICES = [
        ('', 'اختر التصنيف...'),
        ('أخبار عامة', 'أخبار عامة'),
        ('رياضة', 'رياضة'),
        ('اقتصاد', 'اقتصاد'),
        ('تقنية', 'تقنية'),
        ('ثقافة وفنون', 'ثقافة وفنون'),
    ]
    source_type = forms.ChoiceField(
        choices=SOURCE_TYPE_CHOICES,
        label='التصنيف',
        widget=forms.Select(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'})
    )

    class Meta:
        model = Source
        fields = [
            'name',
            'link',
            'source_type',
            'iframe_flag',
            'website',
            'logo_url',
            'brief_info',
            'admin_email',
            'admin_name',
            'note'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'link': forms.URLInput(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'iframe_flag': forms.CheckboxInput(attrs={'class': 'rounded text-primary focus:ring-primary'}),
            'website': forms.URLInput(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'logo_url': forms.URLInput(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'brief_info': forms.Textarea(attrs={'rows': 3, 'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'admin_email': forms.EmailInput(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'admin_name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': 'w-full rounded-xl border-gray-400 focus:border-primary focus:ring-primary'}),
        }
        labels = {
            'name': 'إسم المصدر',
            'link': 'رابط RSS',
            'iframe_flag': 'هل البيان في آيفرايم؟',
            'website': 'موقع إلكتروني',
            'logo_url': 'رابط إلى الشعار',
            'brief_info': 'معلومات موجزة',
            'admin_email': 'البريد الإلكتروني للمشرف',
            'admin_name': 'إسم المشرف',
            'note': 'ملحوظة',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure all fields are required as indicated by * in the user's screenshot
        for field_name, field in self.fields.items():
            if field_name != 'iframe_flag':
                field.required = True
        # Default iframe_flag to True as checked in the screenshot
        self.fields['iframe_flag'].initial = True
