import re
from typing import Dict, List, Tuple
from django.contrib.auth import get_user_model
from apps.posts.models import Vote, NewsletterOptOut
from apps.sources.models import Source

# 1. Non-existent, dead, or unroutable domains from DNS MX audit
DEAD_DOMAINS = {
    'yemenportal.com', 'tut.by', 'onecalllawncare.com', 'legion-investments.com',
    'auryc.com', 'debugcomputer.net', 'akeeldesigns.com', 'trinitylogisticsgroup.com',
    'nationaltrailsinc.com', 'myfirstfarmer.com', 'nyexectransportation.com',
    'us.army.mil', 'alarabiatimes.net', 't.mail', 'example.com'
}

# 2. US Residential ISP broadband domains heavily scraped in spam combo lists
US_ISP_DOMAINS = {
    'sbcglobal.net', 'verizon.net', 'att.net', 'bellsouth.net', 'comcast.net',
    'charter.net', 'cox.net', 'embarqmail.com', 'optonline.net', 'windstream.net',
    'earthlink.net', 'roadrunner.com', 'frontier.com', 'centurylink.net', 'suddenlink.net'
}

# 3. Known Arabic / Yemeni names and roots (checked as words or distinct parts)
ARABIC_NAME_ROOTS = [
    'ahmed', 'ahmad', 'moham', 'mham', 'saleh', 'abdo', 'abdu', 'abdel', 'abdul',
    'yemen', 'aden', 'sanaa', 'taiz', 'hassan', 'hasan', 'hussein', 'hussain',
    'nasser', 'naser', 'khalid', 'khaled', 'mansoor', 'mansur', 'saqaf', 'sakaf',
    'sharaf', 'ghaleb', 'taha', 'zayd', 'zaid', 'noman', 'amr', 'mustafa',
    'moustafa', 'almasdar', 'alsahwa', 'aleryani', 'alaswadi', 'sharehi', 'alshami',
    'alkasir', 'mecodify', 'al-saqaf', 'al_saqaf', 'wsaqaf', 'soso', 'fadi',
    'malik', 'tareq', 'tariq', 'yousef', 'youssef', 'yusuf', 'ibrahim', 'ibraheem',
    'sultan', 'osama', 'fadhl', 'fadel', 'nabeel', 'nabil', 'jamal', 'kamal',
    'salem', 'samir', 'sameer', 'anwar', 'walid', 'waleed', 'yasser', 'yasir',
    'ziad', 'zeyad', 'munir', 'muneer', 'marwan', 'hamza', 'bilal', 'badr',
    'basem', 'basim', 'ayman', 'wael', 'ammar', 'sami', 'sameh', 'faris',
    'fares', 'rashid', 'rasheed', 'hakim', 'hakeem', 'hadi', 'majed', 'majid',
    'qasim', 'kasim', 'habib', 'akram', 'mokhtar', 'mukhtar', 'alwan'
]

ARABIC_CHAR_REGEX = re.compile(r'[\u0600-\u06FF]')
COMMON_BUSINESS_KEYWORDS = ['plumbing', 'lawncare', 'heating', 'carpet', 'dentist', 'roofing', 'contractor']


def is_gibberish_username(lp: str) -> bool:
    """Detects random algorithmic string generation in email username."""
    lp_clean = lp.lower().strip()
    
    # 5+ consecutive consonants (e.g., 'ggngvwxrsbrmftc', 'hxfidjyvvj')
    if re.search(r'[bcdfghjklmnpqrstvwxyz]{5,}', lp_clean):
        return True
        
    # Pattern of letters followed by isolated digits followed by letters (e.g. 'tonettema3yc', 'charissejikr')
    if re.search(r'^[a-z]{4,}\d{1,2}[a-z]{2,}$', lp_clean):
        return True
        
    # High numeric density interspersed in random string without a year
    if len(lp_clean) > 8 and sum(c.isdigit() for c in lp_clean) >= 4 and not re.search(r'(19\d\d|20\d\d)$', lp_clean):
        return True
        
    return False


def matches_arabic_name(lp: str) -> bool:
    """Checks if the email local-part contains a recognizable Arabic/Yemeni name component."""
    lp_clean = lp.lower()
    for root in ARABIC_NAME_ROOTS:
        if root in lp_clean:
            return True
    # Standalone 'ali' or 'omar' with boundaries
    if re.search(r'(^|[._\d-])(ali|omar|nour|nour|saad|saed)([._\d-]|$)', lp_clean):
        return True
    return False


def classify_subscribers() -> Dict[str, list]:
    """
    Classifies all registered users into three safety tiers:
    - tier1: Genuine, active, or verified Arabic/Yemeni users (safe for immediate send).
    - tier2: Unconfirmed legacy users (valid domains, but unproven activity).
    - tier3: Confirmed spam bots, defunct domains, scraper lists, and placeholders (to be excluded).
    """
    User = get_user_model()
    voter_ids = set(Vote.objects.values_list('user_id', flat=True))
    suggestor_ids = set(Source.objects.filter(user_id__isnull=False).values_list('user_id', flat=True))

    tier1 = []
    tier2 = []
    tier3 = []

    for u in User.objects.all().order_by('id'):
        email = (u.email or '').strip().lower()
        if not email or '@' not in email:
            tier3.append({
                'user': u,
                'email': email,
                'reason': 'Empty or malformed email'
            })
            continue

        lp, _, domain = email.partition('@')
        first = (u.first_name or '').strip()
        last = (u.last_name or '').strip()
        full_name = f'{first} {last}'.strip()

        # 1. Tier 1 Signals: Active Interaction / Human Name / Staff
        has_activity = (u.id in voter_ids or u.id in suggestor_ids or u.is_staff or u.is_superuser or u.last_login is not None)
        has_arabic_name = bool(ARABIC_CHAR_REGEX.search(full_name))
        has_name = bool(first or last)
        is_arabic_email = matches_arabic_name(lp)

        if has_activity or has_arabic_name or (has_name and is_arabic_email) or (has_name and not is_gibberish_username(lp) and domain in ('gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com')):
            tier1.append({
                'user': u,
                'email': email,
                'full_name': full_name,
                'reason': 'Active interaction / Real name / Verified Arabic profile'
            })
            continue

        # If email itself has a clear Arabic/Yemeni name and is not on dead or spam domains
        if is_arabic_email and domain not in DEAD_DOMAINS and domain not in US_ISP_DOMAINS and not is_gibberish_username(lp):
            tier1.append({
                'user': u,
                'email': email,
                'full_name': full_name,
                'reason': 'Recognized Arabic/Yemeni name root'
            })
            continue

        # 2. Tier 3 Signals: Dead domains, Spambots, Scraper lists
        is_tier3 = False
        reason = ''

        if domain in DEAD_DOMAINS:
            is_tier3 = True
            reason = f'Dead/Unroutable domain ({domain})'
        elif 'datarockets.com' in domain or '_twitter@' in email or '_facebook@' in email or (domain == 'yemenportal.net' and lp not in ('support', 'admin', 'contact')):
            is_tier3 = True
            reason = 'Developer test account or legacy OAuth dummy placeholder'
        elif len(lp) <= 2:
            is_tier3 = True
            reason = f'Placeholder/dummy username ({lp})'
        elif domain in US_ISP_DOMAINS:
            is_tier3 = True
            reason = f'US residential broadband scraper bot ({domain})'
        elif is_gibberish_username(lp):
            is_tier3 = True
            reason = f'Algorithmic bot gibberish string ({lp})'
        elif any(k in lp for k in COMMON_BUSINESS_KEYWORDS):
            is_tier3 = True
            reason = 'US commercial business scraper'

        if is_tier3:
            tier3.append({
                'user': u,
                'email': email,
                'reason': reason
            })
        else:
            # 3. Tier 2: Unconfirmed legacy subscribers
            tier2.append({
                'user': u,
                'email': email,
                'reason': 'Unconfirmed legacy user'
            })

    return {
        'tier1': tier1,
        'tier2': tier2,
        'tier3': tier3,
    }


def sync_tier3_to_optout() -> int:
    """
    Adds all Tier 3 spam/bot/defunct emails to NewsletterOptOut so they are
    permanently and automatically excluded from any mailing or newsletter.
    """
    classified = classify_subscribers()
    tier3_emails = {item['email'] for item in classified['tier3'] if item['email']}
    
    existing = set(NewsletterOptOut.objects.values_list('email', flat=True))
    to_create = [
        NewsletterOptOut(email=e)
        for e in tier3_emails
        if e not in existing
    ]
    
    if to_create:
        NewsletterOptOut.objects.bulk_create(to_create, ignore_conflicts=True)
    return len(to_create)
