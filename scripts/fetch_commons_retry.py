"""Retry Commons queries for the ids that failed (429 / timeout / null).

Uses a longer delay and on-429 backoff. Writes results into the existing
commons_result.json, only overwriting the retried ids.
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"

# id -> list of candidate search terms to try in order
RETRY = {
    2:  ["Beijing Xishan National Forest Park", "Xishan Beijing forest"],
    3:  ["Xiaoqinghe River Beijing", "Beijing Fangshan river park"],
    6:  ["Zhenhaisi郊野公园", "Beijing Zhenhaisi Park"],
    7:  ["Bihai Park Daxing", "Beijing Daxing park"],
    8:  ["Banbidian Forest Park", "Beijing Banbidian"],
    9:  ["Yinghai wetland Beijing", "Beijing Yinghai"],
    11: ["Taihu Wetland Park Tongzhou", "Beijing Taihu park"],
    12: ["Nanyuan Forest Wetland Park", "Beijing Nanyuan park"],
    13: ["Yongding River Forest Park", "Beijing Yongding river park"],
    16: ["Huangcaowan Park Beijing", "Beijing Huangcaowan"],
    18: ["Heiqiao Park Beijing", "Beijing Cuigezhuang park"],
    19: ["Yeyahu National Wetland Park", "Yanqing Yeyahu wetland"],
    20: ["Temple of Heaven Hall of Prayer", "Tian Tan Beijing"],
    21: ["Summer Palace Kunming Lake", "Yiheyuan Beijing"],
    22: ["Gaobeidian Beijing", "Beijing Gaobeidian village"],
    23: ["Yuan Dadu City Wall Ruins", "Yuan Dadu wall park Beijing"],
    24: ["Chaoyang Park Beijing", "Beijing Chaoyang Park lake"],
    25: ["Honglingjin Park Beijing", "Beijing Honglingjin"],
    26: ["Xinglong Park Beijing", "Beijing Xinglong Park"],
    27: ["Yuyuantan Park Beijing", "Beijing Yuyuantan"],
    28: ["Beihai Park Beijing", "Beijing Beihai Park white pagoda"],
    29: ["Jingshan Park Beijing", "Beijing Jingshan"],
    30: ["Zizhuyuan Park Beijing", "Purple Bamboo Park Beijing"],
    31: ["Taoranting Park Beijing", "Beijing Taoranting"],
    32: ["Longtanhu Park Beijing", "Beijing Longtanhu"],
    33: ["Fragrant Hills Xiangshan", "Beijing Xiangshan Park"],
    34: ["Yuanmingyuan Old Summer Palace", "Beijing Yuanmingyuan ruins"],
    35: ["Beijing Botanical Garden", "Beijing Botanical Garden greenhouse"],
    36: ["Haidian Park Beijing", "Beijing Haidian Park"],
    38: ["Dongjiao Wetland Park Beijing", "Beijing Shunyi wetland"],
    42: ["Baili Shanshui Gallery Yanqing", "Yanqing Baili gallery"],
}


def query(term: str):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"filetype:bitmap {term}", "gsrlimit": "8",
        "gsrnamespace": "6", "prop": "imageinfo", "iiprop": "url",
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
            return {"title": title, "url": ii.get("url"), "thumb": ii.get("thumburl")}
    return None


def main():
    path = "/Users/liboyang/WorkBuddy/cicada-map/scripts/commons_result.json"
    with open(path) as f:
        out = json.load(f)
    for pid, terms in RETRY.items():
        res = None
        for term in terms:
            for attempt in range(4):
                try:
                    r = query(term)
                    if r:
                        res = r
                        break
                    time.sleep(2)
                except Exception as e:  # noqa: BLE001
                    err = str(e)
                    if "429" in err:
                        time.sleep(8 * (attempt + 1))
                    else:
                        time.sleep(3)
            if res:
                break
            time.sleep(2)
        out[str(pid)] = res if res else {"error": "no image found"}
        print(f"[{pid}] -> {res['title'] if res else 'NONE'}")
        time.sleep(4)
    with open(path, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nUpdated commons_result.json")


if __name__ == "__main__":
    main()
