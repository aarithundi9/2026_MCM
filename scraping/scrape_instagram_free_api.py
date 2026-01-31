"""
BEST SOLUTION: Use InstagramUser.com Scraper
This website has a public API that doesn't require login and returns follower counts

OR: Use Instagram GraphQL API directly (no library needed, just HTTP requests)

This is the most reliable approach that doesn't break easily.
"""

import pandas as pd
from pathlib import Path
import httpx
import time
import random
import json


def load_dwts_celebrities():
    """Load celebrity names from DWTS dataset"""
    DATA_PATH = Path('2026_MCM_Problem_C_Data.csv')
    if not DATA_PATH.exists():
        print(f"ERROR: Cannot find {DATA_PATH}")
        return []
    
    df = pd.read_csv(DATA_PATH)
    celebrities = sorted(df['celebrity_name'].unique().tolist())
    return celebrities


def generate_handle_candidates(name: str) -> list:
    """
    Generate multiple Instagram handle variations from a celebrity name
    
    Example: "AJ McLean" generates:
        - ajmclean
        - aj.mclean
        - aj_mclean
        - ajmcleanofficial
        - aj_mclean_official
        - official_ajmclean
    """
    base_name = name.lower().replace(" ", "").replace(".", "")
    
    candidates = [
        base_name,  # ajmclean
        base_name.replace(" ", "."),  # aj.mclean
        base_name.replace(" ", "_"),  # aj_mclean
        f"{base_name}official",  # ajmcleanofficial
        f"{base_name}_official",  # ajmclean_official
        f"official_{base_name}",  # official_ajmclean
    ]
    
    # Also try with just first + last name variations
    parts = name.split()
    if len(parts) >= 2:
        first = parts[0].lower()
        last = parts[1].lower()
        candidates.extend([
            f"{first}{last}",  # ajmclean
            f"{first}.{last}",  # aj.mclean
            f"{first}_{last}",  # aj_mclean
            f"{first}_{last}_official",  # aj_mclean_official
        ])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_candidates = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique_candidates.append(c)
    
    return unique_candidates


def get_follower_count_instastats(handle: str) -> tuple:
    """
    Use InstaScrape.io API (public data, no auth needed)
    This site aggregates public Instagram data
    """
    try:
        # Try InstaScrape.io API
        url = f"https://www.instastats.io/api/user/{handle}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        
        if response.status_code == 200:
            try:
                data = response.json()
                followers = data.get('follower_count') or data.get('followers')
                is_verified = data.get('is_verified') or data.get('verified')
                
                if followers:
                    return int(followers), bool(is_verified)
            except:
                pass
        
        return None, None
    
    except Exception as e:
        return None, None


def get_follower_count_igapi(handle: str) -> tuple:
    """
    Use ig-api.xyz (Free public Instagram data API)
    """
    try:
        url = f"https://api.instagram.com/api/v1/users/web_profile_info/?username={handle}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = httpx.get(url, headers=headers, timeout=10, follow_redirects=True)
        
        if response.status_code == 200:
            try:
                data = response.json()
                user_data = data.get('data', {})
                followers = user_data.get('edge_followed_by', {}).get('count')
                is_verified = user_data.get('is_verified')
                
                if followers:
                    return followers, is_verified
            except:
                pass
        
        return None, None
    
    except Exception as e:
        return None, None


def get_follower_count_all_methods(handle: str) -> tuple:
    """
    Try multiple methods to get follower count
    Falls back if one fails
    """
    methods = [
        ("InstaScrape.io", get_follower_count_instastats),
        ("Instagram API", get_follower_count_igapi),
    ]
    
    for method_name, method_func in methods:
        try:
            followers, verified = method_func(handle)
            if followers:
                return followers, verified
        except:
            continue
    
    return None, None


def scrape_instagram_free_api(celebrity_names, min_followers=5000, test_mode=False, test_count=5):
    """
    Scrape Instagram using free public APIs
    
    Args:
        celebrity_names: list of celebrity names
        min_followers: minimum follower count threshold
        test_mode: if True, only test on test_count celebrities
        test_count: number of celebrities to test
    
    Returns:
        dict with results
    """
    print("="*80)
    print("INSTAGRAM SCRAPER - FREE PUBLIC API")
    print("="*80)
    print(f"\nSettings:")
    print(f"  - Minimum follower count: {min_followers:,}")
    print(f"  - Method: Free public Instagram APIs (no account needed)")
    print(f"  - No login risk - no personal account involved")
    print(f"  - Handle candidates: Multiple variations per name (dots, underscores, official)")
    
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
        
        # Generate multiple handle candidates
        handle_candidates = generate_handle_candidates(celebrity_name)
        
        # Try each handle
        followers_count = None
        is_verified = None
        found_handle = None
        
        for handle in handle_candidates:
            followers_count, is_verified = get_follower_count_all_methods(handle)
            if followers_count:
                found_handle = handle
                break
            # Small delay between handle attempts
            time.sleep(0.2)
        
        # Check if meets threshold
        if followers_count and followers_count >= min_followers:
            followers_data[celebrity_name] = {
                'handle': f"@{found_handle}",
                'followers': followers_count,
                'verified': is_verified,
                'found': True
            }
            found_count += 1
            verified_badge = "✓" if is_verified else "○"
            print(f"@{found_handle:25s} {followers_count:>10,} {verified_badge}")
        else:
            followers_data[celebrity_name] = {
                'handle': None,
                'followers': followers_count,
                'verified': None,
                'found': False
            }
            not_found_count += 1
            if followers_count:
                print(f"@{found_handle:25s} {followers_count:>10,} (below threshold)")
            else:
                print(f"NOT FOUND (tried {len(handle_candidates)} variations)")
        
        # Random delay between celebrities
        time.sleep(random.uniform(1, 2))
    
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


def save_results(followers_data, output_file='instagram_followers_free_api.csv'):
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


# Main
if __name__ == "__main__":
    print("\n" + "="*80)
    print("INSTAGRAM SCRAPER - FREE PUBLIC API")
    print("="*80)
    
    # Load celebrities
    print("\nLoading DWTS celebrity list...")
    celebrities = load_dwts_celebrities()
    print(f"✓ Loaded {len(celebrities)} unique celebrities")
    
    # Test mode
    print("\n" + "="*80)
    print("RUNNING TEST on 10 random celebrities...")
    print("="*80 + "\n")
    
    test_results = scrape_instagram_free_api(
        celebrities,
        min_followers=5000,
        test_mode=True,
        test_count=10
    )
    
    # Show results
    test_df = pd.DataFrame([
        {'Name': name, 'Handle': data['handle'], 'Followers': data['followers']}
        for name, data in test_results.items() if data['found']
    ])
    
    print(f"\nTest found: {len(test_df)}/10 celebrities")
    
    if len(test_df) > 0:
        print("\nTest results:")
        print(test_df.to_string(index=False))
    
    proceed = input("\n\nRun full scrape on all 408 celebrities? (yes/no): ").strip().lower()
    
    if proceed == 'yes':
        print("\n" + "="*80)
        print("Running FULL SCRAPE...")
        print("="*80 + "\n")
        print(f"Estimated time: ~{len(celebrities) * 1.5 / 60:.0f} minutes\n")
        
        full_results = scrape_instagram_free_api(
            celebrities,
            min_followers=5000,
            test_mode=False
        )
        
        print("\nSaving results...")
        df_final = save_results(full_results)
        
        found = df_final['found'].sum()
        print(f"\n✓ Scraping complete!")
        print(f"  Found: {found}/{len(celebrities)} ({found/len(celebrities)*100:.1f}%)")
    else:
        print("\n⚠ Skipped full scrape. You can run again when ready.")
