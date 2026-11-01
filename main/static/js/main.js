/**
 * Crickethub - Client-side Interactive JavaScript
 * File: static/js/main.js
 * Description:
 *   Handles modal dialogues, pre-populating edit forms, alert auto-dismiss,
 *   confirmation prompts for deletions, and keyboard accessibility.
 */

document.addEventListener('DOMContentLoaded', () => {
    // -----------------------------------------------------------------
    // 1. MODAL DIALOG CONTROLS
    // -----------------------------------------------------------------
    window.openModal = function (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            // Focus on first input
            const firstInput = modal.querySelector('input, select, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        }
    };

    window.closeModal = function (modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('active');
            document.body.style.overflow = '';
        }
    };

    // Close modal on Escape key press
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach((modal) => {
                modal.classList.remove('active');
            });
            document.body.style.overflow = '';
        }
    });

    // Close modal when clicking outside box
    document.querySelectorAll('.modal-overlay').forEach((overlay) => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });

    // -----------------------------------------------------------------
    // 2. ALERT AUTO-DISMISS & CLOSE BUTTONS
    // -----------------------------------------------------------------
    document.querySelectorAll('.alert').forEach((alert) => {
        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 200);
            });
        }
        // Auto-dismiss success notifications after 5 seconds
        if (alert.classList.contains('alert-success')) {
            setTimeout(() => {
                alert.style.transition = 'opacity 0.4s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 400);
            }, 5000);
        }
    });

    // -----------------------------------------------------------------
    // 3. EDIT FORM PRE-POPULATION HELPER
    // -----------------------------------------------------------------
    window.populateEditModal = function (modalId, data) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        Object.keys(data).forEach((key) => {
            const field = modal.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = data[key] !== null && data[key] !== undefined ? data[key] : '';
            }
        });

        openModal(modalId);
    };

    // -----------------------------------------------------------------
    // 4. CONFIRMATION PROMPTS
    // -----------------------------------------------------------------
    document.querySelectorAll('form[data-confirm]').forEach((form) => {
        form.addEventListener('submit', (e) => {
            const promptMsg = form.getAttribute('data-confirm') || 'Are you sure you want to perform this action?';
            if (!confirm(promptMsg)) {
                e.preventDefault();
            }
        });
    });
});
