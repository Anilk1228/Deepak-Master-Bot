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
    process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await process.communicate()

@bot.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text("🌟 **Deepak Master Bot Ready!** 🌟\n\nAb Token Expiry Checker bhi lag gaya hai. Send .txt file.")

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
    except:
        if os.path.exists(file_path): os.remove(file_path)
        return await prog.edit("❌ File format error.")

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
            # 1. URL Bypass (Token Checker Ke Sath)
            if any(domain in url for domain in ["classplusapp", "videos", "tencdn"]):
                await status_msg.edit("🔓 **Signing URL & Checking Token...**")
                headers = {'x-access-token': CLASSPLUS_TOKEN, 'User-Agent': 'Mozilla/5.0'}
                
                sign_req = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers=headers)
                
                try:
                    api_res = sign_req.json()
                    if 'url' in api_res:
                        url = api_res['url']
                    else:
                        await status_msg.edit(f"❌ **Classplus Token Expired!**\nNaya Token lagao. Response: `{api_res}`")
                        continue
                except:
                    await status_msg.edit(f"❌ **API Failed.** Status: {sign_req.status_code}")
                    continue

            # 2. Local PSSH Extraction
            await status_msg.edit("🔍 **Extracting PSSH Locally...**")
            
            # Google Edge Cache Error Bypass Headers
            req_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Origin': 'https://web.classplusapp.com',
                'Referer': 'https://web.classplusapp.com/'
            }
            
            mpd_req = requests.get(url, headers=req_headers)
            mpd_text = mpd_req.text
            
            # Agar master playlist hai
            if ".m3u8" in url and "#EXT-X-STREAM-INF" in mpd_text:
                for line in mpd_text.splitlines():
                    if line.strip() and not line.startswith('#'):
                        variant_url = urllib.parse.urljoin(url, line.strip())
                        mpd_text = requests.get(variant_url, headers=req_headers).text
                        break
            
            pssh_match = re.search(r'<cenc:pssh[^>]*>(.*?)</cenc:pssh>', mpd_text, re.I | re.S)
            if not pssh_match:
                pssh_match = re.search(r'URI="data:text/plain;base64,([^"]+)"', mpd_text)
            
            if not pssh_match:
                clean_text = mpd_text[:150].replace('<', '&lt;').replace('>', '&gt;')
                await status_msg.edit(f"❌ **PSSH not found!** Google Response:\n`{clean_text}`")
                continue
                
            extracted_pssh = pssh_match.group(1).strip().replace("\n", "")

            # 3. Key Fetching via Vercel
            await status_msg.edit("🔑 **Fetching Key from Vercel...**")
            safe_pssh = urllib.parse.quote(extracted_pssh, safe='')
            api_url = f"https://deepak-drm-api.vercel.app/classplus?pssh={safe_pssh}&token={CLASSPLUS_TOKEN}"
            
            async with ClientSession() as session:
                async with session.get(api_url) as resp:
                    data = await resp.json()
                    key = data.get("KEYS")

            # 4. Decrypt & Upload
            if key:
                await status_msg.edit(f"✅ **Key:** `{key}`\n📥 **Downloading...**")
                dec_file = f"DEC_{str(i+1).zfill(3)}.mp4"
                
                cmd = (
                    f'yt-dlp -k --allow-unplayable-formats -f "bestvideo[height<={quality}]+bestaudio" '
                    f'--fixup never "{url}" -o "temp_{dec_file}" '
                    f'--exec "mp4decrypt --key {key} {{}} \'{dec_file}\' && rm {{}}"'
                )
                await run_command(cmd)
                
                if os.path.exists(dec_file):
                    await status_msg.edit("📤 **Uploading...**")
                    await client.send_video(m.chat.id, video=dec_file, caption=f"🎬 {name}\n📚 {b_name}", supports_streaming=True)
                    os.remove(dec_file)
                    await status_msg.delete()
                else:
                    await status_msg.edit("❌ **Decryption Failed!**")
            else:
                await status_msg.edit(f"❌ **API Error:** `{data.get('error')}`")

        except Exception as e:
            await m.reply_text(f"⚠️ Error: {e}")

    await m.reply_text("✅ **Batch Complete!**")

if __name__ == "__main__":
    bot.run()
