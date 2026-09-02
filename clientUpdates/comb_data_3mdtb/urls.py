from django.urls import path
from . import views

app_name = "comb_data_3mdtb"

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
    path("pfas_update/", views.pfas_update, name="pfas_update"),
    path("annual_flows/", views.annual_flows, name="annual_flows"),
    path("af_update/", views.af_update, name="af_update"),
    path("mf_update/", views.mf_update, name="mf_update"),
]
