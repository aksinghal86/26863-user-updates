document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('add-source-form');
    if (!form) return;

    const sourceName = form.querySelector('[name="source_name"]');
    const sourceType = form.querySelector('[name="source_type"]');
    const sourceOther = form.querySelector('[name="source_other"]');
    const sourceOtherRow = document.getElementById('source-other-row');
    const pfasTested = form.querySelector('[name="pfas_tested"]');
    const pfasDetected = form.querySelector('[name="pfas_detected"]');
    const pfasFile1 = form.querySelector('[name="pfas_file_1"]');
    const pfasFile2 = form.querySelector('[name="pfas_file_2"]');
    const pfasFile3 = form.querySelector('[name="pfas_file_3"]');
    
    const pwsOwnSource = form.querySelector('[name="pws_own_source"]');
    const pwsOwnSourceExplanation = form.querySelector('[name="pws_own_source_explanation"]');
    const pwsOwnSourceExplanationRow = document.getElementById('pws-own-source-explanation-row');
    
    const pwsOperateSource = form.querySelector('[name="pws_operate_source"]');
    const pwsOperateSourceExplanation = form.querySelector('[name="pws_operate_source_explanation"]');
    const pwsOperateSourceExplanationRow = document.getElementById('pws-operate-source-explanation-row');
    
    const coOwners = form.querySelector('[name="co_owners"]');
    const coOwnersExplanation = form.querySelector('[name="co_owners_explanation"]');
    const coOwnersExplanationRow = document.getElementById('co-owners-explanation-row');
    
    const purchasedWater = form.querySelector('[name="purchased_water"]');
    const purchasedWaterExplanation = form.querySelector('[name="purchased_water_explanation"]');
    const purchasedWaterExplanationRow = document.getElementById('purchased-water-explanation-row');
    
    const pfasWarningBlurb = document.getElementById('pfas-warning-blurb');
    
    // Add validation error display function
    const showError = (input, message) => {
        const group = input.closest('.pfas-form-group');
        let error = group.querySelector('.text-danger.small');
        if (!error) {
            error = document.createElement('div');
            error.className = 'text-danger small js-error';
            group.appendChild(error);
        }
        error.textContent = message;
        input.classList.add('is-invalid');
    };

    const clearError = (input) => {
        const group = input.closest('.pfas-form-group');
        const error = group.querySelector('.text-danger.small.js-error');
        if (error) {
            error.textContent = '';
        }
        input.classList.remove('is-invalid');
    };

    form.addEventListener('submit', function(event) {
        let isValid = true;
        const generalError = document.getElementById('pfas-general-error');

        // Clear previous JS errors
        form.querySelectorAll('.js-error').forEach(e => e.textContent = '');
        form.querySelectorAll('.is-invalid').forEach(i => i.classList.remove('is-invalid'));
        if (generalError) generalError.style.display = 'none';

        // Validate Source Name
        if (sourceName.value.trim().length < 3) {
            showError(sourceName, 'Source name must be at least 3 characters long.');
            isValid = false;
        }

        // Validate Source Other if Source Type is "Other"
        if (sourceType.value === 'Other' && !sourceOther.value.trim()) {
            showError(sourceOther, 'Please provide explanation for Other source type.');
            isValid = false;
        }

        // Validate PFAS Tested/Detected logic
        if (pfasTested.value === 'No' && pfasDetected.value === 'Yes') {
            showError(pfasDetected, 'PFAS cannot be detected if it was not tested.');
            isValid = false;
        }

        // Validate PWS Own Source Explanation
        if (pwsOwnSource.value === 'No' && !pwsOwnSourceExplanation.value.trim()) {
            showError(pwsOwnSourceExplanation, 'Please provide explanation for not owning the source.');
            isValid = false;
        }

        // Validate PWS Operate Source Explanation
        if (pwsOperateSource.value === 'No' && !pwsOperateSourceExplanation.value.trim()) {
            showError(pwsOperateSourceExplanation, 'Who operates this source? (PWSID and PWS Name)');
            isValid = false;
        }

        // Validate Co-Owners Explanation
        if (coOwners.value === 'Yes' && !coOwnersExplanation.value.trim()) {
            showError(coOwnersExplanation, 'Please provide explanation for co-owners.');
            isValid = false;
        }

        // Validate Purchased Water Explanation
        if (purchasedWater.value === 'Yes' && !purchasedWaterExplanation.value.trim()) {
            showError(purchasedWaterExplanation, 'Please provide explanation for purchased water.');
            isValid = false;
        }

        // Validate at least one file is uploaded if PFAS tested is Yes
        if (pfasTested.value === 'Yes' && !pfasFile1.value && !pfasFile2.value && !pfasFile3.value) {
            showError(pfasFile1, 'At least one PFAS data file must be uploaded.');
            isValid = false;
        }

        // Required fields check (most are required by Django, but good to have here too)
        const requiredFields = form.querySelectorAll('select[required], input[required]');
        requiredFields.forEach(field => {
            if (!field.value) {
                showError(field, 'This field is required.');
                isValid = false;
            }
        });

        if (!isValid) {
            event.preventDefault();
            if (generalError) generalError.style.display = 'block';
            // Scroll to the first error
            const firstError = form.querySelector('.is-invalid');
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
                form.submit();
            }, 100);
        }
    });

    if (sourceType && sourceOtherRow) {
        const toggleSourceOther = (value) => {
            if (value === 'Other') {
                sourceOtherRow.style.display = 'flex';
            } else {
                sourceOtherRow.style.display = 'none';
                if (sourceOther) {
                    sourceOther.value = '';
                    clearError(sourceOther);
                }
            }
        };

        sourceType.addEventListener('change', function() {
            toggleSourceOther(this.value);
        });

        // Initial check
        toggleSourceOther(sourceType.value);

        // Some plugins might trigger jQuery change event
        if (typeof jQuery !== 'undefined') {
            jQuery(sourceType).on('change', function() {
                toggleSourceOther(this.value);
            });
        }
    }

    if (pfasTested && pfasFile1 && pfasFile2 && pfasFile3) {
        const pfasFileUploadRow = pfasFile1.closest('.pfas-form-row');
        const togglePfasFiles = (value) => {
            if (value === 'Yes') {
                if (pfasFileUploadRow) pfasFileUploadRow.style.display = 'block';
                if (pfasWarningBlurb) pfasWarningBlurb.style.display = 'block';
            } else {
                if (pfasFileUploadRow) pfasFileUploadRow.style.display = 'none';
                if (pfasWarningBlurb) pfasWarningBlurb.style.display = 'none';
                pfasFile1.value = '';
                pfasFile2.value = '';
                pfasFile3.value = '';
                clearError(pfasFile1);
            }
        };

        pfasTested.addEventListener('change', function() {
            togglePfasFiles(this.value);
            if (this.value === 'No' && pfasDetected.value === 'Yes') {
                showError(pfasDetected, 'PFAS cannot be detected if it was not tested.');
            } else {
                clearError(pfasDetected);
            }
        });

        // Initial check
        togglePfasFiles(pfasTested.value);
    } else if (pfasTested) {
        pfasTested.addEventListener('change', function() {
            if (this.value === 'No' && pfasDetected.value === 'Yes') {
                showError(pfasDetected, 'PFAS cannot be detected if it was not tested.');
            } else {
                clearError(pfasDetected);
            }
        });
    }

    if (pfasDetected && pfasTested) {
        pfasDetected.addEventListener('change', function() {
            if (pfasTested.value === 'No' && this.value === 'Yes') {
                showError(this, 'PFAS cannot be detected if it was not tested.');
            } else {
                clearError(this);
            }
        });
    }

    if (pwsOwnSource && pwsOwnSourceExplanationRow) {
        const togglePwsOwnSourceExplanation = (value) => {
            if (value === 'No') {
                pwsOwnSourceExplanationRow.style.display = 'flex';
            } else {
                pwsOwnSourceExplanationRow.style.display = 'none';
                if (pwsOwnSourceExplanation) {
                    pwsOwnSourceExplanation.value = '';
                    clearError(pwsOwnSourceExplanation);
                }
            }
        };

        pwsOwnSource.addEventListener('change', function() {
            togglePwsOwnSourceExplanation(this.value);
        });

        togglePwsOwnSourceExplanation(pwsOwnSource.value);
    }

    if (pwsOperateSource && pwsOperateSourceExplanationRow) {
        const togglePwsOperateSourceExplanation = (value) => {
            if (value === 'No') {
                pwsOperateSourceExplanationRow.style.display = 'flex';
            } else {
                pwsOperateSourceExplanationRow.style.display = 'none';
                if (pwsOperateSourceExplanation) {
                    pwsOperateSourceExplanation.value = '';
                    clearError(pwsOperateSourceExplanation);
                }
            }
        };

        pwsOperateSource.addEventListener('change', function() {
            togglePwsOperateSourceExplanation(this.value);
        });

        togglePwsOperateSourceExplanation(pwsOperateSource.value);
    }

    if (coOwners && coOwnersExplanationRow) {
        const toggleCoOwnersExplanation = (value) => {
            if (value === 'Yes') {
                coOwnersExplanationRow.style.display = 'flex';
            } else {
                coOwnersExplanationRow.style.display = 'none';
                if (coOwnersExplanation) {
                    coOwnersExplanation.value = '';
                    clearError(coOwnersExplanation);
                }
            }
        };

        coOwners.addEventListener('change', function() {
            toggleCoOwnersExplanation(this.value);
        });

        toggleCoOwnersExplanation(coOwners.value);
    }

    if (purchasedWater && purchasedWaterExplanationRow) {
        const togglePurchasedWaterExplanation = (value) => {
            if (value === 'Yes') {
                purchasedWaterExplanationRow.style.display = 'flex';
            } else {
                purchasedWaterExplanationRow.style.display = 'none';
                if (purchasedWaterExplanation) {
                    purchasedWaterExplanation.value = '';
                    clearError(purchasedWaterExplanation);
                }
            }
        };

        purchasedWater.addEventListener('change', function() {
            togglePurchasedWaterExplanation(this.value);
        });

        togglePurchasedWaterExplanation(purchasedWater.value);
    }
});
