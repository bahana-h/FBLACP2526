// Chrysalis Connect - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Help modal
    const helpModal = document.getElementById('helpModal');
    const helpTrigger = document.getElementById('helpTrigger');
    const helpClose = document.getElementById('helpClose');
    const helpBackdrop = document.getElementById('helpBackdrop');

    function openHelp() {
        if (helpModal) {
            helpModal.classList.add('is-open');
            helpModal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeHelp() {
        if (helpModal) {
            helpModal.classList.remove('is-open');
            helpModal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        }
    }

    if (helpTrigger) helpTrigger.addEventListener('click', openHelp);
    if (helpClose) helpClose.addEventListener('click', closeHelp);
    if (helpBackdrop) helpBackdrop.addEventListener('click', closeHelp);

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && helpModal && helpModal.classList.contains('is-open')) {
            closeHelp();
        }
    });

    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(function(flash) {
        setTimeout(function() {
            flash.style.transition = 'opacity 0.5s';
            flash.style.opacity = '0';
            setTimeout(function() {
                flash.remove();
            }, 500);
        }, 5000);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#ef4444';
                } else {
                    field.style.borderColor = '';
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
});

