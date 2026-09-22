from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.utils.http import urlencode
from django.contrib import messages

from clientUpdates.utils.dropbox_utils import upload_to_dropbox
from .utils import process_pfas, process_annual_flow, process_max_flow, get_dashboard_data, get_all_yearly_flows
from .forms import PFASUpdateForm, AFUpdateForm, MFUpdateForm, AddNewSourceForm, HazardIndexUpdateForm
from .models import UpdatePfasResult
from clientUpdates.utils.calculations import calc_gpm_flow_rate

from django.views.decorators.cache import never_cache


@login_required
@never_cache
def landing_page(request):

    # get pwsid
    pwsid = request.user.username

    # retrieve all dashboard data for the given pwsid
    data = get_dashboard_data(pwsid)

    # Calculate total estimate
    total_estimate = sum(row.get('carrier4_est', 0) for row in data if row.get('carrier4_est') is not None)

    # Calculate number of impacted sources
    impacted_sources_count = sum(1 for row in data if not row.get('all_nds', True))

    # Calculate number of unimpacted sources
    unimpacted_sources_count = sum(1 for row in data if row.get('all_nds', True))

    return render(request, "comb_data_3mdtb/landing_page.html", {
        "data": data,
        "pwsid": pwsid,
        "total_estimate": total_estimate,
        "impacted_sources_count": impacted_sources_count,
        "unimpacted_sources_count": unimpacted_sources_count
    })


@login_required
@never_cache
def pfas_update(request):
    pwsid = request.user.username
    
    # Common logic to get min_value from process_pfas
    analyte = request.POST.get('analyte') or request.GET.get('analyte', 'PFOA')
    source_name = request.POST.get('source_name') or request.GET.get('source_name')
    
    min_value = 0
    if source_name:
        pfas_data = process_pfas(pwsid, source_name=source_name)
        if pfas_data:
            source_data = pfas_data[0]
            if analyte == "PFOA":
                min_value = source_data.get("max_pfoa") or 0
            elif analyte == "PFOS":
                min_value = source_data.get("max_pfos") or 0
            else:
                # For "Other PFAS" or specific other analytes
                # If we are in the "Other PFAS" category from landing page, 
                # we might need to be careful if multiple exist, but 
                # landing page passes the specific max_other_pfas_analyte.
                # Here we use max_other_pfas as the threshold for any 'Other' analyte update.
                min_value = source_data.get("max_other_pfas") or 0

    if request.method == "POST":
        form = PFASUpdateForm(request.POST, request.FILES, min_result=min_value)
        if form.is_valid():
            # Save form instance without committing immediately
            instance = form.save(commit=False)

            # Ensure pwsid and source_name are saved from the form (which are hidden)
            instance.pwsid = pwsid
            instance.source_name = source_name
            instance.unit = "ppt" # Standard unit for these updates

            # Map the uploaded file name to the filename field in the model
            supporting_file = request.FILES.get('supporting_file')
            if supporting_file:
                instance.filename = supporting_file.name
                upload_to_dropbox(file=supporting_file, filetype="New Claims/PFAS", pwsid=instance.pwsid)
            
            instance.save()
            messages.success(request, "Form Submitted Successfully!")
            return redirect("comb_data_3mdtb:landing_page")
        else:
            # Re-render update page with form errors
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
def hi_update(request):
    pwsid = request.user.username

    # Common logic to get min_hi from process_pfas
    source_name = request.POST.get('source_name') or request.GET.get('source_name')

    min_hi = 0
    if source_name:
        pfas_data = process_pfas(pwsid, source_name=source_name)
        if pfas_data:
            source_data = pfas_data[0]
            min_hi = source_data.get("max_hazard_index") or 0

            # Round min_hi to two decimal places
            try:
                min_hi = f"{float(min_hi):.2f}"
            except (ValueError, TypeError):
                min_hi = "0.00"

    if request.method == "POST":
        form = HazardIndexUpdateForm(request.POST, request.FILES, min_hi=min_hi)
        if form.is_valid():
            source_name = request.POST.get('source_name')

            # Map values
            analyte_map = {
                'PFHxS': form.cleaned_data['pfhxs_result'],
                'HFPO-DA': form.cleaned_data['hfpo_da_result'],
                'PFNA': form.cleaned_data['pfna_result'],
                'PFBS': form.cleaned_data['pfbs_result'],
            }

            supporting_file = request.FILES.get('supporting_file')
            if supporting_file:
                upload_to_dropbox(file=supporting_file, filetype="New Claims/PFAS", pwsid=pwsid)

            for analyte, result in analyte_map.items():
                instance = UpdatePfasResult(
                    pwsid=pwsid,
                    source_name=source_name,
                    analyte=analyte,
                    result_ppt=result,
                    lab=form.cleaned_data['lab'],
                    lab_sample_id=form.cleaned_data['lab_sample_id'],
                    analysis_method=form.cleaned_data['analysis_method'],
                    sampling_date=form.cleaned_data['sampling_date'],
                    analysis_date=form.cleaned_data['analysis_date'],
                    unit="ppt",
                    filename=supporting_file.name if supporting_file else None
                )
                instance.save()

            messages.success(request, "Hazard Index Updated Successfully!")
            return redirect("comb_data_3mdtb:landing_page")
        else:
            return render(
                request,
                "comb_data_3mdtb/hi_update.html",
                {
                    "form": form,
                    "pwsid": pwsid,
                    "source_name": source_name,
                    "min_hi": min_hi
                }
            )

    # GET request
    form = HazardIndexUpdateForm()
    return render(
        request,
        "comb_data_3mdtb/hi_update.html",
        {
            "form": form,
            "pwsid": pwsid,
            "source_name": source_name,
            "min_hi": min_hi
        }
    )


@login_required
@never_cache
def annual_flows(request):
    pwsid = request.user.username
    source_name = request.GET.get('source_name')

    # get the pfas data by source
    source_pfas_data = process_pfas(pwsid, source_name=source_name)[0]

    yearly_flows = get_all_yearly_flows(pwsid, source_name)

    return render(
        request,
        "comb_data_3mdtb/annual_flows.html",
        {
            "pwsid": pwsid,
            "source_name": source_name,
            "source_data": yearly_flows,
            "source_pfas_data": source_pfas_data,
        }
    )


@login_required
@never_cache
def af_update(request):
    pwsid = request.user.username
    if request.method == "POST":
        source_name = request.POST.get('source_name')
        year = request.POST.get('year')

        # Get existing flow rate for this year to prevent lower updates
        existing_flow_gpm = None
        if year and pwsid and source_name:
            yearly_flows = get_all_yearly_flows(pwsid, source_name)
            for flow in yearly_flows:
                if str(flow['year']) == str(year):
                    existing_flow_gpm = flow['flow_rate_gpm']
                    break

        form = AFUpdateForm(request.POST, request.FILES, existing_flow_gpm=existing_flow_gpm)
        if form.is_valid():
            instance = form.save(commit=False)
            
            supporting_file = request.FILES.get('supporting_file')
            if supporting_file:
                instance.filename = supporting_file.name
                upload_to_dropbox(file=supporting_file, filetype="New Claims/Annual Flow", pwsid=pwsid)
            
            instance.pwsid = pwsid
            instance.source_name = source_name
            instance.year = year
            instance.flow_rate_gpm = calc_gpm_flow_rate(instance.flow_rate, instance.unit.lower())
            
            instance.save()
            messages.success(request, "Form Submitted Successfully!")
            
            # Safely build the redirect URL with encoded parameters
            base_url = reverse("comb_data_3mdtb:annual_flows")
            query_string = urlencode({
                "source_name": source_name,
            })
            return redirect(f"{base_url}?{query_string}")
        else:
            return render(
                request,
                "comb_data_3mdtb/af_update.html",
                {
                    "form": form,
                    "pwsid": pwsid,
                    "source_name": source_name,
                    "year": year,
                    "existing_flow_gpm": existing_flow_gpm,
                }
            )
    
    # GET request
    source_name = request.GET.get('source_name')
    year = request.GET.get('year')

    # Get existing flow rate for this year to prevent lower updates
    existing_flow_gpm = None
    if year and pwsid and source_name:
        yearly_flows = get_all_yearly_flows(pwsid, source_name)
        for flow in yearly_flows:
            if str(flow['year']) == str(year):
                existing_flow_gpm = flow['flow_rate_gpm']
                break
    
    form = AFUpdateForm(existing_flow_gpm=existing_flow_gpm)
    return render(
        request,
        "comb_data_3mdtb/af_update.html",
        {
            "form": form,
            "pwsid": pwsid,
            "source_name": source_name,
            "year": year,
            "existing_flow_gpm": existing_flow_gpm,
        }
    )


@login_required
@never_cache
def mf_update(request):
    pwsid = request.user.username
    if request.method == "POST":
        source_name = request.POST.get('source_name')

        # Get existing max flow rate for validation in form
        existing_max_flow_gpm = None
        if pwsid and source_name:
            max_flow_data = process_max_flow(pwsid)
            for item in max_flow_data:
                if item['source_name'] == source_name:
                    existing_max_flow_gpm = item['max_flow_gpm']
                    break
        
        form = MFUpdateForm(request.POST, request.FILES, existing_max_flow_gpm=existing_max_flow_gpm)

        if form.is_valid():
            instance = form.save(commit=False)
            
            supporting_file = request.FILES.get('supporting_file')
            if supporting_file:
                instance.filename = supporting_file.name
                upload_to_dropbox(file=supporting_file, filetype="New Claims/Max Flow", pwsid=pwsid)
            
            instance.pwsid = pwsid
            instance.source_name = source_name
            instance.flow_rate_gpm = calc_gpm_flow_rate(instance.flow_rate, instance.unit.lower())
            
            instance.save()
            messages.success(request, "Form Submitted Successfully!")
            return redirect("comb_data_3mdtb:landing_page")
        else:
            return render(
                request,
                "comb_data_3mdtb/mf_update.html",
                {
                    "form": form,
                    "pwsid": pwsid,
                    "source_name": source_name,
                    "existing_max_flow_gpm": existing_max_flow_gpm,
                }
            )
    
    # GET request
    source_name = request.GET.get('source_name')
    
    # Get existing max flow rate to prevent lower updates
    existing_max_flow_gpm = None
    if pwsid and source_name:
        max_flow_data = process_max_flow(pwsid)
        for item in max_flow_data:
            if item['source_name'] == source_name:
                existing_max_flow_gpm = item['max_flow_gpm']
                break
    
    form = MFUpdateForm(existing_max_flow_gpm=existing_max_flow_gpm)
    return render(
        request,
        "comb_data_3mdtb/mf_update.html",
        {
            "form": form,
            "pwsid": pwsid,
            "source_name": source_name,
            "existing_max_flow_gpm": existing_max_flow_gpm,
        }
    )


@login_required
@never_cache
def add_source(request):
    if request.method == "POST":
        form = AddNewSourceForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            
            pwsid = request.user.username
            instance.pwsid = pwsid
            
            # Manually handle file uploads
            pfas_file_1 = request.FILES.get('pfas_file_1')
            if pfas_file_1:
                instance.filename_1 = pfas_file_1.name
                upload_to_dropbox(file=pfas_file_1, filetype="New Claims/PFAS", pwsid=pwsid)
                
            pfas_file_2 = request.FILES.get('pfas_file_2')
            if pfas_file_2:
                instance.filename_2 = pfas_file_2.name
                upload_to_dropbox(file=pfas_file_2, filetype="New Claims/PFAS", pwsid=pwsid)
                
            pfas_file_3 = request.FILES.get('pfas_file_3')
            if pfas_file_3:
                instance.filename_3 = pfas_file_3.name
                upload_to_dropbox(file=pfas_file_3, filetype="New Claims/PFAS", pwsid=pwsid)

            instance.save()
            messages.success(request, "Form Submitted Successfully!")
            return redirect("comb_data_3mdtb:landing_page")
        else:
            return render(request, "comb_data_3mdtb/add_source.html", {"form": form})
    
    form = AddNewSourceForm()
    return render(request, "comb_data_3mdtb/add_source.html", {"form": form})
