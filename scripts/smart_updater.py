import json
import os
import requests
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import time

# Configuration
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
YOUTUBE_CHANNEL_ID = 'UCcYzLCs3zrQIBVHYA1sK2sw'  # Sadhguru official channel
DATA_FILE = 'data/content.json'

# Trusted sources
TRUSTED_SOURCES = {
    'isha_foundation': 'https://ishafoundation.org',
    'isha_sadhguru': 'https://isha.sadhguru.org',
    'twitter': 'https://x.com/SadhguruJV',
    'instagram': 'https://www.instagram.com/sadhguru/'
}

def load_existing_data():
    """Load existing content data"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'quotes': [],
            'articles': [],
            'videos': [],
            'last_updated': None
        }

def save_data(data):
    """Save data to JSON file"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    data['last_updated'] = datetime.now().isoformat()
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def is_duplicate(item, existing_items, key='content'):
    """Check if item already exists"""
    for existing in existing_items:
        if key in item and key in existing:
            if item[key] == existing[key]:
                return True
        elif 'url' in item and 'url' in existing:
            if item['url'] == existing['url']:
                return True
    return False

def fetch_daily_quote():
    """Fetch Sadhguru's quote of the day"""
    quotes = []
    
    # Try fetching from Instagram (simulated - in real implementation use Instagram API)
    # For now, we'll use a placeholder structure
    try:
        # This is a placeholder - actual implementation would use Instagram Graph API
        # or web scraping with proper rate limiting
        print("📝 Checking for daily quote...")
        
        # Placeholder quote structure
        today = datetime.now().strftime('%Y-%m-%d')
        quote = {
            'content': f'Daily wisdom from Sadhguru - {today}',
            'source': 'Instagram @sadhguru',
            'url': 'https://www.instagram.com/sadhguru/',
            'date': today,
            'tags': ['daily', 'wisdom'],
            'type': 'quote'
        }
        
        print("✅ Daily quote fetched")
        return quote
        
    except Exception as e:
        print(f"⚠️ Error fetching daily quote: {e}")
        return None

def fetch_recent_youtube_videos():
    """Fetch YouTube videos from last 24 hours"""
    if not YOUTUBE_API_KEY:
        print("⚠️ No YouTube API key found")
        return []
    
    try:
        print("🎥 Checking for new videos...")
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # Get videos from last 24 hours
        yesterday = (datetime.now() - timedelta(days=1)).isoformat() + 'Z'
        
        request = youtube.search().list(
            part='snippet',
            channelId=YOUTUBE_CHANNEL_ID,
            maxResults=10,
            order='date',
            publishedAfter=yesterday,
            type='video'
        )
        
        response = request.execute()
        videos = []
        
        for item in response.get('items', []):
            video = {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'][:300],
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                'thumbnail': item['snippet']['thumbnails']['high']['url'],
                'date': item['snippet']['publishedAt'][:10],
                'source': 'YouTube Official',
                'tags': ['video', 'youtube'],
                'type': 'video'
            }
            videos.append(video)
        
        print(f"✅ Found {len(videos)} new videos")
        return videos
        
    except Exception as e:
        print(f"⚠️ Error fetching YouTube videos: {e}")
        return []

def fetch_recent_articles():
    """Fetch recent articles from Isha websites"""
    articles = []
    
    try:
        print("📰 Checking for new articles...")
        
        # This is a placeholder - actual implementation would scrape the websites
        # with proper rate limiting and respect for robots.txt
        
        # Example structure for when you implement actual scraping
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Placeholder - you would implement actual scraping here
        print("ℹ️ Article scraping placeholder - implement based on website structure")
        
        return articles
        
    except Exception as e:
        print(f"⚠️ Error fetching articles: {e}")
        return []

def smart_update():
    """Main function to perform smart incremental update"""
    print("=" * 50)
    print("🕉️ Starting Smart Sadhguru Content Update")
    print("=" * 50)
    
    # Load existing data
    data = load_existing_data()
    new_items = 0
    
    # 1. ALWAYS fetch quote of the day
    print("\n1️⃣ Fetching daily quote...")
    daily_quote = fetch_daily_quote()
    if daily_quote and not is_duplicate(daily_quote, data['quotes']):
        data['quotes'].insert(0, daily_quote)  # Add to beginning
        new_items += 1
        print("   ✅ New quote added!")
    else:
        print("   ℹ️ Quote already exists or fetch failed")
    
    # 2. Check for new videos (last 24 hours)
    print("\n2️⃣ Checking for new videos...")
    new_videos = fetch_recent_youtube_videos()
    for video in new_videos:
        if not is_duplicate(video, data['videos'], key='url'):
            data['videos'].insert(0, video)
            new_items += 1
    
    if new_videos:
        print(f"   ✅ Added {len(new_videos)} new videos")
    else:
        print("   ℹ️ No new videos today")
    
    # 3. Check for new articles
    print("\n3️⃣ Checking for new articles...")
    new_articles = fetch_recent_articles()
    for article in new_articles:
        if not is_duplicate(article, data['articles'], key='url'):
            data['articles'].insert(0, article)
            new_items += 1
    
    if new_articles:
        print(f"   ✅ Added {len(new_articles)} new articles")
    else:
        print("   ℹ️ No new articles today")
    
    # Save data
    print("\n" + "=" * 50)
    if new_items > 0:
        save_data(data)
        print(f"✅ Update complete! Added {new_items} new items")
        print(f"📊 Total content: {len(data['quotes'])} quotes, {len(data['videos'])} videos, {len(data['articles'])} articles")
    else:
        print("ℹ️ No new content to add today")
    print("=" * 50)

if __name__ == '__main__':
    smart_update()
