
/* ============================================================
   PFAS UPDATE MODAL
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

    const modal =
        document.getElementById('pfas-update-modal');

    const closeButton =
        document.getElementById('pfas-modal-close');

    const cancelButton =
        document.getElementById('pfas-modal-cancel');


    /* ============================================================
       OPEN MODAL
       ============================================================ */

    const editButtons =
        document.querySelectorAll('.pfas-edit-button');


    editButtons.forEach(function (button) {

        button.addEventListener('click', function () {
            const analyte = button.getAttribute('data-analyte');

            const analyteText = document.getElementById('pfas-analyte-text');
            const analyteSelect = document.getElementById('pfas-analyte-select');

            if (analyte === 'Other PFAS') {
                // Switch to dropdown for Other PFAS
                if (analyteText) {
                    analyteText.readOnly = true;
                    analyteText.style.display = 'none';
                    analyteText.disabled = true;
                }
                if (analyteSelect) {
                    analyteSelect.style.display = '';
                    analyteSelect.disabled = false;
                    analyteSelect.value = '';
                }
            } else {
                // Ensure text input shows PFOA/PFOS and dropdown hidden
                if (analyteText) {
                    analyteText.value = analyte || '';
                    analyteText.readOnly = true;
                    analyteText.style.display = '';
                    analyteText.disabled = false;
                }
                if (analyteSelect) {
                    analyteSelect.style.display = 'none';
                    analyteSelect.disabled = true;
                }
            }

            modal.style.display = 'flex';

        });

    });


    /* ============================================================
       CLOSE MODAL
       ============================================================ */

    closeButton.addEventListener('click', function () {

        modal.style.display = 'none';

    });


    cancelButton.addEventListener('click', function () {

        modal.style.display = 'none';

    });


    /* ============================================================
       CLOSE WHEN CLICKING OUTSIDE MODAL
       ============================================================ */

    modal.addEventListener('click', function (event) {

        if (event.target === modal) {

            modal.style.display = 'none';

        }

    });

});

