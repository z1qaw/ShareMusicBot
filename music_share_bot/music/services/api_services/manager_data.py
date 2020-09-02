import dataclasses
from typing import Any


@dataclasses.dataclass
class ServiceDataRequestQuery:
    bot_inline_query_id: int
    main_result_id: int
    service_name: str
    query_text: str
    query_data_type: str
    completed: bool
    bad: bool
    result: Any
