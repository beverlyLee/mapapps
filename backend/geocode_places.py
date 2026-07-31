#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geocode Beijing cicada gathering places via Photon (keyless OSM geocoder, WGS-84),
convert to GCJ-02 (what AMap JS API expects), and write to cicada_points.xlsx.
"""
import json, math, time, urllib.parse, urllib.request, sys
import openpyxl

OUT_XLSX = "/Users/liboyang/WorkBuddy/cicada-map/backend/data/cicada_points.xlsx"
CACHE = "/tmp/geocode_cache.json"
UA = "cicada-map-research/1.0 (contact: local)"

# ---------- WGS84 -> GCJ02 ----------
A = 6378245.0
EE = 0.00669342162296594323

def _t_lat(x, y):
    r = -100.0 + 2.0*x + 3.0*y + 0.2*y*y + 0.1*x*y + 0.2*math.sqrt(abs(x))
    r += (20.0*math.sin(6.0*x*math.pi) + 20.0*math.sin(2.0*x*math.pi)) * 2.0/3.0
    r += (20.0*math.sin(y*math.pi) + 40.0*math.sin(y/3.0*math.pi)) * 2.0/3.0
    r += (160.0*math.sin(y/12.0*math.pi) + 320*math.sin(y*math.pi/30.0)) * 2.0/3.0
    return r

def _t_lng(x, y):
    r = 300.0 + x + 2.0*y + 0.1*x*x + 0.1*x*y + 0.1*math.sqrt(abs(x))
    r += (20.0*math.sin(6.0*x*math.pi) + 20.0*math.sin(2.0*x*math.pi)) * 2.0/3.0
    r += (20.0*math.sin(x*math.pi) + 40.0*math.sin(x/3.0*math.pi)) * 2.0/3.0
    r += (150.0*math.sin(x/12.0*math.pi) + 300.0*math.sin(x/30.0*math.pi)) * 2.0/3.0
    return r

def wgs84_to_gcj02(lng, lat):
    if not (73.66 < lng < 135.05 and 3.86 < lat < 53.55):
        return lng, lat
    dlat = _t_lat(lng-105.0, lat-35.0)
    dlng = _t_lng(lng-105.0, lat-35.0)
    radlat = lat/180.0*math.pi
    magic = math.sin(radlat)
    magic = 1 - EE*magic*magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat*180.0)/((A*(1-EE))/(magic*sqrtmagic)*math.pi)
    dlng = (dlng*180.0)/(A/sqrtmagic*math.cos(radlat)*math.pi)
    return lng+dlng, lat+dlat

# ---------- Photon geocode ----------
def photon(query):
    q = urllib.parse.urlencode({"q": query, "limit": "1"})
    url = "https://photon.komoot.io/api/?" + q
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("features"):
        f = data["features"][0]
        lon, lat = f["geometry"]["coordinates"]
        return lat, lon, f["properties"].get("name", ""), f["properties"].get("district", "")
    return None

cache = {}
try:
    with open(CACHE, "r", encoding="utf-8") as fh:
        cache = json.load(fh)
except Exception:
    cache = {}

def geocode(name, query):
    key = query
    if key in cache:
        return cache[key]
    for attempt in range(3):
        try:
            res = photon(query)
            if res:
                cache[key] = res
                return res
        except Exception as e:
            print(f"  retry {name}: {e}", file=sys.stderr)
        time.sleep(0.5)
    return None

# ---------- Manual corrections (GCJ-02, consistent with dataset frame) ----------
# Applied where Photon returned a wrong POI or found nothing.
OVERRIDE = {
    "奥林匹克森林公园（北园）": (116.396, 39.993),
    "西山国家森林公园": (116.108, 39.985),
    "小清河郊野公园": (116.045, 39.735),
    "台湖湿地公园": (116.585, 39.782),
    "北京植物园（卧佛寺）": (116.203, 39.992),
    "千家店镇白河（百里画廊）": (116.580, 40.600),
    "天坛回音壁": (116.406, 39.883),
}

# ---------- Species / season by category ----------
CAT = {
    "urban":        ("黑蚱蝉·蟪蛄", "6–8月"),
    "urban_late":   ("黑蚱蝉·蟪蛄·蒙古寒蝉", "6–9月"),
    "wetland":      ("黑蚱蝉·蒙古寒蝉", "6–9月"),
    "mountain":     ("蒙古寒蝉·黑蚱蝉·斑透翅蝉", "7–9月"),
    "north_mountain":("斑透翅蝉·蒙古寒蝉·黑蚱蝉", "8–9月"),
    "street":       ("黑蚱蝉·鸣鸣蝉", "7–8月"),
}

# ---------- Master list ----------
# (name, district, query, cat, abundance, is_famous, note)
PLACES = [
    # ---- existing 21 (refined) ----
    ("奥林匹克森林公园（北园）", "朝阳区", "奥林匹克森林公园 北京市朝阳区", "urban_late", "高", True, "北京最知名蝉鸣聚集区，北园仰山林区"),
    ("西山国家森林公园", "海淀区", "北京西山森林公园", "mountain", "高", True, "6月中蟪蛄→7月黑蚱蝉/蒙古寒蝉"),
    ("小清河郊野公园", "房山区", "小清河郊野公园 北京", "urban_late", "高", True, "本土季鸟猴知名聚集区"),
    ("大运河森林公园", "通州区", "大运河森林公园 北京", "wetland", "中", False, "滨河林地"),
    ("温榆河公园", "朝阳区", "温榆河公园 北京", "wetland", "中", False, "朝阳北部大尺度绿地"),
    ("镇海寺郊野公园", "朝阳区", "镇海寺郊野公园 北京", "urban", "中", False, ""),
    ("碧海公园", "大兴区", "碧海公园 北京", "urban", "中", False, ""),
    ("半壁店森林公园", "大兴区", "半壁店森林公园 北京", "urban_late", "中", False, "南城老牌林地"),
    ("瀛海滨河绿地", "大兴区", "瀛海 北京", "urban", "中", False, "瀛海周边滨河绿地"),
    ("潮白河滨河公园", "通州区", "潮白河滨河公园 北京", "wetland", "中", False, ""),
    ("台湖湿地公园", "通州区", "台湖湿地公园 北京", "wetland", "中", False, ""),
    ("南苑森林湿地公园", "丰台区", "南苑森林湿地公园 北京", "wetland", "中", False, ""),
    ("永定河休闲森林公园", "石景山区", "永定河休闲森林公园 北京", "urban", "中", False, ""),
    ("汉石桥湿地", "顺义区", "汉石桥湿地 北京", "wetland", "中", False, ""),
    ("翠湖国家城市湿地公园", "海淀区", "翠湖国家城市湿地公园 北京", "wetland", "中", False, ""),
    ("黄草湾郊野公园", "朝阳区", "黄草湾郊野公园 北京", "urban", "中", False, ""),
    ("将府公园", "朝阳区", "将府公园 北京", "urban", "中", False, ""),
    ("黑桥公园", "朝阳区", "黑桥公园 北京", "urban", "中", False, ""),
    ("野鸭湖国家湿地公园", "延庆区", "野鸭湖国家湿地公园 北京", "north_mountain", "中", False, "蒙古寒蝉为主"),
    ("天坛公园", "东城区", "天坛公园 北京", "urban_late", "低", False, "古柏蝉鸣"),
    ("颐和园", "海淀区", "颐和园 北京", "urban_late", "低", False, "昆明湖畔柳树"),

    # ---- detailed / research-derived NEW spots ----
    ("惠新西街", "朝阳区", "惠新西街 北京", "street", "中", False, "老槐树成行，鸣鸣蝉密集"),
    ("元大都城垣遗址公园", "朝阳区", "元大都城垣遗址公园 北京", "urban_late", "中", False, "海棠花溪，柳树多蝉多"),
    ("朝阳公园", "朝阳区", "朝阳公园 北京", "urban_late", "中", False, "市区最大公园，柳树成片"),
    ("红领巾公园", "朝阳区", "红领巾公园 北京", "urban", "低", False, "紧邻朝阳公园的小绿地"),
    ("兴隆公园", "朝阳区", "兴隆公园 北京", "urban", "中", False, "东四环老公园"),
    ("玉渊潭公园", "海淀区", "玉渊潭公园 北京", "urban_late", "中", False, "滨湖柳堤"),
    ("北海公园", "西城区", "北海公园 北京", "urban", "低", False, "琼华岛古柳"),
    ("景山公园", "西城区", "景山公园 北京", "urban", "低", False, "皇家园林古槐"),
    ("紫竹院公园", "海淀区", "紫竹院公园 北京", "urban_late", "中", False, "竹林水系旁阔叶树"),
    ("陶然亭公园", "西城区", "陶然亭公园 北京", "urban", "低", False, ""),
    ("龙潭湖公园", "东城区", "龙潭湖公园 北京", "urban", "低", False, ""),
    ("香山公园", "海淀区", "香山公园 北京", "mountain", "中", False, "山地阔叶林，蒙古寒蝉多"),
    ("圆明园遗址公园", "海淀区", "圆明园 北京", "wetland", "中", False, "水边柳槐"),
    ("北京植物园（卧佛寺）", "海淀区", "北京植物园 北京", "mountain", "中", False, "山地林木"),
    ("海淀公园", "海淀区", "海淀公园 北京", "urban", "中", False, ""),
    ("莲花池公园", "丰台区", "莲花池公园 北京", "urban", "低", False, ""),
    ("东郊湿地公园", "顺义区", "东郊湿地公园 北京", "wetland", "中", False, "东郊大湿地"),
    ("雁栖湖", "怀柔区", "雁栖湖 北京", "mountain", "中", False, "怀柔湖区林地"),
    ("喇叭沟门满族乡（自然森林）", "怀柔区", "喇叭沟门 北京", "north_mountain", "中", False, "规范采集示范林，原始次生林"),
    ("金海湖", "平谷区", "金海湖 北京", "mountain", "中", False, "平谷湖区山地"),
    ("千家店镇白河（百里画廊）", "延庆区", "百里画廊 北京", "north_mountain", "中", False, "8月底斑透翅蝉为主"),

    # ---- fine-grained sub-spots of the 3 famous parks (detail) ----
    ("奥林匹克森林公园（南园）", "朝阳区", "奥林匹克森林公园南园 北京", "urban_late", "高", True, "南园奥海南岸林地"),
    ("颐和园西堤", "海淀区", "颐和园西堤 北京", "urban_late", "低", False, "西堤柳桥，临水蝉声"),
    ("天坛回音壁", "东城区", "天坛回音壁 北京", "urban_late", "低", False, "回音壁外古柏"),
]

# ---------- geocode + build ----------
rows = []
miss = []
for i, (name, district, query, cat, abundance, famous, note) in enumerate(PLACES, start=1):
    sp, season = CAT[cat]
    ov = OVERRIDE.get(name)
    if ov:
        glng, glat = ov
        rows.append({
            "id": i, "name": name, "district": district,
            "lng": round(glng, 6), "lat": round(glat, 6),
            "species": sp, "peak_season": season,
            "abundance": abundance, "is_famous": famous, "note": note,
            "src": "人工校正(GCJ-02)",
        })
        print(f"[{i:02d}] {name}: OVERRIDE GCJ02 ({glng:.5f},{glat:.5f})")
        continue
    res = geocode(name, query)
    if res:
        wlat, wlon, found_name, found_dist = res
        glng, glat = wgs84_to_gcj02(wlon, wlat)
        rows.append({
            "id": i, "name": name, "district": district,
            "lng": round(glng, 6), "lat": round(glat, 6),
            "species": sp, "peak_season": season,
            "abundance": abundance, "is_famous": famous, "note": note,
            "src": found_name,
        })
        print(f"[{i:02d}] {name}: GCJ02 ({glng:.5f},{glat:.5f})  via '{found_name}'")
    else:
        print(f"[{i:02d}] {name}: *** MISS *** query='{query}'")
        miss.append((i, name, query, district, cat, abundance, famous, note))

with open(CACHE, "w", encoding="utf-8") as fh:
    json.dump(cache, fh, ensure_ascii=False, indent=2)

print(f"\nGEOCODED OK: {len(rows)} | MISSED: {len(miss)}")

# ---------- write xlsx ----------
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "cicada_points"
hdr = ["id","name","district","lng","lat","species","peak_season","abundance","is_famous"]
ws.append(hdr)
for r in rows:
    ws.append([r["id"], r["name"], r["district"], r["lng"], r["lat"],
               r["species"], r["peak_season"], r["abundance"], r["is_famous"]])
wb.save(OUT_XLSX)
print(f"WROTE {OUT_XLSX}  rows={len(rows)}")

if miss:
    print("\n=== MISSED (need manual coords) ===")
    for m in miss:
        print(m)
