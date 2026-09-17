
document.addEventListener('DOMContentLoaded', function () {
    const hiForm = document.getElementById('hi-update-form');
    if (!hiForm) return;

    const minHiInput = document.getElementById('min_hi_input');
    const minHi = minHiInput ? parseFloat(minHiInput.value || '0') : 0;

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

    function showError(fieldName, message) {
        const field = document.getElementsByName(fieldName)[0];
        if (field) {
            const group = field.closest('.pfas-form-group');
            if (group) {
                let errorDiv = group.querySelector('.field-error');
                if (!errorDiv) {
                    errorDiv = document.createElement('div');
                    errorDiv.className = 'pfas-error-message field-error';
                    errorDiv.style.color = 'red';
                    group.appendChild(errorDiv);
                }
                errorDiv.textContent = message;
                errorDiv.style.display = 'block';
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

    function calculateHI(pfhxs, hfpoda, pfna, pfbs) {
        // HI = [PFHxS]/9 + [HFPO-DA]/10 + [PFNA]/10 + [PFBS]/2000
        return (pfhxs / 9) + (hfpoda / 10) + (pfna / 10) + (pfbs / 2000);
    }

    hiForm.addEventListener('submit', function (event) {
        clearErrors();
        let hasErrors = false;

        // 1. Required fields check
        const requiredFields = hiForm.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value || (field.type === 'file' && field.files.length === 0)) {
                if (field.type === 'file') {
                    showError(field.name, "A file must be uploaded");
                } else {
                    showError(field.name, "This field is required.");
                }
                hasErrors = true;
            }
        });

        // 2. Analyte results validation (non-negative and HI calculation)
        const pfhxsVal = parseFloat(document.getElementById('pfhxs_result').value);
        const hfpodaVal = parseFloat(document.getElementById('hfpo_da_result').value);
        const pfnaVal = parseFloat(document.getElementById('pfna_result').value);
        const pfbsVal = parseFloat(document.getElementById('pfbs_result').value);

        const analytes = [
            { id: 'pfhxs_result', name: 'pfhxs_result', val: pfhxsVal, label: 'PFHxS' },
            { id: 'hfpo_da_result', name: 'hfpo_da_result', val: hfpodaVal, label: 'HFPO-DA' },
            { id: 'pfna_result', name: 'pfna_result', val: pfnaVal, label: 'PFNA' },
            { id: 'pfbs_result', name: 'pfbs_result', val: pfbsVal, label: 'PFBS' }
        ];

        analytes.forEach(a => {
            if (!isNaN(a.val) && a.val < 0) {
                showError(a.name, `${a.label} result cannot be negative.`);
                hasErrors = true;
            }
        });

        if (!hasErrors && !analytes.some(a => isNaN(a.val))) {
            const calculatedHI = calculateHI(pfhxsVal, hfpodaVal, pfnaVal, pfbsVal);
            const roundedHI = Math.round((calculatedHI + Number.EPSILON) * 100) / 100;
            
            // Log for debugging
            console.log("Calculated HI:", calculatedHI, "Rounded HI:", roundedHI, "Min HI:", minHi);

            if (roundedHI <= minHi) {
                const generalError = document.getElementById('pfas-general-error');
                if (generalError) {
                    generalError.textContent = `The calculated Hazard Index (${roundedHI.toFixed(2)}) must be greater than the current maximum (${minHi.toFixed(2)}).`;
                    generalError.style.display = 'block';
                }
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
            if (generalError && (generalError.style.display === 'none' || !generalError.textContent || generalError.textContent === "Submission failure: please correct all validation errors.")) {
                generalError.textContent = "Submission failure: please correct all validation errors.";
                generalError.style.display = 'block';
            }
            
            // Scroll to the first error
            const firstError = document.querySelector('.field-error[style*="display: block"]');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        } else {
            event.preventDefault();
            const loaderContainer = document.getElementById('loader-container');
            if (loaderContainer) {
                loaderContainer.style.setProperty('display', 'flex', 'important');
            }
            
            setTimeout(() => {
                hiForm.submit();
            }, 100);
        }
    });
});
