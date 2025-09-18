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
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probability = {}
    for p in corpus:
        probability[p] = (1-damping_factor)/len(corpus)

    links = corpus[page]
    if not links:
        links = set(corpus.keys())
    for p in links:
        probability[p] += damping_factor/len(links)

    return probability
    raise NotImplementedError

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    counts = {}
    pages = list(corpus.keys())
    for p in pages:
        counts[p] = 0

    current = random.choice(pages)
    counts[current] += 1

    for _ in range(1,n):
            dist = transition_model(corpus, current, damping_factor)
            population = list(dist.keys())
            weights = list(dist.values())
            current = random.choices(population, weights=weights, k=1)[0]
            counts[current] += 1

    pagerank = {}
    for p in pages:
        pagerank[p] = counts[p]/n

    return pagerank
    raise NotImplementedError

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    pages = list(corpus.keys())
    prob = {}
    for p in pages:
        prob[p] = 1/N
    
    def out_count(p):
        if len(corpus[p])>0:
            return len(corpus[p])
        else:
            return N
        
    def links_to(p):
        incoming = []
        for q in pages:
            if p in corpus[q] or len(corpus[q]) == 0:
                incoming.append(q)
        return incoming
            

    converged = False
    while not converged:
        converged = True
        new_prob = {}
        for p in pages:
            s = 0.0
            for q in links_to(p):
                cq = out_count(q)
                s += prob[q]/cq
            new_prob[p] = (1-damping_factor) / N + damping_factor*s

            if abs(new_prob[p] - prob[p])>0.001:
                converged = False
        prob = new_prob

    total = sum(prob.values())
    for p in pages:
        prob[p] = prob[p]/total

    return prob
    raise NotImplementedError

    

if __name__ == "__main__":
    main()
