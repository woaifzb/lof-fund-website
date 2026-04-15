// LOF 基金数据处理脚本 - 文武的天兵
class LOFFundTracker {
    constructor() {
        this.funds = [];
        this.filteredFunds = [];
        this.sortColumn = null;
        this.sortDirection = 'asc';
        
        this.init();
    }
    
    init() {
        this.loadFundData();
        this.bindEvents();
        this.renderTable();
        this.updateLastUpdate();
    }
    
    loadFundData() {
        // 从全局变量加载数据
        if (typeof LOF_FUND_DATA !== 'undefined') {
            this.funds = LOF_FUND_DATA;
        } else {
            console.warn('未找到 LOF_FUND_DATA');
            this.funds = [];
        }
        this.filteredFunds = [...this.funds];
    }
    
    bindEvents() {
        // 搜索框事件
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterFunds(e.target.value);
            });
        }

        // 表头排序事件
        const headers = document.querySelectorAll('#fundTable th');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.title = '点击排序';
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
        currentHeader.textContent += this.sortDirection === 'asc' ? ' ▼' : ' ▲';

        // 执行排序
        this.filteredFunds.sort((a, b) => {
            let valA, valB;

            switch(columnIndex) {
                case 0: // 基金信息（代码 + 名称）
                    valA = a.code + a.name;
                    valB = b.code + b.name;
                    break;
                case 1: // 溢价率
                    valA = parseFloat(a.premiumRate.replace('%', '').replace('+', '')) || 0;
                    valB = parseFloat(b.premiumRate.replace('%', '').replace('+', '')) || 0;
                    // 处理负号
                    if (a.premiumRate.includes('-')) valA = -Math.abs(valA);
                    if (b.premiumRate.includes('-')) valB = -Math.abs(valB);
                    break;
                case 2: // 限购值
                    // "无限额"排最后
                    if (a.limitAmount === '无限额' && b.limitAmount !== '无限额') return 1;
                    if (a.limitAmount !== '无限额' && b.limitAmount === '无限额') return -1;
                    
                    if (a.limitAmount === '无限额') return 0;
                    
                    valA = parseFloat(a.limitAmount.replace('万', ''));
                    valB = parseFloat(b.limitAmount.replace('万', ''));
                    break;
                default:
                    return 0;
            }

            // 处理 NaN 情况
            if (isNaN(valA) && !isNaN(valB)) return 1;
            if (!isNaN(valA) && isNaN(valB)) return -1;
            if (isNaN(valA) && isNaN(valB)) return 0;

            return this.sortDirection === 'asc' ? 
                (valA > valB ? 1 : -1) : 
                (valA < valB ? 1 : -1);
        });

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
        this.renderTable();
    }
    
    renderTable() {
        const tbody = document.getElementById('fundTableBody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (this.filteredFunds.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3">暂无数据</td></tr>';
            return;
        }
        
        // 显示所有基金（不分页）
        this.filteredFunds.forEach(fund => {
            const row = document.createElement('tr');
            
            // 基金信息（代码 + 名称）
            const infoCell = document.createElement('td');
            infoCell.className = 'fund-info';
            infoCell.innerHTML = `<strong>${fund.code}</strong><br>${fund.name}`;
            row.appendChild(infoCell);
            
            // 溢价率
            const premiumCell = document.createElement('td');
            premiumCell.textContent = fund.premiumRate;
            premiumCell.className = this.getPremiumClass(fund.premiumRate);
            row.appendChild(premiumCell);
            
            // 限购值
            const limitCell = document.createElement('td');
            if (fund.subscriptionStatus === 'paused') {
                limitCell.textContent = '暂停申购';
                limitCell.className = 'subscription-paused';
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
        
        // 更新基金总数显示
        const totalCount = document.getElementById('totalCount');
        if (totalCount) {
            totalCount.textContent = `共 ${this.filteredFunds.length} 只基金`;
        }
    }
    
    getPremiumClass(premiumRate) {
        if (premiumRate === 'N/A') return '';
        const value = parseFloat(premiumRate.replace('%', '').replace('+', ''));
        if (premiumRate.includes('-')) return 'negative';
        if (value > 0.5) return 'high-premium';
        if (value > 0) return 'positive';
        return '';
    }
    
    updateLastUpdate() {
        const now = new Date();
        const timeString = now.toLocaleString('zh-CN');
        const element = document.getElementById('lastUpdate');
        if (element) {
            element.textContent = `最后更新：${timeString}`;
        }
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.lofTracker = new LOFFundTracker();
});