
// ---------- phase2_landing_page -------------------

const deleteButtons = Array.from(document.querySelectorAll('form'))
    .filter(form => form.querySelector('button.btn.btn-danger'));
const addPWSForm = document.getElementById('addPWSForm');
const addSourceForm = document.getElementById('addSourceForm')
const viewEditButtons = document.querySelectorAll('.btn-warning')
const loaderContainer = document.getElementById('loader-container');
const loader = document.getElementById('loader');
const addFormButtons = Array(addPWSForm, addSourceForm)


// --------------------------------- functions -------------------------------

function showLoaderDisableEl(el){
    el.disabled = true;
    loaderContainer.style.display = 'flex';
    loader.style.display = 'block';
}


// -----------------------------------do stuff ---------------------------------
deleteButtons.forEach(node =>node.addEventListener("click", function (elem) {

        let check = true;
        if (!confirm("Are you sure you'd like to delete this form?")) {
            elem.preventDefault();
            check = false;
        } else if (!confirm("The information contained in this form cannot be recovered once deleted. Are you sure you'd like to proceed?")) {
            elem.preventDefault();
            check = false;
        }
        if (check === true){
            showLoaderDisableEl(elem)
        }

    })
);

addFormButtons.forEach(el => el.addEventListener("click", () => showLoaderDisableEl(el)));
viewEditButtons.forEach(el => el.addEventListener("click", () => showLoaderDisableEl(el)));



