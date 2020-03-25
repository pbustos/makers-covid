import os
import json
from enum import Enum

parent_folder = os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

TIPOUSUARIO, CIUDAD, CAPACTUAL = range(3)


class DATA(Enum):
    ORIGINAL = os.path.join(parent_folder, "data", "data.json")
    WORKING = os.path.join(parent_folder, "data", "dataset_working.json")
    SESSION = os.path.join(parent_folder, "data", "session_")


def load_data(which_data):
    try:
        with open(which_data) as f:
            dataset = json.load(f)
        return dataset
    except:
        return {}


def load_datasession(user):
    session_data = str(DATA.SESSION.value) + f"{user.username}.json"
    result = load_data(session_data)
    if result == {}:
        result = {user.id: {
            "telegram_id": user.id,
            "Tipousuario": "maker",
            "username": user.username,
            "usuario": user.first_name,
            "capacidad diaria": 0,
            "cantidad actual": 0,
            "entregadas": 0,
            "direccion": "",
            "Localidad": "",
            "lat": "",
            "long": ""}
        }
        write_session(user.username, result)
    return result


def write_data(new_data, which_data=DATA.WORKING.value):
    with open(which_data, "w") as f:
        f.write(json.dumps(new_data, sort_keys=True, indent=4))


def write_session(username, new_data):
    session_data = str(DATA.SESSION.value) + f"{username}.json"
    write_data(new_data, session_data)


def session(user, type_session, data):
    session_data = str(DATA.SESSION.value) + f"{user.username}.json"
    data = load_data(session_data)
    if type_session == TIPOUSUARIO:
        pass
    elif type_session == CIUDAD:
        data[user.id]["Localidad"] = data
    elif type_session == CAPACTUAL:
        data[user.id]["cantidad actual"] = data
    write_session(user.username, data)

