import telebot
from telebot import types
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

# أسعار
rates = {
    "USD": {"buy": 11870, "sell": 11950},
    "EUR": {"buy": 13630, "sell": 13830}
}

user_data = {}

# ---------------- START ----------------
@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    markup = main_menu()
    bot.send_message(message.chat.id, f"👋 أهلاً {name}\n\nاختر من القائمة:", reply_markup=markup)

# ---------------- MAIN MENU ----------------
def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("💱 سعر الصرف", callback_data="rates"),
        types.InlineKeyboardButton("🧮 الحاسبة", callback_data="calc")
    )
    markup.add(
        types.InlineKeyboardButton("💸 تحويل شام كاش", callback_data="sham"),
        types.InlineKeyboardButton("📱 تحويل سيريتل كاش", callback_data="syriatel")
    )
    markup.add(
        types.InlineKeyboardButton("📞 تواصل", callback_data="contact")
    )
    return markup

# ---------------- CALLBACKS ----------------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):

    if call.data == "rates":
        text = f"""
💱 أسعار الصرف:

🇺🇸 USD:
شراء: {rates['USD']['buy']}
بيع: {rates['USD']['sell']}

🇪🇺 EUR:
شراء: {rates['EUR']['buy']}
بيع: {rates['EUR']['sell']}
"""
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_home())

    elif call.data == "calc":
        markup = types.InlineKeyboardMarkup()
        for cur in ["USD", "EUR", "SYP"]:
            markup.add(types.InlineKeyboardButton(cur, callback_data=f"from_{cur}"))
        markup.add(back_button())
        bot.edit_message_text("اختر العملة الأولى:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("from_"):
        user_data[call.from_user.id] = {"from": call.data.split("_")[1]}
        markup = types.InlineKeyboardMarkup()
        for cur in ["USD", "EUR", "SYP"]:
            markup.add(types.InlineKeyboardButton(cur, callback_data=f"to_{cur}"))
        markup.add(back_button())
        bot.edit_message_text("اختر العملة الثانية:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("to_"):
        user_data[call.from_user.id]["to"] = call.data.split("_")[1]
        bot.send_message(call.message.chat.id, "💰 أدخل المبلغ:")

    elif call.data == "sham":
        bot.edit_message_text("💸 تحويل شام كاش قيد التطوير", call.message.chat.id, call.message.message_id, reply_markup=back_home())

    elif call.data == "syriatel":
        bot.edit_message_text("📱 تحويل سيريتل كاش قيد التطوير", call.message.chat.id, call.message.message_id, reply_markup=back_home())

    elif call.data == "contact":
        bot.edit_message_text("📞 تواصل معنا: @Owner_MEN1", call.message.chat.id, call.message.message_id, reply_markup=back_home())

    elif call.data == "back":
        bot.edit_message_text("رجعنا خطوة 👇", call.message.chat.id, call.message.message_id, reply_markup=main_menu())

    elif call.data == "home":
        bot.edit_message_text("🏠 الرئيسية", call.message.chat.id, call.message.message_id, reply_markup=main_menu())

# ---------------- CALCULATION ----------------
@bot.message_handler(func=lambda message: message.text.isdigit())
def calculate(message):
    user_id = message.from_user.id

    if user_id not in user_data:
        return

    amount = float(message.text)
    data = user_data[user_id]

    from_cur = data["from"]
    to_cur = data["to"]

    if from_cur == to_cur:
        result = amount
    elif from_cur == "USD" and to_cur == "SYP":
        result = amount * rates["USD"]["sell"]
    elif from_cur == "SYP" and to_cur == "USD":
        result = amount / rates["USD"]["buy"]
    elif from_cur == "EUR" and to_cur == "SYP":
        result = amount * rates["EUR"]["sell"]
    elif from_cur == "SYP" and to_cur == "EUR":
        result = amount / rates["EUR"]["buy"]
    else:
        result = amount  # تبسيط

    bot.send_message(message.chat.id, f"✅ النتيجة: {round(result, 2)}")

# ---------------- BUTTONS ----------------
def back_button():
    return types.InlineKeyboardButton("🔙 رجوع", callback_data="back")

def back_home():
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🔙 رجوع", callback_data="back"),
        types.InlineKeyboardButton("🏠 الرئيسية", callback_data="home")
    )
    return markup

# ---------------- RUN ----------------
print("Bot running...")
bot.infinity_polling()
