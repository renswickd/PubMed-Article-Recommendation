from bs4 import BeautifulSoup
import requests
import chromadb
from pprint import pprint

from utils import create_search_link

client = chromadb.Client()

collection = client.create_collection(
      name="pubmed",
      metadata={"hnsw:space": "cosine"}
  )

metadata_url = create_search_link(input().strip()) #"https://pubmed.ncbi.nlm.nih.gov/?term=covid"
metadata_response = requests.get(metadata_url)

extracted_content = dict()
if metadata_response.status_code == 200:
    metadata_soup = BeautifulSoup(metadata_response.content, 'html.parser')
    metadata_content = metadata_soup.find_all('div', class_ = "docsum-content")

    for item in metadata_content:
        pmid = item.find("span", class_="docsum-pmid").text.strip()
        paper_name = item.find("a", class_="docsum-title").text.strip()
        author = item.find("span", class_="docsum-authors full-authors").text.strip()
        
        extracted_content[pmid] = {
                        "paper_name": paper_name,
                        "author":author
        }


for pmid in extracted_content.keys():
    
    abstarct_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    abstract_response = requests.get(abstarct_url)

    abstract_soup = BeautifulSoup(abstract_response.content, 'html.parser')
    abstract_content = abstract_soup.find_all('div', class_ = "article-page")
    
    for i in abstract_content:
        if i.find('div', class_="abstract-content selected"):
            abstarct = i.find('div', class_="abstract-content selected").text.strip()
            if abstarct:
                extracted_content[pmid]['abstract'] = abstarct

# print(extracted_content)
'''
extracted_content object will contain metadata of the results of search query(page 1)
output format:
{
    pmid1: {
        title : titleof article1,
        author : authors of article1,
        abstract : abstract of article1
        }
    pmid2: {
        title : titleof article2,
        author : authors of article2,
        abstract : abstract of article2
        }
    
}
'''

doc_list = []
pmid_list = []
for k in extracted_content.keys():
    if 'abstract' in extracted_content[k].keys():
    # print(extracted_content[k]['abstract'])
        doc_list.append(extracted_content[k]['abstract'])
        embeddings_list.append(list(model.encode(extracted_content[k]['abstract'])))
        # print(k)
        pmid_list.append(k)
        
meta = []
for i in range(len(pmid_list)):
    meta.append({"topic":term})
    
collection.add(
    embeddings = collection.get(ids=pmid_list, include=['embeddings'])['embeddings'],
    documents= doc_list,
    metadatas=meta,
    ids=pmid_list,
)

query = []
user_input = input("Enter the query: ") #Try "Haemophilia affects which age group?"
query.append(user_input)

results = collection.query(
    query_texts=query, #example in case when the search key was "haemophilia"
    n_results=len(pmid),
    include = ["embeddings","distances","documents"]
)

find_index = results['distances'][0].index(min(results['distances'][0]))
print(results['ids'][0][find_index])
print(results['documents'][0][find_index])
