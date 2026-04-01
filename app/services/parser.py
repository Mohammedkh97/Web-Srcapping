from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re


class HTMLParser:
    """Parser for extracting content from HTML pages."""
    
    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, 'lxml')
    
    def extract_articles(self) -> List[Dict]:
        """
        Extract articles from the HTML.
        Optimized for legal consultancy and blog websites.
        """
        articles = []
        
        # Common article selectors for various website structures
        article_selectors = [
            'article',
            '.post',
            '.blog-post',
            '.entry',
            '.article',
            '.post-item',
            '[class*="article"]',
            '[class*="post"]',
            '.card',
            '.item'
        ]
        
        # Try each selector
        for selector in article_selectors:
            elements = self.soup.select(selector)
            if elements:
                for element in elements:
                    article = self._extract_article_data(element)
                    if article.get('title') or article.get('content'):
                        articles.append(article)
                
                if articles:
                    break
        
        # If no articles found with selectors, try to extract from main content
        if not articles:
            articles = self._extract_from_main_content()
        
        return articles
    
    def _extract_article_data(self, element) -> Dict:
        """Extract data from a single article element."""
        article = {}
        
        # Extract title
        title_selectors = [
            'h1', 'h2', 'h3',
            '.title', '.post-title', '.entry-title',
            '[class*="title"]', 'a[rel="bookmark"]'
        ]
        for sel in title_selectors:
            title_elem = element.select_one(sel)
            if title_elem:
                article['title'] = self._clean_text(title_elem.get_text())
                # Get link from title if available
                link = title_elem.find('a')
                if link and link.get('href'):
                    article['url'] = link.get('href')
                break
        
        # Extract URL if not found in title
        if 'url' not in article:
            link = element.find('a', href=True)
            if link:
                article['url'] = link.get('href')
        
        # Extract content/excerpt
        content_selectors = [
            '.content', '.post-content', '.entry-content',
            '.excerpt', '.summary', '.description',
            'p', '[class*="content"]', '[class*="excerpt"]'
        ]
        for sel in content_selectors:
            content_elem = element.select_one(sel)
            if content_elem:
                text = self._clean_text(content_elem.get_text())
                if len(text) > 50:  # Only use if substantial content
                    article['content'] = text
                    article['excerpt'] = text[:300] + '...' if len(text) > 300 else text
                    break
        
        # Extract date
        date_selectors = [
            'time', '.date', '.post-date', '.entry-date',
            '[class*="date"]', '[datetime]', '.meta'
        ]
        for sel in date_selectors:
            date_elem = element.select_one(sel)
            if date_elem:
                # Try datetime attribute first
                date_str = date_elem.get('datetime') or self._clean_text(date_elem.get_text())
                if date_str and self._looks_like_date(date_str):
                    article['date'] = date_str
                    break
        
        # Extract author
        author_selectors = [
            '.author', '.post-author', '.byline',
            '[class*="author"]', '[rel="author"]'
        ]
        for sel in author_selectors:
            author_elem = element.select_one(sel)
            if author_elem:
                article['author'] = self._clean_text(author_elem.get_text())
                break
        
        # Extract image
        img = element.find('img')
        if img:
            article['image_url'] = img.get('src') or img.get('data-src')
        
        # Extract category
        category_selectors = [
            '.category', '.cat', '[class*="category"]',
            '.tag', '[rel="tag"]'
        ]
        for sel in category_selectors:
            cat_elem = element.select_one(sel)
            if cat_elem:
                article['category'] = self._clean_text(cat_elem.get_text())
                break
        
        return article
    
    def _extract_from_main_content(self) -> List[Dict]:
        """Fallback: extract content from main page areas."""
        articles = []
        
        # Try to find main content area
        main_selectors = ['main', '#content', '.content', '#main', '.main']
        
        for sel in main_selectors:
            main_elem = self.soup.select_one(sel)
            if main_elem:
                # Get all paragraphs
                paragraphs = main_elem.find_all('p')
                if paragraphs:
                    content = ' '.join([self._clean_text(p.get_text()) for p in paragraphs])
                    if content:
                        # Get page title
                        title = self.soup.find('h1')
                        if not title:
                            title = self.soup.find('title')
                        
                        articles.append({
                            'title': self._clean_text(title.get_text()) if title else 'Untitled',
                            'content': content,
                            'excerpt': content[:300] + '...' if len(content) > 300 else content
                        })
                        break
        
        return articles
    
    def extract_all_links(self) -> List[Dict]:
        """Extract all links from the page."""
        links = []
        for a in self.soup.find_all('a', href=True):
            href = a.get('href')
            text = self._clean_text(a.get_text())
            if href and text:
                links.append({
                    'url': href,
                    'text': text
                })
        return links
    
    def extract_metadata(self) -> Dict:
        """Extract page metadata."""
        metadata = {}
        
        # Title
        title = self.soup.find('title')
        if title:
            metadata['title'] = self._clean_text(title.get_text())
        
        # Meta tags
        for meta in self.soup.find_all('meta'):
            name = meta.get('name') or meta.get('property', '')
            content = meta.get('content', '')
            
            if 'description' in name.lower():
                metadata['description'] = content
            elif 'keywords' in name.lower():
                metadata['keywords'] = content
            elif 'author' in name.lower():
                metadata['author'] = content
            elif 'og:image' in name:
                metadata['og_image'] = content
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text:
            return ''
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _looks_like_date(self, text: str) -> bool:
        """Check if text looks like a date."""
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # ISO format
            r'\d{1,2}/\d{1,2}/\d{2,4}',  # US/EU format
            r'\d{1,2}\s+\w+\s+\d{4}',  # "15 January 2024"
            r'\w+\s+\d{1,2},?\s+\d{4}',  # "January 15, 2024"
        ]
        for pattern in date_patterns:
            if re.search(pattern, text):
                return True
        return False


def parse_html(html: str) -> HTMLParser:
    """Create a parser instance for the given HTML."""
    return HTMLParser(html)
