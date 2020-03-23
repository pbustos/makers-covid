import json
from copy import deepcopy
from pprint import pprint

from dictdiffer import diff, patch, swap, revert



with open('data.json') as json_file:
    data = json.load(json_file)
    data2 = deepcopy(data)
    # Change
    data2["makers"]["@IvanBarbecho"]["Cantidad actual"]="1"
    # Delete
    del data2["makers"]["Jesús Merideño (Cacéres y Malpartida CC) @JMergal"]
    # Add
    data2["makers"]["orensbruli"] = deepcopy(data2["makers"]["@IvanBarbecho"])
    data2["makers"]["orensbruli"]["Usuario Telegram"] = "orensbruli"

    # calculate diff
    result = diff(data, data2, dot_notation=False)
    result = list(result)
    pprint(list(result))