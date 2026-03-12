import re
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models import Q
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from ..utils import parse_identifier_query
from ..mappings import genderMapping, addressUseMapping


def broad_address_match(queryset, name, value, prefix=""):
    location_filter_paths = [
        prefix + "address__address_us__delivery_line_1",
        prefix + "address__address_us__delivery_line_2",
        prefix + "address__address_us__city_name",
        prefix + "address__address_us__state_code__abbreviation",
        prefix + "address__address_us__zipcode",
    ]

    return queryset.annotate(search=SearchVector(*location_filter_paths)).filter(
        search=SearchQuery(value, search_type="websearch", config="english")
    )


def field_based_vector_search(queryset, name, value, address_path):
    return queryset.annotate(search=SearchVector(address_path)).filter(
        search=SearchQuery(value, search_type="websearch", config="english")
    )


def city_address_search(queryset, name, value, prefix=""):
    path = prefix + "address__address_us__city_name"
    return field_based_vector_search(queryset, name, value, path)


def state_address_search(queryset, name, value, prefix=""):
    path = prefix + "address__address_us__state_code__abbreviation"
    return field_based_vector_search(queryset, name, value, path)


def postalcode_address_search(queryset, name, value, prefix=""):
    path = prefix + "address__address_us__zipcode"
    arg = {path: value}
    return queryset.filter(**arg)


def address_use_search(queryset, name, value, prefix=""):
    if value in addressUseMapping.keys():
        value = addressUseMapping.toNPD(value)
    else:
        value = -1

    arg = {prefix + "__address_use_id": value}
    return queryset.filter(**arg)


def general_filter_distance(queryset, name, value, prefix=""):
    pattern = r"(-?\d+\.?\d*)\|(-?\d+\.?\d*)\|(\d+\.?\d*)\|?(km|mi|ft)?"
    match = re.fullmatch(pattern, value)
    if match:
        lat, lon, distance, units = match.groups()
        lon = float(lon)
        lat = float(lat)
        distance = float(distance)
        user_location = Point(lon, lat, srid=4326)
        match units:
            case "mi":
                distance_function = D(mi=distance)
            case "ft":
                distance_function = D(ft=distance)
            case _:
                distance_function = D(km=distance)

        arg = {
            prefix + "address__address_us__geolocation__distance_lte": (
                user_location,
                distance_function,
            )
        }
        return queryset.filter(**arg)
    else:
        return queryset.objects.none()


def filter_identifier_general(
    queryset, name, value, npi_prefix=None, ein_prefix=None, other_prefix=None
):
    from uuid import UUID

    system, identifier_id = parse_identifier_query(value)
    queries = Q(pk__isnull=True)

    try:
        npi_q_argument = {npi_prefix + "npi": int(identifier_id)}
    except (ValueError, TypeError):
        # TODO: implement validationerror to show users that NPI must be an int
        npi_q_argument = None

    if system:  # specific identifier search requested
        if system.upper() == "NPI":
            if npi_q_argument:
                queries = Q(**npi_q_argument)
    else:  # general identifier search requested
        if npi_q_argument:
            queries |= Q(**npi_q_argument)

        if ein_prefix:
            try:
                ein_q_argument = {ein_prefix + "ein_id": identifier_id}
                UUID(identifier_id)
                queries |= Q(**ein_q_argument)
            except (ValueError, TypeError):
                pass

        if other_prefix:
            other_q_argument = {other_prefix + "other_id": identifier_id}
            queries |= Q(**other_q_argument)

    return queryset.filter(queries).distinct()


def generic_filter_gender(queryset, name, value, prefix):
    gender_path = prefix + "__individual__gender"
    if value in genderMapping.keys():
        param_map = {gender_path: genderMapping.toNPD(value)}
        return queryset.filter(**param_map)
    return queryset


def simple_generic_field_search(queryset, name, value, name_path):
    query = SearchQuery(value, search_type="websearch", config="english")

    name_path_dict = {name_path: query}

    return queryset.filter(**name_path_dict)


def filter_individual_name(queryset, name, value, prefix):
    path = prefix + "__individual__individualtoname__search_vector"
    return simple_generic_field_search(queryset, name, value, path)

def filter_organization_name_gen(queryset, name, value, prefix=""):
    path = prefix + "organizationtoname__search_vector"
    return simple_generic_field_search(queryset, name, value, path)

def gen_nucc_code_filter(queryset, name, value, prefix=""):
    path = prefix + "organization__clinicalorganization__organizationtotaxonomy__nucc_code__code"
    return field_based_vector_search(queryset, name, value, path)

def gen_nucc_display_filter(queryset, name, value, prefix=""):
    path = prefix + "organization__clinicalorganization__organizationtotaxonomy__nucc_code__display_name"
    return field_based_vector_search(queryset, name, value, path)