from ast import For

from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from rich import print
#Think of BeautifulSoup as a tool for navigating the webpage's HTML elements.
from bs4 import BeautifulSoup
from readability import Document
#Trafilatura is a Python library designed to extract the main text from webpages, especially articles, blogs, and news pages.
import trafilatura
import re

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    #results is likely a dictionary containing a list of search-result dictionaries.
    results = tavily.search(query=query, search_depth='advanced', max_results=1)
        
    out = []
    
    for r in results['results']:        
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content'][:300]}\n"
        )
    final_output = "\n-----\n".join(out)
    return final_output

@tool
def scrape_url(url: str) -> str:
    """Scrape and extract clean readable content from a URL.
    Uses multiple extraction strategies for better reliability."""
    #multiple extraction strategies — means the function tries different libraries if the previous method doesn't extract enough text.
    
    #Setting HTTP headers to mimic a real browser request
    #Think of headers as a small note you send along with your request to a website, telling the website a little about your request.
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }
    
    try:
        #----Fetch Page----
        response = requests.get(url, headers=headers, timeout=15)
        #200 OK — normally continues successfully.
        #404 Not Found / 403 Forbidden / 500 Internal Server Error - Raises an HTTPError
        response.raise_for_status()  # Raise an exception for HTTP errors. 
        html = response.text # The raw HTML content of the page.
        
        #To extract readable content from the HTML, we can use multiple strategies.
        
        #-----------------------------------------
        #Strategy 1 -> trafilatura (Best for articles/blog posts)
        #-----------------------------------------
        extracted = trafilatura.extract(html, include_comments=False, include_tables=False)
        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r'\s+',' ', extracted)
            return cleaned[:5000]
        
        #-----------------------------------------
        #Strategy 2 -> Readability and BeautifulSoup
        #-----------------------------------------
        #Document comes from the Readability library
        #It analyzes the HTML and tries to identify the main content area of the webpage.
        #For example, it tries to distinguish the article from navigation menus and other surrounding page elements.
        doc = Document(html)
        clean_html = doc.summary()#returns an HTML fragment containing the content Readability identifies as the main content.
        #The result is still HTML, so you need another step to convert it into text.
        #Using BeautifulSoup to convert the HTML fragment into plain text
        soup = BeautifulSoup(clean_html, "html.parser") #parses the HTML into a structure that Python can work with.
        #Removing Unwanted Tags
        for tag in soup(["script","style","nav","footer","header","aside","form"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        
        if text and len(text.strip()) > 200:
            cleaned = re.sub(r'\s+',' ',text)
            return cleaned[:5000]
        
        #---------------------------------------------
        #Strategy 3 -> fallback full page extraction
        #---------------------------------------------
        #This time, we pass the original HTML rather than the HTML extracted by Readability.
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script","style","nav","footer","header","aside","form"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        
        cleaned = re.sub(r'\s+', ' ', text)
        if cleaned:
            return cleaned[:5000]
        return "Could not extract meaningful content from the page"
            
    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."
    except requests.exceptions.HTTPError as e:
        return f"HTTP error occurred while scraping the URL: {str(e)}"
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"