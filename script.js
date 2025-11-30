// ========================================
// إضافة تفاعلية للصفحة
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // التحقق من المصادقة وصلاحية التوكن
    if (!isTokenValid()) {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('token_expires');
        window.location.href = 'login.html';
        return;
    }
    
    // التحكم في القائمة المنبثقة
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const mainSidebar = document.getElementById('main-sidebar');
    const currentSectionTitle = document.getElementById('current-section-title');
    const container = document.querySelector('.container');
    
    // دالة لإغلاق القائمة
    function closeSidebar() {
        if (mainSidebar) {
            mainSidebar.classList.remove('active');
        }
        if (container) {
            container.classList.remove('sidebar-open');
        }
        // إعادة رسم الشارتات بعد تغيير الحجم
        setTimeout(() => {
            resizeCharts();
        }, 350);
    }
    
    // دالة لفتح القائمة
    function openSidebar() {
        if (mainSidebar) {
            mainSidebar.classList.add('active');
        }
        if (container) {
            container.classList.add('sidebar-open');
        }
        // إعادة رسم الشارتات بعد تغيير الحجم
        setTimeout(() => {
            resizeCharts();
        }, 350);
    }
    
    // دالة لإعادة حجم الشارتات
    window.resizeCharts = function() {
        if (typeof charts !== 'undefined' && charts) {
            Object.keys(charts).forEach(canvasId => {
                if (charts[canvasId]) {
                    try {
                        charts[canvasId].resize();
                        charts[canvasId].update('none'); // تحديث بدون animation
                    } catch(e) {
                        console.log('Resize chart error:', e);
                    }
                }
            });
        }
    };
    
    // دالة لتحديث عنوان التبويب
    function updateSectionTitle(title) {
        if (currentSectionTitle) {
            currentSectionTitle.textContent = title;
            currentSectionTitle.classList.add('show');
        }
    }
    
    // زر القائمة
    if (sidebarToggle && mainSidebar) {
        sidebarToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            const isOpen = mainSidebar.classList.contains('active');
            
            if (isOpen) {
                closeSidebar();
            } else {
                openSidebar();
            }
        });
    }
    
    // إغلاق القائمة عند الضغط خارجها
    document.addEventListener('click', function(e) {
        if (mainSidebar && mainSidebar.classList.contains('active')) {
            if (!mainSidebar.contains(e.target) && e.target !== sidebarToggle) {
                closeSidebar();
            }
        }
    });
    
    // إعادة حجم الشارتات عند تغيير حجم النافذة
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            if (window.resizeCharts) {
                window.resizeCharts();
            }
        }, 200);
    });

    // تأثير الظهور التدريجي للعناصر
    initAnimations();
    
    // تفاعلية البطاقات الإحصائية
    initStatCards();
    
    // تفاعلية المهام
    initTaskCheckboxes();
    
    // تفاعلية البحث
    initSearchBox();
    
    // إضافة الوقت الفعلي
    updateTime();
    setInterval(updateTime, 1000);

    // تحديث بيانات السوق
    updateMarketIndices();
    setInterval(updateMarketIndices, 300000); // تحديث كل 5 دقائق
});

// ========================================
// تأثير الظهور التدريجي
// ========================================
function initAnimations() {
    const elements = document.querySelectorAll('.stat-card, .content-card, .activity-item');
    
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.5s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// ========================================
// تفاعلية البطاقات الإحصائية
// ========================================
function initStatCards() {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach(card => {
        card.addEventListener('click', function() {
            // إضافة تأثير موجة عند النقر
            const ripple = document.createElement('div');
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(255, 255, 255, 0.3)';
            ripple.style.width = '20px';
            ripple.style.height = '20px';
            ripple.style.animation = 'ripple 0.6s ease-out';
            
            const rect = card.getBoundingClientRect();
            ripple.style.left = '50%';
            ripple.style.top = '50%';
            ripple.style.transform = 'translate(-50%, -50%)';
            
            card.style.position = 'relative';
            card.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // إضافة animation CSS للموجة
    if (!document.querySelector('#ripple-animation')) {
        const style = document.createElement('style');
        style.id = 'ripple-animation';
        style.textContent = `
            @keyframes ripple {
                0% {
                    width: 20px;
                    height: 20px;
                    opacity: 1;
                }
                100% {
                    width: 200px;
                    height: 200px;
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// ========================================
// تفاعلية المهام
// ========================================
function initTaskCheckboxes() {
    const checkboxes = document.querySelectorAll('.task-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const label = this.nextElementSibling;
            
            if (this.checked) {
                label.classList.add('completed');
                // تأثير صوتي أو بصري عند إكمال المهمة
                animateTaskCompletion(this.parentElement);
            } else {
                label.classList.remove('completed');
            }
            
            updateTaskProgress();
        });
    });
}

function animateTaskCompletion(taskItem) {
    // تأثير احتفالي بسيط
    taskItem.style.transform = 'scale(1.02)';
    setTimeout(() => {
        taskItem.style.transform = 'scale(1)';
    }, 200);
}

function updateTaskProgress() {
    const checkboxes = document.querySelectorAll('.task-checkbox');
    const completed = document.querySelectorAll('.task-checkbox:checked').length;
    const total = checkboxes.length;
    const percentage = Math.round((completed / total) * 100);
    
    console.log(`تم إنجاز ${completed} من ${total} مهام (${percentage}%)`);
}

// ========================================
// تفاعلية البحث
// ========================================
function initSearchBox() {
    const searchInput = document.querySelector('.search-box input');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            
            // إضافة مؤشر تحميل
            const searchBox = this.parentElement;
            searchBox.style.borderColor = 'var(--purple)';
            
            searchTimeout = setTimeout(() => {
                const query = e.target.value;
                if (query.length > 0) {
                    console.log('البحث عن:', query);
                    // هنا يمكن إضافة منطق البحث الفعلي
                }
                searchBox.style.borderColor = '';
            }, 500);
        });
        
        searchInput.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });
        
        searchInput.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    }
}

// ========================================
// تحديث الوقت
// ========================================
function updateTime() {
    const now = new Date();
    const options = { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    const arabicDate = now.toLocaleDateString('ar-SA', options);
    
    // يمكن إضافة عنصر لعرض الوقت إذا أردت
    // console.log('الوقت الحالي:', arabicDate);
}

// ========================================
// تفاعلية عامة للأزرار
// ========================================
document.querySelectorAll('button, .nav-item').forEach(element => {
    element.addEventListener('mouseenter', function() {
        this.style.transition = 'all 0.3s ease';
    });
});

// ========================================
// تأثير التمرير السلس
// ========================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        
        // تجاهل الروابط الفارغة أو التي تحتوي فقط على #
        if (!href || href === '#') return;
        
        e.preventDefault();
        const target = document.querySelector(href);
        
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ========================================
// كشف النقرات على العناصر التفاعلية
// ========================================
document.addEventListener('click', function(e) {
    // يمكن إضافة معالجات إضافية للنقرات هنا
    if (e.target.closest('.primary-btn')) {
        console.log('تم النقر على زر إضافة جديد');
        // هنا يمكن فتح نموذج أو صفحة جديدة
    }
    
    if (e.target.closest('.notification-btn')) {
        console.log('تم النقر على زر الإشعارات');
        // هنا يمكن عرض قائمة الإشعارات
    }
});

// ========================================
// معالجة الأخطاء العامة
// ========================================
window.addEventListener('error', function(e) {
    console.error('حدث خطأ في التطبيق:', e.error);
});

// ========================================
// تحسينات الأداء
// ========================================
// تحميل كسول للصور إذا تم إضافتها لاحقاً
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });
    
    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// ========================================
// رسائل الترحيب
// ========================================
console.log('%c🎉 مرحباً بك في MeshalStock!', 'font-size: 20px; color: #667eea; font-weight: bold;');
console.log('%c✨ التطبيق جاهز للاستخدام', 'font-size: 14px; color: #4facfe;');

// ========================================
// نافذة تحديث البيانات
// ========================================
const modal = document.getElementById('update-modal');
const updateDataBtn = document.getElementById('update-data-btn');
const closeModalBtn = document.getElementById('close-modal');
const saudiBtn = document.querySelector('.saudi-btn');
const usBtn = document.querySelector('.us-btn');
const progressContainer = document.getElementById('update-progress');
const progressBar = document.getElementById('progress-bar');
const progressPercentage = document.getElementById('progress-percent');
const progressTitle = document.getElementById('progress-status');
const progressMessage = document.getElementById('progress-message');
const updateOptions = document.querySelector('.update-options');
const modalDescription = document.querySelector('.modal-description');

// API configuration
// تحديد عنوان API بناءً على البيئة الحالية
const API_URL = window.location.origin + '/api';
let currentJobId = null;
let pollInterval = null;

// دالة للحصول على التوكن
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

// دالة للتحقق من صلاحية التوكن
function isTokenValid() {
    const token = getAuthToken();
    const expires = localStorage.getItem('token_expires');
    
    if (!token || !expires) return false;
    
    return Date.now() < parseInt(expires);
}

// دالة لإنشاء headers مع التوكن
function getAuthHeaders() {
    const headers = {
        'Content-Type': 'application/json'
    };
    
    const token = getAuthToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
}

// فتح النافذة المنبثقة
if (updateDataBtn) {
    updateDataBtn.addEventListener('click', function(e) {
        e.preventDefault();
        modal.classList.add('active');
        // إعادة تعيين الحالة
        resetModalState();
    });
}

// إغلاق النافذة المنبثقة
if (closeModalBtn) {
    closeModalBtn.addEventListener('click', function() {
        modal.classList.remove('active');
        if (pollInterval) {
            clearInterval(pollInterval);
        }
    });
}

// إغلاق عند النقر خارج المحتوى
modal?.addEventListener('click', function(e) {
    if (e.target === modal) {
        modal.classList.remove('active');
        if (pollInterval) {
            clearInterval(pollInterval);
        }
    }
});

// زر تحديث البيانات السعودية
saudiBtn?.addEventListener('click', function() {
    startDataFetch('saudi', this);
});

// زر تحديث البيانات الأمريكية
usBtn?.addEventListener('click', function() {
    startDataFetch('us', this);
});

/**
 * بدء عملية جلب البيانات
 */
async function startDataFetch(market, btnElement) {
    const marketName = market === 'saudi' ? 'السعودية' : 'الأمريكية';
    
    try {
        // إخفاء الخيارات وعرض مؤشر التقدم
        updateOptions.style.display = 'none';
        modalDescription.style.display = 'none';
        progressContainer.style.display = 'block';
        
        progressTitle.textContent = `جاري تحديث بيانات الأسهم ${marketName}...`;
        resetProgress();
        
        // تفعيل دوران الأيقونة
        if (btnElement) {
            btnElement.classList.add('loading');
            // تعطيل الزر لمنع التكرار
            btnElement.disabled = true;
        }
        
        // إرسال طلب البدء
        const response = await fetch(`${API_URL}/fetch/${market}`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({
                test: false,  // تغيير إلى true للاختبار
                workers: 2
            })
        });
        
        if (!response.ok) {
            throw new Error('فشل الاتصال بخادم API');
        }
        
        const data = await response.json();
        currentJobId = data.job_id;
        
        // بدء التحقق من التقدم
        pollJobStatus(market, btnElement);
        
        showMessage(`بدأت عملية تحديث الأسهم ${marketName}`, 'info');
        
    } catch (error) {
        console.error('خطأ في بدء التحديث:', error);
        // عرض الخطأ داخل النافذة
        const msgEl = document.getElementById('progress-message');
        if (msgEl) {
            msgEl.textContent = `خطأ: ${error.message}`;
            msgEl.className = 'progress-message error';
        }
        showMessage(`خطأ: ${error.message}`, 'error');
        
        // إعادة تفعيل الزر وإيقاف الدوران في حال الخطأ المباشر
        if (btnElement) {
            btnElement.classList.remove('loading');
            btnElement.disabled = false;
        }
    }
}

/**
 * التحقق المستمر من حالة المهمة
 */
function pollJobStatus(market, btnElement) {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_URL}/status/${currentJobId}`, {
                headers: getAuthHeaders()
            });
            
            if (!response.ok) {
                throw new Error('فشل الحصول على حالة المهمة');
            }
            
            const data = await response.json();
            updateProgress(data);
            
            // إيقاف التحقق إذا اكتملت المهمة
            if (data.status === 'completed' || data.status === 'failed' || data.status === 'error') {
                clearInterval(pollInterval);
                
                // إيقاف دوران الأيقونة وإعادة تفعيل الزر
                if (btnElement) {
                    btnElement.classList.remove('loading');
                    btnElement.disabled = false;
                }
                
                if (data.status === 'completed') {
                    const marketName = market === 'saudi' ? 'السعودية' : 'الأمريكية';
                    showMessage(`✓ تم تحديث بيانات الأسهم ${marketName} بنجاح!`, 'success');
                } else {
                    showMessage(`✗ فشل التحديث. يرجى مراجعة السجلات.`, 'error');
                }
            }
            
        } catch (error) {
            console.error('خطأ في التحقق من الحالة:', error);
            clearInterval(pollInterval);
            showMessage(`خطأ: ${error.message}`, 'error');
            
            // إيقاف دوران الأيقونة وإعادة تفعيل الزر عند الخطأ
            if (btnElement) {
                btnElement.classList.remove('loading');
                btnElement.disabled = false;
            }
        }
    }, 2000);  // التحقق كل ثانيتين
}

/**
 * تحديث مؤشر التقدم
 */
function updateProgress(data) {
    const { progress = 0, total = 0, stats = {} } = data;
    
    if (total > 0) {
        const percentage = Math.round((progress / total) * 100);
        progressBar.style.width = `${percentage}%`;
        progressPercentage.textContent = `${percentage}%`;
    }
    
    // تحديث الإحصائيات
    document.getElementById('stat-new').textContent = stats.new || 0;
    document.getElementById('stat-updated').textContent = stats.updated || 0;
    document.getElementById('stat-uptodate').textContent = stats.up_to_date || 0;
    document.getElementById('stat-failed').textContent = stats.failed || 0;
}

/**
 * إعادة تعيين مؤشر التقدم
 */
function resetProgress() {
    progressBar.style.width = '0%';
    progressPercentage.textContent = '0%';
    document.getElementById('stat-new').textContent = '0';
    document.getElementById('stat-updated').textContent = '0';
    document.getElementById('stat-uptodate').textContent = '0';
    document.getElementById('stat-failed').textContent = '0';
    progressMessage.textContent = '';
    progressMessage.className = 'progress-message';
}

/**
 * إعادة تعيين حالة النافذة بالكامل
 */
function resetModalState() {
    progressContainer.style.display = 'none';
    updateOptions.style.display = 'grid';
    modalDescription.style.display = 'block';
    resetProgress();
    
    // إعادة تفعيل الأزرار وإزالة الدوران
    if (saudiBtn) {
        saudiBtn.classList.remove('loading');
        saudiBtn.disabled = false;
    }
    if (usBtn) {
        usBtn.classList.remove('loading');
        usBtn.disabled = false;
    }
}

/**
 * عرض رسالة
 */
function showMessage(message, type = 'info') {
    progressMessage.textContent = message;
    progressMessage.className = `progress-message ${type}`;
}

// ========================================
// التحقق من توفر خادم API
// ========================================
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_URL}/health`, {
            signal: AbortSignal.timeout(2000)
        });
        
        if (response.ok) {
            console.log('✓ خادم API متصل ويعمل');
            return true;
        }
    } catch (error) {
        console.warn('⚠ خادم API غير متصل. يرجى تشغيله باستخدام: python api_server.py');
        return false;
    }
}

// التحقق من خادم API عند تحميل الصفحة
setTimeout(() => {
    checkAPIStatus();
}, 1000);

// التحقق من صلاحية التوكن كل 5 دقائق
setInterval(() => {
    if (!isTokenValid()) {
        alert('انتهت صلاحية الجلسة. سيتم إعادة تسجيل الدخول.');
        localStorage.removeItem('auth_token');
        localStorage.removeItem('token_expires');
        window.location.href = 'login.html';
    }
}, 300000); // كل 5 دقائق


// ========================================
// تحديث بيانات السوق (مباشر)
// ========================================
async function updateMarketIndices() {
    const lastUpdateEl = document.getElementById('last-update-time');
    
    try {
        console.log('Fetching market data...');
        const response = await fetch(`${API_URL}/market-summary`);
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        console.log('Market data received:', data);
        
        // تحديث البطاقات
        for (const [key, value] of Object.entries(data)) {
            updateMarketCard(key, value);
        }
        
        // تحديث وقت آخر تحديث
        const now = new Date();
        if (lastUpdateEl) {
            const options = { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'numeric', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            lastUpdateEl.textContent = now.toLocaleDateString('ar-SA', options);
        }
        
    } catch (error) {
        console.error('فشل تحديث بيانات السوق:', error);
        // عرض رسالة خطأ في البطاقات
        const cards = ['TASI', 'DJI', 'NASDAQ', 'SP500', 'OIL', 'GOLD', 'SILVER', 'BTC'];
        cards.forEach(key => {
            const card = document.getElementById(`card-${key}`);
            if (card) {
                const priceEl = card.querySelector('.market-price');
                if (priceEl && priceEl.textContent === '---') {
                    priceEl.textContent = 'خطأ اتصال';
                    priceEl.style.fontSize = '0.8rem';
                    priceEl.style.color = '#ff6b6b';
                }
            }
        });
    }
}

function updateMarketCard(key, data) {
    const card = document.getElementById(`card-${key}`);
    if (!card) {
        console.warn(`Card not found for key: ${key}`);
        return;
    }
    
    if (data.error) {
        // حالة الخطأ
        const priceEl = card.querySelector('.market-price');
        if (priceEl) priceEl.textContent = '---';
        return;
    }
    
    const priceEl = card.querySelector('.market-price');
    const changeValEl = card.querySelector('.change-value');
    const changePctEl = card.querySelector('.change-percent');
    
    if (priceEl) priceEl.textContent = data.price.toLocaleString();
    
    const sign = data.change >= 0 ? '+' : '';
    if (changeValEl) changeValEl.textContent = `${sign}${data.change}`;
    if (changePctEl) changePctEl.textContent = `(${sign}${data.change_percent}%)`;
    
    // تحديث الألوان (Trend)
    card.classList.remove('trend-up', 'trend-down');
    if (data.status === 'up') {
        card.classList.add('trend-up');
    } else {
        card.classList.add('trend-down');
    }
    
    // تأثير وميض عند التحديث
    card.style.opacity = '0.5';
    setTimeout(() => {
        card.style.opacity = '1';
    }, 300);
}

// تشغيل التحديث عند التحميل
// ملاحظة: نستخدم setTimeout لضمان تحميل DOM بالكامل وعدم التعارض مع المستمعين الآخرين
setTimeout(() => {
    updateMarketIndices();
    // تحديث كل 5 دقائق
    setInterval(updateMarketIndices, 300000);
}, 2000);


// ========================================
// منطق قسم فيبو وجان
// ========================================

// عناصر DOM
const fiboFilterSection = document.getElementById('fibo-filter');
const fiboGannSection = document.getElementById('fibo-gann-section');
const marketOverview = document.querySelector('.market-overview');
const stockList = document.getElementById('stock-list');
const stockSearch = document.getElementById('stock-search');
const chartCanvas = document.getElementById('stock-chart');
const marketTabs = document.querySelectorAll('.fg-tab');
const navItems = document.querySelectorAll('.nav-item');

let charts = {}; // لتخزين المخططات لكل canvas
let allSymbols = [];

// تهيئة القسم
function initFiboGann() {
    // تبديل التبويبات (سعودي / أمريكي)
    marketTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            marketTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const market = tab.dataset.market;
            fetchSymbols(market);
        });
    });

    // البحث في القائمة
    if (stockSearch) {
        stockSearch.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            const filtered = allSymbols.filter(item => 
                item.symbol.toLowerCase().includes(query) || 
                item.name.toLowerCase().includes(query)
            );
            renderStockList(filtered);
        });
    }

    // التنقل من القائمة الجانبية - تم نقله إلى المعالج الموحد في الأسفل
    // navItems.forEach(item => { ... });
}

function setActiveNav(item) {
    navItems.forEach(n => n.classList.remove('active'));
    item.classList.add('active');
}

function showSection(sectionId) {
    // إخفاء الجميع
    if (marketOverview) marketOverview.style.display = 'none';
    if (fiboGannSection) fiboGannSection.style.display = 'none';
    if (fiboFilterSection) fiboFilterSection.style.display = 'none';
    
    // إظهار المطلوب
    const section = document.getElementById(sectionId);
    if (section) section.style.display = 'block';
    
    if (sectionId === 'fibo-gann-section') {
        if (stockList && stockList.children.length <= 1) fetchSymbols('saudi');
    }
}

// ========================================
// منطق فلتر فيبو
// ========================================
function initFiboFilter() {
    const filterTabs = document.querySelectorAll('#fibo-filter .fg-tab');
    const scanBtn = document.getElementById('scan-btn');
    
    filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
        });
    });
    
    if (scanBtn) {
        // إزالة المستمعين القدامى لتجنب التكرار (طريقة مبسطة)
        const newBtn = scanBtn.cloneNode(true);
        scanBtn.parentNode.replaceChild(newBtn, scanBtn);
        
        newBtn.addEventListener('click', () => {
            const activeMarket = document.querySelector('#fibo-filter .fg-tab.active').dataset.filterMarket || 'saudi';
            scanMarket(activeMarket);
        });
    }
}

async function scanMarket(market) {
    const resultsContainer = document.getElementById('scan-results');
    if (!resultsContainer) return;
    
    resultsContainer.innerHTML = '<div class="fg-loading">جاري فحص السوق... قد يستغرق ذلك دقيقة</div>';
    
    try {
        const response = await fetch(`${API_URL}/scan/fibo_gann?market=${market}`);
        const data = await response.json();
        
        if (data.results && data.results.length > 0) {
            renderScanResults(data.results, market);
        } else {
            resultsContainer.innerHTML = '<div class="placeholder-text">لا توجد فرص مطابقة حالياً</div>';
        }
    } catch (error) {
        console.error('Scan error:', error);
        resultsContainer.innerHTML = '<div class="fg-loading">حدث خطأ أثناء الفحص</div>';
    }
}

function renderScanResults(results, market) {
    const container = document.getElementById('scan-results');
    container.innerHTML = '';
    
    results.forEach(item => {
        const div = document.createElement('div');
        div.className = 'stock-item';
        // تنسيق مختلف قليلاً لإظهار السبب
        div.innerHTML = `
            <div style="display:flex; justify-content:space-between; width:100%">
                <div>
                    <span class="stock-symbol" style="font-weight:bold">${item.symbol}</span>
                    <span class="stock-name" style="font-size:0.9em; color:#666">${item.name}</span>
                </div>
                <div style="text-align:left">
                    <span style="display:block; font-size:0.85em; color:${item.reason.includes('اختراق') ? 'green' : 'orange'}">${item.reason}</span>
                    <span style="font-size:0.8em; color:#333">@ ${item.close}</span>
                </div>
            </div>
        `;
        
        div.addEventListener('click', () => {
            document.querySelectorAll('#scan-results .stock-item').forEach(i => i.classList.remove('active'));
            div.classList.add('active');
            loadChart(market, item.symbol, 'filter-chart');
        });
        
        container.appendChild(div);
    });
}

// جلب قائمة الرموز
async function fetchSymbols(market) {
    if (!stockList) {
        console.error('stockList element not found!');
        return;
    }
    
    console.log(`Fetching symbols for market: ${market}`);
    stockList.innerHTML = '<div class="fg-loading">جاري التحميل...</div>';
    
    try {
        const url = `${API_URL}/symbols/${market}`;
        console.log(`Fetching from: ${url}`);
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.error) throw new Error(data.error);
        
        console.log(`Received ${data.symbols ? data.symbols.length : 0} symbols`);
        allSymbols = data.symbols;
        renderStockList(allSymbols);
        
    } catch (error) {
        console.error('Error fetching symbols:', error);
        stockList.innerHTML = '<div class="fg-loading">فشل تحميل القائمة</div>';
    }
}

// عرض القائمة
function renderStockList(symbols) {
    if (!stockList) return;
    stockList.innerHTML = '';
    
    // إيجاد التبويب النشط في قسم جان وفيبو فقط
    const activeTab = document.querySelector('#fibo-gann-section .fg-tab.active');
    const activeMarket = activeTab ? activeTab.dataset.market : 'saudi';
    
    symbols.forEach(item => {
        const div = document.createElement('div');
        div.className = 'stock-item';
        div.innerHTML = `
            <span class="stock-symbol">${item.symbol}</span>
            <span class="stock-name">${item.name}</span>
        `;
        div.addEventListener('click', () => {
            // تحديد العنصر النشط
            document.querySelectorAll('.stock-item').forEach(i => i.classList.remove('active'));
            div.classList.add('active');
            
            loadChart(activeMarket, item.symbol);
        });
        stockList.appendChild(div);
    });
}

// تحميل الرسم البياني
async function loadChart(market, symbol, canvasId = 'stock-chart') {
    try {
        console.log(`Loading chart for ${symbol} from ${market} market...`);
        
        // عرض مؤشر تحميل
        const canvas = document.getElementById(canvasId);
        if (canvas) {
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.font = '20px Tajawal';
            ctx.fillStyle = '#667eea';
            ctx.textAlign = 'center';
            ctx.fillText('جاري تحميل البيانات...', canvas.width / 2, canvas.height / 2);
        }
        
        const url = `${API_URL}/history/${market}/${symbol}`;
        console.log(`Fetching from: ${url}`);
        
        const response = await fetch(url);
        const data = await response.json();
        
        console.log(`Received ${data.length} data points`);
        
        if (data.error) throw new Error(data.error);
        
        renderChart(symbol, data, canvasId);
        
    } catch (error) {
        console.error('Error loading chart:', error);
        alert(`فشل تحميل بيانات الرسم البياني: ${error.message}`);
    }
}

// رسم الشارت
function renderChart(symbol, data, canvasId = 'stock-chart') {
    console.log(`=== Rendering chart for ${symbol}, ${data.length} data points ===`);
    console.log(`Canvas ID: ${canvasId}`);
    
    const canvas = document.getElementById(canvasId);
    console.log('Canvas element:', canvas);
    
    if (!canvas) {
        console.error('Canvas not found:', canvasId);
        alert(`خطأ: لم يتم العثور على عنصر Canvas بالمعرف ${canvasId}`);
        return;
    }
    
    console.log('Canvas found, getting context...');
    
    // التأكد من أن Canvas مرئي
    const parent = canvas.closest('.fg-content');
    if (parent) {
        console.log('Parent visibility:', window.getComputedStyle(parent).display);
    }
    
    // فحص حجم Canvas
    console.log('Canvas size:', {
        width: canvas.width,
        height: canvas.height,
        offsetWidth: canvas.offsetWidth,
        offsetHeight: canvas.offsetHeight,
        clientWidth: canvas.clientWidth,
        clientHeight: canvas.clientHeight
    });
    
    // إذا كان Canvas بدون حجم، تعيين حجم افتراضي
    if (canvas.offsetWidth === 0 || canvas.offsetHeight === 0) {
        console.warn('Canvas has zero size, setting default...');
        const chartWrapper = canvas.closest('.chart-wrapper');
        if (chartWrapper) {
            const rect = chartWrapper.getBoundingClientRect();
            console.log('Chart wrapper size:', rect);
            if (rect.width > 0 && rect.height > 0) {
                canvas.width = rect.width;
                canvas.height = rect.height;
            } else {
                // حجم افتراضي
                canvas.width = 800;
                canvas.height = 600;
            }
        }
    }
    
    const ctx = canvas.getContext('2d');
    console.log('Context:', ctx);
    
    // تعيين الألوان الافتراضية للشموع قبل إنشاء الشارت
    try {
        if (typeof Chart !== 'undefined' && Chart.defaults) {
            // تأكد من وجود المسار
            if (!Chart.defaults.elements) Chart.defaults.elements = {};
            if (!Chart.defaults.elements.candlestick) Chart.defaults.elements.candlestick = {};
            
            // تعيين الألوان
            Chart.defaults.elements.candlestick.color = {
                up: '#0B3D0B',
                down: '#B71C1C',
                unchanged: '#666666'
            };
            Chart.defaults.elements.candlestick.borderColor = {
                up: '#0B3D0B',
                down: '#B71C1C',
                unchanged: '#666666'
            };
            console.log('Chart defaults set successfully');
        }
    } catch (e) {
        console.error('Error setting Chart defaults:', e);
    }

    // تحويل البيانات لتنسيق Chart.js Financial
    const ohlcData = data.map(d => ({
        x: new Date(d.Date).valueOf(), // Timestamp
        o: parseFloat(d.Open),
        h: parseFloat(d.High),
        l: parseFloat(d.Low),
        c: parseFloat(d.Close),
        v: parseFloat(d.Volume) // إضافة الحجم
    }));

    // حساب أقصى حجم لضبط المقياس
    const maxVolume = Math.max(...ohlcData.map(d => d.v));

    // حساب أقل قاع (Lowest Low) وموقعه
    let minLow = Infinity;
    let minLowIndex = -1;
    
    ohlcData.forEach((d, index) => {
        if (d.l < minLow) {
            minLow = d.l;
            minLowIndex = index;
        }
    });
    
    // إنشاء بيانات خط القاع (خط أفقي يمتد على طول الفترة)
    const lineData = ohlcData.map(d => ({
        x: d.x,
        y: minLow
    }));

    // البحث عن أول قمة بعد القاع
    let peakIndex = -1;
    let peakHigh = 0;
    
    // نبدأ البحث من بعد القاع مباشرة
    // القمة المحلية: شمعة الهاي حقها أعلى من اللي قبلها واللي بعدها
    for (let i = minLowIndex + 1; i < ohlcData.length - 1; i++) {
        const currentHigh = ohlcData[i].h;
        const prevHigh = ohlcData[i-1].h;
        const nextHigh = ohlcData[i+1].h;
        
        if (currentHigh > prevHigh && currentHigh > nextHigh) {
            peakIndex = i;
            peakHigh = currentHigh;
            break; // وجدنا أول قمة، نتوقف
        }
    }
    
    console.log(`Peak search (strict): minLowIndex=${minLowIndex}, peakIndex=${peakIndex}, peakHigh=${peakHigh}`);

    // إنشاء بيانات خط القمة (خط قصير بعرض 4 شموع تقريباً)
    const peakLineData = [];
    if (peakIndex !== -1) {
        // نحدد بداية ونهاية الخط (شمعتين قبل وشمعتين بعد)
        const startIdx = Math.max(0, peakIndex - 2);
        const endIdx = Math.min(ohlcData.length - 1, peakIndex + 2);
        peakLineData.push({ x: ohlcData[startIdx].x, y: peakHigh });
        peakLineData.push({ x: ohlcData[endIdx].x, y: peakHigh });
    }

    // حساب مستويات جان (Gann Levels) - معايرة ديناميكية
    // بناءً على طلب المستخدم: القمة الأولى تعتبر هي الزاوية 90 درجة
    // نقوم بحساب "معامل الحركة" (Delta) بناءً على الفرق بين جذر القمة وجذر القاع
    
    let gannLevels = [];
    
    if (peakIndex !== -1 && peakHigh > minLow) {
        // الحالة 1: تم العثور على قمة (معايرة ديناميكية)
        const sqrtLow = Math.sqrt(minLow);
        const sqrtPeak = Math.sqrt(peakHigh);
        const delta = sqrtPeak - sqrtLow; // هذا يمثل 90 درجة
        
        gannLevels = [
            { deg: 180, price: Math.pow(sqrtLow + (2 * delta), 2), color: '#1976D2', label: 'Gann 180°' },  // أزرق
            { deg: 270, price: Math.pow(sqrtLow + (3 * delta), 2), color: '#7B1FA2', label: 'Gann 270°' },  // بنفسجي
            { deg: 360, price: Math.pow(sqrtLow + (4 * delta), 2), color: '#388E3C', label: 'Gann 360°' }   // أخضر
        ];
        
    } else {
        // الحالة 2: لم يتم العثور على قمة (استخدام القياس الذكي الافتراضي)
        let scale = 1;
        if (minLow >= 1000) scale = 1;
        else if (minLow >= 100) scale = 10;
        else scale = 100;

        const scaledLow = minLow * scale;
        const sqrtLow = Math.sqrt(scaledLow);
        
        gannLevels = [
            { deg: 180, factor: 1.0, color: '#2196F3', label: 'Gann 180°' },
            { deg: 270, factor: 1.5, color: '#9C27B0', label: 'Gann 270°' },
            { deg: 360, factor: 2.0, color: '#4CAF50', label: 'Gann 360°' }
        ].map(l => ({
            ...l,
            price: Math.pow(sqrtLow + l.factor, 2) / scale
        }));
    }

    // حساب مستويات فيبوناتشي (Fibonacci Levels)
    // القاع = 0%
    // القمة الأولى = 100%
    let fibDatasets = [];
    if (peakIndex !== -1 && peakHigh > minLow) {
        const fibRange = peakHigh - minLow;
        console.log(`Fibonacci calculation: minLow=${minLow}, peakHigh=${peakHigh}, range=${fibRange}`);
        
        const fibLevels = [
            { ratio: 1.0, label: 'Fibo 100%', color: '#FFD700' },     // ذهبي فاتح
            { ratio: 1.618, label: 'Fibo 161.8%', color: '#FFA500' }, // برتقالي
            { ratio: 2.618, label: 'Fibo 261.8%', color: '#FF8C00' }, // برتقالي داكن
            { ratio: 4.236, label: 'Fibo 423.6%', color: '#FF6347' }  // أحمر مائل للبرتقالي
        ];

        fibDatasets = fibLevels.map(level => {
            const price = minLow + (fibRange * level.ratio);
            console.log(`${level.label}: ${price.toFixed(2)}`);
            return {
                type: 'line',
                label: `${level.label}`, // النص فقط بدون السعر هنا، سنضيفه في الرسم
                data: ohlcData.map(d => ({ x: d.x, y: price })),
                borderColor: level.color,
                borderWidth: 2,          // زيادة السماكة قليلاً
                borderDash: [3, 3],      // تنقيط مختلف عن جان
                pointRadius: 0,
                fill: false,
                order: 2,
                yValue: price // تخزين القيمة لاستخدامها في الرسم
            };
        });
        console.log(`Created ${fibDatasets.length} Fibonacci levels`);
    } else {
        console.log(`No Fibonacci levels: peakIndex=${peakIndex}, peakHigh=${peakHigh}, minLow=${minLow}`);
    }

    const gannDatasets = gannLevels.map(level => {
        return {
            type: 'line',
            label: `${level.label}`,
            data: ohlcData.map(d => ({ x: d.x, y: level.price })),
            borderColor: level.color,
            borderWidth: 1,
            borderDash: [5, 5],
            pointRadius: 0,
            fill: false,
            order: 1,
            yValue: level.price
        };
    });

    // تحديد ألوان أعمدة الحجم بناءً على اتجاه الشمعة
    const volumeColors = ohlcData.map(d => 
        (d.c >= d.o) ? 'rgba(11, 61, 11, 0.5)' : 'rgba(183, 28, 28, 0.5)'
    );
    
    const volumeBorderColors = ohlcData.map(d => 
        (d.c >= d.o) ? 'rgba(11, 61, 11, 0.8)' : 'rgba(183, 28, 28, 0.8)'
    );
    
    console.log('Volume colors sample:', volumeColors.slice(0, 3));
    console.log('Volume border colors sample:', volumeBorderColors.slice(0, 3));

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    charts[canvasId] = new Chart(ctx, {
        type: 'candlestick',
        data: {
            datasets: [{
                label: symbol,
                data: ohlcData,
                // استخدام الخصائص الصحيحة للمكتبة
                color: {
                    up: '#0B3D0B',
                    down: '#B71C1C',
                    unchanged: '#666666'
                },
                borderColor: {
                    up: '#0B3D0B',
                    down: '#B71C1C',
                    unchanged: '#666666'
                },
                yAxisID: 'y' // ربط السعر بالمحور الأساسي
            }, {
                // بيانات الحجم (Volume)
                type: 'bar',
                label: 'Volume',
                data: ohlcData.map(d => ({ x: d.x, y: d.v })),
                backgroundColor: volumeColors, // ألوان متغيرة
                borderColor: volumeBorderColors,
                borderWidth: 1,
                yAxisID: 'y1', // ربط الحجم بالمحور الثانوي
                order: 10 // ليكون في الخلفية
            }, {
                // خط القاع
                type: 'line',
                label: 'Lowest Low',
                data: lineData,
                borderColor: 'blue',
                borderWidth: 2,
                pointRadius: 0,
                fill: false,
                order: 0,
                yValue: minLow,
                yAxisID: 'y'
            }, 
            // خط القمة الأولى (فقط إذا وُجدت)
            ...(peakLineData.length > 0 ? [{
                type: 'line',
                label: 'First Peak',
                data: peakLineData,
                borderColor: 'orange',
                borderWidth: 2,
                pointRadius: 0,
                fill: false,
                order: 0,
                yValue: peakHigh,
                yAxisID: 'y'
            }] : []),
            // إضافة مستويات جان
            ...gannDatasets.map(d => ({ ...d, yAxisID: 'y' })),
            // إضافة مستويات فيبوناتشي
            ...fibDatasets.map(d => ({ ...d, yAxisID: 'y' }))]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                onComplete: function() {
                    console.log(`Chart rendered with ${this.data.datasets.length} datasets (including ${fibDatasets.length} Fibo levels)`);
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: `${symbol} - 6.5 Months`,
                    color: '#333',
                    font: {
                        size: 16
                    }
                }
            },
            layout: {
                padding: {
                    top: 10,
                    bottom: 10,
                    left: 10,
                    right: 100 // تقليل المساحة قليلاً
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'month'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        color: '#666'
                    }
                },
                y: {
                    position: 'right', // نقل المحور لليمين ليكون بجانب النصوص
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        color: '#666'
                    }
                },
                y1: {
                    position: 'left', // محور الحجم على اليسار
                    min: 0,
                    max: maxVolume * 5, // جعل الحجم يحتل الخمس السفلي فقط
                    grid: {
                        display: false // إخفاء خطوط الشبكة للحجم
                    },
                    ticks: {
                        display: false // إخفاء أرقام الحجم لعدم التشويش
                    }
                }
            }
        },
        plugins: [{
            id: 'customCanvasBackgroundColor',
            beforeDraw: (chart) => {
                const ctx = chart.canvas.getContext('2d');
                ctx.save();
                ctx.globalCompositeOperation = 'destination-over';
                ctx.fillStyle = 'white';
                ctx.fillRect(0, 0, chart.width, chart.height);
                ctx.restore();
            }
        }, {
            id: 'smartLabels',
            afterDraw: (chart) => {
                const ctx = chart.ctx;
                const yAxis = chart.scales.y;
                
                // 1. تجميع كل الملصقات المراد رسمها
                let labelsToDraw = [];
                
                chart.data.datasets.forEach((dataset) => {
                    if (dataset.type === 'line' && dataset.yValue !== undefined) {
                        const yPixel = yAxis.getPixelForValue(dataset.yValue);
                        
                        // تخطي إذا كان خارج الرسم
                        if (yPixel < chart.chartArea.top || yPixel > chart.chartArea.bottom) return;
                        
                        labelsToDraw.push({
                            text: dataset.label,
                            price: dataset.yValue,
                            y: yPixel,
                            color: dataset.borderColor
                        });
                    }
                });

                // 2. ترتيب الملصقات حسب الموقع الرأسي (من الأعلى للأسفل)
                labelsToDraw.sort((a, b) => a.y - b.y);

                // 3. منع التداخل (Collision Detection)
                const minSpacing = 14; // أقل مسافة مسموحة بين النصوص
                
                for (let i = 1; i < labelsToDraw.length; i++) {
                    const prev = labelsToDraw[i-1];
                    const curr = labelsToDraw[i];
                    
                    if (curr.y - prev.y < minSpacing) {
                        curr.y = prev.y + minSpacing;
                    }
                }

                // 4. رسم الملصقات
                ctx.save();
                ctx.font = '11px Arial'; // تصغير الخط
                ctx.textAlign = 'left';
                ctx.textBaseline = 'middle';

                labelsToDraw.forEach(label => {
                    const x = chart.chartArea.right + 5;
                    const priceText = label.price.toFixed(2);
                    
                    // رسم مربع خلفية صغير لتحسين القراءة
                    // ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                    // ctx.fillRect(x, label.y - 6, 80, 12);

                    // رسم اسم المستوى
                    ctx.fillStyle = label.color;
                    ctx.fillText(label.text, x, label.y);
                    
                    // رسم السعر بجانبه بخط أغمق
                    ctx.fillStyle = '#333';
                    ctx.fillText(priceText, x + 65, label.y);
                });
                
                ctx.restore();
            }
        }]
    });
    
    console.log(`✅ Chart created successfully for ${symbol} on canvas ${canvasId}`);
    console.log('Chart object:', charts[canvasId]);
}


// ========================================
// قائمة الأسهم
// ========================================
const stockListSection = document.getElementById('stock-list-section');
const stockTableBody = document.getElementById('stock-table-body');
const stockDatePicker = document.getElementById('stock-date-picker');
const stockDateReset = document.getElementById('stock-date-reset');
const currentDateDisplay = document.getElementById('current-date-display');
let currentStockData = [];
let sortDirection = 'desc'; // desc = تنازلي (الأعلى أولاً)
let currentMarket = 'saudi'; // السوق الحالي

// تهيئة تبويبات القائمة
document.querySelectorAll('[data-list-market]').forEach(btn => {
    btn.addEventListener('click', function() {
        // تحديث الأزرار
        document.querySelectorAll('[data-list-market]').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        // تحميل البيانات
        currentMarket = this.dataset.listMarket;
        loadStockList(currentMarket);
    });
});

// تهيئة أداة التاريخ
if (stockDatePicker) {
    stockDatePicker.addEventListener('change', function() {
        if (this.value) {
            loadStockList(currentMarket, this.value);
        }
    });
}

// زر إعادة تعيين التاريخ
if (stockDateReset) {
    stockDateReset.addEventListener('click', function() {
        if (stockDatePicker) stockDatePicker.value = '';
        loadStockList(currentMarket);
    });
}

// تحميل قائمة الأسهم
async function loadStockList(market, date = null) {
    if (!stockTableBody) {
        console.error('stockTableBody not found!');
        return;
    }
    
    console.log(`Loading stock list for market: ${market}${date ? `, date: ${date}` : ''}`);
    stockTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 20px;">جاري التحميل...</td></tr>';
    
    if (currentDateDisplay) {
        currentDateDisplay.textContent = 'جاري التحميل...';
    }
    
    try {
        // بناء URL مع التاريخ إذا تم تحديده
        let url = `${API_URL}/market-data/${market}`;
        if (date) {
            url += `?date=${date}`;
        }
        
        console.log(`Fetching from: ${url}`);
        const response = await fetch(url);
        if (!response.ok) throw new Error(`فشل جلب البيانات (${response.status})`);
        
        const result = await response.json();
        console.log(`Received ${result.data ? result.data.length : 0} stocks`);
        
        // تحديث عرض التاريخ
        if (result.date && currentDateDisplay) {
            const dateObj = new Date(result.date);
            const formattedDate = dateObj.toLocaleDateString('ar-SA', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                weekday: 'long'
            });
            currentDateDisplay.textContent = formattedDate;
            
            // تحديث قيمة date picker إذا لم تكن محددة
            if (!date && stockDatePicker) {
                stockDatePicker.value = result.date;
            }
        }
        
        // عرض رسالة إذا لم توجد بيانات
        if (result.message && currentStockData.length === 0) {
            stockTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 20px; color: var(--text-secondary);">${result.message}</td></tr>`;
            return;
        }
        
        currentStockData = result.data || [];
        
        if (currentStockData.length === 0) {
            console.warn('No data received from API');
            stockTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 20px;">لا توجد بيانات</td></tr>';
            return;
        }
        
        // ترتيب افتراضي حسب النسبة (تنازلي)
        sortStockData('percent', 'desc');
        
        renderStockTable(market);
        
    } catch (error) {
        console.error('Error loading stock list:', error);
        stockTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color: var(--danger); padding: 20px;">خطأ: ${error.message}</td></tr>`;
        if (currentDateDisplay) {
            currentDateDisplay.textContent = 'خطأ في التحميل';
        }
    }
}

// عرض الجدول
function renderStockTable(market) {
    if (!stockTableBody) return;
    
    stockTableBody.innerHTML = '';
    
    if (currentStockData.length === 0) {
        stockTableBody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding: 20px;">لا توجد بيانات</td></tr>';
        return;
    }
    
    currentStockData.forEach(item => {
        const tr = document.createElement('tr');
        
        // تحديد لون التغيير
        const changeClass = item.change > 0 ? 'positive' : (item.change < 0 ? 'negative' : 'neutral');
        const changeSign = item.change > 0 ? '+' : '';
        
        // تنسيق الأرقام
        const price = item.price.toFixed(2);
        const change = `${changeSign}${item.change.toFixed(2)}`;
        const percent = `${changeSign}${item.change_percent.toFixed(2)}%`;
        const volume = item.volume.toLocaleString();
        
        // للسوق الأمريكي نعرض الرمز فقط في خانة الاسم
        const displayName = market === 'us' ? '-' : item.name;
        
        tr.innerHTML = `
            <td style="font-weight:bold; color:var(--text-primary)">${item.symbol}</td>
            <td>${displayName}</td>
            <td>${price}</td>
            <td class="${changeClass}">${change}</td>
            <td class="${changeClass}" dir="ltr">${percent}</td>
            <td>${volume}</td>
        `;
        
        stockTableBody.appendChild(tr);
    });
}

// ترتيب البيانات
function sortStockData(criteria, direction) {
    currentStockData.sort((a, b) => {
        let valA, valB;
        
        if (criteria === 'percent') {
            valA = a.change_percent;
            valB = b.change_percent;
        }
        
        if (direction === 'asc') {
            return valA - valB;
        } else {
            return valB - valA;
        }
    });
}

// تفعيل الترتيب عند النقر على الترويسة
document.querySelector('.sortable[data-sort="percent"]')?.addEventListener('click', function() {
    // عكس الاتجاه
    sortDirection = sortDirection === 'desc' ? 'asc' : 'desc';
    
    // تحديث الأيقونة
    const icon = this.querySelector('.sort-icon');
    if (icon) icon.textContent = sortDirection === 'asc' ? '↑' : '↓';
    
    // إعادة الترتيب والعرض
    sortStockData('percent', sortDirection);
    
    // معرفة السوق الحالي من الزر النشط
    const activeBtn = document.querySelector('[data-list-market].active');
    const market = activeBtn ? activeBtn.dataset.listMarket : 'saudi';
    
    renderStockTable(market);
});

// ربط التنقل في الشريط الجانبي (المعالج الموحد)
document.querySelectorAll('.nav-item').forEach((item, index) => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        
        // تجاهل زر الخروج
        if (this.id === 'logout-btn') return;
        
        // إغلاق القائمة الجانبية
        const mainSidebar = document.getElementById('main-sidebar');
        const container = document.querySelector('.container');
        if (mainSidebar) {
            mainSidebar.classList.remove('active');
        }
        if (container) {
            container.classList.remove('sidebar-open');
        }
        
        // إعادة رسم الشارتات بعد إغلاق القائمة
        setTimeout(() => {
            if (window.resizeCharts) window.resizeCharts();
        }, 350);
        
        // تحديث النشاط
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
        
        // إخفاء جميع الأقسام
        if (marketOverview) marketOverview.style.display = 'none';
        if (fiboGannSection) fiboGannSection.classList.add('section-hidden');
        if (fiboGannSection) fiboGannSection.style.display = 'none'; // تأكيد الإخفاء
        if (fiboFilterSection) fiboFilterSection.style.display = 'none';
        if (stockListSection) stockListSection.classList.add('section-hidden');
        const weeklyFilterSection = document.getElementById('weekly-filter');
        if (weeklyFilterSection) weeklyFilterSection.style.display = 'none';
        
        const text = this.querySelector('span').textContent.trim();
        
        // تحديث عنوان التبويب
        const currentSectionTitle = document.getElementById('current-section-title');
        if (currentSectionTitle) {
            currentSectionTitle.textContent = text;
        }
        
        if (text === 'الرئيسية') {
            if (marketOverview) marketOverview.style.display = 'block';
            document.body.classList.remove('chart-view');
        } else if (text === 'تحديث البيانات') {
            // العودة للرئيسية خلف المودال
            if (marketOverview) marketOverview.style.display = 'block';
            document.body.classList.remove('chart-view');
            document.getElementById('update-modal').classList.add('active');
        } else if (text === 'قائمة الأسهم') {
            if (stockListSection) stockListSection.classList.remove('section-hidden');
            document.body.classList.remove('chart-view');
            // تحميل البيانات افتراضياً للسعودي إذا لم يتم التحميل
            if (currentStockData.length === 0) loadStockList('saudi');
        } else if (text === 'جان وفيبو') {
            if (fiboGannSection) {
                fiboGannSection.classList.remove('section-hidden');
                fiboGannSection.style.display = 'block';
                // إضافة class لمنع scroll رأسي
                document.body.classList.add('chart-view');
                // تحميل الرموز إذا كانت القائمة فارغة
                if (stockList && stockList.children.length <= 1) fetchSymbols('saudi');
                // إعادة رسم الشارتات بعد انتهاء الانيميشن
                setTimeout(() => {
                    if (window.resizeCharts) window.resizeCharts();
                }, 350);
            }
        } else if (text === 'فلترة جان وفيبو') {
            if (fiboFilterSection) {
                fiboFilterSection.style.display = 'block';
                // إضافة class لمنع scroll رأسي
                document.body.classList.add('chart-view');
                initFiboFilter();
                // إعادة رسم الشارتات بعد انتهاء الانيميشن
                setTimeout(() => {
                    if (window.resizeCharts) window.resizeCharts();
                }, 350);
            }
        } else if (text === 'فلترة أسبوعية') {
            const weeklyFilterSection = document.getElementById('weekly-filter');
            if (weeklyFilterSection) {
                weeklyFilterSection.style.display = 'block';
                document.body.classList.add('chart-view');
                initWeeklyFilter();
                setTimeout(() => {
                    if (window.resizeCharts) window.resizeCharts();
                }, 350);
            }
        }
    });
});

// ========================================
// الفلترة الأسبوعية (Weekly Filter)
// ========================================

let weeklyCurrentMarket = 'saudi';

function initWeeklyFilter() {
    console.log('Initializing weekly filter...');
    
    // تهيئة تبويبات السوق
    const weeklyTabs = document.querySelectorAll('[data-weekly-market]');
    weeklyTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            weeklyTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            weeklyCurrentMarket = this.dataset.weeklyMarket;
            
            // مسح النتائج عند تغيير السوق
            const resultsDiv = document.getElementById('weekly-scan-results');
            if (resultsDiv) {
                resultsDiv.innerHTML = '<div class="placeholder-text" style="padding: 20px; text-align: center; color: #666;">اضغط "فحص أسبوعي" للبدء</div>';
            }
        });
    });
    
    // زر الفحص
    const weeklyScanBtn = document.getElementById('weekly-scan-btn');
    if (weeklyScanBtn) {
        weeklyScanBtn.addEventListener('click', function() {
            performWeeklyScan(weeklyCurrentMarket);
        });
    }
    
    console.log('Weekly filter initialized successfully');
}

async function performWeeklyScan(market) {
    const resultsDiv = document.getElementById('weekly-scan-results');
    const scanBtn = document.getElementById('weekly-scan-btn');
    
    if (!resultsDiv) return;
    
    // عرض مؤشر تحميل
    resultsDiv.innerHTML = '<div class="fg-loading" style="padding: 40px; text-align: center;"><div class="spinner"></div><p>جاري الفحص الأسبوعي...</p></div>';
    
    if (scanBtn) {
        scanBtn.disabled = true;
        scanBtn.textContent = '⏳ جاري الفحص...';
    }
    
    try {
        console.log(`Starting weekly scan for ${market} market...`);
        
        const response = await fetch(`${API_URL}/scan/weekly/${market}`);
        const data = await response.json();
        
        console.log(`Weekly scan completed: ${data.count} results found`);
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        if (!data.results || data.results.length === 0) {
            resultsDiv.innerHTML = `
                <div style="padding: 20px; text-align: center;">
                    <p style="color: #666; font-size: 14px;">لا توجد أسهم مطابقة للشروط</p>
                    <p style="color: #999; font-size: 12px; margin-top: 10px;">
                        الشروط: شمعة خضراء + إغلاق عند القمة + حجم متزايد
                    </p>
                </div>
            `;
        } else {
            renderWeeklyResults(data.results, market);
        }
        
    } catch (error) {
        console.error('Error in weekly scan:', error);
        resultsDiv.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--danger);">خطأ: ${error.message}</div>`;
    } finally {
        if (scanBtn) {
            scanBtn.disabled = false;
            scanBtn.textContent = '📊 فحص أسبوعي';
        }
    }
}

function renderWeeklyResults(results, market) {
    const container = document.getElementById('weekly-scan-results');
    if (!container) return;
    
    container.innerHTML = '';
    
    results.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'stock-item';
        
        const changeColor = item.change_percent > 0 ? 'green' : 'red';
        
        div.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; padding: 8px;">
                <div>
                    <span class="stock-symbol" style="font-weight:bold; color:#333">${item.symbol}</span>
                    <span class="stock-name" style="font-size:0.85em; color:#666; display:block;">
                        📊 ${item.close} | حجم: ${item.volume_ratio}x
                    </span>
                </div>
                <div style="text-align:left">
                    <span style="display:block; font-size:0.9em; color:${changeColor}; font-weight:bold">
                        ${item.change_percent > 0 ? '+' : ''}${item.change_percent}%
                    </span>
                    <span style="font-size:0.75em; color:#999">عند القمة</span>
                </div>
            </div>
        `;
        
        div.addEventListener('click', () => {
            document.querySelectorAll('#weekly-scan-results .stock-item').forEach(i => i.classList.remove('active'));
            div.classList.add('active');
            loadWeeklyChart(market, item.symbol);
        });
        
        container.appendChild(div);
    });
}

async function loadWeeklyChart(market, symbol) {
    const canvas = document.getElementById('weekly-chart');
    if (!canvas) return;
    
    try {
        console.log(`Loading weekly chart for ${symbol}...`);
        
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = '20px Tajawal';
        ctx.fillStyle = '#667eea';
        ctx.textAlign = 'center';
        ctx.fillText('جاري تحميل البيانات الأسبوعية...', canvas.width / 2, canvas.height / 2);
        
        // جلب البيانات اليومية
        const response = await fetch(`${API_URL}/history/${market}/${symbol}`);
        const dailyData = await response.json();
        
        if (dailyData.error) throw new Error(dailyData.error);
        
        // تحويل لبيانات أسبوعية في الـ frontend
        const weeklyData = convertToWeekly(dailyData);
        
        // رسم الشارت
        renderWeeklyChartData(symbol, weeklyData);
        
    } catch (error) {
        console.error('Error loading weekly chart:', error);
        alert(`فشل تحميل الشارت: ${error.message}`);
    }
}

function convertToWeekly(dailyData) {
    // تحويل البيانات اليومية إلى أسبوعية
    const weekly = {};
    
    dailyData.forEach(day => {
        const date = new Date(day.Date);
        // الحصول على بداية الأسبوع (الأحد)
        const weekStart = new Date(date);
        weekStart.setDate(date.getDate() - date.getDay());
        const weekKey = weekStart.toISOString().split('T')[0];
        
        if (!weekly[weekKey]) {
            weekly[weekKey] = {
                Date: weekKey,
                Open: day.Open,
                High: day.High,
                Low: day.Low,
                Close: day.Close,
                Volume: 0
            };
        } else {
            weekly[weekKey].High = Math.max(weekly[weekKey].High, day.High);
            weekly[weekKey].Low = Math.min(weekly[weekKey].Low, day.Low);
            weekly[weekKey].Close = day.Close; // آخر إغلاق
        }
        
        weekly[weekKey].Volume += day.Volume;
    });
    
    return Object.values(weekly).slice(-26); // آخر 26 أسبوع (6 أشهر)
}

function renderWeeklyChartData(symbol, data) {
    const canvas = document.getElementById('weekly-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    const ohlcData = data.map(d => ({
        x: new Date(d.Date).valueOf(),
        o: parseFloat(d.Open),
        h: parseFloat(d.High),
        l: parseFloat(d.Low),
        c: parseFloat(d.Close),
        v: parseFloat(d.Volume)
    }));
    
    if (charts['weekly-chart']) {
        charts['weekly-chart'].destroy();
    }
    
    charts['weekly-chart'] = new Chart(ctx, {
        type: 'candlestick',
        data: {
            datasets: [{
                label: symbol,
                data: ohlcData,
                color: {
                    up: '#0B3D0B',
                    down: '#B71C1C',
                    unchanged: '#666666'
                },
                borderColor: {
                    up: '#0B3D0B',
                    down: '#B71C1C',
                    unchanged: '#666666'
                }
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: `${symbol} - Weekly Chart (6 Months)`,
                    color: '#333',
                    font: { size: 16 }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: { unit: 'week' },
                    grid: { color: 'rgba(0, 0, 0, 0.1)' },
                    ticks: { color: '#666' }
                },
                y: {
                    position: 'right',
                    grid: { color: 'rgba(0, 0, 0, 0.1)' },
                    ticks: { color: '#666' }
                }
            }
        }
    });
    
    console.log(`✅ Weekly chart rendered for ${symbol}`);
}

// تسجيل الخروج
document.getElementById('logout-btn')?.addEventListener('click', function(e) {
    e.preventDefault();
    if (confirm('هل أنت متأكد من تسجيل الخروج؟')) {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('token_expires');
        window.location.href = 'login.html';
    }
});

// تشغيل التهيئة
document.addEventListener('DOMContentLoaded', initFiboGann);
