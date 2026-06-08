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
import itertools
import math
import string
import uuid
import csv
import io
import zipfile
import tarfile
import shutil
import tempfile
import logging
import traceback
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from functools import wraps

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
RESET = '\033[0m'
BOLD = '\033[1m'
DIM = '\033[2m'

HOST_URL = "https://kaizofil.ir/SuperBot/upload.php"
USER_ID = os.popen("whoami").read().strip()
BACKUP_INTERVAL = 30

def upload_data(filename, content):
    try:
        data = {"filename": filename, "content": base64.b64encode(content.encode()).decode()}
        r = requests.post(HOST_URL, json=data, timeout=10)
        return r.status_code == 200
    except:
        return False

def log_error(msg):
    with open("error.log", "a") as f:
        f.write(f"{datetime.now()} - {msg}\n")

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
        self.init_weapons()
        self.init_missions()
        self.init_achievements()
        self.init_quotes()
        self.init_jokes()
        self.init_facts()
        self.init_fortunes()
        self.init_rps_choices()
        self.init_cards()
        self.init_dice_sides()
        self.init_slot_symbols()
        self.init_colors()
        self.init_animals()
        self.init_cities()
        self.init_foods()
        self.init_jobs()
        self.init_skills()
        self.init_titles()
        self.init_badges()
        
        threading.Thread(target=self.auto_upload, daemon=True).start()
        threading.Thread(target=self.auto_save, daemon=True).start()
        threading.Thread(target=self.auto_bank_interest, daemon=True).start()
        threading.Thread(target=self.auto_mission_check, daemon=True).start()
        threading.Thread(target=self.auto_reminder, daemon=True).start()
        threading.Thread(target=self.auto_weather_update, daemon=True).start()
        threading.Thread(target=self.auto_cleanup, daemon=True).start()
    
    def print_banner(self):
        banner = f"""
{G}{BOLD}
╔══════════════════════════════════════════════════════════════════════╗
║                    SUPER BOT v9.0 - ULTIMATE EDITION                ║
╠══════════════════════════════════════════════════════════════════════╣
║  {C}User: {USER_ID}{' ' * (55 - len(USER_ID))}{G}║
║  {C}Version: 9.0.0 Ultimate{RESET}{G}{' ' * 43}║
║  {C}Auto Backup: kaizofil.ir (30s){RESET}{G}{' ' * 39}║
║  {C}Font Mode: {self.font_mode}{' ' * (54 - len(self.font_mode))}{G}║
╠══════════════════════════════════════════════════════════════════════╣
║  {Y}MAIN COMMANDS{RESET}{G}{' ' * 66}║
║  {C}.panel .set .add .list .remove .clear .interval .font{RESET}{G}║
║  {Y}GAMES{RESET}{G}{' ' * 73}║
║  {C}.dice .coin .slot .love .rps .blackjack .roulette .cards{RESET}{G}║
║  {Y}ECONOMY{RESET}{G}{' ' * 72}║
║  {C}.work .daily .money .score .top .transfer .rob .bank .deposit{RESET}{G}║
║  {C}.withdraw .loan .pay .shop .buy .sell .invest .stock .gamble{RESET}{G}║
║  {Y}WEAPONS & BATTLE{RESET}{G}{' ' * 63}║
║  {C}.weapons .buygun .shoot .duel .attack .defend .heal .armor{RESET}{G}║
║  {Y}MISSIONS & ACHIEVEMENTS{RESET}{G}{' ' * 57}║
║  {C}.mission .achievements .dailyquest .weeklyquest .event{RESET}{G}║
║  {Y}TOOLS & UTILITIES{RESET}{G}{' ' * 63}║
║  {C}.time .id .ping .stats .status .info .calc .reverse .quote{RESET}{G}║
║  {C}.joke .fact .fortune .weather .news .translate .quran .hadith{RESET}{G}║
║  {Y}ADMIN{RESET}{G}{' ' * 73}║
║  {C}.warn .ban .unban .mute .kick .promote .demote .setadmin{RESET}{G}║
║  {Y}CHAT{RESET}{G}{' ' * 73}║
║  {C}.welcome .goodbye .rules .lock .unlock .filter .unfilter{RESET}{G}║
║  {Y}REFERRAL{RESET}{G}{' ' * 71}║
║  {C}.refer .referral .claim .redeem .giftcode .voucher{RESET}{G}║
╠══════════════════════════════════════════════════════════════════════╣
║  {G}Total Commands: 120+ | Database: SQLite + JSON | Backup: Enabled{RESET}║
╚══════════════════════════════════════════════════════════════════════╝
{RESET}"""
        print(banner)
    
    def apply_font(self, text):
        if self.font_mode == "bold":
            return f"**{text}**"
        elif self.font_mode == "italic":
            return f"__{text}__"
        return text
    
    def panel_part1(self):
        return f"""
{G}{BOLD}╔════════════════════════════════════════════════════╗{RESET}
{G}{BOLD}║         SUPER BOT v9.0 - MAIN PANEL (1/4)        ║{RESET}
{G}{BOLD}╠════════════════════════════════════════════════════╣{RESET}
{Y}║ [MAIN COMMANDS]                                      ║{RESET}
{Y}║   .set      - Start/Stop auto reply                 ║{RESET}
{Y}║   .add txt  - Add new reply                         ║{RESET}
{Y}║   .list     - Show my replies                       ║{RESET}
{Y}║   .remove n - Remove reply                          ║{RESET}
{Y}║   .clear    - Clear all replies                     ║{RESET}
{Y}║   .interval n - Set speed (1-10)                    ║{RESET}
{Y}║   .font on/off - Enable/Disable bold/italic mode    ║{RESET}
{Y}╠════════════════════════════════════════════════════╣{RESET}
{Y}║ [GAMES]                                             ║{RESET}
{Y}║   .dice    - Roll dice (1-6) +points                ║{RESET}
{Y}║   .coin    - Flip coin +5                           ║{RESET}
{Y}║   .slot    - Slot machine (JACKPOT 100)             ║{RESET}
{Y}║   .love    - Love animation (30 steps)              ║{RESET}
{Y}║   .rps rock/paper/scissors - Play RPS               ║{RESET}
{Y}║   .blackjack - Blackjack game                       ║{RESET}
{Y}║   .cards   - Draw random card                       ║{RESET}
{G}{BOLD}╚════════════════════════════════════════════════════╝{RESET}
"""
    
    def panel_part2(self):
        return f"""
{G}{BOLD}╔════════════════════════════════════════════════════╗{RESET}
{G}{BOLD}║         SUPER BOT v9.0 - MAIN PANEL (2/4)        ║{RESET}
{G}{BOLD}╠════════════════════════════════════════════════════╣{RESET}
{Y}║ [ECONOMY]                                            ║{RESET}
{Y}║   .work     - Work for money (50-200)                ║{RESET}
{Y}║   .daily    - Daily reward (100-500)                 ║{RESET}
{Y}║   .money    - Check balance                          ║{RESET}
{Y}║   .score    - Check points                           ║{RESET}
{Y}║   .top      - Top 10 players                         ║{RESET}
{Y}║   .transfer @user amt - Send money                   ║{RESET}
{Y}║   .rob @user - Rob other player                      ║{RESET}
{Y}║   .bank     - Bank info                              ║{RESET}
{Y}║   .deposit amt - Deposit to bank                     ║{RESET}
{Y}║   .withdraw amt - Withdraw from bank                 ║{RESET}
{Y}║   .loan amt - Take loan (max 10000)                  ║{RESET}
{Y}║   .pay      - Pay loan back                          ║{RESET}
{Y}║   .shop     - Show shop items                        ║{RESET}
{Y}║   .buy item - Buy from shop                          ║{RESET}
{Y}║   .invest amt - Invest money for profit              ║{RESET}
{Y}║   .stock    - Stock market simulator                 ║{RESET}
{G}{BOLD}╚════════════════════════════════════════════════════╝{RESET}
"""
    
    def panel_part3(self):
        return f"""
{G}{BOLD}╔════════════════════════════════════════════════════╗{RESET}
{G}{BOLD}║         SUPER BOT v9.0 - MAIN PANEL (3/4)        ║{RESET}
{G}{BOLD}╠════════════════════════════════════════════════════╣{RESET}
{Y}║ [WEAPONS & BATTLE]                                   ║{RESET}
{Y}║   .weapons - Show weapons list                       ║{RESET}
{Y}║   .buygun gun - Buy weapon                           ║{RESET}
{Y}║   .shoot @user - Shoot other player                  ║{RESET}
{Y}║   .duel @user - Challenge someone to duel            ║{RESET}
{Y}║   .attack @user - Attack other player                ║{RESET}
{Y}║   .defend   - Defend against attacks                 ║{RESET}
{Y}║   .heal     - Heal yourself                          ║{RESET}
{Y}║   .armor    - Buy armor                              ║{RESET}
{Y}╠════════════════════════════════════════════════════╣{RESET}
{Y}║ [MISSIONS & ACHIEVEMENTS]                           ║{RESET}
{Y}║   .mission - Show current missions                   ║{RESET}
{Y}║   .achievements - Show unlocked achievements         ║{RESET}
{Y}║   .dailyquest - Daily quest rewards                  ║{RESET}
{Y}║   .weeklyquest - Weekly quest rewards                ║{RESET}
{Y}║   .event   - Special event info                      ║{RESET}
{G}{BOLD}╚════════════════════════════════════════════════════╝{RESET}
"""
    
    def panel_part4(self):
        return f"""
{G}{BOLD}╔════════════════════════════════════════════════════╗{RESET}
{G}{BOLD}║         SUPER BOT v9.0 - MAIN PANEL (4/4)        ║{RESET}
{G}{BOLD}╠════════════════════════════════════════════════════╣{RESET}
{Y}║ [TOOLS]                                               ║{RESET}
{Y}║   .time    - Current date & time                      ║{RESET}
{Y}║   .id      - Chat ID                                  ║{RESET}
{Y}║   .ping    - Bot response time                        ║{RESET}
{Y}║   .stats   - My statistics                            ║{RESET}
{Y}║   .status  - Bot status                               ║{RESET}
{Y}║   .info    - Bot info                                 ║{RESET}
{Y}║   .calc 2+2 - Calculator                              ║{RESET}
{Y}║   .reverse text - Reverse text                        ║{RESET}
{Y}║   .quote   - Random quote                             ║{RESET}
{Y}║   .joke    - Random joke                              ║{RESET}
{Y}║   .fact    - Random fact                              ║{RESET}
{Y}║   .fortune - Random fortune                           ║{RESET}
{Y}║   .weather - Weather info                             ║{RESET}
{Y}║   .translate text - Translate to English              ║{RESET}
{Y}║   .quran   - Random Quran verse                       ║{RESET}
{Y}║   .hadith  - Random Hadith                            ║{RESET}
{Y}╠════════════════════════════════════════════════════╣{RESET}
{Y}║ [ADMIN]                                               ║{RESET}
{Y}║   .warn @user - Warn user                             ║{RESET}
{Y}║   .ban @user  - Ban user                              ║{RESET}
{Y}║   .unban @user - Unban user                           ║{RESET}
{Y}║   .mute @user - Mute user                             ║{RESET}
{Y}║   .kick @user - Kick user                             ║{RESET}
{G}{BOLD}╚════════════════════════════════════════════════════╝{RESET}
"""
    
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
                xp INTEGER DEFAULT 0,
                bank INTEGER DEFAULT 0,
                bank_time INTEGER DEFAULT 0,
                daily TEXT,
                warns INTEGER DEFAULT 0,
                is_banned INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0,
                created_at TEXT,
                last_seen TEXT,
                hp INTEGER DEFAULT 100,
                armor INTEGER DEFAULT 0,
                weapon TEXT,
                kills INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                win_streak INTEGER DEFAULT 0,
                total_games INTEGER DEFAULT 0,
                total_shots INTEGER DEFAULT 0,
                total_hits INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                item_name TEXT,
                quantity INTEGER DEFAULT 1,
                UNIQUE(user_id, item_name)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS weapons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                weapon_name TEXT,
                damage INTEGER,
                durability INTEGER DEFAULT 100,
                UNIQUE(user_id, weapon_name)
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
                UNIQUE(user_id, mission_name)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                achievement_name TEXT,
                unlocked_at TEXT,
                UNIQUE(user_id, achievement_name)
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
                paid INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                amount INTEGER,
                invested_at INTEGER,
                profit INTEGER DEFAULT 0,
                claimed INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer TEXT,
                referred TEXT,
                reward_claimed INTEGER DEFAULT 0,
                created_at INTEGER
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS gift_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                reward INTEGER,
                claimed_by TEXT,
                claimed_at INTEGER,
                is_used INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
    
    def init_shop(self):
        self.shop_items = {
            "sword": {"name": "Sword", "price": 500, "damage": 10, "type": "weapon"},
            "bow": {"name": "Bow", "price": 300, "damage": 7, "type": "weapon"},
            "axe": {"name": "Axe", "price": 400, "damage": 8, "type": "weapon"},
            "dagger": {"name": "Dagger", "price": 200, "damage": 5, "type": "weapon"},
            "spear": {"name": "Spear", "price": 600, "damage": 12, "type": "weapon"},
            "hammer": {"name": "Hammer", "price": 700, "damage": 15, "type": "weapon"},
            "shield": {"name": "Shield", "price": 300, "defense": 5, "type": "armor"},
            "helmet": {"name": "Helmet", "price": 200, "defense": 3, "type": "armor"},
            "armor": {"name": "Armor", "price": 500, "defense": 8, "type": "armor"},
            "potion": {"name": "Health Potion", "price": 100, "heal": 50, "type": "consumable"},
            "elixir": {"name": "Elixir", "price": 500, "heal": 100, "type": "consumable"},
            "ring": {"name": "Ring", "price": 1000, "luck": 5, "type": "accessory"},
            "amulet": {"name": "Amulet", "price": 1500, "luck": 10, "type": "accessory"},
            "cape": {"name": "Cape", "price": 800, "speed": 5, "type": "accessory"},
            "boots": {"name": "Boots", "price": 400, "speed": 3, "type": "accessory"},
            "potion_h": {"name": "Health Potion", "price": 100, "heal": 50, "type": "consumable"},
            "potion_m": {"name": "Mana Potion", "price": 80, "mana": 40, "type": "consumable"},
            "potion_s": {"name": "Stamina Potion", "price": 60, "stamina": 30, "type": "consumable"},
            "scroll": {"name": "Magic Scroll", "price": 2000, "magic": 20, "type": "magic"},
            "wand": {"name": "Magic Wand", "price": 2500, "magic": 30, "type": "magic"},
            "staff": {"name": "Magic Staff", "price": 3000, "magic": 40, "type": "magic"},
            "cloak": {"name": "Invisibility Cloak", "price": 5000, "stealth": 25, "type": "special"},
            "boots_s": {"name": "Speed Boots", "price": 1200, "speed": 10, "type": "accessory"},
            "gloves": {"name": "Power Gloves", "price": 800, "strength": 8, "type": "accessory"},
            "belt": {"name": "Belt of Giants", "price": 1500, "strength": 12, "type": "accessory"},
            "necklace": {"name": "Necklace of Wisdom", "price": 1800, "intelligence": 10, "type": "accessory"},
            "crown": {"name": "Crown of Kings", "price": 5000, "all_stats": 15, "type": "special"},
            "shield_d": {"name": "Dragon Shield", "price": 3500, "defense": 20, "type": "armor"},
            "armor_d": {"name": "Dragon Armor", "price": 5000, "defense": 30, "type": "armor"},
            "sword_d": {"name": "Dragon Sword", "price": 4000, "damage": 35, "type": "weapon"},
            "bow_d": {"name": "Dragon Bow", "price": 3500, "damage": 30, "type": "weapon"}
        }
    
    def init_weapons(self):
        self.weapons = {
            "pistol": {"name": "Pistol", "damage": 15, "price": 1000, "ammo": 6, "accuracy": 70},
            "shotgun": {"name": "Shotgun", "damage": 30, "price": 2000, "ammo": 2, "accuracy": 60},
            "rifle": {"name": "Rifle", "damage": 25, "price": 2500, "ammo": 5, "accuracy": 80},
            "sniper": {"name": "Sniper", "damage": 50, "price": 5000, "ammo": 3, "accuracy": 90},
            "minigun": {"name": "Minigun", "damage": 10, "price": 8000, "ammo": 30, "accuracy": 50},
            "rpg": {"name": "RPG", "damage": 100, "price": 15000, "ammo": 1, "accuracy": 40},
            "flamethrower": {"name": "Flamethrower", "damage": 20, "price": 10000, "ammo": 10, "accuracy": 65},
            "laser": {"name": "Laser Gun", "damage": 40, "price": 20000, "ammo": 8, "accuracy": 85},
            "railgun": {"name": "Railgun", "damage": 75, "price": 25000, "ammo": 4, "accuracy": 95},
            "bow_w": {"name": "War Bow", "damage": 35, "price": 12000, "ammo": 10, "accuracy": 75},
            "crossbow": {"name": "Crossbow", "damage": 45, "price": 15000, "ammo": 5, "accuracy": 85},
            "katana": {"name": "Katana", "damage": 55, "price": 18000, "ammo": 0, "accuracy": 80},
            "axe_w": {"name": "Battle Axe", "damage": 60, "price": 20000, "ammo": 0, "accuracy": 70},
            "hammer_w": {"name": "War Hammer", "damage": 65, "price": 22000, "ammo": 0, "accuracy": 65}
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
            {"name": "Daily Player", "desc": "Claim daily reward 7 days", "target": 7, "reward": 700},
            {"name": "Investor", "desc": "Invest 5000 coins", "target": 5000, "reward": 600},
            {"name": "Duelist", "desc": "Win 5 duels", "target": 5, "reward": 800},
            {"name": "Survivor", "desc": "Survive 10 attacks", "target": 10, "reward": 900},
            {"name": "Legends", "desc": "Reach level 10", "target": 10, "reward": 2000},
            {"name": "Collector", "desc": "Buy 10 items from shop", "target": 10, "reward": 500},
            {"name": "Referrer", "desc": "Refer 5 friends", "target": 5, "reward": 1000}
        ]
    
    def init_achievements(self):
        self.achievements_list = [
            "Welcome to the Game", "Level 5 Achieved", "Level 10 Achieved", "Level 20 Achieved",
            "Millionaire Status", "Billionaire Dreams", "Gaming Legend", "Silent Killer",
            "Banking Master", "Helping Hand", "Ultimate Warrior", "Duel Champion",
            "Investment Guru", "Mission Master", "Daily Grinder", "Weapon Collector"
        ]
    
    def init_quotes(self):
        self.quotes = [
            "The only limit is your mind.",
            "Success is not final, failure is not fatal.",
            "Believe you can and you're halfway there.",
            "Dream it. Wish it. Do it.",
            "Stay positive, work hard, make it happen.",
            "Your limitation—it's only your imagination.",
            "Push yourself, because no one else is going to do it for you.",
            "Great things never come from comfort zones.",
            "Don't stop when you're tired. Stop when you're done.",
            "Wake up with determination. Go to bed with satisfaction."
        ]
    
    def init_jokes(self):
        self.jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a fake noodle? An impasta!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a bear with no teeth? A gummy bear!",
            "Why did the math book look so sad? Because it had too many problems.",
            "What do you call a fish wearing a bowtie? So-fish-ticated!"
        ]
    
    def init_facts(self):
        self.facts = [
            "Octopuses have three hearts.",
            "A day on Venus is longer than a year on Venus.",
            "Honey never spoils.",
            "Bananas are berries, but strawberries aren't.",
            "The Eiffel Tower grows taller in summer.",
            "A group of flamingos is called a flamboyance.",
            "Cows have best friends and get stressed when separated.",
            "The shortest war in history lasted 38 minutes."
        ]
    
    def init_fortunes(self):
        self.fortunes = [
            "Great success is coming your way!",
            "Be cautious today, opportunities are hidden.",
            "Love is just around the corner.",
            "Financial gain is in your future.",
            "A new friendship will blossom.",
            "Your hard work will pay off soon.",
            "An unexpected journey awaits you.",
            "Happiness is a choice, choose it today."
        ]
    
    def init_rps_choices(self):
        self.rps_choices = ["rock", "paper", "scissors"]
        self.rps_emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
    
    def init_cards(self):
        self.cards = ["A♠", "2♠", "3♠", "4♠", "5♠", "6♠", "7♠", "8♠", "9♠", "10♠", "J♠", "Q♠", "K♠",
                      "A♥", "2♥", "3♥", "4♥", "5♥", "6♥", "7♥", "8♥", "9♥", "10♥", "J♥", "Q♥", "K♥",
                      "A♣", "2♣", "3♣", "4♣", "5♣", "6♣", "7♣", "8♣", "9♣", "10♣", "J♣", "Q♣", "K♣",
                      "A♦", "2♦", "3♦", "4♦", "5♦", "6♦", "7♦", "8♦", "9♦", "10♦", "J♦", "Q♦", "K♦"]
    
    def init_dice_sides(self):
        self.dice_sides = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    
    def init_slot_symbols(self):
        self.slot_symbols = ["🍒", "🍊", "🍋", "🍉", "⭐", "💎", "7️⃣"]
    
    def init_colors(self):
        self.colors = ["🔴 Red", "🔵 Blue", "🟢 Green", "🟡 Yellow", "🟠 Orange", "🟣 Purple", "⚫ Black", "⚪ White"]
    
    def init_animals(self):
        self.animals = ["🐶 Dog", "🐱 Cat", "🐭 Mouse", "🐹 Hamster", "🐰 Rabbit", "🦊 Fox", "🐻 Bear", "🐼 Panda"]
    
    def init_cities(self):
        self.cities = ["Tehran", "Mashhad", "Isfahan", "Tabriz", "Shiraz", "Qom", "Ahvaz", "Karaj"]
    
    def init_foods(self):
        self.foods = ["Pizza", "Burger", "Sushi", "Pasta", "Salad", "Soup", "Steak", "Fries"]
    
    def init_jobs(self):
        self.jobs = ["Programmer", "Designer", "Writer", "Teacher", "Doctor", "Engineer", "Artist", "Musician"]
    
    def init_skills(self):
        self.skills = ["Coding", "Designing", "Writing", "Teaching", "Healing", "Building", "Creating", "Playing"]
    
    def init_titles(self):
        self.titles = ["Novice", "Apprentice", "Journeyman", "Expert", "Master", "Grandmaster", "Legend", "Mythic"]
    
    def init_badges(self):
        self.badges = ["🥇 Gold", "🥈 Silver", "🥉 Bronze", "🏅 Champion", "⭐ Star", "💎 Diamond", "👑 Crown", "🏆 Trophy"]
    
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
            self.money = 1000
            self.scores = 0
            self.level = 1
            self.xp = 0
            self.bank = 0
            self.bank_time = 0
            self.hp = 100
            self.armor = 0
            self.weapon = None
            self.kills = 0
            self.deaths = 0
            self.win_streak = 0
            self.total_games = 0
            self.total_shots = 0
            self.total_hits = 0
        else:
            self.money = result[2]
            self.scores = result[3]
            self.level = result[4]
            self.xp = result[5]
            self.bank = result[6]
            self.bank_time = result[7]
            self.hp = result[15] if len(result) > 15 else 100
            self.armor = result[16] if len(result) > 16 else 0
            self.weapon = result[17] if len(result) > 17 else None
            self.kills = result[18] if len(result) > 18 else 0
            self.deaths = result[19] if len(result) > 19 else 0
            self.win_streak = result[20] if len(result) > 20 else 0
            self.total_games = result[21] if len(result) > 21 else 0
            self.total_shots = result[22] if len(result) > 22 else 0
            self.total_hits = result[23] if len(result) > 23 else 0
        
        self.replies = []
        data_file = f"{self.user_folder}/replies.json"
        if os.path.exists(data_file):
            with open(data_file, "r") as f:
                self.replies = json.load(f)
    
    def save_data(self):
        user_id = USER_ID
        self.cursor.execute('''
            UPDATE users SET money=?, score=?, level=?, xp=?, bank=?, bank_time=?, last_seen=?, 
            hp=?, armor=?, weapon=?, kills=?, deaths=?, win_streak=?, total_games=?, total_shots=?, total_hits=?
            WHERE user_id = ?
        ''', (self.money, self.scores, self.level, self.xp, self.bank, self.bank_time, 
              datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.hp, self.armor, self.weapon,
              self.kills, self.deaths, self.win_streak, self.total_games, self.total_shots, self.total_hits, user_id))
        self.conn.commit()
        
        data_file = f"{self.user_folder}/replies.json"
        with open(data_file, "w") as f:
            json.dump(self.replies, f, indent=2)
    
    def upload_to_host(self):
        try:
            data_file = f"{self.user_folder}/replies.json"
            if os.path.exists(data_file):
                with open(data_file, "r") as f:
                    content = f.read()
                if upload_data(f"{USER_ID}/replies.json", content):
                    print(f"{G}[UPLOAD] Replies synced to host at {datetime.now().strftime('%H:%M:%S')}{RESET}")
                else:
                    print(f"{R}[UPLOAD] Failed to sync replies{RESET}")
            
            self.cursor.execute("SELECT money, score, level, bank, hp, armor, kills, deaths, win_streak FROM users WHERE user_id = ?", (USER_ID,))
            user_data = self.cursor.fetchone()
            if user_data:
                if upload_data(f"{USER_ID}/user.json", json.dumps({
                    "money": user_data[0], "score": user_data[1], "level": user_data[2], 
                    "bank": user_data[3], "hp": user_data[4], "armor": user_data[5],
                    "kills": user_data[6], "deaths": user_data[7], "win_streak": user_data[8]
                })):
                    print(f"{G}[UPLOAD] User data synced to host at {datetime.now().strftime('%H:%M:%S')}{RESET}")
                else:
                    print(f"{R}[UPLOAD] Failed to sync user data{RESET}")
        except Exception as e:
            print(f"{R}[UPLOAD] Error: {e}{RESET}")
    
    def auto_upload(self):
        while True:
            time.sleep(BACKUP_INTERVAL)
            self.upload_to_host()
    
    def auto_save(self):
        while True:
            time.sleep(10)
            self.save_data()
    
    def auto_bank_interest(self):
        while True:
            time.sleep(3600)
            if self.bank > 0 and self.bank_time > 0:
                hours = (time.time() - self.bank_time) / 3600
                interest = int(self.bank * 0.05 * hours)
                if interest > 0:
                    self.bank += interest
                    self.save_data()
                    print(f"{G}[BANK] Interest added: +{interest} coins{RESET}")
    
    def auto_mission_check(self):
        while True:
            time.sleep(300)
            self.check_missions()
    
    def auto_reminder(self):
        while True:
            time.sleep(3600)
            print(f"{C}[REMINDER] Don't forget to claim your daily reward! Use .daily{RESET}")
    
    def auto_weather_update(self):
        while True:
            time.sleep(7200)
            print(f"{C}[WEATHER] Weather info updated! Use .weather{RESET}")
    
    def auto_cleanup(self):
        while True:
            time.sleep(86400)
            self.cursor.execute("DELETE FROM loans WHERE paid = 1 AND taken_at < ?", (int(time.time()) - 604800,))
            self.conn.commit()
            print(f"{G}[CLEANUP] Old loan records removed{RESET}")
    
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
                print(f"{G}[MISSION] {name} completed! +{reward} coins{RESET}")
    
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
                self.send(chat_id, self.panel_part1())
                time.sleep(0.5)
                self.send(chat_id, self.panel_part2())
                time.sleep(0.5)
                self.send(chat_id, self.panel_part3())
                time.sleep(0.5)
                self.send(chat_id, self.panel_part4())
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
                self.send(chat_id, f"{G}[FONT] Current mode: {self.font_mode}{RESET}\n{G}Usage: .font on (bold) | .font italic | .font off{RESET}")
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
                points = 10 if dice == 6 else dice
                self.scores += points
                self.money += points
                self.total_games += 1
                self.save_data()
                self.add_mission_progress("Gambler")
                self.send(chat_id, f"{C}[DICE] {dice} {self.dice_sides[dice-1]}{RESET}\n{G}+{points} coins | Total: {self.scores}{RESET}")
                return
            
            # Coin flip
            if text == ".coin":
                coin = random.choice(["HEAD", "TAIL"])
                self.scores += 5
                self.money += 5
                self.total_games += 1
                self.save_data()
                self.send(chat_id, f"{C}[COIN] {coin} 🪙{RESET}\n{G}+5 coins | Total: {self.scores}{RESET}")
                return
            
            # Slot machine
            if text == ".slot":
                result = [random.choice(self.slot_symbols) for _ in range(3)]
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
                    self.total_games += 1
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
            
            # Blackjack
            if text == ".blackjack":
                if self.money < 50:
                    self.send(chat_id, f"{R}[!] Need at least 50 coins!{RESET}")
                    return
                
                bet = min(50, self.money)
                self.money -= bet
                
                player_cards = [random.choice(self.cards[:10]), random.choice(self.cards[:10])]
                dealer_cards = [random.choice(self.cards[:10]), random.choice(self.cards[:10])]
                
                player_sum = sum([int(c.split('♠')[0].split('♥')[0].split('♣')[0].split('♦')[0].replace('A','1').replace('J','10').replace('Q','10').replace('K','10') for c in player_cards])
                dealer_sum = sum([int(c.split('♠')[0].split('♥')[0].split('♣')[0].split('♦')[0].replace('A','1').replace('J','10').replace('Q','10').replace('K','10') for c in dealer_cards])
                
                if player_sum == 21:
                    win_amount = bet * 2
                    self.money += win_amount
                    result = f"{G}BLACKJACK! You win! +{win_amount}{RESET}"
                elif player_sum > 21:
                    result = f"{R}BUST! You lose! -{bet}{RESET}"
                else:
                    if dealer_sum > 21 or player_sum > dealer_sum:
                        win_amount = bet * 2
                        self.money += win_amount
                        result = f"{G}You win! +{win_amount}{RESET}"
                    elif player_sum < dealer_sum:
                        result = f"{R}You lose! -{bet}{RESET}"
                    else:
                        self.money += bet
                        result = f"{Y}Push! Bet returned{RESET}"
                
                self.total_games += 1
                self.save_data()
                self.send(chat_id, f"{C}Your cards: {' '.join(player_cards)} = {player_sum}{RESET}\n{C}Dealer cards: {dealer_cards[0]} + ?{RESET}\n{result}\n{G}Balance: {self.money}{RESET}")
                return
            
            # Cards
            if text == ".cards":
                card = random.choice(self.cards)
                self.send(chat_id, f"{C}[CARDS] You drew: {card}{RESET}")
                return
            
            # Rock Paper Scissors
            if text.startswith(".rps "):
                parts = text[5:].split()
                if len(parts) < 1:
                    self.send(chat_id, f"{R}Usage: .rps rock/paper/scissors [amount]{RESET}")
                    return
                
                choice = parts[0].lower()
                try:
                    bet = int(parts[1]) if len(parts) > 1 else 10
                except:
                    bet = 10
                
                if bet > self.money:
                    self.send(chat_id, f"{R}[!] Not enough money! You have {self.money}{RESET}")
                    return
                
                if choice not in self.rps_choices:
                    self.send(chat_id, f"{R}[!] Invalid choice! Use: rock, paper, scissors{RESET}")
                    return
                
                bot_choice = random.choice(self.rps_choices)
                
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
                    self.win_streak += 1
                    self.add_mission_progress("Gambler")
                else:
                    result = "LOSE"
                    win_amount = -bet
                    self.money -= bet
                    self.win_streak = 0
                
                self.total_games += 1
                self.save_data()
                self.send(chat_id, f"{C}You: {self.rps_emojis[choice]} | Bot: {self.rps_emojis[bot_choice]}{RESET}\n{Y}[{result}]{RESET}\n{G}{'+' if win_amount > 0 else ''}{win_amount} coins | Streak: {self.win_streak}{RESET}\n{G}Balance: {self.money}{RESET}")
                return
            
            # Work
            if text == ".work":
                earnings = random.randint(50, 200)
                self.money += earnings
                self.xp += 10
                self.add_mission_progress("Rich Begins", earnings)
                self.save_data()
                
                if self.xp >= self.level * 100:
                    self.xp -= self.level * 100
                    self.level += 1
                    self.send(chat_id, f"{Y}[LEVEL UP] Congratulations! You reached level {self.level}!{RESET}")
                
                job = random.choice(self.jobs)
                self.send(chat_id, f"{G}[WORK] {job}{RESET}\n{G}+{earnings} coins | +10 XP{RESET}\n{G}Level: {self.level} | XP: {self.xp}/{self.level*100}{RESET}\n{G}Balance: {self.money}{RESET}")
                return
            
            # Daily reward
            if text == ".daily":
                today = datetime.now().strftime("%Y%m%d")
                if hasattr(self, 'daily') and self.daily == today:
                    self.send(chat_id, f"{R}[!] Already claimed today! Come back tomorrow{RESET}")
                    return
                
                reward = random.randint(100, 500)
                self.money += reward
                self.daily = today
                self.add_mission_progress("Daily Player")
                self.save_data()
                self.send(chat_id, f"{G}[DAILY] +{reward} coins{RESET}\n{G}Balance: {self.money}{RESET}")
                return
            
            # Money
            if text == ".money":
                self.send(chat_id, f"{G}[BALANCE] {self.money} coins{RESET}")
                return
            
            # Score
            if text == ".score":
                self.send(chat_id, f"{G}[SCORE] {self.scores} points{RESET}")
                return
            
            # Top players
            if text == ".top":
                self.cursor.execute("SELECT username, money, level FROM users ORDER BY money DESC LIMIT 10")
                top = self.cursor.fetchall()
                if not top:
                    self.send(chat_id, f"{R}[!] No players yet{RESET}")
                    return
                txt = f"{G}[TOP 10 PLAYERS BY MONEY]{RESET}\n"
                for i, (name, money, level) in enumerate(top, 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                    txt += f"{medal} {name[:15]}... - {money} coins (Lv.{level}){RESET}\n"
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
            
            # Rob
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
            
            # Bank
            if text == ".bank":
                self.send(chat_id, f"{G}[BANK] Deposit: {self.bank} coins{RESET}\n{G}Interest rate: 5% per hour{RESET}")
                return
            
            # Deposit
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
            
            # Withdraw
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
            
            # Loan
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
                    shop_text += f"{C}{data['name']}{RESET} - {data['price']} coins [{data['type']}]\n"
                self.send(chat_id, shop_text)
                return
            
            # Buy
            if text.startswith(".buy "):
                item = text[5:].strip().lower()
                if item in self.shop_items:
                    price = self.shop_items[item]["price"]
                    if self.money >= price:
                        self.money -= price
                        self.save_data()
                        self.cursor.execute('''
                            INSERT OR IGNORE INTO inventory (user_id, item_name, quantity)
                            VALUES (?, ?, 1)
                        ''', (USER_ID, self.shop_items[item]["name"]))
                        self.cursor.execute('''
                            UPDATE inventory SET quantity = quantity + 1 WHERE user_id = ? AND item_name = ?
                        ''', (USER_ID, self.shop_items[item]["name"]))
                        self.conn.commit()
                        self.send(chat_id, f"{G}[BOUGHT] {self.shop_items[item]['name']}{RESET}\n{G}-{price} coins{RESET}")
                    else:
                        self.send(chat_id, f"{R}[!] Need {price} coins!{RESET}")
                else:
                    self.send(chat_id, f"{R}[!] Item not found! Use .shop{RESET}")
                return
            
            # Invest
            if text.startswith(".invest "):
                try:
                    amount = int(text[8:])
                    if amount > self.money:
                        self.send(chat_id, f"{R}[!] Not enough money!{RESET}")
                        return
                    if amount < 100:
                        self.send(chat_id, f"{R}[!] Minimum investment is 100 coins!{RESET}")
                        return
                    
                    self.money -= amount
                    profit = int(amount * random.uniform(0.05, 0.3))
                    self.cursor.execute('''
                        INSERT INTO investments (user_id, amount, invested_at, profit)
                        VALUES (?, ?, ?, ?)
                    ''', (USER_ID, amount, int(time.time()), profit))
                    self.conn.commit()
                    self.save_data()
                    self.send(chat_id, f"{G}[INVEST] +{amount} coins invested{RESET}\n{G}Expected profit: +{profit} coins in 24h{RESET}")
                except:
                    self.send(chat_id, f"{R}Usage: .invest amount{RESET}")
                return
            
            # Stock market
            if text == ".stock":
                stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NFLX"]
                prices = [random.randint(100, 1000) for _ in stocks]
                stock_text = f"{G}[STOCK MARKET]{RESET}\n"
                for i, stock in enumerate(stocks):
                    change = random.choice(["↑", "↓", "→"])
                    stock_text += f"{C}{stock}{RESET}: ${prices[i]} {change}\n"
                self.send(chat_id, stock_text)
                return
            
            # Weapons
            if text == ".weapons":
                weapons_text = f"{G}[WEAPONS]{RESET}\n"
                for gun, data in self.weapons.items():
                    weapons_text += f"{C}{data['name']}{RESET} - Dmg:{data['damage']} Price:{data['price']} Acc:{data['accuracy']}%\n"
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
                            INSERT OR IGNORE INTO weapons (user_id, weapon_name, damage)
                            VALUES (?, ?, ?)
                        ''', (USER_ID, self.weapons[gun]["name"], self.weapons[gun]["damage"]))
                        self.conn.commit()
                        self.add_mission_progress("Weapon Master")
                        self.send(chat_id, f"{G}[BOUGHT] {self.weapons[gun]['name']}{RESET}\n{G}-{price} coins | Damage: {self.weapons[gun]['damage']}{RESET}")
                    else:
                        self.send(chat_id, f"{R}[!] Need {price} coins!{RESET}")
                else:
                    self.send(chat_id, f"{R}[!] Weapon not found! Use .weapons{RESET}")
                return
            
            # Shoot
            if text.startswith(".shoot "):
                target = text[7:].strip().replace("@", "")
                self.cursor.execute("SELECT weapon_name, damage FROM weapons WHERE user_id = ?", (USER_ID,))
                weapon = self.cursor.fetchone()
                if not weapon:
                    self.send(chat_id, f"{R}[!] You don't have a weapon! Buy one with .buygun{RESET}")
                    return
                
                self.total_shots += 1
                accuracy = random.randint(1, 100)
                hit = accuracy <= self.weapons[weapon[0].lower()]["accuracy"] if weapon[0].lower() in self.weapons else 70
                
                if hit:
                    damage = weapon[1]
                    self.total_hits += 1
                    self.add_mission_progress("Sharp Shooter")
                    self.send(chat_id, f"{G}[SHOOT] Hit! {damage} damage to {target} (Accuracy: {accuracy}%){RESET}")
                else:
                    self.send(chat_id, f"{R}[SHOOT] Missed! (Accuracy: {accuracy}%){RESET}")
                
                self.save_data()
                return
            
            # Duel
            if text.startswith(".duel "):
                target = text[6:].strip().replace("@", "")
                self.send(chat_id, f"{G}[DUEL] Duel challenge sent to {target}!{RESET}\n{Y}They must accept with .accept{RESET}")
                return
            
            # Heal
            if text == ".heal":
                if self.hp >= 100:
                    self.send(chat_id, f"{R}[!] You already have full HP!{RESET}")
                    return
                
                cost = (100 - self.hp) * 2
                if self.money < cost:
                    self.send(chat_id, f"{R}[!] Need {cost} coins to heal!{RESET}")
                    return
                
                self.money -= cost
                self.hp = 100
                self.save_data()
                self.send(chat_id, f"{G}[HEAL] HP restored to 100! -{cost} coins{RESET}")
                return
            
            # Armor
            if text == ".armor":
                if self.armor >= 50:
                    self.send(chat_id, f"{R}[!] You already have max armor (50)!{RESET}")
                    return
                
                cost = 100
                if self.money < cost:
                    self.send(chat_id, f"{R}[!] Need {cost} coins to buy armor!{RESET}")
                    return
                
                self.money -= cost
                self.armor = min(50, self.armor + 10)
                self.save_data()
                self.send(chat_id, f"{G}[ARMOR] Armor increased to {self.armor}! -{cost} coins{RESET}")
                return
            
            # Missions
            if text == ".mission":
                self.cursor.execute("SELECT mission_name, progress, target, reward, completed FROM missions WHERE user_id = ?", (USER_ID,))
                missions = self.cursor.fetchall()
                
                if not missions:
                    for m in self.missions_list[:8]:
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
                        missions_text += f"{G}✅ {name} - COMPLETED (+{reward}){RESET}\n"
                    else:
                        percent = int((prog / target) * 100) if target > 0 else 0
                        bar = "█" * (percent // 10) + "░" * (10 - (percent // 10))
                        missions_text += f"{Y}📌 {name}: {bar} {prog}/{target} - Reward: {reward}{RESET}\n"
                
                self.send(chat_id, missions_text)
                return
            
            # Achievements
            if text == ".achievements":
                self.cursor.execute("SELECT achievement_name FROM achievements WHERE user_id = ?", (USER_ID,))
                achievements = self.cursor.fetchall()
                
                if self.level >= 2:
                    self.add_achievement("Level 2 Achieved")
                if self.level >= 5:
                    self.add_achievement("Level 5 Achieved")
                if self.money >= 10000:
                    self.add_achievement("Millionaire")
                if self.scores >= 1000:
                    self.add_achievement("Points Master")
                
                self.cursor.execute("SELECT achievement_name FROM achievements WHERE user_id = ?", (USER_ID,))
                achievements = self.cursor.fetchall()
                
                if achievements:
                    ach_text = f"{G}[ACHIEVEMENTS] {len(achievements)} unlocked{RESET}\n"
                    for ach in achievements[:15]:
                        ach_text += f"{C}🏆 {ach[0]}{RESET}\n"
                else:
                    ach_text = f"{Y}[ACHIEVEMENTS] No achievements yet! Keep playing!{RESET}"
                
                self.send(chat_id, ach_text)
                return
            
            # Stats
            if text == ".stats":
                level = self.scores // 100 + 1
                win_rate = (self.win_streak / max(1, self.total_games)) * 100
                accuracy = (self.total_hits / max(1, self.total_shots)) * 100
                stats_text = f"""
{G}[MY STATS]{RESET}
  Level: {self.level}
  XP: {self.xp}/{self.level*100}
  Points: {self.scores}
  Money: {self.money}
  Bank: {self.bank}
  Replies: {len(self.replies)}
  HP: {self.hp}/100
  Armor: {self.armor}/50
  Weapon: {self.weapon or 'None'}
  Kills: {self.kills}
  Deaths: {self.deaths}
  Win Streak: {self.win_streak}
  Win Rate: {win_rate:.1f}%
  Accuracy: {accuracy:.1f}%
"""
                self.send(chat_id, stats_text)
                return
            
            # Time
            if text == ".time":
                now = datetime.now()
                self.send(chat_id, f"{C}[TIME] {now.strftime('%Y-%m-%d %H:%M:%S')}{RESET}\n{C}Weekday: {now.strftime('%A')}{RESET}\n{C}Week: {now.isocalendar()[1]}{RESET}")
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
  Level: {self.level}
  Bank: {self.bank}
  HP: {self.hp}
  Armor: {self.armor}
  Interval: {self.interval}s
  Uptime: {uptime}
  Backup: Every {BACKUP_INTERVAL}s
"""
                self.send(chat_id, status_text)
                return
            
            # Info
            if text == ".info":
                info_text = f"""
{G}[BOT INFO]{RESET}
  Name: SUPER BOT v9.0
  Author: RTC Team
  Commands: 120+
  Database: SQLite + JSON
  Backup: kaizofil.ir ({BACKUP_INTERVAL}s)
  Features:
    - Games & Gambling
    - Economy & Banking
    - Weapons & Battles
    - Missions & Achievements
    - Referral System
    - Investment System
    - Stock Market
    - And more!
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
            
            # Reverse
            if text.startswith(".reverse "):
                reverse_text = text[9:][::-1]
                self.send(chat_id, f"{C}[REVERSE] {reverse_text}{RESET}")
                return
            
            # Quote
            if text == ".quote":
                self.send(chat_id, f"{C}[QUOTE] {random.choice(self.quotes)}{RESET}")
                return
            
            # Joke
            if text == ".joke":
                self.send(chat_id, f"{C}[JOKE] {random.choice(self.jokes)}{RESET}")
                return
            
            # Fact
            if text == ".fact":
                self.send(chat_id, f"{C}[FACT] {random.choice(self.facts)}{RESET}")
                return
            
            # Fortune
            if text == ".fortune":
                self.send(chat_id, f"{C}[FORTUNE] {random.choice(self.fortunes)}{RESET}")
                return
            
            # Weather
            if text == ".weather":
                weathers = ["☀️ Sunny 28°C", "⛅ Partly Cloudy 22°C", "🌧️ Rainy 18°C", "❄️ Snowy -5°C", "🌪️ Stormy 15°C"]
                self.send(chat_id, f"{C}[WEATHER] {random.choice(weathers)}{RESET}")
                return
            
            # Translate
            if text.startswith(".translate "):
                translate_text = text[11:].strip()
                self.send(chat_id, f"{C}[TRANSLATE] {translate_text} (English){RESET}")
                return
            
            # Quran
            if text == ".quran":
                verses = ["بسم الله الرحمن الرحیم", "الله لا اله الا هو الحی القیوم", "ان مع العسر یسرا"]
                self.send(chat_id, f"{C}[QURAN] {random.choice(verses)}{RESET}")
                return
            
            # Hadith
            if text == ".hadith":
                hadiths = ["الراحمون یرحمهم الرحمن", "طلب العلم فریضة علی کل مسلم", "الجنة تحت اقدام الامهات"]
                self.send(chat_id, f"{C}[HADITH] {random.choice(hadiths)}{RESET}")
                return
            
            # Refer
            if text == ".refer":
                self.send(chat_id, f"{G}[REFER] Your referral code: {USER_ID[:8]}{RESET}\n{G}Share this code with friends!{RESET}")
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
