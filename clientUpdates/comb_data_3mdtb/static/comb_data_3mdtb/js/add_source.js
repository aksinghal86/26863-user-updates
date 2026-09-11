document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('add-source-form');
    if (!form) return;

    const sourceName = form.querySelector('[name="source_name"]');
    const pfasTested = form.querySelector('[name="pfas_tested"]');
    const pfasDetected = form.querySelector('[name="pfas_detected"]');
    
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

        // Clear previous JS errors
        form.querySelectorAll('.js-error').forEach(e => e.textContent = '');
        form.querySelectorAll('.is-invalid').forEach(i => i.classList.remove('is-invalid'));

        // Validate Source Name
        if (sourceName.value.trim().length < 3) {
            showError(sourceName, 'Source name must be at least 3 characters long.');
            isValid = false;
        }

        // Validate PFAS Tested/Detected logic
        if (pfasTested.value === 'No' && pfasDetected.value === 'Yes') {
            showError(pfasDetected, 'PFAS cannot be detected if it was not tested.');
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
            // Scroll to the first error
            const firstError = form.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });

    // Real-time validation for PFAS logic
    pfasTested.addEventListener('change', function() {
        if (this.value === 'No' && pfasDetected.value === 'Yes') {
            showError(pfasDetected, 'PFAS cannot be detected if it was not tested.');
        } else {
            clearError(pfasDetected);
        }
    });

    pfasDetected.addEventListener('change', function() {
        if (pfasTested.value === 'No' && this.value === 'Yes') {
            showError(this, 'PFAS cannot be detected if it was not tested.');
        } else {
            clearError(this);
        }
    });
});
