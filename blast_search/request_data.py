"Url data definitions for requests between components"

from dataclasses import dataclass
from dataclasses_json import dataclass_json

from blast_search.models import BlastType
from blast_search.blast.blast import FormParameters


BLAST_DB_URL = '/db'
BLAST_SEARCH_URL = '/blast'
BLAST_WORKERS_URL = '/workers'

@dataclass_json
@dataclass
class BlastSearchRequest:
    "Request for new blast search"
    blast_query: str
    blast_type: BlastType
    db_name: str
    params: FormParameters
