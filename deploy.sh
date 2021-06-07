#!/bin/bash
# Production environmnent
REMOTE_PATH=/var/www/html/assessment-tool/api
OUT=.
CONNECTION=reliefapps@92.243.25.191

set -e
echo -e "Synchronizing files updated..."
rsync -e "ssh -o StrictHostKeyChecking=no -o PubkeyAuthentication=yes" --omit-dir-times -avzr --delete --exclude-from '.gitignore' $OUT/* $CONNECTION:$REMOTE_PATH
#CMD="'""cd $REMOTE_PATH && mv docker-compose.yml.dist docker-compose.yml""'" TODO add when we have dist
#ssh -oStrictHostKeyChecking=no -o PubkeyAuthentication=yes $CONNECTION "'"$CMD"'"

echo -e "Stopping docker containers..."
CMD="'""cd $REMOTE_PATH && echo '$SSH_PASS' | sudo -S docker-compose down""'"
ssh -oStrictHostKeyChecking=no -o PubkeyAuthentication=yes $CONNECTION "'"$CMD"'"

echo -e "Starting docker containers..."
CMD="'""cd $REMOTE_PATH && echo '$SSH_PASS' | sudo -S docker-compose up --build -d""'"
ssh -oStrictHostKeyChecking=no -o PubkeyAuthentication=yes $CONNECTION "'"$CMD"'"

echo -e "Executing migrations..."
CMD="'""cd $REMOTE_PATH && echo '$SSH_PASS' | sudo -S docker-compose run --rm web python manage.py migrate""'"
ssh -oStrictHostKeyChecking=no -o PubkeyAuthentication=yes $CONNECTION "'"$CMD"'"

echo -e "Load languages and countries..."
CMD="'""cd $REMOTE_PATH && echo '$SSH_PASS' | sudo -S docker-compose run --rm web python manage.py loadlanguagescountries""'"
ssh -oStrictHostKeyChecking=no -o PubkeyAuthentication=yes $CONNECTION "'"$CMD"'"

echo -e "Deployed!"