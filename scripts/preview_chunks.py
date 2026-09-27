from collections import Counter
from pathlib import Path

from app.services.chunker import chunk_directory

chunks = chunk_directory(Path("knowledge"))

print(f"Total chunks: {len(chunks)}\n")
for source, count in Counter(c.source for c in chunks).items():
    print(f"{source:45s} {count:3d}")

lengths = [len(c.text) for c in chunks]
print(f"\nChunk length (chars): min {min(lengths)}, max {max(lengths)}, avg {sum(lengths) // len(lengths)}")

print("\n--- Example chunk (as it will be embedded) ---")
example = next(c for c in chunks if c.section == "Tech stack")
print(example.for_embedding())
