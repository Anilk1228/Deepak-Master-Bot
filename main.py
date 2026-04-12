import os
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
from aiohttp import ClientSession
import cloudscraper
import urllib.parse
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
        os.remove(file_path)
        return await prog.edit(f"❌ File padhne mein error: {e}")

    if not links:
        return await prog.edit("❌ File mein koi valid link nahi hai!")

    await prog.edit(f"✅ **Total Links Found:** {len(links)}")

    # 2. Interactive Menu (Batch, Resolution, Credit)
    try:
        # Batch Name
        batch_msg = await bot.ask(m.chat.id, "📚 **Enter Batch Name:**\n*(Ya default ke liye 'd' bhejein)*", timeout=60)
        b_name = m.document.file_name.replace(".txt", "") if batch_msg.text.lower() == 'd' else batch_msg.text
        
        # Resolution
        res_msg = await bot.ask(m.chat.id, "⚙️ **Enter Resolution (144, 240, 360, 480, 720, 1080):**", timeout=60)
        quality = res_msg.text if res_msg.text in ["144", "240", "360", "480", "720", "1080"] else "720"
        
        # Extracted By / Credit Name
        credit_msg = await bot.ask(m.chat.id, "✍️ **Enter Your Name/Channel Name:**\n*(Ya default ke liye 'd' bhejein)*", timeout=60)
        credit = "Deepak Master Bot" if credit_msg.text.lower() == 'd' else credit_msg.text

    except asyncio.TimeoutError:
        return await m.reply_text("❌ **Time out!** Aapne jaldi reply nahi kiya. Wapas file bhejein.")

    await m.reply_text(f"🚀 **Downloading Shuru!**\n\n📚 Batch: {b_name}\n⚙️ Quality: {quality}p\n✍️ Credit: {credit}")

    # 3. Processing Loop
    for i, (raw_name, url) in enumerate(links):
        clean_name = re.sub(r'[\\/*?:"<>|]', "", raw_name)[:60]
        vid_id = str(i + 1).zfill(3)
        mp4_file = f"{vid_id}_{clean_name}.mp4"
        dec_file = f"DEC_{vid_id}.mp4"
        
        caption = f"🎬 **Title:** `{clean_name}`\n📚 **Batch:** `{b_name}`\n⚙️ **Quality:** `{quality}p`\n🌟 **Extracted By:** {credit}"
        status_msg = await m.reply_text(f"⏳ **Processing [{vid_id}/{len(links)}]:** `{clean_name}`")

        # --- DRM / CLASSPLUS LOGIC ---
        if "classplus" in url or ".mpd" in url or "drm" in url:
            await status_msg.edit("🔑 **Fetching DRM Key...**")
            
            # Aapki API hit kar rahe hain (Token parameter ke sath)
            api_url = f"https://deepak-drm-api.vercel.app/classplus?pssh={url}&license_url={url}&token={CLASSPLUS_TOKEN}"
            
            try:
                async with ClientSession() as session:
                    async with session.get(api_url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            key = data.get("KEYS")
                            
                            if key:
                                await status_msg.edit(f"✅ **Key Found:** `{key}`\n📥 **Downloading & Decrypting...**")
                                
                                # Magic Command: Download aur Decrypt ek sath
                                cmd = (
                                    f'yt-dlp -k --allow-unplayable-formats -f "bestvideo[height<={quality}]+bestaudio" '
                                    f'--fixup never "{url}" -o "{mp4_file}" '
                                    f'--exec "mp4decrypt --key {key} {{}} {dec_file} && rm {{}}"'
                                )
                                await run_command(cmd)
                                final_video = dec_file if os.path.exists(dec_file) else None
                            else:
                                await status_msg.edit("❌ **Key nahi mili API se!**")
                                continue
                        else:
                            await status_msg.edit(f"⚠️ **API Error:** {resp.status}")
                            continue
            except Exception as e:
                await status_msg.edit(f"⚠️ **DRM Error:** {e}")
                continue

        # --- NORMAL VIDEO LOGIC ---
        else:
            await status_msg.edit("📥 **Normal Video Download ho rahi hai...**")
            cmd = f'yt-dlp -f "bestvideo[height<={quality}]+bestaudio/best" "{url}" -o "{mp4_file}"'
            await run_command(cmd)
            final_video = mp4_file if os.path.exists(mp4_file) else None

        # --- UPLOAD TO TELEGRAM ---
        if final_video and os.path.exists(final_video):
            await status_msg.edit("📤 **Telegram par Upload ho raha hai...**")
            try:
                await client.send_video(
                    chat_id=m.chat.id,
                    video=final_video,
                    caption=caption,
                    supports_streaming=True
                )
                await status_msg.delete()
            except Exception as e:
                await status_msg.edit(f"❌ Upload Failed: {e}")
            finally:
                if os.path.exists(final_video):
                    os.remove(final_video)
        else:
            await status_msg.edit("❌ **Download/Decryption fail ho gaya.**")

    await m.reply_text("🎉 **Batch Complete! Saari videos bhej di gayi hain.**")

if __name__ == "__main__":
    print("🚀 Master Bot is Running...")
    bot.run()
