#!/usr/bin/env python3
"""
Kinky.nl Web Scraper
Scrapes ads from kinky.nl with pagination support and profile details
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import os
import time
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import logging
from pathlib import Path
import schedule
import threading
from typing import List, Dict, Optional
import hashlib

class KinkyScraper:
    def __init__(self, base_url: str = "https://www.kinky.nl"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Create directories
        self.setup_directories()
        
        # Setup logging
        self.setup_logging()
        
        # Data storage
        self.scraped_data = []
        
    def setup_directories(self):
        """Create necessary directories for storing data"""
        directories = ['/workspace/imgs', '/workspace/vids', '/workspace/data', '/workspace/logs']
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/workspace/logs/scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch a page with retry logic"""
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
                    
    def extract_pagination_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract pagination links from the current page"""
        pagination_links = []
        
        # Look for common pagination patterns
        pagination_selectors = [
            'a[href*="page="]',
            'a[href*="p="]',
            '.pagination a',
            '.pager a',
            '.page-numbers a',
            'a.next',
            'a.prev'
        ]
        
        for selector in pagination_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(current_url, href)
                    if full_url not in pagination_links and full_url != current_url:
                        pagination_links.append(full_url)
        
        # Also look for numbered pagination
        page_numbers = soup.find_all('a', href=re.compile(r'page=\d+|p=\d+'))
        for link in page_numbers:
            href = link.get('href')
            if href:
                full_url = urljoin(current_url, href)
                if full_url not in pagination_links:
                    pagination_links.append(full_url)
                    
        return pagination_links
        
    def extract_ad_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract individual ad links from the listing page"""
        ad_links = []
        
        # Common selectors for ad links
        ad_selectors = [
            'a[href*="/profiel/"]',
            'a[href*="/advertentie/"]',
            'a[href*="/vrouw/"]',
            '.ad-link',
            '.profile-link',
            'a.profile'
        ]
        
        for selector in ad_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin(current_url, href)
                    if full_url not in ad_links:
                        ad_links.append(full_url)
                        
        return ad_links
        
    def extract_profile_data(self, soup: BeautifulSoup, profile_url: str) -> Dict:
        """Extract detailed information from a profile page"""
        profile_data = {
            'url': profile_url,
            'scraped_at': datetime.now().isoformat(),
            'name': '',
            'title': '',
            'description': '',
            'location': '',
            'date_type': '',
            'price': '',
            'body_info': {},
            'photos': [],
            'videos': [],
            'contact_info': {}
        }
        
        try:
            # Extract name/title
            name_selectors = ['h1', '.profile-name', '.name', '.title']
            for selector in name_selectors:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    profile_data['name'] = element.get_text(strip=True)
                    break
                    
            # Extract description
            desc_selectors = ['.description', '.profile-text', '.content', '.bio']
            for selector in desc_selectors:
                element = soup.select_one(selector)
                if element:
                    profile_data['description'] = element.get_text(strip=True)
                    break
                    
            # Extract location
            location_selectors = ['.location', '.city', '.region', '[class*="location"]']
            for selector in location_selectors:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    profile_data['location'] = element.get_text(strip=True)
                    break
                    
            # Extract price information
            price_selectors = ['.price', '.rate', '.cost', '[class*="price"]']
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    profile_data['price'] = element.get_text(strip=True)
                    break
                    
            # Extract body information
            body_info = {}
            body_selectors = {
                'age': ['.age', '[class*="age"]'],
                'height': ['.height', '[class*="height"]'],
                'weight': ['.weight', '[class*="weight"]'],
                'body_type': ['.body-type', '[class*="body"]'],
                'hair': ['.hair', '[class*="hair"]'],
                'eyes': ['.eyes', '[class*="eye"]']
            }
            
            for field, selectors in body_info.items():
                for selector in selectors:
                    element = soup.select_one(selector)
                    if element and element.get_text(strip=True):
                        body_info[field] = element.get_text(strip=True)
                        break
                        
            profile_data['body_info'] = body_info
            
            # Extract media links
            media_links = self.extract_media_links(soup)
            profile_data['photos'] = media_links['photos']
            profile_data['videos'] = media_links['videos']
            
            # Download media files
            self.download_media(profile_data['photos'], profile_data['videos'], profile_url)
            
        except Exception as e:
            self.logger.error(f"Error extracting profile data from {profile_url}: {e}")
            
        return profile_data
        
    def extract_media_links(self, soup: BeautifulSoup) -> Dict:
        """Extract photo and video links from profile page"""
        photos = []
        videos = []
        
        # Extract image links
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src') or img.get('data-src')
            if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                photos.append(src)
                
        # Extract video links
        video_tags = soup.find_all('video')
        for video in video_tags:
            src = video.get('src')
            if src:
                videos.append(src)
                
        # Look for video links in other elements
        video_links = soup.find_all('a', href=re.compile(r'\.(mp4|avi|mov|wmv|flv|webm)', re.I))
        for link in video_links:
            href = link.get('href')
            if href:
                videos.append(href)
                
        return {'photos': photos, 'videos': videos}
        
    def download_media(self, photos: List[str], videos: List[str], profile_url: str):
        """Download photos and videos to respective folders"""
        # Create profile-specific folders
        profile_id = hashlib.md5(profile_url.encode()).hexdigest()[:8]
        img_folder = f"/workspace/imgs/{profile_id}"
        vid_folder = f"/workspace/vids/{profile_id}"
        
        Path(img_folder).mkdir(parents=True, exist_ok=True)
        Path(vid_folder).mkdir(parents=True, exist_ok=True)
        
        # Download photos
        for i, photo_url in enumerate(photos):
            try:
                if not photo_url.startswith('http'):
                    photo_url = urljoin(profile_url, photo_url)
                    
                response = self.session.get(photo_url, timeout=30)
                if response.status_code == 200:
                    filename = f"photo_{i+1}_{os.path.basename(urlparse(photo_url).path)}"
                    filepath = os.path.join(img_folder, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    self.logger.info(f"Downloaded photo: {filename}")
                    
            except Exception as e:
                self.logger.error(f"Error downloading photo {photo_url}: {e}")
                
        # Download videos
        for i, video_url in enumerate(videos):
            try:
                if not video_url.startswith('http'):
                    video_url = urljoin(profile_url, video_url)
                    
                response = self.session.get(video_url, timeout=60)
                if response.status_code == 200:
                    filename = f"video_{i+1}_{os.path.basename(urlparse(video_url).path)}"
                    filepath = os.path.join(vid_folder, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    self.logger.info(f"Downloaded video: {filename}")
                    
            except Exception as e:
                self.logger.error(f"Error downloading video {video_url}: {e}")
                
    def scrape_all_pages(self, start_url: str):
        """Main scraping function that handles pagination and profile extraction"""
        self.logger.info(f"Starting scrape from: {start_url}")
        
        visited_pages = set()
        pages_to_visit = [start_url]
        all_ad_links = set()
        
        # Scrape all listing pages
        while pages_to_visit:
            current_url = pages_to_visit.pop(0)
            
            if current_url in visited_pages:
                continue
                
            self.logger.info(f"Scraping page: {current_url}")
            soup = self.get_page(current_url)
            
            if not soup:
                continue
                
            visited_pages.add(current_url)
            
            # Extract ad links from current page
            ad_links = self.extract_ad_links(soup, current_url)
            all_ad_links.update(ad_links)
            
            # Extract pagination links
            pagination_links = self.extract_pagination_links(soup, current_url)
            for link in pagination_links:
                if link not in visited_pages and link not in pages_to_visit:
                    pages_to_visit.append(link)
                    
            # Be respectful with requests
            time.sleep(2)
            
        self.logger.info(f"Found {len(all_ad_links)} total ad links")
        
        # Scrape individual profiles
        for i, ad_url in enumerate(all_ad_links, 1):
            self.logger.info(f"Scraping profile {i}/{len(all_ad_links)}: {ad_url}")
            
            soup = self.get_page(ad_url)
            if soup:
                profile_data = self.extract_profile_data(soup, ad_url)
                self.scraped_data.append(profile_data)
                
            # Be respectful with requests
            time.sleep(3)
            
        # Save data
        self.save_data()
        
    def save_data(self):
        """Save scraped data to JSON and CSV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = f"/workspace/data/scraped_data_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
            
        # Save as CSV
        if self.scraped_data:
            csv_file = f"/workspace/data/scraped_data_{timestamp}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.scraped_data[0].keys())
                writer.writeheader()
                writer.writerows(self.scraped_data)
                
        self.logger.info(f"Data saved to {json_file} and {csv_file}")
        
    def run_scraper(self):
        """Run the scraper"""
        start_url = "https://www.kinky.nl/vrouwen/neuken-zonder-condoom"
        self.scrape_all_pages(start_url)

def run_scheduled_scraper():
    """Function to run the scraper on schedule"""
    scraper = KinkyScraper()
    scraper.run_scraper()

def main():
    """Main function to set up and run the scraper"""
    # Schedule the scraper to run every hour
    schedule.every().hour.do(run_scheduled_scraper)
    
    # Run once immediately
    run_scheduled_scraper()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()