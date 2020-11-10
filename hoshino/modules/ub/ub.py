import os
import random

from nonebot.exceptions import CQHttpError
from nonebot import MessageSegment
from hoshino import R, Service, priv

sv = Service('ub', enable_on_default=True, visible=False)
xcw_folder = R.get('record/ub/').path

def get_xcw():
    filename = "ub.amr"
    rec = R.get('record/ub/', filename)
    return rec


@sv.on_fullmatch('来发ub', only_to_me=True)
async def xcw(bot, ev) -> MessageSegment:
    # conditions all ok, send a xcw.
    file = get_xcw()
    try:
        rec = MessageSegment.record(f'file:///{os.path.abspath(file.path)}')
        await bot.send(ev, rec)
    except CQHttpError:
        sv.logger.error("发送失败")