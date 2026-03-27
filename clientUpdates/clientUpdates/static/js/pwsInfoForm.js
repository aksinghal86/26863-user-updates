const loaderContainer = document.getElementById('loader-container');
const loader = document.getElementById('loader');
const submitButton = document.getElementById('submit');

// --------------------------------- functions -------------------------------

function showLoaderDisableEl(el){
    el.disabled = true;
    loaderContainer.style.display = 'flex';
    loader.style.display = 'block';
}

// --------------------------------do stuff ------------------------------------
document.getElementById('pwsInfoForm').addEventListener('submit', function(event){

    showLoaderDisableEl(submitButton)

});