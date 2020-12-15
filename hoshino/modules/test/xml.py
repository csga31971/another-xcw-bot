import hoshino
from hoshino import Service, util, priv
from hoshino.typing import MessageSegment, CQEvent
from lxml import etree

sv = Service('xml')

@sv.on_prefix('xml')
async def xml(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '?')
    xml_str = ev.message[1].data['text'].strip()
    try:
        xml = etree.XML(xml_str)
        xml_segment = f'[CQ:xml,data={xml}]'
        await bot.send(ev, xml_segment)
    except Exception as e:
        print(str(e))
        await bot.finish(ev, '看不懂看不懂看不懂')
        
@sv.on_fullmatch('测试123')
async def test123(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.finish(ev, '?')
    xml_str = '''
    <?xml version='1.0' encoding='UTF-8' standalone='yes'?>
    <msg templateID="123" url="https://osu.ppy.sh" serviceID="1" action="web" actionData="" a_actionData="" i_actionData="" brief="免费领取2077豪华版" flag="0">
        <item layout="2">
            <title>免费领取2077豪华版</title>
            <summary>免费领取2077豪华版</summary>
        </item>
        <source url="https://osu.ppy.sh" appid="0" action="web" actionData="" i_actionData=""/>
    </msg>
    '''.strip()

    try:
        # xml = etree.XML(xml_str)
        xml_segment = f'[CQ:xml,data={xml_str},resid=1]'
        await bot.send(ev, xml_segment)
    except Exception as e:
        print(str(e))
        await bot.finish(ev, '看不懂看不懂看不懂')