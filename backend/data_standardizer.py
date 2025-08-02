from typing import List

# Pete template headers (from  
PETE_TEMPLATE_HEADERS: List[str] = [
    "externalId",
    "Fullname",
    "PropertyAddress",
    "PropertyState",
]

class DataStandardizer:
    """
    Utility for standardizing uploaded data files to Pete format.
    """
    def __init__(self, template_headers: List[str] = PETE_TEMPLATE_HEADERS):
        self.template_headers = template_headers

    # Future: implement scan, load, fuzzy match, standardize, log/report, CLI, etc. 