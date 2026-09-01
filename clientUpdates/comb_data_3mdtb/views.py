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
        form = PFASUpdateForm(request.POST, request.FILES)
        if form.is_valid():
            # Save form instance without committing immediately
            instance = form.save(commit=False)
            
            # Map the uploaded file name to the filename field in the model
            supporting_file = request.FILES.get('supporting_file')
            if supporting_file:
                instance.filename = supporting_file.name
            
            instance.save()
            return redirect("comb_data_3mdtb:landing_page")
        else:
            # Re-render update page with form errors
            analyte = request.POST.get('analyte', 'PFOA')
            return render(
                request,
                "comb_data_3mdtb/pfas_update.html",
                {
                    "form": form,
                    "analyte": analyte
                }
            )
    
    # GET request
    analyte = request.GET.get('analyte', 'PFOA')
    form = PFASUpdateForm()
    return render(
        request,
        "comb_data_3mdtb/pfas_update.html",
        {
            "form": form,
            "analyte": analyte
        }
    )
