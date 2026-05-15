# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import time
import asyncio
import pyrogram

from pyrogram import Client, filters, enums
from pyrogram.errors import (FloodWait,UserAlreadyParticipant,InviteHashExpired,UsernameNotOccupied)
from pyrogram.types import (InlineKeyboardMarkup,InlineKeyboardButton,Message)
from config import (API_ID,API_HASH,ERROR_MESSAGE,LOGIN_SYSTEM,STRING_SESSION,CHANNEL_ID,WAITING_TIME)
from database.db import db
from TechVJ.strings import HELP_TXT
from bot import TechVJUser


# Runtime Settings
RUNTIME_CHANNEL_ID = CHANNEL_ID
RUNTIME_WAITING_TIME = WAITING_TIME

# Cached User Clients
USER_CLIENTS = {}

# Progress Cache
PROGRESS_CACHE = {}


class batch_temp(object):
    IS_BATCH = {}


# =========================
# USER CLIENT CACHE SYSTEM
# =========================

async def get_user_client(user_id, session_string, api_id, api_hash):

    if user_id in USER_CLIENTS:
        return USER_CLIENTS[user_id]

    client = Client(
        f"user_{user_id}",
        session_string=session_string,
        api_id=api_id,
        api_hash=api_hash
    )

    await client.connect()

    USER_CLIENTS[user_id] = client

    return client


# =========================
# PROGRESS BAR
# =========================

async def progress_bar(current, total, message, start, text_type):

    now = time.time()

    if message.id not in PROGRESS_CACHE:
        PROGRESS_CACHE[message.id] = 0

    if now - PROGRESS_CACHE[message.id] < 2:
        return

    PROGRESS_CACHE[message.id] = now

    percentage = current * 100 / total

    speed = current / (now - start)

    elapsed_time = now - start

    time_to_completion = (
        (total - current) / speed
        if speed > 0 else 0
    )

    estimated_total_time = elapsed_time + time_to_completion

    elapsed_time = time.strftime(
        "%H:%M:%S",
        time.gmtime(elapsed_time)
    )

    estimated_total_time = time.strftime(
        "%H:%M:%S",
        time.gmtime(estimated_total_time)
    )

    bar_length = 20

    filled_bar_length = int(
        bar_length * current / total
    )

    bar = "█" * filled_bar_length + "░" * (
        bar_length - filled_bar_length
    )

    try:
        await message.edit_text(
            f"**{text_type}**\n\n"
            f"`{bar}`\n\n"
            f"⚡ **Progress:** `{percentage:.1f}%`\n"
            f"💾 **Done:** `{current / 1024 / 1024:.2f} MB`\n"
            f"📦 **Total:** `{total / 1024 / 1024:.2f} MB`\n"
            f"🚀 **Speed:** `{speed / 1024 / 1024:.2f} MB/s`\n"
            f"⏳ **ETA:** `{estimated_total_time}`"
        )

    except:
        pass


# =========================
# START
# =========================

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(
            message.from_user.id,
            message.from_user.first_name
        )

    buttons = [[
        InlineKeyboardButton(
            "❣️ Developer",
            url="https://t.me/kingvj01"
        )
    ], [
        InlineKeyboardButton(
            '🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ',
            url='https://t.me/vj_bot_disscussion'
        ),
        InlineKeyboardButton(
            '🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ',
            url='https://t.me/vj_bots'
        )
    ]]

    reply_markup = InlineKeyboardMarkup(buttons)

    await client.send_message(
        chat_id=message.chat.id,
        text=(
            f"<b>👋 Hi {message.from_user.mention}, "
            f"I am Save Restricted Content Bot.\n\n"
            f"For downloading restricted content /login first.\n\n"
            f"Know how to use bot by - /help</b>"
        ),
        reply_markup=reply_markup,
        reply_to_message_id=message.id
    )


# =========================
# SETTINGS
# =========================

@Client.on_message(filters.command(["setchannel"]) & filters.private)
async def set_channel(client: Client, message: Message):

    global RUNTIME_CHANNEL_ID

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/setchannel -100xxxxxxxxxx"
        )

    try:
        RUNTIME_CHANNEL_ID = int(message.command[1])

        await message.reply_text(
            f"✅ Channel changed to:\n"
            f"`{RUNTIME_CHANNEL_ID}`"
        )

    except:
        await message.reply_text(
            "❌ Invalid Channel ID."
        )


@Client.on_message(filters.command(["setwait"]) & filters.private)
async def set_wait(client: Client, message: Message):

    global RUNTIME_WAITING_TIME

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/setwait 2"
        )

    try:
        new_time = int(message.command[1])

        if new_time < 0:
            return await message.reply_text(
                "❌ Waiting time cannot be negative."
            )

        RUNTIME_WAITING_TIME = new_time

        await message.reply_text(
            f"✅ Waiting Time Updated To:"
            f" `{RUNTIME_WAITING_TIME}` sec"
        )

    except:
        await message.reply_text(
            "❌ Please provide valid number."
        )


@Client.on_message(filters.command(["getsettings"]) & filters.private)
async def get_settings(client: Client, message: Message):

    await message.reply_text(
        f"⚙ Current Settings:\n\n"
        f"📢 Channel ID: `{RUNTIME_CHANNEL_ID}`\n"
        f"⏳ Waiting Time: `{RUNTIME_WAITING_TIME}` sec"
    )


# =========================
# AUTO SET CHANNEL
# =========================

@Client.on_message(filters.forwarded & filters.private)
async def auto_set_channel(client: Client, message: Message):

    global RUNTIME_CHANNEL_ID

    if message.forward_from_chat:

        chat = message.forward_from_chat

        if chat.type in ["channel", "supergroup"]:

            RUNTIME_CHANNEL_ID = chat.id

            await message.reply_text(
                f"✅ Channel Auto Detected!\n\n"
                f"📢 Title: {chat.title}\n"
                f"🆔 ID: `{chat.id}`"
            )

        else:
            await message.reply_text(
                "❌ Please forward a channel message."
            )

    else:
        await message.reply_text(
            "❌ Cannot detect channel."
        )


# =========================
# HELP
# =========================

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):

    await client.send_message(
        chat_id=message.chat.id,
        text=f"{HELP_TXT}"
    )


# =========================
# CANCEL
# =========================

@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):

    batch_temp.IS_BATCH[message.from_user.id] = False

    await client.send_message(
        chat_id=message.chat.id,
        text="**Batch Cancelled Successfully.**"
    )


# =========================
# MAIN SAVE
# =========================

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):

    # Join Chat
    if (
        "https://t.me/+" in message.text
        or "https://t.me/joinchat/" in message.text
    ) and LOGIN_SYSTEM == False:

        if TechVJUser is None:
            return await client.send_message(
                message.chat.id,
                "String Session is not Set"
            )

        try:
            await TechVJUser.join_chat(message.text)

            await client.send_message(
                message.chat.id,
                "Chat Joined"
            )

        except UserAlreadyParticipant:
            await client.send_message(
                message.chat.id,
                "Chat already Joined"
            )

        except InviteHashExpired:
            await client.send_message(
                message.chat.id,
                "Invalid Link"
            )

        except Exception as e:
            await client.send_message(
                message.chat.id,
                f"Error: {e}"
            )

        return

    # Telegram Link
    if message.text.startswith("https://t.me/"):

        if batch_temp.IS_BATCH.get(message.from_user.id):
            return await message.reply_text(
                "**One Task Already Running.**"
            )

        batch_temp.IS_BATCH[message.from_user.id] = True

        datas = message.text.split("/")

        temp = datas[-1].replace(
            "?single",
            ""
        ).split("-")

        fromID = int(temp[0].strip())

        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        # LOGIN SYSTEM
        if LOGIN_SYSTEM == True:

            user_data = await db.get_session(
                message.from_user.id
            )

            if user_data is None:
                batch_temp.IS_BATCH[message.from_user.id] = False

                return await message.reply(
                    "**Please /login First.**"
                )

            api_id = int(
                await db.get_api_id(message.from_user.id)
            )

            api_hash = await db.get_api_hash(
                message.from_user.id
            )

            try:
                acc = await get_user_client(
                    message.from_user.id,
                    user_data,
                    api_id,
                    api_hash
                )

            except Exception:
                batch_temp.IS_BATCH[message.from_user.id] = False

                return await message.reply(
                    "**Session Expired. "
                    "Please /logout and /login again.**"
                )

        else:

            if TechVJUser is None:
                batch_temp.IS_BATCH[message.from_user.id] = False

                return await client.send_message(
                    message.chat.id,
                    "**String Session is not Set**"
                )

            acc = TechVJUser

        # LOOP
        for msgid in range(fromID, toID + 1):

            if not batch_temp.IS_BATCH.get(message.from_user.id):
                break

            try:

                # PRIVATE
                if "https://t.me/c/" in message.text:

                    chatid = int("-100" + datas[4])

                    await handle_private(
                        client,
                        acc,
                        message,
                        chatid,
                        msgid
                    )

                # BOT
                elif "https://t.me/b/" in message.text:

                    username = datas[4]

                    await handle_private(
                        client,
                        acc,
                        message,
                        username,
                        msgid
                    )

                # PUBLIC
                else:

                    username = datas[3]

                    try:
                        msg = await client.get_messages(
                            username,
                            msgid
                        )

                    except UsernameNotOccupied:
                        return await client.send_message(
                            message.chat.id,
                            "Username not occupied."
                        )

                    try:
                        await client.copy_message(
                            message.chat.id,
                            msg.chat.id,
                            msg.id,
                            reply_to_message_id=message.id
                        )

                    except:

                        await handle_private(
                            client,
                            acc,
                            message,
                            username,
                            msgid
                        )

            except FloodWait as fw:
                await asyncio.sleep(fw.value)

            except Exception as e:

                if ERROR_MESSAGE == True:
                    await client.send_message(
                        message.chat.id,
                        f"Error: {e}"
                    )

            await asyncio.sleep(RUNTIME_WAITING_TIME)

        batch_temp.IS_BATCH[message.from_user.id] = False


# =========================
# HANDLE PRIVATE
# =========================

async def handle_private(
    client: Client,
    acc,
    message: Message,
    chatid,
    msgid
):

    msg: Message = await acc.get_messages(
        chatid,
        msgid
    )

    if msg.empty:
        return

    msg_type = get_message_type(msg)

    if not msg_type:
        return

    if RUNTIME_CHANNEL_ID:

        try:
            chat = int(RUNTIME_CHANNEL_ID)

        except:
            chat = message.chat.id

    else:
        chat = message.chat.id

    if not batch_temp.IS_BATCH.get(message.from_user.id):
        return

    # TEXT
    if msg_type == "Text":

        try:
            await client.send_message(
                chat,
                msg.text,
                entities=msg.entities,
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:

            if ERROR_MESSAGE:
                await client.send_message(
                    message.chat.id,
                    f"Error: {e}"
                )

        return

    # DOWNLOAD STATUS MESSAGE
    smsg = await client.send_message(
        message.chat.id,
        "**Downloading Started...**"
    )

    start_time = time.time()

    # DOWNLOAD
    try:

        file = await acc.download_media(
            msg,
            progress=progress_bar,
            progress_args=(
                smsg,
                start_time,
                "📥 Downloading"
            )
        )

    except Exception as e:

        if ERROR_MESSAGE:
            await client.send_message(
                message.chat.id,
                f"Error: {e}"
            )

        return await smsg.delete()

    if not batch_temp.IS_BATCH.get(message.from_user.id):
        return

    caption = msg.caption if msg.caption else None

    upload_start = time.time()

    # DOCUMENT
    if msg_type == "Document":

        try:
            ph_path = await acc.download_media(
                msg.document.thumbs[0].file_id
            )

        except:
            ph_path = None

        try:

            await client.send_document(
                chat,
                file,
                thumb=ph_path,
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                progress=progress_bar,
                progress_args=(
                    smsg,
                    upload_start,
                    "📤 Uploading"
                )
            )

        except Exception as e:

            if ERROR_MESSAGE:
                await client.send_message(
                    message.chat.id,
                    f"Error: {e}"
                )

        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)

    # VIDEO
    elif msg_type == "Video":

        try:
            ph_path = await acc.download_media(
                msg.video.thumbs[0].file_id
            )

        except:
            ph_path = None

        try:

            await client.send_video(
                chat,
                file,
                duration=msg.video.duration,
                width=msg.video.width,
                height=msg.video.height,
                thumb=ph_path,
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                progress=progress_bar,
                progress_args=(
                    smsg,
                    upload_start,
                    "📤 Uploading"
                )
            )

        except Exception as e:

            if ERROR_MESSAGE:
                await client.send_message(
                    message.chat.id,
                    f"Error: {e}"
                )

        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)

    # PHOTO
    elif msg_type == "Photo":

        try:

            await client.send_photo(
                chat,
                file,
                caption=caption,
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:

            if ERROR_MESSAGE:
                await client.send_message(
                    message.chat.id,
                    f"Error: {e}"
                )

    # AUDIO
    elif msg_type == "Audio":

        try:
            ph_path = await acc.download_media(
                msg.audio.thumbs[0].file_id
            )

        except:
            ph_path = None

        try:

            await client.send_audio(
                chat,
                file,
                thumb=ph_path,
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                progress=progress_bar,
                progress_args=(
                    smsg,
                    upload_start,
                    "📤 Uploading"
                )
            )

        except Exception as e:

            if ERROR_MESSAGE:
                await client.send_message(
                    message.chat.id,
                    f"Error: {e}"
                )

        if ph_path and os.path.exists(ph_path):
            os.remove(ph_path)

    # VOICE
    elif msg_type == "Voice":

        try:

            await client.send_voice(
                chat,
                file,
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                progress=progress_bar,
                progress_args=(
                    smsg,
                    upload_start,
                    "📤 Uploading"
                )
            )

        except Exception as e:

            if ERROR_MESSAGE:
                await client.send_message(
                    message.chat.id,
                    f"Error: {e}"
                )

    # STICKER
    elif msg_type == "Sticker":

        try:
            await client.send_sticker(chat, file)

        except Exception as e:

            if ERROR_MESSAGE:
                await client.send_message(
                    message.chat.id,
                    f"Error: {e}"
                )

    # ANIMATION
    elif msg_type == "Animation":

        try:
            await client.send_animation(chat, file)

        except Exception as e:

            if ERROR_MESSAGE:
                await client.send_message(
                    message.chat.id,
                    f"Error: {e}"
                )

    # CLEANUP
    try:

        if os.path.exists(file):
            os.remove(file)

    except:
        pass

    try:
        await smsg.delete()

    except:
        pass


# =========================
# MESSAGE TYPE
# =========================

def get_message_type(
    msg: pyrogram.types.messages_and_media.message.Message
):

    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass


# Don't Remove Credit @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01
