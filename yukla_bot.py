import os
import re
import yt_dlp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)
from telegram.request import HTTPXRequest

# 🎯 Qabul qilinadigan video platformalar regexi
VIDEO_LINK_REGEX = re.compile(
    r"(https?://(?:www\.)?"
    r"(youtube\.com|youtu\.be|facebook\.com|fb\.watch|instagram\.com|tiktok\.com)"
    r"/[^\s]+)"
)

# 📥 Video yuklab olish funksiyasi
def download_video(url, filename):
    ydl_opts = {
        'outtmpl': filename,
        'format': 'mp4',
        'quiet': True,
        'merge_output_format': 'mp4',
        'filesize-limit': 49 * 1024 * 1024  # 49 MB limit
    }
    try:
        yt_dlp.YoutubeDL(ydl_opts).download([url])
        return True
    except Exception as e:
        print(f"[Xato] Video yuklab bo‘lmadi: {e}")
        return False

# 🧾 Xabarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text or ""
    match = VIDEO_LINK_REGEX.search(text)

    if match:
        url = match.group(1)
        user = update.message.from_user
        message_id = update.message.message_id
        chat_id = update.message.chat_id

        if user.username:
            sender_name = f"@{user.username}"
        else:
            sender_name = f"{user.first_name or ''} {user.last_name or ''}".strip()

        await update.message.reply_text("📥 Video yuklanmoqda...")

        filename = f"video_{message_id}.mp4"
        success = download_video(url, filename)

        if success and os.path.exists(filename):
            filesize = os.path.getsize(filename)
            if filesize > 49 * 1024 * 1024:
                await update.message.reply_text("⚠️ Video 50MB dan katta. Yuborib bo‘lmaydi.")
                os.remove(filename)
                return

            caption = f"🎬 Yuklandi\n👤 {sender_name}"
            with open(filename, 'rb') as video_file:
                await update.message.reply_video(video=video_file, caption=caption)

            os.remove(filename)

            # ✅ Asl linkli xabarni o‘chirish
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                print(f"[✔] Linkli xabar o‘chirildi: {message_id}")
            except Exception as e:
                print(f"[Xato] Linkni o‘chirib bo‘lmadi: {e}")
        else:
            await update.message.reply_text("⚠️ Video yuklab bo‘lmadi.")
    else:
        pass  # boshqa xabarlar e'tiborga olinmaydi

# 🚀 Botni ishga tushirish
def main():
    BOT_TOKEN = "8086222828:AAFm5Lg5CPghCdo_DTVwy88EuDUJFqfBtIk"  # ← bu yerga o‘z bot tokeningizni yozing

    app = ApplicationBuilder().token(BOT_TOKEN).request(
        HTTPXRequest(
            read_timeout=60,
            connect_timeout=60,
            write_timeout=120
        )
    ).build()

    app.add_handler(MessageHandler(filters.TEXT & filters.ALL, handle_message))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
