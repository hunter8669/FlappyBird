import { Link } from 'react-router-dom'
import { Play, Download, Star, Zap, Shield, Clock } from 'lucide-react'

const HomePage = () => {
  const gameFeatures = [
    {
      icon: <Star className="w-8 h-8 text-yellow-400" />,
      title: "经典模式",
      description: "原版Flappy Bird的无尽挑战，躲避管道获得高分"
    },
    {
      icon: <Clock className="w-8 h-8 text-blue-400" />,
      title: "限时挑战",
      description: "在90秒内获得尽可能高的分数，考验你的技巧"
    },
    {
      icon: <Zap className="w-8 h-8 text-purple-400" />,
      title: "反向模式",
      description: "重力反转，控制方式相反，带来全新体验"
    },
    {
      icon: <Shield className="w-8 h-8 text-red-400" />,
      title: "Boss战斗",
      description: "挑战四种不同Boss，使用武器系统击败它们"
    }
  ]

  const powerUps = [
    { name: "加速道具", color: "bg-orange-500", symbol: "S", description: "提高鸟儿飞行速度" },
    { name: "无敌道具", color: "bg-yellow-500", symbol: "I", description: "暂时无视碰撞" },
    { name: "慢动作", color: "bg-blue-500", symbol: "T", description: "减缓飞行速度" },
    { name: "缩小道具", color: "bg-purple-500", symbol: "-", description: "缩小鸟儿体积" }
  ]

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* 英雄区域 */}
      <div className="text-center mb-16">
        <div className="text-6xl mb-4 animate-bounce-slow">🐦</div>
        <h1 className="pixel-font text-4xl md:text-6xl text-white mb-4 drop-shadow-lg">
          FlapPy Bird
        </h1>
        <h2 className="pixel-font text-xl md:text-2xl text-yellow-300 mb-8">
          增强版
        </h2>
        <p className="text-lg text-white mb-8 max-w-2xl mx-auto leading-relaxed">
          经典小鸟游戏的全新体验！包含四种游戏模式、道具系统、Boss战斗等丰富内容。
          立即开始你的飞行冒险！
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            to="/play"
            className="inline-flex items-center px-8 py-4 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors animate-glow"
          >
            <Play className="w-5 h-5 mr-2" />
            <span className="pixel-font">立即游戏</span>
          </Link>
          <Link
            to="/download"
            className="inline-flex items-center px-8 py-4 bg-orange-500 hover:bg-orange-600 text-white rounded-lg transition-colors"
          >
            <Download className="w-5 h-5 mr-2" />
            <span className="pixel-font">下载游戏</span>
          </Link>
        </div>
      </div>

      {/* 游戏模式 */}
      <div className="mb-16">
        <h3 className="pixel-font text-2xl text-white text-center mb-8">🎮 游戏模式</h3>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {gameFeatures.map((feature, index) => (
            <div key={index} className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-6 text-center hover:bg-opacity-30 transition-all">
              <div className="flex justify-center mb-4">{feature.icon}</div>
              <h4 className="pixel-font text-lg text-white mb-3">{feature.title}</h4>
              <p className="text-sm text-gray-100 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 道具系统 */}
      <div className="mb-16">
        <h3 className="pixel-font text-2xl text-white text-center mb-8">⚡ 道具系统</h3>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {powerUps.map((powerUp, index) => (
            <div key={index} className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-6 text-center hover:bg-opacity-30 transition-all">
              <div className={`w-16 h-16 ${powerUp.color} rounded-full flex items-center justify-center mx-auto mb-4`}>
                <span className="pixel-font text-white text-xl">{powerUp.symbol}</span>
              </div>
              <h4 className="pixel-font text-lg text-white mb-3">{powerUp.name}</h4>
              <p className="text-sm text-gray-100 leading-relaxed">{powerUp.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* 特色功能 */}
      <div className="mb-16">
        <h3 className="pixel-font text-2xl text-white text-center mb-8">✨ 特色功能</h3>
        <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-8">
          <div className="grid md:grid-cols-2 gap-8">
            <div>
              <h4 className="pixel-font text-lg text-yellow-300 mb-4">🏆 Boss战斗系统</h4>
              <ul className="text-gray-100 space-y-2 text-sm">
                <li>• 四种不同类型的Boss挑战</li>
                <li>• 武器系统：基础子弹、三连发、激光、追踪导弹</li>
                <li>• Boss怒气系统和大招机制</li>
                <li>• 精美的战斗特效和过渡动画</li>
              </ul>
            </div>
            <div>
              <h4 className="pixel-font text-lg text-yellow-300 mb-4">🎨 用户界面</h4>
              <ul className="text-gray-100 space-y-2 text-sm">
                <li>• 精心设计的主菜单界面</li>
                <li>• 实时道具效果显示</li>
                <li>• 武器切换和弹药显示</li>
                <li>• 中文本地化支持</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* 开源信息 */}
      <div className="text-center">
        <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-6">
          <h4 className="pixel-font text-lg text-white mb-4">🔓 开源项目</h4>
          <p className="text-gray-100 text-sm mb-4">
            本项目基于pygame开发，完全开源。感谢原始Flappy Bird的创意！
          </p>
          <div className="text-xs text-gray-200">
            Version 1.2.0 | 支持Windows、macOS、Linux
          </div>
        </div>
      </div>
    </div>
  )
}

export default HomePage 