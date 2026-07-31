"""Batch-query Wikimedia Commons for hotlinkable park photos.

Prints a JSON map {park_search_term: {url, thumb, title}} for the first
plausible image found per search term. We use the generator=search +
imageinfo approach and pick the first result whose title looks like an image.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
import time

API = "https://commons.wikimedia.org/w/api.php"

# Map each point id -> a search term (park + optional landmark) to query on Commons
SEARCH = {
    1: "Olympic Forest Park Beijing",
    2: "Xishan National Forest Park Beijing",
    3: "Xiaoqing River Beijing",
    4: "Grand Canal Forest Park Tongzhou Beijing",
    5: "Wenyu River Park Beijing",
    6: "Zhenhaisi Park Beijing",
    7: "Bihai Park Beijing Daxing",
    8: "Banbidian Forest Park Beijing",
    9: "Yinghai Beijing Wetland",
    10: "Chaobai River Beijing",
    11: "Taihu Wetland Park Beijing",
    12: "Nanyuan Forest Wetland Park Beijing",
    13: "Yongding River Forest Park Beijing",
    14: "Hanshiqiao Wetland Beijing",
    15: "Cuihu Wetland Park Beijing",
    16: "Huangcaowan Park Beijing",
    17: "Jiangfu Park Beijing",
    18: "Heiqiao Park Beijing",
    19: "Yeyahu Wetland Park Beijing",
    20: "Temple of Heaven Beijing",
    21: "Summer Palace Beijing",
    22: "Gaobeidian Village Beijing",
    23: "Yuan Dadu City Wall Ruins Park Beijing",
    24: "Chaoyang Park Beijing",
    25: "Honglingjin Park Beijing",
    26: "Xinglong Park Beijing",
    27: "Yuyuantan Park Beijing",
    28: "Beihai Park Beijing",
    29: "Jingshan Park Beijing",
    30: "Zizhuyuan Park Beijing",
    31: "Taoranting Park Beijing",
    32: "Longtanhu Park Beijing",
    33: "Fragrant Hills Beijing",
    34: "Old Summer Palace Beijing",
    35: "Beijing Botanical Garden Wofo Temple",
    36: "Haidian Park Beijing",
    37: "Lianhuachi Park Beijing",
    38: "Dongjiao Wetland Park Beijing",
    39: "Yanqi Lake Beijing",
    40: "Labagoumen Beijing forest",
    41: "Jinhai Lake Beijing",
    42: "Baili Gallery Beijing Yanqing",
    43: "Olympic Forest Park South Beijing",
    44: "Summer Palace West Dyke Beijing",
    45: "Echo Wall Temple of Heaven Beijing",
}


def query(term: str):
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": f"filetype:bitmap {term}",
        "gsrlimit": "8",
        "gsrnamespace": "6",
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": "900",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "cicada-map/1.0 (research)"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    pages = data.get("query", {}).get("pages", {})
    for p in pages.values():
        title = p.get("title", "")
        if title.lower().endswith((".jpg", ".jpeg", ".png")):
            ii = p.get("imageinfo", [{}])[0]
            return {
                "title": title,
                "url": ii.get("url"),
                "thumb": ii.get("thumburl"),
            }
    return None


def main():
    out = {}
    for pid, term in SEARCH.items():
        try:
            r = query(term)
            out[pid] = r
            print(f"[{pid}] {term!r} -> {r['title'] if r else None}")
        except Exception as e:  # noqa: BLE001
            out[pid] = {"error": str(e)}
            print(f"[{pid}] {term!r} -> ERROR {e}")
        time.sleep(0.4)
    with open("/Users/liboyang/WorkBuddy/cicada-map/scripts/commons_result.json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nSaved commons_result.json")


if __name__ == "__main__":
    main()
