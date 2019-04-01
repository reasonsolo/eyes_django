#!/bin/sh

crontab -r
echo "* * 10 * * /root/letsencrypt/certbot-auto renew" > timercron
echo "*/10 * * * * python3 /data/eyes_django/wx_auth/app_token.py" >> timercron
crontab ./timercron
