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
            # Handle valid form (save to database)
            form.save()
            return redirect("comb_data_3mdtb:landing_page")
        else:
            # Re-render landing page with form errors
            pwsid = request.user.username
            data = get_dashboard_data(pwsid)
            return render(
                request,
                "comb_data_3mdtb/landing_page.html",
                {
                    "data": data,
                    "form": form,
                    "show_modal": True
                }
            )
    return redirect("comb_data_3mdtb:landing_page")
