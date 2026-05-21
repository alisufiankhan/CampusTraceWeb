document.addEventListener("DOMContentLoaded", function() {
    // Auto dismiss flash messages after 4 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 4000);

    // Confirm dialog before any delete or reject action
    var confirmButtons = document.querySelectorAll('form[action*="delete"], form[action*="reject"]');
    confirmButtons.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to perform this action?')) {
                e.preventDefault();
            }
        });
    });

    // Active nav link highlighting
    var currentUrl = window.location.pathname;
    var navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentUrl) {
            link.classList.add('active');
        }
    });
});
