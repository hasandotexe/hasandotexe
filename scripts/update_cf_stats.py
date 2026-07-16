"""
Fetches live Codeforces stats for a handle and writes them into README.md
between the CF_STATS_START / CF_STATS_END markers.

No external badge/image service involved — pure text, generated from the
official Codeforces API, committed straight into the repo.
"""

import os
import sys
import urllib.request
import json
from datetime import datetime, timezone

HANDLE = os.environ.get("CF_HANDLE", "Hamim_Hasan")
README_PATH = "README.md"
START_MARK = "<!--CF_STATS_START-->"
END_MARK = "<!--CF_STATS_END-->"


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode())


def get_user_info(handle):
    data = fetch_json(f"https://codeforces.com/api/user.info?handles={handle}")
    if data["status"] != "OK":
        raise RuntimeError(f"user.info failed: {data}")
    return data["result"][0]


def get_submissions(handle):
    data = fetch_json(f"https://codeforces.com/api/user.status?handle={handle}")
    if data["status"] != "OK":
        raise RuntimeError(f"user.status failed: {data}")
    return data["result"]


def get_rating_history(handle):
    data = fetch_json(f"https://codeforces.com/api/user.rating?handle={handle}")
    if data["status"] != "OK":
        raise RuntimeError(f"user.rating failed: {data}")
    return data["result"]


def build_stats_block(handle):
    info = get_user_info(handle)
    submissions = get_submissions(handle)
    rating_history = get_rating_history(handle)

    solved = {
        (s["problem"].get("contestId"), s["problem"]["index"], s["problem"]["name"])
        for s in submissions
        if s["verdict"] == "OK"
    }

    rank = info.get("rank", "unrated").title()
    max_rank = info.get("maxRank", "unrated").title()
    rating = info.get("rating", "N/A")
    max_rating = info.get("maxRating", "N/A")
    contribution = info.get("contribution", 0)
    friend_count = info.get("friendOfCount", 0)
    rated_contests = len(rating_history)

    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return f"""| Stat | Value |
|---|---|
| Rank | {rank} (max: {max_rank}) |
| Contest Rating | {rating} |
| Max Contest Rating | {max_rating} |
| Rated Contests | {rated_contests} |
| Problems Solved | {len(solved)} |
| Submissions | {len(submissions)} |
| Friend of | {friend_count} |
| Contribution | {contribution} |

*Last updated: {updated}*"""


def update_readme(new_block):
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARK not in content or END_MARK not in content:
        print(f"ERROR: markers {START_MARK} / {END_MARK} not found in {README_PATH}")
        sys.exit(1)

    before = content.split(START_MARK)[0]
    after = content.split(END_MARK)[1]

    new_content = f"{before}{START_MARK}\n{new_block}\n{END_MARK}{after}"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)


if __name__ == "__main__":
    block = build_stats_block(HANDLE)
    update_readme(block)
    print("README.md stats block updated.")
