import os
from typing import List, Dict, Any, Optional
import httpx
from backend.app.config.config import settings
from backend.app.core.logging import logger

class SearchService:
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.use_mock = not self._is_valid_key(self.api_key)
        if not self.use_mock:
            try:
                from tavily import TavilyClient
                self.client = TavilyClient(api_key=self.api_key)
                logger.info("Initialized Tavily Search Client.")
            except Exception as e:
                logger.error(f"Failed to load Tavily Python library: {e}. Using mock search.")
                self.use_mock = True

    def _is_valid_key(self, key: Optional[str]) -> bool:
        if not key:
            return False
        k_lower = key.lower()
        if "mock" in k_lower or "your_" in k_lower or len(key.strip()) < 10:
            return False
        return True

    async def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Executes a web search query. Falls back to generating realistic mock results 
        if Tavily keys are missing or api calls fail.
        """
        if self.use_mock:
            return self._generate_mock_results(query, max_results)

        try:
            logger.info(f"Executing search query on Tavily: {query}")
            # Tavily python SDK call (synchronous execution wrapped, or we can use async client if needed)
            # Since we want to keep it simple, we run the search call
            response = self.client.search(query=query, max_results=max_results, search_depth="basic")
            results = response.get("results", [])
            
            structured_results = []
            for item in results:
                # Map Tavily fields to our schema
                # Tavily returns 'title', 'url', 'content', and optionally others
                structured_results.append({
                    "title": item.get("title", "Search Result"),
                    "url": item.get("url", "https://example.com"),
                    "published_date": item.get("published_date") or None, # Some results contain published date
                    "source_type": "web",
                    "content": item.get("content", ""),
                    "relevance_score": item.get("score", 0.8)
                })
            return structured_results
            
        except Exception as e:
            logger.error(f"Tavily search failed for query '{query}': {e}. Falling back to mock results.")
            return self._generate_mock_results(query, max_results)

    def _generate_mock_results(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Generates realistic search results based on the search query terms 
        for development and testing purposes.
        """
        logger.info(f"Generating mock search results for: '{query}'")
        
        # Determine likely company name from query
        company = "Target Company"
        words = query.split()
        if words:
            # First few words are often the company name if we query like "{Company} overview"
            company = words[0].capitalize()

        q_lower = query.lower()
        
        if "product" in q_lower or "service" in q_lower:
            return [
                {
                    "title": f"Products and Services at {company} - Detailed Catalog",
                    "url": f"https://www.example-{company.lower()}.com/products",
                    "published_date": "2026-03-12",
                    "source_type": "web",
                    "content": f"Discover the complete product lineup of {company}, featuring their enterprise SaaS dashboard, automated customer outreach templates, and CRM data sync plug-ins.",
                    "relevance_score": 0.95
                },
                {
                    "title": f"Reviewing {company}'s AI Integration Solutions",
                    "url": "https://www.saas-reviews-blog.com/posts/ai-integration",
                    "published_date": "2026-04-20",
                    "source_type": "blog",
                    "content": f"{company}'s AI Assistant plugin connects to major browsers and offers automated summarization features that save sales teams up to 5 hours a week.",
                    "relevance_score": 0.88
                }
            ][:max_results]
            
        elif "risk" in q_lower or "competitor" in q_lower:
            return [
                {
                    "title": f"{company} Market Competitors & Analysis - Business Radar",
                    "url": "https://www.business-radar-news.com/competitors/market",
                    "published_date": "2026-05-01",
                    "source_type": "news",
                    "content": f"{company} competes directly with legacy CRM extension tools but distinguishes itself through deep learning wrappers and cheaper API cost profiles.",
                    "relevance_score": 0.92
                },
                {
                    "title": f"Operational Vulnerabilities and Security Challenges for AI Startups",
                    "url": "https://www.tech-security-insights.org/posts/startup-challenges",
                    "published_date": "2026-02-15",
                    "source_type": "web",
                    "content": f"Like many early-stage AI copilots, {company} faces risks related to rate limits from foundation LLM providers and data compliance regulations in the EU.",
                    "relevance_score": 0.85
                }
            ][:max_results]
            
        elif "news" in q_lower or "funding" in q_lower:
            return [
                {
                    "title": f"{company} Announces New $15M Series A Funding for Expansion",
                    "url": "https://www.techcrunch-mock.com/news/series-a",
                    "published_date": "2026-05-18",
                    "source_type": "news",
                    "content": f"{company} has closed a $15 million Series A round to accelerate growth, double their engineering headcount, and invest in proprietary model development.",
                    "relevance_score": 0.98
                },
                {
                    "title": f"{company} Partners with Cloud Providers for AI Scale-Up",
                    "url": f"https://www.example-{company.lower()}.com/press/partnership",
                    "published_date": "2026-06-02",
                    "source_type": "press_release",
                    "content": f"{company} today announced a strategic infrastructure partnership to leverage cloud computing databases and optimize API latencies for corporate users.",
                    "relevance_score": 0.94
                }
            ][:max_results]
            
        else:
            return [
                {
                    "title": f"{company} Company Profile: Overview and Business Model",
                    "url": f"https://www.example-{company.lower()}.com/about",
                    "published_date": "2026-01-10",
                    "source_type": "web",
                    "content": f"{company} provides state-of-the-art sales automation and business intelligence software. They focus on AI-driven workflows to streamline outreach and qualification.",
                    "relevance_score": 0.90
                }
            ][:max_results]
