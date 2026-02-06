import logging
from datetime import datetime

from structlog.typing import EventDict


# convert django.db.backend SQL query log records to structured type
# the default django.db.backends query log format is a string:
#   '(%{duration}.3f) %{sql}s; args=%{args}s; alias=%{alias}s'
# by converting it to
def unpack_sql_trace(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    record: logging.LogRecord = event_dict["_record"]

    if record.name == "django.db.backends" and record.module == "utils":
        # the default django query log uses the
        event_dict["event"] = "sql_query"
        event_dict["alias"] = record.alias
        event_dict["sql"] = record.sql
        event_dict["args"] = record.args
        event_dict["duration"] = record.duration
        event_dict["created"] = datetime.fromtimestamp(record.created).isoformat()

    return event_dict
