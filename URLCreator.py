from typing import Dict, Union
import re
from datetime import datetime
import json

class URLCreator:
    def __init__(self, search: Union[Dict, None]) -> None:
        self.base_url = r'https://www.gov.uk/search/all?keywords="{:s}"'
        self.search = search
        self.page_no = 0
        self.max_page = None

    def set_search_parameters(self, search: Dict) -> None:
        self.search = search
        self.page_no = 0
        self.max_page = None        

    def create_url(self) -> None:
        target_url = self.base_url.format( '"+"'.join(['+'.join(i.split()) for i in self.search['search_terms']]))
        if self.search.get('order', None) is not None:
            target_url += "&order=updated-newest"
        if self.search.get('start', None) is not None:
            start_date = datetime.strptime(self.search['start'])
            target_url += "&public_timestamp[from][day]=" + str(start_date.day)
            target_url += "&public_timestamp[from][month]=" + str(start_date.month)
            target_url += "&public_timestamp[from][year]=" + str(start_date.year)
        if self.search.get('end', None) is not None:
            end_date = datetime.strptime(self.search['end'])
            target_url += "&public_timestamp[to][day]=" + str(end_date.day)
            target_url += "&public_timestamp[to][month]=" + str(end_date.month)
            target_url += "&public_timestamp[to][year]=" + str(end_date.year)
        if self.search.get('organisations', None) is not None:
            for org in self.search['organisations']:
                target_url += "&organisations[]=" + org
        self.target_url = target_url
    
    def set_max_page(self, max_page: int) -> None:
        self.max_page = max_page
    
    def next_page(self) -> str:
        if self.max_page is None:
            return self.target_url
        else:
            self.page_no += 1
            return self.target_url +  "&page=" + str(self.page_no)
        
    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4)
