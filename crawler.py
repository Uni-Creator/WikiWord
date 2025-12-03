from bs4 import BeautifulSoup
import requests
import wikipediaapi
import urllib.parse
import time



def extract_wikipedia_page(title, retries=3, backoff=1.5, timeout=15):
    """
    Robust Wikipedia page extractor with retry logic.
    - Retries network requests
    - Recovers from timeouts
    - Avoids 403 with User-Agent
    - Filters internal links properly
    """

    # Initialize Wikipedia API ONCE per function call
    wiki = wikipediaapi.Wikipedia(
        user_agent="WikiWorldBot (abhayr24564@gmail.com)",
        language="en",
        extract_format=wikipediaapi.ExtractFormat.HTML
    )

    # Retry loop
    for attempt in range(retries):
        try:
            # ------ Fetch Metadata (fast) ------
            page = wiki.page(title)
            if not page.exists():
                return None

            page_title = page.title
            page_summary = page.summary

            # ------ Fetch Full HTML (slow + network risky) ------
            headers = {'User-Agent': 'WikiWorldBot (abhayr24564@gmail.com)'}

            response = requests.get(page.fullurl, headers=headers, timeout=timeout)
            response.raise_for_status()  # triggers HTTPError for 4xx/5xx

            soup = BeautifulSoup(response.content, 'html.parser')
            content_div = soup.find(id="mw-content-text")
            page_content = str(content_div) if content_div else ""

            # ------ Extract Internal Links ------
            internal_links = []
            if content_div:
                for link in content_div.find_all('a', href=True):
                    href = link['href']

                    # Only internal wiki links: /wiki/<Page>
                    if not href.startswith('/wiki/'):
                        continue

                    file_name = href.split('/')[-1]
                    if ':' in file_name:
                        continue  # Skip File:, Category:, Template:, etc.

                    # Extract clean page name
                    raw = file_name.split('#')[0].split('?')[0]
                    raw = urllib.parse.unquote(raw).replace('_', ' ')

                    link_title = link.get_text(strip=True)

                    # Skip disambiguation links
                    if "disambiguation" in raw.lower() or "disambiguation" in link_title.lower():
                        continue

                    internal_links.append({
                        'title': link_title,
                        'page': raw,
                        'url': href
                    })

            # ------ Deduplicate links ------
            seen = set()
            unique_links = []
            for link in internal_links:
                if link['page'] not in seen:
                    seen.add(link['page'])
                    unique_links.append(link)

            # SUCCESS → return result
            return {
                'title': page_title,
                'summary': page_summary,
                'content': page_content,
                'internal_links': unique_links
            }

        except (requests.exceptions.RequestException, Exception) as e:
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
                continue
            return None
