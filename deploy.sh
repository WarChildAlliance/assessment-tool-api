#!/bin/bash

OUT=.
DOCKER_COMPOSE="docker-compose"

set -e
echo -e "Synchronizing files..."
rsync -e "ssh -oStrictHostKeyChecking=no -o PubkeyAuthentication=yes" -avzr --delete --exclude-from '.gitignore' $OUT/* $CONNECTION:$REMOTE_PATH

if [ "$AZURE" = true ]
then
  DOCKER_COMPOSE="docker compose"
  echo -e "Copy local.py file..."
  CMD="'""cd $REMOTE_PATH && mv admin/settings/local.dist.py admin/settings/local.py""'"
  ssh -oStrictHostKeyChecking=no -o PubkeyAuthentication=yes $CONNECTION "'"$CMD"'"
  echo -e "Copy docker-compose.yml file..."
  CMD="'""cd $REMOTE_PATH && mv docker-compose.dist.yml docker-compose.yml""'"
  ssh -oStrictHostKeyChecking=no -o PubkeyAuthentication=yes $CONNECTION "'"$CMD"'"
fi

echo -e "Stopping docker containers..."
CMD="'""cd $REMOTE_PATH && echo '$SSH_PASS' | sudo -S $DOCKER_COMPOSE down""'"
ssh -oStrictHostKeyChecking=no -o PubkeyAuthentication=yes $CONNECTION "'"$CMD"'"

echo -e "Starting docker containers..."
CMD="'""cd $REMOTE_PATH && echo '$SSH_PASS' | sudo -S $DOCKER_COMPOSE up --build -d""'"
ssh -oStrictHostKeyChecking=no -o PubkeyAuthentication=yes $CONNECTION "'"$CMD"'"

echo -e "Executing migrations..."
CMD="'""cd $REMOTE_PATH && echo '$SSH_PASS' | sudo -S $DOCKER_COMPOSE run --rm web python manage.py migrate""'"
ssh -oStrictHostKeyChecking=no -o PubkeyAuthentication=yes $CONNECTION "'"$CMD"'"

echo -e "Load languages and countries..."
CMD="'""cd $REMOTE_PATH && echo '$SSH_PASS' | sudo -S $DOCKER_COMPOSE run --rm web python manage.py loaddata languages_countries""'"
ssh -oStrictHostKeyChecking=no -o PubkeyAuthentication=yes $CONNECTION "'"$CMD"'"

echo -e "Deployed!"