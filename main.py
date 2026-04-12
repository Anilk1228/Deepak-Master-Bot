import os
import re
import sys
import json
import time
import asyncio
import requests
import subprocess
import urllib.parse
import yt_dlp
import cloudscraper
import m3u8
import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web
import yt_dlp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# 🛑 Stop Command track karne ke liye (Naya Logic)
stop_batch = {}

photo = "https://i.postimg.cc/dVY9nL63/IMG-20250426-130510-655.jpg"
cpphoto = "https://i.postimg.cc/dVY9nL63/IMG-20250426-130510-655.jpg"
appxzip = "https://i.postimg.cc/dVY9nL63/IMG-20250426-130510-655.jpg"
my_name = "🅂🄿🄸🄳🅈"
CHANNEL_ID = "-1003646612944"##change it with your channel 🆔 

cookies_file_path = os.getenv("COOKIES_FILE_PATH", "youtube_cookies.txt")

# Define aiohttp routes
routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("your_render_url") ## change it with your host url

async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app

async def start_bot():
    await bot.start()
    print("Bot is up and running")

async def stop_bot():
    await bot.stop()

async def main():
    if WEBHOOK:
        # Start the web server
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        site = web.TCPSite(app_runner, "0.0.0.0", PORT)
        await site.start()
        print(f"Web server started on port {PORT}")

    # Start the bot
    await start_bot()

    # Keep the program running
    try:
        while True:
            await asyncio.sleep(3600)  # Run forever, or until interrupted
    except (KeyboardInterrupt, SystemExit):
        await stop_bot()
        
class Data:
    START = (
        "🌟 Welcome {0}! 🌟\n\n"
    )

# Define the start command handler
@bot.on_message(filters.command("start"))
async def start(client: Client, msg: Message):
    user = await client.get_me()
    mention = user.mention
    start_message = await client.send_message(
        msg.chat.id,
        Data.START.format(msg.from_user.mention)
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Initializing Uploader bot... 🤖\n\n"
        "Progress: [⬜⬜⬜⬜⬜⬜⬜⬜⬜] 0%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Loading features... ⏳\n\n"
        "Progress: [🟥🟥🟥⬜⬜⬜⬜⬜⬜] 25%\n\n"
    )
    
    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "This may take a moment, sit back and relax! 😊\n\n"
        "Progress: [🟧🟧🟧🟧🟧⬜⬜⬜⬜] 50%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Checking Bot Status... 🔍\n\n"
        "Progress: [🟨🟨🟨🟨🟨🟨🟨⬜⬜] 75%\n\n"
    )

    await asyncio.sleep(1)
    await start_message.edit_text(
        Data.START.format(msg.from_user.mention) +
        "Checking status Ok... Command Nhi Bataunga **Bot Made BY 🅂🄿🄸🄳🅈™👨🏻‍💻**🔍\n\n"
        "Progress:[🟩🟩🟩🟩🟩🟩🟩🟩🟩] 100%\n\n"
    )

# 🛑 Naya Soft Stop Handler
@bot.on_message(filters.command(["stop"]))
async def stop_handler(_, m):
    await m.delete()
    stop_batch[m.chat.id] = True
    await m.reply_text("**🛑 STOPPED! Jo video process ho rahi hai bas wo hogi, uske baad batch ruk jayega.**", True)

# ==================================
# 👑 KING / UPLOAD COMMAND
# ==================================
@bot.on_message(filters.command(["king","upload"]) )
async def txt_handler1(bot: Client, m: Message):
    await m.delete()
    
    stop_batch[m.chat.id] = False # Naya batch start hote hi reset karein
    
    editable = await m.reply_text(f"**🔹Hi I am Poweful TXT Downloader📥 Bot.**\n🔹**Send me the TXT file and wait.**")
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))
    credit = f"𝗦𝗣𝗜𝗗𝗬™"
    token = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzYxNTE3MzAuMTI2LCJkYXRhIjp7Il9pZCI6IjYzMDRjMmY3Yzc5NjBlMDAxODAwNDQ4NyIsInVzZXJuYW1lIjoiNzc2MTAxNzc3MCIsImZpcnN0TmFtZSI6IkplZXYgbmFyYXlhbiIsImxhc3ROYW1lIjoic2FoIiwib3JnYW5pemF0aW9uIjp7Il9pZCI6IjVlYjM5M2VlOTVmYWI3NDY4YTc5ZDE4OSIsIndlYnNpdGUiOiJwaHlzaWNzd2FsbGFoLmNvbSIsIm5hbWUiOiJQaHlzaWNzd2FsbGFoIn0sImVtYWlsIjoiV1dXLkpFRVZOQVJBWUFOU0FIQEdNQUlMLkNPTSIsInJvbGVzIjpbIjViMjdiZDk2NTg0MmY5NTBhNzc4YzZlZiJdLCJjb3VudHJ5R3JvdXAiOiJJTiIsInR5cGUiOiJVU0VSIn0sImlhdCI6MTczNTU0NjkzMH0.iImf90mFu_cI-xINBv4t0jVz-rWK1zeXOIwIFvkrS0M"
    try:    
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            if "://" in i:
                links.append(i.split("://", 1))
        os.remove(x)
    except:
        await m.reply_text("Invalid file input.")
        os.remove(x)
        return

    await editable.edit(f"Total links found are **{len(links)}**\n\nSend from where you want to download (initial is **1**).")
    
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
    
    try:
        arg = int(raw_text)
    except ValueError:
        arg = 1
    
    if raw_text == "1":
        file_name_without_ext = os.path.splitext(file_name)[0]
        fancy_batch_name = f"𝐁𝐚𝐭𝐜𝐡 𝐍𝐚𝐦𝐞: 𝗤𝘂𝗮𝗹𝗶𝘁𝘆".replace("𝗤𝘂𝗮𝗹𝗶𝘁𝘆", file_name_without_ext)
        
        name_message = await bot.send_message(
            m.chat.id,
            f"📌 **Batch Name Pinned!** 📌\n"
            f"🎨 {fancy_batch_name}\n"
            f"✨ Stay organized with your pinned batches 🚀!"
        )
        await bot.pin_chat_message(m.chat.id, name_message.id)
        await asyncio.sleep(2)
        
    await editable.edit("**Enter Your Batch Name or send d for grabing from text filename.**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    if raw_text0 == 'd':
        b_name = file_name
    else:
        b_name = raw_text0

    await editable.edit("**Enter resolution.\n Eg : 480 or 720**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    try:
        if raw_text2 == "144": res = "144x256"
        elif raw_text2 == "240": res = "240x426"
        elif raw_text2 == "360": res = "360x640"
        elif raw_text2 == "480": res = "480x854"
        elif raw_text2 == "720": res = "720x1280"
        elif raw_text2 == "1080": res = "1080x1920" 
        else: res = "UN"
    except Exception:
        res = "UN"
    
    await editable.edit("**Enter Your Name or send 'de' for use default.\n Eg : 𝗦𝗣𝗜𝗗𝗬™👨🏻‍💻**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    if raw_text3 == 'de':
        CR = credit
    else:
        CR = raw_text3
        
    await editable.edit("**Enter Your PW Token For 𝐌𝐏𝐃 𝐔𝐑𝐋  or send 'Not' for use default**")
    input4: Message = await bot.listen(editable.chat.id)
    raw_text4 = input4.text
    await input4.delete(True)
    if raw_text4.lower() == 'not':
        MR = token
    else:
        MR = raw_text4
        
    await editable.edit("Now send the **Thumb url**\n**Eg :** ``\n\nor Send `no`")
    input6 = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "no"

    count = int(arg)    
    try:
        for i in range(arg-1, len(links)):
            
            # 🛑 Stop Logic Check
            if stop_batch.get(m.chat.id, False):
                await m.reply_text("🛑 **Batch Rok Diya Gaya Hai!**")
                stop_batch[m.chat.id] = False
                break

            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            
            # (Purana Logic as it is...)
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            if "acecwply" in url:
                cmd = f'yt-dlp -o "{name}.%(ext)s" -f "bestvideo[height<={raw_text2}]+bestaudio" --hls-prefer-ffmpeg --no-keep-video --remux-video mkv --no-warning "{url}"'
                
            if 'd1d34p8vz63oiq' in url:
                vid_id = url.split("/")[-2]
                url = f"https://dl.alphacbse.site/download/{vid_id}/master.m3u8"

            elif 'videos.classplusapp' in url or "tencdn.classplusapp" in url or "webvideos.classplusapp.com" in url or "media-cdn-alisg.classplusapp.com" in url or "videos.classplusapp" in url or "videos.classplusapp.com" in url or "media-cdn-a.classplusapp" in url or "media-cdn.classplusapp" in url or "alisg-cdn-a.classplusapp" in url:
             url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9r'}).json()['url']

            elif "apps-s3-jw-prod.utkarshapp.com" in url:
                if 'enc_plain_mp4' in url:
                    url = url.replace(url.split("/")[-1], res+'.mp4')
                elif 'Key-Pair-Id' in url:
                    url = None
                elif '.m3u8' in url:
                    q = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).split("/")[0]
                    x = url.split("/")[5]
                    x = url.replace(x, "")
                    url = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).replace(q+"/", x)
                    
            if 'amazonaws.com' in url:
                url =  f"https://master-api-v3.vercel.app/adda-mp4-m3u8?url={url}&quality={raw_text2}&token={raw_text4}"
                
            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]} {my_name}'

            if "appx" in url and "pdf" in url:
                url = f"https://deepak-drm-api.vercel.app//pdf/{url}"
            if "appx-recordings-mcdn.akamai.net.in/drm/" in url:
                cmd = f'ffmpeg -i "{url}" -c copy -bsf:a aac_adtstoasc "{name}.mp4"'
            elif "arvind" in url:
                cmd = f'ffmpeg -i "{url}" -c copy -bsf:a aac_adtstoasc "{name}.mp4"'
            if ".zip" in url:
                url = f"https://video.pablocoder.eu.org/appx-zip?url={url}"

            elif "https://appx-transcoded-videos.livelearn.in/videos/rozgar-data/" in url:
                url = url.replace("https://appx-transcoded-videos.livelearn.in/videos/rozgar-data/", "")
                name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "@").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
                name = f'{str(count).zfill(3)}) {name1[:60]}'
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'

            elif "https://appx-transcoded-videos-mcdn.akamai.net.in/videos/bhainskipathshala-data/" in url:
                url = url.replace("https://appx-transcoded-videos-mcdn.akamai.net.in/videos/bhainskipathshala-data/", "")
                name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "@").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
                name = f'{str(count).zfill(3)}) {name1[:60]}'
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
                
            if '/do' in url:               
               pdf_id = url.split("/")[-1].split(".pdf")[0]
               url = f"https://kgs-v2.akamaized.net/kgs/do/pdfs/{pdf_id}.pdf"
               
            if 'sec-prod-mediacdn.pw.live' in url:
             vid_id = url.split("sec-prod-mediacdn.pw.live/")[1].split("/")[0]
             url = f"https://pwplayer-0e2dbbdc0989.herokuapp.com/player?url=https://d1d34p8vz63oiq.cloudfront.net/{vid_id}/master.mpd?token={raw_text4}"
   
            if 'bitgravity.com' in url:               
               parts = url.split('/')               
               part1 = parts[1]; part2 = parts[2]; part3 = parts[3]; part4 = parts[4]; part5 = parts[5]; part6 = parts[6]
               url = f"https://kgs-v2.akamaized.net/{part3}/{part4}/{part5}/{part6}"

            if '?list' in url:
               video_id = url.split("/embed/")[1].split("?")[0]
               url = f"https://www.youtube.com/embed/{video_id}"
                
            if 'workers.dev' in url:
             vid_id = url.split("cloudfront.net/")[1].split("/")[0]
             url = f"https://madxapi-d0cbf6ac738c.herokuapp.com/{vid_id}/master.m3u8?token={raw_text4}"
                
            if 'psitoffers.store' in url:
             vid_id = url.split("vid=")[1].split("&")[0]
             url =  f"https://madxapi-d0cbf6ac738c.herokuapp.com/{vid_id}/master.m3u8?token={raw_text4}"

            if "edge.api.brightcove.com" in url:
                bcov = 'bcov_auth=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MzUxMzUzNjIsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiYmt3cmVIWmxZMFUwVXpkSmJYUkxVemw2ZW5Oclp6MDkiLCJmaXJzdF9uYW1lIjoiY25GdVpVdG5kRzR4U25sWVNGTjRiVW94VFhaUVVUMDkiLCJlbWFpbCI6ImFFWllPRXhKYVc1NWQyTlFTazk0YmtWWWJISTNRM3BKZW1OUVdIWXJWWE0wWldFNVIzZFNLelE0ZHowPSIsInBob25lIjoiZFhSNlFrSm9XVlpCYkN0clRUWTFOR3REU3pKTVVUMDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJhVVZGZGpBMk9XSnhlbXRZWm14amF6TTBVazQxUVQwOSIsImRldmljZV90eXBlIjoid2ViIiwiZGV2aWNlX3ZlcnNpb24iOiJDaHJvbWUrMTE5IiwiZGV2aWNlX21vZGVsIjoiY2hyb21lIiwicmVtb3RlX2FkZHIiOiIyNDA5OjQwYzI6MjA1NTo5MGQ0OjYzYmM6YTNjOTozMzBiOmIxOTkifX0.Kifitj1wCe_ohkdclvUt7WGuVBsQFiz7eezXoF1RduDJi4X7egejZlLZ0GCZmEKBwQpMJLvrdbAFIRniZoeAxL4FZ-pqIoYhH3PgZU6gWzKz5pdOCWfifnIzT5b3rzhDuG7sstfNiuNk9f-HMBievswEIPUC_ElazXdZPPt1gQqP7TmVg2Hjj6-JBcG7YPSqa6CUoXNDHpjWxK_KREnjWLM7vQ6J3vF1b7z_S3_CFti167C6UK5qb_turLnOUQzWzcwEaPGB3WXO0DAri6651WF33vzuzeclrcaQcMjum8n7VQ0Cl3fqypjaWD30btHQsu5j8j3pySWUlbyPVDOk-g'
                url = url.split("bcov_auth")[0]+bcov

            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
            
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "webvideos.classplusapp." in url:
               cmd = f'yt-dlp --add-header "referer:https://web.classplusapp.com/" --add-header "x-cdn-tag:empty" -f "{ytf}" "{url}" -o "{name}.mp4"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:  
                cc = f'**🎞️ VID_ID: {str(count).zfill(3)}.\n\n📝 Title: {name1} {my_name} {res}.mkv\n\n📚 Batch Name: {b_name}\n\n📥 Extracted By : {CR}\n\n**━━━━━✦{my_name}✦━━━━━**'
                cc1 = f'**📁 PDF_ID: {str(count).zfill(3)}.\n\n📝 Title: {name1} {my_name}.pdf\n\n📚 Batch Name: {b_name}\n\n📥 Extracted By : {CR}\n\n**━━━━━✦{my_name}✦━━━━━**'
                cyt = f'**🎞️ VID_ID: {str(count).zfill(3)}.\n\n📝 Title: {name1} {my_name}.mkv\n\n📚 Batch Name: {b_name}\n\n**🔗 𝐕𝐢𝐝𝐞𝐨 𝐥𝐢𝐧𝐤 - ({url})**\n\n📥 Extracted By : {CR}\n\n**━━━━━✦{my_name}✦━━━━━**'
                ccp = f'**🎞️ VID_ID: {str(count).zfill(3)}.\n\n📝 Title: {name1} {my_name}.mkv\n\n📚 Batch Name: {b_name}\n\n**🔗 𝐕𝐢𝐝𝐞𝐨 𝐥𝐢𝐧𝐤 - ({url})**\n\n📥 Extracted By : {CR}\n\n**━━━━━✦{my_name}✦━━━━━**'
                czip = f'**🎞️ VID_ID: {str(count).zfill(3)}.\n\n📝 Title: {name1} {my_name}.mkv\n\n📚 Batch Name: {b_name}\n\n**🔗 𝐕𝐢𝐝𝐞𝐨 𝐥𝐢𝐧𝐤 - ({url})**\n\n📥 Extracted By : {CR}\n\n**━━━━━✦{my_name}✦━━━━━**'
                cczip = f'**💾 ZIP_ID: {str(count).zfill(3)}.\n\n📝 Title: {name1} {my_name}.pdf\n\n📚 Batch Name: {b_name}\n\n📥 Extracted By : {CR}\n\n**━━━━━✦{my_name}✦━━━━━**'
                    
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                        time.sleep(1)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue

                elif ".pdf" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                        count += 1
                        os.remove(f'{name}.pdf')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue                       
                
                # 🔥 YAHAN HAIN NAYA DRM LOGIC 🔥
                elif "classplus" in url or ".mpd" in url or "drm" in url or ".m3u8" in url:
                    try:
                        Show = f"🔑 **Fetching DRM Key...**\n\n📝 Title:- `{name}`\n\n**𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ 🅂🄿🄸🄳🅈**"
                        prog = await m.reply_text(Show)
                        
                        safe_url = urllib.parse.quote(url, safe='')
                        api_url = f"https://deepak-drm-api.vercel.app/classplus?link={safe_url}&token={MR}"
                        
                        async with ClientSession() as session:
                            async with session.get(api_url) as resp:
                                if resp.status == 200:
                                    data = await resp.json()
                                    key = data.get("KEYS")
                                    if key:
                                        await prog.edit(f"✅ **Key Found:** `{key}`\n📥 **Downloading & Decrypting...**")
                                        dec_file = f"DEC_{name}.mp4"
                                        
                                        drm_cmd = (
                                            f'yt-dlp -k --allow-unplayable-formats -f "bestvideo[height<={raw_text2}]+bestaudio" '
                                            f'--fixup never "{url}" -o "{name}.mp4" '
                                            f'--exec "mp4decrypt --key {key} {{}} \'{dec_file}\' && rm {{}}"'
                                        )
                                        process = await asyncio.create_subprocess_shell(drm_cmd)
                                        await process.communicate()
                                        
                                        if os.path.exists(dec_file):
                                            await prog.delete(True)
                                            await helper.send_vid(bot, m, cc, dec_file, thumb, name, prog)
                                            count += 1
                                            time.sleep(1)
                                        else:
                                            await prog.edit("❌ **Decryption Failed! File not found.**")
                                            time.sleep(2)
                                    else:
                                        await prog.edit(f"❌ **API Error:** `{data}`")
                                        time.sleep(2)
                                else:
                                    await prog.edit(f"❌ **API Server Error! Status:** {resp.status}")
                                    time.sleep(2)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue
                    except Exception as e:
                        await m.reply_text(f"DRM Error: {e}")
                        continue
                          
                else:
                    Show = f"📥 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 »\n\n📝 Title:- `{name}\n\n**🔗 𝐓𝐨𝐭𝐚𝐥 𝐔𝐑𝐋 »** ✨{len(links)}✨\n\n⌨ 𝐐𝐮𝐚𝐥𝐢𝐭𝐲 » {raw_text2}`\n\n**𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ 🅂🄿🄸🄳🅈"
                    prog = await m.reply_text(Show)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    time.sleep(1)

            except Exception as e:
                await m.reply_text(
                    f"⌘ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝐈𝐧𝐭𝐞𝐫𝐮𝐩𝐭𝐞𝐝 ❌ \n\n⌘ 𝐍𝐚𝐦𝐞 » {name}\n⌘ 𝐋𝐢𝐧𝐤 » `{url}`"
                )
                continue

    except Exception as e:
        await m.reply_text(e)
    await m.reply_text("**✅ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐃𝐨𝐧𝐞**")

# ==================================
# 👑 BRAVO COMMAND
# ==================================
@bot.on_message(filters.command(["bravo"]) )
async def txt_handler2(bot: Client, m: Message):
    stop_batch[m.chat.id] = False
    editable = await m.reply_text(f"**📁Send me the TXT file and wait.**")
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))
    credit = f"𝗦𝗣𝗜𝗗𝗬™🇮🇳"
    
    try:    
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            if "://" in i:
                links.append(i.split("://", 1))
        os.remove(x)
    except:
        await m.reply_text("Invalid file input.")
        os.remove(x)
        return
   
    await editable.edit(f"Total links found are **{len(links)}**\n\nSend From where you want to download initial is **1**")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
    try:
        arg = int(raw_text)
    except:
        arg = 1
    await editable.edit("**Enter Your Batch Name or send d for grabing from text filename.**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    if raw_text0 == 'd': b_name = file_name
    else: b_name = raw_text0

    await editable.edit("**Enter resolution.\n Eg : 480 or 720**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    try:
        if raw_text2 == "144": res = "144x256"
        elif raw_text2 == "240": res = "240x426"
        elif raw_text2 == "360": res = "360x640"
        elif raw_text2 == "480": res = "480x854"
        elif raw_text2 == "720": res = "720x1280"
        elif raw_text2 == "1080": res = "1080x1920" 
        else: res = "UN"
    except Exception:
        res = "UN"
    
    await editable.edit("**Enter Your Name or send 'de' for use default.\n Eg : 𝗦𝗣𝗜𝗗𝗬™👨🏻‍💻**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    if raw_text3 == 'de': CR = credit
    else: CR = raw_text3
       
    await editable.edit("Now send the **Thumb url**\n**Eg :** ``\n\nor Send `no`")
    input6 = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "no"

    count = int(arg)    
    try:
        for i in range(arg-1, len(links)):
            
            # 🛑 Stop Logic Check
            if stop_batch.get(m.chat.id, False):
                await m.reply_text("🛑 **Batch Rok Diya Gaya Hai!**")
                stop_batch[m.chat.id] = False
                break

            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            if 'videos.classplusapp' in url or "tencdn.classplusapp" in url or "webvideos.classplusapp.com" in url or "media-cdn-alisg.classplusapp.com" in url or "videos.classplusapp" in url or "videos.classplusapp.com" in url or "media-cdn-a.classplusapp" in url or "media-cdn.classplusapp" in url or "alisg-cdn-a.classplusapp" in url:
             url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9r'}).json()['url']

            elif "apps-s3-jw-prod.utkarshapp.com" in url:
                if 'enc_plain_mp4' in url:
                    url = url.replace(url.split("/")[-1], res+'.mp4')
                elif 'Key-Pair-Id' in url:
                    url = None
                elif '.m3u8' in url:
                    q = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).split("/")[0]
                    x = url.split("/")[5]
                    x = url.replace(x, "")
                    url = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).replace(q+"/", x)
                    
            elif '/master.mpd' in url:
             vid_id =  url.split("/")[-2]
             url =  f"https://pw-links-api.onrender.com/process?v=https://sec1.pw.live/{vid_id}/master.mpd&quality={raw_text2}"

            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]} {my_name}'
                      
            if "edge.api.brightcove.com" in url:
                bcov = 'bcov_auth=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg'
                url = url.split("bcov_auth")[0]+bcov

            if 'sec-prod-mediacdn.pw.live' in url:
             vid_id = url.split("sec-prod-mediacdn.pw.live/")[1].split("/")[0]
             url = f"https://pwplayer-0e2dbbdc0989.herokuapp.com/player?url=https://d1d34p8vz63oiq.cloudfront.net/{vid_id}/master.mpd?token=not"

            if '?list' in url:
               video_id = url.split("/embed/")[1].split("?")[0]
               url = f"https://www.youtube.com/embed/{video_id}"
                
            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
            
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:  
                cc = f'**<pre><code>🎞️ 𝐕𝐈𝐃_𝐈𝐃: {str(count).zfill(3)}.</code></pre>\n\n<pre><code>📝 𝐓𝐈𝐓𝐋𝐄:👇🏻</code></pre>\n<pre><code>{name1} {res} .mkv</code></pre>\n\n<pre><code>📚 𝐁𝐀𝐓𝐂𝐇 𝐍𝐀𝐌𝐄:👇🏻</code>\n</pre><pre><code>{b_name}</code></pre>\n\n<pre><code>✨𝐄𝐗𝐓𝐑𝐀𝐂𝐓𝐄𝐃 𝐁𝐘 : {CR}</code></pre>**\n\n<pre><code>━━━━━✦𝗦𝗣𝗜𝗗𝗬❤️✦━━━━━</code></pre>'
                cc1 = f'**<pre><code>📁 𝐏𝐃𝐅_𝐈𝐃: {str(count).zfill(3)}.</code></pre>\n\n<pre><code>📝 𝐓𝐈𝐓𝐋𝐄:👇🏻</code></pre>\n<pre><code>{name1} .pdf</code></pre>\n\n<pre><code>📚 𝐁𝐀𝐓𝐂𝐇 𝐍𝐀𝐌𝐄:👇🏻</code>\n</pre><pre><code>{b_name}</code></pre>\n\n<pre><code>✨𝐄𝐗𝐓𝐑𝐀𝐂𝐓𝐄𝐃 𝐁𝐘 : {CR}</code></pre>**\n\n<pre><code>━━━━━✦𝗦𝗣𝗜𝗗𝗬❤️✦━━━━━</code></pre>'
                    
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                        time.sleep(1)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue

                elif ".pdf" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                        count += 1
                        os.remove(f'{name}.pdf')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue                       
                
                # 🔥 YAHAN HAIN NAYA DRM LOGIC 🔥
                elif "classplus" in url or ".mpd" in url or "drm" in url or ".m3u8" in url:
                    try:
                        Show = f"🔑 **Fetching DRM Key...**\n\n📝 Title:- `{name}`\n\n**𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ 🅂🄿🄸🄳🅈**"
                        prog = await m.reply_text(Show)
                        
                        safe_url = urllib.parse.quote(url, safe='')
                        api_url = f"https://deepak-drm-api.vercel.app/classplus?link={safe_url}&token=not"
                        
                        async with ClientSession() as session:
                            async with session.get(api_url) as resp:
                                if resp.status == 200:
                                    data = await resp.json()
                                    key = data.get("KEYS")
                                    if key:
                                        await prog.edit(f"✅ **Key Found:** `{key}`\n📥 **Downloading & Decrypting...**")
                                        dec_file = f"DEC_{name}.mp4"
                                        
                                        drm_cmd = (
                                            f'yt-dlp -k --allow-unplayable-formats -f "bestvideo[height<={raw_text2}]+bestaudio" '
                                            f'--fixup never "{url}" -o "{name}.mp4" '
                                            f'--exec "mp4decrypt --key {key} {{}} \'{dec_file}\' && rm {{}}"'
                                        )
                                        process = await asyncio.create_subprocess_shell(drm_cmd)
                                        await process.communicate()
                                        
                                        if os.path.exists(dec_file):
                                            await prog.delete(True)
                                            await helper.send_vid(bot, m, cc, dec_file, thumb, name, prog)
                                            count += 1
                                            time.sleep(1)
                                        else:
                                            await prog.edit("❌ **Decryption Failed! File not found.**")
                                            time.sleep(2)
                                    else:
                                        await prog.edit(f"❌ **API Error:** `{data}`")
                                        time.sleep(2)
                                else:
                                    await prog.edit(f"❌ **API Server Error! Status:** {resp.status}")
                                    time.sleep(2)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue
                    except Exception as e:
                        await m.reply_text(f"DRM Error: {e}")
                        continue
                        
                else:
                    Show = f"📥 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 »\n\n📝 Title:- `{name}\n\n**🔗 𝐓𝐨𝐭𝐚𝐥 𝐔𝐑𝐋 »** ✨{len(links)}✨\n\n⌨ 𝐐𝐮𝐥𝐢𝐭𝐲 » {raw_text2}`\n\n**🔗 𝐔𝐑𝐋 »** `{url}`\n\n**𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ 🅂🄿🄸🄳🅈"
                    prog = await m.reply_text(Show)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    time.sleep(1)

            except Exception as e:
                await m.reply_text(
                    f"⌘ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝐈𝐧𝐭𝐞𝐫𝐮𝐩𝐭𝐞𝐝\n\n⌘ 𝐍𝐚𝐦𝐞 » {name}\n⌘ 𝐋𝐢𝐧𝐤 » `{url}`"
                )
                continue

    except Exception as e:
        await m.reply_text(e)
    await m.reply_text("🔰Done🔰\n✨Thankyou For Choosing")

# ==================================
# 👑 ALPHA COMMAND (advance/alpha)
# ==================================
@bot.on_message(filters.command(["alpha", "advance"]))
async def txt_handler3(bot: Client, m: Message):
    stop_batch[m.chat.id] = False
    editable = await m.reply_text(f"**🔹Send me the TXT file and wait.**")
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))
    credit = f"𝗦𝗣𝗜𝗗𝗬™🇮🇳"
    try:    
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for i in content:
            if "://" in i:
                links.append(i.split("://", 1))
        os.remove(x)
    except:
        await m.reply_text("Invalid file input.")
        os.remove(x)
        return
   
    await editable.edit(f"Total links found are **{len(links)}**\n\nSend From where you want to download initial is **1**")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)
    try:
        arg = int(raw_text)
    except:
        arg = 1
    await editable.edit("**Enter Your Batch Name or send d for grabing from text filename.**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)
    if raw_text0 == 'd': b_name = file_name
    else: b_name = raw_text0

    await editable.edit("**Enter resolution.\n Eg : 480 or 720**")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    try:
        if raw_text2 == "144": res = "144x256"
        elif raw_text2 == "240": res = "240x426"
        elif raw_text2 == "360": res = "360x640"
        elif raw_text2 == "480": res = "480x854"
        elif raw_text2 == "720": res = "720x1280"
        elif raw_text2 == "1080": res = "1080x1920" 
        else: res = "UN"
    except Exception:
        res = "UN"
    
    await editable.edit("**Enter Your Name or send 'de' for use default.\n Eg : 𝗦𝗣𝗜𝗗𝗬™👨🏻‍💻**")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    if raw_text3 == 'de': CR = credit
    else: CR = raw_text3

    await editable.edit("**Enter Your PW Token For 𝐌𝐏𝐃 𝐔𝐑𝐋  or send 'unknown' for use default**")
    input4: Message = await bot.listen(editable.chat.id)
    raw_text4 = input4.text
    await input4.delete(True)
    if raw_text4 == 'unknown': MR = raw_text4
    else: MR = raw_text4
        
    await editable.edit("Now send the **Thumb url**\n**Eg :** ``\n\nor Send `no`")
    input6 = await bot.listen(editable.chat.id)
    raw_text6 = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = input6.text
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb = "no"

    count = int(arg)    
    try:
        for i in range(arg-1, len(links)):
            
            # 🛑 Stop Logic Check
            if stop_batch.get(m.chat.id, False):
                await m.reply_text("🛑 **Batch Rok Diya Gaya Hai!**")
                stop_batch[m.chat.id] = False
                break

            Vxy = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","")
            url = "https://" + Vxy
            
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)

            elif 'videos.classplusapp' in url or "tencdn.classplusapp" in url or "webvideos.classplusapp.com" in url or "media-cdn-alisg.classplusapp.com" in url or "videos.classplusapp" in url or "videos.classplusapp.com" in url or "media-cdn-a.classplusapp" in url or "media-cdn.classplusapp" in url:
             url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9r'}).json()['url']

            elif "apps-s3-jw-prod.utkarshapp.com" in url:
                if 'enc_plain_mp4' in url:
                    url = url.replace(url.split("/")[-1], res+'.mp4')
                elif 'Key-Pair-Id' in url:
                    url = None
                elif '.m3u8' in url:
                    q = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).split("/")[0]
                    x = url.split("/")[5]
                    x = url.replace(x, "")
                    url = ((m3u8.loads(requests.get(url).text)).data['playlists'][1]['uri']).replace(q+"/", x)
                    
            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]} {my_name}'
                      
            if '/do' in url:               
               pdf_id = url.split("/")[-1].split(".pdf")[0]
               url = f"https://kgs-v2.akamaized.net/kgs/do/pdfs/{pdf_id}.pdf"
               
            if '?list' in url:
               video_id = url.split("/embed/")[1].split("?")[0]
               url = f"https://www.youtube.com/embed/{video_id}"
                
            if 'sec-prod-mediacdn.pw.live' in url:
             vid_id = url.split("sec-prod-mediacdn.pw.live/")[1].split("/")[0]
             url = f"https://pwplayer-0e2dbbdc0989.herokuapp.com/player?url=https://d1d34p8vz63oiq.cloudfront.net/{vid_id}/master.mpd?token={raw_text4}"
    
            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"
            
            if "jw-prod" in url:
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            elif "youtube.com" in url or "youtu.be" in url:
                cmd = f'yt-dlp --cookies youtube_cookies.txt -f "{ytf}" "{url}" -o "{name}".mp4'
            else:
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'

            try:  
                cc = f'**🎞️ VID_ID: {str(count).zfill(3)}.\n\n📝 Title: {name1} @Spidy_Universe {res}.mkv\n\n<pre><code>📚 Batch Name: {b_name}</code></pre>\n\n📥 Extracted By : {CR}\n\n**━━━━━✦𝗦𝗣𝗜𝗗𝗬❤️✦━━━━━**'
                cc1 = f'**📁 PDF_ID: {str(count).zfill(3)}.\n\n📝 Title: {name1} @Spidy_Universe.pdf\n\n<pre><code>📚 Batch Name: {b_name}</code></pre>\n\n📥 Extracted By : {CR}\n\n**━━━━━✦𝗦𝗣𝗜𝗗𝗬❤️✦━━━━━**'
                    
                if "drive" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                        time.sleep(1)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue

                elif ".pdf" in url:
                    try:
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                        count += 1
                        os.remove(f'{name}.pdf')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue                       
                
                # 🔥 YAHAN HAIN NAYA DRM LOGIC 🔥
                elif "classplus" in url or ".mpd" in url or "drm" in url or ".m3u8" in url:
                    try:
                        Show = f"🔑 **Fetching DRM Key...**\n\n📝 Title:- `{name}`\n\n**𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ 🅂🄿🄸🄳🅈**"
                        prog = await m.reply_text(Show)
                        
                        safe_url = urllib.parse.quote(url, safe='')
                        api_url = f"https://deepak-drm-api.vercel.app/classplus?link={safe_url}&token={MR}"
                        
                        async with ClientSession() as session:
                            async with session.get(api_url) as resp:
                                if resp.status == 200:
                                    data = await resp.json()
                                    key = data.get("KEYS")
                                    if key:
                                        await prog.edit(f"✅ **Key Found:** `{key}`\n📥 **Downloading & Decrypting...**")
                                        dec_file = f"DEC_{name}.mp4"
                                        
                                        drm_cmd = (
                                            f'yt-dlp -k --allow-unplayable-formats -f "bestvideo[height<={raw_text2}]+bestaudio" '
                                            f'--fixup never "{url}" -o "{name}.mp4" '
                                            f'--exec "mp4decrypt --key {key} {{}} \'{dec_file}\' && rm {{}}"'
                                        )
                                        process = await asyncio.create_subprocess_shell(drm_cmd)
                                        await process.communicate()
                                        
                                        if os.path.exists(dec_file):
                                            await prog.delete(True)
                                            await helper.send_vid(bot, m, cc, dec_file, thumb, name, prog)
                                            count += 1
                                            time.sleep(1)
                                        else:
                                            await prog.edit("❌ **Decryption Failed! File not found.**")
                                            time.sleep(2)
                                    else:
                                        await prog.edit(f"❌ **API Error:** `{data}`")
                                        time.sleep(2)
                                else:
                                    await prog.edit(f"❌ **API Server Error! Status:** {resp.status}")
                                    time.sleep(2)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue
                    except Exception as e:
                        await m.reply_text(f"DRM Error: {e}")
                        continue
                        
                else:
                    Show = f"📥 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 »\n\n📝 Title:- `{name}\n\n**🔗 𝐓𝐨𝐭𝐚𝐥 𝐔𝐑𝐋 »** ✨{len(links)}✨\n\n⌨ 𝐐𝐮𝐥𝐢𝐭𝐲 » {raw_text2}`\n\n**🔗 𝐔𝐑𝐋 »** `{url}`\n\n**𝐁𝐨𝐭 𝐌𝐚𝐝𝐞 𝐁𝐲 ✦ 🅂🄿🄸🄳🅈"
                    prog = await m.reply_text(Show)
                    res_file = await helper.download_video(url, cmd, name)
                    filename = res_file
                    await prog.delete(True)
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    count += 1
                    time.sleep(1)

            except Exception as e:
                await m.reply_text(
                    f"⌘ 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝐈𝐧𝐭𝐞𝐫𝐮𝐩𝐭𝐞𝐝\n\n⌘ 𝐍𝐚𝐦𝐞 » {name}\n⌘ 𝐋𝐢𝐧𝐤 » `{url}`"
                )
                continue

    except Exception as e:
        await m.reply_text(e)
    await m.reply_text("🔰Done🔰\n✨Thankyou For Choosing")

if __name__ == "__main__":
    WEBHOOK = False
    PORT = 8080
    asyncio.run(main())
