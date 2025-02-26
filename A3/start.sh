#!/bin/sh

# 启动主服务
python /app/app.py &

# 启动验证服务
python /app/auth.py

# 注意：最后一个命令不能用&后台运行，否则容器会立即退出