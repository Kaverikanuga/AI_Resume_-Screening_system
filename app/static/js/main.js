/* ============================================
   ResumeAI Pro - Main JavaScript
   Charts · Gauge · Animations · Upload · Chat
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

    /* ---------- Loading Overlay ---------- */
    setTimeout(function () {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.classList.add('hidden');
    }, 400);

    /* ---------- Theme Toggle ---------- */
    const themeBtns = document.querySelectorAll('[data-theme-toggle]');
    themeBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const isDark = document.body.classList.toggle('theme-light');
            const theme = isDark ? 'light' : 'dark';
            document.body.classList.toggle('dark-theme', !isDark);
            try {
                fetch('/api/theme', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrf()
                    },
                    body: JSON.stringify({ theme: theme })
                });
            } catch (e) { /* non-fatal */ }
        });
    });

    /* ---------- Mouse Glow ---------- */
    const glow = document.getElementById('mouse-glow');
    if (glow) {
        document.addEventListener('mousemove', function (e) {
            glow.style.left = e.clientX + 'px';
            glow.style.top = e.clientY + 'px';
        });
    }

    /* ---------- Floating Particles ---------- */
    const particlesEl = document.getElementById('particles');
    if (particlesEl) {
        const colors = ['#6c5ce7', '#00cec9', '#fd79a8', '#8b7cf6'];
        for (let i = 0; i < 25; i++) {
            const p = document.createElement('span');
            p.className = 'particle';
            const size = Math.random() * 6 + 2;
            p.style.width = size + 'px';
            p.style.height = size + 'px';
            p.style.left = Math.random() * 100 + '%';
            p.style.top = (Math.random() * 100 + 20) + '%';
            p.style.background = colors[Math.floor(Math.random() * colors.length)];
            p.style.animationDuration = (Math.random() * 15 + 10) + 's';
            p.style.animationDelay = (Math.random() * 10) + 's';
            particlesEl.appendChild(p);
        }
    }

    /* ---------- Sidebar Toggle ---------- */
    const sidebarToggle = document.querySelector('[data-sidebar-toggle]');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function () {
            document.querySelectorAll('.sidebar, .sidebar-overlay').forEach(function (el) {
                el.classList.toggle('show');
            });
            document.querySelector('.sidebar')?.classList.toggle('open');
        });
    }

    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function () {
            sidebarOverlay.classList.remove('show');
            document.querySelector('.sidebar')?.classList.remove('open');
        });
    }

    /* ---------- AOS ---------- */
    if (window.AOS) {
        AOS.init({ duration: 800, once: true, offset: 80 });
    }

    /* ---------- Animated Counters ---------- */
    const counters = document.querySelectorAll('[data-count]');
    counters.forEach(function (counter) {
        const target = parseFloat(counter.getAttribute('data-count'));
        const suffix = counter.getAttribute('data-suffix') || '';
        const duration = 1500;
        const start = performance.now();
        function update(now) {
            const progress = Math.min((now - start) / duration, 1);
            const val = Math.floor(progress * target);
            counter.textContent = val + suffix;
            if (progress < 1) requestAnimationFrame(update);
            else counter.textContent = target + suffix;
        }
        requestAnimationFrame(update);
    });

    /* ---------- Score Gauge ---------- */
    document.querySelectorAll('[data-gauge]').forEach(function (gauge) {
        const score = parseFloat(gauge.getAttribute('data-gauge')) || 0;
        const fill = gauge.querySelector('.gauge-fill');
        const label = gauge.querySelector('.gauge-label');
        if (fill) {
            const circumference = 502;
            const offset = circumference - (score / 100) * circumference;
            fill.style.strokeDashoffset = offset;
        }
        if (label) label.textContent = Math.round(score) + '%';
    });

    /* ---------- Chart.js Charts ---------- */
    function initCharts() {
        if (typeof Chart === 'undefined') return;

        const defaultColors = ['#6c5ce7', '#00cec9', '#fd79a8', '#fdcb6e', '#00b894', '#e17055'];
        const gridColor = getComputedStyle(document.body).getPropertyValue('--glass-border').trim() || 'rgba(255,255,255,0.1)';
        const textColor = getComputedStyle(document.body).getPropertyValue('--text-muted').trim() || '#9aa0b8';

        /* Pie Chart */
        const pieCtx = document.querySelector('[data-chart="pie"]');
        if (pieCtx) {
            const data = JSON.parse(pieCtx.getAttribute('data-labels') || '[]');
            const values = JSON.parse(pieCtx.getAttribute('data-values') || '[]');
            new Chart(pieCtx, {
                type: 'doughnut',
                data: {
                    labels: data,
                    datasets: [{
                        data: values,
                        backgroundColor: defaultColors,
                        borderWidth: 0
                    }]
                },
                options: chartBaseOptions(textColor, true)
            });
        }

        /* Bar Chart */
        const barCtx = document.querySelector('[data-chart="bar"]');
        if (barCtx) {
            const data = JSON.parse(barCtx.getAttribute('data-labels') || '[]');
            const values = JSON.parse(barCtx.getAttribute('data-values') || '[]');
            new Chart(barCtx, {
                type: 'bar',
                data: {
                    labels: data,
                    datasets: [{
                        label: barCtx.getAttribute('data-label') || 'Score',
                        data: values,
                        backgroundColor: defaultColors,
                        borderRadius: 8
                    }]
                },
                options: chartBaseOptions(textColor)
            });
        }

        /* Radar Chart */
        const radarCtx = document.querySelector('[data-chart="radar"]');
        if (radarCtx) {
            const data = JSON.parse(radarCtx.getAttribute('data-labels') || '[]');
            const values = JSON.parse(radarCtx.getAttribute('data-values') || '[]');
            new Chart(radarCtx, {
                type: 'radar',
                data: {
                    labels: data,
                    datasets: [{
                        label: radarCtx.getAttribute('data-label') || 'Scores',
                        data: values,
                        backgroundColor: 'rgba(108, 92, 231, 0.2)',
                        borderColor: '#6c5ce7',
                        pointBackgroundColor: '#00cec9',
                        pointBorderColor: '#fff',
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            beginAtZero: true,
                            max: 100,
                            grid: { color: gridColor },
                            pointLabels: { color: textColor }
                        }
                    }
                }
            });
        }

        /* Line Chart */
        const lineCtx = document.querySelector('[data-chart="line"]');
        if (lineCtx) {
            const data = JSON.parse(lineCtx.getAttribute('data-labels') || '[]');
            const values = JSON.parse(lineCtx.getAttribute('data-values') || '[]');
            new Chart(lineCtx, {
                type: 'line',
                data: {
                    labels: data,
                    datasets: [{
                        label: lineCtx.getAttribute('data-label') || 'Score Trend',
                        data: values,
                        borderColor: '#6c5ce7',
                        backgroundColor: 'rgba(108, 92, 231, 0.15)',
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#00cec9'
                    }]
                },
                options: chartBaseOptions(textColor)
            });
        }
    }

    function chartBaseOptions(textColor, legend) {
        const gridColor = getComputedStyle(document.body).getPropertyValue('--glass-border').trim() || 'rgba(255,255,255,0.1)';
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: !!legend,
                    labels: { color: textColor }
                }
            },
            scales: {
                x: { grid: { color: gridColor }, ticks: { color: textColor } },
                y: { grid: { color: gridColor }, ticks: { color: textColor }, beginAtZero: true }
            }
        };
    }
    initCharts();

    /* ---------- Drag & Drop Upload ---------- */
    const dropzone = document.querySelector('[data-dropzone]');
    const fileInput = document.querySelector('[data-file-input]');
    if (dropzone && fileInput) {
        ['dragenter', 'dragover'].forEach(function (evt) {
            dropzone.addEventListener(evt, function (e) {
                e.preventDefault();
                dropzone.classList.add('dragover');
            });
        });
        ['dragleave', 'drop'].forEach(function (evt) {
            dropzone.addEventListener(evt, function (e) {
                e.preventDefault();
                dropzone.classList.remove('dragover');
            });
        });
        dropzone.addEventListener('drop', function (e) {
            const files = e.dataTransfer.files;
            if (files.length) fileInput.files = files;
        });
        dropzone.addEventListener('click', function () { fileInput.click(); });

        fileInput.addEventListener('change', function () {
            if (fileInput.files.length) {
                const file = fileInput.files[0];
                const nameEl = document.querySelector('[data-file-name]');
                const sizeEl = document.querySelector('[data-file-size]');
                if (nameEl) nameEl.textContent = file.name;
                if (sizeEl) sizeEl.textContent = formatBytes(file.size);
                const progress = document.querySelector('[data-upload-progress]');
                if (progress) {
                    let p = 0;
                    const timer = setInterval(function () {
                        p = Math.min(p + Math.random() * 20, 100);
                        progress.style.width = p + '%';
                        if (p >= 100) clearInterval(timer);
                    }, 120);
                }
            }
        });
    }

    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /* ---------- Career Assistant Chat ---------- */
    const chatForm = document.querySelector('[data-chat-form]');
    if (chatForm) {
        chatForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const input = chatForm.querySelector('input[name="query"]');
            const box = document.querySelector('[data-chat-box]');
            const query = input.value.trim();
            if (!query) return;

            // Add user message
            addChatMessage(box, query, 'user');
            input.value = '';

            // Loading indicator
            const loader = document.createElement('div');
            loader.className = 'chat-msg ai-msg';
            loader.innerHTML = '<div class="chat-bubble"><i class="fas fa-spinner fa-spin"></i> Analyzing...</div>';
            box.appendChild(loader);
            box.scrollTop = box.scrollHeight;

// Fetch response
            fetch(chatForm.getAttribute('action'), {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrf(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new URLSearchParams(new FormData(chatForm))
            })
            .then(function (r) { return r.json(); })
            .then(function (data) {
                loader.querySelector('.chat-bubble').innerHTML = data.response || 'No response.';
                box.scrollTop = box.scrollHeight;
            })
            .catch(function () {
                loader.querySelector('.chat-bubble').innerHTML = 'An error occurred. Please try again.';
            });
        });
    }

    function addChatMessage(box, text, type) {
        const msg = document.createElement('div');
        msg.className = 'chat-msg ' + (type === 'user' ? 'user-msg' : 'ai-msg');
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble';
        bubble.textContent = text;
        msg.appendChild(bubble);
        box.appendChild(msg);
        box.scrollTop = box.scrollHeight;
    }

    /* ---------- Suggestion Chips (career) ---------- */
    const chips = document.querySelectorAll('[data-suggestion]');
    chips.forEach(function (chip) {
        chip.addEventListener('click', function () {
            const input = document.querySelector('input[name="query"]');
            if (input) input.value = chip.getAttribute('data-suggestion');
        });
    });

    /* ---------- Live Resume Editor Preview ---------- */
    const editorInput = document.querySelector('[data-editor-input]');
    const previewOutput = document.querySelector('[data-preview-output]');
    if (editorInput && previewOutput) {
        editorInput.addEventListener('input', function () {
            previewOutput.textContent = editorInput.value;
        });
    }

    /* ---------- Auto Save (Editor) ---------- */
    const autoSaveForm = document.querySelector('[data-autosave]');
    if (autoSaveForm) {
        let timer;
        autoSaveForm.addEventListener('input', function () {
            clearTimeout(timer);
            const status = document.querySelector('[data-save-status]');
            if (status) status.textContent = 'Unsaved changes...';
            timer = setTimeout(function () {
                const data = new FormData(autoSaveForm);
                fetch(autoSaveForm.getAttribute('action'), {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCsrf() },
                    body: data
                }).then(function () {
                    if (status) status.textContent = 'Saved ✓';
                }).catch(function () {
                    if (status) status.textContent = 'Save failed';
                });
            }, 800);
        });
    }

    /* ---------- Chart.js color on theme change ---------- */
    const observer = new MutationObserver(function () {
        initCharts();
    });
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] });

    /* ---------- Chat welcome quick history ---------- */
    const historyItems = document.querySelectorAll('[data-history-query]');
    historyItems.forEach(function (item) {
        item.addEventListener('click', function () {
            const input = document.querySelector('input[name="query"]');
            if (input) input.value = item.getAttribute('data-history-query');
        });
    });

    /* ---------- Print Report ---------- */
    const printBtn = document.querySelector('[data-print]');
    if (printBtn) {
        printBtn.addEventListener('click', function () { window.print(); });
    }
});

/* ---------- CSRF Helper ---------- */
function getCsrf() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}
