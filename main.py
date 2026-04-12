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

# 🛑 Stop function track karne ke liye dictionary
stop_batch = {}

# System Command chalane ka helper function
async def run_command(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()

@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text("🌟 **Welcome to Master DRM Bot!** 🌟\n\nBhai, aap mujhe apni `.txt` file bhejo, main aapse details puchunga.\n\n💡 *Tip: Kisi bhi chalte huye batch ko rokne ke liye aap `/stop` bhej sakte hain.*")

# 🛑 Naya Stop Command Logic
@bot.on_message(filters.command("stop"))
async def stop_cmd(client, message):
    stop_batch[message.chat.id] = True
    await message.reply_text("🛑 **Stop Command Received!**\nJo video abhi process ho rahi hai bas wo complete hogi, aur uske baad batch ruk jayega.")

@bot.on_message(filters.document & filters.private)
async def process_txt_file(client: Client, m: Message):
    if not m.document.file_name.endswith(".txt"):
        return await m.reply_text("❌ Kripya sirf `.txt` file hi bhejein!")

    # Naya batch start hote hi stop flag reset kar dena
    stop_batch[m.chat.id] = False

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

    # Classplus License URL
    LICENSE_URL = "https://appx.classplusapp.com/get-drm-license"

    await prog.edit(f"✅ **Total Links Found:** {len(links)}")

    # Interactive Menu
    try:
        batch_msg = await bot.ask(m.chat.id, "📚 **Enter Batch Name:**\n*(Ya default ke liye 'd' bhejein)*", timeout=60)
        b_name = m.document.file_name.replace(".txt", "") if batch_msg.text.lower() == 'd' else batch_msg.text
        
        res_msg = await bot.ask(m.chat.id, "⚙️ **Enter Resolution (144, 240, 360, 480, 720, 1080):**", timeout=60)
        quality = res_msg.text if res_msg.text in ["144", "240", "360", "480", "720", "1080"] else "720"
        
        credit_msg = await bot.ask(m.chat.id, "✍️ **Enter Your Name/Channel Name:**\n*(Ya default ke liye 'd' bhejein)*", timeout=60)
        credit = "Deepak Master Bot" if credit_msg.text.lower() == 'd' else credit_msg.text
    except asyncio.TimeoutError:
        return await m.reply_text("❌ **Time out!** Wapas file bhejein.")

    await m.reply_text(f"🚀 **Downloading Shuru!**\n📚 Batch: {b_name}\n⚙️ Quality: {quality}p")

    # Processing Loop
    for i, (raw_name, url) in enumerate(links):
        
        # 🛑 Check karna ki user ne /stop toh nahi bheja
        if stop_batch.get(m.chat.id, False):
            await m.reply_text(f"🛑 **Batch yahin rok diya gaya hai!** ({i} videos done)")
            break

        clean_name = re.sub(r'[\\/*?:"<>|]', "", raw_name)[:60]
        vid_id = str(i + 1).zfill(3)
        mp4_file = f"{vid_id}_{clean_name}.mp4"
        dec_file = f"DEC_{vid_id}.mp4"
        final_video = None
        
        caption = f"🎬 **Title:** `{clean_name}`\n📚 **Batch:** `{b_name}`\n⚙️ **Quality:** `{quality}p`\n🌟 **Extracted By:** {credit}"
        status_msg = await m.reply_text(f"⏳ **Processing [{vid_id}/{len(links)}]:** `{clean_name}`")

        try:
            if "classplus" in url or ".mpd" in url or "drm" in url:
                await status_msg.edit("🔍 **MPD file se PSSH nikal raha hoon...**")
                
                # 🔥 PSSH EXTRACTOR LOGIC
                pssh_string = None
                async with ClientSession() as session:
                    async with session.get(url) as mpd_resp:
                        if mpd_resp.status == 200:
                            mpd_text = await mpd_resp.text()
                            # MPD ke andar se PSSH dhundhna
                            pssh_match = re.search(r'<cenc:pssh[^>]*>(.*?)</cenc:pssh>', mpd_text)
                            if pssh_match:
                                pssh_string = pssh_match.group(1)
                
                if not pssh_string:
                    await status_msg.edit("❌ **Error:** MPD link se PSSH nahi mila!")
                    continue

                await status_msg.edit("🔑 **Fetching DRM Key...**")
                await asyncio.sleep(2) # Flood protection
                
                safe_pssh = urllib.parse.quote(pssh_string, safe='')
                safe_license = urllib.parse.quote(LICENSE_URL, safe='')
                
                api_url = f"https://deepak-drm-api.vercel.app/classplus?pssh={safe_pssh}&license_url={safe_license}&token={CLASSPLUS_TOKEN}"
                
                async with ClientSession() as session:
                    async with session.get(api_url) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            key = data.get("KEYS")
                            if key:
                                await status_msg.edit(f"✅ **Key Found:** `{key}`\n📥 **Downloading...**")
                                await asyncio.sleep(2)
                                cmd = (
                                    f'yt-dlp -k --allow-unplayable-formats -f "bestvideo[height<={quality}]+bestaudio" '
                                    f'--fixup never "{url}" -o "{mp4_file}" '
                                    f'--exec "mp4decrypt --key {key} {{}} {dec_file} && rm {{}}"'
                                )
                                await run_command(cmd)
                                final_video = dec_file if os.path.exists(dec_file) else None
                            else:
                                await status_msg.edit(f"❌ **API Error:** `{data}`")
                                continue
            else:
                await status_msg.edit("📥 **Downloading Normal Video...**")
                cmd = f'yt-dlp -f "bestvideo[height<={quality}]+bestaudio/best" "{url}" -o "{mp4_file}"'
                await run_command(cmd)
                final_video = mp4_file if os.path.exists(mp4_file) else None

            # Upload
            if final_video and os.path.exists(final_video):
                await status_msg.edit("📤 **Uploading...**")
                await asyncio.sleep(3)
                await client.send_video(chat_id=m.chat.id, video=final_video, caption=caption, supports_streaming=True)
                await status_msg.delete()
            else:
                await status_msg.edit("❌ **Process Failed!**")
        
        except Exception as e:
            if "FloodWait" in str(e):
                wait_time = int(re.findall(r'\d+', str(e))[0])
                print(f"Waiting {wait_time}s due to FloodWait...")
                await asyncio.sleep(wait_time + 5)
            else:
                print(f"Error: {e}")
            continue
        finally:
            if os.path.exists(mp4_file): os.remove(mp4_file)
            if final_video and os.path.exists(final_video): os.remove(final_video)

    # 🛑 Final Message check karna ki naturally khatam hua ya roka gaya hai
    if stop_batch.get(m.chat.id, False):
        await m.reply_text("🛑 **Process ko manually rok diya gaya tha.**")
    else:
        await m.reply_text("🎉 **Batch Complete! Saari videos bhej di gayi hain.**")

if __name__ == "__main__":
    try:
        print("🚀 Deepak Master Bot starting...")
        bot.run()
    except Exception as e:
        print(f"❌ Bot crash ho gaya! Error: {e}")
