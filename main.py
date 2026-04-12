import os
import re
import asyncio
import urllib.parse
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
from aiohttp import ClientSession
from config import API_ID, API_HASH, BOT_TOKEN, CLASSPLUS_TOKEN

bot = Client("MasterBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

stop_batch = {}

async def run_command(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()

@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text("🌟 **Deepak Master Bot Ready!** 🌟\n\nAb Classplus DRM links bypass honge. /stop se batch rok sakte hain.")

@bot.on_message(filters.command("stop"))
async def stop_cmd(client, message):
    stop_batch[message.chat.id] = True
    await message.reply_text("🛑 **Stop Command Received!** Current video ke baad batch ruk jayega.")

@bot.on_message(filters.document & filters.private)
async def process_txt_file(client: Client, m: Message):
    if not m.document.file_name.endswith(".txt"):
        return await m.reply_text("❌ Kripya sirf `.txt` file hi bhejein!")

    stop_batch[m.chat.id] = False
    prog = await m.reply_text("📁 **TXT File scanning...**")
    file_path = await m.download()
    
    links = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f.read().splitlines():
                if "://" in line:
                    parts = line.split("://", 1)
                    links.append((parts[0].strip(), "https://" + parts[1].strip()))
        os.remove(file_path)
    except Exception as e:
        if os.path.exists(file_path): os.remove(file_path)
        return await prog.edit(f"❌ Error: {e}")

    await prog.edit(f"✅ **Total Links Found:** {len(links)}")

    try:
        b_name_msg = await bot.ask(m.chat.id, "📚 **Batch Name?** (d for default)", timeout=60)
        b_name = m.document.file_name.replace(".txt", "") if b_name_msg.text == 'd' else b_name_msg.text
        
        quality_msg = await bot.ask(m.chat.id, "⚙️ **Quality?** (480, 720, 1080)", timeout=60)
        quality = quality_msg.text
    except: return

    for i, (name1, url) in enumerate(links):
        if stop_batch.get(m.chat.id, False): break

        name = f"{str(i+1).zfill(3)}) {name1[:50]}"
        status_msg = await m.reply_text(f"⏳ **Processing:** `{name}`")

        try:
            # 1. URL Bypass (Sign the URL first)
            if any(domain in url for domain in ["classplusapp", "videos", "tencdn"]):
                await status_msg.edit("🔓 **Signing URL for PSSH...**")
                headers = {'x-access-token': CLASSPLUS_TOKEN}
                api_res = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers=headers).json()
                url = api_res.get('url', url) # <--- Ab 'url' signed hai

            # 2. Key Fetching via Vercel
            await status_msg.edit("🔑 **Fetching Key...**")
            safe_url = urllib.parse.quote(url, safe='')
            # Token bhej rahe hain taaki API signed link ko khol sake
            api_url = f"https://deepak-drm-api.vercel.app/classplus?link={safe_url}&token={CLASSPLUS_TOKEN}"
            
            async with ClientSession() as session:
                async with session.get(api_url) as resp:
                    data = await resp.json()
                    key = data.get("KEYS")

            if key:
                await status_msg.edit(f"✅ **Key:** `{key}`\n📥 **Downloading...**")
                dec_file = f"{name}.mp4"
                cmd = (
                    f'yt-dlp -k --allow-unplayable-formats -f "bestvideo[height<={quality}]+bestaudio" '
                    f'--fixup never "{url}" -o "temp_{name}.mp4" '
                    f'--exec "mp4decrypt --key {key} {{}} \'{dec_file}\' && rm {{}}"'
                )
                await run_command(cmd)
                
                if os.path.exists(dec_file):
                    await status_msg.edit("📤 **Uploading...**")
                    await client.send_video(m.chat.id, video=dec_file, caption=f"🎬 {name}\n📚 {b_name}")
                    os.remove(dec_file)
                    await status_msg.delete()
                else:
                    await status_msg.edit("❌ **Decryption Failed!**")
            else:
                # Agar PSSH nahi mila toh API error yahan dikhega
                await status_msg.edit(f"❌ **API Error:** `{data.get('error')}`\n`{data.get('details', '')}`")

        except Exception as e:
            await m.reply_text(f"⚠️ Error in {name}: {e}")

    await m.reply_text("✅ **Batch Processed!**")

if __name__ == "__main__":
    bot.run()
