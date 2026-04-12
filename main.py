import os
import re
import asyncio
import urllib.parse
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
from aiohttp import ClientSession
from config import API_ID, API_HASH, BOT_TOKEN, CLASSPLUS_TOKEN

bot = Client("MasterBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# System Command chalane ka helper function
async def run_command(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()

@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text("🌟 **Welcome to Master DRM Bot!** 🌟\n\nBhai, aap mujhe apni `.txt` file bhejo, main aapse details puchunga aur downloading shuru kar dunga.")

@bot.on_message(filters.document & filters.private)
async def process_txt_file(client: Client, m: Message):
    if not m.document.file_name.endswith(".txt"):
        return await m.reply_text("❌ Kripya sirf `.txt` file hi bhejein!")

    # 1. File Download and Parse
    prog = await m.reply_text("📁 **TXT File mil gayi! Scan kar raha hoon...**")
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
        return await prog.edit(f"❌ File padhne mein error: {e}")

    if not links:
        return await prog.edit("❌ File mein koi valid link nahi hai!")

    await prog.edit(f"✅ **Total Links Found:** {len(links)}")

    # 2. Interactive Menu
    try:
        batch_msg = await bot.ask(m.chat.id, "📚 **Enter Batch Name:**\n*(Ya default ke liye 'd' bhejein)*", timeout=60)
        b_name = m.document.file_name.replace(".txt", "") if batch_msg.text.lower() == 'd' else batch_msg.text
        
        res_msg = await bot.ask(m.chat.id, "⚙️ **Enter Resolution (144, 240, 360, 480, 720, 1080):**", timeout=60)
        quality = res_msg.text if res_msg.text in ["144", "240", "360", "480", "720", "1080"] else "720"
        
        credit_msg = await bot.ask(m.chat.id, "✍️ **Enter Your Name/Channel Name:**\n*(Ya default ke liye 'd' bhejein)*", timeout=60)
        credit = "Deepak Master Bot" if credit_msg.text.lower() == 'd' else credit_msg.text

    except asyncio.TimeoutError:
        return await m.reply_text("❌ **Time out!** Aapne jaldi reply nahi kiya.")

    await m.reply_text(f"🚀 **Downloading Shuru!**\n📚 Batch: {b_name}\n⚙️ Quality: {quality}p")

# Processing Loop ke andar jahan status_msg.edit hai, wahan ye logic lagaen:

    for i, (raw_name, url) in enumerate(links):
        # ... (baaki ka purana code)
        
        status_msg = await m.reply_text(f"⏳ **Processing [{vid_id}/{len(links)}]:** `{clean_name}`")

        try:
            # --- DRM / CLASSPLUS LOGIC ---
            if "classplus" in url or ".mpd" in url or "drm" in url:
                await status_msg.edit("🔑 **Fetching DRM Key...**")
                await asyncio.sleep(4) # 🟢 Gap badha diya hai (Anti-Flood)
                
                # ... (API calling logic)
                
                if key:
                    await status_msg.edit(f"✅ **Key Found!**\n📥 **Downloading...**")
                    await asyncio.sleep(3) # 🟢 Ek aur gap
                    
                    # ... (yt-dlp command logic)
                    
            # --- UPLOAD SECTION ---
            if final_video and os.path.exists(final_video):
                await status_msg.edit("📤 **Uploading to Telegram...**")
                await asyncio.sleep(5) # 🟢 Upload se pehle lamba pause
                
                await client.send_video(chat_id=m.chat.id, video=final_video, caption=caption)
                await status_msg.delete()
                
        except Exception as e:
            # 🔥 Agar Telegram FloodWait bhejta hai toh bot yahan handle karega
            if "FloodWait" in str(e):
                wait_time = int(re.findall(r'\d+', str(e))[0])
                print(f"⚠️ Telegram speed limit! Waiting for {wait_time} seconds...")
                await asyncio.sleep(wait_time + 5) # Bot khud hi wait karke resume karega
            else:
                print(f"❌ Error: {e}")
            continue
