# Деплой PetShare Israel на VPS (Zomro, Ubuntu)

Сервер один на оба бота: RoboCompanion и PetShare спокойно живут рядом
(PetShare — в /opt/petshare, RoboCompanion — в /opt/robocompanion).

## Часть 0. Если сервер ещё не куплен

Следуйте «Части 0» в robo_companion_v2/deploy/DEPLOY.md: тариф Blitz Intel
уже выбран, осталось на экране ОС выбрать **Ubuntu 24.04 LTS x64**
(не Windows!), панель — «Без панели», оплатить и подождать письмо
с IP-адресом и паролем root.

## Часть 1. Перенос PetShare (одна команда)

На Mac в Terminal, из папки проекта:

```bash
cd ~/Desktop/petshare_israel
bash deploy/to_vps.sh IP_СЕРВЕРА
```

При первом запуске спросит `yes/no` (введите yes) и пароль root (дважды:
для копирования и для настройки). Скрипт сам: скопирует проект,
поставит Python-зависимости, настроит автозапуск systemd и запустит бота.

## Часть 2. Выключить бота на Mac

Два экземпляра бота конфликтуют за Telegram, поэтому после успешного
запуска на сервере выполните на Mac:

```bash
launchctl bootout gui/$(id -u)/com.petshare.bot
rm ~/Library/LaunchAgents/com.petshare.bot.plist
```

## Часть 3. Проверка и полезные команды на сервере

Подключиться: `ssh root@IP_СЕРВЕРА`

```bash
systemctl status petshare      # статус (active (running) — всё хорошо)
journalctl -u petshare -n 50   # последние 50 строк лога
systemctl restart petshare     # перезапуск
tail -f /opt/petshare/bot.log  # живой лог бота
```

## Обновление кода в будущем

Снова одна команда с Mac: `bash deploy/to_vps.sh IP_СЕРВЕРА` —
она скопирует изменения и перезапустит бота.
