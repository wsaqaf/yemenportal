from django import forms
from .models import Source

INPUT_CLASSES = (
    'w-full px-4 py-2.5 rounded-xl border border-gray-300 dark:border-slate-600 '
    'bg-white dark:bg-slate-700 text-gray-900 dark:text-slate-100 placeholder-gray-400 '
    'shadow-sm focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none transition-all'
)

SELECT_CLASSES = (
    'w-full px-4 py-2.5 rounded-xl border border-gray-300 dark:border-slate-600 '
    'bg-white dark:bg-slate-700 text-gray-900 dark:text-slate-100 shadow-sm '
    'focus:border-primary focus:ring-2 focus:ring-primary/20 focus:outline-none transition-all cursor-pointer'
)

CHECKBOX_CLASSES = (
    'w-4 h-4 rounded border border-gray-300 dark:border-slate-600 text-primary focus:ring-primary cursor-pointer'
)

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
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'link': forms.URLInput(attrs={'class': INPUT_CLASSES}),
            'website': forms.URLInput(attrs={'class': INPUT_CLASSES}),
            'brief_info': forms.Textarea(attrs={'rows': 3, 'class': INPUT_CLASSES}),
            'state': forms.Select(attrs={'class': SELECT_CLASSES}),
            'approve_state': forms.Select(attrs={'class': SELECT_CLASSES}),
            'iframe_flag': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
            'logo_url': forms.URLInput(attrs={'class': INPUT_CLASSES}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': INPUT_CLASSES}),
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
    class Meta:
        model = Source
        fields = [
            'name',
            'link',
            'iframe_flag',
            'website',
            'logo_url',
            'brief_info',
            'admin_email',
            'admin_name',
            'note'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'link': forms.URLInput(attrs={'class': INPUT_CLASSES}),
            'iframe_flag': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
            'website': forms.URLInput(attrs={'class': INPUT_CLASSES}),
            'logo_url': forms.URLInput(attrs={'class': INPUT_CLASSES}),
            'brief_info': forms.Textarea(attrs={'rows': 3, 'class': INPUT_CLASSES}),
            'admin_email': forms.EmailInput(attrs={'class': INPUT_CLASSES}),
            'admin_name': forms.TextInput(attrs={'class': INPUT_CLASSES}),
            'note': forms.Textarea(attrs={'rows': 2, 'class': INPUT_CLASSES}),
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
