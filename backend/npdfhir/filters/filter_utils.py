from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models import Q

from ..utils import parse_identifier_query
from ..mappings import genderMapping

def broad_address_match(queryset, name, value, address_paths):
    return queryset.annotate(search=SearchVector(*address_paths)).filter(
        search=SearchQuery(value, search_type="websearch", config="english")
    )


def field_based_vector_search(queryset, name, value, address_path):
    return queryset.annotate(search=SearchVector(address_path)).filter(
        search=SearchQuery(value, search_type="websearch", config="english")
    )


def filter_identifier_general(queryset, name, value, npi_path=None, ein_path=None, other_path=None):
    from uuid import UUID

    system, identifier_id = parse_identifier_query(value)
    queries = Q(pk__isnull=True)

    try:
        npi_q_argument = {npi_path: int(identifier_id)}
    except (ValueError, TypeError):
        # TODO: implement validationerror to show users that NPI must be an int
        npi_q_argument = None

    ein_q_argument = {ein_path: identifier_id}
    other_q_argument = {other_path: identifier_id}

    if system:  # specific identifier search requested
        if system.upper() == "NPI":
            if npi_q_argument:
                queries = Q(**npi_q_argument)
    else:  # general identifier search requested
        if npi_q_argument:
            queries |= Q(**npi_q_argument)

        if ein_path:
            try:
                UUID(identifier_id)
                queries |= Q(**ein_q_argument)
            except (ValueError, TypeError):
                pass

        if other_path:
            queries |= Q(**other_q_argument)

    return queryset.filter(queries).distinct()


def generic_filter_gender(queryset, name, value, gender_path):
    if value in genderMapping.keys():
        param_map = {gender_path: genderMapping.toNPD(value)}
        return queryset.filter(**param_map)
    return queryset
