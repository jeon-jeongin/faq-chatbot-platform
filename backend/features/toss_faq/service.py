import time


def ask(input):

    start = time.time()
    elapsed = time.time() - start
    return {
        "answer": input,
        "sources": [],
        "elapsed": elapsed,
        "status": "ok",
    }
