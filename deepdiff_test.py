import json
from copy import deepcopy
from pprint import pprint

from deepdiff import DeepDiff

def reconstruct(d, new):
    if d.up:
        print(d.up)
        print(d)
        reconstruct(d.up, new)
    else:
        return new

with open('data.json') as json_file:
    data = json.load(json_file)
    data2 = deepcopy(data)
    data2["makers"]["@IvanBarbecho"]["Cantidad actual"]="1"
    ddiff = DeepDiff(data, data2, view='tree')
    for d in ddiff["values_changed"]:
        reconstruct(d,{})
    pprint(ddiff)
