import httpx
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

print("=== Testing HackerRank ===")
for url in [
    "https://www.hackerrank.com/rest/hackers/tourist",
    "https://www.hackerrank.com/rest/hackers/tourist/badges",
    "https://www.hackerrank.com/profile/tourist",
    "https://www.hackerrank.com/tourist",
]:
    try:
        r = httpx.get(url, headers=headers, timeout=8.0, follow_redirects=True)
        print(f"{url} -> status={r.status_code}, len={len(r.text)}")
        if r.status_code == 200:
            if "application/json" in r.headers.get("content-type", ""):
                print("  JSON keys:", list(r.json().keys()))
                if "model" in r.json():
                    print("  model keys:", list(r.json()["model"].keys()))
            else:
                # Look for profile data in HTML
                title = re.search(r"<title>([^<]+)</title>", r.text)
                print("  Title:", title.group(1) if title else "None")
                # Look for badges, solved, or data in script tags
                initial_state = re.findall(r'__INITIAL_STATE__\s*=\s*({.*?});', r.text)
                if initial_state:
                    print("  Found __INITIAL_STATE__ in HTML!")
    except Exception as e:
        print(f"{url} -> error {e}")

print("\n=== Testing CodeChef ===")
for u in ["tourist", "lakshminarasimha"]:
    try:
        r = httpx.get(f"https://www.codechef.com/users/{u}", headers=headers, timeout=8.0, follow_redirects=True)
        html = r.text
        title = re.search(r"<title>([^<]+)</title>", html)
        print(f"User {u}: Status={r.status_code}, Title={title.group(1) if title else None}")
        
        rating_match = re.search(r'class="rating-number">(\d+)<', html)
        stars_match = re.search(r'class="rating-star">\s*(\d+)★', html)
        if not stars_match:
            stars_match = re.search(r'(\d+)★', html)
        global_rank_match = re.search(r'Global Rank[^\d]*(\d+)', html)
        solved_match = re.search(r'Fully Solved \((\d+)\)', html)
        if not solved_match:
            solved_match = re.search(r'Problems Solved[^\d]*(\d+)', html, re.IGNORECASE)
            
        print(f"  rating: {rating_match.group(1) if rating_match else 'None'}")
        print(f"  stars: {stars_match.group(1) if stars_match else 'None'}")
        print(f"  global_rank: {global_rank_match.group(1) if global_rank_match else 'None'}")
        print(f"  solved: {solved_match.group(1) if solved_match else 'None'}")
        
        # Search for any numbers or rating in text
        if not rating_match:
            any_rating = re.findall(r'(\d+)\s*(?:Rating|rating)', html)
            print(f"  any_rating search: {any_rating}")
        if not solved_match:
            any_solved = re.findall(r'(\d+)\s*(?:Problems Solved|problems solved|Solved)', html)
            print(f"  any_solved search: {any_solved[:5]}")
    except Exception as e:
        print(f"CodeChef {u} error: {e}")
