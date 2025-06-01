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
    version: 'v1.2.0',
    size: '~25-50MB',
    updated: '2024-01-15',
    type: 'Windows EXE',
    downloads: '1,234+'
  };

  // 下载处理函数
  const handleDownload = async () => {
    try {
      console.log('开始下载游戏文件...');
      
      // 使用窗口打开方式下载（Replit环境兼容）
      window.open('/api/downloads/desktop', '_blank');
      
      // 记录下载统计
      try {
        await fetch('/api/downloads/track', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            type: 'desktop',
            version: downloadStats.version,
            timestamp: new Date().toISOString()
          })
        });
        console.log('下载统计已记录');
      } catch (statsError) {
        console.warn('统计记录失败:', statsError);
      }
      
      // 显示下载提示
      setTimeout(() => {
        alert('🎉 下载已开始！\n\n📦 文件：FlapPyBird-v1.2.0.zip\n\n💡 如果没有开始下载：\n1. 检查浏览器弹窗设置\n2. 允许从此站点下载\n3. 手动访问：' + window.location.origin + '/api/downloads/desktop');
      }, 500);
      
    } catch (error) {
      console.error('下载失败:', error);
      const directLink = window.location.origin + '/api/downloads/desktop';
      alert(`⚠️ 下载失败\n\n🔗 手动下载链接：\n${directLink}\n\n📋 复制上面链接到浏览器地址栏\n或右键选择"另存为"`);
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
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-pink-600 py-8">
      <div className="container mx-auto px-4">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="pixel-font text-3xl text-white mb-4">📦 下载游戏</h1>
          <p className="text-blue-100 text-lg">
            下载独立的EXE游戏文件，无需Python环境即可游戏
          </p>
        </div>

        <div className="max-w-4xl mx-auto grid gap-8">
          
          {/* 主要下载区域 */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-8 border border-white/20">
            {/* 桌面版下载 */}
            <div className="text-center">
              <div className="text-6xl mb-4">🎮</div>
              <h2 className="pixel-font text-2xl text-white mb-6">Windows 桌面版</h2>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 text-sm">
                <div className="bg-black/20 rounded-lg p-3">
                  <div className="text-gray-200">版本</div>
                  <span className="text-white font-bold">{downloadStats.version}</span>
                </div>
                <div className="bg-black/20 rounded-lg p-3">
                  <div className="text-gray-200">大小</div>
                  <span className="text-white font-bold">{downloadStats.size}</span>
                </div>
                <div className="bg-black/20 rounded-lg p-3">
                  <div className="text-gray-200">更新</div>
                  <span className="text-white font-bold">{downloadStats.updated}</span>
                </div>
                <div className="bg-black/20 rounded-lg p-3">
                  <div className="text-gray-200">下载次数</div>
                  <span className="text-white font-bold">{downloadStats.downloads}</span>
                </div>
              </div>

              <button 
                className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white px-8 py-4 rounded-full text-lg font-bold transition-all duration-300 transform hover:scale-105 shadow-lg flex items-center justify-center mx-auto"
                onClick={handleDownload}
              >
                <span className="text-2xl mr-2">⬇️</span>
                <span className="pixel-font">下载独立版游戏</span>
              </button>

              <div className="text-center mt-4 space-y-2">
                <p className="text-green-200 text-sm">
                  ✅ 包含独立EXE文件，无需安装Python
                </p>
                <p className="text-blue-200 text-sm">
                  🔧 智能检测：优先提供EXE，备选源码+构建工具
                </p>
                <p className="text-yellow-200 text-sm">
                  🌟 支持所有Windows版本（Win7/10/11）
                </p>
              </div>
            </div>
          </div>

          {/* 在线版本推荐 */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <div className="text-center">
              <div className="text-4xl mb-3">🌐</div>
              <h3 className="pixel-font text-xl text-white mb-4">在线版本（推荐体验）</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 text-sm">
                <div className="flex items-center justify-center text-green-200">
                  <span className="mr-2">✅</span>无需下载安装
                </div>
                <div className="flex items-center justify-center text-blue-200">
                  <span className="mr-2">🚀</span>即开即玩
                </div>
                <div className="flex items-center justify-center text-purple-200">
                  <span className="mr-2">📱</span>支持所有设备
                </div>
              </div>

              <a 
                href="/game" 
                className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-6 py-3 rounded-full font-bold transition-all duration-300 transform hover:scale-105 shadow-lg inline-flex items-center"
              >
                <span className="text-xl mr-2">🎮</span>
                <span className="pixel-font">立即游戏</span>
              </a>
            </div>
          </div>

          {/* 版本对比 */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 className="pixel-font text-xl text-white mb-4 text-center">📊 版本对比</h3>
            
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="text-left text-white p-3">特性</th>
                    <th className="text-center text-green-300 p-3">🌐 在线版</th>
                    <th className="text-center text-blue-300 p-3">💻 下载版</th>
                  </tr>
                </thead>
                <tbody className="text-gray-200">
                  <tr className="border-b border-white/10">
                    <td className="p-3">安装要求</td>
                    <td className="text-center p-3">无</td>
                    <td className="text-center p-3">解压即用</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-3">网络要求</td>
                    <td className="text-center p-3">需要联网</td>
                    <td className="text-center p-3">离线可玩</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-3">游戏模式</td>
                    <td className="text-center p-3">完整四种模式</td>
                    <td className="text-center p-3">完整四种模式</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-3">性能表现</td>
                    <td className="text-center p-3">优秀</td>
                    <td className="text-center p-3">最佳</td>
                  </tr>
                  <tr className="border-b border-white/10">
                    <td className="p-3">更新方式</td>
                    <td className="text-center p-3">自动</td>
                    <td className="text-center p-3">手动下载</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* 安装说明 */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 className="pixel-font text-xl text-white mb-4 text-center">📋 安装说明</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-green-300 font-bold mb-2">🎯 EXE独立版（推荐）</h4>
                <ol className="text-gray-200 space-y-1 text-sm">
                  <li>1. 下载并解压ZIP文件</li>
                  <li>2. 双击"FlapPyBird.exe"</li>
                  <li>3. Windows安全提示选择"仍要运行"</li>
                  <li>4. 开始游戏！</li>
                </ol>
              </div>
              
              <div>
                <h4 className="text-blue-300 font-bold mb-2">🔧 源码版（需Python）</h4>
                <ol className="text-gray-200 space-y-1 text-sm">
                  <li>1. 下载并解压ZIP文件</li>
                  <li>2. 双击"构建EXE.bat"生成EXE</li>
                  <li>3. 或双击"启动游戏.bat"直接运行</li>
                  <li>4. 首次运行会自动安装依赖</li>
                </ol>
              </div>
            </div>
          </div>

          {/* 系统要求 */}
          <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
            <h3 className="pixel-font text-xl text-white mb-4 text-center">⚙️ 系统要求</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-gray-200">
              <div>
                <h4 className="text-green-300 font-bold mb-2">EXE独立版</h4>
                <ul className="space-y-1 text-sm">
                  <li>• Windows 7/8/10/11 (64位)</li>
                  <li>• 至少100MB可用空间</li>
                  <li>• 分辨率：1024x768或更高</li>
                  <li>• 无需其他软件</li>
                </ul>
              </div>
              
              <div>
                <h4 className="text-blue-300 font-bold mb-2">源码版</h4>
                <ul className="space-y-1 text-sm">
                  <li>• Windows 7/8/10/11</li>
                  <li>• Python 3.9或更高版本</li>
                  <li>• 网络连接（首次安装依赖）</li>
                  <li>• 至少200MB可用空间</li>
                </ul>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default DownloadPage; 