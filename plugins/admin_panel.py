from config import admin_id
from pyrogram import Client, filters
import plugins.keyboards as kb
import plugins.commands as cm

reservations = []


@Client.on_message(filters.user(admin_id) & filters.regex('admin'))
async def adm_menu(_, message):
    await message.reply('hey', reply_markup=kb.reservation)


@Client.on_callback_query(filters.user(admin_id) & filters.regex("accept"))
async def acc(_, callback_query):
    reservations.append(callback_query.message.text)
    await callback_query.message.edit(text=f'{callback_query.message.text}\n\naccepted', reply_markup=None)
    await callback_query.answer('Stored to reservations')
    for item in cm.uzerzs:
        if str(item) in callback_query.message.text:
            return await Client.send_message(_, chat_id=item, text='Meal is cooking!')


@Client.on_callback_query(filters.user(admin_id) & filters.regex("reject"))
async def rej(_, callback_query):
    await callback_query.message.edit(text=f'{callback_query.message.text}\n\nrejected', reply_markup=None)
    for item in cm.uzerzs:
        if str(item) in callback_query.message.text:
            return await Client.send_message(_, chat_id=item, text='Order rejected!')


@Client.on_message(filters.user(admin_id) & filters.regex("reservations"))
async def list_res(_, message):
    if len(reservations) > 10:
        del reservations[0]
    for food in reservations:
        await message.reply(food)