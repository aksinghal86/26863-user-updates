from .models import Pws, ClaimPws
from .utils.data_cleaning import get_phase1_sources, get_tb_sources, get_phase2_sources
import logging

logger = logging.getLogger('clientUpdates')

def info_bar_context(request):
    if request.user.is_authenticated:
        try:
            pws_record = Pws.objects.get(form_userid=request.user.username)
            claim_pws_record = ClaimPws.objects.get(pwsid=pws_record.pwsid)

            return {
                'pws': pws_record,
                'claim_pws': claim_pws_record,
            }
        except (Pws.DoesNotExist, ClaimPws.DoesNotExist):
            #logger.info("Pws or ClaimPws record does not exist.")
            return {}
    return {}

def claim_status_context(request):
    if request.user.is_authenticated:
        pwsid = request.user.username
        has_phase1_claim = bool(get_phase1_sources(pwsid))
        has_tb_claim = bool(get_tb_sources(pwsid))
        has_phase2_claim = bool(get_phase2_sources(pwsid))
        
        return {
            'has_phase1_claim': has_phase1_claim,
            'has_tb_claim': has_tb_claim,
            'has_phase2_claim': has_phase2_claim,
        }
    return {
        'has_phase1_claim': False,
        'has_tb_claim': False,
        'has_phase2_claim': False,
    }