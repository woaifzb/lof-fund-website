// LOF基金数据处理脚本
class LOFFundTracker {
    constructor() {
        this.funds = [];
        this.filteredFunds = [];
        this.currentPage = 1;
        this.itemsPerPage = 50;
        this.sortColumn = null;
        this.sortDirection = 'asc';
        
        this.init();
    }
    
    init() {
        this.loadFundData();
        this.bindEvents();
        this.renderTable();
    }
    
    loadFundData() {
        this.funds = [
            {code: "161005", name: "富国天惠LOF", premiumRate: "0.25%", dailyChange: "+1.23%", limitAmount: "100万", subscriptionStatus: "open"},
            {code: "160607", name: "鹏华动力增长LOF", premiumRate: "-0.15%", dailyChange: "-0.87%", limitAmount: "无限额", subscriptionStatus: "open"},
            {code: "162204", name: "泰达荷银精选LOF", premiumRate: "0.42%", dailyChange: "+2.15%", limitAmount: "50万", subscriptionStatus: "open"},
            {code: "160119", name: "南方积配LOF", premiumRate: "-0.08%", dailyChange: "+0.34%", limitAmount: "无限额", subscriptionStatus: "open"},
            {code: "160213", name: "国泰纳斯达克100LOF", premiumRate: "1.25%", dailyChange: "+3.45%", limitAmount: "20万", subscriptionStatus: "open"},
            {code: "161116", name: "易方达黄金主题LOF", premiumRate: "0.67%", dailyChange: "-1.23%", limitAmount: "无限额", subscriptionStatus: "paused"},
            {code: "160716", name: "嘉实基本面50LOF", premiumRate: "-0.32%", dailyChange: "+0.78%", limitAmount: "100万", subscriptionStatus: "open"},
            {code: "163407", name: "兴全合润LOF", premiumRate: "0.18%", dailyChange: "+1.56%", limitAmount: "无限额", subscriptionStatus: "open"},
            {code: "162711", name: "广发聚瑞LOF", premiumRate: "-0.21%", dailyChange: "-0.45%", limitAmount: "50万", subscriptionStatus: "open"},
            {code: "161714", name: "招商深证100LOF", premiumRate: "0.09%", dailyChange: "+0.67%", limitAmount: "无限额", subscriptionStatus: "open"},
            {code: "161224", name: "国投瑞银瑞源LOF", premiumRate: "0.33%", dailyChange: "+0.89%", limitAmount: "无限额", subscriptionStatus: "open"},
            {code: "161226", name: "国投瑞银瑞和沪深300LOF", premiumRate: "-0.12%", dailyChange: "+1.23%", limitAmount: "50万", subscriptionStatus: "paused"},
            {code: "160706", name: "嘉实300LOF", premiumRate: "0.15%", dailyChange: "+0.45%", limitAmount: "无限额", subscriptionStatus: "open"},
            {code: "162207", name: "泰达宏利效率LOF", premiumRate: "-0.25%", dailyChange: "-1.12%", limitAmount: "30万", subscriptionStatus: "open"},
            {code: "163402", name: "兴全趋势LOF", premiumRate: "0.28%", dailyChange: "+2.34%", limitAmount: "无限额", subscriptionStatus: "open"},
            {code: "160806", name: "长盛同智LOF", premiumRate: "0.19%", dailyChange: "-0.78%", limitAmount: "20万", subscriptionStatus: "open"},
            {code: "161606", name: "融通巨潮100LOF", premiumRate: "-0.05%", dailyChange: "+0.23%", limitAmount: "无限额", subscriptionStatus: "open"},
            {code: "162209", name: "泰达宏利市值LOF", premiumRate: "0.41%", dailyChange: "+1.67%", limitAmount: "100万", subscriptionStatus: "open"},
            {code: "160917", name: "大成深证成长40LOF", premiumRate: "-0.18%", dailyChange: "-0.56%", limitAmount: "无限额", subscriptionStatus: "open"},
            {code: "161017", name: "富国500LOF", premiumRate: "0.22%", dailyChange: "+0.98%", limitAmount: "50万", subscriptionStatus: "open"},
            {code: "160217", name: "国泰国证食品饮料LOF", premiumRate: "1.45%", dailyChange: "+4.23%", limitAmount: "10万", subscriptionStatus: "open"},
            {code: "161119", name: "易方达中证银行LOF", premiumRate: "-0.35%", dailyChange: "-1.45%", limitAmount: "无限额", subscriptionStatus: "paused"},
            {code: "160717", name: "嘉实恒生中国企业LOF", premiumRate: "0.87%", dailyChange: "+2.78%", limitAmount: "20万", subscriptionStatus: "open"},
            {code: "162211", name: "泰达宏利中证500LOF", premiumRate: "0.12%", dailyChange: "+0.67%", limitAmount: "无限额", subscriptionStatus: "open"},
            {code: "163808", name: "中银中小盘LOF", premiumRate: "-0.28%", dailyChange: "-1.34%", limitAmount: "30万", subscriptionStatus: "open"},
            {code: "161713", name: "招商大盘蓝筹LOF", premiumRate: "0.16%", dailyChange: "+0.89%", limitAmount: "无限额", subscriptionStatus: "open"},
            {code: "160610", name: "鹏华资源LOF", premiumRate: "2.34%", dailyChange: "+5.67%", limitAmount: "5万", subscriptionStatus: "paused"},
            {code: "162213", name: "泰达宏利逆向策略LOF", premiumRate: "-0.19%", dailyChange: "-0.87%", limitAmount: "无限额", subscriptionStatus: "open"},
            {code: "161015", name: "富国天成红利LOF", premiumRate: "0.31%", dailyChange: "+1.45%", limitAmount: "100万", subscriptionStatus: "open"},
            {code: "160616", name: "鹏华丰润债券LOF", premiumRate: "0.05%", dailyChange: "+0.12%", limitAmount: "无限额", subscriptionStatus: "open"}
        ];
        
        this.filteredFunds = [...this.funds];
        this.updateLastUpdate();
    }
    
    bindEvents() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterFunds(e.target.value);
            });
        }

        // 添加排序事件监听
        const headers = document.querySelectorAll('#fundTable th');
        headers.forEach((header, index) => {
            header.addEventListener('click', () => {
                this.sortTable(index);
            });
        });
    }
    
    sortTable(columnIndex) {
        // 更新排序状态
        if (this.sortColumn === columnIndex) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = columnIndex;
            this.sortDirection = 'asc';
        }

        // 清除所有表头的排序指示器
        const headers = document.querySelectorAll('#fundTable th');
        headers.forEach(header => {
            header.textContent = header.textContent.replace(/ ▼| ▲/g, '');
        });

        // 设置当前排序列的指示器
        const currentHeader = headers[columnIndex];
        currentHeader.textContent += this.sortDirection === 'asc' ? ' ▲' : ' ▼';

        // 执行排序
        this.filteredFunds.sort((a, b) => {
            let valA, valB;

            switch(columnIndex) {
                case 0: // 基金代码
                    valA = a.code;
                    valB = b.code;
                    break;
                case 1: // 基金名称
                    valA = a.name.toLowerCase();
                    valB = b.name.toLowerCase();
                    break;
                case 2: // 实时溢价率
                    valA = parseFloat(a.premiumRate.replace('%', ''));
                    valB = parseFloat(b.premiumRate.replace('%', ''));
                    break;
                case 3: // 当日涨跌幅
                    valA = parseFloat(a.dailyChange.replace('%', '').replace('+', ''));
                    valB = parseFloat(b.dailyChange.replace('%', '').replace('+', ''));
                    break;
                case 4: // 限购数量
                    // 暂停申购的基金排在最后
                    if (a.subscriptionStatus === 'paused' && b.subscriptionStatus !== 'paused') return 1;
                    if (a.subscriptionStatus !== 'paused' && b.subscriptionStatus === 'paused') return -1;
                    
                    if (a.subscriptionStatus === 'paused') return 0;
                    
                    if (a.limitAmount === '无限额') return 1;
                    if (b.limitAmount === '无限额') return -1;
                    valA = parseFloat(a.limitAmount.replace('万', ''));
                    valB = parseFloat(b.limitAmount.replace('万', ''));
                    break;
                default:
                    return 0;
            }

            // 处理NaN情况
            if (isNaN(valA) && !isNaN(valB)) return 1;
            if (!isNaN(valA) && isNaN(valB)) return -1;
            if (isNaN(valA) && isNaN(valB)) return 0;

            if (this.sortDirection === 'asc') {
                return valA > valB ? 1 : -1;
            } else {
                return valA < valB ? 1 : -1;
            }
        });

        this.currentPage = 1;
        this.renderTable();
    }
    
    filterFunds(searchTerm) {
        if (!searchTerm) {
            this.filteredFunds = [...this.funds];
        } else {
            const term = searchTerm.toLowerCase();
            this.filteredFunds = this.funds.filter(fund => 
                fund.code.includes(term) || 
                fund.name.toLowerCase().includes(term)
            );
        }
        this.currentPage = 1;
        this.renderTable();
    }
    
    renderTable() {
        const tbody = document.getElementById('fundTableBody');
        if (!tbody) return;
        
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = Math.min(startIndex + this.itemsPerPage, this.filteredFunds.length);
        const pageFunds = this.filteredFunds.slice(startIndex, endIndex);
        
        tbody.innerHTML = '';
        pageFunds.forEach(fund => {
            const row = document.createElement('tr');
            
            // 基金代码
            const codeCell = document.createElement('td');
            codeCell.textContent = fund.code;
            row.appendChild(codeCell);
            
            // 基金名称
            const nameCell = document.createElement('td');
            nameCell.textContent = fund.name;
            row.appendChild(nameCell);
            
            // 溢价率
            const premiumCell = document.createElement('td');
            premiumCell.textContent = fund.premiumRate;
            if (fund.premiumRate.startsWith('-')) {
                premiumCell.className = 'negative';
            } else if (fund.premiumRate !== '0.00%') {
                premiumCell.className = 'positive';
            }
            row.appendChild(premiumCell);
            
            // 涨跌幅
            const changeCell = document.createElement('td');
            changeCell.textContent = fund.dailyChange;
            if (fund.dailyChange.startsWith('-')) {
                changeCell.className = 'negative';
            } else if (fund.dailyChange !== '+0.00%') {
                changeCell.className = 'positive';
            }
            row.appendChild(changeCell);
            
            // 限购数量 + 暂停申购标记
            const limitCell = document.createElement('td');
            if (fund.subscriptionStatus === 'paused') {
                limitCell.textContent = '暂停';
                limitCell.className = 'subscription-paused';
                // 添加悬停提示
                limitCell.title = '该基金当前暂停申购';
            } else {
                limitCell.textContent = fund.limitAmount;
                if (fund.limitAmount === '无限额') {
                    limitCell.className = 'unlimited';
                }
            }
            row.appendChild(limitCell);
            
            tbody.appendChild(row);
        });
        
        this.updatePagination();
    }
    
    updatePagination() {
        const totalPages = Math.ceil(this.filteredFunds.length / this.itemsPerPage);
        document.getElementById('pageInfo').textContent = `第 ${this.currentPage} 页，共 ${totalPages} 页`;
        
        document.getElementById('prevBtn').disabled = this.currentPage <= 1;
        document.getElementById('nextBtn').disabled = this.currentPage >= totalPages;
    }
    
    updateLastUpdate() {
        const now = new Date();
        const timeString = now.toLocaleString('zh-CN');
        document.getElementById('lastUpdate').textContent = `最后更新: ${timeString}`;
    }
    
    changePage(direction) {
        const totalPages = Math.ceil(this.filteredFunds.length / this.itemsPerPage);
        this.currentPage += direction;
        
        if (this.currentPage < 1) this.currentPage = 1;
        if (this.currentPage > totalPages) this.currentPage = totalPages;
        
        this.renderTable();
    }
    
    refreshData() {
        this.loadFundData();
        this.renderTable();
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.lofTracker = new LOFFundTracker();
});