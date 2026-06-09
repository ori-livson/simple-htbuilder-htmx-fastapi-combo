import pickle


def cache(obj, path: str):
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def uncache(path: str):
    with open(path, "rb") as f:
        return pickle.load(f)
