import hoshino
from hoshino import Service, priv
from hoshino.typing import CQEvent
from hoshino.modules.priconne._pcr_data import chara_master
from hoshino.modules.priconne import chara

sv = Service('addnickname')

@sv.on_prefix('添加昵称')
async def tosspot(bot, ev: CQEvent):
    message_text = ev.message.extract_plain_text().strip()
    message_split = message_text.split()
    if(len(message_split) != 2):
        await bot.finish(ev, '小仓唯教你要这样用：添加昵称 <角色名/昵称> <新昵称>')
    name = message_split[0]
    new_name = message_split[1]
    id = chara.name2id(name)
    if id == chara.UNKNOWN:
        await bot.finish(ev, '你在给谁加呢，小仓唯听不懂呀')
    if(chara_master.check_duplicated(new_name)):
        await bot.finish(ev, '已经有人叫这个名字了哦')
    chara_master.add_nickname(id, new_name)
    await bot.send(ev, '添加成功!')