import subprocess
import os
import sys
import jinja2

sys.stdout.reconfigure(encoding="utf-8")

# ── Scalar template variables ─────────────────────────────────────────────────
data = {
    "CURR_DATE":                  "29-Apr-25",
    "Offer_First_Name":           "Anand ",
    "Offer_Mgr_Middle_Name":      "Ashok",
    "Offer_Last_Name":            "Thorat",
    "Offer_Address":              "Chakan",
    "DesignationTitle":           "Officer",
    "Offer_Contract_Start_Date":  "05-May-25",
    "Offer_Contract_End_Date":    "31-May-26",
    "Monthly_CTC_Salary":         "29,167",
    "Notice_Period":              "30 Days",
    "logo_path":                  "logo",   # set to image path, or "" to skip
    "sealPath":                   "",       # set to the company-seal image path, or "" to skip
    "default_signatory_for_letter":   "logo2",       # set to image path, or "" to skip
    "Onb_Mgr_Declaration_Signature": "logo2",    # set to candidate's signature image path, or "" to skip
    "ClientName":                 "Bosch Chassis Systems India Pvt. Ltd",
    "offeredLocationStateName":   "Maharashtra",
}

# ── Compensation break-up rows (page 2) ───────────────────────────────────────
# type 0 -> earnings, type 1 -> deductions. Rows with column1Value == 0 are
# filtered out below before being handed to the template.
breakUpData = [
    {"SalaryHeaderTitle": "Offered CTC",                    "column1Value": 29167, "type": 2},
    {"SalaryHeaderTitle": "Basic",                          "column1Value": 19000, "type": 0},
    {"SalaryHeaderTitle": "HRA",                             "column1Value": 6414,  "type": 0},
    {"SalaryHeaderTitle": "Statutory Bonus Monthly",         "column1Value": 1583,  "type": 0},
    {"SalaryHeaderTitle": "Additional Wages",                "column1Value": 0,     "type": 0},
    {"SalaryHeaderTitle": "EPFER",                           "column1Value": 1800,  "type": 0},
    {"SalaryHeaderTitle": "PF Admin Charges",                "column1Value": 75,    "type": 0},
    {"SalaryHeaderTitle": "EDLI Charges CM",                 "column1Value": 75,    "type": 0},
    {"SalaryHeaderTitle": "EESICER",                         "column1Value": 0,     "type": 0},
    {"SalaryHeaderTitle": "Insurance",                       "column1Value": 190,   "type": 0},
    {"SalaryHeaderTitle": "Workmen Compensation",            "column1Value": 30,    "type": 0},
    {"SalaryHeaderTitle": "EPFEE",                           "column1Value": 1800,  "type": 1},
    {"SalaryHeaderTitle": "ESICEE",                          "column1Value": 0,     "type": 1},
    {"SalaryHeaderTitle": "Transport and Canteen deduction", "column1Value": 496,   "type": 1},
    {"SalaryHeaderTitle": "P Tax",                           "column1Value": 200,   "type": 1},
]
monthlyCTC = 29167
salaryStructureGross = 26997
salaryStructureNet = 24501

# Split by type, then drop zero-value rows before handing off to the template.
EarningHeadersTable   = [row for row in breakUpData if row["type"] == 0 and row["column1Value"] > 0]
DeductionHeadersTable = [row for row in breakUpData if row["type"] == 1 and row["column1Value"] > 0]

# ── Jinja2 environment — delimiters match \VAR{} / \BLOCK{} in the template ──
_here = os.path.dirname(os.path.abspath(__file__))

env = jinja2.Environment(
    block_start_string    = r"\BLOCK{",
    block_end_string      = "}",
    variable_start_string = r"\VAR{",
    variable_end_string   = "}",
    comment_start_string  = r"\#{",
    comment_end_string    = "}",
    trim_blocks           = True,
    lstrip_blocks          = True,
    undefined              = jinja2.Undefined,
    loader                 = jinja2.FileSystemLoader(_here),
)

# ── Render ─────────────────────────────────────────────────────────────────────
output_path = os.path.join(_here, "offerletter_generated.tex")

content = env.get_template("offerLetter.tex").render(
    **data,
    breakUpData=breakUpData,
    EarningHeadersTable=EarningHeadersTable,
    DeductionHeadersTable=DeductionHeadersTable,
    monthlyCTC=monthlyCTC,
    salaryStructureGross=salaryStructureGross,
    salaryStructureNet=salaryStructureNet,
)

with open(output_path, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Generated: {output_path}")

# ── Compile with XeLaTeX ──────────────────────────────────────────────────────
result = subprocess.run(
    ["xelatex", "-interaction=nonstopmode", "offerletter_generated.tex"],
    cwd=_here,
    capture_output=True,
    encoding="utf-8",
    errors="replace",
)

pdf_path = os.path.join(_here, "offerletter_generated.pdf")
if os.path.exists(pdf_path):
    print("PDF compiled successfully: offerletter_generated.pdf")
    if result.returncode != 0:
        print("(compiled with warnings — see offerletter_generated.log)")
else:
    print("Compilation FAILED — no PDF produced")
    print(result.stdout[-3000:])
