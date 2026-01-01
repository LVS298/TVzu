import os
import re
import requests
import time
import concurrent.futures
import subprocess
import socket  # 添加缺失的导入
import ipaddress  # 添加ipaddress模块
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Set, Tuple
import json

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
        "CCTV-14少儿", "CCTV-15音乐", "CCTV-16奥林匹克", "CCTV-17农业农村", "CCTV-4K超高清", "CCTV-8K超高清", "环球旅游",
        "兵器科技", "风云音乐", "风云足球", "风云剧场", "怀旧剧场", "第一剧场", "女性时尚", "世界地理", "央视台球", "高尔夫网球",
        "央视文化精品", "卫生健康", "电视指南", "中学生", "发现之旅", "书法频道", "国学频道", "环球奇观", "峨眉电影4K", "翡翠台", "明珠台",
    ],
    "卫视频道": [
        "湖南卫视", "湖南卫视4K", "浙江卫视", "浙江卫视4K", "江苏卫视", "江苏卫视4K", "东方卫视", "东方卫视4K","深圳卫视", "深圳卫视4K", "北京卫视",  
        "北京卫视4K","广东卫视", "广东卫视4K", "广西卫视", "东南卫视", "海南卫视", "河北卫视", "河南卫视", "湖北卫视", "江西卫视", "四川卫视",
        "四川卫视4K", "重庆卫视", "贵州卫视", "云南卫视", "天津卫视", "安徽卫视", "山东卫视", "山东卫视4K", "辽宁卫视", "黑龙江卫视", "吉林卫视",
        "内蒙古卫视", "宁夏卫视", "山西卫视", "陕西卫视", "甘肃卫视", "青海卫视", "新疆卫视", "西藏卫视", "三沙卫视", "兵团卫视", "延边卫视",
        "安多卫视", "康巴卫视", "农林卫视", "山东教育卫视", "中国教育1台", "中国教育2台", "中国教育3台", "中国教育4台", "早期教育", "新视觉HD",
        "绚影4K", "4K乐享", "大湾区卫视", "澳亚卫视", "广州竞赛", "咖秀综艺", "爱宠宠物",  
    ],
    "数字频道": [
        "CHC动作电影", "CHC家庭影院", "CHC影迷电影", "淘电影", "淘剧场", "淘4K", "淘娱乐",  "淘萌宠", "重温经典",
        "星空卫视", "CHANNEL[V]", "凤凰卫视中文台", "凤凰卫视资讯台", "凤凰卫视香港台", "凤凰卫视电影台", "求索纪录", "求索科学",
        "求索生活", "求索动物", "纪实人文", "金鹰纪实", "纪实科教", "睛彩竞技", "睛彩篮球", "睛彩广场舞", "魅力足球", "五星体育",
        "劲爆体育", "快乐垂钓", "四海钓鱼", "来钓鱼吧", "茶频道", "先锋乒羽", "天元围棋", "汽摩", "梨园频道", "文物宝库", "法制天地", 
        "乐游", "生活时尚", "都市剧场", "欢笑剧场", "游戏风云", "武术世界", "哒啵赛事", "哒啵电竞", "中国交通", "中国天气",  
        "华数4K", "华数光影", "华数星影", "华数精选", "华数动作影院", "华数喜剧影院", "华数家庭影院", "华数经典电影", "华数热播剧场", "华数碟战剧场",
        "华数军旅剧场", "华数城市剧场", "华数武侠剧场", "华数古装剧场", "华数魅力时尚", "峨眉电影", "爱体育", "爱历史", "爱动漫", 
        "爱喜剧", "爱奇谈", "爱幼教", "爱悬疑", "爱旅行", "爱浪漫", "爱玩具", "爱科幻", "爱谍战", "爱赛车", "爱院线", "BesTV-4K", "BesTV4K-1", 
        "BesTV4K-2", "CBN每日影院", "CBN幸福娱乐", "CBN幸福剧场", "CBN风尚生活", "爱探索", "爱青春", "爱怀旧", "爱经典", "爱都市", "爱家庭",
        "NEWTV家庭剧场", "NEWTV精品纪录", "NEWTV健康有约", "NEWTV精品体育", "NEWTV军事评论", "NEWTV农业致富", "NEWTV古装剧场", "NEWTV动作电影",
        "NEWTV军旅剧场", "NEWTV惊悚悬疑", "NewTV海外剧场", "NewTV搏击", "NewTV明星大片", "NewTV爱情喜剧", "NewTV精品大剧", "NewTV中国功夫",
        "NewTV金牌综艺",
    ],
    "少儿教育": [
        "乐龄学堂", "少儿天地", "动漫秀场", "淘BABY", "黑莓动画", "睛彩青少", "金色学堂", "新动漫", "卡酷少儿", "金鹰卡通", "优漫卡通", "哈哈炫动", "嘉佳卡通",
        "华数少儿动画", "华数卡通", "亲子趣学", "少儿天地",
    ],
     "湖北": [
        "湖北公共新闻", "湖北经视频道", "湖北综合频道", "湖北垄上频道", "湖北影视频道", "湖北生活频道", "湖北教育频道", "武汉新闻综合", "武汉电视剧", "武汉科技生活",
        "武汉文体频道", "武汉教育频道", "阳新综合", "房县综合", "蔡甸综合",
    ],#任意添加，与仓库中rtp/省份运营商.txt内频道一致即可，或在下方频道名映射中改名
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
    "湖南卫视": ["湖南卫视HD"],
    "北京卫视": ["北京卫视HD"],
    "东方卫视": ["东方卫视HD"],
    "广东卫视": ["广东卫视HD"],
    "深圳卫视": ["深圳卫视HD"],
    "山东卫视": ["山东卫视HD"],
    "四川卫视": ["四川卫视HD"],
    "浙江卫视": ["浙江卫视HD"],
    "CHC影迷电影": ["CHC影迷电影HD", "CHC-影迷电影", "影迷电影", "chc影迷电影高清"],
    "CHC家庭影院": ["CHC-家庭影院", "CHC家庭影院HD", "chc家庭影院高清"], 
    "CHC动作电影": ["CHC-动作电影", "CHC动作电影HD", "CHC高清电影", "chc动作电影高清"],
    "淘电影": ["IPTV淘电影", "北京IPTV淘电影", "北京淘电影"],
    "淘剧场": ["IPTV淘剧场", "北京IPTV淘剧场", "北京淘剧场"],
    "淘4K": ["IPTV淘4K", "北京IPTV4K超高清", "北京淘4K", "淘4K", "北京IPTV淘4K", "北京IPTV4K超清", "4K超清"],
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
    "凤凰卫视电影台": ["凤凰电影", "凤凰电影台", "凤凰卫视电影", "鳳凰衛視電影台", "凤凰电影"],
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
    "华数光影": ["光影"],
    "华数星影": ["星影"],
    "华数精选": ["精选"],
    "华数电影": ["IPTV6华数电影"],
    "华数动作影院": ["动作电影"],
    "华数喜剧影院": ["喜剧影院"],
    "华数家庭影院": ["家庭影院"], 
    "华数经典电影": ["IPTV经典电影", "经典电影"],
    "华数热播剧场": ["IPTV热播剧场", "热播剧场"],
    "华数碟战剧场": ["IPTV谍战剧场", "谍战剧场"],
    "华数军旅剧场": ["军旅剧场"],
    "华数城市剧场": ["城市剧场"],
    "华数武侠剧场": ["武侠剧场"],
    "华数古装剧场": ["古装剧场"],
    "华数魅力时尚": ["魅力时尚"],
    "华数少儿动画": ["IPTV少儿动画", "华数电影1"],
    "华数动画": ["华数动画", "华数卡通"],
    "峨眉电影": ["四川峨眉HD", "峨眉电影高清", "峨眉电影", "四川峨眉", "四川峨眉电影", "四川峨眉高清"],
    "峨眉电影4K": ["4K超高清电影"],
    "绚影4K": ["绚影4K", "睛彩绚影4K", "精彩连播", "天府绚影高清影院"],
    "4K乐享": ["乐享4K"],
    "爱体育": ["爱体育HD", "IHOT爱体育", "HOT爱体育", "爱体育高清"],
    "爱历史": ["爱历史HD", "IHOT爱历史", "HOT爱历史", "HO爱历史", "爱历史高清"], 
    "爱动漫": ["爱动漫HD", "IHOT爱动漫", "HOT爱动漫" "爱动漫高清"], 
    "爱喜剧": ["爱喜剧HD", "IHOT爱喜剧", "HOT爱喜剧", "爱喜剧高清"],
    "爱奇谈": ["爱奇谈HD", "IHOT爱奇谈", "HOT爱奇谈", "爱奇谈高清"], 
    "爱幼教": ["爱幼教HD", "IHOT爱幼教", "HOT爱幼教", "爱幼教高清"], 
    "爱悬疑": ["爱悬疑HD", "IHOT爱悬疑", "HOT爱悬疑", "爱悬疑高清"],
    "爱旅行": ["爱旅行HD", "IHOT爱旅行", "HOT爱旅行", "爱旅行高清"], 
    "爱浪漫": ["爱浪漫HD", "IHOT爱浪漫", "HOT爱浪漫", "爱浪漫高清"],
    "爱玩具": ["爱玩具HD", "IHOT爱玩具", "HOT爱玩具", "爱玩具高清"],
    "爱科幻": ["爱科幻HD", "IHOT爱科幻", "HOT爱科幻", "爱科幻高清"], 
    "爱谍战": ["爱谍战HD", "IHOT爱谍战", "HOT爱谍战", "爱谍战高清"],
    "爱赛车": ["爱谍战HD", "IHOT爱赛车", "HOT爱赛车", "爱赛车高清"],
    "爱院线": ["爱院线HD", "IHOT爱院线", "HOT爱院线", "爱院线高清"],
    "爱科学": ["爱科学HD", "IHOT爱科学", "HOT爱科学", "爱科学高清"],
    "爱探索": ["爱探索HD", "THOT爱探索", "HOT爱探索", "爱探索高清"],
    "爱青春": ["爱青春HD", "IHOT爱青春", "HOT爱青春", "爱青春高清"],
    "爱怀旧": ["爱怀旧HD", "IHOT爱怀旧", "HOT爱怀旧", "爱怀旧高清"],
    "爱经典": ["爱经典HD", "IHOT爱经典", "HOT经典", "HO经典", "爱经典高清"],
    "爱都市": ["爱都市HD", "IHOT爱都市", "HOT爱都市", "爱都市高清"],
    "爱家庭": ["爱家庭HD", "IHOT爱家庭", "HOT爱家庭", "爱家庭高清"],
    "环球奇观": ["环球奇观HD"],
}#格式为"频道分类中的标准名": ["rtp/中的名字"],

# ===============================
# 新增：四川城市IP段URL配置
SICHUAN_CITY_URLS = {
    "四川省": "https://metowolf.github.io/iplist/data/cncity/510000.txt",
    "成都市": "https://metowolf.github.io/iplist/data/cncity/510100.txt",
    "自贡市": "https://metowolf.github.io/iplist/data/cncity/510300.txt",
    "攀枝花市": "https://metowolf.github.io/iplist/data/cncity/510400.txt",
    "泸州市": "https://metowolf.github.io/iplist/data/cncity/510500.txt",
    "德阳市": "https://metowolf.github.io/iplist/data/cncity/510600.txt",
    "绵阳市": "https://metowolf.github.io/iplist/data/cncity/510700.txt",
    "广元市": "https://metowolf.github.io/iplist/data/cncity/510800.txt",
    "遂宁市": "https://metowolf.github.io/iplist/data/cncity/510900.txt",
    "内江市": "https://metowolf.github.io/iplist/data/cncity/511000.txt",
    "乐山市": "https://metowolf.github.io/iplist/data/cncity/511100.txt",
    "南充市": "https://metowolf.github.io/iplist/data/cncity/511300.txt",
    "眉山市": "https://metowolf.github.io/iplist/data/cncity/511400.txt",
    "宜宾市": "https://metowolf.github.io/iplist/data/cncity/511500.txt",
    "广安市": "https://metowolf.github.io/iplist/data/cncity/511600.txt",
    "达州市": "https://metowolf.github.io/iplist/data/cncity/511700.txt",
    "雅安市": "https://metowolf.github.io/iplist/data/cncity/511800.txt",
    "巴中市": "https://metowolf.github.io/iplist/data/cncity/511900.txt",
    "资阳市": "https://metowolf.github.io/iplist/data/cncity/512000.txt",
    "阿坝藏族羌族自治州": "https://metowolf.github.io/iplist/data/cncity/513200.txt",
    "甘孜藏族自治州": "https://metowolf.github.io/iplist/data/cncity/513300.txt",
    "凉山彝族自治州": "https://metowolf.github.io/iplist/data/cncity/513400.txt",
}

# 新增：运营商IP段URL配置
ISP_URLS = {
    "电信": "https://metowolf.github.io/iplist/data/isp/chinatelecom.txt",
    "移动": "https://metowolf.github.io/iplist/data/isp/chinamobile.txt",
    "联通": "https://metowolf.github.io/iplist/data/isp/chinaunicom.txt",
    "阿里云": "https://metowolf.github.io/iplist/data/isp/aliyun.txt",
    "腾讯云": "https://metowolf.github.io/iplist/data/isp/tencent.txt",
    "华为云": "https://metowolf.github.io/iplist/data/isp/huawei.txt",
}

# ===============================
# 新增：IP数据管理器
class IPDataManager:
    """IP数据管理器，用于加载和匹配城市、运营商IP段"""
    
    def __init__(self):
        self.city_cidrs = {}  # 城市 -> CIDR列表
        self.isp_cidrs = {}   # 运营商 -> CIDR列表
        self.loaded = False
    
    def load_all_data(self):
        """加载所有IP数据"""
        print("📥 开始加载IP数据...")
        
        # 加载四川城市数据
        self.load_sichuan_city_data()
        
        # 加载运营商数据
        self.load_isp_data()
        
        self.loaded = True
        print(f"✅ IP数据加载完成: {len(self.city_cidrs)}个城市, {len(self.isp_cidrs)}个运营商")
    
    def load_sichuan_city_data(self):
        """加载四川城市CIDR数据"""
        for city_name, url in SICHUAN_CITY_URLS.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    cidrs = []
                    for line in response.text.strip().split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                network = ipaddress.ip_network(line, strict=False)
                                cidrs.append(network)
                            except ValueError:
                                continue
                    self.city_cidrs[city_name] = cidrs
                    print(f"  ✓ 加载 {city_name}: {len(cidrs)}个CIDR")
                else:
                    print(f"  ✗ 加载失败 {city_name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ✗ 加载失败 {city_name}: {e}")
    
    def load_isp_data(self):
        """加载运营商CIDR数据"""
        for isp_name, url in ISP_URLS.items():
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    cidrs = []
                    for line in response.text.strip().split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                network = ipaddress.ip_network(line, strict=False)
                                cidrs.append(network)
                            except ValueError:
                                continue
                    self.isp_cidrs[isp_name] = cidrs
                    print(f"  ✓ 加载 {isp_name}: {len(cidrs)}个CIDR")
                else:
                    print(f"  ✗ 加载失败 {isp_name}: HTTP {response.status_code}")
            except Exception as e:
                print(f"  ✗ 加载失败 {isp_name}: {e}")
    
    def get_city_by_ip(self, ip_str: str) -> str:
        """根据IP获取城市（优先四川城市，然后其他省份）"""
        try:
            ip = ipaddress.ip_address(ip_str)
            
            # 首先检查四川各城市
            for city_name, cidr_list in self.city_cidrs.items():
                for cidr in cidr_list:
                    if ip in cidr:
                        return city_name
            
            return "未知城市"
        except ValueError:
            return "无效IP"
        except Exception:
            return "未知城市"
    
    def get_isp_by_ip_cidr(self, ip_str: str) -> str:
        """使用CIDR精确判断IP的运营商"""
        try:
            ip = ipaddress.ip_address(ip_str)
            
            for isp_name, cidr_list in self.isp_cidrs.items():
                for cidr in cidr_list:
                    if ip in cidr:
                        return isp_name
            
            return "未知"
        except ValueError:
            return "无效IP"
        except Exception:
            return "未知"

# 全局IP数据管理器实例
ip_manager = IPDataManager()

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
    isp_raw = (data.get("isp") or "").lower()

    if "telecom" in isp_raw or "ct" in isp_raw or "chinatelecom" in isp_raw:
        return "电信"
    elif "unicom" in isp_raw or "cu" in isp_raw or "chinaunicom" in isp_raw:
        return "联通"
    elif "mobile" in isp_raw or "cm" in isp_raw or "chinamobile" in isp_raw:
        return "移动"
    # 新增
    elif "cable" in isp_raw or "cbn" in isp_raw or "broadcast" in isp_raw or "chinabroadcastnet" in isp_raw:
        return "广电"
    elif "aliyun" in isp_raw or "alibabacloud" in isp_raw:
        return "阿里云"
    elif "tencent" in isp_raw or "qcloud" in isp_raw:
        return "腾讯云"
    elif "huawei" in isp_raw or "huaweicloud" in isp_raw:
        return "华为云"
    elif "ctm" in isp_raw or "macau telecom" in isp_raw or "macau-telecom" in isp_raw:
        return "澳门电讯"
    else:
        return "未知"

# ===== 运营商识别配置 =====
ISP_CONFIG = {
    "电信": {
        "api_keywords": ["telecom", "ct", "chinatelecom", "电信", "chinanet"],
        "ip_patterns": [
            r"^1\.(1[2-9]|2[0-9]|3[0-9]|4[0-9]|5[0-9]|6[0-9]|8[0-9]|9[0-9])\.",
            r"^5\.",
            r"^8\.(13[0-9]|14[0-9]|15[0-9])\.",
            r"^14\.",
            # ... 其他电信IP段
        ]
    },
    # ... 其他运营商配置（可以保持原有）
}

# 修改get_isp_by_ip函数，结合CIDR方法
def get_isp_by_ip(ip_address: str) -> str:
    """
    根据IP地址判断运营商（结合正则和CIDR方法）
    
    Args:
        ip_address: IP地址字符串
        
    Returns:
        str: 运营商名称或"未知"
    """
    # 首先使用正则方法（保持向后兼容）
    for isp_name, config in ISP_CONFIG.items():
        for pattern in config["ip_patterns"]:
            if re.match(pattern, ip_address):
                return isp_name
    
    # 如果正则没匹配到，使用CIDR方法
    if ip_manager.loaded:
        return ip_manager.get_isp_by_ip_cidr(ip_address)
    
    return "未知"

# ===============================
# 修改后的第一阶段：结合城市和运营商分类
def first_stage():
    """第一阶段：爬取IP并分类（结合城市和运营商）"""
    
    # 加载IP数据
    if not ip_manager.loaded:
        ip_manager.load_all_data()
    
    os.makedirs(IP_DIR, exist_ok=True)
    all_ips = set()

    # 爬取FOFA数据
    for url, filename in FOFA_URLS.items():
        print(f"📡 正在爬取 {filename} ...")
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            urls_all = re.findall(r'<a href="http://(.*?)"', r.text)
            all_ips.update(u.strip() for u in urls_all if u.strip())
            print(f"  ✓ 获取到 {len(urls_all)} 个URL")
        except Exception as e:
            print(f"❌ 爬取失败：{e}")
        time.sleep(3)

    # 分类字典：文件名 -> IP集合
    classification_dict = {}

    # 处理每个IP
    for ip_port in all_ips:
        try:
            host = ip_port.split(":")[0]

            # 域名解析
            is_ip = re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host)
            if not is_ip:
                try:
                    resolved_ip = socket.gethostbyname(host)
                    print(f"🌐 域名解析成功: {host} → {resolved_ip}")
                    ip = resolved_ip
                except Exception:
                    print(f"❌ 域名解析失败，跳过：{ip_port}")
                    continue
            else:
                ip = host

            # 获取地理信息（API）
            province = "未知"
            try:
                res = requests.get(f"http://ip-api.com/json/{ip}?lang=zh-CN", timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("status") == "success":
                        province = data.get("regionName", "未知")
            except Exception:
                pass

            # 获取城市信息（CIDR方法）
            city = ip_manager.get_city_by_ip(ip)
            
            # 获取运营商信息（结合API和CIDR）
            isp = "未知"
            try:
                if res.status_code == 200 and data.get("status") == "success":
                    isp = get_isp_from_api(data)
            except Exception:
                pass
            
            if isp == "未知":
                isp = get_isp_by_ip(ip)  # 使用结合方法

            # 生成文件名
            if province == "四川" and city != "未知城市" and city != "四川省":
                # 四川城市级分类：四川_成都市_电信.txt
                filename = f"四川_{city}_{isp}.txt"
            elif province != "未知" and isp != "未知":
                # 省级分类：四川电信.txt
                filename = f"{province}{isp}.txt"
            else:
                print(f"⚠️ 无法分类，跳过：{ip_port}")
                continue

            # 添加到分类字典
            classification_dict.setdefault(filename, set()).add(ip_port)

        except Exception as e:
            print(f"⚠️ 解析 {ip_port} 出错：{e}")
            continue

    # 保存计数
    count = get_run_count() + 1
    save_run_count(count)

    # 写入文件
    for filename, ip_set in classification_dict.items():
        path = os.path.join(IP_DIR, filename)
        try:
            # 追加写入模式
            mode = "a" if os.path.exists(path) else "w"
            with open(path, mode, encoding="utf-8") as f:
                for ip_port in sorted(ip_set):
                    f.write(ip_port + "\n")
            print(f"📁 {path} 已{'追加' if mode == 'a' else '新建'}写入 {len(ip_set)} 个IP")
        except Exception as e:
            print(f"❌ 写入 {path} 失败：{e}")

    print(f"✅ 第一阶段完成，当前轮次：{count}")
    print(f"   共处理 {len(all_ips)} 个IP，分类到 {len(classification_dict)} 个文件")
    return count

# ===============================
# 第二阶段（保持不变）
def second_stage():
    print("🔔 第二阶段触发：生成 zubo.txt")
    if not os.path.exists(IP_DIR):
        print("⚠️ ip 目录不存在，跳过第二阶段")
        return

    combined_lines = []

    if not os.path.exists(RTP_DIR):
        print("⚠️ rtp 目录不存在，无法进行第二阶段组合，跳过")
        return

    for ip_file in os.listdir(IP_DIR):
        if not ip_file.endswith(".txt"):
            continue

        ip_path = os.path.join(IP_DIR, ip_file)
        rtp_path = os.path.join(RTP_DIR, ip_file)

        if not os.path.exists(rtp_path):
            # 尝试匹配简化的文件名（去掉城市前缀）
            if ip_file.startswith("四川_"):
                # 如：四川_成都市_电信.txt -> 四川电信.txt
                simplified = ip_file.replace("四川_", "").split("_")[-1]
                simplified = "四川" + simplified
                rtp_path = os.path.join(RTP_DIR, simplified)
                if not os.path.exists(rtp_path):
                    continue
            else:
                continue

        try:
            with open(ip_path, encoding="utf-8") as f1, open(rtp_path, encoding="utf-8") as f2:
                ip_lines  = [x.strip() for x in f1 if x.strip()]
                rtp_lines = [x.strip() for x in f2 if x.strip()]
        except Exception as e:
            print(f"⚠️ 文件读取失败：{e}")
            continue

        if not ip_lines or not rtp_lines:
            continue

        for ip_port in ip_lines:
            for rtp_line in rtp_lines:
                if "," not in rtp_line:
                    continue

                ch_name, src_url = rtp_line.split(",", 1)

                if "rtp://" in src_url:
                    part = src_url.split("rtp://", 1)[1]
                    combined_lines.append(f"{ch_name},http://{ip_port}/rtp/{part}")

                elif "udp://" in src_url:
                    part = src_url.split("udp://", 1)[1]
                    combined_lines.append(f"{ch_name},http://{ip_port}/udp/{part}")

                elif src_url.startswith(("http://", "https://")):
                    # 把 // 后面到第一个 / 之前的那段（域名或IP+端口）整体换掉
                    new_url = re.sub(r"(?<=://)[^/]+", ip_port, src_url)
                    combined_lines.append(f"{ch_name},{new_url}")

    # 去重：同一 url 只保留一条（频道名取第一次出现的）
    unique = {}
    for line in combined_lines:
        url = line.split(",", 1)[1]
        if url not in unique:
            unique[url] = line

    try:
        with open(ZUBO_FILE, "w", encoding="utf-8") as f:
            for line in unique.values():
                f.write(line + "\n")
        print(f"🎯 第二阶段完成，写入 {len(unique)} 条记录")
    except Exception as e:
        print(f"❌ 写文件失败：{e}")

# ===============================
# 第三阶段（保持不变）
def third_stage():
    print("🧩 第三阶段：多线程检测代表频道生成 IPTV.txt 并写回可用 IP 到 ip/目录（覆盖）")

    if not os.path.exists(ZUBO_FILE):
        print("⚠️ zubo.txt 不存在，跳过第三阶段")
        return

    def check_stream(url, timeout=5):
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

    # 选择代表频道并检测
    def detect_ip(ip_port, entries):
        rep_channels = [u for c, u in entries if c == "CCTV1"]
        if not rep_channels and entries:
            rep_channels = [entries[0][1]]
        playable = any(check_stream(u) for u in rep_channels)
        return ip_port, playable

    print(f"🚀 启动多线程检测（共 {len(groups)} 个 IP）...")
    playable_ips = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(detect_ip, ip, chs): ip for ip, chs in groups.items()}
        for future in concurrent.futures.as_completed(futures):
            try:
                ip_port, ok = future.result()
            except Exception as e:
                print(f"⚠️ 线程检测返回异常：{e}")
                continue
            if ok:
                playable_ips.add(ip_port)

    print(f"✅ 检测完成，可播放 IP 共 {len(playable_ips)} 个")

    valid_lines = []
    seen = set()
    operator_playable_ips = {}

    for ip_port in playable_ips:
        operator = ip_info.get(ip_port, "未知")

        for c, u in groups.get(ip_port, []):
            key = f"{c},{u}"
            if key not in seen:
                seen.add(key)
                valid_lines.append(f"{c},{u}${operator}")

                operator_playable_ips.setdefault(operator, set()).add(ip_port)

    for operator, ip_set in operator_playable_ips.items():
        target_file = os.path.join(IP_DIR, operator + ".txt")
        try:
            with open(target_file, "w", encoding="utf-8") as wf:
                for ip_p in sorted(ip_set):
                    wf.write(ip_p + "\n")
            print(f"📥 写回 {target_file}，共 {len(ip_set)} 个可用地址")
        except Exception as e:
            print(f"❌ 写回 {target_file} 失败：{e}")

    # 写 IPTV.txt（包含更新时间与分类）
    beijing_now = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")
    disclaimer_url = "https://kakaxi-1.asia/LOGO/Disclaimer.mp4"

    try:
        with open(IPTV_FILE, "w", encoding="utf-8") as f:
            f.write(f"更新时间: {beijing_now}（北京时间）\n\n")
            f.write("更新时间,#genre#\n")
            f.write(f"{beijing_now},{disclaimer_url}\n\n")

            for category, ch_list in CHANNEL_CATEGORIES.items():
                f.write(f"{category},#genre#\n")
                for ch in ch_list:
                    for line in valid_lines:
                        name = line.split(",", 1)[0]
                        if name == ch:
                            f.write(line + "\n")
                f.write("\n")
        print(f"🎯 IPTV.txt 生成完成，共 {len(valid_lines)} 条频道")
    except Exception as e:
        print(f"❌ 写 IPTV.txt 失败：{e}")

# ===============================
# 文件推送（保持不变）
def push_all_files():
    print("🚀 推送所有更新文件到 GitHub...")
    try:
        os.system('git config --global user.name "github-actions"')
        os.system('git config --global user.email "github-actions@users.noreply.github.com"')
    except Exception:
        pass

    os.system("git add 计数.txt || true")
    os.system("git add ip/*.txt || true")
    os.system("git add IPTV.txt || true")
    os.system('git commit -m "自动更新：计数、IP文件、IPTV.txt" || echo "⚠️ 无需提交"')
    os.system("git push origin main || echo '⚠️ 推送失败'")

# ===============================
# 主执行逻辑
if __name__ == "__main__":
    # 确保目录存在
    os.makedirs(IP_DIR, exist_ok=True)
    os.makedirs(RTP_DIR, exist_ok=True)

    # 运行第一阶段（已集成城市+运营商分类）
    run_count = first_stage()

    if run_count % 10 == 0:
        second_stage()
        third_stage()
    else:
        print("ℹ️ 本次不是 10 的倍数，跳过第二、三阶段")

    push_all_files()
