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

        // 0. Existing flow validation
        const existingFlowGpm = parseFloat(window.afData?.existingFlowGpm || '');
        const flowRateInput = document.getElementsByName('flow_rate')[0];
        const unitSelect = document.getElementsByName('unit')[0];
        
        if (flowRateInput && unitSelect && !isNaN(existingFlowGpm)) {
            const flowRate = parseFloat(flowRateInput.value);
            const unit = unitSelect.value;
            
            if (!isNaN(flowRate) && unit) {
                let newFlowGpm = 0;
                const unitLower = unit.toLowerCase();
                
                if (unitLower === 'gpm') {
                    newFlowGpm = flowRate;
                } else if (unitLower === 'gpy') {
                    newFlowGpm = flowRate / (365 * 1440);
                } else if (unitLower === 'mgd') {
                    newFlowGpm = flowRate * 1e6 / 1440;
                } else if (unitLower === 'mgy') {
                    newFlowGpm = flowRate * 1e6 / (365 * 1440);
                } else if (unitLower === 'afpy') {
                    newFlowGpm = flowRate * 325851 / (365 * 1440);
                }
                
                if (newFlowGpm < (existingFlowGpm - 0.00001)) { // Small epsilon for floating point comparison
                    showError('flow_rate', `New flow rate must be greater than or equal to the current value of ${existingFlowGpm.toFixed(1)} GPM.`);
                    hasErrors = true;
                }
            }
        }

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
