/**
 * 管理员界面通用JavaScript功能
 * 包含认证、API调用、UI组件等通用功能
 */

class AdminApp {
    constructor() {
        this.token = localStorage.getItem('admin_token');
        this.adminInfo = JSON.parse(localStorage.getItem('admin_info') || '{}');
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkAuthStatus();
        this.initComponents();
    }

    // 设置事件监听器
    setupEventListeners() {
        // 侧边栏切换
        const toggleBtn = document.querySelector('.toggle-sidebar');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', this.toggleSidebar.bind(this));
        }

        // 登出按钮
        const logoutBtn = document.querySelector('.logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', this.logout.bind(this));
        }

        // 模态框关闭
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        // ESC键关闭模态框
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modal = document.querySelector('.modal.show');
                if (modal) {
                    this.closeModal(modal);
                }
            }
        });
    }

    // 检查认证状态
    async checkAuthStatus() {
        if (!this.token) {
            this.redirectToLogin();
            return;
        }

        try {
            const response = await this.apiCall('/api/admin/check', 'GET');
            if (!response.success) {
                this.redirectToLogin();
                return;
            }

            // 更新管理员信息显示
            this.updateAdminInfo(response.admin);
        } catch (error) {
            console.error('认证检查失败:', error);
            this.redirectToLogin();
        }
    }

    // 更新管理员信息显示
    updateAdminInfo(adminInfo) {
        this.adminInfo = adminInfo;
        localStorage.setItem('admin_info', JSON.stringify(adminInfo));

        const adminUserEl = document.querySelector('.admin-user');
        if (adminUserEl) {
            adminUserEl.innerHTML = `
                <i class="fas fa-user-shield"></i>
                <span>${adminInfo.username}</span>
                <span class="badge badge-info">${adminInfo.role}</span>
            `;
        }
    }

    // API调用封装
    async apiCall(url, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (this.token) {
            options.headers['Authorization'] = `Bearer ${this.token}`;
        }

        if (data) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || `HTTP ${response.status}`);
            }

            return result;
        } catch (error) {
            console.error('API调用失败:', error);
            throw error;
        }
    }

    // 显示消息提示
    showAlert(message, type = 'info', duration = 5000) {
        const alertContainer = document.querySelector('.alert-container') || this.createAlertContainer();
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>${message}</span>
                <button type="button" onclick="this.parentElement.parentElement.remove()" 
                        style="background: none; border: none; font-size: 1.2rem; cursor: pointer;">×</button>
            </div>
        `;

        alertContainer.appendChild(alert);

        // 自动移除
        if (duration > 0) {
            setTimeout(() => {
                if (alert.parentElement) {
                    alert.remove();
                }
            }, duration);
        }

        return alert;
    }

    createAlertContainer() {
        const container = document.createElement('div');
        container.className = 'alert-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
        return container;
    }

    // 显示加载状态
    showLoading(element, text = '加载中...') {
        if (typeof element === 'string') {
            element = document.querySelector(element);
        }
        
        if (element) {
            element.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px; justify-content: center; padding: 20px;">
                    <div class="loading"></div>
                    <span>${text}</span>
                </div>
            `;
        }
    }

    // 模态框操作
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {
        if (typeof modal === 'string') {
            modal = document.getElementById(modal);
        }
        
        if (modal) {
            modal.classList.remove('show');
            document.body.style.overflow = '';
        }
    }

    // 侧边栏切换
    toggleSidebar() {
        const sidebar = document.querySelector('.admin-sidebar');
        const main = document.querySelector('.admin-main');
        
        if (sidebar && main) {
            sidebar.classList.toggle('collapsed');
            main.classList.toggle('expanded');
        }
    }

    // 登出
    async logout() {
        if (!confirm('确定要登出吗？')) return;

        try {
            await this.apiCall('/api/admin/logout', 'POST');
        } catch (error) {
            console.error('登出失败:', error);
        } finally {
            this.clearAuth();
            this.redirectToLogin();
        }
    }

    // 清除认证信息
    clearAuth() {
        localStorage.removeItem('admin_token');
        localStorage.removeItem('admin_info');
        this.token = null;
        this.adminInfo = {};
    }

    // 重定向到登录页
    redirectToLogin() {
        window.location.href = '/admin-login?logout=1';
    }

    // 初始化组件
    initComponents() {
        this.initDataTables();
        this.initForms();
        this.initTooltips();
    }

    // 初始化数据表格
    initDataTables() {
        const tables = document.querySelectorAll('.data-table');
        tables.forEach(table => {
            // 添加排序功能
            const headers = table.querySelectorAll('th[data-sort]');
            headers.forEach(header => {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    const sortField = header.dataset.sort;
                    const currentOrder = header.dataset.order || 'asc';
                    const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
                    
                    // 移除其他列的排序标识
                    headers.forEach(h => {
                        h.classList.remove('sort-asc', 'sort-desc');
                        delete h.dataset.order;
                    });
                    
                    // 设置当前列的排序
                    header.dataset.order = newOrder;
                    header.classList.add(`sort-${newOrder}`);
                    
                    // 触发自定义事件
                    table.dispatchEvent(new CustomEvent('sort', {
                        detail: { field: sortField, order: newOrder }
                    }));
                });
            });
        });
    }

    // 初始化表单
    initForms() {
        const forms = document.querySelectorAll('form[data-api]');
        forms.forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData(form);
                const data = Object.fromEntries(formData.entries());
                const apiUrl = form.dataset.api;
                const method = form.dataset.method || 'POST';
                
                try {
                    const submitBtn = form.querySelector('[type="submit"]');
                    const originalText = submitBtn.textContent;
                    
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<div class="loading"></div> 处理中...';
                    
                    const result = await this.apiCall(apiUrl, method, data);
                    
                    if (result.success) {
                        this.showAlert(result.message || '操作成功', 'success');
                        
                        // 触发自定义事件
                        form.dispatchEvent(new CustomEvent('success', { detail: result }));
                    } else {
                        this.showAlert(result.message || '操作失败', 'error');
                    }
                    
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                    
                } catch (error) {
                    this.showAlert(error.message || '请求失败', 'error');
                    
                    const submitBtn = form.querySelector('[type="submit"]');
                    submitBtn.disabled = false;
                    submitBtn.textContent = submitBtn.dataset.originalText || '提交';
                }
            });
        });
    }

    // 初始化工具提示
    initTooltips() {
        const tooltips = document.querySelectorAll('[data-tooltip]');
        tooltips.forEach(element => {
            const tooltipText = element.dataset.tooltip;
            
            const tooltip = document.createElement('span');
            tooltip.className = 'tooltiptext';
            tooltip.textContent = tooltipText;
            
            element.classList.add('tooltip');
            element.appendChild(tooltip);
        });
    }

    // 格式化日期
    formatDate(dateString, format = 'YYYY-MM-DD HH:mm:ss') {
        if (!dateString) return '-';
        
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return '-';
        
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        
        return format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day)
            .replace('HH', hours)
            .replace('mm', minutes)
            .replace('ss', seconds);
    }

    // 数字格式化
    formatNumber(number, decimals = 0) {
        if (typeof number !== 'number') return '-';
        return number.toLocaleString('zh-CN', { 
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals 
        });
    }

    // 文件大小格式化
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // 获取用户状态徽章
    getUserStatusBadge(user) {
        if (!user) return '<span class="badge badge-secondary">未知</span>';
        
        if (user.is_active === false) {
            return '<span class="badge badge-danger">已禁用</span>';
        }
        
        const lastLogin = user.last_login;
        if (!lastLogin) {
            return '<span class="badge badge-warning">未登录</span>';
        }
        
        const lastLoginDate = new Date(lastLogin);
        const now = new Date();
        const daysDiff = (now - lastLoginDate) / (1000 * 60 * 60 * 24);
        
        if (daysDiff < 1) {
            return '<span class="badge badge-success">活跃</span>';
        } else if (daysDiff < 7) {
            return '<span class="badge badge-info">一般</span>';
        } else {
            return '<span class="badge badge-warning">不活跃</span>';
        }
    }

    // 分页组件
    createPagination(container, currentPage, totalPages, onPageChange) {
        if (typeof container === 'string') {
            container = document.querySelector(container);
        }
        
        if (!container || totalPages <= 1) {
            container.innerHTML = '';
            return;
        }
        
        let paginationHTML = '<div class="pagination">';
        
        // 上一页
        if (currentPage > 1) {
            paginationHTML += `<button onclick="(${onPageChange})(${currentPage - 1})">上一页</button>`;
        }
        
        // 页码
        const startPage = Math.max(1, currentPage - 2);
        const endPage = Math.min(totalPages, currentPage + 2);
        
        if (startPage > 1) {
            paginationHTML += `<button onclick="(${onPageChange})(1)">1</button>`;
            if (startPage > 2) {
                paginationHTML += '<span>...</span>';
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === currentPage ? 'active' : '';
            paginationHTML += `<button class="${activeClass}" onclick="(${onPageChange})(${i})">${i}</button>`;
        }
        
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                paginationHTML += '<span>...</span>';
            }
            paginationHTML += `<button onclick="(${onPageChange})(${totalPages})">${totalPages}</button>`;
        }
        
        // 下一页
        if (currentPage < totalPages) {
            paginationHTML += `<button onclick="(${onPageChange})(${currentPage + 1})">下一页</button>`;
        }
        
        paginationHTML += '</div>';
        container.innerHTML = paginationHTML;
    }

    // 搜索防抖
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // 确认对话框
    confirm(message, title = '确认操作') {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'modal show';
            modal.innerHTML = `
                <div class="modal-content" style="max-width: 400px;">
                    <div class="modal-header">
                        <h3 class="modal-title">${title}</h3>
                    </div>
                    <div style="padding: 20px 0;">
                        <p style="margin: 0; color: #374151;">${message}</p>
                    </div>
                    <div style="display: flex; gap: 10px; justify-content: flex-end;">
                        <button class="btn btn-secondary" onclick="resolveConfirm(false)">取消</button>
                        <button class="btn btn-danger" onclick="resolveConfirm(true)">确认</button>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            document.body.style.overflow = 'hidden';
            
            window.resolveConfirm = (result) => {
                document.body.removeChild(modal);
                document.body.style.overflow = '';
                delete window.resolveConfirm;
                resolve(result);
            };
        });
    }
}

// 全局管理员应用实例
window.adminApp = new AdminApp();

// 导出常用函数到全局
window.showAlert = (message, type, duration) => adminApp.showAlert(message, type, duration);
window.showModal = (modalId) => adminApp.showModal(modalId);
window.closeModal = (modal) => adminApp.closeModal(modal);
window.apiCall = (url, method, data) => adminApp.apiCall(url, method, data);
window.formatDate = (date, format) => adminApp.formatDate(date, format);
window.formatNumber = (number, decimals) => adminApp.formatNumber(number, decimals);
window.getUserStatusBadge = (user) => adminApp.getUserStatusBadge(user);

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎮 FlapPy Bird 管理员界面已加载');
}); 