#!/bin/bash

export CPU_COUNT=`grep -c ^processor /proc/cpuinfo `
export WORKER_COUNT=${WORKER_COUNT:-$(( $CPU_COUNT * 2 ))}
export MAX_REQUESTS=${MAX_REQUESTS:-1000}

[ ! -z $ENV_FILE ] \
        && source /envs/${ENV_FILE}.env

env

./manage.py migrate \
        || { echo >&2 "[CRIT] migrate fails. Aborting"; exit 1; }

celery -A events worker -c ${WORKER_COUNT} -l ${LOG_LEVEL} &
# gunicorn --bind 0.0.0.0:8000 -k eventlet -w ${WORKER_COUNT} --max-requests ${MAX_REQUESTS} --reload core.wsgi:application
daphne -b 0.0.0.0 -p 8000 core.asgi:application