from django.urls import path
from . import views

app_name = "comb_data_3mdtb"

urlpatterns = [
    path("", views.landing_page, name="landing_page"),
]
