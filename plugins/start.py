# (©)Codexbotz
# Recode by @mrismanaziz

import asyncio
from datetime import datetime
from time import time

from bot import Bot
from config import (
    ADMINS,
    CUSTOM_CAPTION,
    DISABLE_CHANNEL_BUTTON,
    FORCE_MSG,
    PROTECT_CONTENT,
    START_MSG,
)

from database.sql import add_user, delete_user, full_userbase, query_msg

from pyrogram import filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked
from pyrogram.types import InlineKeyboardMarkup, Message

from helper_func import decode, get_messages, subsall, subsch, subsgc
from .button import fsub_button, start_button

START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()

TIME_DURATION_UNITS = (
    ("week", 60 * 60 * 24 * 7),
    ("day", 60**2 * 24),
    ("hour", 60**2),
    ("min", 60),
    ("sec", 1),
)


async def _human_time_duration(seconds):
    if seconds == 0:
        return "inf"

    parts = []

    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)

        if amount > 0:
            parts.append(f'{amount} {unit}{"" if amount == 1 else "s"}')

    return ", ".join(parts)


@Bot.on_message(filters.command("start") & filters.private & subsall & subsch & subsgc)
async def start_command(client: Bot, message: Message):

    try:
        await message.delete()
    except:
        pass

    id = message.from_user.id

    user_name = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else None
    )

    try:
        await add_user(id, user_name)
    except:
        pass

    text = message.text

    if len(text) > 7:

        try:
            base64_string = text.split(" ", 1)[1]
        except BaseException:
            return

        string = await decode(base64_string)

        argument = string.split("-")

        if len(argument) == 3:

            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except BaseException:
                return

            if start <= end:
                ids = range(start, end + 1)

            else:
                ids = []
                i = start

                while True:
                    ids.append(i)
                    i -= 1

                    if i < end:
                        break

        elif len(argument) == 2:

            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except BaseException:
                return

        temp_msg = await message.reply("<code>Tunggu Sebentar...</code>")

        try:
            messages = await get_messages(client, ids)

        except BaseException:
            await message.reply_text("<b>Telah Terjadi Error </b>🥺")
            return

        await temp_msg.delete()

        for msg in messages:

            if bool(CUSTOM_CAPTION) & bool(msg.document):

                caption = CUSTOM_CAPTION.format(
                    previouscaption=msg.caption.html if msg.caption else "",
                    filename=msg.document.file_name,
                )

            else:
                caption = msg.caption.html if msg.caption else ""

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    protect_content=PROTECT_CONTENT,
                    reply_markup=reply_markup,
                )

                await asyncio.sleep(0.5)

            except FloodWait as e:

                await asyncio.sleep(e.x)

                await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    protect_content=PROTECT_CONTENT,
                    reply_markup=reply_markup,
                )

            except BaseException:
                pass

    else:

        out = await start_button(client)

        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=f"@{message.from_user.username}"
                if message.from_user.username
                else None,
                mention=message.from_user.mention,
                id=message.from_user.id,
            ),
            reply_markup=InlineKeyboardMarkup(out),
            disable_web_page_preview=True,
            quote=True,
        )

    return


@Bot.on_message(filters.command("start") & filters.private)
async def not_joined(client: Bot, message: Message):

    buttons = await fsub_button(client, message)

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=f"@{message.from_user.username}"
            if message.from_user.username
            else None,
            mention=message.from_user.mention,
            id=message.from_user.id,
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True,
    )
