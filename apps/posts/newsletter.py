from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import NewsletterOptOut

signer = TimestampSigner(salt='yp-newsletter-unsub-salt')

def make_unsub_token(email):
    return signer.sign(email.strip().lower())

def parse_unsub_token(token, max_age_days=365):
    try:
        return signer.unsign(token, max_age=86400 * max_age_days)
    except (BadSignature, SignatureExpired):
        return None

@method_decorator(csrf_exempt, name='dispatch')
class NewsletterUnsubscribeView(View):
    def post(self, request, token):
        email = parse_unsub_token(token)
        if not email:
            return HttpResponse("Invalid or expired token", status=400)
        NewsletterOptOut.objects.get_or_create(email=email)
        return HttpResponse("Unsubscribed successfully", status=200)

    def get(self, request, token):
        email = parse_unsub_token(token)
        if not email:
            return render(request, 'newsletter/unsubscribed.html', {'error': True}, status=400)
        NewsletterOptOut.objects.get_or_create(email=email)
        return render(request, 'newsletter/unsubscribed.html', {'error': False, 'email': email})
