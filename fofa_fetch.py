import os
import re
import requests
import time
import concurrent.futures
import subprocess
from datetime import datetime, timezone, timedelta
import socket

# ===============================
# 配置区
FOFA_URLS = {
    "https://fofa.info/result?qbase64=InVkcHh5IiAmJiBjb3VudHJ5PSJDTiI%3D": "ip.txt",
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

COUNTER_FILE = "计数.txt"
IP_DIR = "ip"
RTP_DIR = "rtp"
ZUBO_FILE = "zubo.txt"
IPTV_FILE = "IPTV.txt"

# ===============================
# 分类与映射配置
CHANNEL_CATEGORIES = {
    "央视频道": [
        "CCTV-1综合", "CCTV-2财经", "CCTV-3综艺", "CCTV-4中文国际", "CCTV-4欧洲", "CCTV-4美洲", "CCTV-5体育", "CCTV-5+体育赛事",
        "CCTV-6电影", "CCTV-7国防军事", "CCTV-8电视剧", "CCTV-9纪录", "CCTV-10科教", "CCTV-11戏曲", "CCTV-12社会与法", "CCTV-13新闻",
        "CCTV-14少儿", "CCTV-15音乐", "CCTV-16奥林匹克", "CCTV-17农业农村", "CCTV-4K超高清", "CCTV-8K超高清",
        "兵器科技", "风云音乐", "风云足球", "风云剧场", "怀旧剧场", "第一剧场", "女性时尚", "世界地理", "央视台球", "高尔夫网球",
        "央视文化精品", "卫生健康", "电视指南", "中学生", "发现之旅", "书法频道", "国学频道", "环球奇观", "峨眉电影4K", "翡翠台", "明珠台",
    ],
    "卫视频道": [
        "湖南卫视", "湖南卫视4K", "浙江卫视", "江苏卫视", "江苏卫视4K", "东方卫视", "东方卫视4K","深圳卫视", "深圳卫视4K", "北京卫视", "北京卫视4K", 
        "广东卫视", "广东卫视4K", "广西卫视", "东南卫视", "海南卫视", "河北卫视", "河南卫视", "湖北卫视", "江西卫视", "四川卫视",
        "四川卫视4K", "重庆卫视", "贵州卫视", "云南卫视", "天津卫视", "安徽卫视", "山东卫视", "山东卫视4K", "辽宁卫视", "黑龙江卫视", "吉林卫视",
        "内蒙古卫视", "宁夏卫视", "山西卫视", "陕西卫视", "甘肃卫视", "青海卫视", "新疆卫视", "西藏卫视", "三沙卫视", "兵团卫视", "延边卫视",
        "安多卫视", "康巴卫视", "农林卫视", "山东教育卫视", "中国教育1台", "中国教育2台", "中国教育3台", "中国教育4台", "早期教育", "新视觉HD",
        "绚影4K", "4K乐享", "大湾区卫视", "澳亚卫视", "广州竞赛", "咖秀综艺", "爱宠宠物",  
    ],
    "数字频道": [
        "CHC动作电影", "CHC家庭影院", "CHC影迷电影", "淘电影", "淘精彩", "淘剧场", "淘4K", "淘娱乐",  "淘萌宠", "重温经典",
        "星空卫视", "CHANNEL[V]", "凤凰卫视中文台", "凤凰卫视资讯台", "凤凰卫视香港台", "凤凰卫视电影台", "求索纪录", "求索科学",
        "求索生活", "求索动物", "纪实人文", "金鹰纪实", "纪实科教", "睛彩竞技", "睛彩篮球", "睛彩广场舞", "魅力足球", "五星体育",
        "劲爆体育", "快乐垂钓", "四海钓鱼", "来钓鱼吧", "茶频道", "先锋乒羽", "天元围棋", "汽摩", "梨园频道", "文物宝库", "法制天地", 
        "乐游", "生活时尚", "都市剧场", "欢笑剧场", "游戏风云", "武术世界", "哒啵赛事", "哒啵电竞", "中国交通", "中国天气",  
        "华数4K", "华数星影", "华数动作影院", "华数喜剧影院", "华数家庭影院", "华数经典电影", "华数热播剧场", "华数碟战剧场",
        "华数军旅剧场", "华数城市剧场", "华数武侠剧场", "华数古装剧场", "华数魅力时尚", "峨眉电影", "爱体育", "爱历史", "爱动漫", 
        "爱喜剧", "爱奇谈", "爱幼教", "爱悬疑", "爱旅行", "爱浪漫", "爱玩具", "爱科幻", "爱谍战", "爱赛车", "爱院线", "BesTV-4K", "BesTV4K-1", 
        "BesTV4K-2", "CBN每日影院", "CBN幸福娱乐", "CBN幸福剧场", "CBN风尚生活", "爱探索", "爱青春", "爱怀旧", "爱经典", "爱都市", "爱家庭",
        "NEWTV家庭剧场", "NEWTV精品纪录", "NEWTV健康有约", "NEWTV精品体育", "NEWTV军事评论", "NEWTV农业致富", "NEWTV古装剧场", "NEWTV动作电影",
        "NEWTV军旅剧场", "NEWTV惊悚悬疑", "NewTV海外剧场", "NewTV搏击", "NewTV明星大片", "NewTV爱情喜剧", "NewTV精品大剧", "NewTV中国功夫",
        "NewTV金牌综艺",
    ],
    "少儿教育": [
        "乐龄学堂", "少儿天地", "动漫秀场", "淘BABY", "黑莓动画", "睛彩青少", "金色学堂", "新动漫", "卡酷少儿", "金鹰卡通", "优漫卡通", "哈哈炫动", "嘉佳卡通",
     "华数少儿动画", "华数动画", "亲子趣学", "少儿天地",
    ],
     "湖北": [
        "湖北公共新闻", "湖北经视频道", "湖北综合频道", "湖北垄上频道", "湖北影视频道", "湖北生活频道", "湖北教育频道", "武汉新闻综合", "武汉电视剧", "武汉科技生活",
        "武汉文体频道", "武汉教育频道", "阳新综合", "房县综合", "蔡甸综合",
    ],
}

# ===== 映射（别名 -> 标准名） =====
CHANNEL_MAPPING = {
    "CCTV-1综合": ["CCTV-1", "CCTV-1 HD", "CCTV1 HD", "CCTV1"],
    "CCTV-2财经": ["CCTV-2", "CCTV-2 HD", "CCTV2 HD", "CCTV2"],
    "CCTV-3综艺": ["CCTV-3", "CCTV-3 HD", "CCTV3 HD", "CCTV3"],
    "CCTV-4中文国际": ["CCTV-4", "CCTV-4 HD", "CCTV4 HD", "CCTV4"],
    "CCTV-4欧洲": ["CCTV-4欧洲", "CCTV-4欧洲", "CCTV4欧洲 HD", "CCTV-4 欧洲", "CCTV-4中文国际欧洲", "CCTV4"],
    "CCTV-4美洲": ["CCTV-4美洲", "CCTV-4北美", "CCTV4美洲 HD", "CCTV-4 美洲", "CCTV-4中文国际美洲", "CCTV4"],
    "CCTV-5体育": ["CCTV-5", "CCTV-5 HD", "CCTV5 HD", "CCTV5"],
    "少儿天地": ["睛彩少儿HD", "精彩连播"],
    "乐龄学堂": ["睛彩学堂HD", "精彩连播"],
    "动漫秀场": ["动漫秀场", "睛彩亲子HD", "精彩连播"],
    "咖秀综艺": ["睛彩综艺HD", "精彩连播"],
    "爱宠宠物": ["睛彩爱宠HD", "精彩连播"],
    "新视觉HD": ["新视觉"],
    "CCTV-5+体育赛事": ["CCTV-5+", "CCTV-5+ HD", "CCTV5+ HD", "CCTV5+"],
    "CCTV-6电影": ["CCTV-6", "CCTV-6 HD", "CCTV6 HD", "CCTV6"],
    "CCTV-7国防军事": ["CCTV-7", "CCTV-7 HD", "CCTV7 HD", "CCTV7"],
    "CCTV-8电视剧": ["CCTV-8", "CCTV-8 HD", "CCTV8 HD", "CCTV8"],
    "CCTV-9纪录": ["CCTV-9", "CCTV-9 HD", "CCTV9 HD", "CCTV9"],
    "CCTV-10科教": ["CCTV-10", "CCTV-10 HD", "CCTV10 HD", "CCTV10"],
    "CCTV-11戏曲": ["CCTV-11", "CCTV-11 HD", "CCTV11 HD", "CCTV11"],
    "CCTV-12社会与法": ["CCTV-12", "CCTV-12 HD", "CCTV12 HD", "CCTV12"],
    "CCTV-13新闻": ["CCTV-13", "CCTV-13 HD", "CCTV13 HD", "CCTV13"],
    "CCTV-14少儿": ["CCTV-14", "CCTV-14 HD", "CCTV14 HD", "CCTV14"],
    "CCTV-15音乐": ["CCTV-15", "CCTV-15 HD", "CCTV15 HD", "CCTV15"],
    "CCTV-16奥林匹克": ["CCTV-16", "CCTV-16 HD", "CCTV-16 4K", "CCTV16", "CCTV16 4K", "CCTV-16奥林匹克4K"],
    "CCTV-17农业农村": ["CCTV-17", "CCTV-17 HD", "CCTV17 HD", "CCTV17"],
    "CCTV-4K超高清": ["CCTV4K超高清", "CCTV4K", "CCTV-4K 超高清", "CCTV 4K"],
    "CCTV-8K超高清": ["CCTV8K超高清", "CCTV8K", "CCTV-8K 超高清", "CCTV 8K"],
    "兵器科技": ["CCTV-兵器科技", "CCTV兵器科技"],
    "风云音乐": ["CCTV-风云音乐", "CCTV风云音乐"],
    "第一剧场": ["CCTV-第一剧场", "CCTV第一剧场"],
    "风云足球": ["CCTV-风云足球", "CCTV风云足球"],
    "风云剧场": ["CCTV-风云剧场", "CCTV风云剧场"],
    "怀旧剧场": ["CCTV-怀旧剧场", "CCTV怀旧剧场"],
    "女性时尚": ["CCTV-女性时尚", "CCTV女性时尚"],
    "世界地理": ["CCTV-世界地理", "CCTV世界地理"],
    "央视台球": ["CCTV-央视台球", "CCTV央视台球"],
    "高尔夫网球": ["CCTV-高尔夫网球", "CCTV高尔夫网球", "CCTV央视高网", "CCTV-高尔夫·网球", "央视高网"],
    "央视文化精品": ["CCTV-央视文化精品", "CCTV央视文化精品", "CCTV文化精品", "CCTV-文化精品", "文化精品"],
    "卫生健康": ["CCTV-卫生健康", "CCTV卫生健康"],
    "电视指南": ["CCTV-电视指南", "CCTV电视指南"],
    "农林卫视": ["陕西农林卫视"],
    "三沙卫视": ["海南三沙卫视"],
    "兵团卫视": ["新疆兵团卫视"],
    "延边卫视": ["吉林延边卫视"],
    "安多卫视": ["青海安多卫视"],
    "康巴卫视": ["四川康巴卫视"],
    "山东教育卫视": ["山东教育"],
    "书法频道": ["书画", "书画HD", "书画", "书画频道"],
    "国学频道": ["国学", "国学高清", "国学HD"],
    "翡翠台": ["TVB翡翠台", "无线翡翠台", "翡翠台"],
    "明珠台": ["明珠台", "无线明珠台", "TVB明珠台"],
    "中国教育1台": ["CETV1", "中国教育一台", "中国教育1", "CETV-1 综合教育", "CETV-1"],
    "中国教育2台": ["CETV2", "中国教育二台", "中国教育2", "CETV-2 空中课堂", "CETV-2"],
    "中国教育3台": ["CETV3", "中国教育三台", "中国教育3", "CETV-3 教育服务", "CETV-3"],
    "中国教育4台": ["CETV4", "中国教育四台", "中国教育4", "CETV-4 职业教育", "CETV-4"],
    "早期教育": ["中国教育5台", "中国教育五台", "CETV早期教育", "华电早期教育", "CETV 早期教育"],
    "新视觉HD": ["新视觉", "新视觉hd", "新视觉高清"],
    "湖南卫视": ["湖南卫视4K"],
    "北京卫视": ["北京卫视4K"],
    "东方卫视": ["东方卫视4K"],
    "广东卫视": ["广东卫视4K"],
    "深圳卫视": ["深圳卫视4K"],
    "山东卫视": ["山东卫视4K"],
    "四川卫视": ["四川卫视4K"],
    "浙江卫视": ["浙江卫视4K"],
    "CHC影迷电影": ["CHC影迷电影HD", "CHC-影迷电影", "影迷电影", "chc影迷电影高清"],
    "CHC家庭影院": ["CHC-家庭影院", "CHC家庭影院HD", "chc家庭影院高清"], 
    "CHC动作电影": ["CHC-动作电影", "CHC动作电影HD", "CHC高清电影", "chc动作电影高清"],
    "淘电影": ["IPTV淘电影", "北京IPTV淘电影", "北京淘电影"],
    "淘精彩": ["IPTV淘精彩", "北京IPTV淘精彩", "北京淘精彩"],
    "淘剧场": ["IPTV淘剧场", "北京IPTV淘剧场", "北京淘剧场"],
    "淘4K": ["IPTV淘4K", "北京IPTV4K超高清", "北京淘4K", "淘4K", "淘 4K"],
    "淘娱乐": ["IPTV淘娱乐", "北京IPTV淘娱乐", "北京淘娱乐"],
    "淘BABY": ["IPTV淘BABY", "北京IPTV淘BABY", "北京淘BABY", "IPTV淘baby", "北京IPTV淘baby", "北京淘baby", "淘Baby", "淘宝贝"],
    "淘萌宠": ["IPTV淘萌宠", "北京IPTV萌宠TV", "北京淘萌宠", "萌宠TV"],
    "魅力足球": ["上海魅力足球"],
    "睛彩青少": ["睛彩羽毛球", "睛彩青少HD", "睛彩青少高清", "睛彩青少hd"],
    "睛彩广场舞":["睛彩广场舞HD", "睛彩广场舞高清", "睛彩广场舞hd"],
    "睛彩竞技":["睛彩竞技高清", "睛彩竞技HD", "睛彩竞技hd"],
    "睛彩篮球":["睛彩篮球HD", "睛彩篮球高清", "睛彩篮球hd"],
    "求索纪录": ["求索记录", "求索纪录HD", "求索记录4K", "求索纪录 4K", "求索记录 4K"],
    "金鹰纪实": ["湖南金鹰纪实", "金鹰记实" "金鹰纪实HD"],
    "纪实科教": ["北京纪实科教", "BRTV纪实科教", "纪实科教8K"],
    "星空卫视": ["星空衛視", "星空衛视", "星空卫視"],
    "CHANNEL[V]": ["CHANNEL-V", "Channel[V]HD", "ChannelV"],
    "凤凰卫视中文台": ["凤凰中文", "凤凰中文台", "凤凰卫视中文", "凤凰卫视"],
    "凤凰卫视香港台": ["凤凰香港台", "凤凰卫视香港", "凤凰香港"],
    "凤凰卫视资讯台": ["凤凰资讯", "凤凰资讯台", "凤凰咨询", "凤凰咨询台", "凤凰卫视咨询台", "凤凰卫视资讯", "凤凰卫视咨询"],
    "凤凰卫视电影台": ["凤凰电影", "凤凰电影台", "凤凰卫视电影", "鳳凰衛視電影台", " 凤凰电影"],
    "茶频道": ["湖南茶频道"],
    "快乐垂钓": ["湖南快乐垂钓", "快乐垂钓HD"],
    "四海钓鱼": ["四海钓鱼HD"],
    "来钓鱼吧": ["来钓鱼吧HD", "睛彩钓鱼HD"],
    "先锋乒羽": ["湖南先锋乒羽"],
    "天元围棋": ["天元围棋频道", "天元围棋HD"],
    "汽摩": ["重庆汽摩", "汽摩频道", "重庆汽摩频道"],
    "梨园频道": ["河南梨园频道", "梨园", "河南梨园", "梨园频道HD"],
    "法制天地": ["法治天地HD"],
    "文物宝库": ["河南文物宝库"],
    "武术世界": ["河南武术世界"],
    "乐游": ["乐游频道", "上海乐游频道", "乐游纪实", "SiTV乐游频道", "SiTV 乐游频道", "乐游HD"],
    "欢笑剧场": ["上海欢笑剧场4K", "欢笑剧场 4K", "欢笑剧场4K", "上海欢笑剧场"],
    "生活时尚": ["生活时尚4K", "SiTV生活时尚", "上海生活时尚", "生活时尚HD"],
    "都市剧场": ["都市剧场4K", "SiTV都市剧场", "上海都市剧场", "都市剧场HD"],
    "游戏风云": ["游戏风云4K", "SiTV游戏风云", "上海游戏风云", "游戏风云HD"],
    "金色学堂": ["金色学堂4K", "SiTV金色学堂", "上海金色学堂", "金色学堂HD"],
    "动漫秀场": ["动漫秀场4K", "SiTV动漫秀场", "上海动漫秀场"],
    "卡酷少儿": ["北京KAKU少儿", "BRTV卡酷少儿", "北京卡酷少儿", "卡酷动画"],
    "哈哈炫动": ["炫动卡通", "上海哈哈炫动"],
    "优漫卡通": ["江苏优漫卡通", "优漫漫画"],
    "金鹰卡通": ["湖南金鹰卡通"],
    "中国交通": ["中国交通频道"],
    "中国天气": ["中国天气频道"],
    "亲子趣学": ["睛彩亲子4K"],
    "华数4K": ["华数低于4K", "华数4K电影", "华数爱上4K", "爱上4K"],
    "华数热播剧场": ["IPTV热播剧场"],
    "华数星影": ["星影", "华数电影7"],
    "华数动作影院": ["华数电影5"],
    "华数喜剧影院": ["华数电影4"],
    "华数家庭影院": ["华数电影6"], 
    "华数经典电影": ["IPTV经典电影", "经典电影", "华数电影2"],
    "华数碟战剧场": ["IPTV谍战剧场"],
    "华数少儿动画": ["IPTV少儿动画"],
    "华数动画": ["华数动画", "华数卡通"],
    "峨眉电影": ["四川峨眉HD", "峨眉电影高清", "峨眉电影", "四川峨眉", "四川峨眉", "四川峨眉高清"],
    "峨眉电影4K": ["4K超高清电影"],
    "绚影4K": ["绚影4K", "睛彩绚影4K", "精彩连播", "天府绚影高清影院"],
    "4K乐享": ["乐享4K"],
    "爱体育": ["爱体育HD", "IHOT爱体育", "HOT爱体育"],
    "爱历史": ["爱历史HD", "IHOT爱历史", "HOT爱历史"], 
    "爱动漫": ["爱动漫HD", "IHOT爱动漫", "HOT爱动漫"], 
    "爱喜剧": ["爱喜剧HD", "IHOT爱喜剧", "HOT爱喜剧"],
    "爱奇谈": ["爱奇谈HD", "IHOT爱奇谈", "HOT爱奇谈"], 
    "爱幼教": ["爱幼教HD", "IHOT爱幼教", "HOT爱幼教"], 
    "爱悬疑": ["爱悬疑HD", "IHOT爱悬疑", "HOT爱悬疑"],
    "爱旅行": ["爱旅行HD", "IHOT爱旅行", "HOT爱旅行"], 
    "爱浪漫": ["爱浪漫HD", "IHOT爱浪漫", "HOT爱浪漫"],
    "爱玩具": ["爱玩具HD", "IHOT爱玩具", "HOT爱玩具"],
    "爱科幻": ["爱科幻HD", "IHOT爱科幻", "HOT爱科幻"],
    "爱谍战": ["爱谍战HD", "IHOT爱谍战", "HOT爱谍战"],
    "爱赛车": ["爱谍战HD", "IHOT爱赛车", "HOT爱赛车"],
    "爱院线": ["爱院线HD", "IHOT爱院线", "HOT爱院线"],
    "爱科学": ["爱科学HD", "IHOT爱科学", "HOT爱科学"],
    "爱探索": ["爱探索HD", "THOT爱探索", "HOT爱探索"],
    "爱青春": ["爱青春HD", "IHOT爱青春", "HOT爱青春"]'
    "爱怀旧": ["爱怀旧HD", "IHOT爱怀旧", "HOT爱怀旧"],
    "爱经典": ["爱经典HD", "IHOT爱经典", "HOT经典"],
    "爱都市": ["爱都市HD", "IHOT爱都市", "HOT爱都市"],
    "爱家庭": ["爱家庭HD", "IHOT爱家庭", "HOT爱家庭"],
    "环球奇观": ["环球奇观HD"],
}

# ===== 运营商识别配置 =====
ISP_CONFIG = {
    "电信": {
        "api_keywords": ["telecom", "ct", "chinatelecom", "电信", "chinanet"],
        "ip_patterns": [
            r"^1[0-9]{2}\.", r"^2[0-3]{2}\.", r"^42\.", r"^43\.", r"^58\.", r"^59\.", r"^60\.", r"^61\.",
            r"^110\.", r"^111\.", r"^112\.", r"^113\.", r"^114\.", r"^115\.", r"^116\.", r"^117\.", r"^118\.", r"^119\.",
            r"^120\.", r"^121\.", r"^122\.", r"^123\.", r"^124\.", r"^125\.", r"^126\.", r"^127\.", r"^175\.", r"^180\.",
            r"^182\.", r"^183\.", r"^184\.", r"^185\.", r"^186\.", r"^187\.", r"^188\.", r"^189\.", r"^223\."
        ]
    },
    "联通": {
        "api_keywords": ["unicom", "cu", "chinaunicom", "联通", "网通", "cnc", "联通宽带"],
        "ip_patterns": [
            r"^42\.", r"^43\.", r"^58\.", r"^59\.", r"^60\.", r"^61\.", r"^110\.", r"^111\.", r"^112\.", r"^113\.",
            r"^114\.", r"^115\.", r"^116\.", r"^117\.", r"^118\.", r"^119\.", r"^120\.", r"^121\.", r"^122\.", r"^123\.",
            r"^124\.", r"^125\.", r"^126\.", r"^127\.", r"^175\.", r"^180\.", r"^182\.", r"^183\.", r"^184\.", r"^185\.",
            r"^186\.", r"^187\.", r"^188\.", r"^189\.", r"^223\."
        ]
    },
    "移动": {
        "api_keywords": ["mobile", "cm", "chinamobile", "移动", "铁通", "cmnet", "中国移动"],
        "ip_patterns": [
            r"^223\.", r"^36\.", r"^37\.", r"^38\.", r"^39\.", r"^100\.", r"^101\.", r"^102\.", r"^103\.", r"^104\.",
            r"^105\.", r"^106\.", r"^107\.", r"^108\.", r"^109\.", r"^134\.", r"^135\.", r"^136\.", r"^137\.", r"^138\.",
            r"^139\.", r"^150\.", r"^151\.", r"^152\.", r"^157\.", r"^158\.", r"^159\.", r"^170\.", r"^178\.", r"^182\.",
            r"^183\.", r"^184\.", r"^187\.", r"^188\.", r"^189\.", r"^240\.", r"^241\.", r"^242\.", r"^243\."
        ]
    },
    "广电": {
        "api_keywords": ["broadcast", "gd", "cbn", "广电", "有线", "歌华", "东方有线", "华数", "天威", "江苏有线", 
                        "湖北广电", "有线电视", "数字电视", "广播电视"],
        "ip_patterns": [
            r"^123\.", r"^124\.", r"^125\.", r"^126\.", r"^127\.", r"^192\.168\.", r"^10\.",
            r"^172\.(1[6-9]|2[0-9]|3[0-1])\."
        ]
    },
    "长城宽带": {
        "api_keywords": ["greatwall", "gwb", "长城宽带", "鹏博士", "pengboshi"],
        "ip_patterns": [
            r"^124\.238\.", r"^124\.239\.", r"^125\.33\.", r"^125\.39\.", r"^125\.76\.",
            r"^211\.161\.", r"^219\.148\.", r"^222\.222\.", r"^222\.223\."
        ]
    },
    "教育网": {
        "api_keywords": ["edu", "cernet", "教育网", "校园网", "大学", "学校"],
        "ip_patterns": [
            r"^202\.112\.", r"^202\.113\.", r"^202\.114\.", r"^202\.115\.", r"^202\.116\.", r"^202\.117\.", r"^202\.118\.",
            r"^202\.119\.", r"^202\.120\.", r"^202\.121\.", r"^202\.122\.", r"^202\.123\.", r"^202\.124\.", r"^202\.125\.",
            r"^202\.126\.", r"^202\.127\.", r"^210\.32\.", r"^210\.33\.", r"^210\.34\.", r"^210\.35\.", r"^210\.36\.",
            r"^210\.37\.", r"^210\.38\."
        ]
    },
    "阿里云": {
        "api_keywords": ["aliyun", "alibaba", "阿里云", "alicloud"],
        "ip_patterns": [
            r"^47\.", r"^100\.64\.", r"^100\.65\.", r"^100\.66\.", r"^100\.67\.", r"^100\.68\.", r"^100\.69\.",
            r"^100\.70\.", r"^100\.71\.", r"^100\.72\.", r"^100\.73\.", r"^100\.74\.", r"^100\.75\.", r"^100\.76\.",
            r"^100\.77\.", r"^100\.78\.", r"^100\.79\.", r"^100\.80\.", r"^100\.81\.", r"^100\.82\.", r"^100\.83\.",
            r"^100\.84\.", r"^100\.85\.", r"^100\.86\.", r"^100\.87\.", r"^100\.88\.", r"^100\.89\.", r"^100\.90\.",
            r"^100\.91\.", r"^100\.92\.", r"^100\.93\.", r"^100\.94\.", r"^100\.95\.", r"^100\.96\.", r"^100\.97\.",
            r"^100\.98\.", r"^100\.99\.", r"^100\.100\.", r"^100\.101\.", r"^100\.102\.", r"^100\.103\.", r"^100\.104\.",
            r"^100\.105\.", r"^100\.106\.", r"^100\.107\.", r"^100\.108\.", r"^100\.109\.", r"^100\.110\.", r"^100\.111\.",
            r"^100\.112\.", r"^100\.113\.", r"^100\.114\.", r"^100\.115\.", r"^100\.116\.", r"^100\.117\.", r"^100\.118\.",
            r"^100\.119\.", r"^100\.120\.", r"^100\.121\.", r"^100\.122\.", r"^100\.123\.", r"^100\.124\.", r"^100\.125\.",
            r"^100\.126\.", r"^100\.127\.", r"^118\.31\.", r"^121\.42\."
        ]
    },
    "腾讯云": {
        "api_keywords": ["tencent", "qcloud", "腾讯云", "tencent cloud"],
        "ip_patterns": [
            r"^101\.", r"^103\.", r"^111\.", r"^112\.", r"^113\.", r"^114\.", r"^115\.", r"^116\.", r"^117\.", r"^118\.",
            r"^119\.", r"^120\.", r"^121\.", r"^122\.", r"^123\.", r"^124\.", r"^125\.", r"^129\.", r"^140\.", r"^143\.",
            r"^150\.", r"^157\.", r"^162\.", r"^163\.", r"^171\.", r"^175\.", r"^180\.", r"^183\.", r"^202\.", r"^203\.",
            r"^210\.", r"^211\.", r"^218\.", r"^219\.", r"^220\.", r"^221\.", r"^222\."
        ]
    },
    "华为云": {
        "api_keywords": ["huawei", "huaweicloud", "华为云", "hwcloud"],
        "ip_patterns": [
            r"^124\.70\.", r"^139\.9\.", r"^139\.159\.", r"^139\.224\.", r"^150\.158\.", r"^182\.92\.", r"^202\.105\.151\.",
            r"^202\.105\.152\.", r"^202\.105\.153\.", r"^202\.105\.154\.", r"^202\.105\.155\.", r"^202\.105\.156\.",
            r"^202\.105\.157\.", r"^202\.105\.158\.", r"^202\.105\.159\.", r"^202\.105\.160\.", r"^202\.105\.161\.",
            r"^202\.105\.162\.", r"^202\.105\.163\.", r"^202\.105\.164\.", r"^202\.105\.165\.", r"^202\.105\.166\.",
            r"^202\.105\.167\.", r"^202\.105\.168\.", r"^202\.105\.169\.", r"^202\.105\.170\.", r"^202\.105\.171\.",
            r"^202\.105\.172\.", r"^202\.105\.173\.", r"^202\.105\.174\.", r"^202\.105\.175\."
        ]
    },
    "其他": {
        "api_keywords": [],
        "ip_patterns": []
    }
}

# ===============================
def get_run_count():
    if os.path.exists(COUNTER_FILE):
        try:
            return int(open(COUNTER_FILE, "r", encoding="utf-8").read().strip() or "0")
        except Exception:
            return 0
    return 0

def save_run_count(count):
    try:
        with open(COUNTER_FILE, "w", encoding="utf-8") as f:
            f.write(str(count))
    except Exception as e:
        print(f"⚠️ 写计数文件失败：{e}")


# ===============================
def get_isp_from_api(data):
    """从API数据获取运营商信息（支持多种运营商）"""
    isp_raw = (data.get("isp") or "").lower()
    org_raw = (data.get("org") or "").lower()
    as_raw = (data.get("as") or "").lower()
    
    # 合并所有可能的文本信息
    all_text = f"{isp_raw} {org_raw} {as_raw}"
    
    # 遍历所有运营商配置
    for isp_name, config in ISP_CONFIG.items():
        for keyword in config["api_keywords"]:
            if keyword.lower() in all_text:
                return isp_name
    
    return "其他"


def get_isp_by_regex(ip):
    """通过IP地址正则匹配运营商"""
    # 遍历所有运营商配置
    for isp_name, config in ISP_CONFIG.items():
        for pattern in config["ip_patterns"]:
            if re.match(pattern, ip):
                return isp_name
    
    # 尝试根据知名IP段进一步判断
    if re.match(r"^192\.168\.", ip) or re.match(r"^10\.", ip) or re.match(r"^172\.(1[6-9]|2[0-9]|3[0-1])\.", ip):
        return "内网"
    
    return "其他"


def get_combined_isp(data, ip):
    """综合判断运营商"""
    # 首先尝试API判断
    isp_api = get_isp_from_api(data)
    if isp_api != "其他":
        return isp_api
    
    # 然后尝试IP正则匹配
    isp_regex = get_isp_by_regex(ip)
    if isp_regex != "其他":
        return isp_regex
    
    # 最后根据ASN信息判断（如果有）
    as_info = data.get("as", "").lower()
    if "cmnet" in as_info:
        return "移动"
    elif "unicom" in as_info:
        return "联通"
    elif "chinanet" in as_info:
        return "电信"
    elif "cernet" in as_info or "edu" in as_info:
        return "教育网"
    elif "aliyun" in as_info:
        return "阿里云"
    elif "tencent" in as_info:
        return "腾讯云"
    elif "huawei" in as_info:
        return "华为云"
    elif "greatwall" in as_info or "gwb" in as_info:
        return "长城宽带"
    
    return "其他"


# ===============================
# 第一阶段
def first_stage():
    os.makedirs(IP_DIR, exist_ok=True)
    all_ips = set()

    for url, filename in FOFA_URLS.items():
        print(f"📡 正在爬取 {filename} ...")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            urls_all = re.findall(r'<a href="http://(.*?)"', r.text)
            all_ips.update(u.strip() for u in urls_all if u.strip())
            print(f"✅ 从 {filename} 获取到 {len(urls_all)} 个链接")
        except Exception as e:
            print(f"❌ 爬取失败：{e}")
        time.sleep(3)

    province_isp_dict = {}
    print(f"🌐 开始解析 {len(all_ips)} 个IP地址...")
    
    processed_count = 0
    for ip_port in all_ips:
        try:
            processed_count += 1
            host = ip_port.split(":")[0]

            # 判断是否为IP地址
            is_ip = re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host)

            if not is_ip:
                try:
                    resolved_ip = socket.gethostbyname(host)
                    print(f"[{processed_count}/{len(all_ips)}] 🌐 域名解析成功: {host} → {resolved_ip}")
                    ip = resolved_ip
                except Exception:
                    print(f"[{processed_count}/{len(all_ips)}] ❌ 域名解析失败，跳过：{ip_port}")
                    continue
            else:
                ip = host

            # 获取IP地理信息和运营商信息
            try:
                res = requests.get(f"http://ip-api.com/json/{ip}?lang=zh-CN", timeout=10)
                data = res.json()
                
                if data.get("status") != "success":
                    print(f"[{processed_count}/{len(all_ips)}] ⚠️ IP-API查询失败: {ip}")
                    province = "未知"
                    isp = get_isp_by_regex(ip)
                else:
                    province = data.get("regionName", "未知")
                    isp = get_combined_isp(data, ip)
                    
                    # 输出详细解析信息
                    print(f"[{processed_count}/{len(all_ips)}] 📍 {ip}: {province} {isp}")
                    
            except Exception as e:
                print(f"[{processed_count}/{len(all_ips)}] ⚠️ IP-API查询异常: {e}")
                province = "未知"
                isp = get_isp_by_regex(ip)

            if isp == "内网":
                print(f"[{processed_count}/{len(all_ips)}] ⚠️ 内网IP，跳过：{ip_port}")
                continue

            # 清理省份名称，去除特殊字符
            province_clean = re.sub(r'[\\/*?:"<>|]', "", province)
            
            # 生成文件名
            if province_clean == "未知":
                fname = f"其他{isp}.txt"
            else:
                fname = f"{province_clean}{isp}.txt"
                
            province_isp_dict.setdefault(fname, set()).add(ip_port)

        except Exception as e:
            print(f"[{processed_count}/{len(all_ips)}] ⚠️ 解析 {ip_port} 出错：{e}")
            continue

    count = get_run_count() + 1
    save_run_count(count)

    # 统计各文件IP数量
    print("\n📊 IP分类统计:")
    total_ips = 0
    for filename, ip_set in province_isp_dict.items():
        print(f"   {filename}: {len(ip_set)} 个IP")
        total_ips += len(ip_set)
    
    print(f"📈 总计: {total_ips} 个IP被分类")

    # 写入文件
    for filename, ip_set in province_isp_dict.items():
        path = os.path.join(IP_DIR, filename)
        try:
            with open(path, "a", encoding="utf-8") as f:
                for ip_port in sorted(ip_set):
                    f.write(ip_port + "\n")
            print(f"📥 {path} 已追加写入 {len(ip_set)} 个 IP")
        except Exception as e:
            print(f"❌ 写入 {path} 失败：{e}")

    print(f"✅ 第一阶段完成，当前轮次：{count}")
    return count


# ===============================
# 第二阶段
def second_stage():
    print("🔔 第二阶段触发：生成 zubo.txt")
    if not os.path.exists(IP_DIR):
        print("⚠️ ip 目录不存在，跳过第二阶段")
        return

    combined_lines = []

    if not os.path.exists(RTP_DIR):
        print("⚠️ rtp 目录不存在，无法进行第二阶段组合，跳过")
        return

    ip_files = [f for f in os.listdir(IP_DIR) if f.endswith(".txt")]
    print(f"📁 找到 {len(ip_files)} 个IP文件")
    
    for ip_file in ip_files:
        ip_path = os.path.join(IP_DIR, ip_file)
        rtp_path = os.path.join(RTP_DIR, ip_file)

        if not os.path.exists(rtp_path):
            print(f"⚠️ 对应的RTP文件不存在: {rtp_path}")
            continue

        try:
            with open(ip_path, encoding="utf-8") as f1, open(rtp_path, encoding="utf-8") as f2:
                ip_lines = [x.strip() for x in f1 if x.strip()]
                rtp_lines = [x.strip() for x in f2 if x.strip()]
                
            print(f"📖 读取 {ip_file}: {len(ip_lines)} 个IP, {len(rtp_lines)} 个RTP源")
        except Exception as e:
            print(f"⚠️ 文件读取失败：{e}")
            continue

        if not ip_lines or not rtp_lines:
            print(f"⚠️ 文件内容为空: {ip_file}")
            continue

        # 组合IP和RTP源
        combinations = 0
        for ip_port in ip_lines:
            for rtp_line in rtp_lines:
                if "," not in rtp_line:
                    continue

                ch_name, rtp_url = rtp_line.split(",", 1)
                
                # 支持多种协议
                if "rtp://" in rtp_url:
                    part = rtp_url.split("rtp://", 1)[1]
                    combined_lines.append(f"{ch_name},http://{ip_port}/rtp/{part}")
                    combinations += 1
                elif "udp://" in rtp_url:
                    part = rtp_url.split("udp://", 1)[1]
                    combined_lines.append(f"{ch_name},http://{ip_port}/udp/{part}")
                    combinations += 1
                elif "http://" in rtp_url or "https://" in rtp_url:
                    # 如果是HTTP源，直接使用
                    combined_lines.append(f"{ch_name},{rtp_url}")
                    combinations += 1
        
        print(f"   ↳ 生成 {combinations} 个组合")

    # 去重
    unique = {}
    for line in combined_lines:
        url_part = line.split(",", 1)[1]
        if url_part not in unique:
            unique[url_part] = line

    print(f"📊 去重前: {len(combined_lines)} 条, 去重后: {len(unique)} 条")

    try:
        with open(ZUBO_FILE, "w", encoding="utf-8") as f:
            for line in unique.values():
                f.write(line + "\n")
        print(f"🎯 第二阶段完成，写入 {len(unique)} 条记录到 {ZUBO_FILE}")
    except Exception as e:
        print(f"❌ 写文件失败：{e}")


# ===============================
# 第三阶段
def third_stage():
    print("🧩 第三阶段：多线程检测代表频道生成 IPTV.txt 并写回可用 IP 到 ip/目录（覆盖）")

    if not os.path.exists(ZUBO_FILE):
        print("⚠️ zubo.txt 不存在，跳过第三阶段")
        return

    def check_stream(url, timeout=5):
        """检测流是否可播放"""
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_streams", "-i", url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout + 2
            )
            return b"codec_type" in result.stdout
        except Exception:
            return False

    # 别名映射
    alias_map = {}
    for main_name, aliases in CHANNEL_MAPPING.items():
        for alias in aliases:
            alias_map[alias] = main_name

    # 读取现有 ip 文件，建立 ip_port -> operator 映射
    ip_info = {}
    if os.path.exists(IP_DIR):
        for fname in os.listdir(IP_DIR):
            if not fname.endswith(".txt"):
                continue
            province_operator = fname.replace(".txt", "")
            try:
                with open(os.path.join(IP_DIR, fname), encoding="utf-8") as f:
                    for line in f:
                        ip_port = line.strip()
                        if ip_port:
                            ip_info[ip_port] = province_operator
            except Exception as e:
                print(f"⚠️ 读取 {fname} 失败：{e}")

    # 读取 zubo.txt 并按 ip:port 分组
    groups = {}
    total_channels = 0
    with open(ZUBO_FILE, encoding="utf-8") as f:
        for line in f:
            if "," not in line:
                continue

            ch_name, url = line.strip().split(",", 1)
            ch_main = alias_map.get(ch_name, ch_name)
            m = re.match(r"http://([^/]+)/", url)
            if not m:
                continue

            ip_port = m.group(1)
            groups.setdefault(ip_port, []).append((ch_main, url))
            total_channels += 1

    print(f"📊 解析完成: {len(groups)} 个IP, {total_channels} 个频道")

    # 选择代表频道并检测
    def detect_ip(ip_port, entries):
        """检测单个IP的代表频道"""
        # 优先检测CCTV-1综合
        rep_channels = [u for c, u in entries if c == "CCTV-1综合"]
        
        # 如果没有CCTV-1综合，检测湖南卫视
        if not rep_channels:
            rep_channels = [u for c, u in entries if c == "湖南卫视"]
        
        # 如果还没有，检测翡翠台
        if not rep_channels:
            rep_channels = [u for c, u in entries if c == "翡翠台"]
        
        # 如果还没有，使用第一个频道
        if not rep_channels and entries:
            rep_channels = [entries[0][1]]
        
        # 尝试检测每个代表频道
        for url in rep_channels:
            print(f"   🔍 检测 {ip_port} 的代表频道...")
            if check_stream(url):
                return ip_port, True, len(entries)
        return ip_port, False, len(entries)

    print(f"🚀 启动多线程检测（共 {len(groups)} 个 IP）...")
    playable_ips = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(detect_ip, ip, chs): ip for ip, chs in groups.items()}
        for future in concurrent.futures.as_completed(futures):
            try:
                ip_port, ok, channel_count = future.result()
            except Exception as e:
                print(f"⚠️ 线程检测返回异常：{e}")
                continue
            if ok:
                playable_ips[ip_port] = channel_count

    print(f"✅ 检测完成，可播放 IP 共 {len(playable_ips)} 个")
    
    # 按频道数量排序
    sorted_ips = sorted(playable_ips.items(), key=lambda x: x[1], reverse=True)
    print("🏆 优质IP排名（按频道数量）:")
    for ip, count in sorted_ips[:10]:  # 显示前10个
        print(f"   {ip}: {count} 个频道")

    valid_lines = []
    seen = set()
    operator_playable_ips = {}

    for ip_port in playable_ips.keys():
        operator = ip_info.get(ip_port, "未知")

        for c, u in groups.get(ip_port, []):
            key = f"{c},{u}"
            if key not in seen:
                seen.add(key)
                # 在频道名后添加运营商信息
                valid_lines.append(f"{c},{u}${operator}")

                operator_playable_ips.setdefault(operator, set()).add(ip_port)

    # 写回可用的IP到对应文件
    for operator, ip_set in operator_playable_ips.items():
        target_file = os.path.join(IP_DIR, operator + ".txt")
        try:
            with open(target_file, "w", encoding="utf-8") as wf:
                for ip_p in sorted(ip_set):
                    wf.write(ip_p + "\n")
            print(f"📥 写回 {target_file}，共 {len(ip_set)} 个可用地址")
        except Exception as e:
            print(f"❌ 写回 {target_file} 失败：{e}")

    # 写 IPTV.txt（纯文本格式，包含分类）
    beijing_now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    disclaimer_url = "https://kakaxi-1.asia/LOGO/Disclaimer.mp4"

    try:
        with open(IPTV_FILE, "w", encoding="utf-8") as f:
            # 写入头部信息（纯文本格式）
            f.write(f"更新时间: {beijing_now}（北京时间）\n")
            f.write(f"频道总数: {len(valid_lines)}\n")
            f.write(f"可用IP数: {len(playable_ips)}\n")
            f.write(f"免责声明: {disclaimer_url}\n\n")
            
            # 按分类写入频道（纯文本格式）
            for category, ch_list in CHANNEL_CATEGORIES.items():
                f.write(f"{category},#genre#\n")
                category_channels = []
                
                for ch in ch_list:
                    for line in valid_lines:
                        if line.startswith(ch + ","):
                            # 提取完整的频道信息
                            f.write(f"{line}\n")
                            category_channels.append(ch)
                
                if category_channels:
                    print(f"📺 {category}: {len(category_channels)} 个频道")
                    f.write("\n")  # 类别之间空一行
            
            # 写入其他未分类频道
            other_count = 0
            other_channels_written = False
            
            for line in valid_lines:
                ch_name = line.split(",", 1)[0]
                # 检查是否已经在分类中出现过
                found = False
                for ch_list in CHANNEL_CATEGORIES.values():
                    if ch_name in ch_list:
                        found = True
                        break
                
                if not found:
                    if not other_channels_written:
                        f.write("其他频道,#genre#\n")
                        other_channels_written = True
                    f.write(f"{line}\n")
                    other_count += 1
            
            if other_count > 0:
                print(f"📺 其他频道: {other_count} 个")
        
        print(f"🎯 IPTV.txt 生成完成，共 {len(valid_lines)} 条频道")
        print(f"📁 文件已保存: {IPTV_FILE}")
        
    except Exception as e:
        print(f"❌ 写 IPTV.txt 失败：{e}")

# ===============================
# 文件推送
def push_all_files():
    print("🚀 推送所有更新文件到 GitHub...")
    try:
        os.system('git config --global user.name "github-actions"')
        os.system('git config --global user.email "github-actions@users.noreply.github.com"')
    except Exception:
        pass

    # 添加所有可能的更新文件
    files_to_add = [
        COUNTER_FILE,
        IPTV_FILE,
        ZUBO_FILE,
    ]
    
    for file in files_to_add:
        if os.path.exists(file):
            os.system(f'git add "{file}" 2>/dev/null || echo "⚠️ 添加 {file} 失败"')
    
    # 添加ip目录下所有文件
    if os.path.exists(IP_DIR):
        os.system('git add ip/*.txt 2>/dev/null || echo "⚠️ 添加ip目录文件失败"')
    
    # 提交并推送
    commit_message = f"自动更新：第{get_run_count()}次运行"
    os.system(f'git commit -m "{commit_message}" 2>/dev/null || echo "⚠️ 无需提交"')
    os.system("git push origin main 2>/dev/null || echo '⚠️ 推送失败'")
    print("✅ 推送完成")

# ===============================
# 主执行逻辑
if __name__ == "__main__":
    print("=" * 60)
    print("🎬 IPTV源自动化脚本开始执行")
    print("=" * 60)
    
    # 显示当前配置信息
    print(f"📁 工作目录: {os.getcwd()}")
    print(f"📊 运营商识别配置: {len(ISP_CONFIG)} 种")
    print(f"📺 频道分类: {len(CHANNEL_CATEGORIES)} 类")
    
    # 确保目录存在
    os.makedirs(IP_DIR, exist_ok=True)
    os.makedirs(RTP_DIR, exist_ok=True)

    run_count = first_stage()

    if run_count % 10 == 0:
        print(f"\n🎯 第 {run_count} 次运行，执行完整流程")
        print("-" * 40)
        second_stage()
        third_stage()
    else:
        print(f"\nℹ️ 第 {run_count} 次运行，不是 10 的倍数，跳过第二、三阶段")

    print("\n" + "=" * 40)
    push_all_files()
    
    print("\n" + "=" * 60)
    print("✅ 所有任务执行完成")
    print("=" * 60)
