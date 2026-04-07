const loaderContainer = document.getElementById('loader-container');
const loader = document.getElementById('loader');
const submitButton = document.getElementById('final-submit');
const pwsForm = document.getElementById('pwsInfoForm');

// --------------------------------- functions -------------------------------

function showLoaderDisableEl(el){
    el.disabled = true;
    loaderContainer.style.display = 'flex';
    loader.style.display = 'block';
}

// --------------------------------do stuff ------------------------------------
pwsForm.addEventListener('submit', function(event){

    showLoaderDisableEl(submitButton)

});


document.getElementById('save_draft').addEventListener("click", function (event){

    document.querySelectorAll('[required]').
    forEach(el => el.required = false);

    document.getElementById('draft_complete').value = "draft";

    loaderContainer.style.display = 'flex';
    loader.style.display = 'block';
    pwsForm.submit();

})