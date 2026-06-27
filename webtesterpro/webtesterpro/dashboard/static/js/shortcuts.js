/**
 * Keyboard Shortcuts Handler
 * 
 * Global keyboard shortcuts for power users:
 * - Ctrl/Cmd + Enter: Submit form
 * - Ctrl/Cmd + N: New test
 * - Ctrl/Cmd + /: Show shortcuts help
 * - Escape: Close modals/dropdowns
 * - G then H: Go to home (Vim-style)
 * - G then A: Go to analytics
 */

(function() {
    'use strict';

    // Shortcut state for multi-key combos
    let lastKey = null;
    let comboTimeout = null;

    // Shortcut definitions
    const shortcuts = {
        // Single key
        'Escape': { action: 'close_modals', description: 'Đóng modal/dropdown' },
        
        // Ctrl/Cmd combinations
        'mod+Enter': { action: 'submit_form', description: 'Submit form hiện tại' },
        'mod+n': { action: 'new_test', description: 'Tạo test mới' },
        'mod+s': { action: 'save', description: 'Lưu (trong form)' },
        'mod+/': { action: 'show_help', description: 'Hiện phím tắt' },
        'mod+k': { action: 'search', description: 'Tìm kiếm' },
        
        // Vim-style G combos
        'g h': { action: 'go_home', description: 'Về trang chủ' },
        'g a': { action: 'go_analytics', description: 'Đến Analytics' },
        'g t': { action: 'go_new_test', description: 'Tạo test mới' },
    };

    // Key mappings
    const modKey = navigator.platform.includes('Mac') ? 'metaKey' : 'ctrlKey';
    const modName = navigator.platform.includes('Mac') ? '⌘' : 'Ctrl';

    function handleShortcut(e) {
        // Don't trigger shortcuts when typing in inputs
        const tagName = e.target.tagName.toLowerCase();
        const isEditable = e.target.isContentEditable || 
                          tagName === 'input' || 
                          tagName === 'textarea' || 
                          tagName === 'select';
        
        // Allow Escape even in inputs
        if (e.key !== 'Escape' && isEditable) return;

        // Build shortcut key
        let key = e.key;
        
        // Handle mod key
        if (e[modKey]) {
            if (key === 'Enter') key = 'mod+Enter';
            else if (key === 'N' || key === 'n') key = 'mod+n';
            else if (key === 'S' || key === 's') key = 'mod+s';
            else if (key === '/') key = 'mod+/';
            else if (key === 'K' || key === 'k') key = 'mod+k';
            else return; // Other Ctrl combinations
        }

        // Handle G combos
        if (key === 'g' && !e[modKey]) {
            if (comboTimeout) clearTimeout(comboTimeout);
            lastKey = 'g';
            comboTimeout = setTimeout(() => { lastKey = null; }, 500);
            return;
        }

        // Check for combo
        if (lastKey === 'g') {
            key = 'g ' + key.toLowerCase();
            lastKey = null;
            if (comboTimeout) clearTimeout(comboTimeout);
        }

        // Find matching shortcut
        const shortcut = shortcuts[key];
        if (!shortcut) return;

        // Prevent default
        e.preventDefault();

        // Execute action
        executeAction(shortcut.action, e);
    }

    function executeAction(action, e) {
        switch(action) {
            case 'close_modals':
                // Close Alpine dropdowns
                document.querySelectorAll('[x-data]').forEach(el => {
                    if (el._x_dataStack && el._x_dataStack[0]) {
                        const data = el._x_dataStack[0];
                        if (typeof data.open !== 'undefined') data.open = false;
                    }
                });
                // Close any open modals
                document.querySelectorAll('[x-show]').forEach(el => {
                    if (el._x_isOpen) el._x_isOpen = false;
                });
                break;

            case 'submit_form':
                const form = e.target.closest('form');
                if (form) {
                    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
                }
                break;

            case 'new_test':
                window.location.href = '/test/new';
                break;

            case 'go_home':
                window.location.href = '/';
                break;

            case 'go_analytics':
                window.location.href = '/analytics';
                break;

            case 'go_new_test':
                window.location.href = '/test/new';
                break;

            case 'show_help':
                showShortcutsHelp();
                break;

            case 'search':
                // Focus search input if exists
                const searchInput = document.querySelector('input[type="search"], input[placeholder*="search" i]');
                if (searchInput) searchInput.focus();
                break;

            case 'save':
                // Trigger save action if in form
                const saveBtn = document.querySelector('[data-action="save"]');
                if (saveBtn) saveBtn.click();
                break;
        }
    }

    function showShortcutsHelp() {
        // Create or show shortcuts modal
        let modal = document.getElementById('shortcuts-modal');
        
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'shortcuts-modal';
            modal.className = 'fixed inset-0 z-[9999] flex items-center justify-center';
            modal.innerHTML = `
                <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" onclick="document.getElementById('shortcuts-modal').remove()"></div>
                <div class="relative card rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-lg font-semibold text-slate-100 flex items-center gap-2">
                            <i data-lucide="keyboard" class="w-5 h-5 text-accent"></i>
                            Keyboard Shortcuts
                        </h3>
                        <button onclick="document.getElementById('shortcuts-modal').remove()" 
                                class="text-slate-500 hover:text-slate-300">
                            <i data-lucide="x" class="w-5 h-5"></i>
                        </button>
                    </div>
                    <div class="space-y-2 text-sm" id="shortcuts-list">
                        <!-- Filled by JS -->
                    </div>
                    <div class="mt-4 pt-4 border-t border-border text-xs text-slate-500 text-center">
                        Press ${modName}+/ to toggle this help
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        } else {
            modal.remove();
            return;
        }

        // Build shortcuts list
        const list = document.getElementById('shortcuts-list');
        const shortcutsHTML = [
            { key: '⌘/Ctrl + Enter', desc: 'Submit form' },
            { key: '⌘/Ctrl + N', desc: 'New test' },
            { key: '⌘/Ctrl + K', desc: 'Search' },
            { key: '⌘/Ctrl + /', desc: 'Toggle shortcuts help' },
            { key: 'G then H', desc: 'Go to Home' },
            { key: 'G then A', desc: 'Go to Analytics' },
            { key: 'G then T', desc: 'New Test' },
            { key: 'Escape', desc: 'Close modal/dropdown' },
        ].map(s => `
            <div class="flex items-center justify-between py-2">
                <span class="text-slate-400">${s.desc}</span>
                <kbd class="px-2 py-1 bg-canvas-hover rounded text-xs font-mono text-slate-300">${s.key}</kbd>
            </div>
        `).join('');
        
        list.innerHTML = shortcutsHTML;
        
        // Re-init icons
        if (window.lucide) lucide.createIcons();
    }

    // Register global listener
    document.addEventListener('keydown', handleShortcut);

    // Expose for debugging
    window.shortcuts = { shortcuts, showHelp: showShortcutsHelp };

})();
