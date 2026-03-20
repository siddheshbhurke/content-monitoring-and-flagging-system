# Content Monitoring & Flagging System

Initial Django REST Framework backend scaffold for a content monitoring and flagging system.

## Structure

- `config/`: Django project configuration.
- `content_monitoring/`: Main application containing models, serializers, views, urls, and services.
- `requirements.txt`: Python dependencies.

## Current domain models

- `Keyword`: tracks unique monitoring keywords.
- `ContentItem`: stores monitored content metadata and body text.
- `Flag`: joins a keyword to a content item with a score and review status.

## Services

- `matching_service.py`: keyword scoring logic.
- `suppression_service.py`: handles suppression of irrelevant matches.
- `scan_service.py`: coordinates the scanning workflow for new content items.

## Next steps

- Install dependencies with `pip install -r requirements.txt`.
- Run migrations with `python manage.py migrate`.
- Start the server with `python manage.py runserver`.
