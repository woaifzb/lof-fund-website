#!/bin/bash

# Cloudflare Pages 部署脚本

echo "🚀 准备部署到 Cloudflare Pages..."

# 1. 初始化git仓库（如果还没有）
if [ ! -d ".git" ]; then
    git init
    echo "📁 Git仓库已初始化"
fi

# 2. 添加所有文件
git add .
git commit -m "Deploy LOF Fund Website - $(date)"

# 3. 提示用户下一步
echo ""
echo "✅ 本地准备完成！"
echo ""
echo "接下来请按以下步骤操作："
echo "1. 在 GitHub 上创建一个新的公开仓库"
echo "2. 复制仓库的HTTPS地址（如：https://github.com/yourname/lof-fund-website.git）"
echo "3. 运行以下命令连接远程仓库："
echo "   git remote add origin YOUR_GITHUB_URL"
echo "   git push -u origin main"
echo ""
echo "4. 访问 https://pages.cloudflare.com"
echo "5. 登录并选择你的GitHub仓库"
echo "6. 构建设置："
echo "   - Build command: (留空)"
echo "   - Output directory: ."
echo "7. 点击部署，等待几分钟即可获得访问地址！"

echo ""
echo "📱 部署完成后，你就可以在手机浏览器中访问你的LOF基金网站了！"