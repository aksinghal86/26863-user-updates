const loaderContainer = document.getElementById('loader-container');
const loader = document.getElementById('loader');
const submitButton = document.getElementById('final-submit');
const pwsForm = document.getElementById('pwsInfoForm');
const privateCodeDiv = document.getElementById('privateCodeDiv')
const stateFedSueDiv = document.getElementById('stateFedSueDiv')
const sdwisCode = document.getElementById('sdwis_owner_code')

// --------------------------------- functions -------------------------------

function showLoaderDisableEl(el){
    el.disabled = true;
    loaderContainer.style.display = 'flex';
    loader.style.display = 'block';
}

function validate(){

    // define what elements are needed to validate
    const ein = document.getElementById('ein');
    const zipCodes = document.querySelectorAll('[id$="zip"]');
    const phoneNumbers = document.querySelectorAll('[id$="phone"]');
    const emails = document.querySelectorAll('[id$="email"]');

    // clear any existing validation error messages
    document.querySelectorAll("div.custom-invalid").forEach(el => el.remove());

    let valid = true;

    // validate the EIN
    if (!/^[A-Z0-9a-z]{2}-[A-Z0-9a-z]{7}$/.test(ein.value)){
        console.log("error")
        showError(ein, "The EIN must follow an alphanumeric pattern of XX-XXXXXXX.", 1)
        valid = false;
    }

    // validate zip codes
    zipCodes.forEach(el => {
        if (!/[0-9]{5}$/.test(el.value)){
            showError(el, "The ZIP Code must be 5 integers.", 2)
            valid = false;
        }
    })

    // validate phone numbers
    phoneNumbers.forEach(el => {
        if (!/[0-9]{3}-[0-9]{3}-[0-9]{4}$/.test(el.value) && el.value !== ""){
            showError(el, "The phone number must be in the format 111-111-1111.", 1)
            valid = false;
        }
    })

    // validate emails
    emails.forEach(el => {
        if (!/@/.test(el.value) && el.value !== ""){
            showError(el, "Emails must contain the '@' symbol.", 1)
            valid = false;
        }
    })

    return valid;
}

function showError(el, message, levels){

    //el.parentElement.nextElementSibling.hidden = false;
    const errorDiv = document.createElement('div');
    errorDiv.className = 'custom-invalid';
    errorDiv.textContent = message;
    if (levels === 1) {
        el.parentElement.insertAdjacentElement('afterend', errorDiv);
    }
    if (levels === 2) {
        el.parentElement.parentElement.insertAdjacentElement('afterend', errorDiv);
    }


}

// --------------------------------do stuff ------------------------------------
pwsForm.addEventListener('submit', function(event){
    event.preventDefault()
    if (confirm('Are you sure you would like to submit this form?')){
        let valid = validate();
        if (!valid){
            alert("Please fix validation errors that exist in the form.");
        } else {
            showLoaderDisableEl(submitButton)
            pwsForm.submit();
        }
    }
});


document.getElementById('save_draft').addEventListener("click", function (event){
    let valid = validate();
    if (!valid){
        alert("Please fix validation errors that exist in the form.");
    } else {
        document.querySelectorAll('[required]').
        forEach(el => el.required = false);

        document.getElementById('draft_complete').value = "draft";

        loaderContainer.style.display = 'flex';
        loader.style.display = 'block';
        pwsForm.submit();
    }

})


document.addEventListener("DOMContentLoaded", function () {

    sdwisCode.addEventListener("change", function(){

        let code = sdwisCode.value;
        if(code === "P"){
            privateCodeDiv.hidden = false;
            privateCodeDiv.querySelector('select').required = true;

            stateFedSueDiv.hidden = true;
            stateFedSueDiv.querySelector('select').required = false;
            stateFedSueDiv.querySelector('select').value = "";
        }

        if(code === "F" || code === "S"){

            stateFedSueDiv.hidden = false;
            stateFedSueDiv.querySelector('select').required = true;

            privateCodeDiv.hidden = true;
            privateCodeDiv.querySelector('select').required = false;
            privateCodeDiv.querySelector('select').value = "";

        }
        if(code !== "P" && code !== "S" && code !== "F"){
            privateCodeDiv.hidden = true;
            privateCodeDiv.querySelector('select').required = false;
            privateCodeDiv.querySelector('select').value = "";

            stateFedSueDiv.hidden = true;
            stateFedSueDiv.querySelector('select').required = false;
            stateFedSueDiv.querySelector('select').value = "";
        }

    })

})