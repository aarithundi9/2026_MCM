"""
Instagram Follower Collector using Instagrapi
Robust version with comprehensive error handling to prevent crashes

INSTALLATION:
    pip install instagrapi
"""

import pandas as pd
from pathlib import Path
import time
import random
from instagrapi import Client
from instagrapi.exceptions import UserNotFound, BadPassword, LoginRequired


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
    Includes common patterns like "thereal", "theofficial", "the name", etc.
    """
    base_name = name.lower().replace(" ", "").replace(".", "")
    
    candidates = [
        # Basic variations
        base_name,
        base_name.replace(" ", "."),
        base_name.replace(" ", "_"),
        base_name.replace(" ", "-"),
        
        # "The" variations
        f"the{base_name}",
        f"the_{base_name}",
        f"the-{base_name}",
        
        # Common celebrity patterns
        f"thereal{base_name}",
        f"the_real_{base_name}",
        f"the-real-{base_name}",
        f"theofficial{base_name}",
        f"the_official_{base_name}",
        f"the-official-{base_name}",
        f"official{base_name}",
        f"official_{base_name}",
        f"official-{base_name}",
        
        # With "official" suffix
        f"{base_name}official",
        f"{base_name}_official",
        f"{base_name}-official",
        f"{base_name}theofficial",
        
        # Alternative suffixes
        f"{base_name}tv",
        f"{base_name}_tv",
        f"{base_name}world",
        f"{base_name}_world",
        f"{base_name}fan",
        f"{base_name}page",
        f"{base_name}_page",
        
        # Number variants (common for duplicate names)
        f"{base_name}1",
        f"{base_name}_1",
        f"{base_name}2",
    ]
    
    # Also try with first + last name
    parts = name.split()
    if len(parts) >= 2:
        first = parts[0].lower()
        last = parts[1].lower()
        
        candidates.extend([
            # Basic first.last
            f"{first}{last}",
            f"{first}.{last}",
            f"{first}_{last}",
            f"{first}-{last}",
            
            # "The" + first last
            f"the{first}{last}",
            f"the_{first}_{last}",
            f"the-{first}-{last}",
            
            # Official variations with first last
            f"thereal{first}{last}",
            f"the_real_{first}_{last}",
            f"the-real-{first}-{last}",
            f"theofficial{first}{last}",
            f"the_official_{first}_{last}",
            f"the-official-{first}-{last}",
            f"official{first}{last}",
            f"official_{first}_{last}",
            f"official-{first}-{last}",
            
            # Suffix variations
            f"{first}_{last}_official",
            f"{first}-{last}-official",
            f"{first}_{last}_tv",
            f"{first}_{last}_page",
            
            # Reverse order
            f"{last}{first}",
            f"{last}_{first}",
        ])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_candidates = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique_candidates.append(c)
    
    return unique_candidates


def collect_followers_instagrapi(celebrity_names, username, password, min_followers=5000, 
                                 test_mode=False, test_count=15, max_retries=3):
    """
    Collect Instagram followers using Instagrapi with robust error handling
    
    Args:
        celebrity_names: list of celebrity names
        username: Instagram username
        password: Instagram password
        min_followers: minimum follower count threshold
        test_mode: if True, only test on test_count celebrities
        test_count: number of celebrities to test
        max_retries: max retries per celebrity
    
    Returns:
        dict with results
    """
    print("="*80)
    print("INSTAGRAM COLLECTOR - Instagrapi (ROBUST VERSION)")
    print("="*80)
    print(f"\nSettings:")
    print(f"  - Account: {username}")
    print(f"  - Minimum follower count: {min_followers:,}")
    print(f"  - Handle variations: Multiple per celebrity")
    print(f"  - Error handling: Comprehensive")
    
    if test_mode:
        sample_names = random.sample(celebrity_names, min(test_count, len(celebrity_names)))
        celebrities_to_search = sample_names
        print(f"  - TEST MODE: {test_count} random celebrities\n")
    else:
        celebrities_to_search = celebrity_names
        print()
    
    # Initialize client
    print("Initializing Instagrapi client...")
    client = Client()
    
    try:
        print(f"Logging in as {username}...")
        client.login(username, password)
        print("✓ Login successful\n")
    except Exception as e:
        print(f"✗ Login failed: {str(e)}")
        return {}
    
    followers_data = {}
    found_count = 0
    not_found_count = 0
    error_count = 0
    skipped_count = 0
    
    try:
        for idx, celebrity_name in enumerate(celebrities_to_search, 1):
            print(f"[{idx:3d}/{len(celebrities_to_search)}] {celebrity_name:35s}", end=" | ", flush=True)
            
            # Generate multiple handle candidates
            handle_candidates = generate_handle_candidates(celebrity_name)
            
            # Try each handle
            followers_count = None
            is_verified = None
            found_handle = None
            last_error = None
            
            for handle in handle_candidates:
                try:
                    # Try to get user info
                    user_info = client.user_info_by_username(handle)
                    
                    followers_count = user_info.follower_count
                    is_verified = user_info.is_verified
                    
                    # Only accept if VERIFIED (to avoid fake accounts)
                    if is_verified:
                        found_handle = handle
                        break
                    else:
                        # Found account but not verified, keep trying for verified version
                        followers_count = None
                        is_verified = None
                        last_error = "not_verified"
                        continue
                
                except UserNotFound:
                    # Handle doesn't exist, try next one
                    last_error = "not_found"
                    continue
                
                except Exception as e:
                    # Other error, try next handle
                    last_error = f"error: {str(e)[:30]}"
                    continue
                
                finally:
                    # Rate limit between attempts
                    time.sleep(random.uniform(0.5, 1.5))
            
            # Check if we found them, verified, and meet threshold
            if followers_count and is_verified and followers_count >= min_followers:
                followers_data[celebrity_name] = {
                    'handle': f"@{found_handle}",
                    'followers': followers_count,
                    'verified': is_verified,
                    'found': True
                }
                found_count += 1
                print(f"@{found_handle:25s} {followers_count:>10,} ✓ VERIFIED")
            
            else:
                # Not found, not verified, or below threshold
                followers_data[celebrity_name] = {
                    'handle': None,
                    'followers': None,
                    'verified': None,
                    'found': False
                }
                not_found_count += 1
                if last_error:
                    print(f"NOT FOUND ({last_error})")
                else:
                    print(f"NOT FOUND")
            
            # Random delay between celebrities
            time.sleep(random.uniform(2, 4))
    
    except (BadPassword, LoginRequired) as e:
        print(f"\n✗ Session error: {str(e)}")
        print("Your account may have been temporarily restricted.")
        print("Try again in a few hours.")
        return followers_data
    
    except KeyboardInterrupt:
        print("\n\n⚠ Collection interrupted by user")
        return followers_data
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        return followers_data
    
    finally:
        # Summary
        print("\n" + "="*80)
        print("COLLECTION SUMMARY:")
        print("="*80)
        print(f"Total searched: {len(celebrities_to_search)}")
        print(f"Found: {found_count}")
        print(f"Not found: {not_found_count}")
        print(f"Errors/Skipped: {error_count + skipped_count}")
        if celebrities_to_search:
            print(f"Success rate: {found_count/len(celebrities_to_search)*100:.1f}%")
        
        if test_mode:
            print(f"\n⚠ TEST MODE - Tested {test_count} random celebrities")
    
    return followers_data


def save_results(followers_data, output_file='instagram_followers_instagrapi.csv'):
    """Save collection results to CSV"""
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
    print("INSTAGRAM COLLECTOR - Instagrapi (ROBUST)")
    print("="*80)
    
    # Load celebrities
    print("\nLoading DWTS celebrity list...")
    celebrities = load_dwts_celebrities()
    print(f"✓ Loaded {len(celebrities)} unique celebrities")
    
    # Get login credentials
    print("\n" + "="*80)
    username = input("Enter Instagram username: ").strip()
    password = input("Enter Instagram password: ").strip()
    
    # Test mode first
    print("\n" + "="*80)
    print("RUNNING TEST on 10 random celebrities...")
    print("="*80 + "\n")
    
    test_results = collect_followers_instagrapi(
        celebrities,
        username=username,
        password=password,
        min_followers=5000,
        test_mode=True,
        test_count=10
    )
    
    # Show results
    test_df = pd.DataFrame([
        {'Name': name, 'Handle': data['handle'], 'Followers': data['followers']}
        for name, data in test_results.items() if data['found'] and data['followers'] >= 5000
    ])
    
    found_count = len(test_df)
    print(f"\nTest found: {found_count}/10 celebrities")
    
    if len(test_df) > 0:
        print("\nTest results:")
        print(test_df.to_string(index=False))
    
    # Ask to continue
    if found_count > 0:
        proceed = input("\n\nRun full collection on all 408 celebrities? (yes/no): ").strip().lower()
        
        if proceed == 'yes':
            print("\n" + "="*80)
            print("Running FULL COLLECTION...")
            print("="*80 + "\n")
            print(f"Estimated time: ~{len(celebrities) * 3 / 60:.0f} minutes")
            print("(Do not interrupt - let it run to completion)\n")
            
            full_results = collect_followers_instagrapi(
                celebrities,
                username=username,
                password=password,
                min_followers=5000,
                test_mode=False
            )
            
            # Save
            print("\nSaving results...")
            df_final = save_results(full_results)
            
            # Final summary
            found = df_final[df_final['found'] & (df_final['follower_count'] >= 5000)].shape[0]
            print(f"\n✓ Collection complete!")
            print(f"  Found: {found}/{len(celebrities)} ({found/len(celebrities)*100:.1f}%)")
        else:
            print("\n⚠ Skipped full collection.")
    else:
        print("\n⚠ Test found no celebrities. There may be an issue with the API or account.")
