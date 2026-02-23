import dropbox
import logging
import os
import requests
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse

logger = logging.getLogger('clientUpdates')
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
