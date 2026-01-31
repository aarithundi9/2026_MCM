"""
Instagram Follower Data Collection Script - Version 2 (with verification)
Uses the unofficial Instagram API (instagrapi) to collect follower counts for DWTS celebrities
Includes minimum follower count filtering to avoid fake accounts

INSTALLATION REQUIRED:
    pip install instagrapi

This script automatically loads celebrities from the DWTS data and attempts to find them on Instagram.
"""

import pandas as pd
import requests
from pathlib import Path
import time
import json
import random
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


def collect_followers_instagrapi(celebrity_names, handle_candidates=None, username=None, password=None, min_followers=5000, test_mode=False, test_count=15):
    """
    Collect followers using instagrapi (unofficial Instagram API)
    Filters by minimum follower count and verified status to avoid fake accounts
    
    Args:
        celebrity_names: list of celebrity names (not Instagram handles)
        handle_candidates: dict mapping names to list of possible IG handles
        username: Instagram username for login (optional but recommended)
        password: Instagram password for login (optional but recommended)
        min_followers: Minimum follower count to consider valid (default 5000)
        test_mode: If True, only test on test_count celebrities
        test_count: Number of celebrities to test (default 15)
    
    Returns:
        dict with celebrity_name: {'handle': handle, 'followers': count, 'found': bool, 'verified': bool}
    """
    print("="*80)
    print("INSTAGRAM FOLLOWER COLLECTION - UNOFFICIAL API (instagrapi) v2")
    print("="*80)
    print(f"\nSettings:")
    print(f"  - Minimum follower count: {min_followers:,}")
    print(f"  - Prefer verified accounts: Yes (✓)")
    if test_mode:
        print(f"  - TEST MODE: Sampling {test_count} random celebrities")
    print()
    
    # Sample test celebrities if in test mode
    if test_mode:
        sample_names = random.sample(celebrity_names, min(test_count, len(celebrity_names)))
        celebrities_to_search = sample_names
        print(f"Testing with: {', '.join(sample_names[:5])}{'...' if len(sample_names) > 5 else ''}\n")
    else:
        celebrities_to_search = celebrity_names
    
    # Initialize Instagram client
    try:
        cl = Client()
        
        # Try to login if credentials provided
        if username and password:
            print(f"Attempting to login as @{username}...")
            try:
                cl.login(username, password)
                print(f"✓ Successfully logged in as @{username}\n")
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
    filtered_out_count = 0
    
    for idx, celebrity_name in enumerate(celebrities_to_search, 1):
        print(f"[{idx:3d}/{len(celebrities_to_search)}] {celebrity_name:35s}", end=" | ", flush=True)
        best_account = None
        
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
                    is_verified = user_info.is_verified
                    
                    # Check if this account meets minimum follower threshold
                    if follower_count >= min_followers:
                        # Prefer verified accounts, but take high-follower accounts too
                        if best_account is None or is_verified or follower_count > best_account['followers']:
                            best_account = {
                                'handle': f"@{handle}",
                                'followers': follower_count,
                                'verified': is_verified,
                                'found': True
                            }
                            if is_verified:
                                break  # Stop searching if we found a verified account
                    # If account doesn't meet minimum follower threshold, skip it
                    
                except Exception as e:
                    # Continue to next handle
                    continue
                
                finally:
                    # Rate limiting: wait 1.5 seconds between requests
                    time.sleep(1.5)
        
        if best_account:
            followers_data[celebrity_name] = best_account
            found_count += 1
            verified_badge = "✓" if best_account['verified'] else "○"
            print(f"{best_account['handle']:22s} {best_account['followers']:>10,} {verified_badge}")
        else:
            followers_data[celebrity_name] = {
                'handle': None,
                'followers': None,
                'verified': None,
                'found': False
            }
            not_found_count += 1
            print("NOT FOUND")
    
    # Summary
    print("\n" + "="*80)
    print("COLLECTION SUMMARY:")
    print("="*80)
    print(f"Total searched: {len(celebrities_to_search)}")
    print(f"Found (✓=verified, ○=unverified): {found_count}")
    print(f"Not found: {not_found_count}")
    if celebrities_to_search:
        success_rate = found_count/len(celebrities_to_search)*100
    else:
        success_rate = 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if test_mode:
        print(f"\n⚠ TEST MODE - Results above are from {test_count} random celebrities")
        print(f"✓ If success rate looks good, run full collection without test mode")
    
    return followers_data


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
            'verified': data.get('verified'),
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
    print("INSTAGRAM FOLLOWER COLLECTOR FOR DWTS CELEBRITIES - TEST MODE")
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
    
    # Step 4: TEST MODE - Collect followers from small sample first
    print("\n" + "="*80)
    print("Step 4: RUNNING TEST on 15 random celebrities...")
    print("="*80)
    print("\nThis will take ~2-3 minutes for testing.\n")
    
    test_followers_data = collect_followers_instagrapi(
        celebrities, 
        handle_candidates, 
        ig_username, 
        ig_password,
        min_followers=5000,  # Default: 5000 followers minimum
        test_mode=True,
        test_count=15
    )
    
    # Step 5: Show test results
    print("\n" + "="*80)
    print("TEST RESULTS:")
    print("="*80)
    test_df = pd.DataFrame([
        {'Name': name, 'Handle': data['handle'], 'Followers': data['followers'], 'Verified': '✓' if data['verified'] else '○' if data['verified'] is False else 'N/A'}
        for name, data in test_followers_data.items() if data['found']
    ])
    
    if len(test_df) > 0:
        print(test_df.to_string(index=False))
    else:
        print("No celebrities found in test run")
    
    # Step 6: Ask user if they want to continue
    print("\n" + "="*80)
    print("DECISION:")
    print("="*80)
    print(f"\nTest results: {test_df.shape[0]}/15 celebrities found")
    
    if test_df.shape[0] > 10:
        print("✓ Success rate looks good!")
    elif test_df.shape[0] > 5:
        print("~ Medium success rate - some celebrities might not be found")
    else:
        print("⚠ Low success rate - consider adjusting settings")
    
    print("\nDo you want to run the FULL COLLECTION on all 408 celebrities? (yes/no): ", end="")
    proceed = input().strip().lower()
    
    if proceed == 'yes':
        print("\n" + "="*80)
        print("Step 5: Collecting followers from ALL celebrities...")
        print("="*80)
        print(f"\nThis will take ~{len(celebrities) * 1.5 / 60:.0f} minutes ({len(celebrities)} celebrities × 1.5 sec per try)")
        print("Please be patient...\n")
        
        full_followers_data = collect_followers_instagrapi(
            celebrities, 
            handle_candidates, 
            ig_username, 
            ig_password,
            min_followers=5000,
            test_mode=False
        )
        
        # Save results
        print("\nStep 6: Saving results...")
        df_results = save_results(full_followers_data)
        
        # Show summary
        found_count = df_results['found'].sum()
        print("\n" + "="*80)
        print("FINAL RESULTS:")
        print("="*80)
        print(f"\nTotal found: {found_count}/{len(celebrities)} ({found_count/len(celebrities)*100:.1f}%)")
        
        # Top 20 celebrities by followers
        print("\n" + "-"*80)
        print("TOP 20 CELEBRITIES (by followers):")
        print("-"*80)
        top_df = df_results[df_results['found']].sort_values('follower_count', ascending=False).head(20)
        for idx, (_, row) in enumerate(top_df.iterrows(), 1):
            verified_badge = "✓" if row['verified'] else "○"
            print(f"{idx:2d}. {row['celebrity_name']:30s} {row['instagram_handle']:25s} {row['follower_count']:>12,} {verified_badge}")
        
        not_found_count = (~df_results['found']).sum()
        if not_found_count > 0:
            print(f"\n{not_found_count} celebrities not found (see instagram_followers_collected.csv)")
    else:
        print("\n⚠ Full collection skipped. You can run again when ready.")
    
    print("\n" + "="*80)
