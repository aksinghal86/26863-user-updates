
document.addEventListener('DOMContentLoaded', function () {
    const pfasForm = document.getElementById('pfas-update-form');
    if (!pfasForm) return;

    // These values should be provided by the HTML via global variables or data attributes
    const analyte = window.pfasData?.analyte || 'PFOA';
    const minVal = parseFloat(window.pfasData?.minValue || '0');
    const selectedAnalyte = window.pfasData?.selectedAnalyte || '';
    const savedValue = window.pfasData?.savedValue || '';

    const analyteText = document.getElementById('pfas-analyte-text');
    const analyteSelect = document.getElementById('pfas-analyte-select');

    // Handle "Other" lab selection
    const labSelect = document.getElementById('lab');
    const otherLabContainer = document.getElementById('other_lab_container');
    const otherLabInput = document.getElementById('other_lab');

    function toggleOtherLab() {
        if (labSelect.value === 'Other') {
            otherLabContainer.style.display = 'block';
            otherLabInput.setAttribute('required', 'required');
        } else {
            otherLabContainer.style.display = 'none';
            otherLabInput.removeAttribute('required');
        }
    }

    if (labSelect) {
        labSelect.addEventListener('change', toggleOtherLab);
        toggleOtherLab(); // Initial state
    }

    // Handle "Other" analysis method selection
    const analysisMethodSelect = document.getElementById('analysis_method');
    const otherAnalysisMethodContainer = document.getElementById('other_analysis_method_container');
    const otherAnalysisMethodInput = document.getElementById('other_analysis_method');

    function toggleOtherAnalysisMethod() {
        if (analysisMethodSelect.value === 'Other') {
            otherAnalysisMethodContainer.style.display = 'block';
            otherAnalysisMethodInput.setAttribute('required', 'required');
        } else {
            otherAnalysisMethodContainer.style.display = 'none';
            otherAnalysisMethodInput.removeAttribute('required');
        }
    }

    if (analysisMethodSelect) {
        analysisMethodSelect.addEventListener('change', toggleOtherAnalysisMethod);
        toggleOtherAnalysisMethod(); // Initial state
    }

    if (analyte === 'Other PFAS') {
        if (analyteText) {
            analyteText.style.display = 'none';
            analyteText.disabled = true;
        }
        if (analyteSelect) {
            analyteSelect.style.display = '';
            analyteSelect.disabled = false;
            
            if (savedValue && savedValue !== 'PFOA' && savedValue !== 'PFOS') {
                analyteSelect.value = savedValue;
            } else if (selectedAnalyte && selectedAnalyte !== 'None') {
                analyteSelect.value = selectedAnalyte;
            } else {
                analyteSelect.value = "";
            }
        }
    } else {
        if (analyteText) {
            analyteText.value = analyte;
            analyteText.style.display = '';
            analyteText.disabled = false;
        }
        if (analyteSelect) {
            analyteSelect.style.display = 'none';
            analyteSelect.disabled = true;
        }
    }

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

    pfasForm.addEventListener('submit', function (event) {
        clearErrors();
        let hasErrors = false;

        // 1. Required fields check
        const requiredFields = pfasForm.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (field.name === 'analyte') return; // Skip analyte field as per requirement
            if (!field.value || (field.type === 'file' && field.files.length === 0)) {
                if (field.type === 'file') {
                    showError(field.name, "A file must be uploaded");
                } else {
                    showError(field.name, "This field is required.");
                }
                hasErrors = true;
            }
        });

        // 2. Result PPT validation
        const resultInput = document.getElementById('result_ppt');
        if (resultInput && resultInput.value) {
            const val = parseFloat(resultInput.value);
            if (val < 0) {
                showError('result_ppt', "Result cannot be negative.");
                hasErrors = true;
            } else if (!isNaN(minVal) && val <= minVal) {
                showError('result_ppt', `New result must be greater than the current value of ${minVal} ng/L.`);
                hasErrors = true;
            }
        }

        // 3. Date validation
        const samplingDateInput = document.getElementById('sampling_date');
        const analysisDateInput = document.getElementById('analysis_date');
        if (samplingDateInput && analysisDateInput && samplingDateInput.value && analysisDateInput.value) {
            const sDate = new Date(samplingDateInput.value);
            const aDate = new Date(analysisDateInput.value);
            if (aDate < sDate) {
                showError('analysis_date', "Analysis date cannot be before sampling date.");
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
        } else {
            event.preventDefault(); // Prevent immediate submission to show loader
            const loaderContainer = document.getElementById('loader-container');
            const loader = document.getElementById('loader');
            if (loaderContainer) {
                loaderContainer.style.setProperty('display', 'flex', 'important');
            }
            if (loader) {
                loader.style.setProperty('display', 'block', 'important');
            }
            // Submit the form after a short delay to allow the browser to render the loader
            setTimeout(() => {
                pfasForm.submit();
            }, 100);
        }
    });
});
