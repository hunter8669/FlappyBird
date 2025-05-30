# FlapPy Bird 增强版 - 前后端分离架构

这是经典FlappyBird游戏的现代化增强版本，采用前后端分离架构，支持Web端和桌面端游戏体验。

## 🏗️ 项目架构

```
FlapPyBird-master1/
├── frontend/                 # 前端React项目
│   ├── src/                 # 前端源码
│   │   ├── components/      # React组件
│   │   ├── pages/           # 页面组件
│   │   └── assets/         # 前端资源
│   └── package.json        # 前端依赖
├── backend/                 # 后端FastAPI项目
│   ├── app/                # API应用
│   │   ├── api/           # API路由
│   │   ├── models/        # 数据模型
│   └── requirements.txt    # Python依赖
├── game-web/               # Web版游戏 (开发中)
├── game-desktop/           # 桌面版游戏
│   ├── src/               # 游戏源码
│   ├── assets/            # 游戏资源
│   └── main.py            # 游戏入口
└── docs/                   # 项目文档
```

## 🎮 游戏特色

### 四种游戏模式

1. **经典模式**：原版Flappy Bird的无尽挑战，躲避管道获得高分
2. **限时挑战**：在90秒内获得尽可能高的分数，考验你的技巧
3. **反向模式**：重力反转，控制方式相反，带来全新体验
4. **Boss战斗模式**：挑战四种不同的Boss，使用武器系统击败它们

### Boss战斗系统

在Boss战斗模式中，玩家将依次面对四种不同类型的Boss：

1. **普通Boss**（红色）：基础型Boss，攻击模式简单，是入门级挑战
2. **速度型Boss**（蓝色）：移动和攻击速度更快，需要更敏捷的操作
3. **分裂型Boss**（绿色）：可以分裂出小型攻击物，增加战斗难度
4. **坦克型Boss**（紫色）：最终Boss，拥有更高的血量和防御力

### Boss战斗系统特性

- **武器系统**：玩家拥有四种不同的武器可以切换使用
  - 基础子弹：无限弹药，中等伤害
  - 三连发：有限弹药，可同时发射三发子弹
  - 激光：有限弹药，快速连射的激光束
  - 追踪导弹：有限弹药，会自动追踪Boss的位置

- **武器切换**：使用Q和E键切换武器，或使用数字键1-4直接选择

- **Boss进化**：随着Boss生命值降低，攻击模式会变得更加激烈

- **Boss转场**：击败一个Boss后会有过渡动画，并补充部分武器弹药

- **Boss怒气系统**：每个Boss都拥有怒气值，随着战斗的进行，怒气值会不断上升
  - 怒气条显示：位于Boss下方，随怒气值增加从紫色渐变至红色
  - 怒气获取：Boss受到玩家攻击或随时间自动积累
  - 怒气阈值：每种Boss有不同的怒气阈值和获取速率
    - 普通Boss（红色）：中等怒气获取速度，阈值90
    - 速度型Boss（蓝色）：最快的怒气获取速度，阈值80
    - 分裂型Boss（绿色）：怒气获取较慢，阈值95
    - 坦克型Boss（紫色）：怒气获取最慢，阈值100
  - 怒气机制：血量低于50%时，怒气获取速度额外提升50%

- **Boss大招系统**：怒气满时会触发大招，有明显的警告特效和音效提示
  - 大招准备阶段：触发大招前有2秒警告时间，伴随闪烁特效和警告提示
  - 大招类型：每种Boss拥有独特的大招技能
    - 普通Boss（红色）：**火焰爆发** - 发射多个高伤害火球，覆盖范围广
    - 速度型Boss（蓝色）：**闪电风暴** - 释放多道高速闪电，穿透性强
    - 分裂型Boss（绿色）：**分裂爆炸** - 向全方位发射分裂子弹，难以躲避
    - 坦克型Boss（紫色）：**能量冲击** - 发射巨大的能量波，伤害极高
  - 视觉特效：每种大招都有独特的粒子效果和颜色，提升战斗观感
  - 冷却机制：大招释放后进入冷却时间，期间不会积累怒气

### 道具系统

游戏包含四种道具，每种道具都有不同的效果：

1. **加速道具**（橙色，标识S）：提高鸟儿的飞行速度
2. **无敌道具**（金色，标识I）：让鸟儿暂时无视碰撞
3. **慢动作道具**（蓝色，标识T）：减缓鸟儿的飞行速度
4. **缩小道具**（紫色，标识-）：缩小鸟儿的体积

## 🚀 快速开始

### 桌面版游戏

1. 确保安装了Python 3.9或更高版本
2. 安装依赖：`pip install pygame`
3. 运行游戏：
   ```bash
   cd game-desktop
   python main.py
   ```

### 前端开发（需要Node.js）

1. 安装依赖：
   ```bash
   cd frontend
   npm install
   ```
2. 启动开发服务器：
   ```bash
   npm run dev
   ```
3. 在浏览器中访问：http://localhost:3000

### 后端开发

1. 安装依赖：
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. 启动API服务器：
   ```bash
   python main.py
   ```
3. API文档访问：http://localhost:8000/docs

## 🌐 Web版本（开发中）

Web版本正在使用pygbag技术将pygame游戏转换为浏览器兼容版本：

- ✅ 完整的四种游戏模式
- ✅ 道具系统和Boss战斗
- ✅ 原生的游戏体验
- ⏳ 浏览器兼容性优化
- ⏳ 触控设备支持

## 🎯 控制方式

- **飞行**：使用空格键或上箭头控制鸟儿飞行
- **射击**（仅Boss模式）：空格键同时也是射击键
- **切换武器**（仅Boss模式）：Q和E键，或数字键1-4
- **选择模式**：在主菜单使用上下箭头选择模式，空格确认

## 🛠️ 技术栈

### 前端
- React 18 + TypeScript
- Vite (构建工具)
- Tailwind CSS (样式框架)
- React Router (路由管理)

### 后端
- FastAPI (Python Web框架)
- SQLAlchemy (ORM)
- SQLite (数据库)
- Uvicorn (ASGI服务器)

### 游戏
- Pygame (游戏引擎)
- Pygbag (Web转换工具)

## 📈 版本更新

**v1.2.0 - 2023-10-15**
- 🏗️ **重大架构升级**：前后端分离架构
- 🌐 **Web前端**：现代化的React展示页面
- 🔗 **API后端**：FastAPI驱动的后端服务
- 📊 **数据统计**：下载统计和用户管理
- 🚧 **Web游戏**：pygbag Web版本开发中

**v1.1.0 - 2023-07-10**
- 新增Boss战斗模式
- 添加四种武器系统
- 实现四种不同类型的Boss
- 添加Boss战斗特效和过渡动画

## 🔮 开发路线图

### 第一阶段（当前）
- ✅ 前后端架构搭建
- ✅ 桌面版游戏迁移
- ✅ 前端展示页面
- ⏳ pygbag Web转换测试

### 第二阶段
- 用户注册登录系统
- 游戏数据同步
- 排行榜功能
- Web版游戏完善

### 第三阶段
- 移动端适配
- 社交功能
- 数据分析
- 性能优化

## 🤝 贡献指南

欢迎提交Issues和Pull Requests！

## 📄 开源协议

本项目基于pygame开发，完全开源。感谢原始Flappy Bird的创意！

## 🙏 致谢

基于原始Flappy Bird游戏开发，感谢原作者的创意和pygame社区的支持。
