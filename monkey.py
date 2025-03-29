import json
import os
from nonebot.permission import SUPERUSER
from nonebot import on_message, on_command
from nonebot.adapters.onebot.v11 import (
    Bot, 
    GroupMessageEvent, 
    Message
)
from nonebot.params import CommandArg
from nonebot.log import logger

# JSON 文件路径
LISTEN_DATA_FILE = "listen_data.json"

# 读取监听数据（QQ 号 + 群号）
def load_listen_data():
    if os.path.exists(LISTEN_DATA_FILE):
        try:
            with open(LISTEN_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("qq_list", [])), set(data.get("group_list", []))
        except json.JSONDecodeError:
            logger.error("JSON 解析失败，已重置监听列表")
    return set(), set()

# 保存监听数据
def save_listen_data():
    with open(LISTEN_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"qq_list": list(target_qq), "group_list": list(target_groups)}, f, ensure_ascii=False, indent=4)

# 加载监听的 QQ 号和群号
target_qq, target_groups = load_listen_data()
logger.info(f"已加载监听 QQ 号：{target_qq}")
logger.info(f"已加载监听群号：{target_groups}")

# 监听群聊消息（仅监听指定群的指定用户）
listen_user = on_message()

@listen_user.handle()
async def handle_monitor(event: GroupMessageEvent, bot: Bot):
    """监听群消息并添加表情"""
    if event.group_id in target_groups and event.user_id in target_qq:
        try:
            await bot.set_msg_emoji_like(message_id=event.message_id, emoji_id='128053')
            logger.success(f"已为群 {event.group_id} 用户 {event.user_id} 的消息 {event.message_id} 添加🐵表情")
        except Exception as e:
            logger.error(f"表情回复失败：{str(e)}")

# 添加监听 QQ 号
add_listen_qq = on_command("添加监听QQ", permission=SUPERUSER)

@add_listen_qq.handle()
async def add_listen_user(args: Message = CommandArg()):
    """添加监听的 QQ 号"""
    global target_qq
    try:
        user_id = int(str(args).strip())
        if user_id in target_qq:
            await add_listen_qq.finish(f"QQ {user_id} 已在贴🐵列表")
        target_qq.add(user_id)
        save_listen_data()
        await add_listen_qq.finish(f"已添加贴🐵 QQ：{user_id}")
    except ValueError:
        await add_listen_qq.finish("请输入正确的 QQ 号")

# 删除监听 QQ 号
remove_listen_qq = on_command("删除监听QQ", permission=SUPERUSER)

@remove_listen_qq.handle()
async def remove_listen_user(args: Message = CommandArg()):
    """删除监听的 QQ 号"""
    global target_qq
    try:
        user_id = int(str(args).strip())
        if user_id not in target_qq:
            await remove_listen_qq.finish(f"QQ {user_id} 不在贴🐵列表")
        target_qq.remove(user_id)
        save_listen_data()
        await remove_listen_qq.finish(f"已取消贴🐵 QQ：{user_id}")
    except ValueError:
        await remove_listen_qq.finish("请输入正确的 QQ 号")

# 查看监听 QQ 号
check_listen_qq = on_command("查看监听QQ", permission=SUPERUSER)

@check_listen_qq.handle()
async def check_listen_users():
    """查看当前监听的 QQ 号"""
    if target_qq:
        await check_listen_qq.finish(f"当前贴🐵的 QQ 号：{', '.join(map(str, target_qq))}")
    else:
        await check_listen_qq.finish("当前没有贴🐵任何 QQ 号")

# 添加监听群
add_listen_group = on_command("添加监听群", permission=SUPERUSER)

@add_listen_group.handle()
async def add_listen_group_func(args: Message = CommandArg()):
    """添加监听的群"""
    global target_groups
    try:
        group_id = int(str(args).strip())
        if group_id in target_groups:
            await add_listen_group.finish(f"群 {group_id} 已在贴🐵列表")
        target_groups.add(group_id)
        save_listen_data()
        await add_listen_group.finish(f"已添加贴🐵群：{group_id}")
    except ValueError:
        await add_listen_group.finish("请输入正确的群号")

# 删除监听群
remove_listen_group = on_command("删除监听群", permission=SUPERUSER)

@remove_listen_group.handle()
async def remove_listen_group_func(args: Message = CommandArg()):
    """删除监听的群"""
    global target_groups
    try:
        group_id = int(str(args).strip())
        if group_id not in target_groups:
            await remove_listen_group.finish(f"群 {group_id} 不在贴🐵列表")
        target_groups.remove(group_id)
        save_listen_data()
        await remove_listen_group.finish(f"已取消贴🐵群：{group_id}")
    except ValueError:
        await remove_listen_group.finish("请输入正确的群号")

# 查看监听群
check_listen_groups = on_command("查看监听群", permission=SUPERUSER)

@check_listen_groups.handle()
async def check_listen_groups_func():
    """查看当前监听的群"""
    if target_groups:
        await check_listen_groups.finish(f"当前贴🐵的群号：{', '.join(map(str, target_groups))}")
    else:
        await check_listen_groups.finish("当前没有贴🐵任何群")
