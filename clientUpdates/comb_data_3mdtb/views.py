from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .utils import process_pfas, process_annual_flow, get_dashboard_data, get_all_yearly_flows
from .forms import PFASUpdateForm, AFUpdateForm, MFUpdateForm
from clientUpdates.utils.calculations import calc_gpm_flow_rate

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
    selected_analyte = request.GET.get('selected_analyte')
    
    form = PFASUpdateForm()
    return render(
        request,
        "comb_data_3mdtb/pfas_update.html",
        {
            "form": form,
            "analyte": analyte,
            "pwsid": pwsid,
            "source_name": source_name,
            "min_value": min_value,
            "selected_analyte": selected_analyte
        }
    )


@login_required
@never_cache
def annual_flows(request):
    pwsid = request.GET.get('pwsid')
    source_name = request.GET.get('source_name')
    all_nds_param = request.GET.get('all_nds')

    if not pwsid:
        pwsid = request.user.username

    yearly_flows = get_all_yearly_flows(pwsid, source_name)

    # Convert all_nds_param string to boolean
    if all_nds_param is not None:
        all_nds = all_nds_param.lower() == 'true'
    else:
        # Fallback in case it's not provided
        all_nds = False

    return render(
        request,
        "comb_data_3mdtb/annual_flows.html",
        {
            "pwsid": pwsid,
            "source_name": source_name,
            "source_data": yearly_flows,
            "all_nds": all_nds,
        }
    )


@login_required
@never_cache
def af_update(request):
    if request.method == "POST":
        form = AFUpdateForm(request.POST, request.FILES)
        pwsid = request.POST.get('pwsid')
        source_name = request.POST.get('source_name')
        year = request.POST.get('year')

        if form.is_valid():
            instance = form.save(commit=False)
            
            supporting_file = request.FILES.get('supporting_file')
            if supporting_file:
                instance.filename = supporting_file.name
            
            instance.pwsid = pwsid
            instance.source_name = source_name
            instance.year = year
            instance.flow_rate_gpm = calc_gpm_flow_rate(instance.flow_rate, instance.unit)
            
            instance.save()
            return redirect(f"/annual_flows/?pwsid={pwsid}&source_name={source_name}")
        else:
            return render(
                request,
                "comb_data_3mdtb/af_update.html",
                {
                    "form": form,
                    "pwsid": pwsid,
                    "source_name": source_name,
                    "year": year,
                }
            )
    
    # GET request
    pwsid = request.GET.get('pwsid')
    source_name = request.GET.get('source_name')
    year = request.GET.get('year')
    
    form = AFUpdateForm()
    return render(
        request,
        "comb_data_3mdtb/af_update.html",
        {
            "form": form,
            "pwsid": pwsid,
            "source_name": source_name,
            "year": year,
        }
    )


@login_required
@never_cache
def mf_update(request):
    if request.method == "POST":
        form = MFUpdateForm(request.POST, request.FILES)
        pwsid = request.POST.get('pwsid')
        source_name = request.POST.get('source_name')

        if form.is_valid():
            instance = form.save(commit=False)
            
            supporting_file = request.FILES.get('supporting_file')
            if supporting_file:
                instance.filename = supporting_file.name
            
            instance.pwsid = pwsid
            instance.source_name = source_name
            instance.flow_rate_gpm = calc_gpm_flow_rate(instance.flow_rate, instance.unit)
            
            instance.save()
            return redirect("comb_data_3mdtb:landing_page")
        else:
            return render(
                request,
                "comb_data_3mdtb/mf_update.html",
                {
                    "form": form,
                    "pwsid": pwsid,
                    "source_name": source_name,
                }
            )
    
    # GET request
    pwsid = request.GET.get('pwsid')
    source_name = request.GET.get('source_name')
    
    form = MFUpdateForm()
    return render(
        request,
        "comb_data_3mdtb/mf_update.html",
        {
            "form": form,
            "pwsid": pwsid,
            "source_name": source_name,
        }
    )
