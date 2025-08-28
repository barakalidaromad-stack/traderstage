import io
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from PIL import Image

TOKEN = "8207089919:AAFVSnuc_5DE8JUYQGJZcu8RZ5N_3D0c3gI"  # <-- o'z tokeningizni yozing

# Har bir foydalanuvchi uchun vaqtincha rasmlar
user_images = {}
MAX_IMAGES = 30  # Har bir foydalanuvchi uchun maksimal rasm soni

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Assalomu alaykum!\n"
        "PDF qilmoqchi bo'lgan rasmingizni yuboring(Max 30 ta)"
        
    )

# Rasm qabul qilish
async def collect_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_images:
        user_images[user_id] = []

    if len(user_images[user_id]) >= MAX_IMAGES:
        await update.message.reply_text(f"❌ Juda ko‘p rasm yubordingiz (maksimal {MAX_IMAGES} ta). /done deb yozing.")
        return

    photo = update.message.photo[-1]  # eng sifatli rasm
    file = await context.bot.get_file(photo.file_id)

    # Faylni RAMga yuklash
    bio = io.BytesIO()
    await file.download_to_memory(out=bio)
    bio.seek(0)

    user_images[user_id].append(bio)
    await update.message.reply_text(f"✅ Rasm qabul qilindi, /done buyrug'ini yuboring!' ({len(user_images[user_id])}/{MAX_IMAGES}).")

# PDF yasash
async def make_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in user_images or not user_images[user_id]:
        await update.message.reply_text("❌ Siz hali rasm yubormadingiz.")
        return

    try:
        # Rasmlarni ochish (RAM dan)
        images = [Image.open(img).convert("RGB") for img in user_images[user_id]]

        # PDFni RAM da yaratish
        pdf_bytes = io.BytesIO()
        images[0].save(pdf_bytes, format="PDF", save_all=True, append_images=images[1:])
        pdf_bytes.seek(0)

        # Foydalanuvchiga yuborish
        await update.message.reply_document(document=pdf_bytes, filename="TraderStage.pdf")
        await update.message.reply_text("📄 PDF tayyor va yuborildi!")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Xatolik: {str(e)}")

    finally:
        # Tozalash
        user_images[user_id] = []

def main():
    app = Application.builder().token(TOKEN).concurrent_updates(True).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, collect_images))
    app.add_handler(CommandHandler("done", make_pdf))

    print("🚀 Bot ishga tushdi (1GB RAM uchun optimallashtirilgan)...")
    app.run_polling()

if name == "__main__":
    main()