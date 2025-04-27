"""
This script extracts and transforms company data from scraped JSON files into csv tables.
"""

import os
import yaml
import json

import pandas as pd


def clean_year(value):
    year_str = str(value)
    return year_str[:4] if len(year_str) > 4 else year_str


def load_yml(path: str = "data/translations.yml") -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def extract_basic_company_details(data, json_file_name, business_id):
    address_data = data.get("address", {})

    # translation
    translation_dict = load_yml()
    category_mappings = translation_dict.get("category_translations", {})
    if data.get("mainLineOfBusinessName"):
        main_line_of_business_category = category_mappings[
            data.get("mainLineOfBusinessName")
        ]
    else:
        main_line_of_business_category = None

    sub_category_mappings = translation_dict.get("sub_category_translations", {})
    if data.get("tolMainLineofBusinessName"):
        main_line_of_business_subcategory = sub_category_mappings[
            data.get("tolMainLineofBusinessName")
        ]
    else:
        main_line_of_business_subcategory = None

    basic_company_details = {
        "business_id": business_id,
        "business_id_raw": json_file_name.replace(".json", ""),
        "name": data.get("name"),
        # "phone_number": data["phone"] if data["hasPhone"] else None, # Let's keep things private
        "province": data.get("provinceName", None),
        "city": data.get("cityName", None),
        "street_address": address_data.get("streetAddress"),
        "postal_code": address_data.get("postalCode"),
        "post_office": address_data.get("postOffice"),
        "coordinates": tuple(data.get("coordinates").values())
        if data.get("coordinates")
        else None,
        "postal_address": data.get("postalAddressBox"),
        "postal_address_code": data.get("postalAddressPostalCode"),
        "postal_address_post_offoce": data.get("postalAddressPostOffice"),
        "postal_address_country": data.get("postalAddressCountryName"),
        "postal_address_country_code": data.get("postalAddressCountryCode"),
        "company_form": data.get("companyForm"),
        "established_date": data.get("established"),
        "main_line_of_business_code": data.get("tolMainLineofBusinessCode"),
        "main_line_of_business": main_line_of_business_subcategory,
        "main_line_of_business_category": main_line_of_business_category,
        # "email": data.get("email"), # Let's keep things private
    }
    return basic_company_details


def extract_company_financial_details(data, business_id):
    financial_fields = {
        "turnover": "financialTurnovers",
        "turnover_change_pct": "financialTurnoverPercentageChanges",
        "operating_profit": "financialOperatingProfits",
        "operating_margin_pct": "financialOperatingMargins",
        "solvency_ratio": "financialSolvencies",
        "balance_sheet_total": "financialBalances",
        "num_employees": "financialNumberOfEmployees",
        "ebitda_margin_pct": "financialEBITDAs",
        "roi_pct": "financialROIs",
        "equity_total": "financialEquities",
        "net_income": "financialNetIncomes",
        "quick_ratio": "financialQuickRatios",
        "current_ratio": "financialCurrentRatios",
    }

    years = data.get("financialFiscalYears", [])
    financial_arrays = {
        field: data.get(json_field, [])
        for field, json_field in financial_fields.items()
    }

    financial_rows = []
    for idx, year_value in enumerate(years):
        year = clean_year(year_value)
        row = {
            "business_id": business_id,
            "year": year,
        }
        for field, array in financial_arrays.items():
            row[field] = array[idx] if idx < len(array) and array[idx] != "" else None
        financial_rows.append(row)

    # scale the financial values
    for year_row in financial_rows:
        year_row["turnover"] = (
            float(year_row["turnover"]) * 1000 if year_row["turnover"] else None
        )
        year_row["operating_profit"] = (
            float(year_row["operating_profit"]) * 1000
            if year_row["operating_profit"]
            else None
        )
        year_row["net_income"] = (
            float(year_row["net_income"]) * 1000
            if year_row["balance_sheet_total"]
            else None
        )

    return financial_rows


def extract_company_decision_persons(data, business_id):
    decision_rows = []
    decision_persons = data.get("decisionPersons", [])
    for person in decision_persons:
        row = {
            "business_id": business_id,
            "decision_person_id": person.get("decisionPersonId"),
            "office_id": person.get("officeId"),
            "position_id": person.get("positionId"),
            "position_text": person.get("positionText"),
            "first_name": person.get("firstName"),
            "last_name": person.get("lastName"),
            "gender": person.get("gender"),
            "status_id": person.get("statusId"),
            "prh_id": person.get("prhId"),
            "mbs_id": person.get("mbsId"),
        }

        responsibilities = person.get("responsibilities", [])
        responsibilities_text = person.get("responsibilitiesText", [])
        row["responsibilities"] = (
            ";".join(responsibilities) if responsibilities else None
        )
        row["responsibilities_text"] = (
            ";".join(responsibilities_text) if responsibilities_text else None
        )

        decision_rows.append(row)

    return decision_rows


def extract_extended_decision_persons(data: dict, business_id: str) -> list:
    rows = []
    associated_persons = data.get("finderDecisionPersons", [])

    for associated_person in associated_persons:
        decision_persons = associated_person.get("decisionPersons", [])

        for person in decision_persons:
            row = {
                "business_id": business_id,
                "finder_decision_person_id": person.get("decisionPersonId"),
                "first_name": person.get("firstName"),
                "last_name": person.get("lastName"),
                "full_name": person.get("companyName"),
                "position_text": person.get("positionText"),
                "position_id": person.get("positionId"),
                "status_id": person.get("statusId"),
                "office_id": person.get("officeId"),
                "person_reg_date": person.get("personRegDate"),
                "prh_id": person.get("prhId"),
                "company_turnover": None,
                "company_operating_margin": None,
            }
            try:
                row["company_turnover"] = (
                    float(person.get("companyTurnover"))
                    if person.get("companyTurnover") not in (None, "")
                    else None
                )
            except ValueError:
                row["company_turnover"] = None

            try:
                row["company_operating_margin"] = (
                    float(person.get("companyOperatingMargin"))
                    if person.get("companyOperatingMargin") not in (None, "")
                    else None
                )
            except ValueError:
                row["company_operating_margin"] = None

            rows.append(row)

    return rows


def main(data_path: str, output_path: str) -> None:
    json_files = [f for f in os.listdir(data_path) if f.endswith(".json")]

    basic_details, financial_details, main_decision_makers, all_decision_makers = (
        [],
        [],
        [],
        [],
    )

    for json_file_name in json_files:
        with open(os.path.join(data_path, json_file_name), "r", encoding="utf-8") as f:
            raw_data = json.load(f)

            data = raw_data["props"]["pageProps"]["dehydratedState"]["queries"][0][
                "state"
            ]["data"]

            business_id = data.get("businessId")
            print(business_id)
            basic_details.append(
                extract_basic_company_details(data, json_file_name, business_id)
            )
            financial_details.extend(
                extract_company_financial_details(data, business_id)
            )
            main_decision_makers.extend(
                extract_company_decision_persons(data, business_id)
            )
            all_decision_makers.extend(
                extract_extended_decision_persons(data, business_id)
            )

    output_tables = {
        "basic_details.csv": basic_details,
        "financial_details.csv": financial_details,
        "main_decision_makers.csv": main_decision_makers,
        "all_decision_makers.csv": all_decision_makers,
    }

    os.makedirs(output_path, exist_ok=True)

    for filename, records in output_tables.items():
        df = pd.DataFrame(records)
        df.to_csv(os.path.join(output_path, filename), index=False)


if __name__ == "__main__":
    input_path = os.path.join("data", "scraped_raw_jsons")
    output_path = os.path.join("data", "company_info")
    main(input_path, output_path)
