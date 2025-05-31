# FlapPyBird Makefile for Replit
.PHONY: all run install clean

# 默认目标
all: install

# 安装依赖
install:
	cd backend && pip install -r requirements_cloud.txt

# 运行应用
run:
	cd backend && python simple_server_cloud.py

# 清理缓存
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete

# 帮助信息
help:
	@echo "可用命令："
	@echo "  make install  - 安装依赖"
	@echo "  make run      - 运行应用"
	@echo "  make clean    - 清理缓存文件"
	@echo "  make help     - 显示此帮助信息" 