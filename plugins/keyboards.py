from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
import emoji


contact_number = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Send the phone number📱', request_contact=True)
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

location = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Location', request_location=True)
        ],
        [
            KeyboardButton('Back')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


def fason():
    return ReplyKeyboardMarkup(
        keyboard=[
            ['Menu'],
            ['Basket'],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


FOOD = []
with open("menu.txt", "r") as db:
    for line in db:
        m = {}
        [meal, cost, link] = line.split(' : ')
        m["name"] = meal
        m["cost"] = int(cost)
        m["link"] = link
        FOOD.append(m)
menu = []

for item in FOOD:
    menu.append(InlineKeyboardButton(emoji.emojize(item['name']), callback_data=f'details|{item["name"]}'))

x = menu[::2]
y = menu[1::2]


def prod():
    return InlineKeyboardMarkup(
        [
            y,
            x,
            [InlineKeyboardButton(emoji.emojize('Back:BACK_arrow:'), callback_data='Back')]
        ]
    )


def is_burg(name):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(emoji.emojize('Back:BACK_arrow:'), callback_data='Back'),
                InlineKeyboardButton(emoji.emojize("Add to Basket:shopping_cart:"), callback_data=f'add_basket|{name}')
            ]
        ]
    )


def order():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Order", callback_data='order'),
                InlineKeyboardButton("Clear", callback_data='clear'),
            ],
            [
                InlineKeyboardButton(emoji.emojize('Back:BACK_arrow:'), callback_data='Back'),
            ]
        ]
    )


def empty():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(emoji.emojize('Back:BACK_arrow:'), callback_data='Back')
            ]
        ]
    )


handling = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("Accept", callback_data='accept'),
            InlineKeyboardButton("Reject", callback_data='reject')
        ]
    ]
)

reservation = ReplyKeyboardMarkup(
    keyboard=[
        ['reservations']
    ],
    resize_keyboard=True,
)
