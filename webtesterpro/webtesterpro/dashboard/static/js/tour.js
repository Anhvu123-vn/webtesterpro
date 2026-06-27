/**
 * Onboarding Tour
 * 
 * Interactive guide for first-time users.
 */

(function() {
    'use strict';

    const TOUR_KEY = 'webtesterpro_tour_done';

    // Tour steps
    const tourSteps = [
        {
            element: '[data-tour="dashboard"]',
            title: 'Chào mừng đến WebTesterPro!',
            content: 'Đây là dashboard chính nơi bạn có thể xem tổng quan về các bài test và truy cập nhanh các chức năng.',
            position: 'center',
        },
        {
            element: 'a[href="/test/new"]',
            title: 'Tạo Test Mới',
            content: 'Nhấp vào đây để bắt đầu một bài kiểm tra website mới. Bạn có thể chọn nhiều module khác nhau.',
            position: 'bottom',
        },
        {
            element: '[data-tour="modules"]',
            title: 'Các Module Kiểm Tra',
            content: 'WebTesterPro cung cấp 8 module kiểm tra: Security, Performance, SEO, Accessibility, Visual, Crawler, Scanner, và Monitor.',
            position: 'top',
        },
        {
            element: '[data-tour="analytics"]',
            title: 'Theo Dõi Analytics',
            content: 'Xem biểu đồ xu hướng điểm số, tần suất test, và các metrics khác để hiểu rõ hơn về hiệu suất website.',
            position: 'left',
        },
        {
            element: '[data-tour="history"]',
            title: 'Lịch Sử Tests',
            content: 'Tất cả các bài test trước đó được lưu lại ở đây. Bạn có thể xem lại, so sánh, và chia sẻ kết quả.',
            position: 'right',
        },
    ];

    let currentStep = 0;
    let tourElement = null;

    function createTourUI() {
        tourElement = document.createElement('div');
        tourElement.id = 'onboarding-tour';
        tourElement.innerHTML = `
            <div class="fixed inset-0 z-[9998] bg-black/40 backdrop-blur-sm"></div>
            <div class="fixed z-[9999] card rounded-2xl p-6 max-w-sm shadow-2xl" id="tour-card">
                <div class="absolute -top-3 left-1/2 -translate-x-1/2 w-6 h-6 bg-accent rounded-full flex items-center justify-center">
                    <i data-lucide="sparkles" class="w-4 h-4 text-white"></i>
                </div>
                <div class="mb-4">
                    <h3 class="text-lg font-semibold text-slate-100" id="tour-title">—</h3>
                    <p class="text-sm text-slate-400 mt-2" id="tour-content">—</p>
                </div>
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-1" id="tour-dots"></div>
                    <div class="flex items-center gap-2">
                        <button onclick="window.tour && window.tour.skip()" 
                                class="px-3 py-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors">
                            Bỏ qua
                        </button>
                        <button onclick="window.tour && window.tour.prev()" 
                                class="px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
                                id="tour-prev" style="display: none;">
                            ← Trước
                        </button>
                        <button onclick="window.tour && window.tour.next()" 
                                class="px-4 py-1.5 bg-accent hover:bg-accent-dark text-white text-xs font-medium rounded-lg transition-colors"
                                id="tour-next">
                            Tiếp →
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(tourElement);
        lucide.createIcons();
    }

    function updateTourPosition() {
        if (!tourElement || currentStep >= tourSteps.length) return;

        const step = tourSteps[currentStep];
        const card = tourElement.querySelector('#tour-card');
        const target = document.querySelector(step.element);

        if (!card) return;

        // Reset position
        card.style.position = 'fixed';
        card.style.left = '50%';
        card.style.top = '50%';
        card.style.transform = 'translate(-50%, -50%)';
        card.style.margin = '0';

        if (step.element === '[data-tour="dashboard"]' || !target) {
            // Center position for intro
            return;
        }

        if (target) {
            const rect = target.getBoundingClientRect();
            
            // Position based on step position
            switch(step.position) {
                case 'bottom':
                    card.style.top = `${rect.bottom + 20}px`;
                    card.style.left = `${rect.left + rect.width / 2}px`;
                    card.style.transform = 'translateX(-50%)';
                    break;
                case 'top':
                    card.style.top = `${rect.top - card.offsetHeight - 20}px`;
                    card.style.left = `${rect.left + rect.width / 2}px`;
                    card.style.transform = 'translateX(-50%)';
                    break;
                case 'left':
                    card.style.top = `${rect.top + rect.height / 2}px`;
                    card.style.left = `${rect.left - card.offsetWidth - 20}px`;
                    card.style.transform = 'translateY(-50%)';
                    break;
                case 'right':
                    card.style.top = `${rect.top + rect.height / 2}px`;
                    card.style.left = `${rect.right + 20}px`;
                    card.style.transform = 'translateY(-50%)';
                    break;
            }

            // Add highlight to target
            target.style.position = 'relative';
            target.style.zIndex = '9997';
            target.classList.add('tour-highlight');
        }
    }

    function updateStep() {
        if (!tourElement || currentStep >= tourSteps.length) return;

        const step = tourSteps[currentStep];
        const title = tourElement.querySelector('#tour-title');
        const content = tourElement.querySelector('#tour-content');
        const dots = tourElement.querySelector('#tour-dots');
        const prevBtn = tourElement.querySelector('#tour-prev');
        const nextBtn = tourElement.querySelector('#tour-next');

        title.textContent = step.title;
        content.textContent = step.content;

        // Update dots
        dots.innerHTML = tourSteps.map((_, i) => 
            `<span class="w-2 h-2 rounded-full ${i === currentStep ? 'bg-accent' : 'bg-slate-600'}"></span>`
        ).join('');

        // Update buttons
        prevBtn.style.display = currentStep > 0 ? 'block' : 'none';
        nextBtn.textContent = currentStep === tourSteps.length - 1 ? 'Hoàn thành ✓' : 'Tiếp →';

        // Remove previous highlights
        document.querySelectorAll('.tour-highlight').forEach(el => {
            el.classList.remove('tour-highlight');
        });

        // Update position
        updateTourPosition();
    }

    function startTour() {
        // Check if already done
        if (localStorage.getItem(TOUR_KEY)) return;

        createTourUI();
        currentStep = 0;
        updateStep();

        // Handle resize
        window.addEventListener('resize', updateTourPosition);
    }

    function completeTour() {
        localStorage.setItem(TOUR_KEY, 'true');
        if (tourElement) {
            tourElement.remove();
            tourElement = null;
        }
        document.querySelectorAll('.tour-highlight').forEach(el => {
            el.classList.remove('tour-highlight');
        });
    }

    // Expose tour API
    window.tour = {
        start: startTour,
        skip: completeTour,
        next: function() {
            currentStep++;
            if (currentStep >= tourSteps.length) {
                completeTour();
            } else {
                updateStep();
            }
        },
        prev: function() {
            if (currentStep > 0) {
                currentStep--;
                updateStep();
            }
        },
        restart: function() {
            localStorage.removeItem(TOUR_KEY);
            startTour();
        },
    };

    // Auto-start for new users
    if (!localStorage.getItem(TOUR_KEY)) {
        setTimeout(startTour, 1000);
    }

})();
