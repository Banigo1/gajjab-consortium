from django.shortcuts import render
import feedparser
from django.http import JsonResponse
from django.core.cache import cache
from datetime import datetime
import time
import re

from urllib.parse import urljoin

def extract_image_from_entry(entry, feed_url):
    """
    Extract image from RSS entry using multiple methods
    """
    image_url = None
    
    # Method 1: Check for media content (most common)
    if hasattr(entry, 'media_content') and entry.media_content:
        for media in entry.media_content:
            if media.get('type', '').startswith('image/'):
                image_url = media['url']
                break
    
    # Method 2: Check for media thumbnail
    if not image_url and hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
        image_url = entry.media_thumbnail[0]['url']
    
    # Method 3: Check for enclosures
    if not image_url and hasattr(entry, 'enclosures') and entry.enclosures:
        for enclosure in entry.enclosures:
            if enclosure.type.startswith('image/'):
                image_url = enclosure.href
                break
    
    # Method 4: Parse HTML content for images
    if not image_url:
        content = entry.get('content', [{}])
        if content and 'value' in content[0]:
            # Search for img tags in content
            img_match = re.search(r'<img[^>]+src="([^">]+)"', content[0]['value'])
            if img_match:
                image_url = img_match.group(1)
    
    # Method 5: Parse summary/description for images
    if not image_url and entry.get('summary'):
        img_match = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
        if img_match:
            image_url = img_match.group(1)
    
    # Method 6: Check for specific RSS extensions
    if not image_url and hasattr(entry, 'links'):
        for link in entry.links:
            if link.get('type', '').startswith('image/'):
                image_url = link['href']
                break
    
    # Convert relative URLs to absolute
    if image_url and image_url.startswith('/'):
        base_url = '/'.join(feed_url.split('/')[:3])
        image_url = urljoin(base_url, image_url)
    
    return image_url

def get_security_updates():
    """
    Fetch security updates from various Nigerian security RSS feeds
    """
    # Cache the results for 30 minutes to avoid too many requests
    cached_data = cache.get('nigeria_security_updates')
    if cached_data:
        return cached_data
    
    security_updates = []
    
    # List of Nigerian security-related RSS feeds
    rss_feeds = [
         {
            'url': 'https://www.premiumtimesng.com/feed/',  # General feed
            'name': 'Premium Times'
        },
        {
            'url': 'https://www.vanguardngr.com/feed/',
            'name': 'Vanguard'
        },
        {
            'url': 'https://guardian.ng/feed/',
            'name': 'The Guardian'
        },
        {
            'url': 'https://www.channelstv.com/feed/',
            'name': 'Channels TV'
        },
        {
            'url': 'https://www.dailytrust.com/feed/',
            'name': 'Daily Trust'
        },
        {
            'url': 'https://www.thisdaylive.com/index.php/feed/',
            'name': 'This Day'
        },
        # International sources that cover Nigerian security
        {
            'url': 'https://feeds.bbci.co.uk/news/world/africa/rss.xml',
            'name': 'BBC Africa'
        },
        {
            'url': 'https://rss.cnn.com/rss/edition_africa.rss',
            'name': 'CNN Africa'
        }
    ]
    
    for feed_info in rss_feeds:
        feed_url = feed_info['url']
        feed_name = feed_info['name']
        
        try:
            print(f"Fetching from: {feed_url}")
            
            # Add timeout and headers to avoid blocking
            feed = feedparser.parse(feed_url)
            
            if hasattr(feed, 'status') and feed.status != 200:
                print(f"Feed {feed_url} returned status {feed.status}")
                continue
                
            if not feed.entries:
                print(f"No entries found in {feed_url}")
                continue
            
            for entry in feed.entries[:6]:  # Get latest 6 entries from each feed
                try:
                    title = entry.title.lower() if entry.title else ''
                    summary = entry.get('summary', '').lower()
                    description = entry.get('description', '').lower()
                    
                    # Combine all text for keyword search
                    content_text = f"{title} {summary} {description}"
                    
                    # Expanded security keywords for Nigeria
                    security_keywords = [
                        'security', 'logistics', 'transport', 'transportation', 'cargo', 
                        'attack', 'terror', 'boko haram', 'bandits', 'transit', 'trailer'
                        'kidnap', 'abduction', 'violence', 'conflict', 'insecurity',
                        'military', 'police', 'army', 'security forces', 'gunmen',
                        'bomb', 'explosion', 'kill', 'dead', 'casualty', 'shot',
                        'armed', 'attack', 'clash', 'crisis', 'emergency', 'herdsmen',
                        'ipob', 'separatist', 'protest', 'riot', 'unrest', 'shot dead',
                        'terrorism', 'extremist', 'violence', 'bloodshed', 'hostage',
                        'insurgency', 'militant', 'soldier', 'officer', 'checkpoint',
                        'raid', 'arrest', 'weapon', 'ammunition', 'shooting'
                    ]
                    
                    # Check if entry contains security-related keywords
                    if any(keyword in content_text for keyword in security_keywords):
                        # Clean the summary
                        clean_summary = entry.get('summary', '') or entry.get('description', '')
                        if clean_summary:
                            clean_summary = clean_summary[:150] + '...' if len(clean_summary) > 150 else clean_summary
                        else:
                            clean_summary = "Security update from Nigeria..."
                        
                        security_updates.append({
                            'title': entry.title,
                            'link': entry.link,
                            'summary': clean_summary,
                            'published': entry.get('published', entry.get('updated', 'Recent')),
                            'source': feed_name
                        })
                        
                except Exception as e:
                    print(f"Error processing entry from {feed_url}: {e}")
                    continue
                    
            # Small delay between feeds to be respectful
            time.sleep(1)
                    
        except Exception as e:
            print(f"Error parsing feed {feed_url}: {e}")
            continue
    
    # If no security updates found, try to get general news as fallback
    if not security_updates:
        security_updates = get_fallback_updates(rss_feeds)
    
    # Sort by date (newest first) and limit to 15 items
    security_updates.sort(key=lambda x: x.get('published', ''), reverse=True)
    security_updates = security_updates[:15]
    
    # Cache for 30 minutes
    cache.set('nigeria_security_updates', security_updates, 1800)
    
    print(f"Found {len(security_updates)} security updates")
    return security_updates

def get_fallback_updates(rss_feeds):
    """Get general news if no security updates found"""
    fallback_updates = []
    
    for feed_info in rss_feeds[:3]:  # Only try first 3 feeds
        try:
            feed = feedparser.parse(feed_info['url'])
            
            for entry in feed.entries[:3]:
                fallback_updates.append({
                    'title': entry.title,
                    'link': entry.link,
                    'summary': entry.get('summary', 'Latest news from Nigeria...')[:120] + '...',
                    'published': entry.get('published', 'Recent'),
                    'source': feed_info['name']
                })
                
        except Exception as e:
            print(f"Error in fallback for {feed_info['url']}: {e}")
            continue
    
    return fallback_updates

def index_view(request):
    try:
        security_updates = get_security_updates()
    except Exception as e:
        print(f"Error in index_view: {e}")
        security_updates = []
    
    context = {
        'title': 'Home',
        'security_updates': security_updates,
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'updates_count': len(security_updates)
    }
    
    return render(request, 'index.html', context)

def debug_feeds(request):
    """Debug view to test RSS feeds"""
    import feedparser
    
    test_feeds = [
        'https://www.premiumtimesng.com/feed/',
        'https://www.vanguardngr.com/feed/',
        'https://guardian.ng/feed/',
        'https://www.channelstv.com/feed/',
        'https://feeds.bbci.co.uk/news/world/africa/rss.xml',
    ]
    
    results = []
    for feed_url in test_feeds:
        try:
            feed = feedparser.parse(feed_url)
            results.append({
                'url': feed_url,
                'status': getattr(feed, 'status', 'unknown'),
                'entries_count': len(feed.entries) if feed.entries else 0,
                'bozo': feed.bozo,  # Indicates if there was a parsing error
                'bozo_exception': str(feed.bozo_exception) if feed.bozo_exception else None
            })
        except Exception as e:
            results.append({
                'url': feed_url,
                'error': str(e)
            })
    return JsonResponse({'feed_results': results})




def about_view(request):
    return render(request, 'about-us.html', context={'title': 'About Us'})

def services_view(request):
    return render(request, 'services.html', context={'title': 'Services'})

def team_view(request):
    return render(request, 'team.html', context={'title': 'Our Team'})

def contact_view(request):
    return render(request, 'contact.html', context={'title': 'Contact Us'})

def move_cargo(request):
    return render(request, 'move-cargo.html', context={'title': 'Move Cargo'})

def features_view(request):
    return render(request, 'features.html', context={'title': 'Features'})

def track_view(request):
    return render(request, 'track.html', context={'title': 'Track and Trace'})

def track_widget(request):
    return render(request, 'SecurityWidget.html', context={'title': 'Dashboard'})

def location_view(request):
    return render(request, 'location.html', context={'title': 'Location'})

def faq_view(request):
    return render(request, 'faqs.html', context={'title': 'FAQs'})


