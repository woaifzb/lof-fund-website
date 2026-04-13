# LOF基金实时数据网站

这是一个展示LOF基金实时数据的网站，包含以下信息：
- 基金代码
- 基金名称  
- 实时溢价率
- 当日涨跌幅
- 限购数量

## 功能特点

1. **响应式设计** - 适配桌面和移动设备
2. **实时数据更新** - 每30秒自动刷新数据
3. **智能排序** - 点击表头可按不同字段排序
4. **搜索过滤** - 支持按基金代码或名称搜索
5. **颜色标识** - 涨跌用不同颜色直观显示

## 数据源说明

由于金融数据获取的复杂性，本网站提供了多种数据集成方案：

### 方案1：使用第三方API（推荐）
需要注册金融数据服务商API，如：
- 新浪财经API
- 东方财富API  
- 雪球API
- 腾讯财经API

在 `script.js` 中配置你的API密钥和端点。

### 方案2：本地JSON数据
可以将基金数据保存为 `data/funds.json` 文件，网站会自动加载。

### 方案3：手动更新
直接编辑HTML表格内容进行静态展示。

## 部署方式

### 静态文件部署
```bash
# 直接将整个目录上传到任何Web服务器
cp -r lof_fund_website /var/www/html/
```

### 本地预览
```bash
# 使用Python启动本地服务器
cd lof_fund_website
python3 -m http.server 8000
# 然后访问 http://localhost:8000
```

### Docker部署
```dockerfile
FROM nginx:alpine
COPY lof_fund_website/ /usr/share/nginx/html/
EXPOSE 80
```

## 自定义配置

编辑 `script.js` 文件中的以下配置：

```javascript
// API配置
const API_CONFIG = {
    endpoint: 'your-api-endpoint',
    apiKey: 'your-api-key',
    timeout: 10000
};

// 刷新间隔（毫秒）
const REFRESH_INTERVAL = 30000;

// 默认排序字段
const DEFAULT_SORT_FIELD = 'premiumRate';
const DEFAULT_SORT_ORDER = 'desc';
```

## 注意事项

1. **数据准确性**：金融数据实时性要求高，请确保使用可靠的API源
2. **API限制**：注意第三方API的调用频率限制
3. **合规性**：使用金融数据时请遵守相关法律法规
4. **缓存策略**：建议实现本地缓存避免频繁API调用

## 扩展功能

- 添加基金详情页
- 历史数据图表
- 自选基金功能
- 价格提醒功能
- 导出CSV功能

## 技术栈

- HTML5 + CSS3 + JavaScript (原生，无框架依赖)
- Responsive Web Design
- AJAX数据获取
- LocalStorage缓存

---
**注意**：由于金融数据的特殊性，实际部署时需要自行解决数据源问题。本网站提供完整的前端框架，数据获取逻辑已在 `script.js` 中预留接口。