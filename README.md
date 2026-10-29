# Yemen Portal (بوابة اليمن الإخبارية)

A high-performance news aggregator covering Yemen and regional affairs, powered by Django 5, PostgreSQL, Redis, and Docker.

## Tech Stack
- **Backend:** Python 3.12+, Django 5
- **Database:** PostgreSQL with full-text search and caching
- **Proxy & Web Server:** Nginx, Gunicorn
- **Containerization:** Docker Compose
- **Tracking & Analytics:** Google Analytics 4 (`G-DC6EV81706`)

## Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md) for full system architecture, model relations, and caching strategies.

## Local Development
1. Ensure Docker Desktop or OrbStack is running.
2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
3. Start the application:
   ```bash
   docker compose up -d
   ```
4. Access the site locally at `http://localhost:8000`.

## Production Deployment
Production runs on Ubuntu 22.04 LTS behind Nginx with automatic SSL management via Certbot.
