import os
import random

from nonebot.exceptions import CQHttpError
from nonebot import MessageSegment
from hoshino import R, Service, priv

sv = Service('ub', enable_on_default=True, visible=False)

@sv.on_fullmatch('来发ub', only_to_me=True)
async def xcw(bot, ev) -> MessageSegment:
    file = R.get('record/ub', 'ub.mp3')
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")

@sv.on_fullmatch('喷水', only_to_me=True)
async def penshui(bot, ev) -> MessageSegment:
    file = R.get('record/103601', 'vo_btl_103601_ub_100.m4a')
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
        cq_code = R.img('penshui.png').cqcode
        await bot.send(ev, cq_code)
    except CQHttpError:
        sv.logger.error("发送失败")