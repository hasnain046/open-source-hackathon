# Module: app.services.deduplicator
# Description: Service implementing SHA-256 exact-match and MinHash LSH near-duplicate detection for syndication.

import hashlib
import re


class MinHashLSHDeduplicator:
    def __init__(self, num_hashes=64, threshold=0.82):
        self.num_hashes = num_hashes
        self.threshold = threshold
        self.prime = 4294967291  # Large prime
        
        # Generate deterministic linear hash function parameters: h(x) = (a*x + b) % prime
        self.hash_params = []
        for i in range(self.num_hashes):
            a = (i * 10007 + 12345) % self.prime
            b = (i * 48611 + 67890) % self.prime
            if a == 0:
                a = 1
            self.hash_params.append((a, b))
        
        # In-memory storage of signatures of the current run/window
        # Mappings: article_id -> signature list
        self.articles = {}

    def _get_shingles(self, text: str) -> set:
        """Tokenize text into lowercased word bigrams (shingles) to capture phrasal similarities."""
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s]", "", text)
        words = text.split()
        if len(words) < 2:
            return set(words)
        shingles = set()
        for i in range(len(words) - 1):
            shingles.add(f"{words[i]} {words[i+1]}")
        return shingles

    def _compute_signature(self, shingles: set) -> list:
        """Compute the MinHash signature of a set of shingles."""
        if not shingles:
            return [self.prime] * self.num_hashes
            
        shingle_hashes = [
            int(hashlib.md5(shingle.encode("utf-8")).hexdigest(), 16) 
            for shingle in shingles
        ]
        
        signature = []
        for a, b in self.hash_params:
            min_val = self.prime
            for sh_hash in shingle_hashes:
                val = (a * sh_hash + b) % self.prime
                if val < min_val:
                    min_val = val
            signature.append(min_val)
        return signature

    def register_article(self, article_id: str, text: str):
        """Pre-calculate and register an article signature in the tracking dictionary."""
        shingles = self._get_shingles(text)
        signature = self._compute_signature(shingles)
        self.articles[article_id] = signature

    def is_duplicate(self, text: str, article_id: str = "") -> str | None:
        """Check if article text matches a previously registered article above the similarity threshold.
        Returns the parent article ID if matched, else None."""
        shingles = self._get_shingles(text)
        if not shingles:
            return None
            
        signature = self._compute_signature(shingles)
        
        best_match_id = None
        best_sim = 0.0
        
        for existing_id, existing_sig in self.articles.items():
            # Estimate Jaccard Similarity by the ratio of identical hash values in the signature
            matches = sum(1 for x, y in zip(signature, existing_sig) if x == y)
            similarity = matches / self.num_hashes
            if similarity > best_sim:
                best_sim = similarity
                best_match_id = existing_id
                
        if best_sim >= self.threshold:
            return best_match_id
            
        # Register signature if we're assigning a new entry
        if article_id:
            self.articles[article_id] = signature
            
        return None


class DeduplicatorService:
    @staticmethod
    def get_sha256_hash(text: str) -> str:
        """Calculate exact SHA-256 signature for URLs and headlines."""
        return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()
