import sys
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from crawler import extract_wikipedia_page
from select_topics import pick_two


def compute_similarity(target_page, candidates, model):
    target_text = f"{target_page['title']}. {target_page['summary']}"
    target_emb = model.encode([target_text])
    target_emb = target_emb / np.linalg.norm(target_emb, axis=1, keepdims=True)

    candidate_emb = model.encode(candidates)
    candidate_emb = candidate_emb / np.linalg.norm(candidate_emb, axis=1, keepdims=True)

    sim = cosine_similarity(target_emb, candidate_emb)[0]
    idx = int(np.argmax(sim))
    return candidates[idx], float(sim[idx])


def get_page(title, cache):
    if title in cache:
        return cache[title]
    page = extract_wikipedia_page(title)
    cache[title] = page
    return page


def run_navigation(start_title, target_title, max_steps=15):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    cache = {}

    start_page = get_page(start_title, cache)
    target_page = get_page(target_title, cache)

    if not start_page or not target_page:
        print("Could not retrieve one of the pages.")
        sys.exit(1)

    path = [start_page['title']]

    steps_left = max_steps
    while start_page["title"] != target_page["title"] and steps_left > 0:
        steps_left -= 1
        print(f"Step {max_steps - steps_left}: {start_page['title']} -> {target_page['title']}")

        links = start_page['internal_links']
        if not links:
            print("No internal links remaining.")
            break

        candidates = [link["title"] for link in links]

        best_title, score = compute_similarity(target_page, candidates, model)
        print(f"Best match: {best_title} (score={score:.4f})")
        path.append(best_title)

        if best_title == target_page['title']:
            print("Target reached.")
            break

        start_page = get_page(best_title, cache)

    return path


if __name__ == "__main__":
    start, target = pick_two()
    print(f"Start Topic: {start}")
    print(f"End Topic: {target}")

    final_path = run_navigation(start, target, max_steps=15)

    print("\nFinal Path:")
    for i, title in enumerate(final_path, start=1):
        print(f"{i}. {title}")
