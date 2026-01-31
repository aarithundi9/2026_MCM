"""
Instagram Follower Scraper using Selenium (Browser Automation)
More reliable than API libraries - uses headless browser to mimic real user behavior

INSTALLATION REQUIRED:
    pip install selenium webdriver-manager

This approach is harder for Instagram to detect because it uses a real browser.
"""

import pandas as pd
from pathlib import Path
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def load_dwts_celebrities():
    """Load celebrity names from DWTS dataset"""
    DATA_PATH = Path('2026_MCM_Problem_C_Data.csv')
    if not DATA_PATH.exists():
        print(f"ERROR: Cannot find {DATA_PATH}")
        return []
    
    df = pd.read_csv(DATA_PATH)
    celebrities = sorted(df['celebrity_name'].unique().tolist())
    return celebrities


def setup_chrome_driver(headless=True):
    """Setup Chrome WebDriver with stealth options"""
    options = Options()
    
    # Headless mode (no window shown)
    if headless:
        options.add_argument('--headless')
    
    # Anti-detection measures
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Rotate user agents
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    
    # Create driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Execute stealth script
    driver.execute_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
    """)
    
    return driver


def get_follower_count(driver, username, wait_time=10):
    """
    Get follower count from Instagram profile
    
    Args:
        driver: Selenium WebDriver instance
        username: Instagram username (without @)
        wait_time: How long to wait for page to load
    
    Returns:
        tuple (follower_count, is_verified) or (None, None) if not found
    """
    try:
        # Navigate to profile
        url = f"https://www.instagram.com/{username}/"
        driver.get(url)
        
        # Random delay to appear human
        time.sleep(random.uniform(2, 4))
        
        # Wait for page to load - look for follower count
        wait = WebDriverWait(driver, wait_time)
        
        try:
            # Try to find follower count in the page
            # Instagram stores this in meta tags and in the page source
            
            # Method 1: Look for meta tag (og:description)
            try:
                meta_desc = driver.find_element(By.CSS_SELECTOR, "meta[property='og:description']")
                description = meta_desc.get_attribute('content')
                
                # Description format: "123K followers, 456 following"
                if 'followers' in description:
                    followers_str = description.split('followers')[0].strip().split()[-1]
                    followers_count = parse_follower_count(followers_str)
                    
                    # Check if verified
                    is_verified = '✓' in description or 'verified' in description.lower()
                    
                    return followers_count, is_verified
            except:
                pass
            
            # Method 2: Look in page source for follower count
            page_source = driver.page_source
            
            # Look for the follower count pattern in Instagram's page structure
            import re
            
            # Pattern 1: "123,456" or "123K" format
            follower_patterns = [
                r'"edge_followed_by":\{"count":(\d+)',  # GraphQL data
                r'follower_count["\']?\s*[:=]\s*(\d+)',  # Direct assignment
            ]
            
            for pattern in follower_patterns:
                match = re.search(pattern, page_source)
                if match:
                    followers_count = int(match.group(1))
                    is_verified = 'verified' in page_source.lower()
                    return followers_count, is_verified
            
            print(f"    ⚠ Could not parse follower count for @{username}")
            return None, None
            
        except TimeoutException:
            print(f"    ⚠ Timeout waiting for @{username} to load")
            return None, None
        
    except Exception as e:
        print(f"    ⚠ Error accessing @{username}: {str(e)[:50]}")
        return None, None


def parse_follower_count(count_str):
    """
    Parse follower count from string like "123K" or "1.5M"
    
    Args:
        count_str: String representation of follower count
    
    Returns:
        Integer follower count
    """
    count_str = count_str.strip().upper()
    
    try:
        if 'K' in count_str:
            return int(float(count_str.replace('K', '')) * 1000)
        elif 'M' in count_str:
            return int(float(count_str.replace('M', '')) * 1000000)
        else:
            return int(count_str.replace(',', ''))
    except:
        return None


def scrape_instagram_followers(celebrity_names, min_followers=5000, test_mode=False, test_count=5):
    """
    Scrape Instagram follower counts using Selenium
    
    Args:
        celebrity_names: list of celebrity names
        min_followers: minimum follower count threshold
        test_mode: if True, only test on test_count celebrities
        test_count: number of celebrities to test
    
    Returns:
        dict with results
    """
    print("="*80)
    print("INSTAGRAM SCRAPER - SELENIUM (Browser Automation)")
    print("="*80)
    print(f"\nSettings:")
    print(f"  - Minimum follower count: {min_followers:,}")
    print(f"  - Browser: Chrome (headless)")
    print(f"  - Anti-detection: Enabled")
    
    if test_mode:
        sample_names = random.sample(celebrity_names, min(test_count, len(celebrity_names)))
        celebrities_to_search = sample_names
        print(f"  - TEST MODE: {test_count} random celebrities\n")
    else:
        celebrities_to_search = celebrity_names
        print()
    
    # Setup driver
    print("Initializing Chrome WebDriver...")
    driver = setup_chrome_driver(headless=True)
    
    followers_data = {}
    found_count = 0
    not_found_count = 0
    
    try:
        for idx, celebrity_name in enumerate(celebrities_to_search, 1):
            print(f"[{idx:3d}/{len(celebrities_to_search)}] {celebrity_name:35s}", end=" | ", flush=True)
            
            # Generate handle from name
            handle = celebrity_name.lower().replace(" ", "")
            
            # Scrape
            followers_count, is_verified = get_follower_count(driver, handle)
            
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
            
            # Random delay between requests (more human-like)
            time.sleep(random.uniform(3, 6))
    
    finally:
        # Close driver
        driver.quit()
    
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


def save_results(followers_data, output_file='instagram_followers_scraped.csv'):
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
    print("INSTAGRAM SCRAPER - SELENIUM VERSION")
    print("="*80)
    
    # Load celebrities
    print("\nLoading DWTS celebrity list...")
    celebrities = load_dwts_celebrities()
    print(f"✓ Loaded {len(celebrities)} unique celebrities")
    
    # Test mode first
    print("\n" + "="*80)
    print("RUNNING TEST on 5 random celebrities first...")
    print("="*80 + "\n")
    
    test_results = scrape_instagram_followers(
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
        print(f"Estimated time: ~{len(celebrities) * 4.5 / 60:.0f} minutes")
        print("(Please don't interrupt - Instagram may block if session is disrupted)\n")
        
        full_results = scrape_instagram_followers(
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
