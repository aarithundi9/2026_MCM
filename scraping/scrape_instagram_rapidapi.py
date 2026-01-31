"""
Instagram Follower Scraper using RapidAPI (Third-Party Service)
Much more reliable - uses pre-built service that handles Instagram blocking

SETUP REQUIRED:
1. Get free RapidAPI account: https://rapidapi.com/
2. Find "Instagram API" services (many free options)
3. Get your API key
4. Export as environment variable or pass directly

Advantages:
- Pre-built service handles Instagram blocking
- Cached data available
- No personal account at risk
- Higher success rate
"""

import pandas as pd
from pathlib import Path
import requests
import time
import random


def load_dwts_celebrities():
    """Load celebrity names from DWTS dataset"""
    DATA_PATH = Path('2026_MCM_Problem_C_Data.csv')
    if not DATA_PATH.exists():
        print(f"ERROR: Cannot find {DATA_PATH}")
        return []
    
    df = pd.read_csv(DATA_PATH)
    celebrities = sorted(df['celebrity_name'].unique().tolist())
    return celebrities


def scrape_with_rapidapi(celebrity_names, api_key=None, test_mode=False, test_count=5):
    """
    Scrape Instagram followers using RapidAPI
    
    Multiple free/cheap options available:
    1. "instagram-api-with-stories" - free tier
    2. "instagram-api-extended" - free tier  
    3. "instagram-api" - free tier
    
    Args:
        celebrity_names: list of celebrity names
        api_key: RapidAPI key
        test_mode: if True, only test on test_count celebrities
        test_count: number of celebrities to test
    """
    if not api_key:
        print("\n" + "="*80)
        print("RapidAPI SETUP REQUIRED")
        print("="*80)
        print("""
To use this method:

1. Go to: https://rapidapi.com/
2. Sign up (free account)
3. Search for: "instagram api"
4. Choose one (many free options):
   - instagram-api-with-stories (free 5 calls/month)
   - instagram-api-extended (free tier)
   - instagram-api (free tier)
5. Subscribe (free) and copy your API key
6. Run this script with your key:

    python scrape_instagram_rapidapi.py <YOUR_API_KEY>

OR set environment variable:
    $env:RAPIDAPI_KEY = "your_key_here"

ALTERNATIVE - Use built-in Wikipedia/Database approach instead.
        """)
        return None
    
    print("="*80)
    print("INSTAGRAM SCRAPER - RapidAPI")
    print("="*80)
    
    if test_mode:
        sample_names = random.sample(celebrity_names, min(test_count, len(celebrity_names)))
        celebrities_to_search = sample_names
        print(f"\nTEST MODE: {test_count} random celebrities\n")
    else:
        celebrities_to_search = celebrity_names
    
    followers_data = {}
    found_count = 0
    
    for idx, celebrity_name in enumerate(celebrities_to_search, 1):
        print(f"[{idx:3d}/{len(celebrities_to_search)}] {celebrity_name:35s}", end=" | ", flush=True)
        
        # Generate handle
        handle = celebrity_name.lower().replace(" ", "")
        
        try:
            # Make API request
            headers = {
                'x-rapidapi-key': api_key,
                'x-rapidapi-host': 'instagram-api-extended.p.rapidapi.com'  # Example
            }
            
            params = {
                'ig_handle': handle
            }
            
            response = requests.get(
                'https://instagram-api-extended.p.rapidapi.com/user/info',
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'followers' in data:
                    followers_count = data.get('followers', 0)
                    is_verified = data.get('is_verified', False)
                    
                    followers_data[celebrity_name] = {
                        'handle': f"@{handle}",
                        'followers': followers_count,
                        'verified': is_verified,
                        'found': True
                    }
                    found_count += 1
                    
                    verified_badge = "✓" if is_verified else "○"
                    print(f"@{handle:25s} {followers_count:>10,} {verified_badge}")
                else:
                    followers_data[celebrity_name] = {
                        'handle': f"@{handle}",
                        'followers': None,
                        'verified': None,
                        'found': False
                    }
                    print("NOT FOUND")
            else:
                followers_data[celebrity_name] = {
                    'handle': f"@{handle}",
                    'followers': None,
                    'verified': None,
                    'found': False
                }
                print(f"ERROR (HTTP {response.status_code})")
        
        except Exception as e:
            print(f"ERROR: {str(e)[:40]}")
            followers_data[celebrity_name] = {
                'handle': f"@{handle}",
                'followers': None,
                'verified': None,
                'found': False
            }
        
        # Rate limit
        time.sleep(0.5)
    
    # Summary
    print("\n" + "="*80)
    print(f"Found: {found_count}/{len(celebrities_to_search)}")
    print("="*80)
    
    return followers_data


if __name__ == "__main__":
    print("\n" + "="*80)
    print("INSTAGRAM SCRAPER - RapidAPI VERSION")
    print("="*80)
    
    # Check for API key
    import sys
    import os
    
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = os.environ.get('RAPIDAPI_KEY')
    
    if not api_key:
        print("\nNo API key provided. Run with:")
        print("  python scrape_instagram_rapidapi.py YOUR_API_KEY")
        print("\nOr set environment variable:")
        print("  $env:RAPIDAPI_KEY = 'your_key_here'")
        scrape_with_rapidapi([], api_key=None)
    else:
        celebrities = load_dwts_celebrities()
        results = scrape_with_rapidapi(celebrities, api_key=api_key, test_mode=True, test_count=5)
