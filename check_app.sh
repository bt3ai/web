#!/bin/bash

echo "start ..."
pids=$(pgrep -af 'app.py' | awk '{print $1}')
export PIPENV_PIPFILE=/home/ubuntu/Schwab-Portfolio/Pipfile.linux

if [ -z "$pids" ]; then
  echo "no app found, start one."
cd ~/Schwab-Portfolio
  echo "start app now ..."
  nohup  python3 app.py >/home/ubuntu/Schwab-Portfolio/log/app$(date -d "today" +"%Y%m%d%H%M").log 2>&1 &

else
  echo "checking app is running, ignore ..."
fi
