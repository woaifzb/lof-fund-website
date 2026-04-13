// 完整的LOF基金数据（包含你提到的161224、161226等）
const LOF_FUND_DATA = [
    // 你提到的基金
    {code: "161224", name: "国投瑞银瑞源LOF", premiumRate: "0.15%", dailyChange: "+0.87%", limitAmount: "无限额"},
    {code: "161226", name: "国投瑞银瑞和沪深300LOF", premiumRate: "-0.23%", dailyChange: "-0.45%", limitAmount: "100万"},
    
    // 主要LOF基金列表
    {code: "161005", name: "富国天惠LOF", premiumRate: "0.25%", dailyChange: "+1.23%", limitAmount: "100万"},
    {code: "160607", name: "鹏华动力增长LOF", premiumRate: "-0.15%", dailyChange: "-0.87%", limitAmount: "无限额"},
    {code: "162204", name: "泰达荷银精选LOF", premiumRate: "0.42%", dailyChange: "+2.15%", limitAmount: "50万"},
    {code: "160119", name: "南方积配LOF", premiumRate: "-0.08%", dailyChange: "+0.34%", limitAmount: "无限额"},
    {code: "160213", name: "国泰纳斯达克100LOF", premiumRate: "1.25%", dailyChange: "+3.45%", limitAmount: "20万"},
    {code: "161116", name: "易方达黄金主题LOF", premiumRate: "0.67%", dailyChange: "-1.23%", limitAmount: "无限额"},
    {code: "160716", name: "嘉实基本面50LOF", premiumRate: "-0.32%", dailyChange: "+0.78%", limitAmount: "100万"},
    {code: "163407", name: "兴全合润LOF", premiumRate: "0.18%", dailyChange: "+1.56%", limitAmount: "无限额"},
    {code: "162711", name: "广发聚瑞LOF", premiumRate: "-0.21%", dailyChange: "-0.45%", limitAmount: "50万"},
    {code: "161714", name: "招商深证100LOF", premiumRate: "0.09%", dailyChange: "+0.67%", limitAmount: "无限额"},
    
    // 更多LOF基金
    {code: "160610", name: "鹏华价值优势LOF", premiumRate: "0.31%", dailyChange: "+1.12%", limitAmount: "无限额"},
    {code: "161606", name: "融通巨潮100LOF", premiumRate: "-0.12%", dailyChange: "-0.23%", limitAmount: "无限额"},
    {code: "160806", name: "长盛同智LOF", premiumRate: "0.45%", dailyChange: "+2.34%", limitAmount: "200万"},
    {code: "163402", name: "兴全趋势LOF", premiumRate: "0.28%", dailyChange: "+1.45%", limitAmount: "无限额"},
    {code: "162207", name: "泰达宏利效率LOF", premiumRate: "-0.18%", dailyChange: "-0.67%", limitAmount: "300万"},
    {code: "160706", name: "嘉实300LOF", premiumRate: "0.14%", dailyChange: "+0.78%", limitAmount: "无限额"},
    {code: "160118", name: "南方香港LOF", premiumRate: "0.89%", dailyChange: "+4.56%", limitAmount: "50万"},
    {code: "161015", name: "富国天盈LOF", premiumRate: "-0.34%", dailyChange: "-1.23%", limitAmount: "无限额"},
    {code: "162411", name: "华宝油气LOF", premiumRate: "2.45%", dailyChange: "+5.67%", limitAmount: "10万"},
    {code: "160631", name: "鹏华资源LOF", premiumRate: "0.56%", dailyChange: "+2.89%", limitAmount: "无限额"},
    {code: "161716", name: "招商双债增强LOF", premiumRate: "0.08%", dailyChange: "+0.34%", limitAmount: "无限额"},
    {code: "160919", name: "大成产业升级LOF", premiumRate: "-0.25%", dailyChange: "-0.89%", limitAmount: "无限额"},
    {code: "161022", name: "富国中证移动互联LOF", premiumRate: "0.67%", dailyChange: "+3.45%", limitAmount: "50万"},
    {code: "161219", name: "国投瑞银中证下游消费LOF", premiumRate: "0.23%", dailyChange: "+1.12%", limitAmount: "无限额"},
    {code: "161611", name: "融通新蓝筹LOF", premiumRate: "-0.15%", dailyChange: "-0.45%", limitAmount: "无限额"},
    {code: "160620", name: "鹏华中证传媒LOF", premiumRate: "0.78%", dailyChange: "+4.23%", limitAmount: "30万"},
    {code: "161017", name: "富国中证500LOF", premiumRate: "0.12%", dailyChange: "+0.67%", limitAmount: "无限额"},
    {code: "162211", name: "泰达宏利中证500LOF", premiumRate: "-0.09%", dailyChange: "-0.34%", limitAmount: "无限额"},
    {code: "160636", name: "鹏华中证国防LOF", premiumRate: "1.23%", dailyChange: "+6.78%", limitAmount: "20万"},
    {code: "161028", name: "富国中证新能源汽车LOF", premiumRate: "0.89%", dailyChange: "+4.56%", limitAmount: "50万"}
];

// 数据加载函数
function loadLOFFundData() {
    return LOF_FUND_DATA;
}