import httpx
import urllib.parse
from typing import Optional
from app.config import get_settings


class ScrapedoService:
    """Service for interacting with Scrape.do API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.scrapedo_base_url
        self.token = self.settings.scrapedo_token
    
    async def scrape(
        self,
        url: str,
        render_js: bool = False,
        super_proxy: bool = False,
        geo_code: Optional[str] = None,
        timeout: int = 60
    ) -> dict:
        """
        Scrape a URL using Scrape.do API.
        
        Args:
            url: Target URL to scrape
            render_js: Whether to render JavaScript
            super_proxy: Use residential proxies
            geo_code: Geographic location code
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with 'success', 'html', and 'error' keys
        """
        if not self.token:
            return {
                "success": False,
                "html": None,
                "error": "Scrape.do token not configured"
            }
        
        # Encode the target URL
        encoded_url = urllib.parse.quote(url, safe='')
        
        # Build API URL with parameters
        api_url = f"{self.base_url}/?token={self.token}&url={encoded_url}"
        
        # Add optional parameters
        if render_js:
            api_url += "&render=true"
        if super_proxy:
            api_url += "&super=true"
        if geo_code:
            api_url += f"&geoCode={geo_code}"
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(api_url)
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "html": response.text,
                        "error": None
                    }
                else:
                    return {
                        "success": False,
                        "html": None,
                        "error": f"Scrape.do returned status {response.status_code}: {response.text[:200]}"
                    }
                    
        except httpx.TimeoutException:
            return {
                "success": False,
                "html": None,
                "error": f"Request timeout after {timeout} seconds"
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "html": None,
                "error": f"Request error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "html": None,
                "error": f"Unexpected error: {str(e)}"
            }


# Create singleton instance
scrapedo_service = ScrapedoService()
