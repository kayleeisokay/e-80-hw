import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # If page has no outgoing links, then transition_model should
    # return a probability distribution with all pages with equal probability
    probability_dist = {}
    if corpus.get(page) is None or len(corpus.get(page)) == 0:
        for page in corpus:
            probability_dist[page] = 1 / len(corpus)
    else:
        # Assign probability to linked pages, equally distributing
        # damping factor among all linked pages
        linked_pages = corpus.get(page)
        num_linked_pages = len(linked_pages)
        for linked_page in linked_pages:
            probability_dist[linked_page] = damping_factor / num_linked_pages

        # Distribute remaining probability to all pages
        total_pages = len(corpus)
        for page in corpus:
            # Avoid key error
            if page in probability_dist:
                probability_dist[page] += (1 - damping_factor) / total_pages
            else:
                probability_dist[page] = (1 - damping_factor) / total_pages

    return probability_dist


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    sample_pages = []

    # Random initialization
    initial_page = random.choice(list(corpus.keys()))
    curr_page = initial_page

    for i in range(n):
        transition_probs = transition_model(corpus, curr_page, damping_factor)

        # population are the values
        states = list(transition_probs.keys())
        # weights are the probabilities
        probs = list(transition_probs.values())

        # Sample from categorical distribution
        new_page = random.choices(states, probs, k=1)[0]
        sample_pages.append(new_page)
        curr_page = new_page

    # Sum up unique values and divide by the toal
    total = len(sample_pages)
    count = {value: sample_pages.count(value) for value in set(sample_pages)}

    probability_dist = {key: count[key] / total for key in count}

    return probability_dist


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_ranks = {}
    initial_rank = 1 / len(corpus)

    for page in corpus:
        page_ranks[page] = initial_rank

    while True:

        new_ranks = {}
        for page in corpus:
            new_rank = (1 - damping_factor) / len(corpus)
            # Find inbound pages
            for page_2 in corpus:
                linked_pages = corpus[page_2]
                # if page is an inbound page
                if page in linked_pages:
                    new_rank += damping_factor * page_ranks[page_2] / len(linked_pages)
                # A page that has no links at all should be interpreted as
                # having one link for every page in the corpus
                elif len(linked_pages) == 0:
                    new_rank += damping_factor * page_ranks[page_2] / len(corpus)
            new_ranks[page] = new_rank

        # update the new
        diff = [abs(new_ranks[page] - page_ranks[page]) for page in page_ranks]
        if all(d < 0.001 for d in diff):
            break
        page_ranks = new_ranks

    return page_ranks


if __name__ == "__main__":
    main()
