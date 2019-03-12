#!/bin/sh

crontab -r
echo "* * 10 * * ? /root/letsencrypt/certbot-auto renew" > timercron
echo "0 */10 * * * ? /data/eyes_django/wx_auth/app_token.py" >> timercron
crontab ./timercron
