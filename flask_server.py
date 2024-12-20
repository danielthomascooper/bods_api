from flask import Flask, request, make_response
from api.bods_api import BODS_request
from time import perf_counter

app = Flask(__name__)

CACHE_TIMEOUT = 15  # seconds

# import api key from file, key acquired from https://data.bus-data.dft.gov.uk/ in account settings
with open("SECRET.txt", "r") as api_reader:
    API_KEY = api_reader.readline().strip()

# naive caching implementation to avoid hitting API limits
last_called = {}
cached_responses = {}

# used to identify if same call has been used in last
def hash_args(args):
    return frozenset(args.items())

@app.route('/locations')
def get_locations():
    global cached_responses, last_called

    hash = hash_args(request.args)
    if hash not in last_called:
        last_called[hash] = 0

    if (hash not in cached_responses) or (perf_counter() - last_called[hash]) > CACHE_TIMEOUT:
        print("getting new data")

        return_data = BODS_request(API_KEY, "location", **request.args)
        response = make_response(return_data.to_json())
        response.headers.add('Access-Control-Allow-Origin', '*')

        cached_responses[hash_args(request.args)] = response
        last_called[hash] = perf_counter()

        return response
    else:
        print("using cache")

        return cached_responses[hash]

