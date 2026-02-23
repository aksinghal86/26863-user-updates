from django.core.files.storage import default_storage


def upload_to_local(pwsid, file, folder):
    local_path = f"{pwsid}/{folder}/{file.name}"
    default_storage.save(local_path, file)


def validate_file(file):
    name = file.name
    size = file.size

    if (name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')) and size <= (25 * 1024 * 1024)):
        return True
    else:
        raise Exception("File type or size is invalid.")
