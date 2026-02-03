from django.db import connection


# Database query helpers
def get_female_npis(npi_list):
    """
    Given a list of NPI numbers, return the subset that are female.
    """
    query = """
        SELECT p.npi, i.gender
        FROM npd.provider p
        JOIN npd.individual i ON p.individual_id = i.id
        WHERE p.npi = ANY(%s)
          AND i.gender = 'F'
    """
    with connection.cursor() as cursor:
        cursor.execute(query, [npi_list])
        results = cursor.fetchall()

    return results


# FHIR response assertion helpers
def assert_fhir_response(test_case, response, expected_status=200):
    test_case.assertEqual(response.status_code, expected_status)
    test_case.assertEqual(response["Content-Type"], "application/fhir+json")


def assert_has_results(test_case, response):
    test_case.assertIn("results", response.data)
    test_case.assertGreater(len(response.data["results"]["entry"]), 0)


def assert_pagination_limit(test_case, response, max_size=100):
    bundle = response.data["results"]
    test_case.assertLessEqual(len(bundle["entry"]), max_size)


# Data extraction helpers
def extract_resource_names(response):
    return [d["resource"].get("name", {}) for d in response.data["results"]["entry"]]


def extract_practitioner_names(response):
    return [
        (d["resource"]["name"][-1].get("family", {}), d["resource"]["name"][-1]["given"][0])
        for d in response.data["results"]["entry"]
    ]


def extract_resource_ids(response):
    return [d["resource"].get("id", {}) for d in response.data["results"]["entry"]]


def extract_resource_fields(response, field):
    return [d["resource"].get(field, {}) for d in response.data["results"]["entry"]]


def concat_address_string(address):
    address_string = ""

    for line in address["line"]:
        address_string += line + " "

    address_string += address["city"] + " "
    address_string += address["state"] + " "
    address_string += address["postalCode"]

    return address_string
