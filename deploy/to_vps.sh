#!/bin/bash
# Перенос PetShare Israel на VPS одной командой.
# Использование:  bash deploy/to_vps.sh IP_СЕРВЕРА
# Пример:         bash deploy/to_vps.sh 185.11.22.33
set -e

IP="$1"
if [ -z "$IP" ]; then
  echo "Укажите IP сервера: bash deploy/to_vps.sh 185.xx.xx.xx"
  exit 1
fi

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "== Копирую файлы проекта на $IP =="
rsync -avz --delete \
  --exclude venv --exclude .git --exclude __pycache__ \
  --exclude bot.log --exclude launchd.log --exclude bot_state.pkl \
  "$PROJECT_DIR"/ root@"$IP":/opt/petshare/

echo "== Настраиваю сервер (Python, зависимости, автозапуск) =="
ssh root@"$IP" 'bash -s' <<'REMOTE'
set -e
apt-get update -qq
apt-get install -y -qq python3-venv python3-pip > /dev/null
cd /opt/petshare
if [ ! -d venv ]; then python3 -m venv venv; fi
./venv/bin/pip install --quiet --upgrade pip
./venv/bin/pip install --quiet -r requirements.txt
cp deploy/petshare.service /etc/systemd/system/petshare.service
systemctl daemon-reload
systemctl enable petshare
systemctl restart petshare
sleep 5
systemctl --no-pager status petshare | head -8
REMOTE

echo ""
echo "== Готово! Бот запущен на сервере =="
echo "ВАЖНО: теперь выключите бота на Mac, иначе они будут конфликтовать:"
echo "  launchctl bootout gui/\$(id -u)/com.petshare.bot"
