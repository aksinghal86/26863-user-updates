// Define variables
const annualFileSelectors = document.querySelectorAll('[id^="annualflow-"][id$="-file_name"]');
const annualDeleteButtons = document.querySelectorAll('[data-target^="annualFile"]');
const annualFileDivs = document.querySelectorAll('[id^="div_annualFile"]');
const annualFiles = document.querySelectorAll('[id^="annualFile"]');
const annualAddFileButton = document.getElementById('annualAddFileButton');
const annualFlowRates = document.querySelectorAll('[id^="annualflow-"][id$="-flow_rate"]');
let annualFileNameList = [];

const pfasFileSelectors = document.querySelectorAll('[id^="pfas-"][id$="-file_name"]');
const pfasDeleteButtons = document.querySelectorAll('[data-target^="pfasFile"]');
const pfasFiles = document.querySelectorAll('[id^="pfasFile"]');
const pfasFileDivs = document.querySelectorAll('[id^="div_pfasFile"]');
const pfasAddFileButton = document.getElementById('pfasAddFileButton');
let pfasFileNameList = [];

const pfasResultsDiv = document.getElementById('pfasResultsDiv')
const pfasEverTested = document.getElementById('pfas_ever_tested')
const pfasCommentsDiv = document.getElementById('pfasCommentsDiv')
const pfasDetected = document.getElementById('pfas_detected')

const pfasResults = document.querySelectorAll('[id^="pfas-"][id$="-result"]');
const maxFlowFile = document.getElementById('maxFlowFile');

const submitButton = document.getElementById('final-submit');
const loaderContainer = document.getElementById('loader-container');
const loader = document.getElementById('loader');
const pfasFormElem = Array.from(document.getElementById('pfasResultsDiv').querySelectorAll('[id$="analyte"], [id$="units"], [id$="result"], [id$="sample_date"], [id$="file_name"]')).filter(el => !el.id.startsWith("pfas-6"));

const allPfasFormElem = document.getElementById('pfasResultsDiv').querySelectorAll('[id$="analyte"], [id$="units"], [id$="result"], [id$="sample_date"], [id$="file_name"]');
const otherResult = document.getElementById('pfas-6-result');

const annualErrorDiv = document.getElementById('annualErrorDiv');
const pfasErrorDiv = document.getElementById('pfasErrorDiv');
const maxFlowErrorDiv = document.getElementById('maxFlowErrorDiv');
const otherResultErrorDiv = document.getElementById('otherPFASErrorDiv');

const maxFlowFileName = document.getElementById('maxflow-file_name');

const sourceForm = document.getElementById('sourceForm');

const draft_complete = document.getElementById('draft_complete');

let initPfasFileNames = []
let initAnnualFileNames = []

const sourceName = document.getElementById('source_name');

// Functions --------------------------------------------------------------------------------------------------------


function renderFileNames(selectorList, fileNameList) {
   selectorList.forEach(elem => {

        // save previous value, if any
        let selected = elem.value
        // clear list of options
        elem.options.length = 0;

        // re-implement default option
        const defaultOption = document.createElement("option");
        defaultOption.value = "";
        defaultOption.textContent = "Select a file";
        defaultOption.disabled = true;
        // set default option only if the currently selected value is not in the fileNameList
        defaultOption.selected = fileNameList.indexOf(selected) === -1;
        elem.appendChild(defaultOption);

        fileNameList.forEach(file => {
            const option = document.createElement("option");
            option.value = file;
            option.textContent = file;
            if (selected === file){
                option.selected = true;
            }
            elem.appendChild(option);
        });

   });
};


function addFiles(button, nodeList) {
    button.addEventListener("click", function () {
        let nearest = Array.from(nodeList).find(elem => elem.classList.contains('hidden'));
        nearest.classList.remove("hidden");
        nearest.classList.add("d-flex");
        nearest.classList.add("justify-content-between");
    });
}

function deleteButtons(deleteButtonList, fileNameList, selectorList){
    deleteButtonList.forEach(elem => {
        elem.addEventListener("click", function () {
            // get associated fileInput
            const fileInput = document.getElementById(this.dataset.target);
            let parentDiv = elem.parentElement;

            // remove value from fileNameList
            if (fileInput.files.length > 0) {

                // get index of where value is found in array
                const index = fileNameList.indexOf(fileInput.files[0].name);

                // remove value
                if (index !== -1) {
                    fileNameList.splice(index, 1);
                }
            }

            // remove file value and hide
            fileInput.value = "";
            //fileInput.classList.add('hidden');

            // hide the delete button as well
            //elem.classList.add('hidden');
            parentDiv.classList.add('hidden');
            parentDiv.classList.remove('d-flex')

            // re-render filenames
            renderFileNames(selectorList, fileNameList);

        });
    });
};

function updateFileList(inputList, fileNameList, initList){
    // clear the array
    fileNameList.length = 0;
    // push all file names from input list
    inputList.forEach(elem => {
        // if the input is visible and has a file loaded
        if (elem.checkVisibility() && elem.files.length > 0) {
            fileNameList.push(elem.files[0].name);
        };
    });

    if (initList.length > 0) {
        for (let el of initList){
            if (fileNameList.indexOf(el) === -1){
                fileNameList.push(el)
            }
        }
    }

}

// function that acts on each pfas result input.
// if zero is entered, all other inputs in that row are rendered disabled
function zeroPfasResults(elem){

    // get closest row
    let row = elem.closest('tr')
    // get input and select tags, exclude all "result" fields, pfas-[0-5]-analyte fields, and pfas-[0-5]-units fields
    let inputsSelects =
        Array.
        from(row.querySelectorAll('input, select')).
        filter(elem => !elem.name.endsWith("result") && !/pfas-[0-5]-(analyte|units)$/.test(elem.id));

    // if the value is zero, disable fields
    if (elem.value !== "" && Number(elem.value) === 0){
        inputsSelects.forEach(e => e.disabled = true)
    } else {
        inputsSelects.forEach(e => e.disabled = false)
    }
}

function zeroAnnualFlowRates(elem){

    // get closest row
    let row = elem.closest('tr')
    // get input and select tags
    let inputsSelects =
        Array.
        from(row.querySelectorAll('input, select')).
            filter(elem => elem.name.endsWith("file_name") || elem.name.endsWith("units"))
        //filter(elem => !elem.name.endsWith("flow_rate") && !/annualflow-([0-9]|1[0-2])-year$/.test(elem.id) && !elem.nam);

    // if the value is zero, disable fields
    if (elem.value !== "" && Number(elem.value) === 0){
        inputsSelects.forEach(e => e.disabled = true)
    } else {
        inputsSelects.forEach(e => e.disabled = false)
    }
}







// clear values
function clearValues(el){
    if (el.tagName === "SELECT") {
        el.selectedIndex = 0;
    } else{
        el.value = '';
    }
}

// if a non-zero value is provided for the "other analyte", make all other parts
// of that form submission required
function checkNonZero(node) {
    let arr = Array.from(node.closest('tr').querySelectorAll('input, select')).filter(el => !el.id.endsWith("result"));
    if (Number(node.value) !== 0 && node.value !== "") {
        arr.forEach(otherEl => otherEl.required = true);
    } else{
        arr.forEach(otherEl => otherEl.required = false);
    }
}

function checkOtherHigher(){

    let pfas6Results = Array.from(pfasResults).filter(el => el.id !== 'pfas-6-result')
    let belowAll = pfas6Results.every(el => (Number(el.value) < Number(otherResult.value) || (Number(el.value) === 0 && Number(otherResult.value) === 0)));
    // default to true if the other result is blank
    if (otherResult.value === "") {belowAll = true};
    return belowAll

}


// Do Stuff -----------------------------------------------------------------------------------------------------------

// functions to run when page is loaded
document.addEventListener("DOMContentLoaded", function () {
    const sourceTypeSelect = document.getElementById('source_type');
    const sourceTypeOtherDiv = document.getElementById('sourceTypeOther');
    const sourceTypeOther = document.getElementById('source_type_other');
    const pwsOperator = document.getElementById('pws_operates_source');
    const otherOperator = document.getElementById('other_operates_source');
    const sourceCoOwned = document.getElementById('source_co_owned');
    const coOwnerInfoDiv = document.getElementById('coOwnerInfo');
    const coOwnerPWSID = document.getElementById('co_owner_pwsid')
    const coOwnerExplained = document.getElementById('co_owner_explained')
    const isPartOfIDWS = document.getElementById('is_part_of_idws')
    const idwsExplanationDiv = document.getElementById('idwsExplanation')
    const idwsExplanation = document.getElementById('idws_explanation')
    const purchasedFrom = document.getElementById('purchased_water_from');
    const pwsPurchased = document.getElementById('pws_purchased');



    // create function that toggles whether the 'hidden' class is applied
    function toggleHiddenRequired() {

        // define variables used more than once
        let detectedDates = Array.from(pfasDetected.parentElement.parentElement.querySelectorAll("div.form-group.grey-bottom")).filter(el => el.querySelector("[id^='detected_b4'], [id^='detected_after']"));

        // True/False Statements
        tf1 = sourceTypeSelect.value === "Other";
        tf2 = sourceCoOwned.value === "Yes";
        tf3 = isPartOfIDWS.value === "Yes";
        tf4 = pwsOperator.value === "No";
        tf5 = pwsPurchased.value === "Yes";
        tf6 = pfasDetected.value === "Yes";
        tf7 = pfasEverTested.value === "Yes";

        // toggle whether the elements are hidden or not
        sourceTypeOtherDiv.classList.toggle("hidden", !tf1);
        coOwnerInfoDiv.classList.toggle("hidden", !tf2);
        idwsExplanationDiv.classList.toggle("hidden", !tf3);
        otherOperator.parentElement.parentElement.classList.toggle("hidden", !tf4);
        purchasedFrom.parentElement.parentElement.classList.toggle("hidden", !tf5);
        detectedDates.forEach(el => el.classList.toggle("hidden", !tf6));
        pfasDetected.parentElement.classList.toggle("hidden", !tf7)

        // toggle whether they are required.
        sourceTypeOther.required = tf1;
        coOwnerPWSID.required = tf2;
        coOwnerExplained.required = tf2;
        idwsExplanation.required = tf3;
        otherOperator.required = tf4;
        purchasedFrom.required = tf5;
        detectedDates.forEach(el => el.required = tf6)
        pfasDetected.required = tf7;

    };

    // once the page is loaded, trigger the function to hide/show based on value
    toggleHiddenRequired();

    // apply function any time there are changes
    sourceTypeSelect.addEventListener("change", toggleHiddenRequired);
    sourceCoOwned.addEventListener("change", toggleHiddenRequired);
    isPartOfIDWS.addEventListener("change", toggleHiddenRequired);
    pwsOperator.addEventListener("change", toggleHiddenRequired);
    pwsPurchased.addEventListener("change", toggleHiddenRequired);
    pfasDetected.addEventListener("change", toggleHiddenRequired);
    pfasEverTested.addEventListener("change", toggleHiddenRequired);

    // when page is first loaded, hide pfas section if necessary based on results
    if (pfasEverTested.value === "No" || pfasDetected.value === "No") {
        pfasResultsDiv.classList.add('hidden');
        pfasCommentsDiv.classList.add('hidden');
        allPfasFormElem.forEach(elem => elem.required = false);
    }

    // when page first loads, determine whether form fields should be disabled
    // based on whether they have a zero result value
    pfasResults.forEach(elem => zeroPfasResults(elem));
    annualFlowRates.forEach(elem => zeroAnnualFlowRates(elem));

    // when page first loads, determine whether form field is required based on
    // whether a non zero result was entered
    checkNonZero(otherResult);

    maxFlowFile.addEventListener("change", function () {

        if (maxFlowFile.files.length > 0) {
            maxFlowFileName.value = maxFlowFile.files[0].name
        } else{
           maxFlowFileName.value = "";
        }
        // console.log("change");
        // maxFlowFileName.value = maxFlowFile.files[0].name ? maxFlowFile.files[0].name : "";

    })

    if (/edit/.test(sourceForm.action)){
        console.log("logic worked")
        pfasFileSelectors.forEach(el => {
            let fileName = el.value;
            console.log("fileName: ", fileName);
            if(initPfasFileNames.indexOf(fileName) === -1 && fileName !== "") {
                initPfasFileNames.push(el.value)
            }
        });
        console.log(initPfasFileNames);
        annualFileSelectors.forEach(el => {
            let fileName = el.value;
            if(initAnnualFileNames.indexOf(fileName) === -1 && fileName !== "") {
                initAnnualFileNames.push(el.value)
            }
        });
        console.log(initAnnualFileNames);
    }


    // when editing an existing form, make the fileList variable load file names that are
    // present in the selectors when page is first loaded. Populate the file list in the
    // selectors
    updateFileList(annualFiles, annualFileNameList, initAnnualFileNames);
    renderFileNames(annualFileSelectors, annualFileNameList);
    updateFileList(pfasFiles, pfasFileNameList, initPfasFileNames);
    renderFileNames(pfasFileSelectors, pfasFileNameList);


});

// conditionally hide pfas section, and whether the pfas section is required, based on
// the pfas detection question
pfasEverTested.addEventListener("change", function (e) {

    if(pfasEverTested.value === "No" || (pfasEverTested.value === "Yes" && pfasDetected.value === "No")){
        pfasResultsDiv.classList.add('hidden');
        pfasCommentsDiv.classList.add('hidden');
        console.log(allPfasFormElem);
        allPfasFormElem.forEach(elem => elem.required = false);
        allPfasFormElem.forEach(el => {
            if (!/pfas-[0-5]-(analyte)$/.test(el.id) && !el.id.endsWith("units")) {
                clearValues(el);
            }
        });

    } else {
        pfasResultsDiv.classList.remove('hidden');
        pfasCommentsDiv.classList.remove('hidden');
        pfasFormElem.forEach(elem => elem.required = true);
    }

})

// conditionally hide pfas section, and whether the pfas section is required, based on
// the pfas detection question
pfasDetected.addEventListener("change", function (e) {

    if(pfasDetected.value === "No" || (pfasDetected.value === "Yes" && pfasEverTested.value === "No")){
        pfasResultsDiv.classList.add('hidden');
        pfasCommentsDiv.classList.add('hidden');
        allPfasFormElem.forEach(elem => elem.required = false);
        allPfasFormElem.forEach(el => {
            if (!/pfas-[0-5]-(analyte)$/.test(el.id) && !el.id.endsWith("units")) {
                clearValues(el);
            }
        });
    } else {
        pfasResultsDiv.classList.remove('hidden');
        pfasCommentsDiv.classList.remove('hidden');
        pfasFormElem.forEach(elem => elem.required = true);
    }

})

// attach zeroPfasResults function to pfasResults on change
pfasResults.forEach(elem => addEventListener("change", function () {
    zeroPfasResults(elem);
}))

// attach zeroAnnualFlowRates function to annualFlowRates on change
annualFlowRates.forEach(elem => addEventListener("change", function () {
    zeroAnnualFlowRates(elem);
}))


addFiles(annualAddFileButton, annualFileDivs);
addFiles(pfasAddFileButton, pfasFileDivs);
deleteButtons(annualDeleteButtons, annualFileNameList, annualFileSelectors);
deleteButtons(pfasDeleteButtons, pfasFileNameList, pfasFileSelectors);

annualFiles.forEach(el => addEventListener("change", function(){

    updateFileList(annualFiles, annualFileNameList, initAnnualFileNames)
    renderFileNames(annualFileSelectors, annualFileNameList);

}));

pfasFiles.forEach(el => addEventListener("change", function(){

    updateFileList(pfasFiles, pfasFileNameList, initPfasFileNames)
    renderFileNames(pfasFileSelectors, pfasFileNameList);

}))


// --------- Do stuff with file validation --------------------------


function validation(complete){

    const clearValidationErrors = () => {
        annualErrorDiv.classList.add('hidden');
        annualFiles.forEach(el => el.classList.remove('is-invalid'));

        pfasErrorDiv.classList.add('hidden');
        pfasFiles.forEach(el => el.classList.remove('is-invalid'));

        maxFlowErrorDiv.classList.add('hidden');
        maxFlowFile.classList.remove('is-invalid');

        otherResultErrorDiv.classList.add('hidden');
        otherResult.classList.remove('is-invalid');

        document.querySelectorAll("[id=sourceNameErrorDiv]").forEach(el => el.remove());
    };

    const showValidationError = (inputElement, errorElement) => {
        if (errorElement) {
            errorElement.classList.remove('hidden')
        }
        inputElement.classList.add('is-invalid');
    };

    const validateFile = (type, fileInput) => {
        const maxFileSizeBytes = 25 * 1024 * 1024; // Max file size: 25 MB
        let allowedExtensions = []
        if (type === "annual" || type === "maxflow"){
            allowedExtensions = ['pdf', 'csv', 'xlsx', 'jpg', 'jpeg', 'png']
        } else if (type === "pfas") {
            allowedExtensions = ['pdf', 'jpg', 'jpeg', 'png']
        }
        const fileName = fileInput.value;
        const fileExtension = fileName.split('.').pop().toLowerCase();
        const file = fileInput.files[0];
        const errorElement = fileInput.closest('div.form-group').nextElementSibling;

        if (!allowedExtensions.includes(fileExtension) || (file && file.size > maxFileSizeBytes)) {
            showValidationError(fileInput, errorElement);
            return false;
        } else {
            return true;
        }

    };

    clearValidationErrors();

    // ensure a source name is provided
    const assertSourceName = () => {
        if(sourceName.value === ""){
            const errorDiv = document.createElement('div');
            errorDiv.id = "sourceNameErrorDiv";
            errorDiv.className = 'custom-invalid';
            errorDiv.textContent = "Please provide a source name.";
            sourceName.insertAdjacentElement("afterend", errorDiv);
            return false;
        } else {
            return true;
        }
    }

    let annualValid = true;
    annualFiles.forEach(elem => {
        if (elem.checkVisibility() && elem.files.length > 0){
            if(!validateFile("annual", elem)){
                annualValid = false;
            }
        }
    })

    let pfasValid = true;
    pfasFiles.forEach(elem => {
        if (elem.checkVisibility() && elem.files.length > 0){
            if(!validateFile("pfas", elem)){
                pfasValid = false;
            }
        }
    })

    let maxFlowValid = true;
    if (maxFlowFile.checkVisibility() && maxFlowFile.files.length > 0) {
        if (!validateFile("maxflow", maxFlowFile)) {
            maxFlowValid = false;
        }
    }
    // on submit (not save), ensure a filename has been assigned
    else if(maxFlowFile.files.length===0 && maxFlowFileName.value === "" && complete){
            maxFlowValid = false;
            showValidationError(maxFlowFile, maxFlowErrorDiv);
    }

    // if a non-zero value was entered for the 'other' pfas result, make sure that it is higher
    // than the other six pfas results
    let checkOther = checkOtherHigher()
    if (!checkOther){
        showValidationError(otherResult, otherResultErrorDiv)
    }

    if (!annualValid || !pfasValid || !maxFlowValid || !checkOther || !assertSourceName()) {
        return false;
    } else {
        return true;
    }



}

sourceForm.addEventListener('submit', function(event) {

    let is_valid = validation(true);
    if (!is_valid) {
        event.preventDefault();
        alert("Please fix validation errors that exist in the form.")
    } else {

        submitButton.disabled = true;
        loaderContainer.style.display = 'flex';
        loader.style.display = 'block';

    }


});

// Continue to do other stuff -----------------------------------------------------------------------------------

otherResult.addEventListener("change", () => checkNonZero(otherResult));

// when the "Save as Draft" button is clicked, remove required attribute from all fields, assign a
// value of "draft" to the draft_complete field, and submit the form
document.getElementById('save_draft').addEventListener("click", function (event){

    let is_valid = validation(false);
    if (!is_valid){
        event.preventDefault();
        alert("Please fix validation errors that exist in the form.")
    } else{

        document.querySelectorAll('[required]').
        forEach(el => el.required = false);
        draft_complete.value = "draft";

        loaderContainer.style.display = 'flex';
        loader.style.display = 'block';
        sourceForm.submit();
    }

})




