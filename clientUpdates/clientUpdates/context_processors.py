from clientUpdates.models import Pws, ClaimPws
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
            logger.warning("Pws or ClaimPws record does not exist.")
            return {}
    return {}