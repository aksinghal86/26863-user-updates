# Custom models and forms
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache

from .models import (Pws, Source, PfasResult, FlowRate, ClaimSource, ClaimFlowRate,
                     ClaimPfasResult, paymentInfo,
                     TB_ClaimPfasResult, TB_ClaimFlowRate, supplementalSourceTracker, TB_ClaimSource,
                     pwsPaymentDist, srcPaymentDist, ClaimSubmission)
from .forms import MaxFlowRateUpdateForm, AnnualProductionForm, PfasResultUpdateForm, ContactForm

# Custom functions
from .utils.handler import handle_update
from .utils.tables_utils import add_pfoas_if_missing, get_max_other_threshold, get_latest_entries, get_combined_results
from .utils.calculations import calc_ppt_result, calc_gpm_flow_rate

# Django functions
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import JsonResponse, Http404
from itertools import chain
from datetime import datetime
from django.db.models import Q, Sum

"""JF commented out on 07/01/2025 to focus on payment dashboard, rather than update dashboard. """
# class CustomLoginView(LoginView):
#     template_name = 'login.html'
#     success_url = reverse_lazy('dashboard')
#
#     def dispatch(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             return redirect('dashboard')  # Redirect to the dashboard if the user is already logged in
#         return super().dispatch(request, *args, **kwargs)

"""JF commented out on 07/01/2025 to focus on payment dashboard, rather than update dashboard. """


# def root_redirect(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard')
#     else:
#         return redirect('login')

class CustomLoginView(LoginView):
    template_name = 'login.html'

    # Placing this in a function that overrides get_success_url... this was done because
    # sometimes it was returning an older URL (the old update dashboard)
    #success_url = reverse_lazy('payment_dashboard')
    def get_success_url(self):
        return reverse_lazy('landing_page')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('landing_page')  # Redirect to the dashboard if the user is already logged in
        return super().dispatch(request, *args, **kwargs)


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('landing_page')
    else:
        return redirect('login')


@login_required
@never_cache
def dashboard(request, claim, supplemental=0):
    # Retrieve the PWS associated with the logged-in user; otherwise, throw an error.
    pws_record = Pws.objects.get(form_userid=request.user.username)
    if not pws_record:
        raise Http404("Record not found")

    # Pull all the sources filed in the claims portal. Only select
    # those that are unimpacted (where all_nds = True)
    # sources = (Source.objects.
    #            filter(pwsid=pws_record.pwsid).
    #            filter(all_nds=True))

    if claim == "3M_DuPont":
        claim_filter = "3M/DuPont Phase 1"
    elif claim == "Tyco_BASF":
        claim_filter = "Tyco/BASF"

    sources = supplementalSourceTracker.objects.filter(pwsid=pws_record.pwsid, claim=claim_filter)
    #sources = get_list_or_404(supplementalSourceTracker, pwsid=pws_record.pwsid, claim=claim_filter)

    context = {
        'pws': pws_record,
        'sources': sources,
        'claim': claim
    }
    if supplemental:
        return render(request, 'dashboard.html', context)
    else:
        return render(request, 'dashboard_simple.html', context)


@login_required
def payment_dashboard(request, claim):
    # 10/27/2025 JF: Commenting this view function out until further notice. For now,
    # redirect to the landing page.

    # Retrieve the PWS associated with the logged-in user; otherwise, throw an error.
    pws_record = Pws.objects.get(form_userid=request.user.username)

    # if claim == "3M_DuPont":
    #     pws_payment_info = pwsPaymentDist.objects.filter(
    #         Q(pwsid=pws_record.pwsid),
    #         Q(claim_type='3M Phase 1') | Q(claim_type='Dupont Phase 1')
    #
    #     )
    #
    #     src_payment = srcPaymentDist.objects.filter(
    #         Q(pwsid=pws_record.pwsid),
    #         Q(fund_description='3M Phase One Action Fund') | Q(fund_description='Dupont Phase One Action Fund')
    #     )
    #
    #     pws_date_totals = (srcPaymentDist
    #             .objects
    #             .filter(Q(pwsid=pws_record.pwsid),
    #                     Q(fund_description='3M Phase One Action Fund') | Q(fund_description='Dupont Phase One Action Fund'))
    #             .values('payment_date', 'fund_description')
    #             .annotate(total=Sum('payment_amount')))
    #
    #
    #     pws_total = (srcPaymentDist
    #             .objects
    #             .filter(Q(pwsid=pws_record.pwsid),
    #                     Q(fund_description='3M Phase One Action Fund') | Q(fund_description='Dupont Phase One Action Fund'))
    #             .aggregate(total=Sum('payment_amount')))
    #
    #     context = {
    #         'pws': pws_record,
    #         'pws_payment_info': pws_payment_info,
    #         #'src_payment_dist': src_payment,
    #         'pws_date_totals': pws_date_totals,
    #         'pws_total': pws_total,
    #         'claim': claim
    #     }
    #
    # # there are currently no Tyco/BASF payments to process
    # else:
    #     context = {
    #         'pws': pws_record,
    #         'claim': claim
    #     }
    #
    # return render(request, 'payment_dashboard2.html', context)

    return render(request, 'landing_page.html')


@login_required
def supplemental_info(request):
    return render(request, 'supplemental_info.html')


@login_required
def source_payment_info(request, claim):
    # Retrieve the PWS associated with the logged-in user; otherwise, throw an error.
    pws_record = Pws.objects.get(form_userid=request.user.username)

    if claim == "3M_DuPont":
        src_payment = srcPaymentDist.objects.filter(
            Q(pwsid=pws_record.pwsid),
            Q(fund_description='3M Phase One Action Fund') | Q(fund_description='Dupont Phase One Action Fund')
        )

        context = {
            'pws': pws_record,
            'src_payment_dist': src_payment,
            'claim': claim
        }

    return render(request, 'source_payment_info.html', context)


@login_required
def payment_details(request):
    # Retrieve the PWS associated with the logged-in user; otherwise, throw an error.
    pws_record = Pws.objects.get(form_userid=request.user.username)

    payment_info = paymentInfo.objects.get(pwsid=pws_record.pwsid)

    #dist_info = paymentDistributions.objects.get(pwsid=)

    context = {
        'pws': pws_record,
        'paymentInfo': payment_info
    }

    return render(request, 'payment_details.html', context)


@login_required
def landing_page(request):
    # Retrieve the PWS associated with the logged-in user; otherwise, throw an error.
    try:

        pws_submitted_claim = ClaimSubmission.objects.get(pwsid=request.user.username)
        pws_record = Pws.objects.get(form_userid=request.user.username)

        context = {
            'pws': pws_record,
        }

        return render(request, 'landing_page.html', context)
    # exception handling for if the query in the above try statement returns nothing.
    except ClaimSubmission.DoesNotExist:

        context = {
            'pws': request.user.username,
        }

        return render(request, 'no_data_landing_page.html', context)








@login_required
def source_detail_view(request, claim, pwsid, source_name):
    if claim == "3M_DuPont":
        source = get_object_or_404(ClaimSource, pwsid=pwsid, source_name=source_name)
        pfas_results = ClaimPfasResult.objects.filter(pwsid=pwsid, source_name=source_name).exclude(
            analyte__isnull=True)
        flow_data = ClaimFlowRate.objects.filter(pwsid=pwsid, source_name=source_name)

    if claim == "Tyco_BASF":
        source = get_object_or_404(TB_ClaimSource, pwsid=pwsid, source_name=source_name)
        pfas_results = TB_ClaimPfasResult.objects.filter(pwsid=pwsid, source_name=source_name).exclude(
            analyte__isnull=True)
        flow_data = TB_ClaimFlowRate.objects.filter(pwsid=pwsid, source_name=source_name)

    pfas_results = list(pfas_results.values())
    for i in pfas_results:
        print(i['analyte'])

    #pfas_results = add_pfoas_if_missing(pfas_results, source.pwsid, source.water_source_id, source.source_name)
    pfas_results = sorted(pfas_results, key=lambda x: x['analyte'], reverse=True)

    flow_data = list(flow_data.values())
    max_flow_rate = next((fr for fr in flow_data if fr['year'] is None), None)
    max_gpm = max_flow_rate.get('flow_rate_gpm') or 0
    max_flow_rate.update({
        'flow_rate_gpy': max_gpm * 1440 * 365,
        'flow_rate_mgd': max_gpm * 1440 / 1_000_000,
        'flow_rate_afpy': max_gpm * 1440 * 365 / 325851,
    })

    annuals = [fr for fr in flow_data if fr['year'] is not None]
    for annual in annuals:
        gpm = annual.get('flow_rate_gpm') or 0
        annual['flow_rate_gpm'] = gpm  # overwrite None with 0
        annual['flow_rate_gpy'] = gpm * 1440 * 365
        annual['flow_rate_afpy'] = gpm * 1440 * 365 / 325_851

    impacted = True if not source.all_nds or pfas_results else False

    context = {
        'source': source,
        'impacted': impacted,
        'max_flow_rate': max_flow_rate,
        'annuals': annuals,
        'pfas_results': pfas_results,
        'claim': claim
    }

    return render(request, 'source_detail.html', context)


#
# @login_required
# def source_detail_view(request, claim, pwsid, source_name):
#     claim_source = get_object_or_404(ClaimSource, pwsid=pwsid, source_name=source_name)
#
#     #### PFAS Results ####
#     columns = ['pwsid', 'water_source_id', 'source_name', 'analyte', 'result_ppt', 'sampling_date', 'analysis_date', 'lab_sample_id', 'data_origin']
#     claim_pfas_results = ClaimPfasResult.objects.filter(pwsid=claim_source.pwsid, source_name=source_name).exclude(analyte__isnull=True)
#
#     updated_pfas_results = Phase1PFASUpdates.objects.filter(pwsid=claim_source.pwsid, source_name=source_name, updated_by_water_provider=True)
#     latest_pfas_results = get_latest_entries(updated_pfas_results)
#     combined_pfas_results = get_combined_results(claim_pfas_results, latest_pfas_results, columns)
#
#     claim_analytes = {entry.analyte for entry in claim_pfas_results}
#     ehe_analytes = {entry.analyte for entry in latest_pfas_results}
#     all_analytes = claim_analytes.union(ehe_analytes)
#
#     combined_pfas_results = []
#
#     for analyte in all_analytes:
#         # Get the latest entry for this analyte from PfasResult
#         latest_pfas_result = next((entry for entry in latest_pfas_results if entry.analyte == analyte), None)
#
#         # Get the entry for this analyte from ClaimPfasResult
#         claim_pfas_result = next((entry for entry in claim_pfas_results if entry.analyte == analyte), None)
#
#         # Lower bound always comes from ClaimPfasResult if it exists
#         lower_bound = claim_pfas_result.result_ppt if claim_pfas_result else 0
#         combined_pfas_results.append({
#             'pwsid': claim_source.pwsid,
#             # 'water_source_id': latest_pfas_result.water_source_id if latest_pfas_result else (claim_pfas_result.water_source_id if claim_pfas_result else None),
#             'source_name': source_name,
#             'analyte': analyte,
#             'lower_bound': lower_bound,
#             'result_ppt': latest_pfas_result.result_ppt if latest_pfas_result else (claim_pfas_result.result_ppt if claim_pfas_result else 0),
#             'sampling_date': latest_pfas_result.sampling_date if latest_pfas_result else (claim_pfas_result.sampling_date if claim_pfas_result else None),
#             'analysis_date': latest_pfas_result.analysis_date if latest_pfas_result else (claim_pfas_result.analysis_date if claim_pfas_result else None),
#             'analysis_method': latest_pfas_result.analysis_method if latest_pfas_result else (claim_pfas_result.analysis_method if claim_pfas_result else None),
#             'lab_sample_id': latest_pfas_result.lab_sample_id if latest_pfas_result else (claim_pfas_result.lab_sample_id if claim_pfas_result else None),
#             'filename': latest_pfas_result.filename if latest_pfas_result else (claim_pfas_result.filename if claim_pfas_result else None),
#             'updated': True if latest_pfas_result else False,
#             'data_origin': latest_pfas_result.data_origin if latest_pfas_result else ('Placeholder' if not claim_pfas_result else claim_pfas_result.data_origin),
#         })
#
#     pfas_results = add_pfoas_if_missing(combined_pfas_results, claim_source.pwsid, claim_source.water_source_id, claim_source.source_name)
#     pfas_results = sorted(pfas_results, key=lambda x: x['analyte'], reverse=True)
#     max_other_threshold = get_max_other_threshold(pfas_results)
#
#     impacted = True if not claim_source.all_nds or updated_pfas_results else False
#
#     #### Max Flow Rate and Annuals ####
#     columns_flow = ['pwsid', 'water_source_id', 'source_name', 'source_variable', 'year', 'flow_rate', 'unit', 'flow_rate_gpm', 'data_origin']
#     claim_flow_rates = ClaimFlowRate.objects.filter(pwsid=claim_source.pwsid, source_name=source_name)
#
#     # JF - change from FlowRate class to Phase1FlowUpdates
#     updated_flow_rates = Phase1FlowUpdates.objects.filter(pwsid=claim_source.pwsid, source_name=source_name, updated_by_water_provider=True)
#     latest_max_flow = get_latest_entries(updated_flow_rates, source_variable='VFR')
#     latest_annuals = get_latest_entries(updated_flow_rates, source_variable='AFR')
#     latest_flow_rates = list(chain(latest_max_flow, latest_annuals))
#
#     years_to_process = list(range(2013, 2023)) + [None] # None for max flow rate
#
#     combined_flow_rates = []
#     # Process each year once
#     for year in years_to_process:
#         latest_flow_rate = next((fr for fr in latest_flow_rates if fr.year == year), None)
#         claim_flow_rate = next((cf for cf in claim_flow_rates if cf.year == year), None)
#
#         # Lower bound from ClaimFlowRate
#         lower_bound = claim_flow_rate.flow_rate_gpm if claim_flow_rate else 0
#
#         # Append combined entry
#         combined_flow_rates.append({
#             'pwsid': claim_source.pwsid,
#             # 'water_source_id': latest_flow_rate.water_source_id if latest_flow_rate else (claim_flow_rate.water_source_id if claim_flow_rate else None),
#             'source_name': source_name,
#             'year': year,
#             'source_variable': latest_flow_rate.source_variable if latest_flow_rate else (claim_flow_rate.source_variable if claim_flow_rate else 'AFR'),
#             'flow_rate': latest_flow_rate.flow_rate if latest_flow_rate else (claim_flow_rate.flow_rate if claim_flow_rate else 0),
#             'unit': latest_flow_rate.unit if latest_flow_rate else (claim_flow_rate.unit if claim_flow_rate else 'GPY'),
#             'flow_rate_gpm': latest_flow_rate.flow_rate_gpm if latest_flow_rate else (claim_flow_rate.flow_rate_gpm if claim_flow_rate else 0),
#             'flow_rate_gpy': ((latest_flow_rate.flow_rate_gpm if latest_flow_rate else (claim_flow_rate.flow_rate_gpm if claim_flow_rate else 0)) * 1440 * 365),
#             'flow_rate_mgd': ((latest_flow_rate.flow_rate_gpm if latest_flow_rate else (claim_flow_rate.flow_rate_gpm if claim_flow_rate else 0)) * 1440 / 1_000_000),
#             'flow_rate_afpy': ((latest_flow_rate.flow_rate_gpm if latest_flow_rate else (claim_flow_rate.flow_rate_gpm if claim_flow_rate else 0)) * 1440 * 365 / 325851),
#             'lower_bound': lower_bound,  # Always from ClaimFlowRate
#             'filename': latest_flow_rate.filename if latest_flow_rate else (claim_flow_rate.filename if claim_flow_rate else None),
#             'updated': True if latest_flow_rate else False,
#             'data_origin': latest_flow_rate.data_origin if latest_flow_rate else ('Placeholder' if not claim_flow_rate else claim_flow_rate.data_origin),
#         })
#
#     max_flow_rate = next((fr for fr in combined_flow_rates if fr['year'] is None), None)
#     annuals = [fr for fr in combined_flow_rates if fr['year'] is not None]
#
#     # Prepare context for rendering
#     context = {
#         'claim_source': claim_source,
#         'impacted': impacted,
#         'max_flow_rate': max_flow_rate,
#         'annuals': annuals,
#         'pfas_results': pfas_results,
#         'max_other_threshold': max_other_threshold
#     }
#
#     return render(request, 'source_detail.html', context)

@login_required
def update_pfas_result_view(request):
    def calc_pfas_fields(instance, cleaned_data):
        instance.result = float(cleaned_data['result'])
        instance.unit = cleaned_data['unit']
        instance.result_ppt = calc_ppt_result(instance.result, instance.unit)

    return handle_update(
        request,
        form_class=PfasResultUpdateForm,
        extra_fields={
            'analyte': 'analyte',
            'sampling_date': 'sampling_date',
            'analysis_date': 'analysis_date',
            'lab': 'lab',
            'analysis_method': 'analysis_method',
            'lab_sample_id': 'lab_sample_id',
            'comments': 'comments'
        },
        calc_func=calc_pfas_fields,
        source_variable=None
    )


@login_required
def update_max_flow_rate_view(request):
    def calc_max_flow_rate_fields(instance, cleaned_data):
        instance.flow_rate = cleaned_data['flow_rate']
        instance.unit = cleaned_data['unit']
        instance.flow_rate_gpm = calc_gpm_flow_rate(instance.flow_rate, instance.unit)

    return handle_update(
        request,
        form_class=MaxFlowRateUpdateForm,
        extra_fields={
            'comments': 'comments'
        },
        calc_func=calc_max_flow_rate_fields,
        source_variable='VFR'
    )


@login_required
def update_annual_production_view(request):
    def calc_annual_production_fields(instance, cleaned_data):
        instance.flow_rate = cleaned_data['flow_rate']
        instance.unit = cleaned_data['unit']
        instance.flow_rate_gpm = calc_gpm_flow_rate(instance.flow_rate, instance.unit)
        instance.year = cleaned_data['year']

    return handle_update(
        request,
        form_class=AnnualProductionForm,
        extra_fields={
            'flow_rate_reduced': 'flow_rate_reduced',
            'comments': 'comments'
        },
        calc_func=calc_annual_production_fields,
        source_variable='AFR'
    )


# @login_required
# def contact_view(request, source_name=None, message=0):
#     pwsid = request.user.username
#     recipients = settings.EMAIL_RECIPIENTS
#
#     if request.method == 'POST':
#         form = ContactForm(request.POST)
#
#         if form.is_valid():
#             name = form.cleaned_data['name']
#             email = form.cleaned_data['email']
#             subject = form.cleaned_data['subject']
#             message = form.cleaned_data['message']
#             full_message = f"From: {name}\n\n{message}"
#
#             email_message = EmailMessage(
#                 subject=f"{subject} (from {pwsid})",
#                 body=full_message,
#                 from_email=settings.EMAIL_HOST_USER,
#                 to=recipients,
#                 reply_to=[email],
#             )
#             email_message.send(fail_silently=False)
#
#             # Return a JSON response for AJAX
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({'message': 'Email sent successfully.'})
#
#             return render(request, 'dashboard.html')
#
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 return JsonResponse({'error': 'Invalid form submission'}, status=400)
#
#     else:
#         form = ContactForm()
#
#     return render(request, 'contact.html', {'form': form})


@login_required
def contact_view(request, claim=None, source_name=None, message=0):
    pwsid = request.user.username
    recipients = settings.EMAIL_RECIPIENTS

    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            full_message = f"From: {name}\n\n{message}"

            email_message = EmailMessage(
                subject=f"{subject} (from {pwsid})",
                body=full_message,
                from_email=settings.EMAIL_HOST_USER,
                to=recipients,
                reply_to=[email],
            )

            email_message.send(fail_silently=False)
            messages.success(request, "This is a test!")

            # Return a JSON response for AJAX.
            # if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            #     return JsonResponse({'message': 'Email sent successfully.'})

            # if this is a user filling out a regular contact form, unrelated to supplemental funds:
            if claim is None:
                return render(request, 'dashboard.html')

            # otherwise...:
            else:

                if claim == "3M_DuPont":
                    claim_filter = "3M/DuPont Phase 1"
                elif claim == "Tyco_BASF":
                    claim_filter = "Tyco/BASF"

                # update supplemental fund information for the source:
                source = get_object_or_404(supplementalSourceTracker, pwsid=pwsid, source_name=source_name,
                                           claim=claim_filter)

                source.sup_notif_sent = True
                source.notif_datetime = timezone.now()
                source.sup_status = "Claim Under Review"
                source.save()

                return redirect('dashboard', claim=claim, supplemental=1)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid form submission'}, status=400)

    else:
        if source_name is not None and message == 1:
            message = "I would like to inquire about submitting a Supplemental Fund Claim for the source referenced in the subject line."

        form = ContactForm()

    return render(request, 'contact.html', {'form': form,
                                            'source_name': source_name,
                                            'message': message,
                                            'pwsid': pwsid,
                                            'claim': claim})

@login_required
def no_data_contact_view(request):
    pwsid = request.user.username
    recipients = settings.EMAIL_RECIPIENTS

    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            full_message = f"From: {name}\n\n{message}"

            email_message = EmailMessage(
                subject=f"{subject} (from {pwsid})",
                body=full_message,
                from_email=settings.EMAIL_HOST_USER,
                to=recipients,
                reply_to=[email],
            )

            email_message.send(fail_silently=False)
            messages.success(request, "This is a test!")

            return render(request, 'no_data_landing_page.html')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid form submission'}, status=400)

    else:
        form = ContactForm()

    return render(request, 'no_data_contact.html', {'form': form,'pwsid': pwsid})



@login_required
def activity_view(request):
    pwsid = request.user.username

    pfas_results = PfasResult.objects.filter(pwsid=pwsid).values(
        'submit_date', 'source_name', 'analyte', 'result_ppt'
    )

    # Format PFAS log entries
    pfas_logs = [
        {
            'time': result['submit_date'],
            'source_name': result['source_name'],
            'table_name': 'PFAS Result',
            'change': f"{result['analyte']} value changed to {result['result_ppt']} ng/L",
        }
        for result in pfas_results
    ]

    # Retrieve flow rate changes
    flow_rates = FlowRate.objects.filter(pwsid=pwsid).values(
        'submit_date', 'source_name', 'source_variable', 'year', 'flow_rate', 'unit'
    )

    # Format flow rate log entries
    flow_logs = [
        {
            'time': flow['submit_date'],
            'source_name': flow['source_name'],
            'table_name': 'Flow Rate',
            'source_variable': flow['source_variable'],  # Keep the original value for logic
            'change': f"{'Annual Production for ' + str(int(flow['year'])) if flow['source_variable'] == 'AFR' else 'Max Flow Rate'} changed to {flow['flow_rate']} {flow['unit']}",
        }
        for flow in flow_rates
    ]

    # Combine and sort logs
    activity_logs = sorted(chain(pfas_logs, flow_logs), key=lambda x: x['time'], reverse=True)

    # Pass logs to template
    return render(request, 'activity.html', {'activity_logs': activity_logs})


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect(f"{settings.LOGIN_URL}")
