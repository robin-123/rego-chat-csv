

import argparse

def generate_capacity_check_rego(ul, dl):
    """
    Generates a Rego policy for capacity check.
    """
    return f"""
package slice.capacitycheck

default deny_message = ""
default allow = false

# Deny if UL or DL usage is over {ul}
allow if not over_usage

deny_message = "{{\"upload\": {ul}, \"download\": {dl}}}" if {{
    over_usage
}}

# Internal rule to check UL or DL limits
over_usage if {{
    ul := input.sliceData.sliceOrder.cells.cellTotalResourceUsageUl
    ul > {ul}
}} else if {{
    dl := input.sliceData.sliceOrder.cells.cellTotalResourceUsageDl
    dl > {dl}
}}
"""

def generate_rantemplate_rego(vendor, sw_version, operation):
    """
    Generates a Rego policy for slice ran template.
    """
    return f"""
package slice.rantemplate

default allow = false
default response = ""

allow if response != ""

# Rule for {operation}
response = "{vendor}_{sw_version}%2F{operation}%2FBaseTemplate.jinja?ref=main" if {{
    input.sliceData.node.actual.vendorName == "{vendor}"
    input.sliceData.node.actual.swVersion == "{sw_version}"
    input.sliceData.sliceOrder.operation == "{operation}"
}}
"""

def generate_sfc_rego(percentage, dl_vol_threshold=None, reason="No feasibility"):
    """
    Generates a Rego policy for checking if a slice is feasible.
    """
    dl_check = ""
    if dl_vol_threshold is not None:
        dl_check = f"    dlvolthreshold >= {dl_vol_threshold}"

    return f"""
package slice.policy

default allow = false
default reason = "{reason}"

allow if {{
    feasible := input.feasibleCellsForSlice
    total := input.totalCellsForSlice
    total > 0  # Prevent division by zero
    percentage := (feasible / total) * 100
    percentage >= {percentage}
    {dl_check}
}}

reason = "Slice is feasible since minimum percentage of cells is available" if allow
"""

def main():
    """
    Main function to handle user input and generate Rego code.
    """
    parser = argparse.ArgumentParser(description="Generate Rego policies based on user input.")
    parser.add_argument("policy_type", choices=["capacity_check", "rantemplate", "sfc"], help="The type of Rego policy to generate.")
    
    args = parser.parse_args()

    if args.policy_type == "capacity_check":
        ul = input("Enter the UL threshold: ")
        dl = input("Enter the DL threshold: ")
        rego_code = generate_capacity_check_rego(ul, dl)
        print(rego_code)

    elif args.policy_type == "rantemplate":
        vendor = input("Enter the vendor name: ")
        sw_version = input("Enter the software version: ")
        operation = input("Enter the operation: ")
        rego_code = generate_rantemplate_rego(vendor, sw_version, operation)
        print(rego_code)

    elif args.policy_type == "sfc":
        percentage = input("Enter the percentage threshold: ")
        dl_vol_threshold = input("Enter the DL volume threshold (optional): ")
        reason = input("Enter the reason for denial (optional, default is 'No feasibility'): ") or "No feasibility"
        
        if dl_vol_threshold:
            rego_code = generate_sfc_rego(percentage, dl_vol_threshold, reason)
        else:
            rego_code = generate_sfc_rego(percentage, reason=reason)
        print(rego_code)

if __name__ == "__main__":
    main()

