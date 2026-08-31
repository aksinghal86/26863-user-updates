from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .utils import process_pfas, process_annual_flow, get_dashboard_data

from django.views.decorators.cache import never_cache


@login_required
@never_cache
def landing_page(request):

    # get pwsid
    pwsid = request.user.username

    # retrieve all dashboard data for the given pwsid
    data = get_dashboard_data(pwsid)

    return render(request, "comb_data_3mdtb/landing_page.html", {"data": data})