import telebot
import pandas as pd
from telebot import types
from datetime import datetime, timedelta
BOT_TOKEN = "809......"

bot = telebot.TeleBot(BOT_TOKEN)

def get_classes_for_sport(schedule_df, sport, day):

    # Get the current date and calculate the target date
    today = datetime.now()
    if day.lower() == "ma":
        target_date = today
    elif day.lower() == "holnap":
        target_date = today + timedelta(days=1)
    elif day.lower() == "holnap után":
        target_date = today + timedelta(days=2)

    target_date_str = target_date.date().strftime('%Y-%m-%d')

    # Filter the schedule for the place and target date
    result = schedule_df[
        (schedule_df["sport"].str.contains(sport.lower(), case=False) ) &
        (schedule_df["date"] == target_date_str)
    ]

    if result.empty:
        return f"Sajnos nincs óra a *{sport} *  *{day}* ({target_date_str})."

    grouped = result.groupby("klub")
    response_lines = []

    for club, classes in grouped:
        # Add the club name
        response_lines.append(f"*{club}*")
        # Add the classes under the club
        for _, row in classes.iterrows():
            response_lines.append(f"    *{row['time']}* {row['sport']} {row['edző']}")

    # Join the response into a single string
    response = "\n".join(response_lines)
    return f"Órák a *{sport}* *{day}* ({target_date.strftime('%Y-%m-%d')}):\n{response}"


def get_classes_for_day(schedule_df, place, day):

    # Get the current date and calculate the target date
    today = datetime.now()
    if day.lower() == "ma":
        target_date = today
    elif day.lower() == "holnap":
        target_date = today + timedelta(days=1)
    elif day.lower() == "holnap után":
        target_date = today + timedelta(days=2)

    target_date_str = target_date.date().strftime('%Y-%m-%d')

    # Filter the schedule for the place and target date
    result = schedule_df[
        (schedule_df["klub"].str.lower() == place.lower()) &
        (schedule_df["date"] == target_date_str)
    ]

    if result.empty:
        return f"Sajnos nincs óra a *{place}* teremben *{day}* ({target_date_str})."

    # Format the results
    response = "\n".join(
        f"*{row['time']}* *{row['sport']}* {row['edző']}"
        for _, row in result.iterrows()
    )
    return f"Órák a *{place}* teremben *{day}* ({target_date.strftime('%Y-%m-%d')}):\n{response}"

# ----------------------------------------------------------------------------------------------------------------
@bot.message_handler(commands=['hely'])
def sign_handler(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('allee', 'nyugati', 'corvin', 'springday', 'etele', 'vaci35')
    sent_msg = bot.send_message(message.chat.id, "Hol edzenél?:", reply_markup=markup)
    bot.register_next_step_handler(sent_msg, ask_last_name)


def ask_last_name(message):
    place_to_gym = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('ma', 'holnap', 'holnap után')
    sent_msg = bot.send_message(message.chat.id, "Mikor edzenél?:", reply_markup=markup)
    bot.register_next_step_handler(sent_msg, hely_date_response, place_to_gym)


def hely_date_response(message, place_to_gym):
    time_to_gym = message.text
    # refresh data
    schedule_df = pd.read_csv('https://raw.githubusercontent.com/misrori/life1/refs/heads/main/orarend.csv')
    markdown_response = get_classes_for_day(schedule_df, place_to_gym, time_to_gym)
    bot.send_message(message.chat.id, markdown_response, parse_mode="Markdown")

# ----------------------------------------------------------------------------------------------------------------


@bot.message_handler(commands=['sport'])
def sport_handler(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Gerinctorna',  'Pilates',  'Kondi', 'Stretching', 'Jóga', 'Szauna', 'Spinning', 'Egyébb')
    sent_msg = bot.send_message(message.chat.id, "Milyen sportot szeretnél?:", reply_markup=markup)
    bot.register_next_step_handler(sent_msg, time_handle)


def time_handle(message):
    selected_sport = message.text

    if selected_sport=='Egyébb':
        text = "Írd meg mit edzenél!"
        sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
        bot.register_next_step_handler(sent_msg, time_handle)
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('ma', 'holnap', 'holnap után')
        sent_msg = bot.send_message(message.chat.id, "Mikor edzenél?:", reply_markup=markup)
        bot.register_next_step_handler(sent_msg, sport_date_response, selected_sport)



def sport_date_response(message, sport_to_gym):
    time_to_gym = message.text
    # refresh data
    schedule_df = pd.read_csv('https://raw.githubusercontent.com/misrori/life1/refs/heads/main/orarend.csv')
    markdown_response = get_classes_for_sport(schedule_df, sport_to_gym, time_to_gym)
    bot.send_message(message.chat.id, markdown_response, parse_mode="Markdown")



bot.infinity_polling()
