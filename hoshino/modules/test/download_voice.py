from bs4 import BeautifulSoup
import requests
import hoshino
import os
import aiohttp
from hoshino import Service
from hoshino.modules.priconne import _pcr_data
from hoshino.typing import CQEvent

BLACK_LIST = [1908, 4031,9000,9401,1999]
HOSHINO_RES_PATH = os.path.expanduser(hoshino.config.RES_DIR)
DIR_PATH = os.path.join(HOSHINO_RES_PATH, 'record')
sv = Service('test')

@sv.on_fullmatch("下下下")
async def download_chara_battle_voice(bot, ev: CQEvent):
    l = []
    ids = []
    logger = sv.logger
    url = f'https://redive.estertion.win/sound/unit_battle_voice/'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    for a in soup.find_all('a'):
        s = a['href'][:-1]
        if s.isdigit():
            l.append(s)
            if(int(s[0:4]) in _pcr_data.CHARA_NAME.keys() and int(s[0:4]) not in BLACK_LIST):
                ids.append(int(s[0:4]))
    for eid in l:
        id = int(eid[0:4])
        if(id in _pcr_data.CHARA_NAME.keys() and id not in BLACK_LIST):
            chara_dir_path = os.path.join(DIR_PATH, eid)
            if not os.path.exists(chara_dir_path):
                os.makedirs(chara_dir_path)
            url = f'https://redive.estertion.win/sound/unit_battle_voice/{eid}/'
            soup = BeautifulSoup(requests.get(url).text, 'html.parser')
            for a in soup.find_all('a'):
                file_name = a['href']
                if(file_name!= "../"):
                    url = f'https://redive.estertion.win/sound/unit_battle_voice/{eid}/{file_name}'
                    file_path = os.path.join(chara_dir_path, file_name)
                    logger.info(f'准备下载{file_name}...')
                    if not await download(url, file_path):
                        logger.info(f'下载{file_name}失败, 准备删除文件.')
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        logger.info(f'删除文件{file_name}成功.')
                    else:
                        logger.info(f'下载{file_name}成功!')
   
async def download(url, path):
    try:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                content = await resp.read()
                with open(path, 'wb') as f:
                    f.write(content)
        return True
    except:
        return False