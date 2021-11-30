from pyrogram import Client, filters, ContinuePropagation
from config import admin_id, pay_token
import plugins.keyboards as kb
from typing import Dict, List
from pyrogram.types import Update, User, Chat, Message
from pyrogram.raw.functions.messages import SendMedia, SetBotPrecheckoutResults
from pyrogram.raw.types import (
    DataJSON,
    InputMediaInvoice,
    Invoice,
    LabeledPrice,
    UpdateBotPrecheckoutQuery,
)

basket = {}
contacts = {}
STEPS = {}
uzerzs = []
loca = {}

_on_checkout_query_handlers: List[callable] = []


def on_checkout_query(func: callable):
    _on_checkout_query_handlers.append(func)
    return func


@Client.on_raw_update()
async def _raw(bot: Client, update: Update, users: Dict[int, User], chats: Dict[int, Chat]):
    if isinstance(update, UpdateBotPrecheckoutQuery):
        for handler in _on_checkout_query_handlers:
            await handler(bot, update, users, chats)
    else:
        raise ContinuePropagation()


@Client.on_message(filters.command("start"))
async def my_handler(_, message):
    uzerzs.append(message.from_user.id)
    await message.reply_text(f"Hey, <b>{message.from_user.first_name}</b>!👋 \n\nSend your phone number to register",
                             reply_markup=kb.contact_number)


@Client.on_message(filters.contact)
async def start_order(_, message):
    STEPS[message.from_user.id] = 1
    try:
        contacts[message.from_user.id] = message.contact.phone_number
        await message.reply_text("You are in main menu🤠",
                                 reply_markup=kb.fason())
    except AttributeError:
        await message.reply_text("You are in main menu🤠",
                                 reply_markup=kb.fason())


@Client.on_message(filters.regex("Menu"))
async def start_menu(_, message):
    STEPS[message.from_user.id] = 2
    await message.reply_text('What will we start with?🔍',
                             reply_markup=kb.prod())


@Client.on_message(filters.regex('Basket'))
async def res(_, message):
    STEPS[message.from_user.id] = 2
    try:
        text = "Basket contains:\n\n"
        total_cost = 0
        for meal in basket[message.from_user.id]:
            text += f"{meal['name'][:meal['name'].find(':')]}\n"
            total_cost += meal['cost']
        text += f"\nTotal cost: {total_cost} sum"
        await message.reply_text(text, reply_markup=kb.order())
    except KeyError:
        await message.reply_text('The basket is empty', reply_markup=kb.empty())


@Client.on_callback_query(filters.regex('details'))
async def choice(_, callback_query):
    STEPS[callback_query.from_user.id] = 3
    meal_name = callback_query.data.split('|')[1]
    for item in kb.FOOD:
        if item['name'] == meal_name:
            await Client.send_photo(_, chat_id=callback_query.from_user.id, photo=item['link'],
                                    caption=f"Cost: <b>{item['cost']} sum</b> ",
                                    reply_markup=kb.is_burg(item['name']))
            return await callback_query.message.delete()


@Client.on_callback_query(filters.regex('add_basket'))
async def deter(_, callback_query):
    meal_name = callback_query.data.split('|')[1]
    for item in kb.FOOD:
        if item['name'] == meal_name:
            if callback_query.from_user.id in basket:
                basket[callback_query.from_user.id] += [item]
            else:
                basket[callback_query.from_user.id] = [item]
            return await callback_query.answer('The meal has been added to the basket', show_alert=True)


@Client.on_callback_query(filters.regex('order'))
async def loc(_, callback_query):
    STEPS[callback_query.from_user.id] = 5
    await callback_query.message.edit('Please, send your location', reply_markup=kb.location)


@Client.on_callback_query(filters.regex('clear'))
async def clea(_, callback_query):
    STEPS[callback_query.from_user.id] = 2
    del basket[callback_query.from_user.id]
    await callback_query.message.edit('Basket is empty now',
                                      reply_markup=kb.empty())


@Client.on_message(filters.location)
async def ordr(bot: Client, msg: Message):
    ccost = []
    STEPS[msg.from_user.id] = 2
    loca[msg.from_user.id] = [msg.location.longitude, msg.location.latitude]
    text = ''
    peer = await bot.resolve_peer(msg.chat.id)
    for meal in basket[msg.from_user.id]:
        text += f"{meal['name'][:meal['name'].find(':')]}\n"
        ccost.append(LabeledPrice(label=meal['name'][:meal['name'].find(':')],
                                  amount=meal['cost'] * 100))
    await bot.send(
        SendMedia(
            peer=peer,
            media=InputMediaInvoice(
                title="Payment",
                description=text,
                invoice=Invoice(
                    currency="UZS",
                    prices=ccost,
                    test=True,
                    flexible=True
                ),
                payload=b"payment",
                provider=pay_token,
                provider_data=DataJSON(data=r"{}"),
                start_param="pay",
            ),
            message="",
            random_id=bot.rnd_id(),
        )
    )


@on_checkout_query
async def process_checkout_query(
        bot: Client,
        query: UpdateBotPrecheckoutQuery,
        users: Dict[int, User],
        chats: Dict[int, Chat],
):
    STEPS[query.user_id] = 2
    text = ""
    for item in basket[query.user_id]:
        text += f"{item['name'][:item['name'].find(':')]}, "
    await bot.send_location(chat_id=admin_id, longitude=loca[query.user_id][0],
                            latitude=loca[query.user_id][1])
    await bot.send_message(chat_id=admin_id,
                           text=f'Client: {contacts[query.user_id]}\nID:{query.user_id}\nMeal: {text}',
                           reply_markup=kb.handling)
    del basket[query.user_id]
    await bot.send_message(
        chat_id=query.user_id,
        text="Your order sent to administrators, please wait few seconds", reply_markup=kb.empty()
    )
    await bot.send(
        SetBotPrecheckoutResults(
            query_id=query.query_id,
            success=True,
            error=None,
        )
    )


levels = {
    1: start_order,
    2: start_menu,
    3: choice,
    4: res,
    5: loc,
    6: clea
}


@Client.on_callback_query(filters.regex('Back'))
async def navigate(_, callback_query):
    current_level = levels[STEPS[callback_query.from_user.id] - 1]
    callback_query.message.from_user.id = callback_query.from_user.id
    await current_level(_, callback_query.message)
    await callback_query.message.delete()


@Client.on_message(filters.regex('Back'))
async def navi_loc(_, message):
    current_level = levels[STEPS[message.from_user.id] - 1]
    await current_level(_, message)
