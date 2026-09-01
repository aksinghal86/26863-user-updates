
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

