from .calculations import calc_pfas_score_and_method, calc_afr_and_note, calc_gfes, calc_base_score
from .tables_utils import get_latest_entries, get_combined_results, get_max_results_by_analyte, get_max_annuals_by_year, get_max_entry
#from ..models import Pws, Source, PfasResult, FlowRate, ClaimSource, ClaimPfasResult, ClaimFlowRate
#from clientUpdates import modePws, Source, PfasResult, FlowRate, ClaimSource, ClaimPfasResult, ClaimFlowRate
from django.db.models import Sum
from django.utils import timezone

def update_pfas_metrics(pwsid, source_name):
    """
    Update the PFAS score, method, all_nds status, and regulatory bump for a given PWSID and source name.

    Combines ClaimPfasResult and the latest entries from PfasResult to calculate the PFAS score and determine 
    the regulatory bump based on thresholds.

    Arguments:
        - pwsid: The PWSID to filter by.
        - source_name: The source name to filter by.

    Updates:
        - The Source model with:
            - all_nds status
            - regulatory bump flag
            - PFAS score
            - PFAS score method
    """
    # Fetch ClaimSource
    claim_source = ClaimSource.objects.filter(pwsid=pwsid, source_name=source_name).first()
    if not claim_source:
        print(f"No Claim Source found for pwsid: {pwsid}, source_name: {source_name}")
        return

    # Fetch ClaimPfasResult and PfasResult
    claim_pfas_results = ClaimPfasResult.objects.filter(
        pwsid=pwsid, source_name=source_name
    ).exclude(analyte__isnull=True)

    updated_pfas_results = PfasResult.objects.filter(
        pwsid=pwsid, source_name=source_name, updated_by_water_provider=True
    )

    # Get latest results, combine, and determine max results
    latest_pfas_results = get_latest_entries(updated_pfas_results)
    combined_pfas_results = get_combined_results(claim_pfas_results, latest_pfas_results, ['analyte', 'result_ppt'])
    max_pfas_results = get_max_results_by_analyte(combined_pfas_results)

    # Extract PFOA, PFOS, and other results
    pfoa_result = next((result['result_ppt'] for result in max_pfas_results if result['analyte'] == 'PFOA'), 0)
    pfos_result = next((result['result_ppt'] for result in max_pfas_results if result['analyte'] == 'PFOS'), 0)
    other_results = [result['result_ppt'] for result in max_pfas_results if result['analyte'] not in ['PFOA', 'PFOS']]
    max_other_result = max(other_results, default=0)

    # Calculate the PFAS score and method
    pfas_score, pfas_score_method = calc_pfas_score_and_method(pfoa_result, pfos_result, max_other_result)

    # Determine all_nds status
    all_nds = pfas_score == 0

    # Determine Regulatory Bump
    REG_BUMP_THRESHOLD = 4
    reg_bump = pfoa_result >= REG_BUMP_THRESHOLD or pfos_result >= REG_BUMP_THRESHOLD

    # Update the Source model with the calculated metrics
    Source.objects.filter(pwsid=pwsid, source_name=source_name).update(
        submit_date=timezone.now(),
        all_nds=all_nds,
        reg_bump=reg_bump,
        pfas_score=pfas_score,
        pfas_score_method=pfas_score_method, 
        data_origin = 'EHE Update Portal'
    )



def update_flow_rate_metrics(pwsid, source_name): 
    """
    Updates flow rate metrics for a given PWSID and source name.

    Calculates maximum annual production by year and maximum VFR.
    """

    # Fetch ClaimSource
    claim_source = ClaimSource.objects.filter(pwsid=pwsid, source_name=source_name).first()
    if not claim_source:
        print(f"No Claim Source found for pwsid: {pwsid}, source_name: {source_name}")
        return

    # Fetch and combine AFR data
    claim_annuals = ClaimFlowRate.objects.filter(pwsid=pwsid, source_name=source_name, source_variable='AFR').exclude(year=2013)
    updated_annuals = FlowRate.objects.filter(pwsid=pwsid, source_name=source_name, source_variable='AFR', updated_by_water_provider = True).exclude(year=2013)
    latest_annuals = get_latest_entries(updated_annuals, source_variable='AFR')
    combined_annuals = get_combined_results(claim_annuals, latest_annuals, ['year', 'flow_rate_gpm'])
    max_annuals = get_max_annuals_by_year(combined_annuals)
    
    # Fetch and combine VFR data
    claim_vfr = ClaimFlowRate.objects.filter(pwsid=pwsid, source_name=source_name, source_variable='VFR')
    updated_vfr = FlowRate.objects.filter(pwsid=pwsid, source_name=source_name, source_variable='VFR', updated_by_water_provider = True)
    latest_vfr = get_latest_entries(updated_vfr, source_variable='VFR')
    combined_vfr = get_combined_results(claim_vfr, latest_vfr, ['flow_rate_gpm'])
    max_vfr_entry = get_max_entry(combined_vfr, 'flow_rate_gpm')
    max_vfr = max_vfr_entry.get('flow_rate_gpm', 0) if max_vfr_entry else None
    
    afr, ehe_afr_note = calc_afr_and_note(max_annuals, max_vfr)

    Source.objects.filter(pwsid=pwsid, source_name=source_name).update(
        submit_date=timezone.now(),
        afr=afr,
        ehe_afr_note=ehe_afr_note, 
        data_origin = 'EHE Update Portal'
    )


def update_base_scores(pwsid, source_name):
    """
    Update Base Score for a given PWSID and source name. 

    Args:
        pwsid: The PWSID for the source.
        source_name: The name of the source.

    Updates the Source model with:
        - Base Score (base_score)
    """
    # Fetch the Source object
    source = Source.objects.filter(pwsid=pwsid, source_name=source_name).first()

    if source:
        base_score = calc_base_score(source.pfas_score, source.afr)
        source.base_score = base_score
        # Eventually also update adjusted base score, which will take into account regulatory bump, lit bump
        source.save()
    else: 
        print(f"No Source found for pwsid: {pwsid}, source_name: {source_name}")
        return


def update_gfes(pwsid, source_name):
    """
    Update GFEs for a given PWSID and source name.

    Args:
        pwsid: The PWSID for the source.
        source_name: The name of the source.

    Updates the Source model with:
        - GFE for Tyco (gfe_tyco)
        - GFE for BASF (gfe_basf)
        - Total GFE for both (gfe_total_basf_tyco)
    """
    # Fetch the Source object
    source = Source.objects.filter(pwsid=pwsid, source_name=source_name).first()
    
    if source: 
        # Calculate GFE for Tyco and BASF
        gfe_tyco = calc_gfes(source.pfas_score, source.afr, 'Tyco')
        gfe_basf = calc_gfes(source.pfas_score, source.afr, 'BASF')
        gfe_total_basf_tyco = gfe_tyco + gfe_basf

        source.gfe_tyco = gfe_tyco
        source.gfe_basf = gfe_basf
        source.gfe_total_basf_tyco = gfe_total_basf_tyco
        source.save()
    else: 
        print(f"No Source found for pwsid: {pwsid}, source_name: {source_name}")
        return


def update_ehe_source_table(pwsid, source_name):
    """
    Update the EH&E source table for the given PWSID and source name.

    This function:
    - Updates PFAS metrics.
    - Updates flow rate metrics.
    - Updates GFE metrics.

    Args:
        pwsid: The PWSID for the source.
        source_name: The name of the source.

    Returns:
        None
    """
    try:
        update_pfas_metrics(pwsid, source_name)
        print(f"PFAS metrics updated successfully for PWSID: {pwsid}, Source: {source_name}")
    except Exception as e:
        print(f"Failed to update PFAS metrics for PWSID: {pwsid}, Source: {source_name}. Error: {e}")

    try:
        update_flow_rate_metrics(pwsid, source_name)
        print(f"Flow rate metrics updated successfully for PWSID: {pwsid}, Source: {source_name}")
    except Exception as e:
        print(f"Failed to update flow rate metrics for PWSID: {pwsid}, Source: {source_name}. Error: {e}")

    try: 
        update_base_scores(pwsid, source_name)
        print(f"Base Score updated successfully for PWSID: {pwsid}, Source: {source_name}")
    except Exception as e:
        print(f"Failed to update Base Score in Source table for PWSID: {pwsid}, Source: {source_name}. Error: {e}")

    try:
        update_gfes(pwsid, source_name)
        print(f"GFEs updated successfully for PWSID: {pwsid}, Source: {source_name}")
    except Exception as e:
        print(f"Failed to update GFEs in Source table for PWSID: {pwsid}, Source: {source_name}. Error: {e}")




def update_ehe_pws_table(pwsid):
    """
    Update the Pws table with aggregated GFE values (gfe_tyco, gfe_basf, and their total)
    for all sources associated with the given PWSID.

    Args:
        pwsid: The PWSID for which to update the Pws table.
    """
    # Aggregate GFE values from all sources related to the PWSID
    gfe_sums = Source.objects.filter(pwsid=pwsid).aggregate(
        total_gfe_tyco=Sum('gfe_tyco'),
        total_gfe_basf=Sum('gfe_basf')
    )

    # Calculate the total GFE for Tyco and BASF
    total_gfe_tyco = gfe_sums.get('total_gfe_tyco') or 0
    total_gfe_basf = gfe_sums.get('total_gfe_basf') or 0
    total_gfe_basf_tyco = total_gfe_tyco + total_gfe_basf

    # Update the Pws table with the aggregated values
    try:
        Pws.objects.filter(pwsid=pwsid).update(
            submit_date=timezone.now(),
            gfe_tyco=total_gfe_tyco,
            gfe_basf=total_gfe_basf,
            gfe_total_basf_tyco=total_gfe_basf_tyco, 
            data_origin = 'EHE Update Portal'
        )
        print(f"GFEs updated successfully in the Pws table")
    except Exception as e:
        print(f"Failed to update GFEs in Pws table for PWSID: {pwsid}. Error: {e}")
    