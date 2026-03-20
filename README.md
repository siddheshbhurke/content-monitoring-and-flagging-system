# Content Monitoring & Flagging System

A Django REST Framework backend for loading content from a mock JSON feed, matching that content against configured keywords, and surfacing reviewable flags.

## Overview

This project provides a starter backend for a content monitoring workflow with these core capabilities:

- store monitoring keywords
- ingest content from a mock JSON dataset
- score keyword matches against content
- create and update flags for review
- suppress flags that were marked irrelevant until the underlying content changes

## Tech Stack

- Python 3.10+
- Django 5
- Django REST Framework
- SQLite for local development

## Project Structure

```text
.
├── config/                    # Django project configuration
├── content_monitoring/
│   ├── data/                  # Mock dataset used by the scan workflow
│   ├── migrations/            # Django migrations
│   ├── services/              # Business logic layer
│   ├── models.py              # Keyword, ContentItem, Flag
│   ├── serializers.py         # API serializers
│   ├── urls.py                # API routes
│   └── views.py               # Thin API views
├── manage.py
└── requirements.txt
```

## Data Model Summary

### Keyword
Represents a monitored term or phrase.

### ContentItem
Represents a single content record loaded from the dataset.

### Flag
Represents a keyword match on a content item and stores:

- keyword
- content item
- score
- review status (`pending`, `relevant`, `irrelevant`)
- last reviewed timestamp

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd content-monitoring-and-flagging-system
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

> On Windows PowerShell, use `\.venv\Scripts\Activate.ps1` instead.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Create an admin user (optional)

```bash
python manage.py createsuperuser
```

## How to Run the Server

Start the local development server:

```bash
python manage.py runserver
```

By default, the app will be available at:

- API root: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/keywords/` | Create a monitoring keyword |
| `POST` | `/scan/` | Load the mock JSON dataset and run scan logic |
| `GET` | `/flags/` | List all flags |
| `PATCH` | `/flags/{id}/` | Update a flag review status |

## How to Trigger a Scan

The scan endpoint loads `content_monitoring/data/mock_content.json` by default and processes each record in the dataset.

```bash
curl -X POST http://127.0.0.1:8000/scan/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

The response returns a summary similar to:

```json
{
  "content_items_scanned": 2,
  "content_items_created": 2,
  "content_items_updated": 0,
  "flags_created": 1,
  "flags_updated": 0,
  "flags_skipped": 0
}
```

You can also provide a custom dataset path for development/testing purposes:

```bash
curl -X POST http://127.0.0.1:8000/scan/ \
  -H "Content-Type: application/json" \
  -d '{"dataset_path": "/absolute/path/to/mock_content.json"}'
```

## API Examples (curl)

### Create a keyword

```bash
curl -X POST http://127.0.0.1:8000/keywords/ \
  -H "Content-Type: application/json" \
  -d '{"name": "alert"}'
```

Example response:

```json
{
  "id": 1,
  "name": "alert"
}
```

### Trigger a scan

```bash
curl -X POST http://127.0.0.1:8000/scan/ \
  -H "Content-Type: application/json" \
  -d '{}'
```

### List flags

```bash
curl http://127.0.0.1:8000/flags/
```

Example response:

```json
[
  {
    "id": 1,
    "keyword": {
      "id": 1,
      "name": "alert"
    },
    "content_item": 1,
    "score": "2.00",
    "status": "pending",
    "last_reviewed_at": null
  }
]
```

### Mark a flag as irrelevant

```bash
curl -X PATCH http://127.0.0.1:8000/flags/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "irrelevant"}'
```

### Mark a flag as relevant

```bash
curl -X PATCH http://127.0.0.1:8000/flags/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "relevant"}'
```

## Business Rules and Scan Behavior

- Content is loaded from a mock JSON dataset.
- Content records are upserted using `source` as the lookup key.
- Flags are unique per `(keyword, content_item)` pair.
- Duplicate flags are prevented by service-layer upsert logic plus the database constraint.
- If a flag has been reviewed as `irrelevant` and the content has not changed, the scanner skips re-flagging it.
- If the content changes, the scanner may update the existing flag and allow it back into review.
- Keyword scoring is currently based on simple text occurrence counting in the title and body.

## Running Tests

```bash
python manage.py test
```

## Assumptions Made

- The mock dataset is sufficient for this phase and acts as the scan source instead of an external feed or queue.
- `source` uniquely identifies a logical content record during rescans.
- Keyword matching is intentionally simple for now and does not yet use stemming, fuzzy matching, or NLP.
- The scan endpoint is designed for development/demo workflows and can optionally accept a local dataset path override.
- Reviewers update flag status manually through the `PATCH /flags/{id}/` endpoint.
- Local development uses SQLite; production concerns such as authentication, authorization, background jobs, and audit history are not yet implemented.
