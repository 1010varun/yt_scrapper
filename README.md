# YouTube Fetcher

A Django application that fetches the latest YouTube videos for specified search queries and provides a REST API to access them. The application also includes a Streamlit dashboard for visualizing the data.

## Features

- Fetches YouTube videos based on search queries
- Stores videos in a database
- Provides a paginated API for accessing videos
- Multiple API key support with automatic rotation when quota is exceeded
- Streamlit dashboard for viewing and filtering videos

## Setup

### Prerequisites

- Python 3.8+
- Redis
- YouTube API key(s)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/1010varun/fam_yt_scrapper
cd fam_yt_scrapper
```

2. Create a virtual environment and activate it:
```bash
virtualenv venv
source venv/bin/activate 
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root directory with your YouTube API key(s):
```
YOUTUBE_API_KEYS=your_api_key_1,your_api_key_2,your_api_key_3
SEARCH_QUERY=bgmi
SECRET_KEY=fam_yt_scrapper
DEBUG=True
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

### Running the Application

1. Start Redis:
```bash
redis-server
```

2. Run the Django development server:
```bash
python manage.py runserver
```

3. In a separate terminal, run Celery worker:
```bash
celery -A youtube_fetcher worker --loglevel=info
```

4. In another terminal, run Celery beat:
```bash
celery -A youtube_fetcher beat --loglevel=info
```

5. Start the Streamlit dashboard:
```bash
streamlit run dashboard.py
```

## Usage

- Access the API at `http://localhost:8000/api/videos` with optional query parameter `q` to specify the search query
- Access the Django admin at `http://localhost:8000/admin`
- Access the Streamlit dashboard at `http://localhost:8501`

## API Documentation

### GET /api/videos

Returns a paginated list of videos.

Query parameters:
- `q`: Search query (default: value from SEARCH_QUERY setting)
- `page`: Page number (default: 1)
- `page_size`: Number of videos per page (default: 10, max: 100)

Example response:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/videos?page=2",
  "previous": null,
  "results": [
    {
      "video_id": "abc123",
      "title": "Sample Video",
      "description": "This is a sample video description.",
      "published_at": "2023-03-15T12:00:00Z",
      "thumbnail_url": "https://example.com/thumbnail.jpg",
      "search_query": "bgmi"
    },
    ...
  ]
}
```
