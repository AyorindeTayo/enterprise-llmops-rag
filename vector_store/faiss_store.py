import pickle
import numpy as np
import logging
from typing import List, Tuple, Dict, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import faiss  # type: ignore
    FAISS_AVAILABLE = True
except Exception:
    FAISS_AVAILABLE = False


if FAISS_AVAILABLE:
    # Use real FAISS-backed implementation when available
    class FaissStore:
        def __init__(self, dim: int = 1536, path: str = "vector_store/faiss.index", use_ivf: bool = False):
            self.dim = dim
            self.path = path
            self.use_ivf = use_ivf
            self.texts: List[str] = []
            self.metadata: List[Dict] = []
            self.embeddings: Optional[np.ndarray] = None

            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            self._initialize_index()
            self._load()

        def _initialize_index(self):
            if self.use_ivf:
                quantizer = faiss.IndexFlatL2(self.dim)
                self.index = faiss.IndexIVFFlat(quantizer, self.dim, nlist=100)
                logger.info("Initialized IVFFlat index for large-scale search")
            else:
                self.index = faiss.IndexFlatL2(self.dim)
                logger.info("Initialized FlatL2 index")

        def _load(self):
            try:
                index_path = Path(self.path)
                if index_path.exists():
                    self.index = faiss.read_index(self.path)
                    texts_path = Path(f"{self.path}.texts")
                    if texts_path.exists():
                        with open(texts_path, "rb") as f:
                            self.texts = pickle.load(f)
                    metadata_path = Path(f"{self.path}.metadata")
                    if metadata_path.exists():
                        with open(metadata_path, "rb") as f:
                            self.metadata = pickle.load(f)
                    embeddings_path = Path(f"{self.path}.embeddings")
                    if embeddings_path.exists():
                        self.embeddings = np.load(embeddings_path)
                    logger.info(f"Loaded FAISS index with {len(self.texts)} vectors")
            except Exception as e:
                logger.warning(f"Could not load existing index: {e}")
                self.texts = []
                self.metadata = []
                self.embeddings = None

        def add(self, embeddings: np.ndarray, texts: List[str], metadata: Optional[List[Dict]] = None) -> None:
            if embeddings.shape[1] != self.dim:
                raise ValueError(f"Embedding dimension {embeddings.shape[1]} does not match store dimension {self.dim}")
            if self.use_ivf and self.index.ntotal == 0:
                self.index.train(embeddings.astype("float32"))
            embeddings_float32 = embeddings.astype("float32")
            self.index.add(embeddings_float32)
            self.texts.extend(texts)
            if metadata:
                self.metadata.extend(metadata)
            else:
                self.metadata.extend([{} for _ in texts])
            if self.embeddings is None:
                self.embeddings = embeddings_float32
            else:
                self.embeddings = np.vstack([self.embeddings, embeddings_float32])
            self._save()
            logger.info(f"Added {len(texts)} vectors. Total: {self.index.ntotal}")

        def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[List[str], List[float], List[int]]:
            if self.index.ntotal == 0:
                return [], [], []
            query_float32 = query_embedding.astype("float32").reshape(1, -1)
            distances, indices = self.index.search(query_float32, k)
            results_texts = [self.texts[i] if i < len(self.texts) else "" for i in indices[0]]
            return results_texts, distances[0].tolist(), indices[0].tolist()

        def search_with_metadata(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
            texts, distances, indices = self.search(query_embedding, k)
            results = []
            for text, distance, idx in zip(texts, distances, indices):
                results.append({
                    "text": text,
                    "distance": float(distance),
                    "metadata": self.metadata[idx] if idx < len(self.metadata) else {},
                    "index": int(idx)
                })
            return results

        def delete(self, index: int) -> None:
            if index < len(self.metadata):
                self.metadata[index]["_deleted"] = True
                self._save()

        def get_stats(self) -> Dict:
            return {
                "total_vectors": self.index.ntotal,
                "embedding_dimension": self.dim,
                "index_type": "IVFFlat" if self.use_ivf else "FlatL2",
                "path": self.path
            }

        def _save(self) -> None:
            try:
                faiss.write_index(self.index, self.path)
                with open(f"{self.path}.texts", "wb") as f:
                    pickle.dump(self.texts, f)
                with open(f"{self.path}.metadata", "wb") as f:
                    pickle.dump(self.metadata, f)
                if self.embeddings is not None:
                    np.save(f"{self.path}.embeddings", self.embeddings)
            except Exception as e:
                logger.error(f"Error saving index: {e}")

        def clear(self) -> None:
            self._initialize_index()
            self.texts = []
            self.metadata = []
            self.embeddings = None
            self._save()

        def __len__(self) -> int:
            return self.index.ntotal

else:
    # Lightweight numpy fallback for environments without faiss
    class FaissStore:
        def __init__(self, dim: int = 1536, path: str = "vector_store/faiss.index", use_ivf: bool = False):
            self.dim = dim
            self.path = path
            self.texts: List[str] = []
            self.metadata: List[Dict] = []
            self.embeddings: Optional[np.ndarray] = None
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
            self._load()

        def _load(self):
            try:
                texts_path = Path(f"{self.path}.texts")
                if texts_path.exists():
                    with open(texts_path, "rb") as f:
                        self.texts = pickle.load(f)
                metadata_path = Path(f"{self.path}.metadata")
                if metadata_path.exists():
                    with open(metadata_path, "rb") as f:
                        self.metadata = pickle.load(f)
                embeddings_path = Path(f"{self.path}.embeddings")
                if embeddings_path.exists():
                    self.embeddings = np.load(embeddings_path)
            except Exception as e:
                logger.warning(f"Could not load existing store: {e}")
                self.texts = []
                self.metadata = []
                self.embeddings = None

        def add(self, embeddings: np.ndarray, texts: List[str], metadata: Optional[List[Dict]] = None) -> None:
            if embeddings.shape[1] != self.dim:
                raise ValueError(f"Embedding dimension {embeddings.shape[1]} does not match store dimension {self.dim}")
            embeddings_float32 = embeddings.astype("float32")
            if self.embeddings is None:
                self.embeddings = embeddings_float32
            else:
                self.embeddings = np.vstack([self.embeddings, embeddings_float32])
            self.texts.extend(texts)
            if metadata:
                self.metadata.extend(metadata)
            else:
                self.metadata.extend([{} for _ in texts])
            self._save()

        def search(self, query_embedding: np.ndarray, k: int = 5) -> Tuple[List[str], List[float], List[int]]:
            if self.embeddings is None or len(self.texts) == 0:
                return [], [], []
            q = query_embedding.astype("float32").reshape(1, -1)
            # L2 distances
            dists = np.linalg.norm(self.embeddings - q, axis=1)
            idxs = np.argsort(dists)[:k]
            results_texts = [self.texts[int(i)] for i in idxs]
            results_distances = [float(dists[int(i)]) for i in idxs]
            results_indices = [int(i) for i in idxs]
            return results_texts, results_distances, results_indices

        def search_with_metadata(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
            texts, distances, indices = self.search(query_embedding, k)
            results = []
            for text, distance, idx in zip(texts, distances, indices):
                results.append({
                    "text": text,
                    "distance": float(distance),
                    "metadata": self.metadata[idx] if idx < len(self.metadata) else {},
                    "index": int(idx)
                })
            return results

        def delete(self, index: int) -> None:
            if index < len(self.metadata):
                self.metadata[index]["_deleted"] = True
                self._save()

        def get_stats(self) -> Dict:
            return {
                "total_vectors": 0 if self.embeddings is None else int(self.embeddings.shape[0]),
                "embedding_dimension": self.dim,
                "index_type": "numpy_fallback",
                "path": self.path
            }

        def _save(self) -> None:
            try:
                with open(f"{self.path}.texts", "wb") as f:
                    pickle.dump(self.texts, f)
                with open(f"{self.path}.metadata", "wb") as f:
                    pickle.dump(self.metadata, f)
                if self.embeddings is not None:
                    np.save(f"{self.path}.embeddings", self.embeddings)
            except Exception as e:
                logger.error(f"Error saving store: {e}")

        def clear(self) -> None:
            self.texts = []
            self.metadata = []
            self.embeddings = None
            self._save()

        def __len__(self) -> int:
            return 0 if self.embeddings is None else int(self.embeddings.shape[0])
