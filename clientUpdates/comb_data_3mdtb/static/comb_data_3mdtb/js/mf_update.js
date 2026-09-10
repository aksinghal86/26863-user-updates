document.addEventListener('DOMContentLoaded', function () {
    const mfForm = document.getElementById('mf-update-form');
    if (!mfForm) return;

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

    mfForm.addEventListener('submit', function (event) {
        clearErrors();
        let hasErrors = false;

        // 1. Required fields check
        const requiredFields = mfForm.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            const val = field.value.trim();
            if (!val || (field.type === 'file' && field.files.length === 0)) {
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
    const unitInput = document.getElementsByName('unit')[0];
    const existingMaxFlowGpmInput = document.getElementById('existing-max-flow-gpm');
    
    if (flowRateInput && flowRateInput.value && unitInput && unitInput.value) {
        const val = parseFloat(flowRateInput.value);
        if (val < 0) {
            showError('flow_rate', "Flow rate cannot be negative.");
            hasErrors = true;
        } else if (existingMaxFlowGpmInput && existingMaxFlowGpmInput.value) {
            const existingGpm = parseFloat(existingMaxFlowGpmInput.value);
            const unit = unitInput.value.toLowerCase();
            let newGpm = 0;
            
            if (unit === 'gpm') {
                newGpm = val;
            } else if (unit === 'mgd') {
                newGpm = val * 1000000 / 1440;
            } else if (unit === 'gpy') {
                newGpm = val / (365 * 1440);
            } else if (unit === 'mgy') {
                newGpm = val * 1000000 / (365 * 1440);
            } else if (unit === 'afpy') {
                newGpm = val * 325851 / (365 * 1440);
            }
            
            if (newGpm <= existingGpm) {
                showError('flow_rate', `New flow rate must be greater than the current value of ${existingGpm.toFixed(1)} GPM.`);
                hasErrors = true;
            }
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
