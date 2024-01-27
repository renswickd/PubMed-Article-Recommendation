def create_search_link(search_term):
    
    # sample link = https://pubmed.ncbi.nlm.nih.gov/?term=covid+19&filter=datesearch.y_1
    search_term_space_removed = search_term.replace(" ","+")
    
    return f"https://pubmed.ncbi.nlm.nih.gov/?term={search_term_space_removed}&filter=datesearch.y_1"