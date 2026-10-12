import math


def dot_product(
    left: list[float],
    right: list[float],
) -> float:
    _validate_vector_size(left, right)

    return sum(
        a * b
        for a, b in zip(left, right)
    )


def vector_norm(
    vector: list[float],
) -> float:
    return math.sqrt(
        sum(value * value for value in vector)
    )


def cosine_similarity(
    left: list[float],
    right: list[float],
) -> float:
    _validate_vector_size(left, right)

    left_norm = vector_norm(left)
    right_norm = vector_norm(right)

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot_product(left, right) / (left_norm * right_norm)


def euclidean_distance(
    left: list[float],
    right: list[float],
) -> float:
    _validate_vector_size(left, right)

    return math.sqrt(
        sum(
            (a - b) * (a - b)
            for a, b in zip(left, right)
        )
    )


def normalize_vector(
    vector: list[float],
) -> list[float]:
    norm = vector_norm(vector)

    if norm == 0:
        return vector

    return [
        value / norm
        for value in vector
    ]


def _validate_vector_size(
    left: list[float],
    right: list[float],
) -> None:
    if len(left) != len(right):
        raise ValueError(
            f"向量维度不一致：left={len(left)}, right={len(right)}"
        )