FROM python:3.12-slim

WORKDIR /app

# Сначала зависимости — этот слой кэшируется и не пересобирается без нужды
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Состояние пользователей храним в примонтированном каталоге (см. compose)
ENV PETSHARE_STATE_FILE=/data/bot_state.pkl

CMD ["python", "bot.py"]
