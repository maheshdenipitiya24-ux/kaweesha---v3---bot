import telebot
import json
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = "8611297717:AAHUIU0VMi8gzxQ4NunTR-N1Te4lTVDYzZs"
bot = telebot.TeleBot(TOKEN)
scheduler = BackgroundScheduler(timezone="Asia/Colombo") # Sri Lanka Time
scheduler.start()

DATA_FILE = "bot_data.json"

# ========== සම්පූර්ණ සතියේ TIME TABLE එක ==========
TIMETABLE = {
    # සඳුදා, බදාදා, බ්‍රහස්පතින්දා, සිකුරාදා - Deep Work Days
    "mon": {
        "04:30": "Wake Up - වතුර 500ml + Stretch",
        "05:00": "Deep Work 1 - Biology: අමාරුම Unit එක, Past Paper 1.5h + Theory 1h",
        "07:30": "කෑම + Power Nap - 20min",
        "08:30": "Deep Work 2 - Chemistry: Physical/Organic, MCQ 30ක් Target",
        "11:00": "නිදාගන්න / School වැඩ",
        "14:00": "Deep Work 3 - Physics: Theory 1 Unit + MCQ 20ක් + Formula List",
        "16:30": "Deep Work 4 - Biology: Diagram Practice + Short Notes",
        "18:00": "Exercise + කනවා",
        "19:30": "Active Recall - 3ම Subject: අද කරපු ටික කටින් කියනවා/ලියනවා",
        "21:30": "Cool Down - හෙට Plan එක"
    },
    "wed": "mon", # බදාදා = සඳුදා වගේම
    "thu": "mon", # බ්‍රහස්පතින්දා = සඳුදා වගේම
    "fri": "mon", # සිකුරාදා = සඳුදා වගේම
    
    # අඟහරුවාදා - Speed Class Day
    "tue": {
        "04:30": "Deep Work 1 - Chemistry: Organic අමාරුම කොටස",
        "07:30": "කෑම + Rest",
        "08:30": "Deep Work 2 - Biology: Theory 2h + Past Paper 1h",
        "11:30": "නිදාගන්න / කෑම / Pre-Study - Speed Class එකට කලින් සූදානම් වෙනවා",
        "17:00": "SPEED CLASS - 3h Tuition",
        "20:00": "Deep Work 3 - Physics + Speed Class Revision",
        "22:00": "නිදාගන්නවා"
    },
    
    # සෙනසුරාදා - Chemistry Class Day
    "sat": {
        "04:30": "Deep Work 1 - Biology Full Paper: වෙලාවට තියලා Paper 1ක්",
        "07:30": "කෑම + ලැස්ති වෙනවා",
        "08:00": "CHEMISTRY CLASS - 5h Tuition",
        "13:00": "කෑම + නිදාගන්නවා",
        "17:00": "Family Time - පොතක් අතින් අල්ලන්න එපා",
        "22:00": "නිදාගන්නවා"
    },
    
    # ඉරිදා - Bio + Physics Class Day
    "sun": {
        "04:30": "Deep Work 1 - Chemistry: සෙනසුරාදා Class එකේ 100% Revision + MCQ 40ක්",
        "07:30": "කෑම + ලැස්ති වෙනවා",
        "08:00": "BIOLOGY CLASS - 4h Tuition",
        "12:00": "කෑම + Rest",
        "13:00": "PHYSICS CLASS - 5h Tuition",
        "18:00": "කෑම + නානවා",
        "19:00": "Weekly Master Revision - සතියේම වැරදුනු MCQ/Structured ටික ආයෙ හදනවා",
        "21:00": "ඊලඟ සතිය Plan කරනවා",
        "22:00": "නිදාගන්නවා"
    }
}
# ================================================================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"homework": [], "chat_ids": []}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

data = load_data()

def setup_tt_reminders():
    for day, schedule in TIMETABLE.items():
        if isinstance(schedule, str): continue # mon, wed, thu, fri duplicate skip
        for time_str, task in schedule.items():
            hour, minute = map(int, time_str.split(':'))
            scheduler.add_job(
                send_tt_reminder,
                'cron',
                day_of_week=day,
                hour=hour,
                minute=minute,
                args=[task]
            )

def send_tt_reminder(task):
    for chat_id in data["chat_ids"]:
        try:
            bot.send_message(chat_id, f"🔔 **Kaweesha v3.0 Alert** 🔔\n\n{task}\n\nදැන් පටන් ගනින්. වෙලාව රත්තරන්!")
        except: pass

setup_tt_reminders()

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in data["chat_ids"]:
        data["chat_ids"].append(chat_id)
        save_data(data)
    bot.reply_to(message, "හෙලෝ Adam! මං උඹේ Kaweesha v3.0 Study Bot 🤖\n\n**Time Table**\n`tt today` - අද දවසේ Plan එක\n`tt now` - දැන් කරන්න තියෙන වැඩේ\n\n**Homework**\n`hw add Maths: Ex 5.2`\n`hw list`\n`hw done 1`")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    global data
    text = message.text
    chat_id = message.chat.id
    if chat_id not in data["chat_ids"]:
        data["chat_ids"].append(chat_id)
        save_data(data)

    day_map = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}
    today_key = day_map[datetime.now().weekday()]
    schedule_today = TIMETABLE[today_key]
    if isinstance(schedule_today, str): # mon,wed,thu,fri case
        schedule_today = TIMETABLE[schedule_today]

    # HW Add
    if text.startswith("hw add "):
        task = text[7:]
        data["homework"].append({"task": task, "chat_id": chat_id, "added": datetime.now().strftime("%m-%d")})
        save_data(data)
        bot.reply_to(message, f"📚 HW එක දැම්මා: {task}")

    # HW List
    elif text == "hw list":
        my_hw = [h for h in data["homework"] if h["chat_id"] == chat_id]
        if not my_hw:
            bot.reply_to(message, "HW නෑ මචන්. ෆුල් ෆ්‍රී 💃")
        else:
            reply = "📚 **උඹේ Homework List:**\n"
            for i, h in enumerate(my_hw, 1):
                reply += f"{i}. {h['task']} - `{h['added']}`\n"
            bot.reply_to(message, reply, parse_mode='Markdown')

    # HW Done
    elif text.startswith("hw done "):
        try:
            index = int(text[8:]) - 1
            my_hw = [h for h in data["homework"] if h["chat_id"] == chat_id]
            if 0 <= index < len(my_hw):
                done_task = my_hw[index]
                data["homework"].remove(done_task)
                save_data(data)
                bot.reply_to(message, f"✅ ශා ඉවරයි: {done_task['task']}")
            else:
                bot.reply_to(message, "ඒ Number එකේ HW එකක් නෑ")
        except:
            bot.reply_to(message, "`hw done 1` වගේ Number එක දාපන්")

    # Time Table Today
    elif text == "tt today":
        day_name = ["සඳුදා", "අඟහරුවාදා", "බදාදා", "බ්‍රහස්පතින්දා", "සිකුරාදා", "සෙනසුරාදා", "ඉරිදා"][datetime.now().weekday()]
        reply = f"🗓️ **අද {day_name} - Kaweesha v3.0 Plan:**\n"
        for time_str, task in sorted(schedule_today.items()):
            reply += f"`{time_str}` - {task}\n"
        bot.reply_to(message, reply, parse_mode='Markdown')

    # Time Table Now
    elif text == "tt now":
        now = datetime.now().strftime("%H:%M")
        current_task = "Free Time / ඊලඟ Task එකට ලෑස්ති වෙයන්"
        for time_str, task in sorted(schedule_today.items(), reverse=True):
            if now >= time_str:
                current_task = task
                break
        bot.reply_to(message, f"⏰ **දැන් කරන්න ඕන:**\n{current_task}")

    else:
        bot.reply_to(message, "Command එක තේරුනේ නෑ. `/start` ගහලා බලපන්")

print("Kaweesha v3.0 Bot Started...")
bot.infinity_polling()
