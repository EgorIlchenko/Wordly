#!/bin/bash
set -e

rabbitmq-server -detached

until rabbitmqctl await_startup; do
    echo "Waiting for RabbitMQ to start..."
    sleep 2
done

rabbitmqctl add_user "$APP_CONFIG__RABBITMQ__USER" "$APP_CONFIG__RABBITMQ__PASSWORD" || true
rabbitmqctl set_user_tags "$APP_CONFIG__RABBITMQ__USER" administrator || true
rabbitmqctl set_permissions -p / "$APP_CONFIG__RABBITMQ__USER" ".*" ".*" ".*" || true

rabbitmqctl stop

rabbitmq-server
