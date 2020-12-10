import hoshino
from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('甩锅')

@sv.on_prefix('禁言')
async def tosspot(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '?')
    print(len(ev.message))
    print(ev.message[0].type)
    target = int(ev.message[0].data['qq'])
    time = int(ev.message[1].data['text'].strip())
    await hoshino.get_bot().set_group_ban(self_id=ev.self_id, group_id=ev.group_id, user_id=target, duration=time)