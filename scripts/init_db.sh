#!/bin/bash

# 初始化数据库

echo "Starting database initialization..."

# 检查 .env 是否存在
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it from .env.example"
    exit 1
fi

# 运行数据库迁移
echo "Running database migrations..."
alembic upgrade head

echo "Database initialization completed!"
