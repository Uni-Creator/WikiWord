import os
import random

THIS_DIR = os.path.dirname(__file__)
TOPICS_FILE = os.path.join(THIS_DIR, 'topics.txt')


def load_topics(path=TOPICS_FILE):
    with open(path, 'r', encoding='utf-8') as f:
        topics = [line.strip() for line in f if line.strip()]
    return topics


def pick_two():
    topics = load_topics()
    if not topics:
        raise ValueError('No topics available in topics.txt')

    start, end = random.sample(topics, 2)

    # If both same (rare), pick a different end
    if start == end:
        remaining = [t for t in topics if t != start]
        end = random.choice(remaining)

    return start, end


if __name__ == '__main__':
    start_topic, end_topic = pick_two()

    # Print and expose variables
    print('Start topic:', start_topic)
    print('End topic:  ', end_topic)

    # Also print indices for reference
    topics = load_topics()
    try:
        print('\nTopics list (index: topic)')
        for i, t in enumerate(topics):
            print(f'{i}: {t}')
    except Exception:
        pass
