from django.contrib.auth.models import AbstractUser
from django.db import models


## DJANGO user ##
class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


## PWS level tables ##
class Pws(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    pwsid = models.CharField(max_length=9, unique=True, blank=False, null=False)
    gfe_3m = models.FloatField(db_column='gfe_3M', blank=True, null=True)  # Field name made lowercase.
    gfe_dupont = models.FloatField(db_column='gfe_Dupont', blank=True, null=True)  # Field name made lowercase.
    gfe_total = models.FloatField(blank=True, null=True)
    gfe_basf = models.FloatField(db_column='gfe_BASF', blank=True, null=True)  # Field name made lowercase.
    gfe_tyco = models.FloatField(blank=True, null=True)
    gfe_total_basf_tyco = models.FloatField(blank=True, null=True)
    submit_date = models.DateTimeField(blank=True, null=True)
    pws_name = models.TextField(blank=True, null=True)
    test_ucmr5 = models.BooleanField(blank=True, null=True)
    test_state = models.BooleanField(blank=True, null=True)
    conn15 = models.BooleanField(blank=True, null=True)
    residents25 = models.BooleanField(blank=True, null=True)
    x3m_3300 = models.BooleanField(blank=True, null=True)
    dupont_3300 = models.BooleanField(blank=True, null=True)
    usa = models.BooleanField(blank=True, null=True)
    ownedbygov = models.BooleanField(blank=True, null=True)
    pws_sdwis_code = models.TextField(blank=True, null=True)
    sdwis_p_type = models.TextField(blank=True, null=True)
    sdwis_sf_sue = models.TextField(blank=True, null=True)
    sdwis_activity_code = models.TextField(blank=True, null=True)
    pws_source_count_gw_count = models.TextField(blank=True, null=True)
    pws_source_count_sw_count = models.TextField(blank=True, null=True)
    pws_source_count_other_count = models.TextField(blank=True, null=True)
    pws_3m_june = models.BooleanField(blank=True, null=True)
    pws_dupont_june = models.BooleanField(blank=True, null=True)
    eurofins_permissions = models.BooleanField(blank=True, null=True)
    estimate_made = models.BooleanField(blank=True, null=True)
    estimate_documents_estimate_doc1 = models.TextField(blank=True, null=True)
    pws_comment = models.TextField(blank=True, null=True)
    ehe_password = models.TextField(blank=True, null=True)
    special_needs = models.TextField(blank=True, null=True)
    form_type = models.TextField(blank=True, null=True)
    workbook_completeness = models.TextField(blank=True, null=True)
    phase_3d = models.TextField(blank=True, null=True)
    phase_tb = models.TextField(blank=True, null=True)
    sl_client_number = models.FloatField(blank=True, null=True)
    pws_group = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    retention_date = models.DateTimeField(blank=True, null=True)
    litigation_filing_date = models.DateTimeField(blank=True, null=True)
    signature_group = models.TextField(blank=True, null=True)
    firm = models.TextField(blank=True, null=True)
    firm_contact_name = models.TextField(blank=True, null=True)
    firm_email = models.TextField(blank=True, null=True)
    workbook_sent_date = models.DateTimeField(blank=True, null=True)
    firm_email_to_client_date = models.DateTimeField(blank=True, null=True)
    ehe_letter_sent_date = models.TextField(blank=True, null=True)
    form_userid = models.TextField(blank=True, null=True)
    form_pw = models.TextField(blank=True, null=True)
    gs_version_control = models.TextField(blank=True, null=True)
    data_entry_status = models.TextField(blank=True, null=True)
    #gfe_requests = models.TextField(blank=True, null=True)
    #gfe_estimate_basis = models.TextField(blank=True, null=True)
    #gfe_already_provided_by_firm = models.TextField(blank=True, null=True)
    form_entry_started = models.TextField(blank=True, null=True)
    #gfe_ready = models.BooleanField(blank=True, null=True)
    final_opt_decision = models.TextField(blank=True, null=True)
    doc_letter = models.TextField(blank=True, null=True)
    letter_group = models.TextField(blank=True, null=True)
    total_in_group = models.IntegerField(blank=True, null=True)
    firm_clean = models.TextField(blank=True, null=True)
    pws_ein = models.TextField(blank=True, null=True)
    pfas_qc = models.BooleanField(blank=True, null=True)
    production_qc = models.BooleanField(blank=True, null=True)
    baseline_qc = models.BooleanField(blank=True, null=True)
    date_reviewed = models.DateField(blank=True, null=True)
    data_origin = models.TextField(blank=True, null=True)

    # JF 07/02/2025: Adding new columns to PWS class
    abs_3m = models.FloatField(blank=True, null=True)
    abs_dupont = models.FloatField(blank=True, null=True)
    gfe_3m_original = models.FloatField(blank=True, null=True)
    gfe_dupont_original = models.FloatField(blank=True, null=True)
    allocation_3m = models.FloatField(blank=True, null=True)
    allocation_dupont = models.FloatField(blank=True, null=True)

    #pfas_files_associated = models.FloatField(blank=True, null=True)
    #n_x = models.IntegerField(db_column='n.x', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    #pct_pfas_associated = models.FloatField(blank=True, null=True)
    #n_pfas_files_rcvd = models.IntegerField(blank=True, null=True)
    #prod_files_associated = models.FloatField(blank=True, null=True)
    #n_y = models.IntegerField(db_column='n.y', blank=True, null=True)  # Field renamed to remove unsuitable characters.
    #pct_prod_associated = models.FloatField(blank=True, null=True)
    #n_prod_files_rcvd = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'pws'


class PwsAddress(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    pwsid = models.CharField(max_length=9, unique=False, blank=False, null=False)
    address = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    address_type = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'pws_address'


class PwsContact(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    pwsid = models.CharField(max_length=9, unique=False, blank=False, null=False)
    contact_name = models.TextField(blank=True, null=True)
    contact_title = models.TextField(blank=True, null=True)
    contact_phone = models.TextField(blank=True, null=True)
    contact_cell = models.TextField(blank=True, null=True)
    contact_email = models.TextField(blank=True, null=True)
    contact_generalemail = models.TextField(blank=True, null=True)
    contact_type = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'pws_contact'


## Source level tables ##
class Source(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    water_source_id = models.BigIntegerField(blank=True, null=True)
    submit_date = models.DateTimeField(blank=True, null=True)
    pwsid = models.CharField(max_length=9, unique=False, blank=False, null=False)
    form_id = models.TextField(blank=True, null=True)
    sample_id = models.TextField(blank=True, null=True)
    source_type_other = models.TextField(blank=True, null=True)
    pws_owns_source = models.BooleanField(blank=True, null=True)
    pws_operates_source = models.BooleanField(blank=True, null=True)
    pws_purchased = models.BooleanField(blank=True, null=True)
    pws_drinking_water = models.BooleanField(blank=True, null=True)
    flow_provided = models.BooleanField(blank=True, null=True)
    no_flow_why = models.TextField(blank=True, null=True)
    provide_flow_future = models.BooleanField(blank=True, null=True)
    flow_2022_flow_rate_reduced_pfas = models.BooleanField(blank=True, null=True)
    pfas_results_available = models.BooleanField(blank=True, null=True)
    no_pfas_why = models.TextField(blank=True, null=True)
    provide_pfas_future = models.BooleanField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    include_form = models.BooleanField(blank=True, null=True)
    form_type = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    sample_id_from = models.TextField(blank=True, null=True)
    source_type = models.TextField(blank=True, null=True)
    source_status = models.TextField(blank=True, null=True)
    testing_recommendation = models.TextField(blank=True, null=True)
    testing_status = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    include_sampling_loc = models.BooleanField(blank=True, null=True)
    file_source = models.BooleanField(blank=True, null=True)
    gswc_comments = models.TextField(blank=True, null=True)
    system_gswc = models.TextField(blank=True, null=True)
    gswc_loc = models.TextField(blank=True, null=True)
    afr = models.FloatField(blank=True, null=True)
    ehe_afr_note = models.TextField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    pfas_score = models.FloatField(blank=True, null=True)
    pfas_score_method = models.TextField(blank=True, null=True)
    reg_bump = models.BooleanField(blank=True, null=True)
    all_nds = models.BooleanField(blank=True, null=True)
    hi_candidate = models.BooleanField(blank=True, null=True)
    ma6_candidate = models.BooleanField(blank=True, null=True)
    base_score = models.FloatField(blank=True, null=True)
    gfe_3m = models.FloatField(db_column='gfe_3M', blank=True, null=True)  # Field name made lowercase.
    gfe_dupont = models.FloatField(db_column='gfe_Dupont', blank=True, null=True)  # Field name made lowercase.
    gfe_total = models.FloatField(blank=True, null=True)
    gfe_basf = models.FloatField(db_column='gfe_BASF', blank=True, null=True)  # Field name made lowercase.
    gfe_tyco = models.FloatField(blank=True, null=True)
    gfe_total_basf_tyco = models.FloatField(blank=True, null=True)
    data_origin = models.TextField(blank=True, null=True)
    abs_3m = models.FloatField(blank=True, null=True)
    abs_dupont = models.FloatField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'source'


class FlowRate(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    water_source_id = models.BigIntegerField(blank=True, null=True)
    submit_date = models.DateTimeField(blank=True, null=True)
    pwsid = models.CharField(max_length=9, unique=False, blank=False, null=False)
    sample_id = models.TextField(blank=True, null=True)
    year = models.FloatField(blank=True, null=True)
    flow_rate = models.FloatField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    flow_rate_reduced = models.BooleanField(blank=True, null=True)
    source_variable = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    method = models.TextField(blank=True, null=True)
    flow_rate_gpm = models.FloatField(blank=True, null=True)
    flag = models.BooleanField(blank=True, null=True)
    ehe_comments = models.TextField(blank=True, null=True)
    system_gswc = models.TextField(blank=True, null=True)
    gswc_loc = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    sample_id_from = models.TextField(blank=True, null=True)
    filename = models.FileField(upload_to='uploads/', blank=True, null=True)
    dms_initials = models.TextField(blank=True, null=True)
    rm_row = models.FloatField(blank=True, null=True)
    qc_flag = models.TextField(blank=True, null=True)
    updated_by_water_provider = models.BooleanField(default=False)
    data_origin = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'flow_rate'

class PfasResult(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    water_source_id = models.BigIntegerField(blank=True, null=True)
    submit_date = models.DateTimeField(blank=True, null=True)
    pwsid = models.CharField(max_length=9, unique=False, blank=False, null=False)
    sample_id = models.TextField(blank=True, null=True)
    sampling_date = models.DateField(blank=True, null=True)
    analyte = models.TextField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    detected = models.BooleanField(blank=True, null=True)
    result_ppt = models.FloatField(blank=True, null=True)
    flag = models.BooleanField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    qc_flag = models.TextField(blank=True, null=True)
    analysis_method = models.TextField(blank=True, null=True)
    lab_sample_id = models.TextField(blank=True, null=True)
    lab = models.TextField(blank=True, null=True)
    cas_number = models.TextField(blank=True, null=True)
    mdl = models.FloatField(blank=True, null=True)
    rl = models.FloatField(blank=True, null=True)
    filename = models.FileField(upload_to='uploads/', blank=True, null=True)
    analysis_date = models.DateField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    dms_initials = models.TextField(blank=True, null=True)
    all_nds = models.BooleanField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    sample_id_from = models.TextField(blank=True, null=True)
    updated_by_water_provider = models.BooleanField(default=False)
    data_origin = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'pfas_result'


## Filenames ##
class ProductionDataFilenames(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    firm = models.TextField(blank=True, null=True)
    file_path = models.TextField(blank=True, null=True)
    client_group = models.TextField(blank=True, null=True)
    pwsid = models.CharField(max_length=9, unique=False, blank=False, null=False)
    pws_name = models.TextField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    cat = models.TextField(blank=True, null=True)
    results_cat = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'production_data_filenames'


class EurofinsReportsFilenames(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    excel_name = models.TextField(blank=True, null=True)
    eurofins_id = models.TextField(blank=True, null=True)
    pdf_name = models.TextField(blank=True, null=True)
    pwsid = models.CharField(max_length=9, unique=False, blank=False, null=False)
    file_path = models.TextField(blank=True, null=True)
    cat = models.TextField(blank=True, null=True)
    results_cat = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'eurofins_reports_filenames'


class PfasReportsFilenames(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    firm = models.TextField(blank=True, null=True)
    file_path = models.TextField(blank=True, null=True)
    client_group = models.TextField(blank=True, null=True)
    pwsid = models.CharField(max_length=9, unique=False, blank=False, null=False)
    pws_name = models.TextField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    cat = models.TextField(blank=True, null=True)
    results_cat = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'pfas_reports_filenames'


class DropboxLinks(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    pwsid = models.TextField(blank=True, null=True)
    url_file_request = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dropbox_links'


## Claims portal tables ##
class ClaimDocumentInfo(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    pwsid = models.TextField(blank=True, null=True)
    water_system_id = models.FloatField(blank=True, null=True)
    water_system_name = models.TextField(blank=True, null=True)
    object_type_attached_to = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    law_firm_3rd_party_representative = models.TextField(blank=True, null=True)
    test_result_date = models.DateField(blank=True, null=True)
    entity_document_file_id = models.FloatField(blank=True, null=True)
    entity_document_id = models.FloatField(blank=True, null=True)
    doc_reference = models.TextField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    file_size = models.TextField(blank=True, null=True)
    document_purpose = models.TextField(blank=True, null=True)
    date_uploaded = models.DateField(blank=True, null=True)
    content_type = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    data_origin = models.TextField(default="Claims Portal")

    class Meta:
        managed = True
        db_table = 'claim_document_info'


class ClaimFlowRate(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    claim_number = models.FloatField(blank=True, null=True)
    pwsid = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    water_source_id = models.FloatField(blank=True, null=True)
    year = models.FloatField(blank=True, null=True)
    flow_rate_reduced = models.BooleanField(blank=True, null=True)
    did_not_exist = models.BooleanField(blank=True, null=True)
    flow_rate = models.FloatField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    flow_rate_gpm = models.FloatField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    source_variable = models.TextField(blank=True, null=True)
    max_flow_rate_explanation = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    data_origin = models.TextField(default="Claims Portal")

    class Meta:
        managed = True
        db_table = 'claim_flow_rate'


class ClaimPfasResult(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    pwsid = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    claim_number = models.FloatField(blank=True, null=True)
    water_source_id = models.TextField(blank=True, null=True)
    analyte = models.TextField(blank=True, null=True)
    result_ppt = models.FloatField(blank=True, null=True)
    lab_sample_id = models.TextField(blank=True, null=True)
    doc_reference = models.TextField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    sampling_date = models.DateField(blank=True, null=True)
    company_of_person_who_took_sample = models.TextField(blank=True, null=True)
    analysis_date = models.DateField(blank=True, null=True)
    analysis_method = models.TextField(blank=True, null=True)
    lab = models.TextField(blank=True, null=True)
    lab_street_address = models.TextField(blank=True, null=True)
    lab_city = models.TextField(blank=True, null=True)
    lab_state = models.TextField(blank=True, null=True)
    lab_zip = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    data_origin = models.TextField(default="Claims Portal")
    all_nds = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'claim_pfas_result'


class ClaimPws(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    claim_number = models.FloatField(blank=True, null=True)
    pwsid = models.TextField(blank=True, null=True)
    pws_name = models.TextField(blank=True, null=True)
    law_firm_3rd_party_representative = models.TextField(blank=True, null=True)
    certification_cst_3m = models.TextField(blank=True, null=True)
    certification_cst_dupont = models.TextField(blank=True, null=True)
    certification_hst_3m = models.TextField(blank=True, null=True)
    certification_hst_dupont = models.TextField(blank=True, null=True)
    postmark_date_3m = models.FloatField(blank=True, null=True)
    postmark_date_dupont = models.FloatField(blank=True, null=True)
    not_participating_3m = models.TextField(blank=True, null=True)
    not_participating_dupont = models.FloatField(blank=True, null=True)
    claim_status = models.TextField(blank=True, null=True)
    cc_a_is_3m = models.BooleanField(blank=True, null=True)
    cc_b_active_and_needs_testing_3m = models.BooleanField(blank=True, null=True)
    cc_c_is_dupont = models.BooleanField(blank=True, null=True)
    cc_d_active_and_needs_testing_dupont = models.BooleanField(blank=True, null=True)
    address_1 = models.TextField(blank=True, null=True)
    address_2 = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zip = models.TextField(blank=True, null=True)
    entity_lookup = models.TextField(blank=True, null=True)
    pws_w9_filename = models.TextField(blank=True, null=True)
    has_lawsuit = models.BooleanField(blank=True, null=True)
    has_lawsuit_pending_mdl = models.BooleanField(blank=True, null=True)
    lawsuit_court_name = models.TextField(blank=True, null=True)
    lawsuit_case_number = models.TextField(blank=True, null=True)
    litigation_filing_date = models.TextField(blank=True, null=True)
    complaint_petition_filename = models.TextField(blank=True, null=True)
    has_attorney_representation = models.BooleanField(blank=True, null=True)
    test_ucmr = models.BooleanField(blank=True, null=True)
    test_state = models.BooleanField(blank=True, null=True)
    conn15 = models.BooleanField(blank=True, null=True)
    residents25 = models.BooleanField(blank=True, null=True)
    fewer_than_3300_people = models.BooleanField(blank=True, null=True)
    usa = models.BooleanField(blank=True, null=True)
    ownedbygov = models.BooleanField(blank=True, null=True)
    pws_sdwis_code = models.TextField(blank=True, null=True)
    sdwis_sf_sue = models.BooleanField(blank=True, null=True)
    sdwis_p_type = models.TextField(blank=True, null=True)
    pws_facility_activity_code = models.TextField(blank=True, null=True)
    sdwis_activity_code = models.TextField(blank=True, null=True)
    total_ground_sources = models.TextField(blank=True, null=True)
    total_ground_sources_tested_with_pfas = models.BooleanField(blank=True, null=True)
    total_ground_sources_ucmr5_tested_with_pfas = models.BooleanField(blank=True, null=True)
    total_ground_sources_tested_without_pfas = models.BooleanField(blank=True, null=True)
    total_ground_sources_ucmr5_tested_without_pfas = models.BooleanField(blank=True, null=True)
    total_sw_sources = models.TextField(blank=True, null=True)
    total_sw_sources_tested_with_pfas = models.BooleanField(blank=True, null=True)
    total_sw_sources_ucmr5_tested_with_pfas = models.BooleanField(blank=True, null=True)
    total_sw_sources_tested_without_pfas = models.BooleanField(blank=True, null=True)
    total_sw_sources_ucmr5_tested_without_pfas = models.BooleanField(blank=True, null=True)
    has_other_sources = models.BooleanField(blank=True, null=True)
    other_sources_description = models.TextField(blank=True, null=True)
    total_other_sources = models.TextField(blank=True, null=True)
    total_other_sources_tested_with_pfas = models.BooleanField(blank=True, null=True)
    total_other_sources_ucmr5_tested_with_pfas = models.BooleanField(blank=True, null=True)
    total_other_sources_tested_without_pfas = models.BooleanField(blank=True, null=True)
    total_other_sources_ucmr5_tested_without_pfas = models.BooleanField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    in_consortium = models.BooleanField(blank=True, null=True)
    data_origin = models.TextField(default="Claims Portal")

    class Meta:
        managed = True
        db_table = 'claim_pws'


class ClaimSource(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    claim_number = models.FloatField(blank=True, null=True)
    pwsid = models.TextField(blank=True, null=True)
    pws_name = models.TextField(blank=True, null=True)
    water_source_id = models.FloatField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    is_part_of_idws = models.BooleanField(blank=True, null=True)
    is_idws_cooperating = models.BooleanField(blank=True, null=True)
    is_idws_responsible_pfas = models.BooleanField(blank=True, null=True)
    partner_name = models.TextField(blank=True, null=True)
    partner_pwsid = models.TextField(blank=True, null=True)
    idws_partner_relationship = models.TextField(blank=True, null=True)
    claimed_share_percent = models.FloatField(blank=True, null=True)
    source_type = models.TextField(blank=True, null=True)
    source_type_other = models.TextField(blank=True, null=True)
    pws_owns_source = models.BooleanField(blank=True, null=True)
    source_co_owned = models.BooleanField(blank=True, null=True)
    pws_operates_source = models.BooleanField(blank=True, null=True)
    source_operated_by = models.BooleanField(blank=True, null=True)
    pws_purchased = models.BooleanField(blank=True, null=True)
    source_original_pwsid = models.TextField(blank=True, null=True)
    pws_drinking_water = models.BooleanField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    data_origin = models.TextField(default="Claims Portal")
    all_nds = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'claim_source'


class paymentInfo(models.Model):
    #row_names = models.BigAutoField(primary_key=True)
    pwsid = models.TextField(null=False, primary_key=True)
    pws_name = models.TextField(blank=True, null=True)
    entity_name = models.TextField(blank=True, null=True)
    claim_number = models.IntegerField(blank=True, null=True)
    payment_method = models.TextField(blank=True, null=True)
    verification_name = models.TextField(blank=True, null=True)
    verification_email = models.TextField(blank=True, null=True)
    verification_number = models.TextField(blank=True, null=True)
    wire_account_name = models.TextField(blank=True, null=True)
    wire_account_number = models.TextField(blank=True, null=True)
    wire_routing_number = models.TextField(blank=True, null=True)
    wire_further_credit = models.TextField(blank=True, null=True)
    wire_client_address = models.TextField(blank=True, null=True)
    wire_client_city = models.TextField(blank=True, null=True)
    wire_client_state = models.TextField(blank=True, null=True)
    wire_client_zip = models.TextField(blank=True, null=True)
    wire_bank_name = models.TextField(blank=True, null=True)
    wire_bank_address = models.TextField(blank=True, null=True)
    wire_bank_city = models.TextField(blank=True, null=True)
    wire_bank_state = models.TextField(blank=True, null=True)
    wire_bank_zip = models.TextField(blank=True, null=True)
    check_payee_name = models.TextField(blank=True, null=True)
    check_addressed_to = models.TextField(blank=True, null=True)
    check_street_address = models.TextField(blank=True, null=True)
    check_city = models.TextField(blank=True, null=True)
    check_state = models.TextField(blank=True, null=True)
    check_zip = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'payment_information'

class TB_ClaimPfasResult(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    pwsid = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    claim_number = models.FloatField(blank=True, null=True)
    water_source_id = models.TextField(blank=True, null=True)
    water_source_determination = models.TextField(blank=True, null=True)
    analyte = models.TextField(blank=True, null=True)
    result_ppt = models.FloatField(blank=True, null=True)
    lab_sample_id = models.TextField(blank=True, null=True)
    doc_reference = models.TextField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    result = models.TextField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    sampling_date = models.DateField(blank=True, null=True)
    company_of_person_who_took_sample = models.TextField(blank=True, null=True)
    analysis_date = models.DateField(blank=True, null=True)
    analysis_method = models.TextField(blank=True, null=True)
    lab = models.TextField(blank=True, null=True)
    lab_street_address = models.TextField(blank=True, null=True)
    lab_city = models.TextField(blank=True, null=True)
    lab_state = models.TextField(blank=True, null=True)
    lab_zip = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    data_origin = models.TextField(default="Claims Portal")
    all_nds = models.BooleanField(blank=True, null=True)
    in_consortium = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'claim_tb_pfas_result'


class TB_ClaimFlowRate(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    claim_number = models.FloatField(blank=True, null=True)
    pwsid = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    water_source_id = models.FloatField(blank=True, null=True)
    year = models.FloatField(blank=True, null=True)
    flow_rate_reduced = models.BooleanField(blank=True, null=True)
    did_not_exist = models.BooleanField(blank=True, null=True)
    flow_rate = models.FloatField(blank=True, null=True)
    unit = models.TextField(blank=True, null=True)
    flow_rate_gpm = models.FloatField(blank=True, null=True)
    filename = models.TextField(blank=True, null=True)
    source_variable = models.TextField(blank=True, null=True)
    max_flow_rate_explanation = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    data_origin = models.TextField(default="Claims Portal")
    in_consortium = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'claim_tb_flow_rate'


class supplementalSourceTracker(models.Model):
    id = models.IntegerField(primary_key=True)
    claim = models.TextField(blank=True, null=True)
    pwsid = models.TextField(blank=True, null=True)
    pws_name = models.TextField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    all_nds = models.BooleanField(blank=True, null=True)
    reg_bump = models.BooleanField(blank=True, null=True)
    sup_notif_sent = models.BooleanField(blank=True, null=True)
    notif_datetime = models.DateTimeField(blank=True, null=True)
    sup_status = models.TextField(blank=True, null=True)
    completion_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'supplemental_fund_source_tracker'

class TB_ClaimSource(models.Model):
    row_names = models.BigAutoField(primary_key=True)
    claim_number = models.FloatField(blank=True, null=True)
    pwsid = models.TextField(blank=True, null=True)
    pws_name = models.TextField(blank=True, null=True)
    needs_recalculation = models.TextField(blank=True, null=True)
    water_source_id = models.FloatField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    water_source_determination = models.FloatField(blank=True, null=True)
    source_type = models.TextField(blank=True, null=True)
    source_type_other = models.TextField(blank=True, null=True)
    pws_owns_source = models.BooleanField(blank=True, null=True)
    source_co_owned = models.BooleanField(blank=True, null=True)
    pws_operates_source = models.BooleanField(blank=True, null=True)
    source_operated_by = models.BooleanField(blank=True, null=True)
    pws_purchased = models.BooleanField(blank=True, null=True)
    source_original_pwsid = models.TextField(blank=True, null=True)
    pws_drinking_water = models.BooleanField(blank=True, null=True)
    is_part_of_idws = models.BooleanField(blank=True, null=True)
    is_idws_cooperating = models.BooleanField(blank=True, null=True)
    is_idws_responsible_pfas = models.BooleanField(blank=True, null=True)
    partner_name = models.TextField(blank=True, null=True)
    partner_pwsid = models.TextField(blank=True, null=True)
    idws_partner_relationship = models.TextField(blank=True, null=True)
    claimed_share_percent = models.FloatField(blank=True, null=True)
    all_nds = models.BooleanField(default=False)
    in_consortium = models.BooleanField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    data_origin = models.TextField(default="Claims Portal")


    class Meta:
        managed = True
        db_table = 'claim_tb_source'

class pwsPaymentDist(models.Model):
    id = models.IntegerField(primary_key=True)
    claim_id = models.IntegerField(blank=True, null=True)
    pwsid = models.TextField(blank=True, null=True)
    pws_name = models.TextField(blank=True, null=True)
    law_firm = models.TextField(blank=True, null=True)
    entity_name = models.TextField(blank=True, null=True)
    claim_type = models.TextField(blank=True, null=True)
    current_pws_total_abs = models.FloatField(blank=True, null=True)
    projected_net_dollars_per_abs_point_value = models.FloatField(blank=True, null=True)
    anticipated_total_net_settlement_award = models.FloatField(blank=True, null=True)
    actual_paid = models.FloatField(blank=True, null=True)
    remaining_balance = models.FloatField(blank=True, null=True)
    remaining_balance_per_abs_pt = models.FloatField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'pws_payment_dist'


class srcPaymentDist(models.Model):
    id = models.IntegerField(primary_key=True)
    fund_description = models.TextField(blank=True, null=True)
    batch_id = models.IntegerField(blank=True, null=True)
    batch_name = models.TextField(blank=True, null=True)
    claim_id = models.IntegerField(blank=True, null=True)
    pwsid = models.TextField(blank=True, null=True)
    pws_name = models.TextField(blank=True, null=True)
    water_source_id = models.BigIntegerField(blank=True, null=True)
    source_name = models.TextField(blank=True, null=True)
    law_firm_id = models.IntegerField(blank=True, null=True)
    law_firm = models.TextField(blank=True, null=True)
    entity_id = models.IntegerField(blank=True, null=True)
    entity_name = models.TextField(blank=True, null=True)
    recipient_name = models.TextField(blank=True, null=True)
    batch_adjusted_base_score = models.TextField(blank=True, null=True)
    batch_dollars_per_abs_points = models.TextField(blank=True, null=True)
    payment_amount = models.FloatField(blank=True, null=True)
    payment_id = models.IntegerField(blank=True, null=True)
    payment_method = models.TextField(blank=True, null=True)
    total_transaction_value = models.FloatField(blank=True, null=True)
    payment_date = models.DateField(blank=True, null=True)


    class Meta:
        managed = True
        db_table = 'source_payment_dist'

class ClaimSubmission(models.Model):
    id = models.BigAutoField(primary_key=True)
    pwsid = models.TextField(blank=True, null=True)
    x3m_dupont_claim = models.BooleanField(blank=True, null=True)
    tyco_basf_claim = models.BooleanField(blank=True, null=True)
    any_claim_submission = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'claim_submissions'