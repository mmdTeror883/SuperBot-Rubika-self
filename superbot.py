#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SUPER BOT - ربات پیشرفته روبیکا
نسخه 5.0 - کامل ترین ربات روبیکا
مناسب برای نشر در GitHub
"""

import subprocess
import sys
import os
import time
import random
import json
import threading
import re
from datetime import datetime

# ==================== نصب خودکار کتابخانه‌ها ====================
def install_package(package):
    try:
        __import__(package.replace('-', '_'))
        print(f"✅ {package} قبلاً نصب شده")
        return True
    except ImportError:
        print(f"📦 در حال نصب {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--break-system-packages"])
            print(f"✅ {package} نصب شد!")
            return True
        except:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user"])
                print(f"✅ {package} نصب شد!")
                return True
            except:
                print(f"❌ خطا در نصب {package}")
                return False

# کتابخانه‌های مورد نیاز
required_packages = ["pyrubi", "requests"]
for pkg in required_packages:
    install_package(pkg)

# ==================== ایمپورت کتابخانه‌ها ====================
from pyrubi import Client
from pyrubi.types import Message

# ==================== کلاس اصلی ربات ====================
class SuperBot:
    def __init__(self):
        self.client = Client(session="SuperBot")
        self.start_time = time.time()
        
        # دیتابیس‌ها
        self.replies = []
        self.active_chats = {}
        self.interval = 2
        self.last_time = {}
        self.scores = {}
        self.money = {}
        self.warns = {}
        self.daily = {}
        
        # بارگذاری دیتابیس
        self.load_data()
        
        # پاسخ‌های پیش‌فرض
        if not self.replies:
            self.replies = [
                "سلام 👋", "خوبی؟ 😊", "خسته نباشی 💪", "ایول 🔥",
                "دمت گرم 🎉", "مرسی ❤️", "باشه ✅", "😂😂", "👍👍", "👌👌"
            ]
        
        print("✅ SUPER BOT راه‌اندازی شد!")
        print(f"📊 {len(self.replies)} پاسخ آماده است")
    
    def load_data(self):
        try:
            if os.path.exists("superbot_data.json"):
                with open("superbot_data.json", "r") as f:
                    data = json.load(f)
                    self.replies = data.get("replies", [])
                    self.scores = data.get("scores", {})
                    self.money = data.get("money", {})
                    self.warns = data.get("warns", {})
        except:
            pass
    
    def save_data(self):
        data = {
            "replies": self.replies,
            "scores": self.scores,
            "money": self.money,
            "warns": self.warns
        }
        with open("superbot_data.json", "w") as f:
            json.dump(data, f, indent=2)
    
    def send(self, chat_id, text):
        try:
            return self.client.send_text(chat_id, text)
        except:
            return None
    
    def get_panel(self):
        return f"""
╔══════════════════════════════════════════════════════════╗
║                   🤖 SUPER BOT 🤖                         ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  🎯 **دستورات اصلی**                                     ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ║
║  `.set`        - شروع/توقف ارسال خودکار                 ║
║  `.add متن`    - اضافه کردن پاسخ جدید                   ║
║  `.list`       - لیست پاسخ‌ها                           ║
║  `.remove 2`   - حذف پاسخ                              ║
║  `.clear`      - پاک کردن همه پاسخ‌ها                   ║
║  `.interval 3` - تغییر سرعت ارسال (1-10)               ║
║                                                          ║
║  💕 **عشق و احساسات**                                    ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ║
║  `.love`       - انیمیشن عشق (۳۰ مرحله)                 ║
║  `.heart نام`  - فرستادن قلب به کسی                    ║
║                                                          ║
║  🎮 **بازی‌ها**                                          ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ║
║  `.dice`       - تاس انداختن (+امتیاز)                 ║
║  `.coin`       - شیر یا خط (+امتیاز)                   ║
║  `.slot`       - ماشین اسلات (جکپات 100)               ║
║  `.guess 5`    - حدس عدد (1-10)                        ║
║  `.rps سنگ`    - سنگ کاغذ قیچی                         ║
║                                                          ║
║  💰 **اقتصاد**                                           ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ║
║  `.work`       - کار کردن (+💰)                        ║
║  `.daily`      - جایزه روزانه                          ║
║  `.money`      - موجودی من                             ║
║  `.transfer @user 50` - انتقال پول                    ║
║  `.rob @user`  - دزدی (⚠️ ریسک)                        ║
║                                                          ║
║  🏆 **امتیاز**                                           ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ║
║  `.score`      - امتیاز من                             ║
║  `.top`        - برترین‌ها                              ║
║  `.level`      - سطح من                                ║
║                                                          ║
║  🔧 **ابزارها**                                          ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ║
║  `.time`       - زمان و تاریخ                          ║
║  `.id`         - آیدی چت                               ║
║  `.ping`       - سرعت ربات                             ║
║  `.status`     - وضعیت ربات                            ║
║  `.info`       - اطلاعات ربات                          ║
║  `.calc 2+2`   - ماشین حساب                            ║
║  `.reverse متن` - برعکس کردن متن                       ║
║                                                          ║
║  ⚠️ **مدیریت**                                           ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   ║
║  `.warn @user`    - اخطار به کاربر                     ║
║  `.warns`         - اخطارهای من                        ║
║  `.tag @user اسم` - دادن تگ                            ║
║  `.mytags`        - تگ‌های من                          ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    
    # ==================== انیمیشن عشق ====================
    def love_animation(self, chat_id):
        try:
            # ارسال پیام اول
            result = self.client.send_text(chat_id, "💘")
            msg_id = result['message_update']['message_id']
            
            # مراحل با فاصله مناسب
            for i in range(2, 31):
                time.sleep(0.3)
                self.client.send_text(chat_id, "💘" * i, message_id=msg_id)
            
            # پیام نهایی
            self.client.send_text(chat_id, "💘" * 30 + "\n❤️ 100% عشق ❤️", message_id=msg_id)
            
        except Exception as e:
            print(f"Love error: {e}")
    
    # ==================== هندلر اصلی ====================
    def run(self):
        @self.client.on_message()
        def handler(msg: Message):
            if not msg.text:
                return
            
            text = msg.text.strip()
            chat_id = str(msg.object_guid)
            user = str(msg.author_guid) if hasattr(msg, "author_guid") else chat_id
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {text[:40]}")
            
            # ===== منو =====
            if text in [".start", ".menu", ".panel"]:
                self.send(chat_id, self.get_panel())
                return
            
            # ===== LOVE =====
            if text == ".love":
                threading.Thread(target=self.love_animation, args=(chat_id,), daemon=True).start()
                return
            
            if text.startswith(".heart "):
                name = text[7:].strip()
                self.send(chat_id, f"❤️❤️❤️❤️❤️\n💕 {name} 💕\n❤️❤️❤️❤️❤️")
                return
            
            # ===== SET =====
            if text == ".set":
                if chat_id in self.active_chats and self.active_chats[chat_id]:
                    self.active_chats[chat_id] = False
                    self.send(chat_id, "❌ **ارسال خودکار متوقف شد**")
                else:
                    if not self.replies:
                        self.send(chat_id, "❗ **پاسخی وجود ندارد!**\n先用 `.add متن` اضافه کن")
                        return
                    self.active_chats[chat_id] = True
                    self.last_time[chat_id] = 0
                    self.send(chat_id, f"✅ **ارسال خودکار فعال شد**\n⏱️ هر {self.interval} ثانیه")
                    time.sleep(0.5)
                    self.send(chat_id, random.choice(self.replies))
                return
            
            # ===== ADD =====
            if text.startswith(".add "):
                new = text[5:].strip()
                if new:
                    self.replies.append(new)
                    self.save_data()
                    self.send(chat_id, f"✅ **اضافه شد:** `{new}`\n📊 تعداد: {len(self.replies)}")
                return
            
            # ===== LIST =====
            if text == ".list":
                if not self.replies:
                    self.send(chat_id, "📭 **هیچ پاسخی وجود ندارد!**")
                    return
                txt = f"📋 **لیست پاسخ‌ها** ({len(self.replies)}):\n"
                for i, r in enumerate(self.replies[:20], 1):
                    txt += f"{i}. {r}\n"
                self.send(chat_id, txt)
                return
            
            # ===== REMOVE =====
            if text.startswith(".remove "):
                try:
                    num = int(text[8:]) - 1
                    if 0 <= num < len(self.replies):
                        removed = self.replies.pop(num)
                        self.save_data()
                        self.send(chat_id, f"🗑️ **حذف شد:** `{removed}`")
                    else:
                        self.send(chat_id, f"❌ عدد 1 تا {len(self.replies)}")
                except:
                    self.send(chat_id, "❌ مثال: `.remove 1`")
                return
            
            # ===== CLEAR =====
            if text == ".clear":
                self.replies = []
                self.save_data()
                self.send(chat_id, "🧹 **همه پاسخ‌ها پاک شد!**")
                return
            
            # ===== INTERVAL =====
            if text.startswith(".interval "):
                try:
                    sec = int(text[10:])
                    if 1 <= sec <= 10:
                        self.interval = sec
                        self.send(chat_id, f"⏱️ **فاصله ارسال:** {sec} ثانیه")
                except:
                    pass
                return
            
            # ===== GAMES =====
            if text == ".dice":
                dice = random.randint(1, 6)
                self.scores[user] = self.scores.get(user, 0) + dice
                self.save_data()
                self.send(chat_id, f"🎲 **تاس:** {dice}\n+{dice} امتیاز")
                return
            
            if text == ".coin":
                coin = random.choice(["شیر 🦁", "خط 📍"])
                self.scores[user] = self.scores.get(user, 0) + 5
                self.save_data()
                self.send(chat_id, f"🪙 **سکه:** {coin}\n+5 امتیاز")
                return
            
            if text == ".slot":
                slot = ["🍒", "🍊", "🍋", "🍉", "⭐", "💎"]
                res = [random.choice(slot) for _ in range(3)]
                if res[0] == res[1] == res[2]:
                    points = 100
                    self.scores[user] = self.scores.get(user, 0) + points
                    self.send(chat_id, f"🎰 `{' '.join(res)}`\n✨ **JACKPOT!** +{points}")
                elif res[0] == res[1] or res[1] == res[2]:
                    points = 20
                    self.scores[user] = self.scores.get(user, 0) + points
                    self.send(chat_id, f"🎰 `{' '.join(res)}`\n🎉 بردی! +{points}")
                else:
                    self.send(chat_id, f"🎰 `{' '.join(res)}`\n😢 باختی!")
                self.save_data()
                return
            
            if text.startswith(".guess "):
                try:
                    guess = int(text[7:])
                    target = random.randint(1, 10)
                    if guess == target:
                        self.scores[user] = self.scores.get(user, 0) + 30
                        self.send(chat_id, f"🎯 **درست بود!** عدد {target}\n+30 امتیاز")
                    else:
                        self.send(chat_id, f"❌ **اشتباه!** عدد {target} بود")
                    self.save_data()
                except:
                    self.send(chat_id, "❌ مثال: `.guess 5`")
                return
            
            if text in [".rps سنگ", ".rps کاغذ", ".rps قیچی"]:
                user_choice = text[5:]
                bot_choice = random.choice(["سنگ", "کاغذ", "قیچی"])
                emojis = {"سنگ": "🪨", "کاغذ": "📄", "قیچی": "✂️"}
                if user_choice == bot_choice:
                    points = 10
                    result = "مساوی 🤝"
                elif (user_choice == "سنگ" and bot_choice == "قیچی") or \
                     (user_choice == "کاغذ" and bot_choice == "سنگ") or \
                     (user_choice == "قیچی" and bot_choice == "کاغذ"):
                    points = 25
                    result = "بردی 🎉"
                else:
                    points = 0
                    result = "باختی 😢"
                self.scores[user] = self.scores.get(user, 0) + points
                self.save_data()
                self.send(chat_id, f"{emojis[user_choice]} vs {emojis[bot_choice]}\n{result}\n+{points}")
                return
            
            # ===== ECONOMY =====
            if text == ".work":
                earnings = random.randint(50, 200)
                self.money[user] = self.money.get(user, 0) + earnings
                self.save_data()
                works = ["💻 برنامه‌نویسی", "📝 تایپ", "🎨 طراحی", "📚 مطالعه", "🧹 تمیزکاری"]
                self.send(chat_id, f"💼 **کار کردی:** {random.choice(works)}\n💰 +{earnings} تومان")
                return
            
            if text == ".daily":
                today = datetime.now().strftime("%Y%m%d")
                if self.daily.get(user) == today:
                    self.send(chat_id, "🎁 **امروز جایزه گرفتی!** فردا بیا")
                    return
                reward = random.randint(100, 500)
                self.money[user] = self.money.get(user, 0) + reward
                self.daily[user] = today
                self.save_data()
                self.send(chat_id, f"🎁 **جایزه روزانه!**\n💰 +{reward} تومان")
                return
            
            if text == ".money":
                self.send(chat_id, f"💰 **موجودی شما:** {self.money.get(user, 0)} تومان")
                return
            
            if text.startswith(".transfer "):
                parts = text[10:].split()
                if len(parts) >= 2:
                    target = parts[0].replace("@", "")
                    amount = int(parts[1])
                    if self.money.get(user, 0) >= amount:
                        self.money[user] = self.money.get(user, 0) - amount
                        self.money[target] = self.money.get(target, 0) + amount
                        self.save_data()
                        self.send(chat_id, f"💰 {amount} تومان به {target} انتقال یافت!")
                    else:
                        self.send(chat_id, "❌ پول کافی نداری!")
                return
            
            if text.startswith(".rob "):
                target = text[5:].strip().replace("@", "")
                if random.random() < 0.4:
                    stolen = random.randint(50, 200)
                    self.money[user] = self.money.get(user, 0) + stolen
                    self.money[target] = max(0, self.money.get(target, 0) - stolen)
                    self.save_data()
                    self.send(chat_id, f"🦹 **دزدی موفق!**\n💰 +{stolen} تومان از {target}")
                else:
                    penalty = random.randint(100, 300)
                    self.money[user] = self.money.get(user, 0) - penalty
                    self.save_data()
                    self.send(chat_id, f"🚨 **دزدی ناموفق! جریمه شدی!**\n💸 -{penalty} تومان")
                return
            
            # ===== SCORE =====
            if text == ".score":
                self.send(chat_id, f"📊 **امتیاز شما:** {self.scores.get(user, 0)}")
                return
            
            if text == ".top":
                top = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)[:10]
                if not top:
                    self.send(chat_id, "📊 هنوز امتیازی ثبت نشده!")
                    return
                txt = "🏆 **برترین‌ها** 🏆\n\n"
                for i, (uid, score) in enumerate(top, 1):
                    medal = {1:"🥇", 2:"🥈", 3:"🥉"}.get(i, "📌")
                    uid_short = uid[:15] + "..." if len(uid) > 15 else uid
                    txt += f"{medal} `{i}.` {uid_short} - {score}\n"
                self.send(chat_id, txt)
                return
            
            if text == ".level":
                score = self.scores.get(user, 0)
                if score < 100:
                    level = "🌱 نوآموز"
                elif score < 300:
                    level = "⭐ تازه‌کار"
                elif score < 600:
                    level = "🔥 حرفه‌ای"
                else:
                    level = "🏆 افسانه"
                self.send(chat_id, f"⭐ **سطح:** {level}\n📊 امتیاز: {score}")
                return
            
            # ===== TOOLS =====
            if text == ".time":
                now = datetime.now()
                self.send(chat_id, f"🕐 **زمان:** {now.strftime('%H:%M:%S')}\n📅 **تاریخ:** {now.strftime('%Y/%m/%d')}")
                return
            
            if text == ".id":
                self.send(chat_id, f"🆔 **آیدی چت:** `{chat_id}`\n👤 **آیدی شما:** `{user}`")
                return
            
            if text == ".ping":
                start = time.time()
                self.send(chat_id, "🏓 پینگ...")
                end = time.time()
                self.send(chat_id, f"🏓 **پونگ!** `{int((end-start)*1000)}ms`")
                return
            
            if text == ".status":
                active = sum(1 for v in self.active_chats.values() if v)
                uptime = time.strftime('%H:%M:%S', time.gmtime(time.time() - self.start_time))
                status = f"""
📊 **وضعیت ربات**
━━━━━━━━━━━━━━━━━━━━━━
• چت‌های فعال: `{active}`
• تعداد پاسخ‌ها: `{len(self.replies)}`
• فاصله ارسال: `{self.interval}s`
• زمان اجرا: `{uptime}`
"""
                self.send(chat_id, status)
                return
            
            if text == ".info":
                info = """
🤖 **SUPER BOT RTC**
━━━━━━━━━━━━━━━━━━━━━━
• نسخه: 5.0 Ultimate
• قابلیت‌ها: 40+ دستور
• بازی‌ها: 7 بازی
• اقتصاد: کامل
• ساخته شده: 2025
• آماده برای GitHub
"""
                self.send(chat_id, info)
                return
            
            if text.startswith(".calc "):
                try:
                    expr = text[6:].strip()
                    if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', expr):
                        result = eval(expr)
                        self.send(chat_id, f"🧮 **نتیجه:** {expr} = {result}")
                except:
                    pass
                return
            
            if text.startswith(".reverse "):
                self.send(chat_id, f"🔄 **برعکس:** {text[9:][::-1]}")
                return
            
            # ===== WARN =====
            if text.startswith(".warn "):
                target = text[6:].strip().replace("@", "")
                self.warns[target] = self.warns.get(target, 0) + 1
                self.save_data()
                self.send(chat_id, f"⚠️ **اخطار به {target}** ({self.warns[target]}/3)")
                if self.warns[target] >= 3:
                    self.send(chat_id, f"🚫 **{target} اخطار سوم! اخراج شد!**")
                    self.warns[target] = 0
                return
            
            if text == ".warns":
                self.send(chat_id, f"⚠️ **اخطارهای شما:** {self.warns.get(user, 0)}/3")
                return
            
            if text.startswith(".tag "):
                parts = text[5:].split(maxsplit=1)
                if len(parts) >= 2:
                    target = parts[0].replace("@", "")
                    tag_name = parts[1]
                    if user not in self.tags:
                        self.tags[user] = []
                    self.tags[user].append(tag_name)
                    self.save_data()
                    self.send(chat_id, f"🏷️ **تگ اضافه شد!**\n🎖️ {tag_name} به {target}")
                return
            
            if text == ".mytags":
                tags = self.tags.get(user, [])
                if not tags:
                    self.send(chat_id, "🏷️ **شما تگی ندارید!**")
                else:
                    self.send(chat_id, f"🏷️ **تگ‌های شما:**\n" + "\n".join([f"• #{t}" for t in tags]))
                return
            
            # ===== AUTO REPLY =====
            if chat_id in self.active_chats and self.active_chats[chat_id]:
                now = time.time()
                last = self.last_time.get(chat_id, 0)
                if now - last >= self.interval and self.replies:
                    self.send(chat_id, random.choice(self.replies))
                    self.last_time[chat_id] = now
        
        # ===== AUTO SENDER =====
        def auto():
            while True:
                try:
                    now = time.time()
                    for cid, active in list(self.active_chats.items()):
                        if active:
                            last = self.last_time.get(cid, 0)
                            if now - last >= self.interval and self.replies:
                                self.send(cid, random.choice(self.replies))
                                self.last_time[cid] = now
                except:
                    pass
                time.sleep(1)
        
        threading.Thread(target=auto, daemon=True).start()
        self.client.run()

# ==================== اجرا ====================
if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║                   🤖 SUPER BOT 🤖                         ║
║                                                          ║
║           کامل‌ترین ربات مدیریتی روبیکا                  ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║  ✅ ربات در حال راه‌اندازی...                           ║
║  📌 پس از لاگین، دستور .panel را بزنید                   ║
║  💡 برای شروع ارسال خودکار: .set                         ║
║  🎮 برای بازی‌ها: .dice , .coin , .slot                  ║
║  💰 برای اقتصاد: .work , .daily , .money                 ║
║  💕 برای عشق: .love                                      ║
║                                                          ║
║  🔗 GitHub: github.com/yourusername/superbot             ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    bot = SuperBot()
    bot.run()
