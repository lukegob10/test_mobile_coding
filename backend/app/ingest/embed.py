import hashlib


def embed_text(text: str, dims: int = 64) -> list[float]:
    vec = [0.0] * dims
    for token in text.lower().split():
        h = int(hashlib.sha256(token.encode('utf-8')).hexdigest(), 16)
        vec[h % dims] += 1.0
    norm = sum(x * x for x in vec) ** 0.5
    return [x / norm for x in vec] if norm else vec
