import math

from app.services.memory import PythonSearchAdapter, simple_embedding, _cosine_similarity


def test_simple_embedding_normalized():
    vec = simple_embedding("teste de busca semântica")
    norm = math.sqrt(sum(v * v for v in vec))
    assert abs(norm - 1.0) < 0.001


def test_cosine_similarity_identical():
    vec = simple_embedding("mesmo texto")
    assert _cosine_similarity(vec, vec) > 0.99


def test_cosine_similarity_different():
    a = simple_embedding("guerra no norte")
    b = simple_embedding("festa na taverna")
    assert _cosine_similarity(a, b) < _cosine_similarity(a, a)


def test_python_search_adapter_instantiates():
    adapter = PythonSearchAdapter()
    assert adapter is not None
