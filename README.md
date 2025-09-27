<<<<<<< master
# Kinky.nl Web Scraper

A comprehensive web scraper for extracting ad listings and profile information from kinky.nl with automatic pagination handling and media download capabilities.
=======


## Features

- **Pagination Support**: Automatically follows all pagination links to scrape all available pages
- **Profile Extraction**: Extracts detailed information from individual profile pages including:
  - Name and title
  - Description and bio
  - Location information
  - Pricing details
  - Body information (age, height, weight, etc.)
  - Contact information
- **Media Download**: Automatically downloads all photos and videos from profiles
- **Data Storage**: Saves data in both JSON and CSV formats
- **Scheduled Execution**: Runs automatically every hour
- **Logging**: Comprehensive logging for monitoring and debugging

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create necessary directories:
```bash
mkdir -p /workspace/imgs /workspace/vids /workspace/data /workspace/logs
```

## Usage

### Run Once
```bash
python kinky_scraper.py
```

### Run with Scheduler (Recommended)
The scraper is configured to run automatically every hour. Simply run:
```bash
python kinky_scraper.py
```

The script will:
1. Run immediately upon startup
2. Schedule itself to run every hour thereafter
3. Continue running indefinitely

## Output Structure

### Data Files
- **JSON**: `/workspace/data/scraped_data_YYYYMMDD_HHMMSS.json`
- **CSV**: `/workspace/data/scraped_data_YYYYMMDD_HHMMSS.csv`

### Media Files
- **Images**: `/workspace/imgs/{profile_id}/`
- **Videos**: `/workspace/vids/{profile_id}/`

### Logs
- **Log File**: `/workspace/logs/scraper.log`

## Configuration

The scraper includes several configurable options:

- **Base URL**: Default is "https://www.kinky.nl"
- **Request Delays**: Built-in delays to be respectful to the server
- **Retry Logic**: Automatic retry for failed requests
- **User Agent**: Realistic browser user agent string

## Data Structure

Each scraped profile contains:

```json
{
  "url": "profile_url",
  "scraped_at": "timestamp",
  "name": "profile_name",
  "title": "profile_title",
  "description": "profile_description",
  "location": "location_info",
  "date_type": "type_of_dates",
  "price": "pricing_info",
  "body_info": {
    "age": "age",
    "height": "height",
    "weight": "weight",
    "body_type": "body_type",
    "hair": "hair_color",
    "eyes": "eye_color"
  },
  "photos": ["photo_urls"],
  "videos": ["video_urls"],
  "contact_info": {}
}
```

## Important Notes

- The scraper includes respectful delays between requests
- All media files are organized by profile ID for easy management
- The scraper handles various pagination patterns automatically
- Comprehensive error handling and logging
- Data is timestamped for easy tracking

## Legal Considerations

Please ensure you comply with:
- Website terms of service
- Local laws and regulations
- Data protection regulations (GDPR, etc.)
- Respectful scraping practices

## Troubleshooting

Check the log file `/workspace/logs/scraper.log` for detailed information about:
- Scraping progress
- Errors and warnings
- Download status
- Performance metrics
