import sys
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from crawler import extract_wikipedia_page
from select_topics import pick_two




def compute_similarity(target_page, candidate_pages, model):
    # Combine title and summary for embedding
    text1 = f"{target_page['title']}. {target_page['summary']}"

    # Generate embeddings
    target_embeddings = model.encode([text1])
    target_embeddings = target_embeddings / np.linalg.norm(target_embeddings, axis=1, keepdims=True)
    
    candidate_embeddings = model.encode(candidate_pages)
    candidate_embeddings = candidate_embeddings / np.linalg.norm(candidate_embeddings, axis=1, keepdims=True)

    
    
    # Compute cosine similarity
    sim = cosine_similarity(target_embeddings, candidate_embeddings)[0]
    best_idx = np.argmax(sim)
    
    if best_idx == -1:
        return None
    # Return the best matching candidate page
    return candidate_pages[best_idx], float(sim[best_idx])

def get_page(title):
    if title in CACHE:
        return CACHE[title]
    page = extract_wikipedia_page(title)
    CACHE[title] = page
    return page


if __name__ == "__main__":
    # Pick two topics
    # start_topic, target_page = pick_two()
    start_topic, target_page = "Association football", "SpaceX"
    print(f"Start Topic: {start_topic}")
    print(f"End Topic: {target_page}")
    
    max_steps = 10
    print(f"Max steps: {max_steps}")
    
    CACHE = {}


    # Extract Wikipedia pages
    start_page = get_page(start_topic)
    target_page = get_page(target_page)
    
    if not start_page or not target_page:
        print("Could not retrieve one of the pages.")
        sys.exit(1)
        
    path = [start_page['title']]

    # Load pre-trained model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    while start_page["title"] != target_page["title"] and max_steps > 0:
        max_steps -= 1
        print(f"Step {10 - max_steps}: {start_page['title']} -> {target_page['title']}")
        
        # If we reach the target page, break
        if start_page['title'] == target_page['title']:
            print("Reached target page!")
            break
        
        # If we run out of internal links, break
        if not start_page['internal_links']:
            print("No more internal links to follow.")
            break
    
        # Prepare candidate pages from internal links of the start page
        candidate_pages = []
        for link in start_page['internal_links']:
            candidate_pages.append(link["title"])
            
        if not candidate_pages:
            print("No candidate pages found from the end topic.")
            sys.exit(1)
            
        # print(candidate_pages[:10])
        # Compute similarity and find the best matching page
        best_match = compute_similarity(target_page, candidate_pages, model)
        print(f"Best matching page to {target_page['title']} from links in {start_page['title']} :")
        print(best_match)
        
        path.append(best_match[0])
        start_page = get_page(best_match[0])
        
    
