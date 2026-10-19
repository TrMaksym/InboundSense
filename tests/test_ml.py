from app.services.ml_engine import ml_engine
from app.services.nlp import generate_embedding, split_text_into_chunks


def test_split_text_into_chunks_basic():
    text = (
        "InboundSense is an asynchronous pipeline for event-driven processing. "
        "It splits long incoming communications into smaller text segments. "
        "Each segment is transformed into a dense vector embedding for semantic search."
    )
    chunks = split_text_into_chunks(text, chunk_size=80, chunk_overlap=15)

    assert len(chunks) > 1
    assert all(isinstance(c, str) for c in chunks)
    assert all(len(c) > 0 for c in chunks)


def test_split_text_into_chunks_short_and_empty():
    short_text = "Short event text"
    assert split_text_into_chunks(short_text, chunk_size=100) == [short_text]
    assert split_text_into_chunks("") == []
    assert split_text_into_chunks("   ") == []


def test_generate_embedding_shape():
    texts = ["Database connection dropped", "Payment failed"]
    vectors = generate_embedding(texts)

    assert len(vectors) == 2
    assert len(vectors[0]) == 384
    assert len(vectors[1]) == 384
    assert all(isinstance(val, float) for val in vectors[0])


def test_generate_embedding_empty():
    assert generate_embedding([]) == []


def test_ml_engine_classify():
    test_text = "PostgreSQL query timeout error on port 5432"
    category, confidence = ml_engine.classify(test_text)

    assert category in ["tech", "support", "sales", "general"]
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0


def test_ml_engine_empty_input():
    category, confidence = ml_engine.classify("")
    assert category in ["tech", "support", "sales", "general"]
    assert isinstance(confidence, float)