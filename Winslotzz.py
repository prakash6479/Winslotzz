import telebot
from telebot import types
import sqlite3
import datetime
import random
import string
import os

# --- 1. Configuration (UPDATED) ---
BOT_TOKEN = '8481818955:AAFRdwHiHDB9OnEQ4Sjo7SoMcg60bBvBuhc' # NEW TOKEN
CHANNEL_USERNAME = '@Testing55551' 
ADMIN_USERNAME = '@Fasttaget' 
ADMIN_IDS = [7762779824, 7565458414] # NEW ADMIN IDs
REFERRER_REWARD = 15.00 
REFERRED_BONUS = 5.00   
DB_NAME = 'winslotzz_bot.db' # Updated DB Name

bot = telebot.TeleBot(BOT_TOKEN)

# --- 2. Game Data (Unchanged) ---
GAME_URLS = {
    "ðŸ”¥ FireKirin": "https://start.firekirin.xyz:8580/index.html",
    "âœ¨ MilkyWay": "http://milkywayapp.xyz:8580/index.html",
    "ðŸ’° Moolah": "https://moolah.vip:8888",
    "ðŸŽ° Vegas Roll": "https://www.vegas-roll.com/m",
    "ðŸ’Ž Loot Game": "https://m.lootgame777.com",
    "ðŸ‘‘ RM777": "https://rm777.net",
    "â­ Junva777": "http://dl.juwa777.com/",
    "ðŸš€ Rising Star": "http://risingstar.vip:8580/index.html",
    "ðŸŒŸ Vegas-X": "http://vegas-x.org/",
    "Vault GameVault": "http://download.gamevault999.com",
    "ðŸ¼ PandaMaster": "https://pandamaster.vip:8888/index.html",
    "ðŸ… UltraPanda": "http://www.ultrapanda.mobi/",
    "ðŸƒ HighRollerSweep": "https://highrollersweep.cc",
    "âš™ï¸ MegaSpinSweeps": "https://www.megaspinsweeps.com/index.html",
    "ðŸŒŒ OrionStars": "https://start.orionstars.vip:8580/index.html",
    "ðŸ€ PasaSweeps": "https://pasasweeps.net/",
    "ðŸ•¹ï¸ Vblink777": "https://www.vblink777.club",
    "ðŸŒƒ LasVegasSweeps": "http://m.lasvegassweeps.com/",
    "ðŸŒ€ CashFrenzy": "http://www.cashfrenzy777.com/m",
    "ðŸ  GameRoom777": "https://www.gameroom777.com",
    "ðŸ¤µ Noble777": "http://web.noble777.com:8008/",
}

# ----------------------------------------------------
# --- 3. Database Functions (Unchanged Logic) ---
# ----------------------------------------------------
# (Database functions remain structurally the same)
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            username TEXT,
            join_date TEXT,
            referral_code TEXT UNIQUE,
            referrer_id INTEGER,
            total_deposits REAL DEFAULT 0.0,
            total_referral_earnings REAL DEFAULT 0.0, 
            verified INTEGER DEFAULT 1
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY,
            referrer_id INTEGER,
            referred_id INTEGER UNIQUE,
            reward_amount REAL,
            date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            amount REAL,
            status TEXT, 
            method TEXT,
            request_date TEXT,
            approve_date TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            game_name TEXT,
            click_time TEXT
        )
    ''')
    try:
        c.execute('ALTER TABLE users ADD COLUMN total_referral_earnings REAL DEFAULT 0.0')
    except sqlite3.OperationalError:
        pass 

    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_NAME)

def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def register_user(user_id, username, referrer_id=None):
    conn = get_db_connection()
    c = conn.cursor()
    join_date = datetime.datetime.now().isoformat()
    ref_code = generate_referral_code()

    try:
        c.execute('''
            INSERT INTO users (user_id, username, join_date, referral_code, referrer_id, verified, total_deposits)
            VALUES (?, ?, ?, ?, ?, 1, ?)
        ''', (user_id, username, join_date, ref_code, referrer_id, REFERRED_BONUS if referrer_id else 0.0))
        conn.commit()

        if referrer_id:
            c.execute('''
                INSERT INTO referrals (referrer_id, referred_id, reward_amount, date)
                VALUES (?, ?, ?, ?)
            ''', (referrer_id, user_id, REFERRER_REWARD, join_date))
            
            c.execute('''
                UPDATE users SET total_referral_earnings = total_referral_earnings + ? WHERE user_id = ?
            ''', (REFERRER_REWARD, referrer_id))
            conn.commit()
            
            return True, 'referral_success'
        
        return True, 'success'
    except sqlite3.IntegrityError:
        return False, 'exists'
    finally:
        conn.close()

def get_user(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def get_total_referrals(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM referrals WHERE referrer_id = ?', (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_user_referral_earnings(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT total_referral_earnings FROM users WHERE user_id = ?', (user_id,))
    earnings = c.fetchone()
    conn.close()
    return earnings[0] if earnings else 0.0

def get_all_user_ids():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT user_id FROM users')
    user_ids = [row[0] for row in c.fetchall()]
    conn.close()
    return user_ids

def add_payment_request(user_id, amount, method):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    request_date = datetime.datetime.now().isoformat()
    c.execute('''
        INSERT INTO payments (user_id, amount, status, method, request_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, amount, 'Pending', method, request_date))
    payment_id = c.lastrowid
    conn.commit()
    conn.close()
    return payment_id

def update_payment_status(payment_id, status, user_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    approve_date = datetime.datetime.now().isoformat() if status == 'Approved' else None
    
    c.execute('UPDATE payments SET status = ?, approve_date = ? WHERE id = ?', (status, approve_date, payment_id))
    
    if status == 'Approved':
        c.execute('SELECT amount FROM payments WHERE id = ?', (payment_id,))
        amount = c.fetchone()[0]
        c.execute('UPDATE users SET total_deposits = total_deposits + ? WHERE user_id = ?', (amount, user_id))

    conn.commit()
    conn.close()
# (Other DB functions like get_all_users, get_user_admin_view are omitted for brevity in comment, but should be in the final code)
# ----------------------------------------------------
# --- 4. Keyboard Markup Functions ---
# ----------------------------------------------------

def main_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('ðŸŽ® Games'),
        types.KeyboardButton('ðŸ¤ Refer & Earn'),
        types.KeyboardButton('ðŸ’³ Add Funds'),
        types.KeyboardButton('ðŸ“Š My Stats'),
        types.KeyboardButton('ðŸ”” Join Our Channel'),
        types.KeyboardButton('â“ Help')
    )
    return markup

def games_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for game_name, url in GAME_URLS.items():
        buttons.append(types.InlineKeyboardButton(text=game_name, callback_data=f"game_{game_name}"))
        
    markup.add(*buttons)
    # Changed callback data to specifically signal Edit mode
    markup.add(types.InlineKeyboardButton(text="ðŸ”™ Main Menu", callback_data="back_edit")) 
    return markup

# --- BACK BUTTON MARKUP (Used when we don't want to remove the previous text) ---
def back_to_main_markup_send():
    markup = types.InlineKeyboardMarkup()
    # Changed callback data to specifically signal Send mode
    markup.add(types.InlineKeyboardButton(text="ðŸ”™ Main Menu", callback_data="back_send"))
    return markup

# --- BACK BUTTON MARKUP (Used when we want to remove the previous text) ---
def back_to_main_markup_edit():
    markup = types.InlineKeyboardMarkup()
    # Changed callback data to specifically signal Edit mode
    markup.add(types.InlineKeyboardButton(text="ðŸ”™ Main Menu", callback_data="back_edit"))
    return markup
# ----------------------------------------------------
# --- 5. Core Utility Functions (Updated Text) ---
# ----------------------------------------------------

def send_main_menu(chat_id, text="ðŸš€ **Main Menu** - Choose an option:", reply_markup=None):
    if reply_markup is None:
        reply_markup = main_menu_markup()
    bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=reply_markup)

def send_welcome_message(message):
    text = (
        "ðŸ¥³ **Welcome to Winslotzz Premium Bot!** ðŸ‘‘\n\n" # Updated Text
        "You have full access to our **21 high-payout games** and the **Refer & Earn** program.\n\n"
        "Select an option below to get started!"
    )
    send_main_menu(message.chat.id, text)

# ----------------------------------------------------
# --- 6. User Handlers (Modified Logic for Back Button) ---
# ----------------------------------------------------

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else str(user_id)
    
    referrer_id = None
    if len(message.text.split()) > 1:
        ref_code = message.text.split()[1]
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT user_id FROM users WHERE referral_code = ?', (ref_code,))
        referrer_data = c.fetchone()
        conn.close()
        if referrer_data:
            referrer_id = referrer_data[0]
            
    success, status = register_user(user_id, username, referrer_id)

    if success and status == 'referral_success':
        bot.send_message(user_id, f"ðŸ† **Welcome Bonus!** You received **${REFERRED_BONUS:.2f} USD** for joining via a friend's link! ðŸ¤", parse_mode='Markdown')
        try:
             bot.send_message(referrer_id, f"ðŸŒŸ **Reward Alert!** User `@{username}` joined using your link. You earned **${REFERRER_REWARD:.2f} USD**! ðŸ’°", parse_mode='Markdown')
        except Exception:
             pass 
    elif not success and status == 'exists':
        pass

    send_welcome_message(message)

@bot.message_handler(func=lambda message: message.text in ['ðŸŽ® Games', '/games'])
def handle_games(message):
    # This section uses 'Edit' logic on back button.
    text = "ðŸŽ° **Game Lobby** - Choose your game! ðŸš€\n\n_Click any game to launch its direct URL._"
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=games_markup())

@bot.message_handler(func=lambda message: message.text in ['ðŸ¤ Refer & Earn', '/refer'])
def handle_refer(message):
    # This section uses 'Send' logic on back button (text remains)
    user = get_user(message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "Error: User data not found. Please try /start.")
        return

    referral_code = user[4]
    bot_username = bot.get_me().username
    referral_link = f"https://t.me/{bot_username}?start={referral_code}"
    
    total_refs = get_total_referrals(message.chat.id)
    total_earnings = get_user_referral_earnings(message.chat.id)

    text = (
        "ðŸ¤ **Refer & Earn Program** ðŸ’°\n\n"
        f"Invite friends and earn **${REFERRER_REWARD:.2f} USD** for every successful signup! The referred user also gets a **${REFERRED_BONUS:.2f} USD** bonus!\n\n"
        "ðŸ”— **Your Unique Referral Link:**\n"
        f"`{referral_link}`\n\n"
        f"ðŸ† **Your Referrals:** **{total_refs}** users referred so far!\n"
        f"ðŸ’¸ **Total Referral Earnings:** **${total_earnings:.2f} USD**\n\n"
        "âš ï¸ **WITHDRAWAL NOTICE:** To withdraw your referral earnings, you **must contact the Admin** directly.\n"
        "**Available Withdrawal Methods:** **Chime, Crypto, and USDT.**"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text="ðŸ’¬ Contact Admin for Withdrawal", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")
    )
    markup.add(types.InlineKeyboardButton(text="ðŸ”™ Main Menu", callback_data="back_send")) # Uses back_send
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['ðŸ’³ Add Funds', '/addfunds'])
def handle_add_funds(message):
    # This section uses 'Send' logic on back button (text remains)
    text = (
        "ðŸ’¸ **Deposit Service** 24/7 â°\n\n"
        "To **DEPOSIT** funds, you **must contact the Admin** directly.\n"
        "**Available Deposit Methods:** **Chime, Crypto, and USDT.**\n\n"
        "ðŸ‘‡ **Contact the Admin:**\n"
        f"ðŸ‘‘ **Admin Username:** **{ADMIN_USERNAME}**"
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text="ðŸ’¬ Contact Admin for Deposit", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")
    )
    markup.add(types.InlineKeyboardButton(text="ðŸ”™ Main Menu", callback_data="back_send")) # Uses back_send
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in ['ðŸ“Š My Stats', '/mystats'])
def handle_mystats(message):
    # This section uses 'Edit' logic on back button.
    user = get_user(message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "Error: User data not found. Please try /start.")
        return
        
    user_id = user[1]
    total_deposits = user[6] 
    total_refs = get_total_referrals(user_id)
    total_ref_earnings = get_user_referral_earnings(user_id)
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT game_name, COUNT(*) as count
        FROM clicks
        WHERE user_id = ?
        GROUP BY game_name
        ORDER BY count DESC
    ''', (user_id,))
    click_stats = c.fetchall()
    conn.close()
    
    game_list = "\n".join([f"- **{name.split(' ')[-1]}:** {count} clicks" for name, count in click_stats[:5]])
    if not game_list:
        game_list = "No games played yet."
        
    text = (
        "ðŸ† **Your Personal Stats** ðŸ“Š\n\n"
        f"ðŸ‘¤ **Your ID:** `{user_id}`\n"
        f"ðŸ’° **Total Funds (Deposits + Bonus):** **${total_deposits:.2f} USD**\n"
        f"ðŸ¤ **Referrals Made:** **{total_refs}** users\n"
        f"ðŸ’¸ **Referral Earnings:** **${total_ref_earnings:.2f} USD**\n\n"
        "ðŸ”¥ **Your Top 5 Games:**\n"
        f"{game_list}\n\n"
        "**Action Required:**\n"
        f"To **deposit or withdraw**, contact Admin: **{ADMIN_USERNAME}**\n"
        "**Available Methods:** **Chime, Crypto, and USDT.**"
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=back_to_main_markup_edit()) # Uses back_edit

@bot.message_handler(func=lambda message: message.text == 'ðŸ”” Join Our Channel')
def handle_join_channel(message):
    # This section uses 'Send' logic on back button (text remains)
    if CHANNEL_USERNAME:
        text = (
            "ðŸ“¢ **Official Channel** ðŸ‘‘\n\n"
            "All the latest news, updates, and major announcements are posted here.\n\n"
            "ðŸ‘‡ **Click to Join:**"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(text="Join Now! ðŸš€", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")
        )
        markup.add(types.InlineKeyboardButton(text="ðŸ”™ Main Menu", callback_data="back_send")) # Uses back_send
        
        bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Error: Channel link is not configured by the admin.", reply_markup=back_to_main_markup_send())

@bot.message_handler(func=lambda message: message.text in ['â“ Help', '/help'])
def handle_help(message):
    # This section uses 'Edit' logic on back button.
    text = (
        "â“ **Help & Guide**\n\n"
        "Here are the main commands and features:\n\n"
        "1. **ðŸŽ® Games** (`/games`): Access the 21 direct-URL games.\n"
        "2. **ðŸ¤ Refer & Earn** (`/refer`): Get your unique link and earn rewards.\n"
        "3. **ðŸ’³ Add Funds** (`/addfunds`): *Contact the Admin* for instant fund deposit.\n"
        "4. **ðŸ“Š My Stats** (`/mystats`): View your deposits, referrals, and top games.\n"
        "5. **ðŸ”” Join Our Channel**: See the latest updates and news.\n"
        f"6. **Admin Support:** For issues, queries, or **Deposit/Withdrawal**, contact our Admin: **{ADMIN_USERNAME}**.\n\n"
        "**Payment Methods:** **Chime, Crypto, and USDT.**\n\n"
        "Thank you for being a **Winslotzz Premium** member! ðŸ‘‘" # Updated Text
    )
    bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=back_to_main_markup_edit()) # Uses back_edit
    
@bot.callback_query_handler(func=lambda call: call.data.startswith('game_'))
def handle_game_click(call):
    game_name_full = call.data[5:]
    user_id = call.from_user.id
    
    conn = get_db_connection()
    c = conn.cursor()
    click_time = datetime.datetime.now().isoformat()
    c.execute('''
        INSERT INTO clicks (user_id, game_name, click_time)
        VALUES (?, ?, ?)
    ''', (user_id, game_name_full, click_time))
    conn.commit()
    conn.close()
    
    url = GAME_URLS.get(game_name_full, "https://example.com/error")
    
    alert_text = f"ðŸ”¥ Launching **{game_name_full.split(' ')[-1]}**! Good luck! ðŸš€"
    
    bot.answer_callback_query(
        callback_query_id=call.id, 
        text=alert_text, 
        show_alert=True
    )
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=f"â–¶ï¸ Go to {game_name_full}", url=url))
    # This button always edits the message back to the game list
    markup.add(types.InlineKeyboardButton(text="ðŸ”™ Back to Games", callback_data="back_games_menu_edit")) 
    
    bot.send_message(call.message.chat.id, 
                     f"**{game_name_full}** is ready! Tap the button below to play:", 
                     parse_mode='Markdown',
                     reply_markup=markup)

# --- NEW CALLBACK HANDLER FOR BACK BUTTONS ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('back_'))
def handle_back_buttons(call):
    chat_id = call.message.chat.id
    action = call.data[5:]
    
    bot.answer_callback_query(call.id)
    
    text = "ðŸš€ **Main Menu** - Choose an option:"
    
    if action == 'send':
        # Send New Message logic: Main Menu will appear below the previous message
        send_main_menu(chat_id, text)
        
    elif action == 'edit':
        # Edit Message logic: Previous message text/buttons are removed and replaced by Main Menu
        try:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=main_menu_markup() # Main menu uses ReplyKeyboard, so we send a new one
            )
        except Exception:
            # Fallback if message cannot be edited (e.g., already edited)
            send_main_menu(chat_id, text)
            
    elif action == 'games_menu_edit':
        # Back to Games Menu logic (uses Edit)
        text = "ðŸŽ° **Game Lobby** - Choose your game! ðŸš€\n\n_Click any game to launch its direct URL._"
        try:
             bot.edit_message_text(
                chat_id=chat_id,
                message_id=call.message.message_id,
                text=text,
                parse_mode='Markdown',
                reply_markup=games_markup()
            )
        except Exception:
            bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=games_markup())

# ----------------------------------------------------
# --- 7. Admin Handlers (Minor Text Update) ---
# ----------------------------------------------------

# (Admin Handlers remain structurally the same, but GameHub is replaced with Winslotzz in notifications)
# ...

# ----------------------------------------------------
# --- 8. Main Execution ---
# ----------------------------------------------------

if __name__ == '__main__':
    print("Initializing Database...")
    init_db()
    print("Database Initialized. Starting Bot Polling...")
    try:
        bot.delete_webhook() 
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An unexpected error occurred during polling: {e}")