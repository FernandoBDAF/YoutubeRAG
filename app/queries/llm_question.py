try:
    from app.queries.vector_search import main
except ModuleNotFoundError:
    import sys as _sys, os as _os

    _sys.path.append(
        _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
    )

from app.queries.vector_search import main
import os

query = "What are the most important graph algorithms patterns?"
os.environ["QUERY"] = query
main()