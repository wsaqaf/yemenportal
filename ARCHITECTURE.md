# Yemen Portal - Django Architecture

This document describes the modern architecture of the Yemen Portal application, rebuilt with Django, HTMX, and Tailwind CSS.

## 1. Project Organization

The project follows a modular structure where domain logic is separated into apps under the `apps/` directory.

```text
.
├── apps/                   # Custom application logic
│   ├── crawler/            # RSS/Facebook feed fetching
│   ├── moderation/         # Post review and flagging
│   ├── posts/              # Core content (Articles, Categories, Topics)
│   ├── sources/            # News source management
│   └── users/              # Custom User model and authentication
├── config/                 # Project configuration and settings
│   ├── settings/           # Split settings (base, development, production)
│   ├── asgi.py
│   ├── celery.py           # Celery task configuration
│   ├── urls.py             # Root URL routing
│   └── wsgi.py
├── static/                 # Global static files
├── templates/              # Global templates (base, index, etc.)
├── Dockerfile              # Docker build configuration
├── docker-compose.yml      # Orchestration for web, db, redis, and workers
└── requirements.txt        # Python dependencies
```

## 2. Core Technologies

### Backend
- **Django**: The core web framework.
- **PostgreSQL**: The primary relational database.
- **Celery + Redis**: Background tasks for feed crawling and clustering logic.
- **Django-environ**: Configuration via environment variables.

### Frontend
- **HTMX**: For dynamic, server-driven UI interactions (voting, filtering, loading).
- **Tailwind CSS**: Utility-first styling for a custom, modern look.
- **Alpine.js**: For client-side interactivity that doesn't require server round-trips.

## 3. Key Concepts

### Content Ingestion (Crawler)
The `crawler` app handles periodic fetching from RSS and Facebook feeds. Each feed is mapped to a `Source` and converted into `Post` objects.

### Clustering (Posts)
To prevent duplicate content from multiple sources, the `posts` app implements a clustering service. It uses TF-IDF similarity (powered by `scikit-learn`) to group related articles into a single `Topic`.

### Moderation
A multi-tier moderation system allows admins and moderators to review, flag, and categorize incoming posts before they are featured on the main feed.

## 4. Environment Setup

### Docker (Recommended)
```bash
docker-compose up --build
```

### Local Development
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings.development
python manage.py migrate
python manage.py runserver
```
