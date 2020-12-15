import importlib
import pygtrie
from fuzzywuzzy import fuzz, process
from PIL import Image
from io import BytesIO
import requests, random

from hoshino import R, log, sucmd, util
from hoshino.typing import CommandSession

from . import _ark_data

logger = log.new_logger('chara')
UNKNOWN = 1000
UnavailableChara = {
    1067,   # 穗希
    1068,   # 晶
    1069,   # 霸瞳
    1072,   # 可萝爹
    1073,   # 拉基拉基
    1102,   # 泳装大眼
}

try:
    gadget_equip = R.img('priconne/gadget/equip.png').open()
    gadget_star = R.img('priconne/gadget/star.png').open()
    gadget_star_dis = R.img('priconne/gadget/star_disabled.png').open()
    gadget_star_pink = R.img('priconne/gadget/star_pink.png').open()
    unknown_chara_icon = R.img(f'arknights/unit/icon_unit_{UNKNOWN}31.png').open()
except Exception as e:
    logger.exception(e)


class Roster:

    def __init__(self):
        self._roster = pygtrie.CharTrie()
        self.update()
    
    def update(self):
        importlib.reload(_ark_data)
        self._roster.clear()
        for idx, names in _ark_data.CHARA_NAME.items():
            for n in names:
                n = util.normalize_str(n)
                if n not in self._roster:
                    self._roster[n] = idx
                else:
                    logger.warning(f'priconne.chara.Roster: 出现重名{n}于id{idx}与id{self._roster[n]}')
        self._all_name_list = self._roster.keys()


    def get_id(self, name):
        name = util.normalize_str(name)
        return self._roster[name] if name in self._roster else UNKNOWN


    def guess_id(self, name):
        """@return: id, name, score"""
        name, score = process.extractOne(name, self._all_name_list)
        return self._roster[name], name, score


    def parse_team(self, namestr):
        """@return: List[ids], unknown_namestr"""
        namestr = util.normalize_str(namestr)
        team = []
        unknown = []
        while namestr:
            item = self._roster.longest_prefix(namestr)
            if not item:
                unknown.append(namestr[0])
                namestr = namestr[1:].lstrip()
            else:
                team.append(item.value)
                namestr = namestr[len(item.key):].lstrip()
        return team, ''.join(unknown)


roster = Roster()

def name2id(name):
    return roster.get_id(name)

def fromid(id_, star=0, equip=0):
    return Chara(id_, star, equip)

def fromname(name, star=0, equip=0):
    id_ = name2id(name)
    return Chara(id_, star, equip)

def guess_id(name):
    """@return: id, name, score"""
    return roster.guess_id(name)

def is_npc(id_):
    if id_ in UnavailableChara:
        return True
    else:
        return not ((1000 < id_ < 1200) or (1800 < id_ < 1900))

def gen_team_pic(team, size=64, star_slot_verbose=True):
    num = len(team)
    des = Image.new('RGBA', (num*size, size), (255, 255, 255, 255))
    for i, chara in enumerate(team):
        src = chara.render_icon(size, star_slot_verbose)
        des.paste(src, (i * size, 0), src)
    return des

class Chara:

    def __init__(self, id_, star=0, equip=0):
        self.id = id_
        self.star = star
        self.equip = equip

    @property
    def name(self):
        return _ark_data.CHARA_NAME[self.id][0] if self.id in _ark_data.CHARA_NAME else _ark_data.CHARA_NAME[UNKNOWN][0]

    @property
    def is_npc(self) -> bool:
        return is_npc(self.id)

    @property
    def icon(self):
        star = '3' if 1 <= self.star <= 5 else '6'
        res = R.img(f'arknights/unit/icon_unit_{self.id}{star}1.png')
        if not res.exist:
            res = R.img(f'arknights/unit/icon_unit_{self.id}31.png')
        if not res.exist:
            res = R.img(f'arknights/unit/icon_unit_{self.id}11.png')
        if not res.exist:
            res = R.img(f'arknights/unit/icon_unit_{UNKNOWN}31.png')
        return res

    @property
    def icon136(self):
        rand = random.randint(0, 2)
        res = R.img(f'arknights/unit/icon_unit_{self.id}61.png')
        if not res.exist:
            rand = random.randint(0, 1)
            if(rand == 0):
                res = R.img(f'arknights/unit/icon_unit_{self.id}11.png')
            if(rand == 1):
                res = R.img(f'arknights/unit/icon_unit_{self.id}31.png')
        else:
            if(rand == 0):
                res = R.img(f'arknights/unit/icon_unit_{self.id}11.png')
            if(rand == 1):
                res = R.img(f'arknights/unit/icon_unit_{self.id}31.png')
            if(rand == 2):
                res = R.img(f'arknights/unit/icon_unit_{self.id}61.png')
        if not res.exist:
            res = R.img(f'arknights/unit/icon_unit_{UNKNOWN}31.png')
        return res

    def render_icon(self, size, star_slot_verbose=True) -> Image:
        try:
            pic = self.icon.open().convert('RGBA').resize((size, size), Image.LANCZOS)
        except FileNotFoundError:
            logger.error(f'File not found: {self.icon.path}')
            pic = unknown_chara_icon.convert('RGBA').resize((size, size), Image.LANCZOS)

        l = size // 6
        star_lap = round(l * 0.15)
        margin_x = ( size - 6*l ) // 2
        margin_y = round(size * 0.05)
        if self.star:
            for i in range(5 if star_slot_verbose else min(self.star, 5)):
                a = i*(l-star_lap) + margin_x
                b = size - l - margin_y
                s = gadget_star if self.star > i else gadget_star_dis
                s = s.resize((l, l), Image.LANCZOS)
                pic.paste(s, (a, b, a+l, b+l), s)
            if 6 == self.star:
                a = 5*(l-star_lap) + margin_x
                b = size - l - margin_y
                s = gadget_star_pink
                s = s.resize((l, l), Image.LANCZOS)
                pic.paste(s, (a, b, a+l, b+l), s)
        if self.equip:
            l = round(l * 1.5)
            a = margin_x
            b = margin_x
            s = gadget_equip.resize((l, l), Image.LANCZOS)
            pic.paste(s, (a, b, a+l, b+l), s)
        return pic



@sucmd('reload-ark-chara', force_private=False, aliases=('方舟重载角色花名册', ))
async def reload_pcr_chara(session: CommandSession):
    try:
        roster.update()
        await session.send('ok')
    except Exception as e:
        logger.exception(e)
        await session.send(f'Error: {type(e)}')
