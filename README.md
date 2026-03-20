# Content Monitoring & Flagging System

Initial Django REST Framework backend scaffold for a content monitoring and flagging system.

## Structure

- `config/`: Django project configuration.
- `content_monitoring/`: Main application containing models, serializers, views, urls, services, and mock scan data.
- `requirements.txt`: Python dependencies.

## Current domain models

- `Keyword`: tracks unique monitoring keywords.
- `ContentItem`: stores monitored content metadata and body text.
- `Flag`: joins a keyword to a content item with a score and review status.

## Services

- `matching_service.py`: keyword scoring logic.
- `suppression_service.py`: handles suppression of irrelevant matches.
- `scan_service.py`: loads the mock JSON dataset, upserts content, runs keyword matching, and prevents duplicate flags.

## API endpoints

- `POST /keywords/`
- `POST /scan/`
- `GET /flags/`
- `PATCH /flags/{id}/`

## Scan behavior

- `POST /scan/` loads `content_monitoring/data/mock_content.json` by default.
- Existing `ContentItem` rows are updated by `source` instead of duplicated.
- Existing `Flag` rows are reused via the `(keyword, content_item)` unique constraint.
- If a flag was marked `irrelevant` and the content has not changed, the scanner skips re-flagging it.
- If the content changes, the scanner allows the flag to be updated and reviewed again.

## Next steps

- Install dependencies with `pip install -r requirements.txt`.
- Run migrations with `python manage.py migrate`.
- Start the server with `python manage.py runserver`.
