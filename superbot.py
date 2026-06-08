#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
import time
import random
import json
import threading
import requests
import base64
import sqlite3
import re
from datetime import datetime

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--break-system-packages"])

install_package("pyrubi")

from pyrubi import Client
from pyrubi.types import Message

G = '\033[92m'
R = '\033[91m'
Y = '\033[93m'
C = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

HOST_URL = "https://kaizofil.ir/SuperBot/upload.php"
USER_ID = os.popen("whoami").read().strip()

def upload_data(filename, content):
    try:
        data = {"filename": filename, "content": base64.b64encode(content.encode()).decode()}
        r = requests.post(HOST_URL, json=data, timeout=10)
        return r.status_code == 200
    except:
        return False

class SuperBot:
    def __init__(self):
        os.system('clear')
        self.font_mode = "normal"
        self.print_banner()
        self.client = Client(session=f"SuperBot_{USER_ID}")
        self.start_time = time.time()
        self.interval = 2
        self.active_chats = {}
        self.last_time = {}
        self.user_folder = f"users/{USER_ID}"
        if not os.path.exists(self.user_folder):
            os.makedirs(self.user_folder)
        
        self.init_database()
        self.load_data()
        self.init_shop()
        
        threading.Thread(target=self.auto_upload, daemon=True).start()
    
    def print_banner(self):
        banner = f"""
{G}{BOLD}
    SUPER BOT v8.0 - RUBIKA SELF BOT
    User: {USER_ID}
    Version: 8.0.0 Ultimate
    Auto Backup: kaizofil.ir
    Font Mode: {self.font_mode}

    MAIN COMMANDS:
      .panel    .set      .add      .list     .remove   .clear     .interval
      .font     .font on  .font off

    GAMES:
      .dice     .coin     .slot     .love     .rps

    ECONOMY:
      .work     .daily    .money    .score    .top      .transfer  .rob
      .bank     .deposit  .withdraw .loan     .pay      .shop      .buy

    WEAPONS:
      .weapons  .buygun   .shoot

    MISSIONS:
      .mission  .achievements

    TOOLS:
      .time     .id       .ping     .stats    .status   .info      .calc
      .reverse  .quote    .joke     .fact

    ADMIN:
      .warn     .ban      .unban

    Total Commands: 50+
{RESET}"""
        print(banner)
    
    def apply_font(self, text):
        if self.font_mode == "bold":
            return f"**{text}**"
        elif self.font_mode == "italic":
            return f"__{text}__"
        return text
    
    def init_database(self):
        self.db_path = f"{self.user_folder}/bot.db"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                money INTEGER DEFAULT 0,
                score INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                bank INTEGER DEFAULT 0,
                daily TEXT,
                warns INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                created_at TEXT,
                last_seen TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                item_name TEXT,
                quantity INTEGER DEFAULT 1
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS weapons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                weapon_name TEXT,
                damage INTEGER
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                mission_name TEXT,
                progress INTEGER DEFAULT 0,
                target INTEGER,
                reward INTEGER,
                completed INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                achievement_name TEXT,
                unlocked_at TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                amount INTEGER,
                interest INTEGER,
                taken_at INTEGER,
                paid INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    def init_shop(self):
        self.shop_items = {
            "sword": {"name": "Sword", "price": 500},
            "bow": {"name": "Bow", "price": 300},
            "axe": {"name": "Axe", "price": 400},
            "shield": {"name": "Shield", "price": 300},
            "potion": {"name": "Health Potion", "price": 100},
            "elixir": {"name": "Elixir", "price": 500}
        }
    
    def load_data(self):
        user_id = USER_ID
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        
        if not result:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute('''
                INSERT INTO users (user_id, username, created_at, last_seen)
                VALUES (?, ?, ?, ?)
            ''', (user_id, user_id, now, now))
            self.conn.commit()
            self.money = 0
            self.scores = 0
            self.level = 1
            self.bank = 0
        else:
            self.money = result[2]
            self.scores = result[3]
            self.level = result[4]
            self.bank = result[5]
        
        self.replies = []
        data_file = f"{self.user_folder}/replies.json"
        if os.path.exists(data_file):
            with open(data_file, "r") as f:
                self.replies = json.load(f)
    
    def save_data(self):
        user_id = USER_ID
        self.cursor.execute('''
            UPDATE users SET money=?, score=?, level=?, bank=?, last_seen=?
            WHERE user_id = ?
        ''', (self.money, self.scores, self.level, self.bank, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
        self.conn.commit()
        
        data_file = f"{self.user_folder}/replies.json"
        with open(data_file, "w") as f:
            json.dump(self.replies, f, indent=2)
    
    def upload_to_host(self):
        data_file = f"{self.user_folder}/replies.json"
        if os.path.exists(data_file):
            with open(data_file, "r") as f:
                content = f.read()
            upload_data(f"{USER_ID}/replies.json", content)
        
        self.cursor.execute("SELECT money, score, level, bank FROM users WHERE user_id = ?", (USER_ID,))
        user_data = self.cursor.fetchone()
        if user_data:
            upload_data(f"{USER_ID}/user.json", json.dumps({
                "money": user_data[0], "score": user_data[1], "level": user_data[2], "bank": user_data[3]
            }))
    
    def auto_upload(self):
        while True:
            time.sleep(60)
            self.upload_to_host()
    
    def send(self, chat_id, text):
        try:
            formatted_text = self.apply_font(text)
            return self.client.send_text(chat_id, formatted_text)
        except:
            return None
    
    def love_anim(self, chat_id):
        try:
            r = self.client.send_text(chat_id, self.apply_font("💘"))
            mid = r['message_update']['message_id']
            for i in range(2, 31):
                time.sleep(0.1)
                self.client.edit_message(mid, chat_id, self.apply_font("💘" * i))
            self.client.edit_message(mid, chat_id, self.apply_font("💘" * 30 + "\nLOVE 100%"))
        except:
            pass
    
    def run(self):
        @self.client.on_message()
        def handler(msg):
            if not msg.text:
                return
            
            text = msg.text.strip()
            chat_id = str(msg.object_guid)
            
            print(f"{C}[{datetime.now().strftime('%H:%M:%S')}] {chat_id[:15]} -> {text[:50]}{RESET}")
            
            # Panel
            if text == ".panel":
                self.send(chat_id, self.print_banner.__doc__)
                return
            
            # Font mode
            if text == ".font on":
                self.font_mode = "bold"
                self.send(chat_id, f"{G}[FONT] Bold mode enabled{RESET}")
                return
            
            if text == ".font italic":
                self.font_mode = "italic"
                self.send(chat_id, f"{G}[FONT] Italic mode enabled{RESET}")
                return
            
            if text == ".font off":
                self.font_mode = "normal"
                self.send(chat_id, f"{G}[FONT] Normal mode enabled{RESET}")
                return
            
            if text == ".font":
                self.send(chat_id, f"{G}[FONT] Current mode: {self.font_mode}{RESET}")
                return
            
            # Love
            if text == ".love":
                threading.Thread(target=self.love_anim, args=(chat_id,), daemon=True).start()
                return
            
            # Set auto reply
            if text == ".set":
                if chat_id in self.active_chats and self.active_chats[chat_id]:
                    self.active_chats[chat_id] = False
                    self.send(chat_id, f"{R}[-] Auto reply OFF{RESET}")
                else:
                    if not self.replies:
                        self.send(chat_id, f"{R}[!] No replies! Use .add{RESET}")
                        return
                    self.active_chats[chat_id] = True
                    self.last_time[chat_id] = 0
                    self.send(chat_id, f"{G}[+] Auto reply ON (every {self.interval}s){RESET}")
                return
            
            # Add reply
            if text.startswith(".add "):
                new = text[5:].strip()
                if new:
                    self.replies.append(new)
                    self.save_data()
                    self.send(chat_id, f"{G}[+] Added: {new}{RESET}\n{G}Total: {len(self.replies)}{RESET}")
                return
            
            # List replies
            if text == ".list":
                if not self.replies:
                    self.send(chat_id, f"{R}[!] No replies{RESET}")
                    return
                txt = f"{G}[+] Replies ({len(self.replies)}):{RESET}\n"
                for i, r in enumerate(self.replies[:30], 1):
                    txt += f"{C}{i}. {r}{RESET}\n"
                self.send(chat_id, txt)
                return
            
            # Remove reply
            if text.startswith(".remove "):
                try:
                    n = int(text[8:]) - 1
                    if 0 <= n < len(self.replies):
                        r = self.replies.pop(n)
                        self.save_data()
                        self.send(chat_id, f"{R}[-] Removed: {r}{RESET}")
                    else:
                        self.send(chat_id, f"{R}[-] Number 1-{len(self.replies)}{RESET}")
                except:
                    self.send(chat_id, f"{R}[-] Usage: .remove 1{RESET}")
                return
            
            # Clear all replies
            if text == ".clear":
                self.replies = []
                self.save_data()
                self.send(chat_id, f"{R}[!] All replies cleared{RESET}")
                return
            
            # Interval
            if text.startswith(".interval "):
                try:
                    s = int(text[10:])
                    if 1 <= s <= 10:
                        self.interval = s
                        self.send(chat_id, f"{G}[+] Interval set to {s}s{RESET}")
                except:
                    pass
                return
            
            # Dice game
            if text == ".dice":
                dice = random.randint(1, 6)
                points = 10 if dice == 6 else dice
                self.scores += points
                self.money += points
                self.save_data()
                self.send(chat_id, f"{C}[DICE] {dice}{RESET}\n{G}+{points} coins | Total: {self.scores}{RESET}")
                return
            
            # Coin flip
            if text == ".coin":
                coin = random.choice(["HEAD", "TAIL"])
                self.scores += 5
                self.money += 5
                self.save_data()
                self.send(chat_id, f"{C}[COIN] {coin}{RESET}\n{G}+5 coins{RESET}")
                return
            
            # Slot machine
            if text == ".slot":
                symbols = ["🍒", "🍊", "🍋", "🍉", "⭐", "💎"]
                result = [random.choice(symbols) for _ in range(3)]
                if result[0] == result[1] == result[2]:
                    points = 100
                    self.scores += points
                    self.money += points
                    msg = f"{Y}[JACKPOT] +{points}{RESET}"
                elif result[0] == result[1] or result[1] == result[2]:
                    points = 20
                    self.scores += points
                    msg = f"{G}[WIN] +{points}{RESET}"
                else:
                    msg = f"{R}[LOSE]{RESET}"
                self.save_data()
                self.send(chat_id, f"{C}[SLOT] {' '.join(result)}{RESET}\n{msg}")
                return
            
            # Rock Paper Scissors
            if text.startswith(".rps "):
                parts = text[5:].split()
                if len(parts) < 1:
                    self.send(chat_id, f"{R}Usage: .rps rock/paper/scissors{RESET}")
                    return
                
                choice = parts[0].lower()
                choices = ["rock", "paper", "scissors"]
                if choice not in choices:
                    self.send(chat_id, f"{R}[!] Invalid choice! Use: rock, paper, scissors{RESET}")
                    return
                
                bot_choice = random.choice(choices)
                
                if choice == bot_choice:
                    result = "DRAW"
                    points = 5
                elif (choice == "rock" and bot_choice == "scissors") or \
                     (choice == "paper" and bot_choice == "rock") or \
                     (choice == "scissors" and bot_choice == "paper"):
                    result = "WIN"
                    points = 15
                else:
                    result = "LOSE"
                    points = -5
                
                self.scores += max(0, points)
                self.money += max(0, points)
                self.save_data()
                self.send(chat_id, f"{C}You: {choice} | Bot: {bot_choice}{RESET}\n{Y}[{result}]{RESET}\n{G}{'+' if points > 0 else ''}{points} coins{RESET}")
                return
            
            # Work
            if text == ".work":
                earnings = random.randint(50, 200)
                self.money += earnings
                self.save_data()
                self.send(chat_id, f"{G}[WORK] +{earnings} coins | Balance: {self.money}{RESET}")
                return
            
            # Daily reward
            if text == ".daily":
                today = datetime.now().strftime("%Y%m%d")
                if self.daily == today:
                    self.send(chat_id, f"{R}[!] Already claimed today! Come back tomorrow{RESET}")
                    return
                
                reward = random.randint(100, 500)
                self.money += reward
                self.daily = today
                self.save_data()
                self.send(chat_id, f"{G}[DAILY] +{reward} coins | Balance: {self.money}{RESET}")
                return
            
            # Check money
            if text == ".money":
                self.send(chat_id, f"{G}[BALANCE] {self.money} coins{RESET}")
                return
            
            # Check score
            if text == ".score":
                self.send(chat_id, f"{G}[SCORE] {self.scores} points{RESET}")
                return
            
            # Top players
            if text == ".top":
                self.cursor.execute("SELECT username, money FROM users ORDER BY money DESC LIMIT 10")
                top = self.cursor.fetchall()
                if not top:
                    self.send(chat_id, f"{R}[!] No players yet{RESET}")
                    return
                txt = f"{G}[TOP 10 PLAYERS]{RESET}\n"
                for i, (name, money) in enumerate(top, 1):
                    txt += f"{C}{i}. {name[:15]}... - {money} coins{RESET}\n"
                self.send(chat_id, txt)
                return
            
            # Transfer money
            if text.startswith(".transfer "):
                parts = text[10:].split()
                if len(parts) < 2:
                    self.send(chat_id, f"{R}Usage: .transfer @user amount{RESET}")
                    return
                
                target = parts[0].replace("@", "")
                try:
                    amount = int(parts[1])
                except:
                    self.send(chat_id, f"{R}Invalid amount!{RESET}")
                    return
                
                if amount > self.money:
                    self.send(chat_id, f"{R}[!] Not enough money! You have {self.money}{RESET}")
                    return
                
                self.money -= amount
                self.save_data()
                self.send(chat_id, f"{G}[TRANSFER] Sent {amount} coins to {target}{RESET}\n{G}Balance: {self.money}{RESET}")
                return
            
            # Rob other player
            if text.startswith(".rob "):
                target = text[5:].strip().replace("@", "")
                if random.random() < 0.4:
                    stolen = random.randint(10, 100)
                    self.money += stolen
                    self.send(chat_id, f"{G}[ROB] Success! +{stolen} coins from {target}{RESET}")
                else:
                    penalty = random.randint(20, 80)
                    self.money -= penalty
                    self.send(chat_id, f"{R}[ROB] Failed! -{penalty} coins penalty{RESET}")
                
                self.save_data()
                self.send(chat_id, f"{G}Balance: {self.money}{RESET}")
                return
            
            # Bank info
            if text == ".bank":
                self.send(chat_id, f"{G}[BANK] Deposit: {self.bank} coins{RESET}")
                return
            
            # Deposit to bank
            if text.startswith(".deposit "):
                try:
                    amount = int(text[9:])
                    if amount > self.money:
                        self.send(chat_id, f"{R}[!] Not enough money!{RESET}")
                        return
                    self.money -= amount
                    self.bank += amount
                    self.save_data()
                    self.send(chat_id, f"{G}[DEPOSIT] +{amount} coins to bank{RESET}\n{G}Balance: {self.money} | Bank: {self.bank}{RESET}")
                except:
                    self.send(chat_id, f"{R}Usage: .deposit amount{RESET}")
                return
            
            # Withdraw from bank
            if text.startswith(".withdraw "):
                try:
                    amount = int(text[10:])
                    if amount > self.bank:
                        self.send(chat_id, f"{R}[!] Not enough in bank!{RESET}")
                        return
                    self.bank -= amount
                    self.money += amount
                    self.save_data()
                    self.send(chat_id, f"{G}[WITHDRAW] -{amount} coins from bank{RESET}\n{G}Balance: {self.money} | Bank: {self.bank}{RESET}")
                except:
                    self.send(chat_id, f"{R}Usage: .withdraw amount{RESET}")
                return
            
            # Take loan
            if text.startswith(".loan "):
                try:
                    amount = int(text[6:])
                    if amount > 10000:
                        self.send(chat_id, f"{R}[!] Max loan is 10000 coins!{RESET}")
                        return
                    
                    self.cursor.execute("SELECT id FROM loans WHERE user_id = ? AND paid = 0", (USER_ID,))
                    if self.cursor.fetchone():
                        self.send(chat_id, f"{R}[!] You have an unpaid loan!{RESET}")
                        return
                    
                    interest = int(amount * 0.1)
                    self.cursor.execute('''
                        INSERT INTO loans (user_id, amount, interest, taken_at)
                        VALUES (?, ?, ?, ?)
                    ''', (USER_ID, amount, interest, int(time.time())))
                    self.money += amount
                    self.conn.commit()
                    self.save_data()
                    self.send(chat_id, f"{G}[LOAN] +{amount} coins{RESET}\n{G}Interest: {interest} coins (10%){RESET}\n{G}Balance: {self.money}{RESET}")
                except:
                    self.send(chat_id, f"{R}Usage: .loan amount{RESET}")
                return
            
            # Pay loan
            if text == ".pay":
                self.cursor.execute("SELECT id, amount, interest FROM loans WHERE user_id = ? AND paid = 0", (USER_ID,))
                loan = self.cursor.fetchone()
                if not loan:
                    self.send(chat_id, f"{R}[!] No active loans!{RESET}")
                    return
                
                loan_id, amount, interest = loan
                total = amount + interest
                if self.money < total:
                    self.send(chat_id, f"{R}[!] Need {total} coins to pay loan!{RESET}")
                    return
                
                self.money -= total
                self.cursor.execute("UPDATE loans SET paid = 1 WHERE id = ?", (loan_id,))
                self.conn.commit()
                self.save_data()
                self.send(chat_id, f"{G}[LOAN PAID] -{total} coins{RESET}\n{G}Balance: {self.money}{RESET}")
                return
            
            # Shop
            if text == ".shop":
                shop_text = f"{G}[SHOP]{RESET}\n"
                for item, data in self.shop_items.items():
                    shop_text += f"{C}{data['name']}{RESET} - {data['price']} coins\n"
                self.send(chat_id, shop_text)
                return
            
            # Buy from shop
            if text.startswith(".buy "):
                item = text[5:].strip().lower()
                if item in self.shop_items:
                    price = self.shop_items[item]["price"]
                    if self.money >= price:
                        self.money -= price
                        self.save_data()
                        self.cursor.execute('''
                            INSERT INTO inventory (user_id, item_name, quantity)
                            VALUES (?, ?, 1)
                        ''', (USER_ID, self.shop_items[item]["name"]))
                        self.conn.commit()
                        self.send(chat_id, f"{G}[BOUGHT] {self.shop_items[item]['name']}{RESET}\n{G}-{price} coins{RESET}")
                    else:
                        self.send(chat_id, f"{R}[!] Need {price} coins!{RESET}")
                else:
                    self.send(chat_id, f"{R}[!] Item not found! Use .shop{RESET}")
                return
            
            # Stats
            if text == ".stats":
                level = self.scores // 100 + 1
                stats_text = f"""
{G}[MY STATS]{RESET}
  Level: {level}
  Points: {self.scores}
  Money: {self.money}
  Bank: {self.bank}
  Replies: {len(self.replies)}
"""
                self.send(chat_id, stats_text)
                return
            
            # Time
            if text == ".time":
                now = datetime.now()
                self.send(chat_id, f"{C}[TIME] {now.strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
                return
            
            # ID
            if text == ".id":
                self.send(chat_id, f"{C}[ID] Chat: {chat_id}{RESET}\n{C}User: {USER_ID}{RESET}")
                return
            
            # Ping
            if text == ".ping":
                start = time.time()
                self.send(chat_id, f"{C}[PING] ...{RESET}")
                end = time.time()
                self.send(chat_id, f"{C}[PONG] {int((end-start)*1000)}ms{RESET}")
                return
            
            # Status
            if text == ".status":
                active = sum(1 for v in self.active_chats.values() if v)
                uptime = time.strftime('%H:%M:%S', time.gmtime(time.time() - self.start_time))
                status_text = f"""
{G}[BOT STATUS]{RESET}
  Active Chats: {active}
  Replies: {len(self.replies)}
  Money: {self.money}
  Points: {self.scores}
  Interval: {self.interval}s
  Uptime: {uptime}
"""
                self.send(chat_id, status_text)
                return
            
            # Info
            if text == ".info":
                info_text = f"""
{G}[BOT INFO]{RESET}
  Name: SUPER BOT v8.0
  Author: RTC Team
  Commands: 50+
  Database: SQLite + JSON
  Backup: kaizofil.ir
"""
                self.send(chat_id, info_text)
                return
            
            # Calculator
            if text.startswith(".calc "):
                try:
                    expr = text[6:].strip()
                    if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', expr):
                        result = eval(expr)
                        self.send(chat_id, f"{C}[CALC] {expr} = {result}{RESET}")
                except:
                    self.send(chat_id, f"{R}[CALC] Invalid expression{RESET}")
                return
            
            # Reverse text
            if text.startswith(".reverse "):
                reverse_text = text[9:][::-1]
                self.send(chat_id, f"{C}[REVERSE] {reverse_text}{RESET}")
                return
            
            # Quote
            if text == ".quote":
                quotes = [
                    "The only limit is your mind.",
                    "Success is not final, failure is not fatal.",
                    "Believe you can and you're halfway there."
                ]
                self.send(chat_id, f"{C}[QUOTE] {random.choice(quotes)}{RESET}")
                return
            
            # Joke
            if text == ".joke":
                jokes = [
                    "Why don't scientists trust atoms? Because they make up everything!",
                    "What do you call a fake noodle? An impasta!",
                    "Why did the scarecrow win an award? He was outstanding in his field!"
                ]
                self.send(chat_id, f"{C}[JOKE] {random.choice(jokes)}{RESET}")
                return
            
            # Fact
            if text == ".fact":
                facts = [
                    "Octopuses have three hearts.",
                    "A day on Venus is longer than a year on Venus.",
                    "Honey never spoils."
                ]
                self.send(chat_id, f"{C}[FACT] {random.choice(facts)}{RESET}")
                return
            
            # Auto reply
            if chat_id in self.active_chats and self.active_chats[chat_id]:
                now = time.time()
                last = self.last_time.get(chat_id, 0)
                if now - last >= self.interval and self.replies:
                    self.send(chat_id, random.choice(self.replies))
                    self.last_time[chat_id] = now
        
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

if __name__ == "__main__":
    bot = SuperBot()
    bot.run()
