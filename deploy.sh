#!/bin/sh

crontab -r
echo "21 0 * * 1 /root/letsencrypt/certbot-auto renew" > timercron
echo "*/10 * * * * python3 /data/eyes_django/wx_auth/app_token.py" >> timercron
echo "*/10 * * * * python3 /data/eyes_django/clean_qrcode.py" >> timercron
echo "*/10 * * * * python3 /data/eyes_django/clean_avatar.py" >> timercron
crontab ./timercron
