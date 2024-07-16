# Copyright 2021 TerminalWarlord under the terms of the MIT
# license found at https://github.com/TerminalWarlord/TikTok-Downloader-Bot/blob/master/LICENSE
# Encoding = 'utf-8'
# Fork and Deploy, do not modify this repo and claim it yours
# For collaboration mail me at dev.jaybee@gmail.com
from pyrogram import Client, filters,enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import requests
import os
import re
import bs4
import string
import random
import time
from progress_bar import progress
from dotenv import load_dotenv

load_dotenv()
bot_token = os.environ.get('BOT_TOKEN')
workers = 2
api = os.environ.get('APP_ID')
hash = os.environ.get('APP_HASH')
channel_chat_id = os.environ.get('CHANNEL_ID')
channel_url = os.environ.get('CHANNEL_URL')
bot_username = os.environ.get('BOT_USERNAME')

print(api)
app = Client("twitter", bot_token=bot_token, api_id=api, api_hash=hash, workers=workers)
app.set_parse_mode(enums.ParseMode.MARKDOWN)


def is_subscribed(user_id):
    try:
        app.get_chat_member(channel_chat_id, user_id)
        return True
    except Exception as e:
        return False

def download_twitter_video(url):
    """Extract the highest quality video url to download into a file

    Args:
        url (str): The twitter post URL to download from
    """

    api_url = f"https://twitsave.com/info?url={url}"

    response = requests.get(api_url)
    data = bs4.BeautifulSoup(response.text, "html.parser")
    download_button = data.find_all("div", class_="origin-top-right")[0]
    quality_buttons = download_button.find_all("a")
    highest_quality_url = quality_buttons[0].get("href") # Highest quality video url
    
    # create random file name
    file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15)) + ".mp4"
    
    return file_name, highest_quality_url

@app.on_message(filters.command('start'))
def start(client, message):
    app.send_message(chat_id=message.from_user.id, text=f"Hello there, I am **X (Twitter) Downloader Bot**.\nI can download any X (Twitter) video from a given link.",reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔔 Subscribe", url=channel_url)]
            ]))

@app.on_message(filters.command('help'))
def help(client, message):


        app.send_message(chat_id=message.from_user.id, text=f"Hello there, I am **X (Twitter) Downloader Bot**.\nI can download any X (Twitter) video from a given link.",
                        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔔 Subscribe", url=channel_url)]
            ]))



@app.on_message((filters.regex("http://")|filters.regex("https://")) & (filters.regex('twitter')|filters.regex('x')))
def download_video(client, message):
    if not is_subscribed(message.from_user.id):
        app.send_message(chat_id=message.chat.id,
                         text='__Please Subscribe to our Channel to use this bot__', reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔔 Subscribe", url=channel_url),InlineKeyboardButton("Try again", callback_data="try_again")]]
                         ))
        return
    a = app.send_message(chat_id=message.chat.id,
                         text='__Downloading File to the Server__')
    link = re.findall(r'\bhttps?://.*[(twitter|x)]\S+', message.text)[0]
    link = link.split("?")[0]
    


    file_name, highest_quality_url = download_twitter_video(link)
    download_path = os.path.join(os.getcwd(), file_name)
    with requests.get(highest_quality_url, timeout=(50, 10000), stream=True) as r:
        with open(download_path, 'wb') as f:
            chunk_size = 1048576
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)


        a.edit(f'__Downloaded to the server!\n'
               f'Uploading to Telegram Now ⏳__')
        start = time.time()
        title = file_name
        app.send_document(chat_id=message.chat.id,
                          document=download_path,
                          caption=f"__Uploaded by @{bot_username}__",
                          file_name=file_name,
                          progress=progress,
                          progress_args=(a, start, title))
        a.delete()
        try:
            os.unlink(download_path)
        except:
            pass


@app.on_callback_query(filters.regex("try_again"))
def try_again(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if is_subscribed(user_id):
        # Your code to handle the download video functionality
        app.send_message(chat_id=callback_query.message.chat.id, text='You are subscribed! You can use the bot now.')
    else:
        app.send_message(
            chat_id=callback_query.message.chat.id,
            text='__You are still not subscribed. Please subscribe to our channel to use the bot.__',
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔔 Subscribe", url=channel_url),
                  InlineKeyboardButton("Try again", callback_data="try_again")]]
            )
        )

app.run()
