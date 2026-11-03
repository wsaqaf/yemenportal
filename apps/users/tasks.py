import logging
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from celery import shared_task
from apps.users.models import User

logger = logging.getLogger(__name__)


def generate_login_report(hours=24, recipient="admin@yemenportal.net"):
    """
    Generates and sends an email report of users who logged in or registered
    in the past `hours` to the specified `recipient`.
    """
    now = timezone.now()
    cutoff = now - timedelta(hours=hours)

    logged_in_users = list(
        User.objects.filter(last_login__gte=cutoff)
        .prefetch_related('socialaccount_set')
        .order_by('-last_login')
    )
    new_users = list(
        User.objects.filter(date_joined__gte=cutoff)
        .prefetch_related('socialaccount_set')
        .order_by('-date_joined')
    )
    total_users_count = User.objects.count()

    subject = f"[يمن بورتال] تقرير تسجيلات الدخول والحسابات النشطة ({len(logged_in_users)} مستخدم)"

    # Text body
    text_lines = [
        f"تقرير نشاط وتسجيلات دخول يمن بورتال",
        f"الفترة: آخر {hours} ساعة (من {cutoff.strftime('%Y-%m-%d %H:%M')} إلى {now.strftime('%Y-%m-%d %H:%M')} UTC)",
        f"إجمالي المستخدمين في النظام: {total_users_count}",
        f"عدد المستخدمين الذين سجلوا دخولهم: {len(logged_in_users)}",
        f"عدد الحسابات الجديدة المنشأة: {len(new_users)}",
        "-" * 50,
        "\nقائمة المستخدمين الذين سجلوا دخولهم:",
    ]

    if logged_in_users:
        for u in logged_in_users:
            providers = [sa.provider for sa in u.socialaccount_set.all()]
            provider_str = ", ".join(providers) if providers else "direct/email"
            last_login_str = u.last_login.strftime('%Y-%m-%d %H:%M:%S UTC') if u.last_login else "-"
            text_lines.append(f"- {u.email} | آخر دخول: {last_login_str} | الطريقة: {provider_str} | الدور: {u.role}")
    else:
        text_lines.append("لا توجد تسجيلات دخول مسجلة خلال هذه الفترة.")

    if new_users:
        text_lines.append("\n" + "-" * 50)
        text_lines.append("الحسابات المنشأة حديثاً:")
        for u in new_users:
            providers = [sa.provider for sa in u.socialaccount_set.all()]
            provider_str = ", ".join(providers) if providers else "direct/email"
            joined_str = u.date_joined.strftime('%Y-%m-%d %H:%M:%S UTC') if u.date_joined else "-"
            text_lines.append(f"- {u.email} | تاريخ التسجيل: {joined_str} | الطريقة: {provider_str}")

    text_content = "\n".join(text_lines)

    # HTML body
    html_rows = ""
    for idx, u in enumerate(logged_in_users, 1):
        providers = [sa.provider for sa in u.socialaccount_set.all()]
        provider_badge = '<span style="background-color:#EBF5FF;color:#1E40AF;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:bold;">Google</span>' if 'google' in providers else '<span style="background-color:#F3F4F6;color:#374151;padding:2px 8px;border-radius:6px;font-size:11px;">مباشر</span>'
        last_login_str = u.last_login.strftime('%Y-%m-%d %H:%M:%S') if u.last_login else "-"
        date_joined_str = u.date_joined.strftime('%Y-%m-%d') if u.date_joined else "-"
        html_rows += f"""
        <tr style="border-bottom:1px solid #E5E7EB;">
            <td style="padding:10px;text-align:center;color:#6B7280;font-size:12px;">{idx}</td>
            <td style="padding:10px;font-weight:bold;color:#111827;direction:ltr;text-align:left;">{u.email}</td>
            <td style="padding:10px;text-align:center;color:#4B5563;font-size:12px;" dir="ltr">{last_login_str}</td>
            <td style="padding:10px;text-align:center;">{provider_badge}</td>
            <td style="padding:10px;text-align:center;color:#6B7280;font-size:12px;">{u.role}</td>
            <td style="padding:10px;text-align:center;color:#6B7280;font-size:12px;" dir="ltr">{date_joined_str}</td>
        </tr>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head><meta charset="utf-8"></head>
    <body style="font-family:'Tajawal',Segoe UI,Arial,sans-serif;background-color:#F9FAFB;padding:24px;color:#1F2937;margin:0;">
        <div style="max-width:700px;margin:0 auto;background:#FFFFFF;border:1px solid #E5E7EB;border-radius:16px;overflow:hidden;box-shadow:0 4px 6px rgba(0,0,0,0.05);">
            <div style="background:linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);padding:24px;color:#FFFFFF;">
                <h1 style="margin:0;font-size:18px;font-weight:bold;">يمن بورتال - تقرير نشاط تسجيلات الدخول</h1>
                <p style="margin:6px 0 0;font-size:12px;opacity:0.9;">تقرير الرصد الدوري لآخر {hours} ساعة ({cutoff.strftime('%Y-%m-%d %H:%M')} إلى {now.strftime('%Y-%m-%d %H:%M')} UTC)</p>
            </div>
            
            <div style="padding:20px;">
                <div style="display:flex;gap:12px;margin-bottom:20px;">
                    <div style="flex:1;background:#F3F4F6;padding:12px;border-radius:12px;text-align:center;">
                        <div style="font-size:11px;color:#6B7280;font-weight:bold;">سجلوا الدخول</div>
                        <div style="font-size:22px;font-weight:bold;color:#2563EB;margin-top:4px;">{len(logged_in_users)}</div>
                    </div>
                    <div style="flex:1;background:#F3F4F6;padding:12px;border-radius:12px;text-align:center;">
                        <div style="font-size:11px;color:#6B7280;font-weight:bold;">حسابات جديدة</div>
                        <div style="font-size:22px;font-weight:bold;color:#059669;margin-top:4px;">{len(new_users)}</div>
                    </div>
                    <div style="flex:1;background:#F3F4F6;padding:12px;border-radius:12px;text-align:center;">
                        <div style="font-size:11px;color:#6B7280;font-weight:bold;">إجمالي المستخدمين</div>
                        <div style="font-size:22px;font-weight:bold;color:#1F2937;margin-top:4px;">{total_users_count}</div>
                    </div>
                </div>

                <h3 style="font-size:14px;color:#111827;border-bottom:2px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">المستخدمون النشطون (آخر {hours} ساعة):</h3>
                <table style="width:100%;border-collapse:collapse;font-size:13px;">
                    <thead>
                        <tr style="background:#F9FAFB;border-bottom:2px solid #E5E7EB;color:#4B5563;">
                            <th style="padding:8px;text-align:center;">#</th>
                            <th style="padding:8px;text-align:left;">البريد الإلكتروني</th>
                            <th style="padding:8px;text-align:center;">آخر دخول</th>
                            <th style="padding:8px;text-align:center;">طريقة الدخول</th>
                            <th style="padding:8px;text-align:center;">الدور</th>
                            <th style="padding:8px;text-align:center;">تاريخ التسجيل</th>
                        </tr>
                    </thead>
                    <tbody>
                        {html_rows if logged_in_users else '<tr><td colspan="6" style="padding:20px;text-align:center;color:#9CA3AF;">لا توجد تسجيلات دخول مسجلة خلال هذه الفترة.</td></tr>'}
                    </tbody>
                </table>
            </div>
            
            <div style="background:#F9FAFB;padding:14px 20px;border-top:1px solid #E5E7EB;font-size:11px;color:#9CA3AF;text-align:center;">
                تم توليد هذا التقرير آلياً عبر نظام يمن بورتال الإخباري (Yemen Portal)
            </div>
        </div>
    </body>
    </html>
    """

    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Yemen Portal <admin@yemenportal.net>')
    msg = EmailMultiAlternatives(subject, text_content, from_email, [recipient])
    msg.attach_alternative(html_content, "text/html")
    msg.send(fail_silently=False)
    logger.info(f"Sent login report to {recipient} ({len(logged_in_users)} active users).")
    return f"Sent login report to {recipient} ({len(logged_in_users)} active users)."


@shared_task(name="apps.users.tasks.send_daily_login_report")
def send_daily_login_report(recipient="admin@yemenportal.net", hours=24):
    """Periodic Celery Beat task that sends a daily summary of logged-in users."""
    return generate_login_report(hours=hours, recipient=recipient)
