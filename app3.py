import json

def parse_rental_agreement(file_path):
    # Read text from the file
    with open(file_path, "r", encoding="utf-8") as file:
        input_text = file.read()

    # Splitting the text into sections
    sections = [section.strip() for section in input_text.split("\n  \n")]

    # Structure the data into a dictionary
    rental_agreement = {
        "RENTAL AGREEMENT": {
            "Date": None,
            "Location": None,
            "Parties": {
                "Owner": {
                    "Name": None,
                    "Relation": None,
                    "Address": None
                },
                "Tenant": {
                    "Name": None,
                    "Relation": None,
                    "Work/Study Address": None,
                    "Permanent Address": None
                },
                "Property Details": {
                    "Owner": None,
                    "Property Address": None,
                    "Description": None
                },
                "Terms and Conditions": {
                    "duration": None,
                    "rent": None,
                    "monthly_maintenance_charge": None,
                    "maintenance_includes": None,
                    "tenant_responsibilities": {
                        "electricity_and_water_bills": None,
                        "security_deposit": None,
                        "refundable": "Yes",
                        "deductions": "Deductions may be made for damages beyond normal wear and tear."
                    },
                    "owner_responsibilities": {
                        "condition_of_premises": None,
                        "property_taxes": "Owner is responsible for property taxes.",
                        "indemnification": "Owner indemnifies Tenant against claims related to quiet possession of the premises."
                    },
                    "other_conditions": {
                        "subletting": "Subletting or assigning the premises, wholly or partially, is prohibited.",
                        "structural_alterations": "Prior written consent from Owner is required for any structural alterations.",
                        "inspection": "Owner reserves the right to inspect the premises for maintenance purposes.",
                        "termination": "Either party may terminate the agreement with one month's written notice.",
                        "disputes_resolution": "Disputes shall be resolved through negotiation between the parties.",
                        "governing_law": "Agreement shall be governed by the laws of the State of New York.",
                        "jurisdiction": "Parties submit to exclusive jurisdiction of courts of New York.",
                        "notices": "Any notices or communications required shall be in writing and sent to provided addresses."
                    }
                }
            }
        }
    }

    # Extracting Information
    try:
        rental_agreement["RENTAL AGREEMENT"]["Date"] = sections[1].split("on ")[1].split(", in")[0].strip()
        rental_agreement["RENTAL AGREEMENT"]["Location"] = sections[1].split("in ")[1].strip()
        
        owner_section = sections[2]
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Owner"]["Name"] = owner_section.split("The owner i")[1].split(",")[0].strip()[1:]
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Owner"]["Relation"] = owner_section.split("son of ")[1].split(",")[0].strip()
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Owner"]["Address"] = owner_section.split("residing at ")[1].strip()

        tenant_section = sections[4]
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Tenant"]["Name"] = tenant_section.split("is ")[1].split(",")[0].strip()
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Tenant"]["Relation"] = tenant_section.split(" of ")[1].split(",")[0].strip()
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Tenant"]["Work/Study Address"] = tenant_section.split("at ")[1].split(",")[0].strip()
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Tenant"]["Permanent Address"] = tenant_section.split("at ")[2].strip()

        property_details_section = sections[6]
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Property Details"]["Owner"] = property_details_section.split("is ")[1].split(",")[0].strip()
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Property Details"]["Property Address"] = property_details_section.split("located at ")[1].split(",")[0].strip()
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Property Details"]["Description"] = property_details_section.split("referred to as the ")[1].split(" in this agreement.")[0].strip()
        
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Terms and Conditions"]["duration"] = sections[8].split("on ")[1].strip()
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Terms and Conditions"]["rent"] = sections[9].split("Rs")[1].split("excluding")[0].strip()
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Terms and Conditions"]["monthly_maintenance_charge"] = sections[10].split("of Rs.")[1].strip()
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Terms and Conditions"]["maintenance_includes"] = sections[10].split("including")[1].split(".")[0].strip()
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Terms and Conditions"]["tenant_responsibilities"]["electricity_and_water_bills"] = sections[11].split("pay for")[1].split(".")[0].strip()
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Terms and Conditions"]["tenant_responsibilities"]["security_deposit"] = sections[12].split("of Rs. ")[1].split(",")[0].strip()
        rental_agreement["RENTAL AGREEMENT"]["Parties"]["Terms and Conditions"]["owner_responsibilities"]["condition_of_premises"] = sections[13].split("that all fittings, fixtures, and appliances in the premises ")[1].split(" at the beginning")[0].strip()
    except IndexError:
        pass  # If any field extraction fails, leave the respective fields as None or empty strings

    return rental_agreement

def save_as_json(data, output_file_path):
    # Convert dictionary to JSON
    rental_agreement_json = json.dumps(data, indent=2)

    # Write JSON data to a file
    with open(output_file_path, "w") as output_file:
        output_file.write(rental_agreement_json)

    print("JSON data has been written to:", output_file_path)

# Example usage:
# file_path = "static/pdf/legal.txt"
# output_file_path = "rental_agreement.json"
# rental_agreement_data = parse_rental_agreement(file_path)
# save_as_json(rental_agreement_data, output_file_path)
