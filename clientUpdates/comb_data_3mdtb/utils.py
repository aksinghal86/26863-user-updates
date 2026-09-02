from .models import ClaimPfasResult, TB_ClaimPfasResult, ClaimFlowRate, TB_ClaimFlowRate, Phase2_ClaimFlowRate, \
    Phase2_ClaimPfasResult, UpdatePfasResult


def process_pfas(pwsid):

    # Fields we want from each PFAS model
    fields = [
        "pwsid",
        "source_name",
        "analyte",
        "result_ppt"
    ]

    # Get PFAS records for this PWSID from the first model
    data1 = ClaimPfasResult.objects.filter(
        pwsid=pwsid
    ).values(*fields)

    # Get PFAS records for this PWSID from the second model
    data2 = TB_ClaimPfasResult.objects.filter(
        pwsid=pwsid
    ).values(*fields)

    # Get PFAS records for this PWSID from the third model
    data3 = Phase2_ClaimPfasResult.objects.filter(
        pwsid=pwsid
    ).values(*fields)

    # Get any updates made to PFAS results
    data4 = UpdatePfasResult.objects.filter(
        pwsid=pwsid
    ).values(*fields)

    # Combine records from all models
    data = list(data1) + list(data2) + list(data3) + list(data4)

    # Dictionary to store the results for each water source
    sources = {}

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
                "max_other_pfas_analyte": None
            }

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

    # Get historical data from all three models.
    claim_data = ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_variable="AFR",
    ).values(*fields)

    tb_claim_data = TB_ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_variable="AFR",
    ).values(*fields)

    phase2_claim_data = Phase2_ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_variable="AFR",
    ).values(*fields)

    # Store data by (pwsid, source_name).
    sources = {}

    # Add data from all three models.
    all_data = list(claim_data) + list(tb_claim_data) + list(phase2_claim_data)

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

        # Future data is false until the new model is implemented.
        future_data_provided = (
                yearly_data[2024] is not None
                and yearly_data[2025] is not None
        )

        results.append({
            "pwsid": pwsid,
            "source_name": source_name,
            "highest_three_years": highest_three,
            "average_annual_production_gpy": average_gpy,
            "future_data_provided": future_data_provided,
        })

    return results

def process_max_flow(pwsid):
    fields = [
        "pwsid",
        "source_name",
        "flow_rate_gpm",
    ]

    # Get max flow data from all three models.
    claim_data = ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_variable="VFR",
    ).values(*fields)

    tb_claim_data = TB_ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_variable="VFR",
    ).values(*fields)

    phase2_claim_data = Phase2_ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_variable="VFR",
    ).values(*fields)

    # Store data by (pwsid, source_name).
    sources = {}

    # Add data from all three models.
    all_data = list(claim_data) + list(tb_claim_data) + list(phase2_claim_data)

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

    # Get PFAS data and organize it by pwsid/source_name.
    pfas_data = {
        (item["pwsid"], item["source_name"]): item
        for item in process_pfas(pwsid)
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

        # Combine the annual flow, max flow, and PFAS data
        # into one result for this source.
        results.append({
            "pwsid": pwsid,
            "source_name": source_name,

            # Annual flow information.
            "highest_three_years": annual.get("highest_three_years"),
            "average_annual_production_gpy": annual.get(
                "average_annual_production_gpy"
            ),
            "future_data_provided": annual.get(
                "future_data_provided",
                False,
            ),

            # Maximum flow information.
            "max_flow_gpm": maximum.get("max_flow_gpm"),

            # PFAS information.
            "max_pfoa": pfas.get("max_pfoa"),
            "max_pfos": pfas.get("max_pfos"),
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

    # Get annual flow records from the first model.
    data1 = ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_name=source_name,
        source_variable="AFR"
    ).values(*fields)

    # Get annual flow records from the second model.
    data2 = TB_ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_name=source_name,
        source_variable="AFR"
    ).values(*fields)

    # Get annual flow records from the third model.
    # Keep the same source_variable filter used in process_annual_flow().
    data3 = Phase2_ClaimFlowRate.objects.filter(
        pwsid=pwsid,
        source_name=source_name,
        source_variable="AFR"
    ).values(*fields)

    # Combine records from all three models.
    data = list(data1) + list(data2) + list(data3)

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
