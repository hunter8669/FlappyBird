import React from 'react';

const DownloadPage = () => {
  const systemRequirements = [
    { system: 'Windows', version: 'Windows 10/11', icon: '🪟' },
    { system: 'macOS', version: 'macOS 10.15+', icon: '🍎' },
    { system: 'Linux', version: 'Ubuntu 20.04+', icon: '🐧' }
  ];

  const features = [
    '完整的四种游戏模式',
    'Boss战斗系统和武器系统',
    '道具系统和特效',
    '中文界面支持',
    '高分保存功能',
    '流畅的60FPS游戏体验'
  ];

  const downloadStats = {
    version: '1.2.0',
    size: '约15MB',
    updated: '2023-10-15',
    downloads: '1,234+'
  };

  // 下载处理函数
  const handleDownload = async () => {
    try {
      console.log('开始下载游戏文件...');
      
      // 创建隐藏的下载链接
      const link = document.createElement('a');
      link.href = 'http://localhost:8000/api/downloads/desktop';
      link.download = 'FlapPyBird-Desktop-v1.2.0.zip';
      link.style.display = 'none';
      
      // 添加到页面并触发下载
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      console.log('下载已开始...');
      
      // 记录下载统计
      try {
        await fetch('http://localhost:8000/api/downloads/track', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            type: 'desktop',
            version: '1.2.0',
            timestamp: new Date().toISOString()
          })
        });
        console.log('下载统计已记录');
      } catch (trackError) {
        console.error('记录统计失败:', trackError);
      }
      
      // 显示下载成功提示
      setTimeout(() => {
        alert('🎉 下载已开始！\n\n文件名: FlapPyBird-Desktop-v1.2.0.zip\n\n下载完成后：\n1. 解压ZIP文件\n2. 双击"启动桌面游戏.bat"\n3. 或运行 game-desktop/main.py');
      }, 1000);
      
    } catch (error) {
      console.error('下载请求失败:', error);
      alert(`⚠️ 下载失败\n\n错误信息: ${error.message}\n\n临时解决方案:\n1. 点击"启动本地游戏"\n2. 或手动运行 game-desktop/main.py`);
    }
  };

  // 启动本地游戏
  const handlePlayLocal = () => {
    alert('启动本地游戏：\n\n方法1: 双击 "启动桌面游戏.bat"\n方法2: 进入 game-desktop 目录，运行:\n   python main.py\n\n⚠️ 确保已安装:\n• Python 3.9+\n• pygame库');
  };

  // 获取GitHub源码
  const handleSourceCode = () => {
    window.open('https://github.com/yourusername/FlapPyBird', '_blank');
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="text-center mb-12">
        <h1 className="pixel-font text-3xl text-white mb-4">📦 下载游戏</h1>
        <p className="text-gray-100 text-lg">
          获取完整版FlapPy Bird，享受最佳游戏体验
        </p>
      </div>

      {/* 主要下载区域 */}
      <div className="grid lg:grid-cols-2 gap-8 mb-12">
        {/* 桌面版下载 */}
        <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-8">
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">🖥️</div>
            <h2 className="pixel-font text-2xl text-white mb-2">桌面版</h2>
            <p className="text-gray-100">适用于Windows、macOS、Linux</p>
          </div>

          <div className="space-y-4 mb-6">
            <div className="flex justify-between text-sm">
              <span className="text-gray-200">版本：</span>
              <span className="text-white">{downloadStats.version}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-200">大小：</span>
              <span className="text-white">{downloadStats.size}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-200">更新时间：</span>
              <span className="text-white">{downloadStats.updated}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-200">下载次数：</span>
              <span className="text-white">{downloadStats.downloads}</span>
            </div>
          </div>

          <button className="w-full bg-green-500 hover:bg-green-600 text-white py-4 px-6 rounded-lg transition-colors flex items-center justify-center" onClick={handleDownload}>
            <span className="text-xl mr-2">📥</span>
            <span className="pixel-font">下载桌面版</span>
          </button>

          <button className="w-full mt-3 bg-blue-500 hover:bg-blue-600 text-white py-3 px-6 rounded-lg transition-colors flex items-center justify-center" onClick={handlePlayLocal}>
            <span className="text-lg mr-2">🎮</span>
            <span className="pixel-font">启动本地游戏</span>
          </button>

          <p className="text-xs text-gray-300 mt-4 text-center">
            自动检测系统类型并下载对应版本
          </p>
        </div>

        {/* Web版信息 */}
        <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-8">
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">🌐</div>
            <h2 className="pixel-font text-2xl text-white mb-2">Web版</h2>
            <p className="text-gray-100">直接在浏览器中游戏</p>
          </div>

          <div className="space-y-4 mb-6">
            <div className="text-center">
              <div className="text-4xl mb-2">🚧</div>
              <p className="text-gray-200 text-sm">正在开发中</p>
            </div>
            <ul className="text-sm text-gray-100 space-y-2">
              <li>✅ 无需下载安装</li>
              <li>✅ 跨平台兼容</li>
              <li>⏳ pygbag转换中</li>
              <li>⏳ 移动端优化</li>
            </ul>
          </div>

          <button 
            disabled 
            className="w-full bg-gray-500 text-gray-300 py-4 px-6 rounded-lg cursor-not-allowed flex items-center justify-center"
          >
            <span className="text-xl mr-2">🌐</span>
            <span className="pixel-font">即将推出</span>
          </button>

          <p className="text-xs text-gray-300 mt-4 text-center">
            Web版本正在开发中，敬请期待
          </p>
        </div>
      </div>

      {/* 系统要求 */}
      <div className="mb-12">
        <h3 className="pixel-font text-2xl text-white text-center mb-8">💻 系统要求</h3>
        <div className="grid md:grid-cols-3 gap-6">
          {systemRequirements.map((req, index) => (
            <div key={index} className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-6 text-center">
              <div className="text-4xl mb-4">{req.icon}</div>
              <h4 className="pixel-font text-lg text-white mb-2">{req.system}</h4>
              <p className="text-gray-100 text-sm">{req.version}</p>
            </div>
          ))}
        </div>
        <div className="text-center mt-6">
          <p className="text-gray-200 text-sm">
            💾 需要Python 3.9+环境 | 🎮 需要pygame 2.4.0+
          </p>
        </div>
      </div>

      {/* 游戏特色 */}
      <div className="mb-12">
        <h3 className="pixel-font text-2xl text-white text-center mb-8">✨ 完整版特色</h3>
        <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-8">
          <div className="grid md:grid-cols-2 gap-6">
            {features.map((feature, index) => (
              <div key={index} className="flex items-center space-x-3">
                <span className="text-green-400 text-xl">✅</span>
                <span className="text-gray-100">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 移动版预告 */}
      <div className="text-center">
        <div className="bg-gradient-to-r from-purple-500 to-pink-500 bg-opacity-20 backdrop-blur-sm rounded-lg p-8">
          <div className="text-6xl mb-4">📱</div>
          <h3 className="pixel-font text-xl text-white mb-4">📱 移动版本</h3>
          <p className="text-gray-100 mb-6">
            iOS和Android版本正在规划中，将支持触控操作和云存档同步
          </p>
          <div className="flex justify-center space-x-4">
            <div className="px-4 py-2 bg-white bg-opacity-20 rounded-lg">
              <span className="text-sm text-gray-200">🍎 iOS版本</span>
            </div>
            <div className="px-4 py-2 bg-white bg-opacity-20 rounded-lg">
              <span className="text-sm text-gray-200">🤖 Android版本</span>
            </div>
          </div>
        </div>
      </div>

      {/* 安装说明 */}
      <div className="mt-12">
        <div className="bg-blue-500 bg-opacity-20 border border-blue-400 rounded-lg p-6">
          <h4 className="pixel-font text-lg text-blue-300 mb-4">📋 安装说明</h4>
          <ol className="text-gray-100 space-y-2 text-sm">
            <li>1. 下载对应系统的安装包</li>
            <li>2. 确保系统已安装Python 3.9+</li>
            <li>3. 运行安装程序或解压游戏文件</li>
            <li>4. 双击main.py或运行程序启动游戏</li>
            <li>5. 享受游戏！如有问题请查看README文档</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default DownloadPage; 