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

# 3. Known Arabic / Yemeni names, family roots, and regions
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
    'qasim', 'kasim', 'habib', 'akram', 'mokhtar', 'mukhtar', 'alwan',
    'batheeb', 'aulaqi', 'ulaqi', 'sabaei', 'hanbse', 'karar', 'rahaal', 'alhadad',
    'haddad', 'ansari', 'zubairi', 'shami', 'jarash', 'mutawakil', 'alwazir',
    'matar', 'khawlani', 'hamdani', 'ansi', 'dhamari', 'mahweet', 'lahji', 'abyani',
    'hadhrami', 'hadramout', 'shabwani', 'mahri', 'socotra', 'alhaimi', 'barak',
    'barakat', 'marwani', 'sharaf', 'shurafi', 'khateeb', 'khatib', 'sabahi',
    'maswari', 'sayani', 'qershi', 'qurashi', 'sharabi', 'sabri', 'suwaidi',
    'qubati', 'hujari', 'zabeedi', 'tuhaita', 'hodeidah', 'marib', 'jawf',
    'saada', 'amran', 'hajjah', 'raymah', 'dhalie', 'bayda', 'mukalla', 'shihr',
    'sayun', 'tarim', 'ghaydah', 'ataq', 'zinjibar', 'mokha',
    'suhaib', 'sohaib', 'khuzam', 'qubati', 'barh', 'yafei', 'yousefi', 'yousifi',
    'kawkabani', 'harazi', 'manakhi', 'arhabi', 'hashidi', 'bakili', 'radfani',
    'yemen', 'yamani', 'yemeni', 'bilqis', 'balqis', 'arwa', 'safaa', 'marwa',
    'khadija', 'aisha', 'fatima', 'fatma', 'zainab', 'asma', 'shaimaa', 'shimaa',
    'samira', 'salwa', 'naglaa', 'nagat', 'najwa', 'nawal', 'amal', 'iman',
    'eman', 'wafa', 'wafaa', 'bushra', 'bushrah', 'reem', 'rim', 'rana',
    'ranya', 'rania', 'huda', 'houda', 'nada', 'maram', 'marwah', 'abeer',
    'abir', 'siham', 'seham', 'manal', 'dalal', 'faten', 'fatin', 'soha',
    'suha', 'maha', 'mona', 'muna', 'ghada', 'ghadah', 'hala', 'hannah',
    'rayan', 'abseim', 'hatim', 'soltan', 'asobhy', 'nashwan', 'alsahwa',
    'shohra', 'almuhtadi', 'baeshen', 'ba-eshen', 'alashwal', 'ashwal',
    'alsharif', 'sharif', 'alwosabi', 'wosabi', 'wasabi', 'al-wasabi',
    'alghamdi', 'ghamdi', 'alharbi', 'harbi', 'otaibi', 'dosari', 'shehri',
    'qarni', 'amri', 'zahrani', 'omari', 'mutairi', 'subaie', 'qahtani',
    'hazmi', 'sulami', 'rowaishan', 'alrowaishan', 'ruwaishan', 'al-ruwaishan',
    'tagheer', 'tihama', 'azizalialslwi', 'shihabi', 'slwi', 'alimi', 'al-alimi'
]

TRUSTED_DOMAINS = {
    'internews.eu', 'mecodify.org', 'yemenportal.net', 'yementimes.com',
    'alkasir.com', 'yodet.org', 'sh.se'
}

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

        # 1. Tier 1 Signals: Active Interaction / Human Name / Staff / Trusted Domain / Arabic Identity
        has_activity = (u.id in voter_ids or u.id in suggestor_ids or u.is_staff or u.is_superuser or u.last_login is not None)
        has_arabic_name = bool(ARABIC_CHAR_REGEX.search(full_name))
        has_name = bool(first or last)
        is_arabic_email = matches_arabic_name(lp) or matches_arabic_name(full_name)
        is_trusted_domain = (domain in TRUSTED_DOMAINS or domain.endswith('.ye'))

        if has_activity or has_arabic_name or has_name or is_trusted_domain or is_arabic_email:
            tier1.append({
                'user': u,
                'email': email,
                'full_name': full_name,
                'reason': 'Genuine subscriber (Active / Real Name / Verified Arabic Profile / Trusted Domain)'
            })
            continue

        # 2. Tier 3: All inactive legacy bot accounts without names or activity
        reason = 'Automated legacy spam bot / inactive unverified account'
        if domain in DEAD_DOMAINS:
            reason = f'Dead/Unroutable domain ({domain})'
        elif domain in US_ISP_DOMAINS:
            reason = f'US residential broadband scraper bot ({domain})'
        elif is_gibberish_username(lp):
            reason = f'Algorithmic bot gibberish string ({lp})'
        elif any(k in lp for k in COMMON_BUSINESS_KEYWORDS):
            reason = 'US commercial business scraper'

        tier3.append({
            'user': u,
            'email': email,
            'reason': reason
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


def purge_tier3_accounts() -> Tuple[int, int]:
    """
    Permanently deletes all Tier 3 spam bot User and EmailAddress records
    from the database.
    """
    from allauth.account.models import EmailAddress
    User = get_user_model()
    classified = classify_subscribers()
    tier3_user_ids = [item['user'].id for item in classified['tier3'] if item['user'] and item['user'].id]
    tier3_emails = {item['email'].lower() for item in classified['tier3'] if item['email']}

    # First add them to optout as a safety record so they never re-enter
    sync_tier3_to_optout()

    # 1. Delete associated EmailAddress records by user_id and email
    ea_deleted, _ = EmailAddress.objects.filter(user_id__in=tier3_user_ids).delete()
    ea_extra, _ = EmailAddress.objects.filter(email__in=tier3_emails).delete()
    total_ea_deleted = ea_deleted + ea_extra

    # 2. Delete the User records
    u_deleted, _ = User.objects.filter(id__in=tier3_user_ids).delete()

    # 3. Clean up any orphan EmailAddress records
    orphan_deleted, _ = EmailAddress.objects.exclude(user__in=User.objects.all()).delete()
    total_ea_deleted += orphan_deleted

    return total_ea_deleted, u_deleted
