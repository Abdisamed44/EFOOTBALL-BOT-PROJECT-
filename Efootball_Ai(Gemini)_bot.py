import asyncio
import os
from google import genai
from google.genai import types
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
GEMINI_API_KEY = "AIzaSyBRprEPbgeepZYhWy6MOOM1ZP9rq98wfT8"
TELEGRAM_TOKEN = "8747420569:AAEj8iQMmQpIMqZ-9CErjXIJj2QM39Fr684"

# Initialize the Client with Automatic Retries
client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            attempts=3,
            initial_delay=2.0,
            http_status_codes=[429, 503] # Added 503 for high demand
        )
    )
)

# --- IMPROVED SYSTEM PROMPT ---
system_instruction = """

You are a professional eFootball coach.

Your job is to ANALYZE the user's problem and classify it internally:
(defense, attack, passing, positioning, mentality)

Then respond in this structure:

⚽ Type: (write the category)

📉 Problem:
(short)

🧠 Why it happens:
(short)

🛠 Fix:
(practical)

🎮 In-game tips:
(bullet points)

RULES:
- If user greets → greet back (no tactics)
- Keep it short and clean
- Be practical, no theory
 

STRICT GUIDELINES:
1. BE HUMAN: If the user says 'Hi', 'Hello', or 'How are you', greet them back naturally. Don't give tactics unless they ask a football question. 
2. BE CONCISE: Only answer what is specifically asked. If they say 'Bye', just wish them luck in their next match.
3. STRUCTURE: Use clear, spaced-out lines. Avoid using heavy double asterisks (**) for every word. Use bullet points (•) for lists.
4. TONE: Professional, encouraging, and clear.
5. VISUALS: Use relevant emojis (⚽, 📋, 🏃‍♂️) to highlight key tactical points.
"""

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    wait_msg = await update.message.reply_text("⏳ Thinking...")
        
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview", # Using a highly stable version for your region
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7 # Makes the conversation feel more natural
            ),
            contents=user_message
        )

        ai_reply = response.text
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

print("eFootball Coach Bot is running with improved logic...")
app.run_polling()
