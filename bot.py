"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import time
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

SERVER_URL = "http://localhost:1234/v1"

i=0

history = [
        {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."},
        {"role": "user", "content": "Hello, introduce yourself to someone opening this program for the first time. Be concise."},
    ]

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

user_data = {} # Allows for multiple Users
# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def AI(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the text to the server and return the response."""
    # Chat with an intelligent assistant in your terminal
    user_id = update.message.from_user.id
    #user_name = update.message.from_user.username
    
    # Initialize user data list if not already present
    if user_id not in user_data:
        user_data[user_id] = []
        history = [
        {"role": "system", "content": "You are an intelligent assistant. You always provide well-reasoned answers that are both correct and helpful."},
        {"role": "user", "content": "Hello, introduce yourself to someone opening this program for the first time. Be concise."},
        ]
    else:
        history = user_data[user_id]
        
    from openai import OpenAI

    # Point to the local server
    client = OpenAI(base_url=SERVER_URL, api_key="lm-studio")

    #global history
    
    
    history.append({"role": "user", "content": update.message.text})
    
    completion = client.chat.completions.create(
        model="Mistral-7B-Instruct-v0.3.Q8_0.gguf",
        messages=history,
        temperature=0.7,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}
    print("User:\n",update.message.text)
    print("AI:")
    for chunk in completion:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
            new_message["content"] += chunk.choices[0].delta.content
    history.append(new_message)
    
    # Uncomment to see chat history
    # import json
    # gray_color = "\033[90m"
    # reset_color = "\033[0m"
    # print(f"{gray_color}\n{'-'*20} History dump {'-'*20}\n")
    # print(json.dumps(history, indent=2))
    # print(f"\n{'-'*55}\n{reset_color}")
    user_data[user_id] = history
    print(user_data)
    print()
    await update.message.reply_text(new_message["content"])

async def image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None :
    global i
    from image_gen import image_generator
    print(update.message.text)
    split_list = update.message.text.split('|')
    image_path = "output_images/image_"+str(i)+".png"
    
    chat_id = update.message.chat_id
    image_generator(prompt = split_list[0],neg_prompt=split_list[1] if len(split_list) > 1 else "",count=i)
    # Sending the image
    with open(image_path, 'rb') as image_file:
        await context.bot.send_photo(chat_id=chat_id, photo=image_file)
    i+=1

#def change_model():
    
def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("YOUR TOKEN HERE").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("image", image))
    #application.add_handler(CommandHandler("model", change_model))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, AI))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()