import hoshino
import os, json, aiohttp, random, math, asyncio
from PIL import Image
from io import BytesIO
from hoshino import R, Service, priv, util
from hoshino.typing import MessageSegment, CQEvent

sv = Service('memberavatarguess')

PIC_SIDE_LENGTH = 25
ONE_TURN_TIME = 20
HOSHINO_RES_PATH = os.path.expanduser(hoshino.config.RES_DIR)
IMG_DIR_PATH = os.path.join(HOSHINO_RES_PATH, 'img')

class WinnerJudger:
    def __init__(self):
        self.on = {}
        self.winner = {}
        self.correct_chara_id = {}
    
    def record_winner(self, gid, uid):
        self.winner[gid] = str(uid)
        
    def get_winner(self, gid):
        return self.winner[gid] if self.winner.get(gid) is not None else ''
        
    def get_on_off_status(self, gid):
        return self.on[gid] if self.on.get(gid) is not None else False
    
    def set_correct_chara_id(self, gid, cid):
        self.correct_chara_id[gid] = cid
    
    def get_correct_chara_id(self, gid):
        return self.correct_chara_id[gid] if self.correct_chara_id.get(gid) is not None else -1
    
    def turn_on(self, gid):
        self.on[gid] = True
        
    def turn_off(self, gid):
        self.on[gid] = False
        self.winner[gid] = ''
        self.correct_chara_id[gid] = -1

winner_judger = WinnerJudger()

@sv.on_fullmatch('测试111')
async def memberguess(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '¿')
        return
    if winner_judger.get_on_off_status(ev.group_id):
        await bot.send(ev, "此轮游戏还没结束，请勿重复使用指令")
        return
    group_id = ev.get('group_id')
    group_dir_path = os.path.join(IMG_DIR_PATH, 'member', str(group_id))
    winner_judger.turn_on(group_id)
    if not os.path.exists(group_dir_path):
        await download_group_member_avatars(bot, ev)
    avatar_list = os.listdir(group_dir_path)
    user_id_list = []
    for a in avatar_list:
        user_id = int(a.split('.')[0])
        user_id_list.append(user_id)
    list_len = len(user_id_list)
    index = random.randint(0, list_len-1)
    chosen_avatar = avatar_list[index]
    chosen_user_id = user_id_list[index]
    winner_judger.set_correct_chara_id(ev.group_id, chosen_user_id)
    chosen_avatar_icon = R.img(f'member/{group_id}/{chosen_avatar}')
    chosen_avatar_img = chosen_avatar_icon.open()
    left = math.floor(random.random()*(141-PIC_SIDE_LENGTH))
    upper = math.floor(random.random()*(141-PIC_SIDE_LENGTH))
    cropped = chosen_avatar_img.crop((left, upper, left+PIC_SIDE_LENGTH, upper+PIC_SIDE_LENGTH))
    cropped = MessageSegment.image(util.pic2b64(cropped))
    msg = f'猜猜这个图片是哪位群友头像的一部分?({ONE_TURN_TIME}s后公布答案){cropped}'
    await bot.send(ev, msg)
    await asyncio.sleep(ONE_TURN_TIME)
    if winner_judger.get_winner(ev.group_id) != '':
        winner_judger.turn_off(ev.group_id)
        return
    correct_user_id = winner_judger.get_correct_chara_id(ev.group_id)
    at_correct_user = MessageSegment.at(correct_user_id)
    msg =  f'正确答案是: {at_correct_user}\n很遗憾，没有人答对~'
    winner_judger.turn_off(ev.group_id)
    await bot.send(ev, msg)

@sv.on_fullmatch('更新群友头像')
async def update_avatars(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.SUPERUSER):
        await bot.send(ev, '¿')
        return
    await download_group_member_avatars(bot, ev)
    await bot.send(ev, '我好了')

@sv.on_message()
async def on_input_chara_name(bot, ev: CQEvent):
    try:
        if winner_judger.get_on_off_status(ev.group_id):
            print(len(ev.message))
            print(ev.message[0].type)
            if(not (len(ev.message) == 1 and ev.message[0].type == 'at')):
                print(ev.message)
                return
            cid = int(ev.message[0].data['qq'])
            print(cid)
            if(cid == winner_judger.get_correct_chara_id(ev.group_id)):
                winner_judger.record_winner(ev.group_id, ev.user_id)
                user_card_dict = await get_user_card_dict(bot, ev.group_id)
                user_card = uid2card(ev.user_id, user_card_dict)
                msg_part = f'{user_card}猜对了，真厉害！\n(此轮游戏将在时间到后自动结束，请耐心等待)'
                correct_user_id = winner_judger.get_correct_chara_id(ev.group_id)
                at_correct_user = MessageSegment.at(correct_user_id)
                msg =  f'正确答案是: {at_correct_user}\n{msg_part}'
                #winner_judger.turn_off(ev.group_id)
                await bot.send(ev, msg)
    except Exception as e:
        await bot.send(ev, '错误:\n' + str(e))


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

async def download_group_member_avatars(bot, ev):
    logger = sv.logger
    group_id = ev.get('group_id')
    group_dir_path = os.path.join(IMG_DIR_PATH, 'member', str(group_id))
    await bot.send(ev, '初始化中，请勿进行其他操作')
    if(not os.path.exists(group_dir_path)):
        os.mkdir(group_dir_path)
    group_member_info = await bot.get_group_member_list(group_id=group_id)
    for m in group_member_info:
        user_id = m['user_id']
        url = f'http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=160'
        file_name = f'{user_id}.jpg'
        file_path = os.path.join(group_dir_path, file_name)
        if(os.path.exists(file_path)):
            os.remove(file_path)
        logger.info(f'准备下载{file_name}...')
        if not await download(url, file_path):
            logger.info(f'下载{file_name}失败, 准备删除文件.')
            if os.path.exists(file_path):
                os.remove(file_path)
            logger.info(f'删除文件{file_name}成功.')
        else:
            logger.info(f'下载{file_name}成功!')

async def get_user_card_dict(bot, group_id):
    mlist = await bot.get_group_member_list(group_id=group_id)
    d = {}
    for m in mlist:
        d[m['user_id']] = m['card'] if m['card']!='' else m['nickname']
    return d

def uid2card(uid, user_card_dict):
    return str(uid) if uid not in user_card_dict.keys() else user_card_dict[uid]