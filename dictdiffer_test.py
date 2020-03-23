import json
from copy import deepcopy
from pprint import pprint

from dictdiffer import diff, patch, swap, revert


with open('data.json') as json_file:
    data = json.load(json_file)
    data2 = deepcopy(data)
    data2["makers"]["@IvanBarbecho"]["Cantidad actual"]="1"
    ddiff = diff(data, data2)
    for d in ddiff["values_changed"]:
        reconstruct(d,{})
    pprint(ddiff)
