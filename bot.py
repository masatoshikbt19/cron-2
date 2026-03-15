import json
import logging
import os
from datetime import time, timezone, timedelta
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

DATA_FILE = Path("bot_data.json")

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]  # 例: @your_channel_username
ADMIN_USER_IDS = {
    int(x.strip())
    for x in os.environ["ADMIN_USER_IDS"].split(",")
    if x.strip()
}

JST = timezone(timedelta(hours=9))

DEFAULT_DATA = {
    "messages": {
        "09:00": (
            "夜の秘密ラウンジへようこそ🌙\n"
    "ここは\n"
    "大人の女の子たちが集まる\n"
    "秘密のナイトラウンジです。\n\n"

        
    "💋 新しい出会い\n"
    "💋 夜の楽しい会話\n"
    "💋 魅力的な女の子たち\n"

    "そんな夜の時間を一緒に楽しみませんか？\n\n"

    "✨ 女の子メンバー募集中\n"
    "✨ 気軽に参加OK\n"

    "👇参加はこちら\n"
    "telegram\n"
    "https://t.me/+CoNGESydKIwyYjI0\n"
    "シグナル\n"
    "https://signal.group/#CjQKIPdSY2w4wY87HxZY-qdJ0WNLWHcqjxWCRv0FEc9ViQ5VEhCn3kyfaS6cGaRTLj45q4HW\n"

        ),
        "12:00": (
            "夜の秘密ラウンジへようこそ🌙\n"
    "ここは\n"
    "大人の女の子たちが集まる\n"
    "秘密のナイトラウンジです。\n\n"

        
    "💋 新しい出会い\n"
    "💋 夜の楽しい会話\n"
    "💋 魅力的な女の子たち\n"

    "そんな夜の時間を一緒に楽しみませんか？\n\n"

    "✨ 女の子メンバー募集中\n"
    "✨ 気軽に参加OK\n"

    "👇参加はこちら\n"
    "telegram\n"
    "https://t.me/+CoNGESydKIwyYjI0\n"
    "シグナル\n"
    "https://signal.group/#CjQKIPdSY2w4wY87HxZY-qdJ0WNLWHcqjxWCRv0FEc9ViQ5VEhCn3kyfaS6cGaRTLj45q4HW\n"
        ),
        "18:00": (
            "夜の秘密ラウンジへようこそ🌙\n"
    "ここは\n"
    "大人の女の子たちが集まる\n"
    "秘密のナイトラウンジです。\n\n"

        
    "💋 新しい出会い\n"
    "💋 夜の楽しい会話\n"
    "💋 魅力的な女の子たち\n"

    "そんな夜の時間を一緒に楽しみませんか？\n\n"

    "✨ 女の子メンバー募集中\n"
    "✨ 気軽に参加OK\n"

    "👇参加はこちら\n"
    "telegram\n"
    "https://t.me/+CoNGESydKIwyYjI0\n"
    "シグナル\n"
    "https://signal.group/#CjQKIPdSY2w4wY87HxZY-qdJ0WNLWHcqjxWCRv0FEc9ViQ5VEhCn3kyfaS6cGaRTLj45q4HW\n"
        ),
    }
}


def load_data() -> dict:
    if not DATA_FILE.exists():
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))

    if "messages" not in data:
        data["messages"] = DEFAULT_DATA["messages"].copy()

    return data


def save_data(data: dict) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_USER_IDS


async def require_admin(update: Update) -> bool:
    user = update.effective_user
    if user is None or not is_admin(user.id):
        if update.message:
            await update.message.reply_text("このコマンドは管理者のみ使えます。")
        return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user and is_admin(user.id):
        await update.message.reply_text(
            "管理者として認識しました。\n\n"
            "使えるコマンド:\n"
            "/whoami\n"
            "/post 本文\n"
            "/setmorning 本文\n"
            "/setnoon 本文\n"
            "/setevening 本文\n"
            "/schedule"
        )
    else:
        await update.message.reply_text("この bot は管理用です。")


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user is None:
        return

    text = f"user_id: {user.id}"
    if user.username:
        text += f"\nusername: @{user.username}"

    await update.message.reply_text(text)


async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin(update):
        return

    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text("使い方: /post 投稿本文")
        return

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        disable_web_page_preview=True,
    )
    await update.message.reply_text("投稿しました。")


def set_message(slot: str, text: str) -> None:
    data = load_data()
    data["messages"][slot] = text
    save_data(data)


async def set_slot_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    slot: str,
    label: str,
) -> None:
    if not await require_admin(update):
        return

    text = " ".join(context.args).strip()
    if not text:
        await update.message.reply_text(f"使い方: /set{label} 本文")
        return

    set_message(slot, text)
    await update.message.reply_text(f"{label} 用メッセージを更新しました。")


async def setmorning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_slot_message(update, context, "09:00", "morning")


async def setnoon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_slot_message(update, context, "12:00", "noon")


async def setevening(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await set_slot_message(update, context, "18:00", "evening")


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await require_admin(update):
        return

    data = load_data()
    msgs = data["messages"]

    text = (
        "現在の定期投稿設定\n\n"
        f"09:00\n{msgs.get('09:00', '')}\n\n"
        f"12:00\n{msgs.get('12:00', '')}\n\n"
        f"18:00\n{msgs.get('18:00', '')}"
    )
    await update.message.reply_text(text, disable_web_page_preview=True)


async def send_scheduled_post(context: ContextTypes.DEFAULT_TYPE) -> None:
    slot = context.job.data["slot"]
    data = load_data()
    text = data["messages"].get(slot)

    if not text:
        logger.warning("No message configured for slot %s", slot)
        return

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=text,
        disable_web_page_preview=True,
    )
    logger.info("Posted scheduled message for %s", slot)


def setup_jobs(application: Application) -> None:
    jq = application.job_queue
    if jq is None:
        raise RuntimeError("JobQueue が利用できません。requirements.txt を確認してください。")

    jq.run_daily(
        send_scheduled_post,
        time=time(hour=9, minute=0, tzinfo=JST),
        data={"slot": "09:00"},
        name="morning_post",
    )
    jq.run_daily(
        send_scheduled_post,
        time=time(hour=12, minute=0, tzinfo=JST),
        data={"slot": "12:00"},
        name="noon_post",
    )
    jq.run_daily(
        send_scheduled_post,
        time=time(hour=18, minute=0, tzinfo=JST),
        data={"slot": "18:00"},
        name="evening_post",
    )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("whoami", whoami))
    app.add_handler(CommandHandler("post", post_command))
    app.add_handler(CommandHandler("setmorning", setmorning))
    app.add_handler(CommandHandler("setnoon", setnoon))
    app.add_handler(CommandHandler("setevening", setevening))
    app.add_handler(CommandHandler("schedule", schedule_command))

    setup_jobs(app)
    app.run_polling()


if __name__ == "__main__":
    main()
