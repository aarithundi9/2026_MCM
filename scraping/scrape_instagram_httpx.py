"""
Instagram Follower Scraper using HTTPX with Smart Parsing
Mimics real browser requests with proper headers and delays

INSTALLATION:
    pip install httpx beautifulsoup4
"""

import pandas as pd
from pathlib import Path
import httpx
import time
import random
import json
import re
from typing import Dict, Tuple, Optional


def load_dwts_celebrities():
    """Load celebrity names from DWTS dataset"""
    DATA_PATH = Path('2026_MCM_Problem_C_Data.csv')
    if not DATA_PATH.exists():
        print(f"ERROR: Cannot find {DATA_PATH}")
        return []
    
    df = pd.read_csv(DATA_PATH)
    celebrities = sorted(df['celebrity_name'].unique().tolist())
    return celebrities


def get_follower_count_httpx(handle: str, timeout: int = 15) -> Tuple[Optional[int], Optional[bool]]:
    """
    Get follower count by parsing Instagram profile page
    Uses HTTPX with proper headers to mimic real browser
    
    Args:
        handle: Instagram username (without @)
        timeout: Request timeout in seconds
    
    Returns:
        tuple (follower_count, is_verified) or (None, None) if not found
    """
    try:
        # Realistic browser headers
        headers = {
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            ]),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        }
        
        url = f"https://www.instagram.com/{handle}/"
        
        # Use HTTPX client
        with httpx.Client(timeout=timeout, follow_redirects=True, http2=True) as client:
            response = client.get(url, headers=headers)
        
        if response.status_code != 200:
            return None, None
        
        html = response.text
        
        # Pattern 1: Look for shared data (most reliable)
        # Instagram embeds user data in <script> tags
        pattern_1 = r'"edge_followed_by":\{"count":(\d+)'
        match = re.search(pattern_1, html)
        if match:
            followers = int(match.group(1))
            is_verified = '"is_verified":true' in html
            return followers, is_verified
        
        # Pattern 2: Look for follower count in meta description
        pattern_2 = r'<meta property="og:description" content="(.*?followers.*?)"'
        match = re.search(pattern_2, html)
        if match:
            desc = match.group(1)
            # Extract number before "followers"
            num_match = re.search(r'([\d,\.]+)\s*followers', desc)
            if num_match:
                followers_str = num_match.group(1).replace(',', '')
                try:
                    followers = int(float(followers_str))
                    is_verified = '✓' in desc or 'verified' in desc.lower()
                    return followers, is_verified
                except:
                    pass
        
        # Pattern 3: Look in window._sharedData
        pattern_3 = r'window\._sharedData\s*=\s*({.*?});'
        match = re.search(pattern_3, html)
        if match:
            try:
                data_str = match.group(1)
                data = json.loads(data_str)
                
                # Navigate through Instagram's data structure
                if 'entry_data' in data:
                    entry = data['entry_data'].get('ProfilePage', [{}])[0]
                    graphql = entry.get('graphql', {})
                    user = graphql.get('user', {})
                    
                    followers = user.get('edge_followed_by', {}).get('count')
                    is_verified = user.get('is_verified', False)
                    
                    if followers:
                        return followers, is_verified
            except:
                pass
        
        return None, None
    
    except Exception as e:
        return None, None


def scrape_instagram_httpx(celebrity_names, min_followers=5000, test_mode=False, test_count=5):
    """
    Scrape Instagram follower counts using HTTPX
    
    Args:
        celebrity_names: list of celebrity names
        min_followers: minimum follower count threshold
        test_mode: if True, only test on test_count celebrities
        test_count: number of celebrities to test
    
    Returns:
        dict with results
    """
    print("="*80)
    print("INSTAGRAM SCRAPER - HTTPX (Smart Browser Parsing)")
    print("="*80)
    print(f"\nSettings:")
    print(f"  - Minimum follower count: {min_followers:,}")
    print(f"  - Method: HTTPX with smart regex parsing")
    print(f"  - Anti-detection: Rotating user agents, realistic headers")
    
    if test_mode:
        sample_names = random.sample(celebrity_names, min(test_count, len(celebrity_names)))
        celebrities_to_search = sample_names
        print(f"  - TEST MODE: {test_count} random celebrities\n")
    else:
        celebrities_to_search = celebrity_names
        print()
    
    followers_data = {}
    found_count = 0
    not_found_count = 0
    
    for idx, celebrity_name in enumerate(celebrities_to_search, 1):
        print(f"[{idx:3d}/{len(celebrities_to_search)}] {celebrity_name:35s}", end=" | ", flush=True)
        
        # Generate handle from name
        handle = celebrity_name.lower().replace(" ", "")
        
        # Get follower count
        followers_count, is_verified = get_follower_count_httpx(handle)
        
        # Check if meets threshold
        if followers_count and followers_count >= min_followers:
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
                'followers': followers_count,
                'verified': None,
                'found': False
            }
            not_found_count += 1
            if followers_count:
                print(f"@{handle:25s} {followers_count:>10,} (below threshold)")
            else:
                print(f"NOT FOUND")
        
        # Random delay between requests
        time.sleep(random.uniform(2, 4))
    
    # Summary
    print("\n" + "="*80)
    print("SCRAPING SUMMARY:")
    print("="*80)
    print(f"Total searched: {len(celebrities_to_search)}")
    print(f"Found: {found_count}")
    print(f"Not found: {not_found_count}")
    if celebrities_to_search:
        print(f"Success rate: {found_count/len(celebrities_to_search)*100:.1f}%")
    
    if test_mode:
        print(f"\n⚠ TEST MODE - Tested {test_count} random celebrities")
    
    return followers_data


def save_results(followers_data, output_file='instagram_followers_httpx.csv'):
    """Save scraping results to CSV"""
    records = []
    for celebrity_name, data in followers_data.items():
        records.append({
            'celebrity_name': celebrity_name,
            'instagram_handle': data.get('handle'),
            'follower_count': data.get('followers'),
            'verified': data.get('verified'),
            'found': data.get('found', False),
            'collection_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df = pd.DataFrame(records)
    df.to_csv(output_file, index=False)
    print(f"✓ Results saved to: {output_file}")
    return df


# Main workflow
if __name__ == "__main__":
    print("\n" + "="*80)
    print("INSTAGRAM SCRAPER - HTTPX VERSION")
    print("="*80)
    
    # Load celebrities
    print("\nLoading DWTS celebrity list...")
    celebrities = load_dwts_celebrities()
    print(f"✓ Loaded {len(celebrities)} unique celebrities")
    
    # Test mode first
    print("\n" + "="*80)
    print("RUNNING TEST on 5 random celebrities first...")
    print("="*80 + "\n")
    
    test_results = scrape_instagram_httpx(
        celebrities,
        min_followers=5000,
        test_mode=True,
        test_count=5
    )
    
    # Ask to continue
    test_df = pd.DataFrame([
        {'Name': name, 'Handle': data['handle'], 'Followers': data['followers']}
        for name, data in test_results.items() if data['found']
    ])
    
    print(f"\nTest found: {len(test_df)}/5 celebrities")
    
    if len(test_df) > 0:
        print("\nTest results:")
        print(test_df.to_string(index=False))
    
    proceed = input("\n\nRun full scrape on all 408 celebrities? (yes/no): ").strip().lower()
    
    if proceed == 'yes':
        print("\n" + "="*80)
        print("Running FULL SCRAPE...")
        print("="*80 + "\n")
        print(f"Estimated time: ~{len(celebrities) * 3 / 60:.0f} minutes\n")
        
        full_results = scrape_instagram_httpx(
            celebrities,
            min_followers=5000,
            test_mode=False
        )
        
        # Save
        print("\nSaving results...")
        df_final = save_results(full_results)
        
        # Summary
        found = df_final['found'].sum()
        print(f"\n✓ Scraping complete!")
        print(f"  Found: {found}/{len(celebrities)} ({found/len(celebrities)*100:.1f}%)")
    else:
        print("\n⚠ Skipped full scrape. You can run again when ready.")
