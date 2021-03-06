"""
作者艾琳有栖

nga风纪区的黑名单

数据来源 https://docs.qq.com/sheet/DV1JqSHJ5aEVNUG1q
由于数据是excel表格 格式不是很规范 只能通过固定的算法得到数据
只要表格的列数增加不修改代码后会造成无法使用

放到插件目录下就好比如
hoshino/modules/priconne/clan_black_list.py

使用方法是

失信UID或者QQ号

例如根据UID搜索
失信1384411921966

例如根据QQ搜索
失信2782133103
"""
import json
import time
import requests
import asyncio
from hoshino import Service
from hoshino.typing import CQEvent

sv = Service('prc-cbl')

# 忽略的表头有4行
keep_head_column = 5
# 每行空白格数是20个
blank_column = 21
# 每行数据开始前有一个空格
blank_head = 0
# 每行一共有多少个数据
data_count = 8
# 数据的结构是啥
data_name = [
    'uid',  
    'name',  
    'qq',  
    'behavior',  
    'quality',  
    'remark',  
    'report',  
    'clanBattle'  
]

# 更新到缓存中 只需要查询这里的数据就好
clan_black_list_data = []


@sv.on_prefix('失信')
async def prc_cbl(bot, ev: CQEvent):
    cbl_list = filter_cbl(ev.message.extract_plain_text().strip())
    await print_cbl(cbl_list, bot, ev)


async def print_cbl(cbl_list, bot, ev):
    if not len(cbl_list):
        await bot.send(ev, '木有找到相关的信息呢\n如果想提交黑名单\n请加群：1067027773\n填群文件提交表交由管理并附带证据进行添加及更改')
        return

    for item in cbl_list:
        msg = 'UID: {uid}\nQQ : {qq}\n昵称: {name}\n性质: {quality}\n会战: {clanBattle}\n行为: \n  {behavior}\n备注: \n  {' \
              'remark}\n'.format
        await bot.send(ev, msg(**item))


def filter_cbl(target):
    res = []
    if target == '' or target == '/' or target == '0':
        return res
    for item in clan_black_list_data:
        if item['uid'] == target or item['qq'] == target:
            res.append(item)
    return res


# 更新在线表格数据
async def update_black_list():
    try:
        url = f'https://docs.qq.com/dop-api/opendoc?outformat=1&normal=1&preview_token=&t={int(time.time())}&id=DV1JqSHJ5aEVNUG1q&tab=BB08J2'
        info = json.loads(requests.get(url).text)
        sheet = info['clientVars']['collab_client_vars']['initialAttributedText']['text'][0][6][0]['c'][1]
        sheet_list = list_split([i for i in sheet.values()], blank_column + blank_head + data_count)[keep_head_column:]
        clan_black_list_data.clear()
        for info in sheet_list:
            black_list = []
            for item in info[blank_head:blank_head + data_count]:
                black_list.append(f'{item["2"][1]}' if item.get('2') else '')
            if ''.join(black_list).strip():
                clan_black_list_data.append(dict(zip(data_name, black_list)))
        print('定时任务: 更新工会战黑名单成功')
    except Exception as e:
        print(e)
        print('定时任务: 更新工会战黑名单失败')


def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]


# 程序启动的时候获取一下数据
def run_event_loop():
    loop = asyncio.new_event_loop()
    loop.run_until_complete(update_black_list())
    loop.close()


run_event_loop()


# 每天0点更新一下数据
@sv.scheduled_job('cron', hour='0', minute='0')
async def run_update_black_list():
    await update_black_list()
