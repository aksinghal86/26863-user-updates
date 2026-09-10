from ..models import ClaimSource, ClaimPws, Phase2_ClaimPws, Phase2_ClaimSource, TB_ClaimPws, TB_ClaimSource
from django.db.models import Q

def get_phase1_sources(pwsid):

    pws_eligible = ClaimPws.objects.filter(
        pwsid=pwsid
    ).filter(
        Q(x3m_eligibility_determination__startswith="Eligible")
        | Q(dupont_eligibility_determination__startswith="Eligible")
    ).exists()

    if pws_eligible:
        sources = (ClaimSource.objects.filter(pwsid=pwsid)
                   .filter(Q(water_source_determination__startswith="Eligible"))
                   .exclude(source_name__endswith="- SUPPLEMENTAL")
                   .values('pwsid', 'pws_name', 'source_name'))
    else:
        sources = []

    return sources


def get_phase2_sources(pwsid):

    pws_eligible = Phase2_ClaimPws.objects.filter(
        pwsid=pwsid
    ).filter(
        Q(x3m_phase_ii_eligibility_determination__startswith="Eligible")
        | Q(dupont_phase_ii_eligibility_determination__startswith="Eligible")
    ).exists()

    if pws_eligible:
        # on 09/10/2026 all water_source_determination values are NULL. Keeping NULL values for now but once this is more
        # updated they should only be selected to where there are eligible sources.
        sources = (Phase2_ClaimSource.objects.filter(pwsid=pwsid)
                   .filter(Q(water_source_determination__startswith="Eligible")
                                                                 | Q(water_source_determination__isnull=True))
                   .exclude(source_name__endswith="- SUPPLEMENTAL")
                   .values('pwsid', 'pws_name', 'source_name'))
    else:
        sources = []

    return sources

def get_tb_sources(pwsid):

    pws_eligible = TB_ClaimPws.objects.filter(
        pwsid=pwsid
    ).filter(
        Q(tyco_eligibility_determination__startswith="Eligible")
        | Q(basf_eligibility_determination__startswith="Eligible")
    ).exists()

    if pws_eligible:
        sources = (TB_ClaimSource.objects.filter(pwsid=pwsid)
                   .filter(Q(water_source_determination__startswith="Eligible"))
                   .exclude(source_name__endswith="- SUPPLEMENTAL")
                   .values('pwsid', 'pws_name', 'source_name'))
    else:
        sources = []

    return sources
