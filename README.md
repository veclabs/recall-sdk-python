# recall-sdk-python

Python SDK for [VecLabs Recall](https://github.com/veclabs/recall) — decentralized vector memory for AI agents.

[![PyPI](https://img.shields.io/badge/pypi-solvec-orange.svg)](https://pypi.org/project/solvec/)
[![Version](https://img.shields.io/badge/version-0.1.0a8-blue.svg)]()
[![Tests](https://img.shields.io/badge/tests-48%20passing-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()

---

## Install

```bash
pip install solvec --pre
```

---

## Quick Start

```python
from solvec import SolVec

sv = SolVec(api_key="your-api-key")
collection = sv.collection("agent-memory", dimensions=1536)

# Upsert vectors
collection.upsert([{
    "id": "mem_001",
    "values": [...],
    "metadata": {"text": "User prefers dark mode"}
}])

# Query
results = collection.query(vector=[...], top_k=5)

# Verify collection integrity against on-chain Merkle root
proof = collection.verify()
print(proof.solana_explorer_url)
```

---

## Authentication

Get an API key at [app.veclabs.xyz](https://app.veclabs.xyz).

```python
import os
from solvec import SolVec

sv = SolVec(api_key=os.environ["RECALL_API_KEY"])
```

**Self-hosted with Shadow Drive** (bring your own Solana wallet):

```python
sv = SolVec(
    network="devnet",
    wallet="~/.config/solana/id.json",
    shadow_drive=True
)
```

---

## API Reference

### `SolVec(api_key?, network?, wallet?, shadow_drive?)`

Creates a client. Use `api_key` for hosted mode or `wallet` + `shadow_drive=True` for self-hosted.

### `sv.collection(name, dimensions?)`

Returns a collection handle. Creates the collection on first write. `dimensions` required on first write, inferred after.

```python
collection = sv.collection("my-collection", dimensions=1536)
```

### `collection.upsert(vectors)`

Insert or update vectors. Each vector requires `id` and `values`. `metadata` is optional.

```python
collection.upsert([
    {"id": "v1", "values": [...], "metadata": {"source": "gpt-4"}},
    {"id": "v2", "values": [...]}
])
```

After every upsert, a SHA-256 Merkle root of all vector IDs is posted to the Solana Anchor program on-chain.

### `collection.query(vector, top_k?, metric?)`

Nearest-neighbor search. Returns top-k results with scores and metadata.

```python
results = collection.query(
    vector=[...],
    top_k=10,              # default: 10
    metric="cosine"        # cosine (default), euclidean, dot
)

for match in results.matches:
    print(match.id, match.score, match.metadata)
```

### `collection.delete(ids)`

Delete vectors by ID.

```python
collection.delete(["v1", "v2"])
```

### `collection.verify()`

Fetches the on-chain Merkle root from Solana and verifies it against the current collection state.

```python
proof = collection.verify()
print(proof.valid)               # bool
print(proof.on_chain_root)       # str
print(proof.computed_root)       # str
print(proof.solana_explorer_url) # str
```

### `collection.stats()`

Returns collection statistics.

```python
stats = collection.stats()
print(stats.vector_count)   # int
print(stats.dimensions)     # int
print(stats.merkle_root)    # str
```

---

## Migrating from Pinecone

The API is intentionally shaped to match Pinecone's client. Migration is three line changes:

```python
# Before
from pinecone import Pinecone
pc = Pinecone(api_key="YOUR_KEY")
index = pc.Index("my-index")

# After
from solvec import SolVec
sv = SolVec(api_key="YOUR_KEY")
index = sv.collection("my-index")

# Everything below stays identical
index.upsert(vectors=[...])
index.query(vector=[...], top_k=10)
index.verify()  # new — Pinecone has no equivalent
```

---

## Usage with LangChain

```python
from langchain.vectorstores import VecLabsRecall
from langchain.embeddings import OpenAIEmbeddings

vectorstore = VecLabsRecall(
    api_key="your-api-key",
    collection="langchain-memory",
    embedding=OpenAIEmbeddings()
)

vectorstore.add_texts(["User prefers dark mode", "Meeting at 3pm"])
docs = vectorstore.similarity_search("user preferences", k=5)
```

> LangChain integration is in progress. Star the repo to follow along.

---

## Development

```bash
git clone https://github.com/veclabs/recall-sdk-python
cd recall-sdk-python

pip install hatch
hatch build
pytest tests/ -v   # 48 tests
```

---

## Status

| Feature                   | Status                             |
| ------------------------- | ---------------------------------- |
| Hosted API (api key mode) | ✅ Live                            |
| Shadow Drive (self-host)  | ✅ Available — `shadow_drive=True` |
| Merkle verification       | ✅ Complete                        |
| TypeScript parity         | ✅ 48/48 tests — full parity       |
| LangChain integration     | 📋 In progress                     |
| LlamaIndex integration    | 📋 Planned                         |
| AutoGen integration       | 📋 Planned                         |

---

## Related

- **Rust core engine** → [`veclabs/recall`](https://github.com/veclabs/recall)
- **TypeScript SDK** → [`veclabs/recall-sdk-js`](https://github.com/veclabs/recall-sdk-js)
- **Hosted API** → [api.veclabs.xyz](https://api.veclabs.xyz)
- **Dashboard** → [app.veclabs.xyz](https://app.veclabs.xyz)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

Priority: LangChain integration, LlamaIndex integration, AutoGen integration.

---

## License

MIT. See [LICENSE](LICENSE).

---

[veclabs.xyz](https://veclabs.xyz) · [@veclabs](https://x.com/veclabs46369) · [Discord](https://discord.gg/veclabs)
