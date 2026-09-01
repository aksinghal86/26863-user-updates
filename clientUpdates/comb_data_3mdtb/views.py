from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .utils import process_pfas, process_annual_flow, get_dashboard_data
from .forms import PFASUpdateForm

from django.views.decorators.cache import never_cache


@login_required
@never_cache
def landing_page(request):

    # get pwsid
    pwsid = request.user.username

    # retrieve all dashboard data for the given pwsid
    data = get_dashboard_data(pwsid)

    return render(request, "comb_data_3mdtb/landing_page.html", {"data": data})


@login_required
@never_cache
def pfas_update(request):
    if request.method == "POST":
        min_value = request.POST.get('min_value')
        form = PFASUpdateForm(request.POST, request.FILES, min_result=min_value)
        if form.is_valid():
            # Save form instance without committing immediately
            instance = form.save(commit=False)
            
            # Map the uploaded file name to the filename field in the model
            supporting_file = request.FILES.get('supporting_file')
            if supporting_file:
                instance.filename = supporting_file.name
            
            # Ensure pwsid and source_name are saved from the form (which are hidden)
            instance.pwsid = request.POST.get('pwsid')
            instance.source_name = request.POST.get('source_name')
            instance.unit = "ppt" # Standard unit for these updates
            
            instance.save()
            return redirect("comb_data_3mdtb:landing_page")
        else:
            # Re-render update page with form errors
            analyte = request.POST.get('analyte', 'PFOA')
            pwsid = request.POST.get('pwsid')
            source_name = request.POST.get('source_name')
            return render(
                request,
                "comb_data_3mdtb/pfas_update.html",
                {
                    "form": form,
                    "analyte": analyte,
                    "pwsid": pwsid,
                    "source_name": source_name,
                    "min_value": min_value
                }
            )
    
    # GET request
    analyte = request.GET.get('analyte', 'PFOA')
    pwsid = request.GET.get('pwsid')
    source_name = request.GET.get('source_name')
    min_value = request.GET.get('min_value')
    
    form = PFASUpdateForm()
    return render(
        request,
        "comb_data_3mdtb/pfas_update.html",
        {
            "form": form,
            "analyte": analyte,
            "pwsid": pwsid,
            "source_name": source_name,
            "min_value": min_value
        }
    )
