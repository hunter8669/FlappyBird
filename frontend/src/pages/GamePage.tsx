import { useEffect } from 'react'
import { AlertCircle, Info, Play, Download, ExternalLink } from 'lucide-react'

const GamePage = () => {
  // 自动跳转到真正的Web版游戏
  useEffect(() => {
    // 立即跳转到实际的游戏页面
    window.location.href = '/game.html'
  }, [])

  // 启动桌面版游戏指导
  const handlePlayDesktop = () => {
    alert('启动桌面版游戏：\n\n1. 确保已下载桌面版游戏\n2. 解压游戏文件\n3. 双击 main.py 文件\n4. 或在命令行运行: python main.py')
  }

  // 跳转到下载页面
  const handleGoToDownload = () => {
    window.location.href = '/download'
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="pixel-font text-3xl text-white mb-4">🎮 正在跳转到游戏...</h1>
        <p className="text-gray-100">
          即将进入Web版FlapPy Bird游戏
        </p>
        
        {/* 如果自动跳转失败的备用链接 */}
        <div className="mt-6">
          <a 
            href="/game.html" 
            className="inline-block bg-blue-500 hover:bg-blue-600 text-white py-3 px-6 rounded-lg transition-colors"
          >
            🎮 点击这里手动进入游戏
          </a>
        </div>
      </div>

      {/* 游戏容器 */}
      <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-6 mb-8">
        <div className="flex justify-center">
          <div className="w-full max-w-2xl">
            {/* 游戏加载占位符 */}
            <div className="bg-gray-800 rounded-lg p-8 text-center">
              <div className="text-6xl mb-4">🐦</div>
              <h3 className="pixel-font text-xl text-white mb-4">游戏准备中...</h3>
              <p className="text-gray-300 mb-6">
                Web版游戏正在开发中，即将上线！
              </p>
              
              {/* 临时解决方案按钮 */}
              <div className="space-y-4">
                <button 
                  onClick={handlePlayDesktop}
                  className="w-full bg-blue-500 hover:bg-blue-600 text-white py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
                >
                  <Play className="w-5 h-5 mr-2" />
                  <span className="pixel-font">启动桌面版游戏</span>
                </button>
                
                <button 
                  onClick={handleGoToDownload}
                  className="w-full bg-green-500 hover:bg-green-600 text-white py-3 px-6 rounded-lg transition-colors flex items-center justify-center"
                >
                  <Download className="w-5 h-5 mr-2" />
                  <span className="pixel-font">下载完整版</span>
                </button>
              </div>
              
              <div className="bg-yellow-500 bg-opacity-20 border border-yellow-400 rounded-lg p-4 mt-6">
                <div className="flex items-center justify-center text-yellow-300">
                  <Info className="w-5 h-5 mr-2" />
                  <span className="text-sm">目前可以下载桌面版体验完整游戏</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 游戏说明 */}
      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-6">
          <h3 className="pixel-font text-lg text-white mb-4">🎯 游戏控制</h3>
          <ul className="text-gray-100 space-y-2 text-sm">
            <li>• <strong>空格键/上箭头</strong>：控制小鸟飞行</li>
            <li>• <strong>上下箭头</strong>：主菜单选择模式</li>
            <li>• <strong>Q/E键</strong>：Boss模式切换武器</li>
            <li>• <strong>1-4数字键</strong>：快速选择武器</li>
          </ul>
        </div>

        <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-6">
          <h3 className="pixel-font text-lg text-white mb-4">⚠️ 游戏提示</h3>
          <ul className="text-gray-100 space-y-2 text-sm">
            <li>• 收集道具可以获得临时能力</li>
            <li>• Boss模式需要合理利用武器</li>
            <li>• 限时模式要在90秒内拿高分</li>
            <li>• 反向模式重力和控制都反转</li>
          </ul>
        </div>
      </div>

      {/* 开发进度说明 */}
      <div className="mt-8">
        <div className="bg-blue-500 bg-opacity-20 border border-blue-400 rounded-lg p-6">
          <div className="flex items-start">
            <AlertCircle className="w-6 h-6 text-blue-300 mr-3 mt-1" />
            <div>
              <h4 className="pixel-font text-lg text-blue-300 mb-2">🚧 开发状态</h4>
              <p className="text-gray-100 text-sm mb-3">
                Web版游戏正在使用pygbag技术将pygame游戏转换为Web版本。预计功能：
              </p>
              <ul className="text-gray-100 text-xs space-y-1">
                <li>✅ 完整的四种游戏模式</li>
                <li>✅ 道具系统和Boss战斗</li>
                <li>✅ 原生的游戏体验</li>
                <li>⏳ 浏览器兼容性优化</li>
                <li>⏳ 触控设备支持</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GamePage 