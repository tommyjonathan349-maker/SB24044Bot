# Telegram Quiz Bot

A simple trivia bot. Only needs a Telegram bot token.

## 1. Get a token
Open Telegram, message **@BotFather**, send `/newbot`, and copy the token.

## 2. Run locally (optional)
```bash
pip install -r requirements.txt
export BOT_TOKEN="your-token"      # Windows: set BOT_TOKEN=your-token
python bot.py
```

## 3. Push to GitHub
```bash
git init
git add .
git commit -m "Quiz bot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/telegram-quiz-bot.git
git push -u origin main
```

## 4. Deploy on Railway
1. Go to railway.app → **New Project** → **Deploy from GitHub repo** → pick this repo.
2. Open the service → **Variables** → add `BOT_TOKEN` = your token.
3. Railway reads the `Procfile` and runs `python bot.py` as a worker. No port or domain needed.
4. Check **Deployments → Logs**, then message your bot `/start`.

## Notes
- Scores are kept in memory and reset on redeploy/restart.
- Add questions in `questions.py`.
- Run only one instance at a time, or Telegram will return a "Conflict" error.
