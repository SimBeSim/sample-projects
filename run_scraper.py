#!/usr/bin/env python3
"""
Simple runner script for the Kinky.nl scraper
This script provides an easy way to run the scraper with different options
"""

import sys
import argparse
from kinky_scraper import KinkyScraper, run_scheduled_scraper
import schedule
import time

def run_once():
    """Run the scraper once"""
    print("Running scraper once...")
    scraper = KinkyScraper()
    scraper.run_scraper()
    print("Scraping completed!")

def run_scheduled():
    """Run the scraper with hourly scheduling"""
    print("Starting scheduled scraper (runs every hour)...")
    print("Press Ctrl+C to stop")
    
    # Schedule the scraper to run every hour
    schedule.every().hour.do(run_scheduled_scraper)
    
    # Run once immediately
    run_scheduled_scraper()
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")

def main():
    parser = argparse.ArgumentParser(description='Kinky.nl Web Scraper')
    parser.add_argument('--mode', choices=['once', 'scheduled'], default='scheduled',
                       help='Run mode: once (run once) or scheduled (run every hour)')
    
    args = parser.parse_args()
    
    if args.mode == 'once':
        run_once()
    else:
        run_scheduled()

if __name__ == "__main__":
    main()