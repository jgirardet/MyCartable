from pathlib import Path

import pytest


root = Path(__file__).parents[1]
binary = root  / "binary"
dist = root / "dist" / "MyCartable"

def test_binary_included():
    dist_binary = dist / "binary"
    for x, y in zip(dist_binary.glob("**/*"), binary.glob("**/*")):
        assert x.relative_to(dist) == y.relative_to(root)


if __name__ == '__main__':
    pytest.main([str(Path(__file__).parent)])