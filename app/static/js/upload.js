/* ============================================
   ResumeAI Pro - Upload Page JavaScript
   Validates PDF (≤16MB), drag & drop, browse,
   real upload progress, and submits to the
   existing Flask upload endpoint.
   ============================================ */

(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {

        // ---- DOM references (IDs from upload.html) ----
        var form        = document.getElementById('upload-form');
        var dropzone    = document.getElementById('drop-zone');
        var fileInput   = document.getElementById('resume-file');
        var fileNameEl  = document.getElementById('file-name');
        var fileSizeEl  = document.getElementById('file-size');
        var filePagesEl = document.getElementById('file-pages');
        var fileWordsEl = document.getElementById('file-words');
        var filePreview = document.getElementById('file-preview');
        var progressWrap = document.getElementById('upload-progress');
        var progressBar = document.getElementById('progress-bar');
        var submitBtn   = document.getElementById('submit-btn');
        var removeBtn   = document.getElementById('remove-file');

        // Only run on the upload page
        if (!form || !dropzone || !fileInput) return;

        var MAX_SIZE = 16 * 1024 * 1024; // 16 MB

        // ---- Helpers ----
        function formatBytes(bytes) {
            if (bytes === 0) return '0 Bytes';
            var k = 1024;
            var sizes = ['Bytes', 'KB', 'MB', 'GB'];
            var i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }

        function showError(message) {
            // Reuse a Bootstrap alert at the top of the form card.
            var alertBox = document.querySelector('.upload-alert');
            if (!alertBox) {
                alertBox = document.createElement('div');
                alertBox.className = 'alert alert-danger alert-dismissible fade show upload-alert';
                alertBox.innerHTML = '<span class="upload-alert-msg"></span>' +
                    '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
                form.parentNode.insertBefore(alertBox, form);
            }
            alertBox.querySelector('.upload-alert-msg').textContent = message;
            alertBox.classList.remove('d-none');
        }

        function clearError() {
            var alertBox = document.querySelector('.upload-alert');
            if (alertBox) alertBox.classList.add('d-none');
        }

        function resetProgress() {
            if (progressWrap) progressWrap.classList.add('d-none');
            if (progressBar) {
                progressBar.style.width = '0%';
                progressBar.textContent = '0%';
            }
        }

        function setProgress(percent) {
            if (progressWrap) progressWrap.classList.remove('d-none');
            if (progressBar) {
                progressBar.style.width = percent + '%';
                progressBar.textContent = Math.round(percent) + '%';
            }
        }

        function setSubmitEnabled(enabled) {
            if (submitBtn) {
                submitBtn.disabled = !enabled;
                submitBtn.classList.toggle('d-none', !enabled);
            }
        }

        // ---- Validate a selected file ----
        function isPdf(file) {
            return file && (file.type === 'application/pdf' ||
                /\.pdf$/i.test(file.name));
        }

        function handleFile(file) {
            clearError();
            resetProgress();

            if (!file) {
                setSubmitEnabled(false);
                return;
            }

            // Validate type: PDF only
            if (!isPdf(file)) {
                showError('Invalid file type. Please upload a PDF resume.');
                setSubmitEnabled(false);
                return;
            }

            // Validate size: max 16 MB
            if (file.size > MAX_SIZE) {
                showError('File is too large. Maximum allowed size is 16 MB.');
                setSubmitEnabled(false);
                return;
            }

            // Show selected file info
            if (fileNameEl) fileNameEl.textContent = file.name;
            if (fileSizeEl) fileSizeEl.textContent = formatBytes(file.size);
            if (filePagesEl) filePagesEl.textContent = '–';
            if (fileWordsEl) fileWordsEl.textContent = '–';

            if (filePreview) filePreview.classList.remove('d-none');
            setSubmitEnabled(true);
        }

        // ---- Browse via the file input ----
        fileInput.addEventListener('change', function () {
            handleFile(fileInput.files && fileInput.files.length ? fileInput.files[0] : null);
        });

        // ---- Remove / reset selection ----
        if (removeBtn) {
            removeBtn.addEventListener('click', function () {
                fileInput.value = '';
                if (filePreview) filePreview.classList.add('d-none');
                setSubmitEnabled(false);
                resetProgress();
                clearError();
            });
        }

        // ---- Drag & drop on the dropzone ----
        ['dragenter', 'dragover'].forEach(function (evt) {
            dropzone.addEventListener(evt, function (e) {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(function (evt) {
            dropzone.addEventListener(evt, function (e) {
                e.preventDefault();
                e.stopPropagation();
                dropzone.classList.remove('dragover');
            });
        });

        dropzone.addEventListener('drop', function (e) {
            var files = e.dataTransfer && e.dataTransfer.files;
            if (files && files.length) {
                fileInput.files = files; // keep the input in sync for the form
                handleFile(files[0]);
            }
        });

        // Click anywhere on the dropzone opens the file browser,
        // EXCEPT when clicking the existing "Browse Files" label
        // (which naturally forwards to the input) to avoid double dialogs.
        dropzone.addEventListener('click', function (e) {
            if (e.target && e.target.tagName === 'LABEL') return;
            fileInput.click();
        });

        // ---- Submit: AJAX to the existing Flask endpoint ----
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            if (!fileInput.files || !fileInput.files.length) {
                showError('Please select a PDF resume to upload.');
                return;
            }

            var file = fileInput.files[0];

            // Re-validate before sending
            if (!isPdf(file)) {
                showError('Invalid file type. Please upload a PDF resume.');
                return;
            }
            if (file.size > MAX_SIZE) {
                showError('File is too large. Maximum allowed size is 16 MB.');
                return;
            }

            clearError();
            setSubmitEnabled(false);
            if (submitBtn) submitBtn.innerHTML =
                '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';

            var xhr = new XMLHttpRequest();
            var action = form.getAttribute('action') || window.location.href;

            xhr.open('POST', action, true);

            // Upload progress (real bytes)
            xhr.upload.addEventListener('progress', function (evt) {
                if (evt.lengthComputable) {
                    var percent = (evt.loaded / evt.total) * 100;
                    setProgress(percent);
                }
            });

            xhr.onload = function () {
                setProgress(100);
                if (xhr.status >= 200 && xhr.status < 300) {
                    // Follow the existing backend redirect (e.g. analysis view).
                    var redirect = xhr.responseURL;
                    if (redirect && redirect !== window.location.href) {
                        window.location.href = redirect;
                    } else {
                        // No redirect: fall back to normal page navigation.
                        form.submit();
                    }
                } else {
                    // 4xx/5xx: show a clear error and restore the form.
                    setSubmitEnabled(true);
                    if (submitBtn) submitBtn.innerHTML =
                        '<i class="fas fa-robot me-2"></i>Analyze Resume';
                    resetProgress();
                    showError('Upload failed (' + xhr.status + '). Please try again.');
                }
            };

            xhr.onerror = function () {
                setSubmitEnabled(true);
                if (submitBtn) submitBtn.innerHTML =
                    '<i class="fas fa-robot me-2"></i>Analyze Resume';
                resetProgress();
                showError('Network error during upload. Please try again.');
            };

            // FormData includes the hidden csrf_token + resume file automatically.
            xhr.send(new FormData(form));
        });
    });
})();
