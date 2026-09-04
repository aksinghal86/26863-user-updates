from django.db import models

from clientUpdates.models import ClaimPfasResult, TB_ClaimPfasResult, ClaimFlowRate, TB_ClaimFlowRate, Phase2_ClaimFlowRate, Phase2_ClaimPfasResult

# Create your models here.
class UpdatePfasResult(models.Model):
    id = models.BigAutoField(primary_key=True)
    pwsid = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    lab = models.TextField(blank=True, null=True)
    lab_sample_id = models.TextField(blank=True, null=True)
    analysis_method = models.TextField(blank=True, null=True)
    sampling_date = models.DateField(blank=True, null=True)
    analysis_date = models.DateField(blank=True, null=True)
    analyte = models.TextField(blank=True, null=True)
    result_ppt = models.FloatField(blank=True, null=True)
    sample_collected_by = models.TextField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    data_origin = models.TextField(default="EHE Portal")
    submit_date = models.DateTimeField(auto_now=True)



    class Meta:
        managed = True
        db_table = 'update_pfas_result'


class UpdateFlowRate(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    pwsid = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    year = models.FloatField(blank=True, null=True)
    flow_rate = models.FloatField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    flow_rate_gpm = models.FloatField(blank=True, null=True)
    flow_rate_reduced = models.BooleanField(default=False)
    existed = models.BooleanField(default=True)
    filename = models.TextField(blank=True, null=True)
    data_origin = models.TextField(default="EHE Portal")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'update_flow_rate'


class UpdateMaxFlowRate(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    pwsid = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    flow_rate = models.FloatField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    flow_rate_gpm = models.FloatField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    data_origin = models.TextField(default="EHE Portal")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'update_max_flow_rate'