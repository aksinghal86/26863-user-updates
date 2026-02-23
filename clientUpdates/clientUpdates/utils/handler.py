import logging

from django.core.files.storage import default_storage

# Custom functions
from .updates import update_ehe_pws_table, update_ehe_source_table
from .dropbox_utils import upload_to_dropbox
# Django functions
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect


logger = logging.getLogger('clientUpdates')


def handle_update(request, form_class, extra_fields, impacted=None, calc_func=None, source_variable=None):
    """
    Handles common update logic for PFAS results, max flow rate, and annual production.
    Also updates source and pws tables every time a user updates either production, annual flow rate, or pfas results. 
    """
    if request.method == 'POST':
        pwsid = request.POST.get('pwsid')
        water_source_id = request.POST.get('water_source_id')
        source_name = request.POST.get('source_name')
        form = form_class(request.POST, request.FILES)

        if form.is_valid():
            logger.debug("Received valid form data: %s", form.cleaned_data)

            # Save form instance without committing immediately
            instance = form.save(commit=False)

            # Add shared fields
            instance.pwsid = pwsid
            instance.water_source_id = water_source_id
            instance.source_name = source_name
            instance.submit_date = timezone.now()
            instance.filename = form.cleaned_data.get('filename').name
            instance.data_origin = "EHE Update Portal"
            instance.updated_by_water_provider = True

            # Add extra fields
            for field, value in extra_fields.items():
                setattr(instance, field, form.cleaned_data.get(value, value))

            # Calculate additional fields if calc_func is provided
            if calc_func:
                calc_func(instance, form.cleaned_data)

            # Add source variable if provided
            if source_variable:
                instance.source_variable = source_variable

            try:
                instance.save()

                # Trigger updates of EH&E Source and Pws tables
                # update_ehe_source_table(pwsid, source_name)
                # update_ehe_pws_table(pwsid)

                filetype = 'Flow Rate' if source_variable else 'PFAS Results'
                logger.info(f"{filetype} updated successfully for {source_name}.")
                messages.success(request, f"{filetype} updated successfully.")

                # Upload file to Dropbox
                file = request.FILES.get('filename')
                
                if file:
                    #upload_to_dropbox(file, filetype, pwsid)

                    # Temporarily saving files locally. Uncomment the upload_to_dropbox function
                    # once ready for production.
                    local_path = f"{pwsid}/{filetype}/{file.name}"
                    default_storage.save(local_path, file)

                return redirect('source-detail', pwsid=pwsid, source_name=source_name)
            except Exception as e:
                logger.error("Error saving instance: %s", e)
                messages.error(request, "Failed to save updates due to a system error.")
                return redirect('source-detail', pwsid=pwsid, source_name=source_name)

        else:
            logger.error("Form validation failed with errors: %s", form.errors)
            messages.error(request, "Form validation failed. Please correct the errors below.")
            return redirect('source-detail', pwsid=pwsid, source_name=source_name)

    messages.error(request, "Invalid request.")
    return redirect('source-detail', pwsid=request.POST.get('pwsid'), source_name=request.POST.get('source_name'))

# def file_upload(instance, filename):
#     print("{0}/{1}".format( instance.pwsid, filename))
#     return "{0}/{1}".format(instance.pwsid, filename)


