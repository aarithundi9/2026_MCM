"""
Instagram Follower Data Collection Script
Uses the unofficial Instagram API (instagrapi) to collect follower counts for DWTS celebrities

INSTALLATION REQUIRED:
    pip install instagrapi

This script automatically loads celebrities from the DWTS data and attempts to find them on Instagram.
"""

import pandas as pd
import requests
from pathlib import Path
import time
import json
from instagrapi import Client
from instagrapi.exceptions import UserNotFound

# Load DWTS data and get unique celebrities
def load_dwts_celebrities():
    """Load celebrity names from DWTS dataset"""
    DATA_PATH = Path('2026_MCM_Problem_C_Data.csv')
    if not DATA_PATH.exists():
        print(f"ERROR: Cannot find {DATA_PATH}")
        return []
    
    df = pd.read_csv(DATA_PATH)
    celebrities = sorted(df['celebrity_name'].unique().tolist())
    return celebrities


def generate_instagram_handles(celebrity_names):
    """
    Generate likely Instagram handles from celebrity names
    Examples: 
        "Artem Chigvintsev" -> ["artemchigvintsev", "artem.chigvintsev", "artemchigvintsevofficial"]
        "Zendaya" -> ["zendaya", "zendaya.coleman"]
    """
    handle_candidates = {}
    
    for name in celebrity_names:
        candidates = []
        
        # Basic: remove spaces, lowercase
        basic = name.lower().replace(" ", "")
        candidates.append(basic)
        
        # With dots
        basic_with_dot = name.lower().replace(" ", ".")
        candidates.append(basic_with_dot)
        
        # With underscore
        basic_with_underscore = name.lower().replace(" ", "_")
        candidates.append(basic_with_underscore)
        
        # First name + last name
        parts = name.split()
        if len(parts) >= 2:
            fname_lname = parts[0].lower() + parts[-1].lower()
            candidates.append(fname_lname)
            
            fname_dot_lname = parts[0].lower() + "." + parts[-1].lower()
            candidates.append(fname_dot_lname)
        
        # With "official"
        candidates.append(basic + "official")
        candidates.append(basic_with_underscore + "official")
        
        handle_candidates[name] = list(set(candidates))  # Remove duplicates
    
    return handle_candidates


def collect_followers_instagrapi(celebrity_names, handle_candidates=None, username=None, password=None):
    """
    Collect followers using instagrapi (unofficial Instagram API)
    Supports login for better results
    
    Args:
        celebrity_names: list of celebrity names (not Instagram handles)
        handle_candidates: dict mapping names to list of possible IG handles
        username: Instagram username for login (optional but recommended)
        password: Instagram password for login (optional but recommended)
    
    Returns:
        dict with celebrity_name: {'handle': handle, 'followers': count, 'found': bool}
    """
    print("="*80)
    print("INSTAGRAM FOLLOWER COLLECTION - UNOFFICIAL API (instagrapi)")
    print("="*80)
    
    # Initialize Instagram client
    try:
        cl = Client()
        
        # Try to login if credentials provided
        if username and password:
            print(f"\nAttempting to login as @{username}...")
            try:
                cl.login(username, password)
                print(f"✓ Successfully logged in as @{username}")
            except Exception as login_error:
                print(f"⚠ Login failed: {login_error}")
                print("Attempting anonymous mode instead...\n")
        else:
            print("✓ Instagram client initialized (anonymous mode)")
            print("Note: For better results, provide Instagram login credentials\n")
        
        client_ready = True
    except Exception as e:
        print(f"✗ Failed to initialize Instagram client: {e}")
        return {}
    
    followers_data = {}
    found_count = 0
    not_found_count = 0
    
    for idx, celebrity_name in enumerate(celebrity_names, 1):
        print(f"[{idx}/{len(celebrity_names)}] Searching for: {celebrity_name}")
        found = False
        
        # Get candidate handles for this celebrity
        if handle_candidates and celebrity_name in handle_candidates:
            candidates = handle_candidates[celebrity_name]
        else:
            # Default candidates
            candidates = [
                celebrity_name.lower().replace(" ", ""),
                celebrity_name.lower().replace(" ", "."),
                celebrity_name.lower().replace(" ", "_"),
            ]
        
        # Try each candidate handle
        if client_ready:
            for handle in candidates:
                try:
                    user_info = cl.user_info_by_username(handle)
                    follower_count = user_info.follower_count
                    
                    followers_data[celebrity_name] = {
                        'handle': f"@{handle}",
                        'followers': follower_count,
                        'found': True
                    }
                    
                    print(f"  ✓ Found: @{handle} - {follower_count:,} followers")
                    found = True
                    found_count += 1
                    break  # Found it, stop trying other handles
                    
                except UserNotFound:
                    print(f"  ✗ @{handle} not found")
                    continue
                except Exception as e:
                    error_msg = str(e)[:80]
                    if any(x in error_msg.lower() for x in ['404', 'not found', 'does not exist']):
                        print(f"  ✗ @{handle} not found")
                    else:
                        print(f"  ⚠ @{handle} - {error_msg}")
                    continue
                
                finally:
                    # Rate limiting: wait 1-2 seconds between requests
                    time.sleep(1.5)
        
        if not found:
            followers_data[celebrity_name] = {
                'handle': None,
                'followers': None,
                'found': False
            }
            not_found_count += 1
    
    # Summary
    print("\n" + "="*80)
    print("COLLECTION SUMMARY:")
    print("="*80)
    print(f"Total celebrities: {len(celebrity_names)}")
    print(f"Found: {found_count}")
    print(f"Not found: {not_found_count}")
    print(f"Success rate: {found_count/len(celebrity_names)*100:.1f}%")
    
    return followers_data


# Option 2: Manual collection with a template (fallback)
    """
    Create a CSV template for manual data entry
    
    Args:
        celebrity_names: list of celebrity names
        output_file: where to save the template
    """
    df = pd.DataFrame({
        'celebrity_name': celebrity_names,
        'instagram_handle': ['@' for _ in celebrity_names],
        'follower_count': [None for _ in celebrity_names],
        'collection_date': [pd.Timestamp.now().strftime('%Y-%m-%d') for _ in celebrity_names],
        'notes': ['' for _ in celebrity_names]
    })
    
    df.to_csv(output_file, index=False)
    print(f"\nTemplate created: {output_file}")
    print("Instructions:")
    print("  1. Fill in the 'instagram_handle' column with their IG usernames (e.g., @zendaya)")
    print("  2. Visit instagram.com/@handle and copy the follower count")
    print("  3. Paste it in the 'follower_count' column")
    print("  4. Save the file")
    return df


# Option 3: Using requests + Beautiful Soup (advanced scraping)
def collect_followers_beautifulsoup(instagram_handles):
    """
    DEPRECATED: Instagram blocks this approach
    Kept for reference only
    """
    print("⚠ This method is deprecated - Instagram blocks web scraping")
    return {}
def collect_followers_socialblade(instagram_handles):
    """
    DEPRECATED: Website structure changed
    Kept for reference only
    """
    print("⚠ This method is deprecated - Social Blade website structure changed")
    return {}


def save_results(followers_data, output_file='instagram_followers_collected.csv'):
    """
    Save collected Instagram data to CSV
    
    Args:
        followers_data: dict from collect_followers_instagrapi()
        output_file: output filename
    """
    records = []
    for celebrity_name, data in followers_data.items():
        records.append({
            'celebrity_name': celebrity_name,
            'instagram_handle': data.get('handle'),
            'follower_count': data.get('followers'),
            'found': data.get('found', False),
            'collection_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df = pd.DataFrame(records)
    df.to_csv(output_file, index=False)
    
    print(f"\n✓ Results saved to: {output_file}")
    return df


# Main workflow
if __name__ == "__main__":
    print("\n" + "="*80)
    print("INSTAGRAM FOLLOWER COLLECTOR FOR DWTS CELEBRITIES")
    print("="*80)
    
    # Step 1: Load celebrities from DWTS data
    print("\nStep 1: Loading DWTS celebrity list...")
    celebrities = load_dwts_celebrities()
    
    if not celebrities:
        print("ERROR: Could not load celebrity list. Exiting.")
        exit(1)
    
    print(f"✓ Loaded {len(celebrities)} unique celebrities")
    
    # Step 2: Ask for Instagram credentials
    print("\n" + "="*80)
    print("Step 2: Instagram Account Login (Optional but RECOMMENDED)")
    print("="*80)
    print("\nLogging in will give better access to follower data.")
    print("If you don't have Instagram, just press Enter to skip.\n")
    
    ig_username = input("Enter your Instagram username (or press Enter to skip): ").strip()
    ig_password = None
    
    if ig_username:
        import getpass
        ig_password = getpass.getpass("Enter your Instagram password: ")
        print("✓ Credentials captured (password hidden)")
    else:
        print("⚠ Skipping login - using anonymous mode (may have limited success)")
    
    # Step 3: Generate Instagram handle candidates
    print("\n" + "="*80)
    print("Step 3: Generating Instagram handle candidates...")
    print("="*80)
    handle_candidates = generate_instagram_handles(celebrities)
    print(f"✓ Generated candidates for {len(handle_candidates)} celebrities")
    
    # Step 4: Collect followers using unofficial API
    print("\n" + "="*80)
    print("Step 4: Collecting followers from Instagram...")
    print("="*80)
    print(f"\nThis will take ~{len(celebrities) * 1.5 / 60:.0f} minutes ({len(celebrities)} celebrities × 1.5 sec per try)")
    print("Please be patient...\n")
    
    followers_data = collect_followers_instagrapi(celebrities, handle_candidates, ig_username, ig_password)
    
    # Step 5: Save results
    print("\nStep 5: Saving results...")
    df_results = save_results(followers_data)
    
    # Step 6: Show summary statistics
    print("\n" + "="*80)
    print("FINAL RESULTS SUMMARY:")
    print("="*80)
    found_count = df_results['found'].sum()
    not_found_count = (~df_results['found']).sum()
    
    print(f"\nSuccessfully found: {found_count}/{len(celebrities)}")
    print(f"Not found: {not_found_count}/{len(celebrities)}")
    print(f"Success rate: {found_count/len(celebrities)*100:.1f}%")
    
    # Show found celebrities
    if found_count > 0:
        print("\n" + "-"*80)
        print("FOUND CELEBRITIES (Top 20 by followers):")
        print("-"*80)
        found_df = df_results[df_results['found']].sort_values('follower_count', ascending=False)
        for idx, (_, row) in enumerate(found_df.head(20).iterrows(), 1):
            print(f"{idx:2d}. {row['celebrity_name']:25s} | {row['instagram_handle']:25s} | {row['follower_count']:>12,} followers")
        
        if found_count > 20:
            print(f"... and {found_count - 20} more")
    
    # Show not found celebrities
    if not_found_count > 0:
        print("\n" + "-"*80)
        print(f"NOT FOUND CELEBRITIES ({not_found_count} total):")
        print("-"*80)
        not_found_df = df_results[~df_results['found']].sort_values('celebrity_name')
        print("Create a manual collection file? (y/n): ", end="")
        create_manual = input().strip().lower()
        
        if create_manual == 'y':
            not_found_names = not_found_df['celebrity_name'].tolist()
            create_manual_collection_template(not_found_names, 'instagram_followers_manual_fillup.csv')
            print(f"\n✓ Template created: instagram_followers_manual_fillup.csv")
            print(f"  Celebrities to manually search: {not_found_count}")
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print(f"1. ✓ Collected Instagram data saved to: instagram_followers_collected.csv")
    
    if not_found_count > 0:
        print(f"2. Fill in the manual template: instagram_followers_manual_fillup.csv")
        print(f"   (Search manually for the {not_found_count} not-found celebrities)")
    
    print("\n3. Load the data into your analysis notebook:")
    print("   ig_data = pd.read_csv('instagram_followers_collected.csv')")
    print("4. Merge with your placement analysis")
    print("="*80 + "\n")
