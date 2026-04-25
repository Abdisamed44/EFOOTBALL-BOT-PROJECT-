import os

def load_env():
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

load_env()


import logging
import asyncio
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from telegram.ext import CommandHandler
import inspect
#print("RUNNING FILE:", __file__)

#print("TOKEN RAW:", repr(os.getenv("TELEGRAM_TOKEN")))


TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]



logging.basicConfig(level=logging.INFO)
# --- CONFIGURATION --- #
# Initialize the Client with Automatic Retries
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- IMPROVED SYSTEM PROMPT ---AIzaSyBRprEPbgeepZYhWy6MOOM1ZP9rq98wfT8
system_instruction = """

You are a professional eFootball coach.

Your job is to ANALYZE the user's problem and classify it internally:
(defense, attack, passing, positioning, mentality)




STRICT GUIDELINES:RULES:

1. UNDERSTAND INTENT:
- If the user describes a PROBLEM (e.g. "I can't defend", "my attack is bad"):
  → Use structured format:

    🔍 Problem  
    ⚙️ Solution  
    🎯 Tips  

- If the user asks a NORMAL QUESTION (tips, players, updates, general gameplay):
  → Answer naturally (NO sections)

2. BE HUMAN:
- If user says "Hi", greet only
- If user says "Bye", respond briefly

3. BE CLEAR:
- Keep answers simple and not too long
- Use bullet points (•) when helpful

4. STYLE:
- Use emojis only when useful (⚽, 📋, 🎯)
- Avoid over-formatting

1. BE HUMAN: If the user says 'Hi', 'Hello', or 'How are you', greet them back naturally. Don't give tactics unless they ask a football question. 
2. BE CONCISE: Only answer what is specifically asked. If they say 'Bye', just wish them luck in their next match.
3. STRUCTURE: Use clear, spaced-out lines. Avoid using heavy double asterisks (**) for every word. Use bullet points (•) for lists.
4. TONE: Professional, encouraging, and clear.
5. VISUALS: Use relevant emojis (⚽, 📋, 🏃‍♂️) to highlight key tactical points.
"""
user_memory = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to your eFootball Coach!\n\n"
        "I can help you improve your gameplay ⚽\n\n"
        "💬 Just send me:\n"
        "• Your problem (e.g. 'I can't defend')\n"
        "• Or ask anything about the game\n\n"
        "📌 Type /help if you need guidance"
    )
\
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 How to use this bot:\n\n"
        "• Describe your problem → I’ll fix it\n"
        "• Ask about tactics, players, or gameplay\n\n"
        "Examples:\n"
        "• 'My defense is bad'\n"
        "• 'Best formation?'\n\n"
        "⚽ I’ll respond like a real coach"
    )

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    wait_msg = await update.message.reply_text("⏳ Thinking...")
    user_id = update.message.chat_id
    history = user_memory.get(user_id, [])
    history.append(f"User: {user_message}")

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", # Using a highly stable version for your region
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7 # Makes the conversation feel more natural
            ),

            contents = "\n".join(history[-5:])
        )

        ai_reply = response.text
        
        history.append(f"Coach: {ai_reply}")
        user_memory[user_id] = history
        # Optional: Clean up any stray double asterisks the AI might still generate
        clean_reply = ai_reply.replace("**", "") 


        try:
            await asyncio.sleep(1)
            await wait_msg.delete()
        except:
            pass

        await update.message.reply_text(clean_reply)

    except Exception as e:
        if "429" in str(e):
            await update.message.reply_text("⏳ Coach is taking a break. Too many requests! Try again in a minute.")
        else:
            print(f"Error: {e}")
            await update.message.reply_text("⚽ Coach is currently reviewing the match tapes. Try again in a moment!")




app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))

print("eFootball Coach Bot is running with improved logic...")
app.run_polling()
