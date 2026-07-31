"""生成 Excel 数据源 backend/data/cicada_points.xlsx。

数据：北京知了（蝉）聚集点位，坐标为各公园大致中心点（GCJ-02），
依据公开报道与昆虫科普资料整理，用于科普/演示，非精确普查。
运行：python gen_excel.py
"""
from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook

# id, province, city, district, town, name, lng, lat, species, peak_season, abundance
# town 可为空字符串
ROWS = [
    (1,  "北京市", "北京市", "朝阳区", "",  "奥林匹克森林公园（北园）", 116.3964, 39.9925, "黑蚱蝉·蟪蛄·蒙古寒蝉",  "6–8月",   "高"),
    (2,  "北京市", "北京市", "海淀区", "",  "西山国家森林公园",       116.1080, 39.9850, "蒙古寒蝉·黑蚱蝉·斑透翅蝉", "7–9月",  "高"),
    (3,  "北京市", "北京市", "房山区", "",  "小清河郊野公园",         116.0450, 39.7350, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "高"),
    (4,  "北京市", "北京市", "通州区", "",  "大运河森林公园",         116.7468, 39.8708, "黑蚱蝉·蒙古寒蝉",         "6–8月",   "中"),
    (5,  "北京市", "北京市", "朝阳区", "",  "温榆河公园",             116.5018, 40.1139, "黑蚱蝉·蒙古寒蝉",         "6–8月",   "中"),
    (6,  "北京市", "北京市", "朝阳区", "",  "镇海寺郊野公园",         116.4863, 39.8288, "黑蚱蝉·蟪蛄",             "6–8月",   "中"),
    (7,  "北京市", "北京市", "大兴区", "",  "碧海公园",               116.4391, 39.8106, "黑蚱蝉·蟪蛄",             "6–8月",   "中"),
    (8,  "北京市", "北京市", "大兴区", "",  "半壁店森林公园",         116.4403, 39.6155, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "中"),
    (9,  "北京市", "北京市", "大兴区", "",  "瀛海滨河绿地",           116.4490, 39.7607, "黑蚱蝉·蟪蛄",             "6–8月",   "中"),
    (10, "北京市", "北京市", "通州区", "",  "潮白河滨河公园",         116.6679, 40.1371, "黑蚱蝉·蒙古寒蝉",         "6–8月",   "中"),
    (11, "北京市", "北京市", "通州区", "",  "台湖湿地公园",           116.5850, 39.7820, "黑蚱蝉·蒙古寒蝉",         "6–8月",   "中"),
    (12, "北京市", "北京市", "丰台区", "",  "南苑森林湿地公园",       116.3800, 39.8300, "黑蚱蝉·蒙古寒蝉·鸣鸣蝉", "6–9月",   "中"),
    (13, "北京市", "北京市", "石景山区", "", "永定河休闲森林公园",    116.1800, 39.9000, "黑蚱蝉·蒙古寒蝉",         "6–8月",   "中"),
    (14, "北京市", "北京市", "顺义区", "",  "汉石桥湿地",             116.7800, 40.1800, "黑蚱蝉·蒙古寒蝉",         "6–9月",   "中"),
    (15, "北京市", "北京市", "海淀区", "",  "翠湖国家城市湿地公园",   116.1800, 40.0500, "黑蚱蝉",                   "6–8月",   "中"),
    (16, "北京市", "北京市", "朝阳区", "",  "黄草湾郊野公园",         116.4350, 40.0300, "黑蚱蝉·蟪蛄",             "6–8月",   "中"),
    (17, "北京市", "北京市", "朝阳区", "",  "将府公园",               116.4900, 39.9800, "黑蚱蝉·蟪蛄",             "6–8月",   "中"),
    (18, "北京市", "北京市", "朝阳区", "",  "黑桥公园",               116.5030, 39.9920, "黑蚱蝉·蟪蛄",             "6–8月",   "中"),
    (19, "北京市", "北京市", "延庆区", "",  "野鸭湖国家湿地公园",     115.8300, 40.4300, "蒙古寒蝉",                 "7–9月",   "中"),
    (20, "北京市", "北京市", "东城区", "",  "天坛公园",               116.4066, 39.8822, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "低"),
    (21, "北京市", "北京市", "海淀区", "",  "颐和园",                 116.2755, 39.9999, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "低"),
    (22, "北京市", "北京市", "朝阳区", "",  "高碑店村",               116.5080, 39.9120, "黑蚱蝉·鸣鸣蝉",           "6–8月",   "中"),
    (23, "北京市", "北京市", "朝阳区", "",  "元大都城垣遗址公园",     116.4200, 39.9400, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "中"),
    (24, "北京市", "北京市", "朝阳区", "",  "朝阳公园",               116.4850, 39.9450, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "中"),
    (25, "北京市", "北京市", "朝阳区", "",  "红领巾公园",             116.5100, 39.9200, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "低"),
    (26, "北京市", "北京市", "朝阳区", "",  "兴隆公园",               116.4900, 39.9250, "黑蚱蝉·蟪蛄",             "6–8月",   "中"),
    (27, "北京市", "北京市", "海淀区", "",  "玉渊潭公园",             116.3800, 39.9900, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "中"),
    (28, "北京市", "北京市", "西城区", "",  "北海公园",               116.3900, 39.9250, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "低"),
    (29, "北京市", "北京市", "西城区", "",  "景山公园",               116.3950, 39.9250, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "低"),
    (30, "北京市", "北京市", "海淀区", "",  "紫竹院公园",             116.3500, 39.9400, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "中"),
    (31, "北京市", "北京市", "西城区", "",  "陶然亭公园",             116.3700, 39.8900, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "低"),
    (32, "北京市", "北京市", "东城区", "",  "龙潭湖公园",             116.4200, 39.8800, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "低"),
    (33, "北京市", "北京市", "海淀区", "",  "香山公园",               116.1850, 39.9850, "蒙古寒蝉·黑蚱蝉·斑透翅蝉", "7–9月", "中"),
    (34, "北京市", "北京市", "海淀区", "",  "圆明园遗址公园",         116.3000, 40.0100, "黑蚱蝉·蒙古寒蝉",         "6–8月",   "中"),
    (35, "北京市", "北京市", "海淀区", "",  "北京植物园（卧佛寺）",   116.2100, 40.0000, "蒙古寒蝉·黑蚱蝉·斑透翅蝉", "7–9月", "中"),
    (36, "北京市", "北京市", "海淀区", "",  "海淀公园",               116.3000, 39.9800, "黑蚱蝉·蟪蛄",             "6–8月",   "中"),
    (37, "北京市", "北京市", "丰台区", "",  "莲花池公园",             116.3200, 39.8800, "黑蚱蝉·蟪蛄",             "6–8月",   "低"),
    (38, "北京市", "北京市", "顺义区", "",  "东郊湿地公园",           116.6800, 40.0800, "黑蚱蝉·蒙古寒蝉",         "6–8月",   "中"),
    (39, "北京市", "北京市", "怀柔区", "",  "雁栖湖",                 116.6700, 40.4000, "蒙古寒蝉·黑蚱蝉·斑透翅蝉", "7–9月", "中"),
    (40, "北京市", "北京市", "怀柔区", "",  "喇叭沟门满族乡（自然森林）", 116.4800, 40.8500, "斑透翅蝉·蒙古寒蝉·黑蚱蝉", "8–9月", "中"),
    (41, "北京市", "北京市", "平谷区", "",  "金海湖",                 117.2400, 40.1800, "蒙古寒蝉·黑蚱蝉·斑透翅蝉", "7–9月", "中"),
    (42, "北京市", "北京市", "延庆区", "",  "千家店镇白河（百里画廊）", 116.2000, 40.5500, "斑透翅蝉·蒙古寒蝉·黑蚱蝉", "8–9月", "中"),
    (43, "北京市", "北京市", "朝阳区", "",  "奥林匹克森林公园（南园）", 116.3900, 39.9700, "黑蚱蝉·蟪蛄·蒙古寒蝉", "6–8月", "高"),
    (44, "北京市", "北京市", "海淀区", "",  "颐和园西堤",             116.2500, 39.9900, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "低"),
    (45, "北京市", "北京市", "东城区", "",  "天坛回音壁",             116.4070, 39.8810, "黑蚱蝉·蟪蛄·蒙古寒蝉",   "6–8月",   "低"),
]

HEADER = ["id", "province", "city", "district", "town",
          "name", "lng", "lat", "species", "peak_season", "abundance",
          "is_famous", "detail", "image_url"]

# 每个点位的"精确微位置"描述（基于公开游记/小红书/抖音等自媒体与公园官方资料整理）
MICRO = {
    1:  "科荟路33号；北园西门进，沿杨树、槐树、柳树林带（南门附近林荫道、湿地木栈道两侧）幼虫与蝉蜕都多。",
    2:  "海淀黑山扈北口19号；大门左转「登山大道」缓坡两侧阔叶林，主峰步道槐树、杨树密集。",
    3:  "房山乡间小路两侧成片阔叶树（柳、杨、榆），本土季鸟猴知名区，林缘土坡洞口多。",
    4:  "北运河两岸；漕运码头、西1门、南门进；河道8.6km两侧柳槐林带，湿地木栈道。",
    5:  "温榆河公园朝阳示范区，一轴一脉五区（森林乐谷/梯田湿地/花溪锦田）乔木林，亲水林带幼虫多。",
    6:  "凉水河沿岸林带，柳杨树密，河堤土坡洞口多。",
    7:  "大兴亦庄 Xiju 片区，园区乔木（杨、槐）行列，草坪边缘树洞多。",
    8:  "团河路片林，成熟杨树纯林，林下松软土坡宜挖猴。",
    9:  "南旱河沿岸绿带，行道柳槐，雨后地面洞口明显。",
    10: "潮白河左岸堤防林，杨柳混交，河滩林地猴多。",
    11: "台湖镇芦苇湿地周边乔木带，林水交错处蝉声密。",
    12: "南苑机场旧址大尺度林地，次生阔叶林（榆、杨、槐）连片。",
    13: "永定河引水渠畔林带，油松、杨槐混交，堤路两侧。",
    14: "顺义木燕路59号，京东大芦荡；环湖木栈道、高台观鸟站周边柳槐。",
    15: "上庄水库畔，芦苇–乔木交错，水边柳树上蝉蜕多。",
    16: "北五环边土坡林地，荆棘阔叶混交，林缘洞口。",
    17: "将台乡铁路遗址绿地，乔木林（杨、槐）与草甸交错。",
    18: "温榆河支流畔，黑桥村林地，杨柳成片。",
    19: "康庄镇官厅水库畔，芦苇–榆林，候鸟区外缘阔叶带。",
    20: "天坛东里甲1号；回音壁、祈年殿古柏区蝉少，公园北侧槐柳林带可捡蜕。",
    21: "新建宫门路19号；西堤、后山、北宫门古树（柳、槐、松），西堤柳堤蝉声佳。",
    22: "通惠河畔漕运文化村，河岸老槐、垂柳，村巷树洞。",
    23: "土城遗址土坡林带（海棠、槐、柳），十号线沿线绿廊。",
    24: "农展馆南路1号；万人广场周边大乔木（杨、槐、柳），人工湖畔林荫。",
    25: "四环路畔，垂柳环湖，城区公园以捡蝉蜕、听鸣为主。",
    26: "高碑店乡，园区槐杨林与健身步道交错。",
    27: "八一湖畔樱柳林，东门进，湖岸柳树蝉蜕易捡。",
    28: "琼华岛、太液池畔古柳，城区公园以捡蜕、听鸣为主。",
    29: "万春亭周边古柏，山前槐树，城区量少以捡蜕为主。",
    30: "南长河、大湖竹柳混交，水畔垂柳蝉声密。",
    31: "华夏名亭园乔木（槐、柳），湖岸林荫捡蜕。",
    32: "龙潭湖畔环湖柳槐，城区以捡蜕、听鸣为主。",
    33: "海淀买卖街40号；碧云寺、双清别墅椴香林，登山步道阔叶树（栾、槐、杨）。",
    34: "西洋楼、福海周边古树（柳、槐、杨），废墟林地猴多。",
    35: "宿根园、树木园栾树、槐、杨，温室山林带。",
    36: "稻香湖路，园区大草坪边槐杨林，亲子挖猴好去处。",
    37: "莲花池畔古柳，城区以捡蝉蜕、听鸣为主。",
    38: "潮白河故道，大片杨树林与湿地交错。",
    39: "雁栖镇湖畔山林（油松、栎、杨），湖光林影。",
    40: "原始次生林（白桦、栎、杨），高海拔8–9月晚蝉。",
    41: "金海湖镇湖畔山林（侧柏、栎、杨），湖区阔叶带。",
    42: "白河峡谷沿岸杨柳，山水林交错。",
    43: "科荟路，南园体育园、乐仕堡周边林带，杨槐柳混交，亲子热门。",
    44: "西堤六桥柳堤，水边垂柳蝉声佳，步道两侧。",
    45: "回音壁–皇穹宇古柏区外侧槐柳林带，清晨捡蜕。",
}

# 可采集物 + 各种玩法的最优时间点（蝉的生物学规律，所有点位通用）
COMMON_DETAIL = (
    "🎒 可采集物（按推荐度）：\n"
    "· 知了幼虫（俗称知了猴/爬叉）：傍晚出土，在树干基部、地面新鲜洞口徒手或小铲捕捉，最肥美，可观察或食用。\n"
    "· 知了皮（蝉蜕）：成虫脱皮后空壳留在树干、枝条上，干燥可入药，成串收集最轻松。\n"
    "· 成虫（黑蚱蝉/蟪蛄/蒙古寒蝉等）：白天鸣叫、翅硬难抓，以「听鸣+观察」为主，不建议大量捕捉。\n\n"
    "⏰ 各种玩法的最优时间点：\n"
    "· 🔦 摸猴/挖幼虫：19:00–22:00（20:00前后出土高峰），雨后傍晚地表湿润最佳；带手电筒、小铲、广口瓶。\n"
    "· 🍃 捡蝉蜕：清晨 6:00–9:00 最佳（一夜脱皮后残留最多），雨后的第二天数量最多。\n"
    "· 🔊 听鸣/观蝉（成虫）：白天 10:00–16:00，尤其午后高温蝉鸣最盛，适合亲子科普。\n"
    "· 🩹 缠胶带诱捕：傍晚在树干离地约1.2米处缠一圈光滑胶带，阻断上爬，次晨统一收取幼虫。"
)

# 实景图（Wikimedia Commons 免费可外链；弱匹配/无图留空，前端将隐藏图片）
IMG = {
    1:  "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Beijing_Olympic_National_Forest_Park_Artificial_Waterfall.jpg/960px-Beijing_Olympic_National_Forest_Park_Artificial_Waterfall.jpg",
    2:  "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/9123626_at_Beijing_Xishan_National_Forest_Park_%2820230220142823%29.jpg/960px-9123626_at_Beijing_Xishan_National_Forest_Park_%2820230220142823%29.jpg",
    4:  "https://upload.wikimedia.org/wikipedia/commons/thumb/2/28/Grand_Canal_Forest_Park_1.jpg/960px-Grand_Canal_Forest_Park_1.jpg",
    5:  "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Beijing_aerial_2.jpg/960px-Beijing_aerial_2.jpg",
    7:  "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/1226602_at_Xiju_%2820231010141355%29.jpg/960px-1226602_at_Xiju_%2820231010141355%29.jpg",
    8:  "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/7839697_at_Bifu_Hwy%2C_Litian_Rd_%2820200922125721%29.jpg/960px-7839697_at_Bifu_Hwy%2C_Litian_Rd_%2820200922125721%29.jpg",
    14: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Shunyi%2C_Beijing%2C_China_-_panoramio_-_jetsun_%2811%29.jpg/960px-Shunyi%2C_Beijing%2C_China_-_panoramio_-_jetsun_%2811%29.jpg",
    15: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Haidian%2C_Beijing%2C_China_-_panoramio_%28111%29.jpg/960px-Haidian%2C_Beijing%2C_China_-_panoramio_%28111%29.jpg",
    20: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/20200110_Temple_of_Heaven-1.jpg/960px-20200110_Temple_of_Heaven-1.jpg",
    21: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/24/Kunming_Lake_Summer_Palace_Beijing_%283%29.jpg/960px-Kunming_Lake_Summer_Palace_Beijing_%283%29.jpg",
    23: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/East_View_of_the_West_Gate_of_Beijing_Yuandadu_Site_Park.jpg/960px-East_View_of_the_West_Gate_of_Beijing_Yuandadu_Site_Park.jpg",
    24: "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Amateur_concert_in_Chaoyang_Park_20240727184447.jpg/960px-Amateur_concert_in_Chaoyang_Park_20240727184447.jpg",
    27: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Concourse_of_Yuyuantan_Park_East_Gate_Station_%2820211231113027%29.jpg/960px-Concourse_of_Yuyuantan_Park_East_Gate_Station_%2820211231113027%29.jpg",
    28: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/Beihai_Park_Br%C3%BCcke-20110104-RM-105624.jpg/960px-Beihai_Park_Br%C3%BCcke-20110104-RM-105624.jpg",
    29: "https://upload.wikimedia.org/wikipedia/commons/thumb/7/71/Beijing_Jingshan_Park_Pavilion_%2810553761515%29.jpg/960px-Beijing_Jingshan_Park_Pavilion_%2810553761515%29.jpg",
    30: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/A_Black-crowned_Night-heron_in_the_wetland_of_Zizhuyuan_Park%2C_Beijing.jpg/960px-A_Black-crowned_Night-heron_in_the_wetland_of_Zizhuyuan_Park%2C_Beijing.jpg",
    31: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/20211005_Stela_in_front_of_the_Cundi_Hall%2C_Taoranting_Park.jpg/960px-20211005_Stela_in_front_of_the_Cundi_Hall%2C_Taoranting_Park.jpg",
    32: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Longtanhu_Park%2C_Beijing_%E5%8C%97%E4%BA%AC%E9%BE%8D%E6%BD%AD%E6%B9%96%E5%85%AC%E5%9C%92_-_panoramio.jpg/960px-Longtanhu_Park%2C_Beijing_%E5%8C%97%E4%BA%AC%E9%BE%8D%E6%BD%AD%E6%B9%96%E5%85%AC%E5%9C%92_-_panoramio.jpg",
    33: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Duoyun_Pavilion%2C_Fragrant_Hills_%2820190918154424%29.jpg/960px-Duoyun_Pavilion%2C_Fragrant_Hills_%2820190918154424%29.jpg",
    34: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Old_Summer_Palace%2C_Palace_Gates_of_Qichunyuan.jpg/960px-Old_Summer_Palace%2C_Palace_Gates_of_Qichunyuan.jpg",
    35: "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b0/Beijing_Botanical_Garden_-_Oct_09_-_IMG_1193.jpg/960px-Beijing_Botanical_Garden_-_Oct_09_-_IMG_1193.jpg",
    36: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/East_Entrace_of_Haidian_Park.jpg/960px-East_Entrace_of_Haidian_Park.jpg",
    37: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Gate_of_Lianhuachi_Park_%2820150118151133%29.JPG/960px-Gate_of_Lianhuachi_Park_%2820150118151133%29.JPG",
    38: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/Shunyi%2C_Beijing%2C_China_-_panoramio_-_jetsun_%2810%29.jpg/960px-Shunyi%2C_Beijing%2C_China_-_panoramio_-_jetsun_%2810%29.jpg",
    39: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Beijing_Yanqi_Lake_International_Convention_and_Exhibition_Center_%2820190915160152%29.jpg/960px-Beijing_Yanqi_Lake_International_Convention_and_Exhibition_Center_%2820190915160152%29.jpg",
    40: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Birch_forest_at_Labagoumen_%2820201025151159%29.jpg/960px-Birch_forest_at_Labagoumen_%2820201025151159%29.jpg",
    43: "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Exit_D_of_Forest_Park_South_Gate_Station_%2820210404164842%29.jpg/960px-Exit_D_of_Forest_Park_South_Gate_Station_%2820210404164842%29.jpg",
    44: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d1/Summer_Palace_Willows_%2813598138%29.jpg/960px-Summer_Palace_Willows_%2813598138%29.jpg",
    45: "https://upload.wikimedia.org/wikipedia/commons/thumb/0/06/Beijing_-_Temple_of_Heaven_Park_IMG_5012_Echo_Wall_-_Imperial_Vault_of_Heaven.jpg/960px-Beijing_-_Temple_of_Heaven_Park_IMG_5012_Echo_Wall_-_Imperial_Vault_of_Heaven.jpg",
}


def build(path: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "cicada_points"
    ws.append(HEADER)
    for r in ROWS:
        rid, prov, city, dist, town, name, lng, lat, sp, peak, ab = r
        detail = "📍 精确位置：" + MICRO.get(rid, "") + "\n\n" + COMMON_DETAIL
        image_url = IMG.get(rid, "")
        ws.append([rid, prov, city, dist, town, name, lng, lat,
                   sp, peak, ab, ab == "高", detail, image_url])
    wb.save(path)
    print(f"已生成 Excel：{path}（{len(ROWS)} 行）")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "data" / "cicada_points.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    build(str(out))
