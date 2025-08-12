#!/bin/bash

# Start supervisord in the background, fully detached
nohup /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf > /var/log/supervisord.out 2>&1 &

# Optional: wait a moment to ensure it's started
sleep 1

# Drop into interactive shell
exec bash
