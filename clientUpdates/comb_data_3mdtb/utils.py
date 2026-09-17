from clientUpdates.utils.calculations import calc_capital_costs, calc_pfas_score_and_method, calc_base_score, \
    calc_adj_base_score
from clientUpdates.utils.data_cleaning import get_phase1_sources, get_tb_sources, get_phase2_sources, remove_sup_suffix
from .models import ClaimPfasResult, TB_ClaimPfasResult, ClaimFlowRate, TB_ClaimFlowRate, Phase2_ClaimFlowRate, \
    Phase2_ClaimPfasResult, UpdatePfasResult, UpdateAnnualFlowRate, UpdateMaxFlowRate

# a function that returns eligible sources for each claim. E.g., if sources in Phase 1 were considered
# inelgible, they would not appear in the phase1_source_names list. These lists include sources
# that filed a supplemental fund claim.
def get_eligible_sources(pwsid):

    phase1_source_names = [s["source_name"] for s in get_phase1_sources(pwsid)]

    tb_source_names = [s["source_name"] for s in get_tb_sources(pwsid)]

    phase2_source_names = [s["source_name"] for s in get_phase2_sources(pwsid)]

    return phase1_source_names, tb_source_names, phase2_source_names


def process_pfas(pwsid):

    # Fields we want from each PFAS model
    fields = [
        "pwsid",
        "source_name",
        "analyte",
        "result_ppt",
        "sampling_date"
    ]

    # get eligible sources by claim
    phase1_source_names, tb_source_names, phase2_source_names = get_eligible_sources(pwsid)


    # Get PFAS records for this PWSID from the first model
    data1 = ClaimPfasResult.objects.filter(
        pwsid=pwsid,
        source_name__in=phase1_source_names
    ).values(*fields)

    # remove supplemental suffix from source names
    data1 = remove_sup_suffix(data1)

    # Get PFAS records for this PWSID from the second model
    data2 = TB_ClaimPfasResult.objects.filter(
        pwsid=pwsid,
        source_name__in=tb_source_names
    ).values(*fields)

    # remove supplemental suffix from source names
    data2 = remove_sup_suffix(data2)

    # Get PFAS records for this PWSID from the third model
    data3 = Phase2_ClaimPfasResult.objects.filter(
        pwsid=pwsid,
        source_name__in=phase2_source_names
    ).values(*fields)

    # remove supplemental suffix from source names
    data3 = remove_sup_suffix(data3)

    # Get any updates made to PFAS results
    data4 = list(UpdatePfasResult.objects.filter(
        pwsid=pwsid
    ).values(*fields))

    # Combine records from all models
    data = list(data1) + list(data2) + list(data3) + data4

    # Dictionary to store the results for each water source
    sources = {}

    # Group records by (pwsid, source_name, sampling_date) for Hazard Index calculation
    samples = {}

    # Process each PFAS record
    for record in data:

        # Use PWSID + source name to uniquely identify the source
        key = (
            record["pwsid"],
            record["source_name"]
        )

        # Create a new entry for a source the first time we see it
        if key not in sources:
            sources[key] = {
                "pwsid": record["pwsid"],
                "source_name": record["source_name"],
                "max_pfoa": None,
                "max_pfos": None,
                "max_other_pfas": None,

                # <-- CHANGE: Store the analyte associated
                # with the maximum Other PFAS result
                "max_other_pfas_analyte": None,
                "max_hazard_index": None
            }

        # Track results by sampling date for Hazard Index
        if record["sampling_date"]:
            sample_key = (record["pwsid"], record["source_name"], record["sampling_date"])
            if sample_key not in samples:
                samples[sample_key] = {}
            
            # If multiple results for same analyte on same date, take max
            current_val = samples[sample_key].get(record["analyte"])
            if current_val is None or record["result_ppt"] > current_val:
                samples[sample_key][record["analyte"]] = record["result_ppt"]

        # Get the PFAS result
        result = record["result_ppt"]

        # Ignore missing or zero results
        if result is None or result == 0:
            continue

        # If PFOA, keep the highest PFOA result for this source
        if record["analyte"] == "PFOA":

            sources[key]["max_pfoa"] = max(
                sources[key]["max_pfoa"] or result,
                result
            )

        # If PFOS, keep the highest PFOS result for this source
        elif record["analyte"] == "PFOS":

            sources[key]["max_pfos"] = max(
                sources[key]["max_pfos"] or result,
                result
            )

        # For all other analytes, keep the highest result
        else:

            # <-- CHANGE: Instead of only updating the maximum
            # value, update the value AND its associated analyte
            if (
                sources[key]["max_other_pfas"] is None
                or result > sources[key]["max_other_pfas"]
            ):
                sources[key]["max_other_pfas"] = result
                sources[key]["max_other_pfas_analyte"] = record["analyte"]

    # Calculate Hazard Index for each sample
    # Formula: HI = [PFHxS]/9 + [HFPO-DA]/10 + [PFNA]/10 + [PFBS]/2000
    for (pwsid, source_name, sampling_date), analytes in samples.items():
        key = (pwsid, source_name)
        
        pfhxs = analytes.get("PFHxS", 0)
        hfpo_da = analytes.get("HFPO-DA", analytes.get("GenX", 0))
        pfna = analytes.get("PFNA", 0)
        pfbs = analytes.get("PFBS", 0)
        
        hi = (pfhxs / 9.0) + (hfpo_da / 10.0) + (pfna / 10.0) + (pfbs / 2000.0)
        
        if hi > 0:
            if sources[key]["max_hazard_index"] is None or hi > sources[key]["max_hazard_index"]:
                sources[key]["max_hazard_index"] = hi

    # Determine whether each source has any reported PFAS result
    for source in sources.values():

        # If none of the PFAS categories have a result,
        # all_nds is True. Otherwise, it is False.
        source["all_nds"] = (
            source["max_pfoa"] is None
            and source["max_pfos"] is None
            and source["max_other_pfas"] is None
        )

    return list(sources.values())

def process_annual_flow(pwsid):
    fields = [
        "pwsid",
        "source_name",
        "year",
        "flow_rate_gpm",
    ]

    # get eligible sources by claim
    phase1_source_names, tb_source_names, phase2_source_names = get_eligible_sources(pwsid)


    # Get historical data from all three models.
    claim_data = ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_name__in=phase1_source_names,
        source_variable="AFR",
    ).values(*fields)

    # remove supplemental suffix from source names
    claim_data = remove_sup_suffix(claim_data)

    tb_claim_data = TB_ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_name__in=tb_source_names,
        source_variable="AFR",
    ).values(*fields)

    # remove supplemental suffix from source names
    tb_claim_data = remove_sup_suffix(tb_claim_data)

    phase2_claim_data = Phase2_ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_name__in=phase2_source_names,
        source_variable="AFR",
    ).values(*fields)

    # remove supplemental suffix from source names
    phase2_claim_data = remove_sup_suffix(phase2_claim_data)

    af_updates = list(UpdateAnnualFlowRate.objects.filter(
        pwsid=pwsid
    ).values(*fields))

    # Add data from all three models.
    all_data = claim_data + tb_claim_data + phase2_claim_data + af_updates

    # Store data by (pwsid, source_name).
    sources = {}

    for record in all_data:
        key = (record["pwsid"], record["source_name"])
        year = record["year"]
        flow_rate = record["flow_rate_gpm"]

        # Create the source if it doesn't exist yet.
        sources.setdefault(key, {})

        # Only use flow rates that have a value.
        if flow_rate is not None:

            # If multiple models have data for the same
            # pwsid/source_name/year, keep the highest value.
            if (
                    year not in sources[key]
                    or flow_rate > sources[key][year]
            ):
                sources[key][year] = flow_rate

    results = []

    # Process each pwsid/source_name combination
    for (pwsid, source_name), yearly_data in sources.items():

        # Add 2024 and 2025 with no data for now.
        # These will eventually come from the new model.
        yearly_data.setdefault(2024, None)
        yearly_data.setdefault(2025, None)

        # Create a list of years that have flow rate data.
        # Years with no data (None) are left out.
        valid_years = [
            {
                "year": year,
                "gpm": flow_rate,
            }
            for year, flow_rate in yearly_data.items()
            if flow_rate is not None
        ]

        # Sort the years by flow rate, highest to lowest.
        # This puts the highest-producing years first.
        valid_years.sort(
            key=lambda item: item["gpm"],
            reverse=True,
        )

        # Take the three highest years.
        highest_three = valid_years[:3]

        # Calculate average GPM for the three highest years.
        if highest_three:
            average_gpm = (
                    sum(item["gpm"] for item in highest_three)
                    / len(highest_three)
            )
        else:
            average_gpm = 0

        # Convert GPM to GPY.
        average_gpy = average_gpm * 60 * 24 * 365

        # Check if there are at least three years of non-zero flow rates.
        # Ensure we only count non-None and non-zero values.
        has_three_years_non_zero = sum(1 for item in valid_years if item.get("gpm") and item["gpm"] > 0) >= 3

        results.append({
            "pwsid": pwsid,
            "source_name": source_name,
            "highest_three_years": highest_three,
            "average_annual_production_gpm": average_gpm,
            "average_annual_production_gpy": average_gpy,
            "has_three_years_non_zero": has_three_years_non_zero,
        })

    return results

def process_max_flow(pwsid):
    fields = [
        "pwsid",
        "source_name",
        "flow_rate_gpm",
    ]

    # get eligible sources by claim
    phase1_source_names, tb_source_names, phase2_source_names = get_eligible_sources(pwsid)

    # Get max flow data from all three models.
    claim_data = ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_name__in=phase1_source_names,
        source_variable="VFR",
    ).values(*fields)

    # remove supplemental suffix from source names
    claim_data = remove_sup_suffix(claim_data)

    tb_claim_data = TB_ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_name__in=tb_source_names,
        source_variable="VFR",
    ).values(*fields)

    # remove supplemental suffix from source names
    tb_claim_data = remove_sup_suffix(tb_claim_data)

    phase2_claim_data = Phase2_ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_name__in=phase2_source_names,
        source_variable="VFR",
    ).values(*fields)

    # remove supplemental suffix from source names
    phase2_claim_data = remove_sup_suffix(phase2_claim_data)

    mf_updates = list(UpdateMaxFlowRate.objects.filter(
        pwsid=pwsid
    ).values(*fields))

    # Store data by (pwsid, source_name).
    sources = {}

    # Add data from all three models.
    all_data = claim_data + tb_claim_data + phase2_claim_data + mf_updates

    for record in all_data:
        key = (record["pwsid"], record["source_name"])
        flow_rate = record["flow_rate_gpm"]

        # Create the source if it doesn't exist yet.
        sources.setdefault(key, None)

        # Only use flow rates that have a value.
        if flow_rate is not None:

            # If multiple models have data for the same
            # pwsid/source_name, keep the highest value.
            if (
                sources[key] is None
                or flow_rate > sources[key]
            ):
                sources[key] = flow_rate

    results = []

    # Process each pwsid/source_name combination.
    for (pwsid, source_name), max_flow_gpm in sources.items():

        results.append({
            "pwsid": pwsid,
            "source_name": source_name,
            "max_flow_gpm": max_flow_gpm,
        })

    return results


def get_dashboard_data(pwsid):

    # Get PFAS data and organize it by pwsid/source_name.
    pfas_data = {
        (item["pwsid"], item["source_name"]): item
        for item in process_pfas(pwsid)
    }

    # Get annual flow data and organize it by pwsid/source_name.
    annual_flow = {
        (item["pwsid"], item["source_name"]): item
        for item in process_annual_flow(pwsid)
    }

    # Get max flow data and organize it by pwsid/source_name.
    max_flow = {
        (item["pwsid"], item["source_name"]): item
        for item in process_max_flow(pwsid)
    }

    results = []

    # Get all unique pwsid/source_name combinations
    # found in any of the three datasets.
    all_sources = set(annual_flow) | set(max_flow) | set(pfas_data)

    # Process each unique pwsid/source_name combination.
    for key in all_sources:
        pwsid, source_name = key

        # Get the data for this source from each dataset.
        # Use an empty dictionary if the source has no data.
        annual = annual_flow.get(key, {})
        maximum = max_flow.get(key, {})
        pfas = pfas_data.get(key, {})

        # Calculate the Average Flow Rate (AFR).
        # (average annual flow rate in gpm + max flow rate in gpm) / 2
        avg_annual_gpm = annual.get("average_annual_production_gpm", 0)
        max_flow_gpm = maximum.get("max_flow_gpm", 0)

        # Convert None to 0 for calculation.
        avg_annual_gpm = avg_annual_gpm if avg_annual_gpm is not None else 0
        max_flow_gpm = max_flow_gpm if max_flow_gpm is not None else 0

        afr = (avg_annual_gpm + max_flow_gpm) / 2

        # Get PFAS Score
        pfoa = pfas.get("max_pfoa") if pfas.get("max_pfoa") is not None else 0
        pfos = pfas.get("max_pfos") if pfas.get("max_pfos") is not None else 0
        other_pfas = pfas.get("max_other_pfas") if pfas.get("max_other_pfas") is not None else 0

        pfas_score, _ = calc_pfas_score_and_method(pfoa, pfos, other_pfas)

        # Get Base Score
        base_score = 0 if pfas.get("all_nds") else calc_base_score(pfas_score, afr)

        # Determine Bumps
        hazard_index = pfas.get("max_hazard_index") or 0
        reg_bump = 4 if pfoa >= 4 or pfos >= 4 or hazard_index >= 1 else 0

        # Determine Adjusted Base Score
        adj_base_score = calc_adj_base_score(base_score=base_score, reg_bump=reg_bump, lit_bump=0, bell_bump=0, idws=1)

        # Determine Estimated Allocation
        carrier4_est = adj_base_score * 0.0047 * 0.75

        # Determine if future annual production data is needed
        future_data_provided = annual.get("has_three_years_non_zero", False)

        # Combine the annual flow, max flow, and PFAS data
        # into one result for this source.
        results.append({
            "pwsid": pwsid,
            "source_name": source_name,

            # carrier4_est
            "carrier4_est": carrier4_est,

            # Status flag
            "future_data_provided": future_data_provided,

            # Annual flow information.
            "highest_three_years": annual.get("highest_three_years"),
            "average_annual_production_gpy": annual.get(
                "average_annual_production_gpy"
            ),
            "has_three_years_non_zero": annual.get(
                "has_three_years_non_zero",
                False,
            ),

            # Maximum flow information.
            "max_flow_gpm": maximum.get("max_flow_gpm"),

            # PFAS information.
            "max_pfoa": pfas.get("max_pfoa"),
            "max_pfos": pfas.get("max_pfos"),
            "max_hazard_index": pfas.get("max_hazard_index"),
            "max_other_pfas": pfas.get("max_other_pfas"),
            # Include the analyte associated
            # with the maximum Other PFAS result.
            "max_other_pfas_analyte": pfas.get(
                "max_other_pfas_analyte"
            ),
            "all_nds": pfas.get("all_nds"),
        })
        # test

    return results


def get_all_yearly_flows(pwsid, source_name):

    # Fields we want from each annual flow model.
    fields = [
        "pwsid",
        "source_name",
        "year",
        "flow_rate_gpm"
    ]

    source_names = [source_name, f"{source_name} - SUPPLEMENTAL"]

    # Get annual flow records from the first model.
    data1 = ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_name__in=source_names,
        source_variable="AFR"
    ).values(*fields)

    # remove supplemental suffix from source names
    data1 = remove_sup_suffix(data1)

    # Get annual flow records from the second model.
    data2 = TB_ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_name__in=source_names,
        source_variable="AFR"
    ).values(*fields)

    # remove supplemental suffix from source names
    data2 = remove_sup_suffix(data2)

    # Get annual flow records from the third model.
    # Keep the same source_variable filter used in process_annual_flow().
    data3 = Phase2_ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_name__in=source_names,
        source_variable="AFR"
    ).values(*fields)

    # remove supplemental suffix from source names
    data3 = remove_sup_suffix(data3)

    af_updates = list(UpdateAnnualFlowRate.objects.filter(
        pwsid=pwsid,
        source_name__in=source_names
    ).values(*fields))

    # Combine records from all three models.
    data = data1 + data2 + data3 + af_updates

    # Dictionary to store the maximum flow for each year.
    yearly_flows = {}

    # Process each flow record.
    for record in data:

        year = record["year"]
        flow = record["flow_rate_gpm"]

        # Ignore missing flow values.
        if flow is None:
            continue

        # If this is the first value for the year,
        # store it as the maximum.
        if year not in yearly_flows:
            yearly_flows[year] = flow

        # Otherwise, keep whichever flow value is higher.
        else:
            yearly_flows[year] = max(
                yearly_flows[year],
                flow
            )

    # Add 2024 and 2025 if they are not already present.
    yearly_flows.setdefault(2024, None)
    yearly_flows.setdefault(2025, None)

    # Return the results sorted by year.
    return [
        {
            "pwsid": pwsid,
            "source_name": source_name,
            "year": year,
            "flow_rate_gpm": yearly_flows[year],
            "gallons_per_year": round(yearly_flows[year] * 60 * 24 * 365, 1) if yearly_flows[year] is not None else None,
            "mgd": round(((yearly_flows[year] * 60 * 24 * 365) / 365) / 1000000, 3) if yearly_flows[year] is not None else None
        }
        for year in sorted(yearly_flows)
    ]
