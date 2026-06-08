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
import hashlib
import sqlite3
import re
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict

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
B = '\033[94m'
P = '\033[95m'
C = '\033[96m'
W = '\033[97m'
BL = '\033[30m'
BG = '\033[42m'
BR = '\033[41m'
BY = '\033[43m'
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

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
        self.init_weapons()
        self.init_missions()
        self.init_achievements()
        
        threading.Thread(target=self.auto_upload, daemon=True).start()
        threading.Thread(target=self.auto_mission_check, daemon=True).start()
        threading.Thread(target=self.auto_bank_interest, daemon=True).start()
    
    def print_banner(self):
        banner = f"""
{G}{BOLD}
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║   ███████╗██╗   ██╗██████╗ ███████╗██████╗     ██████╗  ██████╗ ████████╗            ║
║   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██╔═══██╗╚══██╔══╝            ║
║   ███████╗██║   ██║██████╔╝█████╗  ██████╔╝    ██████╔╝██║   ██║   ██║               ║
║   ╚════██║██║   ██║██╔═══╝ ██╔══╝  ██╔══██╗    ██╔══██╗██║   ██║   ██║               ║
║   ███████║╚██████╔╝██║     ███████╗██║  ██║    ██████╔╝╚██████╔╝   ██║               ║
║   ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝    ╚═════╝  ╚═════╝    ╚═╝               ║
║                                                                                      ║
║                    ██████╗ ███████╗████████╗██╗   ██╗██████╗ ███╗   ██╗            ║
║                    ██╔══██╗██╔════╝╚══██╔══╝╚██╗ ██╔╝██╔══██╗████╗  ██║            ║
║                    ██████╔╝█████╗     ██║    ╚████╔╝ ██████╔╝██╔██╗ ██║            ║
║                    ██╔══██╗██╔══╝     ██║     ╚██╔╝  ██╔══██╗██║╚██╗██║            ║
║                    ██████╔╝███████╗   ██║      ██║   ██║  ██║██║ ╚████║            ║
║                    ╚═════╝ ╚══════╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝            ║
║                                                                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║  {C}[+] User: {USER_ID}{' ' * (68 - len(USER_ID))}{G}║
║  {C}[+] Version: 7.0.0 Ultimate{RESET}{G}{' ' * 57}║
║  {C}[+] Auto Backup: kaizofil.ir{RESET}{G}{' ' * 58}║
║  {C}[+] Sync Interval: 60 seconds{RESET}{G}{' ' * 55}║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║  {Y}[!] MAIN COMMANDS{RESET}{G}{' ' * 66}║
║  {C}    .panel    .set      .add      .list     .remove   .clear     .interval{RESET}{G}║
║  {Y}[!] GAMES{RESET}{G}{' ' * 73}║
║  {C}    .dice     .coin     .slot     .love     .rps      .blackjack .roulette{RESET}{G}║
║  {Y}[!] ECONOMY{RESET}{G}{' ' * 72}║
║  {C}    .work     .daily    .money    .score    .top      .transfer  .rob{RESET}{G}    ║
║  {C}    .bank     .deposit  .withdraw .loan     .pay      .shop      .buy{RESET}{G}    ║
║  {Y}[!] WEAPONS{RESET}{G}{' ' * 72}║
║  {C}    .weapons  .buygun   .shoot    .bullets  .armor    .heal{RESET}{G}             ║
║  {Y}[!] MISSIONS{RESET}{G}{' ' * 70}║
║  {C}    .mission  .achievements{RESET}{G}{' ' * 62}║
║  {Y}[!] TOOLS{RESET}{G}{' ' * 73}║
║  {C}    .time     .id       .ping     .stats    .status   .info     .calc{RESET}{G}   ║
║  {C}    .reverse  .quote    .joke     .fact     .weather  .news{RESET}{G}            ║
║  {Y}[!] ADMIN{RESET}{G}{' ' * 73}║
║  {C}    .warn     .ban      .unban    .mute     .kick     .promote  .demote{RESET}{G} ║
║  {C}    .setadmin .setrule  .welcome  .lock     .unlock{RESET}{G}                    ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║  {G}[+] Total Commands: 60+{RESET}{G}{' ' * 62}║
║  {G}[+] Database: SQLite + JSON{RESET}{G}{' ' * 57}║
║  {G}[+] Auto Backup: Enabled{RESET}{G}{' ' * 62}║
╚══════════════════════════════════════════════════════════════════════════════════════╝
{RESET}"""
        print(banner)
    
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
                xp INTEGER DEFAULT 0,
                bank INTEGER DEFAULT 0,
                bank_time INTEGER DEFAULT 0,
                daily TEXT,
                warns INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                created_at TEXT,
                last_seen TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                item_name TEXT,
                quantity INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS weapons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                weapon_name TEXT,
                damage INTEGER,
                durability INTEGER DEFAULT 100,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bullets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                bullet_type TEXT,
                quantity INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
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
                completed INTEGER DEFAULT 0,
                claimed INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                achievement_name TEXT,
                unlocked_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                amount INTEGER,
                interest INTEGER,
                taken_at INTEGER,
                due_at INTEGER,
                paid INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                bet_type TEXT,
                amount INTEGER,
                result TEXT,
                won INTEGER,
                created_at TEXT
            )
        ''')
        
        self.conn.commit()
    
    def init_shop(self):
        self.shop_items = {
            "sword": {"name": "⚔️ Sword", "price": 500, "damage": 10},
            "bow": {"name": "🏹 Bow", "price": 300, "damage": 7},
            "axe": {"name": "🪓 Axe", "price": 400, "damage": 8},
            "dagger": {"name": "🗡️ Dagger", "price": 200, "damage": 5},
            "spear": {"name": "🔱 Spear", "price": 600, "damage": 12},
            "hammer": {"name": "🔨 Hammer", "price": 700, "damage": 15},
            "shield": {"name": "🛡️ Shield", "price": 300, "defense": 5},
            "helmet": {"name": "⛑️ Helmet", "price": 200, "defense": 3},
            "armor": {"name": "🦺 Armor", "price": 500, "defense": 8},
            "potion": {"name": "🧪 Health Potion", "price": 100, "heal": 50},
            "elixir": {"name": "✨ Elixir", "price": 500, "heal": 100},
            "ring": {"name": "💍 Ring", "price": 1000, "luck": 5},
            "amulet": {"name": "📿 Amulet", "price": 1500, "luck": 10},
            "cape": {"name": "🧥 Cape", "price": 800, "speed": 5},
            "boots": {"name": "👢 Boots", "price": 400, "speed": 3}
        }
    
    def init_weapons(self):
        self.weapons = {
            "pistol": {"name": "🔫 Pistol", "damage": 15, "price": 1000, "ammo": 6},
            "shotgun": {"name": "🔫 Shotgun", "damage": 30, "price": 2000, "ammo": 2},
            "rifle": {"name": "🔫 Rifle", "damage": 25, "price": 2500, "ammo": 5},
            "sniper": {"name": "🎯 Sniper", "damage": 50, "price": 5000, "ammo": 3},
            "minigun": {"name": "💥 Minigun", "damage": 10, "price": 8000, "ammo": 30},
            "rpg": {"name": "💣 RPG", "damage": 100, "price": 15000, "ammo": 1},
            "flamethrower": {"name": "🔥 Flamethrower", "damage": 20, "price": 10000, "ammo": 10},
            "laser": {"name": "⚡ Laser Gun", "damage": 40, "price": 20000, "ammo": 8}
        }
    
    def init_missions(self):
        self.missions_list = [
            {"name": "First Blood", "desc": "Win first game", "target": 1, "reward": 100},
            {"name": "Rich Begins", "desc": "Earn 1000 coins", "target": 1000, "reward": 200},
            {"name": "Gambler", "desc": "Play dice 10 times", "target": 10, "reward": 150},
            {"name": "Sharp Shooter", "desc": "Shoot 5 times", "target": 5, "reward": 250},
            {"name": "Weapon Master", "desc": "Buy a weapon", "target": 1, "reward": 100},
            {"name": "Millionaire", "desc": "Reach 10000 coins", "target": 10000, "reward": 1000},
            {"name": "Banker", "desc": "Deposit 5000 in bank", "target": 5000, "reward": 500},
            {"name": "Daily Player", "desc": "Claim daily reward 7 days", "target": 7, "reward": 700}
        ]
    
    def init_achievements(self):
        self.achievements_list = [
            "🏆 Welcome", "⭐ Level 5", "⭐ Level 10", "⭐ Level 20",
            "💰 Millionaire", "💰 Billionaire", "🎮 Gamer", "🔫 Killer",
            "🏦 Banker", "🤝 Helper", "👑 Legend"
        ]
    
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
            self.xp = 0
            self.bank = 0
            self.bank_time = 0
        else:
            self.money = result[2]
            self.scores = result[3]
            self.level = result[4]
            self.xp = result[5]
            self.bank = result[6]
            self.bank_time = result[7]
        
        self.replies = []
        data_file = f"{self.user_folder}/replies.json"
        if os.path.exists(data_file):
            with open(data_file, "r") as f:
                self.replies = json.load(f)
    
    def save_data(self):
        user_id = USER_ID
        self.cursor.execute('''
            UPDATE users SET money=?, score=?, level=?, xp=?, bank=?, bank_time=?, last_seen=?
            WHERE user_id = ?
        ''', (self.money, self.scores, self.level, self.xp, self.bank, self.bank_time, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
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
        
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (USER_ID,))
        user_data = self.cursor.fetchone()
        if user_data:
            upload_data(f"{USER_ID}/user.json", json.dumps({
                "money": user_data[2], "score": user_data[3], "level": user_data[4],
                "xp": user_data[5], "bank": user_data[6]
            }))
    
    def auto_upload(self):
        while True:
            time.sleep(60)
            self.upload_to_host()
    
    def auto_mission_check(self):
        while True:
            time.sleep(300)
            self.check_missions()
    
    def auto_bank_interest(self):
        while True:
            time.sleep(3600)
            if self.bank > 0 and self.bank_time > 0:
                hours = (time.time() - self.bank_time) / 3600
                interest = int(self.bank * 0.05 * hours)
                if interest > 0:
                    self.bank += interest
                    self.save_data()
    
    def check_missions(self):
        self.cursor.execute("SELECT mission_name, progress, target, reward, completed FROM missions WHERE user_id = ? AND completed = 0", (USER_ID,))
        missions = self.cursor.fetchall()
        
        for mission in missions:
            name, progress, target, reward, completed = mission
            if progress >= target and not completed:
                self.cursor.execute("UPDATE missions SET completed = 1 WHERE user_id = ? AND mission_name = ?", (USER_ID, name))
                self.money += reward
                self.conn.commit()
                self.save_data()
    
    def add_mission_progress(self, mission_name, amount=1):
        self.cursor.execute("SELECT progress, target FROM missions WHERE user_id = ? AND mission_name = ?", (USER_ID, mission_name))
        result = self.cursor.fetchone()
        
        if result:
            progress, target = result
            if progress < target:
                self.cursor.execute("UPDATE missions SET progress = progress + ? WHERE user_id = ? AND mission_name = ?", (amount, USER_ID, mission_name))
                self.conn.commit()
        else:
            for m in self.missions_list:
                if m["name"] == mission_name:
                    self.cursor.execute('''
                        INSERT INTO missions (user_id, mission_name, progress, target, reward)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (USER_ID, mission_name, amount, m["target"], m["reward"]))
                    self.conn.commit()
                    break
    
    def add_achievement(self, achievement_name):
        self.cursor.execute("SELECT * FROM achievements WHERE user_id = ? AND achievement_name = ?", (USER_ID, achievement_name))
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO achievements (user_id, achievement_name, unlocked_at) VALUES (?, ?, ?)",
                              (USER_ID, achievement_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.conn.commit()
            return True
        return False
    
    def send(self, chat_id, text):
        try:
            return self.client.send_text(chat_id, text)
        except:
            return None
    
    def love_anim(self, chat_id):
        try:
            r = self.client.send_text(chat_id, "💘")
            mid = r['message_update']['message_id']
            for i in range(2, 31):
                time.sleep(0.1)
                self.client.send_text(chat_id, "💘" * i, message_id=mid)
            self.client.send_text(chat_id, "💘" * 30 + "\n❤️ 100% LOVE ❤️", message_id=mid)
        except:
            pass
    
    def panel(self):
        return f"""
{G}{BOLD}╔════════════════════════════════════════════════════════════════════╗{RESET}
{G}{BOLD}║                    SUPER BOT v7.0 COMMANDS                         ║{RESET}
{G}{BOLD}╠════════════════════════════════════════════════════════════════════╣{RESET}
{Y}║ [MAIN]                                                                  ║{RESET}
{Y}║   .set     - Start/Stop auto reply                                     ║{RESET}
{Y}║   .add txt - Add new reply                                             ║{RESET}
{Y}║   .list    - Show my replies                                           ║{RESET}
{Y}║   .remove n- Remove reply                                              ║{RESET}
{Y}║   .clear   - Clear all replies                                         ║{RESET}
{Y}║   .interval n - Set speed (1-10)                                       ║{RESET}
{Y}╠════════════════════════════════════════════════════════════════════╣{RESET}
{Y}║ [GAMES]                                                                 ║{RESET}
{Y}║   .dice    - Roll dice (1-6) +points                                   ║{RESET}
{Y}║   .coin    - Flip coin (HEAD/TAIL) +5                                  ║{RESET}
{Y}║   .slot    - Slot machine (JACKPOT 100)                                ║{RESET}
{Y}║   .love    - Love animation (30 steps)                                 ║{RESET}
{Y}║   .rps     - Rock Paper Scissors                                       ║{RESET}
{Y}║   .blackjack - Blackjack game                                          ║{RESET}
{Y}║   .roulette - Russian Roulette                                         ║{RESET}
{Y}╠════════════════════════════════════════════════════════════════════╣{RESET}
{Y}║ [ECONOMY]                                                              ║{RESET}
{Y}║   .work    - Work for money (50-200)                                   ║{RESET}
{Y}║   .daily   - Daily reward (100-500)                                    ║{RESET}
{Y}║   .money   - Check balance                                             ║{RESET}
{Y}║   .score   - Check points                                              ║{RESET}
{Y}║   .top     - Top 10 players                                            ║{RESET}
{Y}║   .transfer @user amt - Send money                                     ║{RESET}
{Y}║   .rob @user - Rob other player (risk)                                 ║{RESET}
{Y}║   .bank    - Bank info                                                 ║{RESET}
{Y}║   .deposit amt - Deposit to bank                                       ║{RESET}
{Y}║   .withdraw amt - Withdraw from bank                                   ║{RESET}
{Y}║   .loan amt - Take loan (max 10000)                                    ║{RESET}
{Y}║   .pay     - Pay loan back                                             ║{RESET}
{Y}║   .shop    - Show shop items                                           ║{RESET}
{Y}║   .buy item - Buy from shop                                            ║{RESET}
{Y}╠════════════════════════════════════════════════════════════════════╣{RESET}
{Y}║ [WEAPONS]                                                              ║{RESET}
{Y}║   .weapons - Show weapons list                                         ║{RESET}
{Y}║   .buygun gun - Buy weapon                                             ║{RESET}
{Y}║   .shoot @user - Shoot other player                                    ║{RESET}
{Y}║   .bullets - Buy bullets                                               ║{RESET}
{Y}║   .armor   - Buy armor                                                 ║{RESET}
{Y}║   .heal    - Heal yourself                                             ║{RESET}
{Y}╠════════════════════════════════════════════════════════════════════╣{RESET}
{Y}║ [MISSIONS]                                                             ║{RESET}
{Y}║   .mission - Show current missions                                     ║{RESET}
{Y}║   .achievements - Show unlocked achievements                           ║{RESET}
{Y}╠════════════════════════════════════════════════════════════════════╣{RESET}
{Y}║ [TOOLS]                                                                ║{RESET}
{Y}║   .time    - Current date & time                                       ║{RESET}
{Y}║   .id      - Chat ID                                                   ║{RESET}
{Y}║   .ping    - Bot response time                                         ║{RESET}
{Y}║   .stats   - My statistics                                             ║{RESET}
{Y}║   .status  - Bot status                                                ║{RESET}
{Y}║   .info    - Bot info                                                  ║{RESET}
{Y}║   .calc 2+2 - Calculator                                              ║{RESET}
{Y}║   .reverse text - Reverse text                                         ║{RESET}
{Y}║   .quote   - Random quote                                              ║{RESET}
{Y}║   .joke    - Random joke                                               ║{RESET}
{Y}║   .fact    - Random fact                                               ║{RESET}
{Y}║   .weather - Weather info                                              ║{RESET}
{Y}║   .news    - Latest news                                               ║{RESET}
{Y}╠════════════════════════════════════════════════════════════════════╣{RESET}
{Y}║ [ADMIN]                                                                ║{RESET}
{Y}║   .warn @user - Warn user                                              ║{RESET}
{Y}║   .ban @user  - Ban user                                               ║{RESET}
{Y}║   .unban @user - Unban user                                            ║{RESET}
{Y}║   .mute @user - Mute user                                              ║{RESET}
{Y}║   .kick @user - Kick user                                              ║{RESET}
{Y}╠════════════════════════════════════════════════════════════════════╣{RESET}
{G}{BOLD}╚════════════════════════════════════════════════════════════════════╝{RESET}
"""
    
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
                self.send(chat_id, self.panel())
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
                if len(self.replies) > 30:
                    txt += f"{DIM}... and {len(self.replies)-30} more{RESET}"
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
                win = dice == 6
                if win:
                    points = 50
                    self.scores += points
                    self.money += points
                    self.add_mission_progress("First Blood")
                    self.add_mission_progress("Gambler")
                    result_msg = f"{G}[JACKPOT] +{points}{RESET}"
                else:
                    points = dice
                    self.scores += points
                    result_msg = f"{Y}+{points} points{RESET}"
                
                self.save_data()
                self.send(chat_id, f"{C}[DICE] {dice}{RESET}\n{result_msg}\n{G}Total: {self.scores}{RESET}")
                return
            
            # Coin flip
            if text == ".coin":
                coin = random.choice(["HEAD", "TAIL"])
                self.scores += 5
                self.money += 5
                self.save_data()
                self.send(chat_id, f"{C}[COIN] {coin}{RESET}\n{G}+5 points | +5 coins{RESET}")
                return
            
            # Slot machine
            if text == ".slot":
                symbols = ["🍒", "🍊", "🍋", "🍉", "⭐", "💎", "7️⃣"]
                result = [random.choice(symbols) for _ in range(3)]
                if result[0] == result[1] == result[2]:
                    if result[0] == "7️⃣":
                        points = 500
                    elif result[0] == "💎":
                        points = 300
                    elif result[0] == "⭐":
                        points = 200
                    else:
                        points = 100
                    self.scores += points
                    self.money += points
                    self.add_mission_progress("Gambler")
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
                if len(parts) < 2:
                    self.send(chat_id, f"{R}Usage: .rps [rock/paper/scissors] [amount]{RESET}")
                    return
                
                choice = parts[0].lower()
                try:
                    bet = int(parts[1])
                except:
                    bet = 10
                
                if bet > self.money:
                    self.send(chat_id, f"{R}[!] Not enough money! You have {self.money}{RESET}")
                    return
                
                choices = ["rock", "paper", "scissors"]
                if choice not in choices:
                    self.send(chat_id, f"{R}[!] Invalid choice! Use: rock, paper, scissors{RESET}")
                    return
                
                bot_choice = random.choice(choices)
                emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
                
                if choice == bot_choice:
                    result = "DRAW"
                    win_amount = 0
                    self.money += bet
                elif (choice == "rock" and bot_choice == "scissors") or \
                     (choice == "paper" and bot_choice == "rock") or \
                     (choice == "scissors" and bot_choice == "paper"):
                    result = "WIN"
                    win_amount = bet
                    self.money += bet * 2
                    self.add_mission_progress("Gambler")
                else:
                    result = "LOSE"
                    win_amount = -bet
                    self.money -= bet
                
                self.save_data()
                self.send(chat_id, f"{C}You: {emojis[choice]} | Bot: {emojis[bot_choice]}{RESET}\n{Y}[{result}]{RESET}\n{G}{'+' if win_amount > 0 else ''}{win_amount} coins{RESET}\n{G}Balance: {self.money}{RESET}")
                return
            
            # Blackjack
            if text == ".blackjack":
                if self.money < 50:
                    self.send(chat_id, f"{R}[!] Need at least 50 coins!{RESET}")
                    return
                
                bet = min(50, self.money)
                self.money -= bet
                
                player_cards = [random.randint(1, 11), random.randint(1, 11)]
                dealer_cards = [random.randint(1, 11), random.randint(1, 11)]
                player_sum = sum(player_cards)
                dealer_sum = sum(dealer_cards)
                
                if player_sum == 21:
                    win_amount = bet * 2
                    self.money += win_amount
                    result = f"{G}BLACKJACK! You win! +{win_amount}{RESET}"
                elif player_sum > 21:
                    result = f"{R}BUST! You lose! -{bet}{RESET}"
                else:
                    while dealer_sum < 17:
                        dealer_cards.append(random.randint(1, 11))
                        dealer_sum = sum(dealer_cards)
                    
                    if dealer_sum > 21 or player_sum > dealer_sum:
                        win_amount = bet * 2
                        self.money += win_amount
                        result = f"{G}You win! +{win_amount}{RESET}"
                    elif player_sum < dealer_sum:
                        result = f"{R}You lose! -{bet}{RESET}"
                    else:
                        self.money += bet
                        result = f"{Y}Push! Bet returned{RESET}"
                
                self.save_data()
                self.send(chat_id, f"{C}Your cards: {player_cards} = {player_sum}{RESET}\n{C}Dealer cards: {dealer_cards[:1]} + ?{RESET}\n{result}\n{G}Balance: {self.money}{RESET}")
                return
            
            # Work
            if text == ".work":
                earnings = random.randint(50, 200)
                self.money += earnings
                self.add_mission_progress("Rich Begins", earnings)
                self.save_data()
                jobs = ["💻 Programmer", "📝 Writer", "🎨 Designer", "📚 Teacher", "🔧 Mechanic", "👨‍🍳 Chef", "🚛 Driver"]
                self.send(chat_id, f"{G}[WORK] {random.choice(jobs)}{RESET}\n{G}+{earnings} coins{RESET}\n{G}Balance: {self.money}{RESET}")
                return
            
            # Daily reward
            if text == ".daily":
                today = datetime.now().strftime("%Y%m%d")
                if self.daily == today:
                    self.send(chat_id, f"{R}[!] Already claimed today! Come back tomorrow{RESET}")
                    return
                
                streak = 1
                self.daily = today
                reward = 100 + (streak * 10)
                self.money += reward
                self.add_mission_progress("Daily Player")
                self.save_data()
                self.send(chat_id, f"{G}[DAILY] +{reward} coins{RESET}\n{G}Streak: {streak} days{RESET}\n{G}Balance: {self.money}{RESET}")
                return
            
            # Check money
            if text == ".money":
                self.send(chat_id, f"{G}[BALANCE] {self.money} coins{RESET}")
                return
            
            # Check score
            if text == ".score":
                self.send(chat_id, f"{G}[SCORE] {self.scores} points{RESET}")
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
                interest = int(self.bank * 0.05) if self.bank > 0 else 0
                self.send(chat_id, f"{G}[BANK]{RESET}\n{G}Deposit: {self.bank} coins{RESET}\n{G}Interest (5%): {interest} coins/hour{RESET}")
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
                    if self.bank_time == 0:
                        self.bank_time = time.time()
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
                    due_at = int(time.time()) + 86400
                    self.cursor.execute('''
                        INSERT INTO loans (user_id, amount, interest, taken_at, due_at)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (USER_ID, amount, interest, int(time.time()), due_at))
                    self.money += amount
                    self.conn.commit()
                    self.save_data()
                    self.send(chat_id, f"{G}[LOAN] +{amount} coins{RESET}\n{G}Interest: {interest} coins (10%){RESET}\n{G}Due: 24 hours{RESET}\n{G}Balance: {self.money}{RESET}")
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
                            ON CONFLICT DO UPDATE SET quantity = quantity + 1
                        ''', (USER_ID, self.shop_items[item]["name"]))
                        self.conn.commit()
                        self.send(chat_id, f"{G}[BOUGHT] {self.shop_items[item]['name']}{RESET}\n{G}-{price} coins{RESET}")
                    else:
                        self.send(chat_id, f"{R}[!] Need {price} coins!{RESET}")
                else:
                    self.send(chat_id, f"{R}[!] Item not found! Use .shop{RESET}")
                return
            
            # Weapons list
            if text == ".weapons":
                weapons_text = f"{G}[WEAPONS]{RESET}\n"
                for gun, data in self.weapons.items():
                    weapons_text += f"{C}{data['name']}{RESET} - Dmg:{data['damage']} Price:{data['price']} Ammo:{data['ammo']}\n"
                self.send(chat_id, weapons_text)
                return
            
            # Buy gun
            if text.startswith(".buygun "):
                gun = text[8:].strip().lower()
                if gun in self.weapons:
                    price = self.weapons[gun]["price"]
                    if self.money >= price:
                        self.money -= price
                        self.save_data()
                        self.cursor.execute('''
                            INSERT INTO weapons (user_id, weapon_name, damage)
                            VALUES (?, ?, ?)
                        ''', (USER_ID, self.weapons[gun]["name"], self.weapons[gun]["damage"]))
                        self.conn.commit()
                        self.add_mission_progress("Weapon Master")
                        self.send(chat_id, f"{G}[BOUGHT] {self.weapons[gun]['name']}{RESET}\n{G}-{price} coins{RESET}")
                    else:
                        self.send(chat_id, f"{R}[!] Need {price} coins!{RESET}")
                else:
                    self.send(chat_id, f"{R}[!] Weapon not found! Use .weapons{RESET}")
                return
            
            # Shoot player
            if text.startswith(".shoot "):
                target = text[7:].strip().replace("@", "")
                self.cursor.execute("SELECT weapon_name, damage FROM weapons WHERE user_id = ?", (USER_ID,))
                weapon = self.cursor.fetchone()
                if not weapon:
                    self.send(chat_id, f"{R}[!] You don't have a weapon! Buy one with .buygun{RESET}")
                    return
                
                hit = random.random() < 0.7
                if hit:
                    damage = weapon[1]
                    self.add_mission_progress("Sharp Shooter")
                    self.send(chat_id, f"{G}[SHOOT] Hit! {damage} damage to {target}{RESET}")
                else:
                    self.send(chat_id, f"{R}[SHOOT] Missed!{RESET}")
                return
            
            # Missions
            if text == ".mission":
                self.cursor.execute("SELECT mission_name, progress, target, reward, completed FROM missions WHERE user_id = ?", (USER_ID,))
                missions = self.cursor.fetchall()
                
                if not missions:
                    for m in self.missions_list[:5]:
                        self.cursor.execute('''
                            INSERT INTO missions (user_id, mission_name, progress, target, reward)
                            VALUES (?, ?, 0, ?, ?)
                        ''', (USER_ID, m["name"], m["target"], m["reward"]))
                    self.conn.commit()
                    missions = self.cursor.fetchall()
                
                missions_text = f"{G}[MISSIONS]{RESET}\n"
                for m in missions:
                    name, prog, target, reward, completed = m
                    if completed:
                        missions_text += f"{G}✅ {name} - COMPLETED{RESET}\n"
                    else:
                        missions_text += f"{Y}📌 {name}: {prog}/{target} - Reward: {reward}{RESET}\n"
                
                self.send(chat_id, missions_text)
                return
            
            # Achievements
            if text == ".achievements":
                self.cursor.execute("SELECT achievement_name FROM achievements WHERE user_id = ?", (USER_ID,))
                achievements = self.cursor.fetchall()
                
                if len(achievements) >= 3:
                    self.add_achievement("🏆 Welcome")
                if self.level >= 5:
                    self.add_achievement("⭐ Level 5")
                if self.level >= 10:
                    self.add_achievement("⭐ Level 10")
                if self.money >= 10000:
                    self.add_achievement("💰 Millionaire")
                
                self.cursor.execute("SELECT achievement_name FROM achievements WHERE user_id = ?", (USER_ID,))
                achievements = self.cursor.fetchall()
                
                if achievements:
                    ach_text = f"{G}[ACHIEVEMENTS]{RESET}\n"
                    for ach in achievements:
                        ach_text += f"{C}🏆 {ach[0]}{RESET}\n"
                else:
                    ach_text = f"{Y}[ACHIEVEMENTS] No achievements yet! Keep playing!{RESET}"
                
                self.send(chat_id, ach_text)
                return
            
            # Stats
            if text == ".stats":
                level = self.scores // 100 + 1
                stats_text = f"""
{G}╔══════════════════════════════╗
║         MY STATS            ║
╠══════════════════════════════╣
║  {C}Level:   {level}{' ' * (22 - len(str(level)))}{G}║
║  {C}Points:  {self.scores}{' ' * (22 - len(str(self.scores)))}{G}║
║  {C}Money:   {self.money}{' ' * (22 - len(str(self.money)))}{G}║
║  {C}Bank:    {self.bank}{' ' * (22 - len(str(self.bank)))}{G}║
║  {C}Replies: {len(self.replies)}{' ' * (22 - len(str(len(self.replies))))}{G}║
╚══════════════════════════════╝{RESET}
"""
                self.send(chat_id, stats_text)
                return
            
            # Time
            if text == ".time":
                now = datetime.now()
                self.send(chat_id, f"{C}[TIME] {now.strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n{C}Weekday: {now.strftime('%A')}{RESET}")
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
{G}╔══════════════════════════════╗
║         BOT STATUS           ║
╠══════════════════════════════╣
║  {C}Active Chats: {active}{' ' * (20 - len(str(active)))}{G}║
║  {C}Replies:     {len(self.replies)}{' ' * (20 - len(str(len(self.replies))))}{G}║
║  {C}Money:       {self.money}{' ' * (20 - len(str(self.money)))}{G}║
║  {C}Points:      {self.scores}{' ' * (20 - len(str(self.scores)))}{G}║
║  {C}Interval:    {self.interval}s{' ' * (20 - len(str(self.interval)))}{G}║
║  {C}Uptime:      {uptime}{' ' * (20 - len(uptime))}{G}║
╚══════════════════════════════╝{RESET}
"""
                self.send(chat_id, status_text)
                return
            
            # Info
            if text == ".info":
                info_text = f"""
{G}╔══════════════════════════════╗
║         BOT INFO             ║
╠══════════════════════════════╣
║  {C}Name:     SUPER BOT v7.0{RESET}{G}{' ' * 11}║
║  {C}Author:   RTC Team{RESET}{G}{' ' * 19}║
║  {C}Commands: 60+{RESET}{G}{' ' * 21}║
║  {C}Database: SQLite + JSON{RESET}{G}{' ' * 12}║
║  {C}Backup:   kaizofil.ir{RESET}{G}{' ' * 15}║
╚══════════════════════════════╝{RESET}
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
                    "Believe you can and you're halfway there.",
                    "Dream it. Wish it. Do it.",
                    "Stay positive, work hard, make it happen."
                ]
                self.send(chat_id, f"{C}[QUOTE] {random.choice(quotes)}{RESET}")
                return
            
            # Joke
            if text == ".joke":
                jokes = [
                    "Why don't scientists trust atoms? Because they make up everything!",
                    "What do you call a fake noodle? An impasta!",
                    "Why did the scarecrow win an award? He was outstanding in his field!",
                    "I told my wife she was drawing her eyebrows too high. She looked surprised."
                ]
                self.send(chat_id, f"{C}[JOKE] {random.choice(jokes)}{RESET}")
                return
            
            # Fact
            if text == ".fact":
                facts = [
                    "Octopuses have three hearts.",
                    "A day on Venus is longer than a year on Venus.",
                    "Honey never spoils.",
                    "Bananas are berries, but strawberries aren't.",
                    "The Eiffel Tower grows taller in summer."
                ]
                self.send(chat_id, f"{C}[FACT] {random.choice(facts)}{RESET}")
                return
            
            # Weather
            if text == ".weather":
                weathers = ["☀️ Sunny 28°C", "⛅ Partly Cloudy 22°C", "🌧️ Rainy 18°C", "❄️ Snowy -5°C", "🌪️ Stormy 15°C"]
                self.send(chat_id, f"{C}[WEATHER] {random.choice(weathers)}{RESET}")
                return
            
            # News
            if text == ".news":
                news = [
                    "New update coming soon!",
                    "Bot reached 1000 users!",
                    "New features added!",
                    "Security update released."
                ]
                self.send(chat_id, f"{C}[NEWS] {random.choice(news)}{RESET}")
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
