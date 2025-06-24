import asyncio
import base64
import io
import json
import os
import re
from tkinter import Image
import xml.etree.ElementTree as ET
import codecs
from urllib.parse import urlparse

import httpx

from sdvx_struct import *

SDVX_XML_PATH = "music_db.xml"
SDVX_ALIASES_PATH = "aliases.json"
SDVX_INDEX_DOMAINNAME = "sdvxindex.com"
SDVX_INNDEX_SCHEME = 'https'
SDVX_INDEX_URL = f"{SDVX_INNDEX_SCHEME}://{SDVX_INDEX_DOMAINNAME}"


def pad_with_zeros(num: int, N : int = 4) -> str:
        return str(num).zfill(N)
    
async def webp_to_jpg_base64(url: str) -> str:
    # 从指定 URL 下载 WebP 图像
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    response.raise_for_status()  # 确保请求成功

    # 读取图像并转换为 JPEG
    image = Image.open(io.BytesIO(response.content))
    jpg_io = io.BytesIO()
    image.convert("RGB").save(jpg_io, format='JPEG')
    jpg_io.seek(0)

    # 将 JPEG 图像编码为 Base64
    base64_str = base64.b64encode(jpg_io.getvalue()).decode('utf-8')
    return base64_str
    
class SDVX_MANAGER:
    def __init__(self, xml_file : str = SDVX_XML_PATH):
        with codecs.open(xml_file, 'r', encoding='shift_jis', errors='ignore') as file:
            content = file.read()
        
        self.__alias_json_gen(SDVX_ALIASES_PATH)
        with open(SDVX_ALIASES_PATH, 'r', encoding='utf-8') as file:
            self.__aliases: dict[str, list[str]] = json.load(file)
        
        self.__sdvx_dict : dict[str, SDVXStrcut] = {}
        
        root = ET.fromstring(content)
        for music in root.findall('music'):
            struct = SDVXStrcut()
            attrib = music.attrib
            id = attrib["id"]
            
            info = music.find('info')
            
            title = info.find('title_name').text
            title_yomigana = info.find('title_yomigana').text
            artist = info.find('artist_name').text
            artist_yomigana = info.find('artist_yomigana').text
            ascii = info.find('ascii').text
            bpm_max = int(info.find('bpm_max').text)
            bpm_min = int(info.find('bpm_min').text)
            distribution_date = int(info.find('distribution_date').text)
            version = int(info.find('version').text)
            inf_ver = int(info.find('inf_ver').text)
            
            struct.id = id
            struct.title = title
            struct.title_yomigana = title_yomigana
            struct.artist = artist
            struct.artist_yomigana = artist_yomigana
            struct.ascii = ascii
            struct.bpm_max = bpm_max
            struct.bpm_min = bpm_min
            struct.date = distribution_date # 年月日
            # 1是Booth
            # 2是Infinite(inf)
            # 3是Gravity(grv)
            # 4是Heavenly(hvn)
            # 5是Vivid(vvd)
            # 6是Exceed(xcd)
            struct.version = version
            struct.inf_ver = inf_ver # 第4个难度的版本(0为没有)
            
            diff_list : list[str] = []
            
            diffs : dict[str, Difficulty] = {}
            
            difficulty = music.find('difficulty')
            if difficulty is not None:
                for diff in difficulty:
                    diff_tag = diff.tag
                    
                    difnum = int(diff.find('difnum').text)
                    
                    if difnum == 0:
                        continue
                    
                    diff_label = None
                    
                    if diff_tag == "novice":
                        diff_label = 'nov'
                    elif diff_tag == "advanced":
                        diff_label = 'adv'
                    elif diff_tag == "exhaust":
                        diff_label = 'exh'
                    elif diff_tag == "infinite":
                        if inf_ver == 0:
                            continue
                        elif inf_ver == 2:
                            diff_label = 'inf'
                        elif inf_ver == 3:
                            diff_label = 'grv'
                        elif inf_ver == 4:
                            diff_label = 'hvn'
                        elif inf_ver == 5:
                            diff_label = 'vvd'
                        elif inf_ver == 6:
                            diff_label = 'xcd'
                    elif diff_tag == "maximum":
                        diff_label = 'mxm'
                    
                    diff_list.append(diff_label)
                    
                    diffi = Difficulty()
                    
                    illustrator = diff.find('illustrator').text
                    effected_by = diff.find('effected_by').text
                    
                    find_max_exscore = diff.find('max_exscore')
                    
                    max_exscore = int(find_max_exscore.text) if find_max_exscore is not None else 0
                    
                    diffi.level = difnum
                    diffi.illustrator = illustrator
                    diffi.effected_by = effected_by
                    diffi.max_exscore = max_exscore
                    
                    radar = diff.find('radar')
                    
                    diffi_radar = Radar()
                    
                    if radar is not None:
                        find_notes = radar.find('notes')
                        
                        diffi_radar.notes = int(find_notes.text) if find_notes is not None else 0
                            
                        find_peak = radar.find('peak')
                        diffi_radar.peak = int(find_peak.text) if find_peak is not None else 0
                        
                        find_tsumami = radar.find('tsumami')
                        diffi_radar.tsumami = int(find_tsumami.text) if find_tsumami is not None else 0
                        
                        find_tricky = radar.find('tricky')
                        diffi_radar.tricky = int(find_tricky.text) if find_tricky is not None else 0
                        
                        find_hand_trip = radar.find('hand-trip')
                        diffi_radar.hand_trip = int(find_hand_trip.text) if find_hand_trip is not None else 0
                        
                        find_one_hand = radar.find('one-hand')
                        diffi_radar.one_hand = int(find_one_hand.text) if find_one_hand is not None else 0
                        
                    diffi.radar = diffi_radar
                    
                    diffs[diff_label] = diffi
                    # for subchild in child:
                        # 输出每个子标签的名称和文本内容
                    #    print(f"  SubTag: <{subchild.tag}>, Text: {subchild.text}")

                    # print()  # 添加空行以便于阅读
            
            struct.diff_list = diff_list
            struct.diffs = diffs
            
            self.__sdvx_dict[id] = struct
    
    # 通过id获取曲目      
    def get(self, id : str | int = None):
        if id is None:
            return self.__sdvx_dict
        
        if isinstance(id, int):
            id = str(id)
        
        return self.__sdvx_dict[id]
    
    # 判断曲目是否存在
    def exist(self, id : str | int):
        if isinstance(id, int):
            id = str(id)
            
        return id in self.__sdvx_dict
        
    # 曲目匹配
    def match(self, query: str, is_nocase : bool = True, is_fuzzy : bool = True) -> list[str]:
        # 转换查询为小写，方便匹配
        if is_nocase:
            query = query.lower()
            
        # 存储匹配的结果
        matches = []
        # 遍历字典，进行模糊匹配
        for key, value in self.__sdvx_dict.items():
            title = value.title
            if is_nocase:
                title = title.lower()
            
            if is_fuzzy:
                if query in title:
                    matches.append(key)
            else:
                if query == title:
                    matches.append(key)
        return matches
    
    # 初始化解析
    def __alias_json_gen(self, alias_file: str = SDVX_ALIASES_PATH):
        if not os.path.exists(alias_file):
            # 创建文件并写入初始内容
            with open(alias_file, 'w', encoding='utf-8') as file:
                json.dump({}, file)  # 写入一个空的 JSON 对象
    
    # 添加别名
    def addali(self, id: str | int, new_alias: str):
        if isinstance(id, int):
            id = str(id)
            
        if not self.exist(id):
            return -2 # 不存在这首歌的id
            
        new_alias = new_alias.strip()
            
        for aliases in self.__aliases.values():
            for alias in aliases:
                if alias == new_alias:
                    return -1 # 已存在
                
        if id not in self.__aliases:
            self.__aliases[id] = []
            
        self.__aliases[id].append(new_alias)
            
        with open(SDVX_ALIASES_PATH, 'w', encoding='utf-8') as file:
            json.dump(self.__aliases, file, ensure_ascii=False)
            
        return 0 # 添加成功
    
    # 删除别名
    def delali(self, del_alias: str):
        found = False
        
        music_id = None
        
        for id, aliases in self.__aliases.items():
            for alias in aliases:
                if alias == del_alias:
                    found = True
                    music_id = id
                    break
        
        if not found:
            return -1 # 没有找到
        
        self.__aliases[music_id].remove(del_alias)
        
        with open(SDVX_ALIASES_PATH, 'w', encoding='utf-8') as file:
            json.dump(self.__aliases, file, ensure_ascii=False)
            
        return 0
    
    # 通过曲目ID获取曲目别名
    def getali(self, id: str | int = None):
        if id is None:
            return self.__aliases, 0
        
        if isinstance(id, int):
            id = str(id)
        
        if not self.exist(id):
            return None, -1 # 不存在这首歌的id
        
        if id in self.__aliases:
            return self.__aliases[id], 0
        
        self.__aliases[id] = []
        
        with open(SDVX_ALIASES_PATH, 'w', encoding='utf-8') as file:
            json.dump(self.__aliases, file, ensure_ascii=False)
        
        return self.__aliases[id], 0
    
    # 别名匹配
    def matchali(self, query: str, is_nocase : bool = True, is_fuzzy : bool = True):
        if is_nocase:
            query = query.lower()
            
        # 存储匹配的结果
        matches = []
        # 遍历字典，进行模糊匹配
        for key, aliases in self.__aliases.items():
            for alias in aliases:
                if is_nocase:
                    alias = alias.lower()
                
                if is_fuzzy:
                    if query in alias:
                        matches.append((key, alias))
                else:
                    if query == alias:
                        matches.append((key, alias))
        return matches
    
async def return_url(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    content_type = response.headers['Content-Type']
    if content_type == "image/webp":
        return url
    return None

class SDVX_INDEX():
    def __init__(self, url : str = SDVX_INDEX_URL):
        self.url : str = url
        
    # 1(NOV)
    # 2(ADV)
    # 3(EXH)
    # 4i(2代)
    # 4g(3代)
    # 4h(4代)
    # 4v(5代)
    # 4x(6代)
    # 5(MXM)
    __LEVEL_TRANS__ = {
        'nov': '1',
        'adv': '2',
        'exh': '3',
        'inf': '4i',
        'grv': '4g',
        'hvn': '4h',
        'vvd': '4v',
        'xcd': '4x',
        'mxm': '5'
    }
        # 获取铺面
    async def chart(self, id : int | str, level : str, ascii: str):
        if isinstance(id, str):
            id = int(id)
        if isinstance(id, int):
            id = pad_with_zeros(id)
        
        level = self.__LEVEL_TRANS__[level]
        
        img_prefix = 'img'
        resname = f'{id}_{ascii}'
        
        # chart: 1n, 2a, 3e, 4i, 5m
        chart_level = level[0]
        
        urls = []  
        for i in range(1, 5 + 1):
            jacket_url = f"{self.url}/{img_prefix}/{resname}/jk_{id}_{i}_b.webp"
            urls.append(jacket_url)
    
        tasks = [asyncio.ensure_future(return_url(url)) for url in urls]  
        results = await asyncio.gather(*tasks)
        for index, value in enumerate(results):
            if value is None:
                results[index] = results[index - 1]
        
        ret_jacket_url = results[int(chart_level) - 1]
        
        if chart_level == '1':
            chart_level += 'n'
        elif chart_level == '2':
            chart_level += 'a'
        elif chart_level == '3':
            chart_level += 'e'
        elif chart_level == '4':
            chart_level += 'i'
        elif chart_level == '5':
            chart_level += 'm'
        
        chart_url_base = f"{self.url}/{img_prefix}/{resname}/{resname}_{chart_level}"
        
        urls = {
            "jacket": ret_jacket_url,
            "charts": {
                "cmod": {
                    "normal": f"{chart_url_base}_cmod_rendered.png",
                    "mirror": f"{chart_url_base}_cmod_rendered_mirror.png"
                },
                "column": {
                    "normal": f"{chart_url_base}_column_rendered.png",
                    "mirror": f"{chart_url_base}_column_rendered_mirror.png"
                }
            }
        }

        return urls

SDVXManager = SDVX_MANAGER(SDVX_XML_PATH)
SDVXIndex = SDVX_INDEX(SDVX_INDEX_URL)

async def main():
    print(SDVXManager.match("晕"))
    for id, alias in SDVXManager.matchali("晕船"):
        print(id, alias)
    v = SDVXManager.get(1970)
    print(await SDVXIndex.chart(v.id, 'mxm', v.ascii))
    # print(SDVXManager.addali(1495, "土蜘蛛"))
    # print(SDVXManager.delali("土蜘蛛"))

if __name__ == "__main__":
    asyncio.run(main())