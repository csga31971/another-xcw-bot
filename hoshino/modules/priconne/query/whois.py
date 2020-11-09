from hoshino.typing import CQEvent, MessageSegment
from hoshino.util import FreqLimiter
from hoshino.modules.pcrdescguess import _chara_data
from .. import chara
from . import sv

lmt = FreqLimiter(5)
tjlmt = FreqLimiter(20)

@sv.on_suffix(('是谁', '是誰'))
@sv.on_prefix(('谁是', '誰是'))
async def whois(bot, ev: CQEvent):
    uid = ev.user_id
    if not lmt.check(uid):
        await bot.send(ev, f'兰德索尔花名册冷却中(剩余 {int(lmt.left_time(uid)) + 1}秒)', at_sender=True)
        return
    lmt.start_cd(uid)

    name = ev.message.extract_plain_text().strip()
    if not name:
        await bot.send(ev, '请发送"谁是"+别称，如"谁是霸瞳"')
        return
    id_ = chara.name2id(name)
    confi = 100
    if id_ == chara.UNKNOWN:
        id_, guess_name, confi = chara.guess_id(name)
    c = chara.fromid(id_)
    
    msg = ''
    if confi < 100:
        lmt.start_cd(uid, 120)
        msg = f'兰德索尔似乎没有叫"{name}"的人...\n角色别称补全计划: github.com/Ice-Cirno/HoshinoBot/issues/5'
        await bot.send(ev, msg)
        msg = f'\n您有{confi}%的可能在找{guess_name} '

    if confi > 60:
        msg += f'{c.icon.cqcode} {c.name}'
        await bot.send(ev, msg, at_sender=True)

@sv.on_suffix('体检')
@sv.on_prefix('体检')
async def whois(bot, ev: CQEvent):
    uid = ev.user_id
    if not tjlmt.check(uid):
        await bot.send(ev, f'兰德索尔人口普查冷却中(剩余 {int(tjlmt.left_time(uid)) + 1}秒)', at_sender=True)
        return
    tjlmt.start_cd(uid)

    name = ev.message.extract_plain_text().strip()
    if not name:
        await bot.send(ev, '请发送"体检"+别称，如"体检您啪"')
        return
    id_ = chara.name2id(name)
    if(id_ not in _chara_data.CHARA_DATA.keys()):
        await bot.send(ev, f'没有体检数据')
        return
    confi = 100
    if id_ == chara.UNKNOWN:
        id_, guess_name, confi = chara.guess_id(name)
    c = chara.fromid(id_)
    
    msg = ''
    chara_desc_list = _chara_data.CHARA_DATA[id_]
    if confi < 100:
        tjlmt.start_cd(uid, 120)
        msg = f'兰德索尔似乎没有叫"{name}"的人...\n角色别称补全计划: github.com/Ice-Cirno/HoshinoBot/issues/5'
        await bot.send(ev, msg)
        msg = f'\n您有{confi}%的可能在找{guess_name} '

    if confi > 60:
        desc_lable = ['名字', '公会', '生日', '年龄', '身高', '体重', '血型', '种族', '喜好', '声优']
        desc_suffix = ['', '', '', '', 'cm', 'kg', '', '', '', '']
        msg += f'{c.icon.cqcode} {c.name}\n'
        for i in range(1, 10):
            msg += f'{desc_lable[i]}: {chara_desc_list[i]}{desc_suffix[i]}\n'
        await bot.send(ev, msg, at_sender=True)