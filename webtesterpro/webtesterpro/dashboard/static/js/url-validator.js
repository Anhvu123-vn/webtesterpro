/**
 * URL Validation and Preview
 * 
 * Real-time URL validation with preview functionality.
 */

(function() {
    'use strict';

    // Debounce helper
    function debounce(func, wait) {
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

    // Validate URL format
    function isValidUrl(string) {
        try {
            const url = new URL(string);
            return url.protocol === 'http:' || url.protocol === 'https:';
        } catch (_) {
            return false;
        }
    }

    // Parse URL to get components
    function parseUrl(urlString) {
        try {
            const url = new URL(urlString);
            return {
                valid: true,
                protocol: url.protocol.replace(':', ''),
                hostname: url.hostname,
                pathname: url.pathname,
                port: url.port,
                search: url.search,
                hash: url.hash,
                isSecure: url.protocol === 'https:',
            };
        } catch (_) {
            return { valid: false };
        }
    }

    // Create validation UI element
    function createValidationUI(input) {
        const wrapper = input.closest('.url-input-wrapper');
        if (!wrapper) return;

        // Remove existing indicator if any
        const existing = wrapper.querySelector('.url-validation-indicator');
        if (existing) existing.remove();

        const indicator = document.createElement('div');
        indicator.className = 'url-validation-indicator absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2';
        indicator.innerHTML = `
            <span class="text-xs text-slate-500 url-status">Checking...</span>
            <i data-lucide="loader" class="w-4 h-4 text-slate-500 animate-spin url-icon"></i>
        `;
        
        wrapper.style.position = 'relative';
        wrapper.appendChild(indicator);
        
        if (window.lucide) lucide.createIcons({ nodes: [indicator] });
        
        return indicator;
    }

    // Update validation UI
    function updateValidationUI(input, isValid, urlData = null) {
        const wrapper = input.closest('.url-input-wrapper');
        if (!wrapper) return;

        const indicator = wrapper.querySelector('.url-validation-indicator');
        if (!indicator) return;

        const status = indicator.querySelector('.url-status');
        const icon = indicator.querySelector('.url-icon');

        if (isValid) {
            status.textContent = urlData?.isSecure ? 'Secure' : 'HTTP';
            status.className = `text-xs ${urlData?.isSecure ? 'text-emerald-400' : 'text-amber-400'} url-status`;
            icon.setAttribute('data-lucide', urlData?.isSecure ? 'lock' : 'unlock');
            icon.className = `w-4 h-4 ${urlData?.isSecure ? 'text-emerald-400' : 'text-amber-400'} url-icon`;
            
            // Add success border to input
            input.classList.add('border-emerald-500/50');
            input.classList.remove('border-red-500/50');
        } else {
            status.textContent = 'Invalid URL';
            status.className = 'text-xs text-red-400 url-status';
            icon.setAttribute('data-lucide', 'alert-circle');
            icon.className = 'w-4 h-4 text-red-400 url-icon';
            
            input.classList.add('border-red-500/50');
            input.classList.remove('border-emerald-500/50');
        }

        if (window.lucide) lucide.createIcons({ nodes: [indicator] });
    }

    // Create URL preview card
    function createPreviewCard(input) {
        const existing = document.getElementById('url-preview-card');
        if (existing) existing.remove();

        const card = document.createElement('div');
        card.id = 'url-preview-card';
        card.className = 'absolute left-0 right-0 top-full mt-2 card rounded-xl p-4 z-50 shadow-xl';
        card.style.display = 'none';
        
        card.innerHTML = `
            <div class="url-preview-content">
                <div class="flex items-center gap-3 mb-3">
                    <div class="w-10 h-10 rounded-lg bg-canvas-hover flex items-center justify-center">
                        <i data-lucide="globe" class="w-5 h-5 text-accent url-preview-icon"></i>
                    </div>
                    <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium text-slate-200 truncate url-preview-host">—</p>
                        <p class="text-xs text-slate-500 truncate url-preview-path">—</p>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs">
                    <div class="bg-canvas-hover/50 rounded-lg p-2">
                        <p class="text-slate-500">Protocol</p>
                        <p class="text-slate-300 font-medium url-preview-protocol">—</p>
                    </div>
                    <div class="bg-canvas-hover/50 rounded-lg p-2">
                        <p class="text-slate-500">Port</p>
                        <p class="text-slate-300 font-medium url-preview-port">—</p>
                    </div>
                </div>
            </div>
        `;

        const formGroup = input.closest('.card') || input.parentElement;
        formGroup.style.position = 'relative';
        formGroup.appendChild(card);

        if (window.lucide) lucide.createIcons({ nodes: [card] });

        return card;
    }

    // Update preview card
    function updatePreviewCard(card, urlData) {
        if (!urlData || !urlData.valid) {
            card.style.display = 'none';
            return;
        }

        const icon = card.querySelector('.url-preview-icon');
        const host = card.querySelector('.url-preview-host');
        const path = card.querySelector('.url-preview-path');
        const protocol = card.querySelector('.url-preview-protocol');
        const port = card.querySelector('.url-preview-port');

        icon.className = `w-5 h-5 ${urlData.isSecure ? 'text-emerald-400' : 'text-amber-400'} url-preview-icon`;
        icon.setAttribute('data-lucide', urlData.isSecure ? 'lock' : 'unlock');
        
        host.textContent = urlData.hostname;
        path.textContent = urlData.pathname === '/' ? '(root)' : (urlData.pathname || '/');
        protocol.textContent = urlData.protocol.toUpperCase();
        port.textContent = urlData.port || (urlData.isSecure ? '443 (default)' : '80 (default)');

        card.style.display = 'block';
        if (window.lucide) lucide.createIcons({ nodes: [card] });
    }

    // Initialize URL inputs
    function initUrlInputs() {
        const urlInputs = document.querySelectorAll('input[name="url"], input[type="url"]');
        
        urlInputs.forEach(input => {
            // Skip if already initialized
            if (input.dataset.urlInit) return;
            input.dataset.urlInit = 'true';

            // Add wrapper class if not present
            if (!input.classList.contains('url-input-wrapper')) {
                input.parentElement.classList.add('url-input-wrapper');
            }

            // Create UI elements
            createValidationUI(input);
            const previewCard = createPreviewCard(input);

            // Debounced validation
            const validateUrl = debounce(() => {
                let url = input.value.trim();
                
                // Auto-prepend https if missing
                if (url && !url.startsWith('http://') && !url.startsWith('https://')) {
                    url = 'https://' + url;
                    if (document.activeElement !== input) {
                        input.value = url;
                    }
                }

                if (!url) {
                    updateValidationUI(input, false);
                    updatePreviewCard(previewCard, null);
                    return;
                }

                const urlData = parseUrl(url);
                updateValidationUI(input, urlData.valid, urlData);
                updatePreviewCard(previewCard, urlData);
            }, 300);

            // Event listeners
            input.addEventListener('input', validateUrl);
            input.addEventListener('blur', () => {
                // Final validation on blur
                let url = input.value.trim();
                if (url && !url.startsWith('http')) {
                    url = 'https://' + url;
                    input.value = url;
                }
                validateUrl();
            });
        });
    }

    // Auto-init on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initUrlInputs);
    } else {
        initUrlInputs();
    }

    // Re-init on HTMX swaps
    document.body.addEventListener('htmx:afterSwap', initUrlInputs);

    // Expose for external use
    window.urlValidator = {
        isValidUrl,
        parseUrl,
        init: initUrlInputs,
    };

})();
