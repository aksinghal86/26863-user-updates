document.addEventListener('DOMContentLoaded', function () {
    const afForm = document.getElementById('af-update-form');
    if (!afForm) return;

    function showError(fieldName, message) {
        const field = document.getElementsByName(fieldName)[0];
        if (field) {
            const group = field.closest('.pfas-form-group');
            if (group) {
                const errorDiv = group.querySelector('.field-error');
                if (errorDiv) {
                    errorDiv.textContent = message;
                    errorDiv.style.display = 'block';
                }
            }
        }
    }

    function clearErrors() {
        const errors = document.querySelectorAll('.field-error');
        errors.forEach(err => {
            err.textContent = '';
            err.style.display = 'none';
        });
        const generalError = document.getElementById('pfas-general-error');
        if (generalError) generalError.style.display = 'none';
    }

    afForm.addEventListener('submit', function (event) {
        clearErrors();
        let hasErrors = false;

        // 1. Required fields check
        const requiredFields = afForm.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value || (field.type === 'file' && field.files.length === 0)) {
                if (field.type === 'file') {
                    showError(field.name, "A file must be uploaded.");
                } else {
                    showError(field.name, "This field is required.");
                }
                hasErrors = true;
            }
        });

        // 2. Flow rate validation
        const flowRateInput = document.getElementsByName('flow_rate')[0];
        if (flowRateInput && flowRateInput.value) {
            const val = parseFloat(flowRateInput.value);
            if (val < 0) {
                showError('flow_rate', "Flow rate cannot be negative.");
                hasErrors = true;
            }
        }

        if (hasErrors) {
            event.preventDefault();
            const generalError = document.getElementById('pfas-general-error');
            if (generalError) generalError.style.display = 'block';
            
            // Scroll to the first error
            const firstError = document.querySelector('.field-error[style*="display: block"]');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });
});
