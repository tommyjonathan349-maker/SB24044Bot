import os
import random
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from questions import QUESTIONS

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

TOKEN = os.environ["BOT_TOKEN"]
CATEGORIES = sorted({q["category"] for q in QUESTIONS})


def get_scores(context):
    return context.bot_data.setdefault("scores", {})  # in memory; resets on restart


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧠 Welcome to the Quiz Bot!\n\n"
        "/quiz - random question\n"
        f"/quiz <category> - one of: {', '.join(CATEGORIES)}\n"
        "/score - your score\n"
        "/leaderboard - top players"
    )


async def send_question(chat_id, context: ContextTypes.DEFAULT_TYPE, category=None):
    pool = [i for i, q in enumerate(QUESTIONS) if not category or q["category"] == category]
    if not pool:
        await context.bot.send_message(chat_id, f"Unknown category. Try: {', '.join(CATEGORIES)}")
        return
    idx = random.choice(pool)
    q = QUESTIONS[idx]
    keyboard = [
        [InlineKeyboardButton(opt, callback_data=f"a:{idx}:{i}")]
        for i, opt in enumerate(q["options"])
    ]
    await context.bot.send_message(
        chat_id,
        f"❓ [{q['category'].title()}]\n\n{q['q']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = context.args[0].lower() if context.args else None
    await send_question(update.effective_chat.id, context, category)


async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "next":
        await query.edit_message_reply_markup(reply_markup=None)
        await send_question(query.message.chat_id, context)
        return

    _, idx, choice = query.data.split(":")
    q = QUESTIONS[int(idx)]
    correct = int(choice) == q["answer"]

    user = query.from_user
    stats = get_scores(context).setdefault(user.id, {"name": user.first_name, "correct": 0, "total": 0})
    stats["total"] += 1
    stats["correct"] += int(correct)

    if correct:
        result = "✅ Correct!"
    else:
        result = f"❌ Wrong. The answer is: {q['options'][q['answer']]}"

    await query.edit_message_text(
        f"❓ {q['q']}\n\n{result}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Next question", callback_data="next")]]),
    )


async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = get_scores(context).get(update.effective_user.id)
    if not s:
        await update.message.reply_text("No answers yet. Send /quiz to start!")
        return
    await update.message.reply_text(f"📊 {s['correct']} correct out of {s['total']}")


async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = get_scores(context)
    if not scores:
        await update.message.reply_text("No players yet. Send /quiz to start!")
        return
    top = sorted(scores.values(), key=lambda s: s["correct"], reverse=True)[:10]
    lines = [f"{n}. {s['name']} - {s['correct']}/{s['total']}" for n, s in enumerate(top, 1)]
    await update.message.reply_text("🏆 Leaderboard\n\n" + "\n".join(lines))


def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CallbackQueryHandler(on_button))
    app.run_polling()


if __name__ == "__main__":
    main()
