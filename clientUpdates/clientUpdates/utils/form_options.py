sdwisOwnerCodes = {("L", "L-Local Government"),
                   ("M", "M-Public/Private"),
                   ("P", "P-Private"),
                   ("N", "N-Native American"),
                   ("S", "S-State Government"),
                   ("F", "F-Federal Government"),
                   ("unknown", "Unknown")}

sdwisFacilityCodes = {("cws", "Community Water System"),
                      ("ntncws", "Non-Transient Non-Community Water System"),
                      ("tncws", "Transient Non-Community Water System"),
                      ("unknown", "Unknown")}

sdwisActivityCodes = {("active", "Active"),
                      ("inactive", "Inactive"),
                      ("change", "Change from public to non-public"),
                      ("merge", "Merged with another system"),
                      ("potential", "Potential future system to be regulated"),
                      ("unknown", "Unknown")}

yesNo = ("Yes", "No")

sourceTypeOptions = {("GW", "Groundwater Well"), ("SW", "Surface Water"), ("Other", "Other")}

unitOptions = {("GPM", "GPM (Gallons Per Minute)"), ("GPY", "GPY (Gallons Per Year)"),
               ("MGD", "MGD (Million Gallons Per Day)"), ("AFPY", "AFPY (Acre-feet Per Year)")}

pfasAnalytes = ("PFOA", "PFOS", "PFHxS", "GenX", "PFNA", "PFBS")

# pfasUnits = {("ug/L", "ug/L (ppb)"),
#              ("ng/L", "ng/L (ppt)")}

years = list(range(2013, 2026))

pfasInitialData = [{"analyte": "PFOA"},
                   {"analyte": "PFOS"},
                   {"analyte": "PFHxS"},
                   {"analyte": "GenX"},
                   {"analyte": "PFNA"},
                   {"analyte": "PFBS"},
                   {"analyte": ""}]

yearInitialData = []
for i in range(13):
    year = {"year": 2013 + i}
    yearInitialData.append(year)

otherAnalytes = ("11Cl-PF3OUdS", "8:2FTS", "4:2FTS", "6:2FTS", "ADONA",
                 "9Cl-PF3ONS", "NFDHA", "PFEESA", "PFMPA", "PFMBA",
                 "PFBA", "PFDA", "PFDoA", "PFHpS", "PFHpA",
                 "PFHxA", "PFPeS", "PFPeA", "PFUnA", "NEtFOSAA",
                 "NMeFOSAA", "PFTA", "PFTrDA")