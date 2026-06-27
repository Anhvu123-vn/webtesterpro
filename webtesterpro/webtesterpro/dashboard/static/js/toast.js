"""Toast Notification System - Client-side JavaScript."""

TOAST_CONTAINER_ID = "toast-container"

TOAST_JS = """
// Toast Notification System
class ToastManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Create container if not exists
        this.container = document.getElementById('toast-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'toast-container';
            this.container.className = 'fixed top-4 right-4 z-[9999] flex flex-col gap-3 max-w-sm';
            document.body.appendChild(this.container);
        }
    }

    show({ type = 'info', title, message, duration = 5000, actions = [] }) {
        const toast = document.createElement('div');
        const typeClasses = {
            success: 'border-emerald-500/30 bg-emerald-500/10',
            error: 'border-red-500/30 bg-red-500/10',
            warning: 'border-amber-500/30 bg-amber-500/10',
            info: 'border-accent/30 bg-accent/10',
            progress: 'border-violet-500/30 bg-violet-500/10',
        };
        const iconClasses = {
            success: 'text-emerald-400',
            error: 'text-red-400',
            warning: 'text-amber-400',
            info: 'text-accent-light',
            progress: 'text-violet-400',
        };
        const icons = {
            success: 'check-circle-2',
            error: 'alert-circle',
            warning: 'alert-triangle',
            info: 'info',
            progress: 'loader-circle',
        };

        toast.className = `card rounded-xl p-4 border ${typeClasses[type] || typeClasses.info} shadow-xl animate-slide-down`;
        toast.innerHTML = `
            <div class="flex items-start gap-3">
                <i data-lucide="${icons[type] || icons.info}" class="w-5 h-5 ${iconClasses[type] || iconClasses.info} shrink-0 mt-0.5"></i>
                <div class="flex-1 min-w-0">
                    ${title ? `<p class="text-sm font-semibold text-slate-100">${this.escapeHtml(title)}</p>` : ''}
                    ${message ? `<p class="text-xs text-slate-400 mt-1">${this.escapeHtml(message)}</p>` : ''}
                    ${actions.length > 0 ? `
                        <div class="flex gap-2 mt-3">
                            ${actions.map(a => `
                                <a href="${this.escapeHtml(a.href)}" 
                                   class="text-xs px-3 py-1.5 rounded-lg ${a.primary ? 'bg-accent text-white' : 'bg-canvas-hover text-slate-300'} font-medium hover:opacity-80 transition-opacity">
                                    ${this.escapeHtml(a.label)}
                                </a>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
                <button onclick="this.closest('.toast-item').remove()" 
                        class="text-slate-500 hover:text-slate-300 transition-colors shrink-0">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            </div>
        `;
        toast.classList.add('toast-item');
        
        // Animate in
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        this.container.appendChild(toast);
        lucide.createIcons({ nodes: [toast] });
        
        requestAnimationFrame(() => {
            toast.style.transition = 'all 0.3s ease-out';
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        });

        // Auto remove
        if (duration > 0) {
            setTimeout(() => this.remove(toast), duration);
        }

        return toast;
    }

    remove(toast) {
        toast.style.transition = 'all 0.3s ease-out';
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }

    success(title, message, options = {}) {
        return this.show({ type: 'success', title, message, ...options });
    }

    error(title, message, options = {}) {
        return this.show({ type: 'error', title, message, ...options });
    }

    warning(title, message, options = {}) {
        return this.show({ type: 'warning', title, message, ...options });
    }

    info(title, message, options = {}) {
        return this.show({ type: 'info', title, message, ...options });
    }

    progress(title, message, options = {}) {
        return this.show({ type: 'progress', title, message, ...options });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global instance
window.toast = new ToastManager();

// Test notification helper
window.showTestComplete = function(reportId, score, url) {
    const scoreColor = score >= 80 ? 'emerald' : score >= 50 ? 'amber' : 'red';
    window.toast.success(
        'Test Hoàn thành!',
        `Website "${url}" đã được kiểm tra. Score: ${score}`,
        {
            duration: 8000,
            actions: [
                { label: 'Xem kết quả', href: `/results/${reportId}`, primary: true }
            ]
        }
    );
};

// SSE Connection Manager
class SSEManager {
    constructor() {
        this.connections = new Map(); // reportId -> EventSource
        this.handlers = new Map(); // reportId -> handler function
    }

    connect(reportId, onProgress, onComplete, onError) {
        if (this.connections.has(reportId)) {
            this.disconnect(reportId);
        }

        const eventSource = new EventSource(`/results/${reportId}/stream`);
        
        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'progress') {
                onProgress && onProgress(data);
            } else if (data.type === 'complete') {
                onComplete && onComplete(data);
                this.disconnect(reportId);
            } else if (data.type === 'error') {
                onError && onError(data);
                this.disconnect(reportId);
            }
        };

        eventSource.onerror = () => {
            onError && onError({ message: 'Connection lost' });
            this.disconnect(reportId);
        };

        this.connections.set(reportId, eventSource);
        return eventSource;
    }

    disconnect(reportId) {
        const eventSource = this.connections.get(reportId);
        if (eventSource) {
            eventSource.close();
            this.connections.delete(reportId);
        }
    }

    disconnectAll() {
        this.connections.forEach((eventSource) => eventSource.close());
        this.connections.clear();
    }
}

window.sseManager = new SSEManager();
"""
