# FlapPyBird云部署Makefile
# 默认目标，运行云服务器
default:
	@make run

# 运行云服务器（Replit/云平台）
run:
	cd backend && python simple_server_cloud.py

# 运行本地游戏（开发用）
game:
	cd game-desktop && python main.py

# 运行本地服务器
local-server:
	cd backend && python simple_server.py

# 使用pygbag构建Web版本
web:
	pygbag game-desktop/main.py

# 构建Web版本
web-build:
	pygbag --build game-desktop/main.py

# 初始化项目，安装依赖
init:
	@pip install -U pip; \
	pip install -e ".[dev]"; \
	pre-commit install; \

# 安装pre-commit钩子
pre-commit:
	pre-commit install

# 对所有文件运行pre-commit检查
pre-commit-all:
	pre-commit run --all-files

# 格式化代码
format:
	black .

# 运行代码检查
lint:
	flake8 --config=../.flake8 --output-file=./coverage/flake8-report --format=default
