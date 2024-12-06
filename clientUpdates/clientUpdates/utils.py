import os

import dropbox
import logging
import requests
from itertools import chain
from collections import defaultdict
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from .models import Source
logger = logging.getLogger('clientUpdates')

def update_ehe_source_table():
    """
    The only changes that should ever me made are to EH&E's tables not claim tables (all prefixed with 'claim_')
    When the water provider updates PFAS result(s), Max Flow Rate, or Annual Production, the following steps need to be taken:
        - calculate new PFAS score for the source
        - calculate new Adjusted Flow Rate (AFR) for the source using the highest max flow rate and three highest years of annual production (not including 2013)
        - update the EHE source table accordingly. note that if PFAS result has been added for a previously unimpacted source, then all_nds needs to be changed to False
        - calculate GFE per source
    
    In order to do so, the following needs to be done: 
        - merge data from claim pfas results and claim flow rate tables with the corresponding EH&E tables to have the full data set of PFAS results and flow rates. 
        - filter ehe tables by data_origin = "EHE Update Portal" and updated_by_water_provider = True
        - ensure that have a) unique entry per year, per analyte and for max flow rate, and b) the highest value for each of those categories. 
        PfasResult.get.object(pwsid=pwsid, source_name=source_name, analyte='PFOA').order_by(result_ppt, -1).first()
        - find the max_other

    """
    return 

def update_ehe_pws_table():
    return

def handle_update(request, form_class, extra_fields, impacted=None, calc_func=None, source_variable=None):
    """
    Handles common update logic for PFAS results, max flow rate, and annual production.
    """
    if request.method == 'POST':
        pwsid = request.POST.get('pwsid')
        source_name = request.POST.get('source_name')
        form = form_class(request.POST, request.FILES)

        if form.is_valid():
            logger.debug("Received valid form data: %s", form.cleaned_data)

            # Save form instance without committing immediately
            instance = form.save(commit=False)

            # Add shared fields
            instance.pwsid = pwsid
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
                # TODO: Joe, please ensure this works for PFAS results, max flow rate, and annual production updates.
                instance.save()
                update_ehe_source_table()
                update_ehe_pws_table()

                filetype = 'Flow Rate' if source_variable else 'PFAS Results'
                logger.info(f"{filetype} updated successfully for {source_name}.")
                messages.success(request, f"{filetype} updated successfully.")

                # Upload file to Dropbox
                # TODO: Joe, pleae ensure that this works.
                file = request.FILES.get('filename')
                
                if file:
                    upload_to_dropbox(file, filetype, pwsid)

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



def calc_ppt_result(result, unit):
    """ Returns results after converting from ppm, ppb, or ppt to ppt. """
    if unit == 'ppt':
        result_ppt = result 
    elif unit == 'ppb':
        result_ppt = result * 1e3
    elif unit == 'ppm':
        result_ppt = result * 1e6
    else:
        raise ValueError(f"Unsupported unit '{unit}' provided.")

    return result_ppt

def calc_gpm_flow_rate(flow_rate, unit):
    """ Returns flow rate after converting form MGD, MGY, GPM, GPY, or AFPY to GPM. """
    if unit == 'mgd':
        flow_rate_gpm = flow_rate * 1e6 / 1440
    elif unit == 'gpm':
        flow_rate_gpm = flow_rate
    elif unit == 'gpy':
        flow_rate_gpm = flow_rate / (365 * 1440)
    elif unit == 'mgy':
        flow_rate_gpm = flow_rate * 1e6 / (365 * 1440)
    elif unit == 'afpy':
        flow_rate_gpm = flow_rate * 325851 / (365 * 1440)
    else:
        raise ValueError(f"Unsupported unit '{unit}' provided.")
    
    return flow_rate_gpm


def get_max_entry(entries, key):
    """ Returns the entry with the maximum value for the given key. """
    if not entries:
        return None
    
    return max(entries, key=lambda x: x[key], default=None)

def get_combined_results(queryset_1, queryset_2, columns):
    """ Combines two querysets by selecting only the specified columns. """
    results_1 = list(queryset_1.values(*columns))
    results_2 = list(queryset_2.values(*columns))
    return list(chain(results_1, results_2))

def get_max_results_by_analyte(combined_pfas_results):
    """ Finds the maximum result per analyte from a combined list of records. """
    max_results_by_analyte = defaultdict(lambda: None)
    for record in combined_pfas_results:
        analyte = record['analyte']
        if max_results_by_analyte[analyte] is None or record['result_ppt'] > max_results_by_analyte[analyte]['result_ppt']:
            max_results_by_analyte[analyte] = record
    return list(max_results_by_analyte.values())

def add_pfoas_if_missing(pfas_results, pwsid, water_source_id, source_name):
    """ Add PFOA and PFOS if they are not in the list. """
    analytes_to_include = ['PFOA', 'PFOS']
    for analyte in analytes_to_include:
        if not any(result['analyte'] == analyte for result in pfas_results):
            pfas_results.append({
                'pwsid': pwsid,
                'water_source_id': water_source_id,
                'source_name': source_name,
                'analyte': analyte,
                'result_ppt': 0,
                'sampling_date': None,
                'analysis_date': None,
                'lab_sample_id': None,
                'data_origin': 'N/A'
            })
    return pfas_results


def get_max_other_threshold(pfas_results):
    """ Finds the threshold result for the maximum another analyte. """
    pfoa_result = next((result['result_ppt'] for result in pfas_results if result['analyte'] == 'PFOA'), 0)
    pfos_result = next((result['result_ppt'] for result in pfas_results if result['analyte'] == 'PFOS'), 0)
    return round((pfoa_result + pfos_result) ** 2, 1)

def get_filtered_annuals(combined_annuals, all_nds):
    """
    Filters annual production records based on source.all_nds value.
    - If `all_nds` is True, include all years from 2013 to 2022.
    - If `all_nds` is False, include non-zero years from 2013 to 2022.
    - Always include year 2023 for adding or updating.
    - If impacted sources have less than 3 non-zero years, add the highest year(s) with zero production to ensure 3 years are shown.
    """
    filtered_annuals = []
    non_zero_years = []
    zero_years = []

    for record in combined_annuals:
        year = record['year']
        flow_rate = record['flow_rate']

        if year == 2023:
            # Always include 2023 for adding or updating
            filtered_annuals.append(record)
        elif all_nds:
            # For unimpacted sources, include all years from 2013 to 2022
            if 2013 <= year <= 2022:
                filtered_annuals.append(record)
        elif not all_nds:
            # For impacted sources, separate non-zero and zero flow rate years
            if 2013 <= year <= 2022:
                if flow_rate > 0:
                    non_zero_years.append(record)
                else:
                    zero_years.append(record)

    # For impacted sources, ensure at least 3 years are shown
    if not all_nds:
        filtered_annuals.extend(non_zero_years)
        if len(non_zero_years) < 3:
            zero_years_sorted = sorted(zero_years, key=lambda x: x['year'], reverse=True)
            filtered_annuals.extend(zero_years_sorted[:3 - len(non_zero_years)])

    # Check if 2023 entry exists; if not, create a placeholder for 2023
    if not any(record['year'] == 2023 for record in filtered_annuals):
        filtered_annuals.append({
            'year': 2023,
            'flow_rate': 0,
            'unit': 'GPY',
            'data_origin': 'EHE portal',  
            'updated_by_water_provider': True  
        })

    # Sort filtered annuals by year in increasing order
    filtered_annuals = sorted(filtered_annuals, key=lambda x: x['year'])

    return filtered_annuals

def get_max_annuals_by_year(combined_annuals):
    """ Finds the maximum annual production by year from a combined list of records. """
    max_annuals_by_year = defaultdict(lambda: None)
    for record in combined_annuals:
        year = record['year']
        if max_annuals_by_year[year] is None or record['flow_rate_gpm'] > max_annuals_by_year[year]['flow_rate_gpm']:
            max_annuals_by_year[year] = record
    return list(max_annuals_by_year.values())

def detected(result):
    if result != 0:
        return True
    else:
        return False




DROPBOX_TOKEN_URL = "https://api.dropbox.com/oauth2/token"

def refresh_dropbox_access_token():
    """
    Refresh the Dropbox access token using the refresh token.
    
    Returns:
        str: The new access token if successful, or None if failed.
    """
    try:
        response = requests.post(
            "https://api.dropbox.com/oauth2/token",
            data={
                'grant_type': 'refresh_token',
                'refresh_token': settings.DROPBOX['refresh_token']
                #'client_id': settings.DROPBOX['app_key'],
                #'client_secret': settings.DROPBOX['app_secret']
            },
            auth=(settings.DROPBOX['app_key'], settings.DROPBOX['app_secret'])
        )
        response.raise_for_status()  # Fixed missing parentheses
        token_data = response.json()

        # Update access token in settings or database
        settings.DROPBOX['access_token'] = token_data['access_token']
        return token_data['access_token']
    except requests.exceptions.RequestException as e:
        print(f"Error refreshing Dropbox access token: {e}")
        return None

def ensure_dropbox_folder(dbx, folder_path):
    """
    Ensure the specified folder exists in Dropbox.
    
    Args:
        dbx (dropbox.Dropbox): Authenticated Dropbox client.
        folder_path (str): The folder path in Dropbox.
    """
    try:
        dbx.files_get_metadata(folder_path)
    except dropbox.exceptions.ApiError as e:
        if isinstance(e.error, dropbox.files.GetMetadataError):
            dbx.files_create_folder_v2(folder_path)

def upload_to_dropbox(file, filetype, pwsid):
    """
    Upload a file to Dropbox under the specified folder.
    
    Args:
        file: The uploaded file object.
        filetype (str): Type of the file to organize folders (e.g., 'documents').
        pwsid (str): A unique identifier for the folder in Dropbox.
    
    Returns:
        JsonResponse: A response indicating success or failure.
    """
    if not file:
        return JsonResponse({'error': 'No file uploaded'}, status=400)

    # Get the current access token
    dropbox_access_token = settings.DROPBOX['access_token']
    if not dropbox_access_token:
        dropbox_access_token = refresh_dropbox_access_token()
        if not dropbox_access_token:
            return JsonResponse({'error': 'Failed to refresh Dropbox token'}, status=401)

    try:
        # Initialize Dropbox client
        dbx = dropbox.Dropbox(dropbox_access_token)

        # Define folder and file paths
        folder_path = f"/uploads/{pwsid}/{filetype}"
        dropbox_path = f"{folder_path}/{file.name}"

        # Path for local upload
        local_path = f"{pwsid}/{filetype}/{file.name}"

        # Save locally
        # TODO: Joe, might be a good idea to save locally temporarily and delete after 5 days. 
        # safeguard against dropbox not working. 
        # deleting after 5 days or so will help with storage issues if that becomes a problem. 

        # if the file does not already exist, save to local storage.
        if not os.path.exists(default_storage.path(local_path)):
            default_storage.save(local_path, file)

        # Ensure folder exists
        ensure_dropbox_folder(dbx, folder_path)

        # Upload the file
        with file.open('rb') as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)

        # Return success response
        logger.info(f"{file} uploaded to Dropbox under /uploads/{pwsid}/{filetype}/ successfully.")
        return JsonResponse({'success': 'File uploaded to Dropbox successfully', 'path': dropbox_path})
    except dropbox.exceptions.AuthError:
        # Refresh token and retry
        dropbox_access_token = refresh_dropbox_access_token()
        if dropbox_access_token:
            dbx = dropbox.Dropbox(dropbox_access_token)
            with file.open('rb') as f:
                dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode.overwrite)
            return JsonResponse({'success': 'File uploaded to Dropbox successfully', 'path': dropbox_path})
        return JsonResponse({'error': 'Dropbox authentication failed'}, status=401)
    except dropbox.exceptions.ApiError as e:
        return JsonResponse({'error': f'Dropbox API error: {str(e)}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)
