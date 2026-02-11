"""Multi-source image search with relevance scoring."""

from typing import List, Optional
from ..api.unsplash_client import UnsplashClient
from ..api.pexels_client import PexelsClient
from ..api.pixabay_client import PixabayClient
from ..storage.models import ImageResult, ImageSource
from ..utils.logger import LoggerMixin
from ..utils.config import Config


class ImageSearchService(LoggerMixin):
    """Search for images across multiple sources with cascade strategy."""

    def __init__(self, config: Config):
        """Initialize image search service."""
        self.config = config
        self.minimum_score = config.minimum_relevance_score
        
        self.clients = {}
        if config.is_source_enabled("unsplash"):
            self.clients[ImageSource.UNSPLASH] = UnsplashClient(config.get_api_key("unsplash"))
        if config.is_source_enabled("pexels"):
            self.clients[ImageSource.PEXELS] = PexelsClient(config.get_api_key("pexels"))
        if config.is_source_enabled("pixabay"):
            self.clients[ImageSource.PIXABAY] = PixabayClient(config.get_api_key("pixabay"))
        
        self.source_priorities = config.source_priorities

    def search_image(self, keywords: List[str]) -> Optional[ImageResult]:
        """Search for best matching image across all sources."""
        self.logger.info(f"Searching for image with keywords: {keywords}")
        
        query = " ".join(keywords)
        all_results = []
        
        for source, priority in sorted(self.source_priorities.items(), key=lambda x: x[1]):
            source_enum = ImageSource(source)
            if source_enum not in self.clients:
                continue
            
            try:
                results = self._search_source(source_enum, query)
                scored_results = [(r, self.score_image_relevance(r, keywords)) for r in results]
                all_results.extend(scored_results)
                
                best = max(scored_results, key=lambda x: x[1], default=(None, 0))
                if best[0] and best[1] >= self.minimum_score:
                    self.logger.info(f"Found good match on {source} (score: {best[1]:.2f})")
                    best[0].relevance_score = best[1]
                    return best[0]
                    
            except Exception as e:
                self.logger.error(f"Error searching {source}: {e}")
                continue
        
        if all_results:
            best = max(all_results, key=lambda x: x[1])
            if best[1] >= self.minimum_score * 0.8:
                self.logger.warning(f"Using lower-scored image (score: {best[1]:.2f})")
                best[0].relevance_score = best[1]
                return best[0]
        
        if len(keywords) > 2:
            self.logger.info("No good match, trying with fewer keywords")
            return self.search_image(keywords[:2])
        
        self.logger.warning("No suitable image found")
        return None

    def _search_source(self, source: ImageSource, query: str) -> List[ImageResult]:
        """Search specific source for images."""
        client = self.clients.get(source)
        if not client:
            return []
        
        try:
            return client.search_images(query, per_page=5)
        except Exception as e:
            self.logger.error(f"Failed to search {source.value}: {e}")
            return []

    def score_image_relevance(self, image: ImageResult, keywords: List[str]) -> float:
        """Score image relevance based on keywords, quality, and source."""
        score = 0.0
        
        title_lower = (image.title or "").lower()
        keyword_matches = sum(1 for kw in keywords if kw.lower() in title_lower)
        score += (keyword_matches / len(keywords)) * 0.6
        
        if image.width >= 1920 and image.height >= 1080:
            score += 0.2
        elif image.width >= 1280 and image.height >= 720:
            score += 0.1
        
        source_scores = {"unsplash": 0.2, "pexels": 0.15, "pixabay": 0.1}
        score += source_scores.get(image.source.value, 0.05)
        
        return min(score, 1.0)
