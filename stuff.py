from serpapi import GoogleSearch
import os

"""Tool to search google for a query."""
api_key = os.environ.get('SERPAPI_API_KEY')


search = GoogleSearch({
"q": 'the price of timber',
# "location": "Austin,Texas",
"api_key": api_key
})
result = search.get_dict()

[r['snippet'] for r in result["organic_results"]]
