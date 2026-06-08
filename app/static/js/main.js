document.addEventListener("DOMContentLoaded", function() {
    // 8. Smooth page transitions
    document.body.classList.add('fade-in-up');
    
    // 1. Auto dismiss alerts after 4 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });

    // 2. Category form toggle (items page)
    const categorySelect = document.getElementById("category");
    if (categorySelect) {
        const typeDivs = {
            electronic: document.getElementById("electronic_div"),
            document: document.getElementById("document_div"),
            personal: document.getElementById("personal_div")
        };
        
        // Hide all initially
        Object.values(typeDivs).forEach(div => {
            if(div) {
                div.style.display = 'none';
                div.style.opacity = '0';
                div.style.transition = 'all 0.3s ease';
            }
        });

        categorySelect.addEventListener("change", function() {
            Object.values(typeDivs).forEach(div => {
                if(div) {
                    div.style.display = 'none';
                    div.style.opacity = '0';
                }
            });
            
            const selected = typeDivs[this.value];
            if (selected) {
                selected.style.display = 'flex';
                // slight delay for transition
                setTimeout(() => {
                    selected.style.opacity = '1';
                }, 10);
            }
        });
    }

    // 3. Confirm dialogs
    const confirmForms = document.querySelectorAll('form[action*="/approve"], form[action*="/reject"], form[action*="/dispute"], form[action*="/expire"]');
    confirmForms.forEach(form => {
        // Skip if form button already has an inline confirm
        if (form.querySelector('button[onclick*="confirm"]')) return;
        
        form.addEventListener('submit', function(e) {
            let msg = 'Are you sure you want to proceed?';
            if (form.action.includes('/approve')) msg = 'Approve this claim?';
            if (form.action.includes('/reject')) msg = 'Reject this claim?';
            if (form.action.includes('/dispute')) msg = 'Mark this claim as disputed?';
            if (form.action.includes('/expire')) msg = 'Mark this item as expired?';
            
            if (!confirm(msg)) {
                e.preventDefault();
            }
        });
    });

    // 4. Active nav link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath && currentPath !== '#') {
            link.classList.add('active');
        }
    });

    // 5. Claim modal data
    const claimModal = document.getElementById('claimModal');
    if (claimModal) {
        claimModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const itemId = button.getAttribute('data-item-id');
            const itemDesc = button.getAttribute('data-item-desc');
            const itemType = button.getAttribute('data-item-type');
            
            document.getElementById('modalItemId').value = itemId;
            document.getElementById('modalItemDesc').textContent = itemDesc;
            
            // Set character counter if exists
            const proofTextarea = document.getElementById('proof');
            const charCount = document.getElementById('charCount');
            if (proofTextarea && charCount) {
                proofTextarea.addEventListener('input', function() {
                    charCount.textContent = this.value.length;
                });
            }
        });
    }

    // 6. Search input enhancement
    const searchInput = document.querySelector('input[name="keyword"]');
    if (searchInput) {
        const searchForm = searchInput.closest('form');
        
        // Setup clear button
        const inputGroup = searchInput.closest('.input-group');
        if (inputGroup) {
            const clearBtn = document.createElement('button');
            clearBtn.type = 'button';
            clearBtn.className = 'btn btn-outline-secondary border-start-0 border-top-1 border-bottom-1';
            clearBtn.style.borderTop = '1.5px solid var(--border)';
            clearBtn.style.borderBottom = '1.5px solid var(--border)';
            clearBtn.style.background = 'white';
            clearBtn.innerHTML = '<i class="fas fa-times"></i>';
            clearBtn.style.display = searchInput.value ? 'block' : 'none';
            
            // Insert before the search button
            inputGroup.insertBefore(clearBtn, searchInput.nextSibling);
            
            searchInput.addEventListener('input', function() {
                clearBtn.style.display = this.value ? 'block' : 'none';
            });
            
            clearBtn.addEventListener('click', function() {
                searchInput.value = '';
                this.style.display = 'none';
                searchInput.focus();
                // Optionally submit form to clear search
                if (searchForm) searchForm.submit();
            });
        }
        
        // Escape to clear
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                this.value = '';
                if (searchForm) searchForm.submit();
            }
        });
    }

    // 7. Table row click
    const rows = document.querySelectorAll('.table tbody tr');
    rows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Don't trigger if clicking a button or form
            if (e.target.tagName === 'BUTTON' || e.target.closest('button') || e.target.tagName === 'A') {
                return;
            }
            const link = this.querySelector('a.btn');
            if (link) {
                window.location.href = link.href;
            }
        });
    });

    // 9. Stat card counter animation
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(stat => {
        const target = parseInt(stat.textContent.trim(), 10);
        if (!isNaN(target)) {
            let start = 0;
            const duration = 1000;
            const interval = 20;
            const step = Math.max(1, Math.floor(target / (duration / interval)));
            
            const timer = setInterval(() => {
                start += step;
                if (start >= target) {
                    stat.textContent = target;
                    clearInterval(timer);
                } else {
                    stat.textContent = start;
                }
            }, interval);
        }
    });
    
    // Handover receipt preview update
    const witnessInput = document.querySelector('input[name="witness"]');
    const conditionInput = document.querySelector('input[name="condition"]');
    const receiptWitness = document.getElementById('receipt-witness');
    const receiptCondition = document.getElementById('receipt-condition');
    
    if (witnessInput && receiptWitness) {
        witnessInput.addEventListener('input', function() {
            receiptWitness.textContent = this.value || '[Witness Name]';
        });
    }
    if (conditionInput && receiptCondition) {
        conditionInput.addEventListener('input', function() {
            receiptCondition.textContent = this.value || '[Item Condition]';
        });
    }
});
