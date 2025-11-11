import sys
from sqlmodel import create_engine, SQLModel, Session, text
from core.config import settings
from models import MedicalAbstract
from Bio import Entrez
from sentence_transformers import SentenceTransformer
import time

# --- Configuration ---
Entrez.email = "your_email@example.com"  # Be polite to NCBI, tell them who you are
SEARCH_TERM = "nutrition AND diabetes"
MAX_PAPERS = 500  # Start small; 500 papers is fast. You can increase this later.
BATCH_SIZE = 100  # Process 100 papers at a time
EMBEDDING_MODEL = 'all-MiniLM-L6-v2' # 384 dimensions, fast and free

def initialize_database(engine):
    """Ensures the pgvector extension is enabled and creates tables."""
    print("Initializing database...")
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        SQLModel.metadata.create_all(engine)
        print("Database initialized and pgvector extension is active.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        print("Please ensure you have run 'create extension if not exists vector;' in your Supabase SQL Editor.")
        sys.exit(1)

def fetch_pubmed_abstracts():
    """Fetches paper abstracts from the PubMed API."""
    print(f"Fetching {MAX_PAPERS} paper IDs for term: '{SEARCH_TERM}'...")
    handle = Entrez.esearch(db="pubmed", term=SEARCH_TERM, retmax=MAX_PAPERS)
    record = Entrez.read(handle)
    handle.close()
    
    id_list = record["IdList"]
    print(f"Found {len(id_list)} IDs. Fetching abstracts...")
    
    handle = Entrez.efetch(db="pubmed", id=id_list, rettype="medline", retmode="xml")
    records = Entrez.read(handle)
    handle.close()
    
    print("Abstracts fetched. Processing...")
    
    papers = []
    for record in records['PubmedArticle']:
        try:
            article = record['MedlineCitation']['Article']
            pmid = record['MedlineCitation']['PMID']
            title = article['ArticleTitle']
            
            # Find the abstract text
            abstract_text = ""
            if 'Abstract' in article:
                abstract_parts = article['Abstract']['AbstractText']
                # Sometimes abstract is in parts, join them
                if isinstance(abstract_parts, list):
                    abstract_text = " ".join(abstract_parts)
                else:
                    abstract_text = abstract_parts
            
            # Get publication date
            pub_date = ""
            if 'ArticleDate' in article:
                pub_date = f"{article['ArticleDate'][0]['Year']}-{article['ArticleDate'][0]['Month']}-{article['ArticleDate'][0]['Day']}"
            
            if title and abstract_text:
                papers.append({
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract_text,
                    "publication_date": pub_date
                })
        except KeyError:
            # Skip paper if it's missing key fields (e.g., title, abstract)
            continue
            
    print(f"Successfully processed {len(papers)} papers with abstracts.")
    return papers

def load_data_into_db(engine, papers, model):
    """Generates embeddings and loads papers into the DB in batches."""
    print(f"Starting to embed and load {len(papers)} papers in batches of {BATCH_SIZE}...")
    
    with Session(engine) as session:
        for i in range(0, len(papers), BATCH_SIZE):
            batch_papers = papers[i : i + BATCH_SIZE]
            
            # 1. Get abstracts to embed
            abstracts_to_embed = [paper['abstract'] for paper in batch_papers]
            
            # 2. Generate embeddings (the "AI" part)
            print(f"  ... Generating embeddings for batch {i // BATCH_SIZE + 1}...")
            embeddings = model.encode(abstracts_to_embed, show_progress_bar=False)
            
            # 3. Create model objects to add
            objects_to_add = []
            for paper, embedding in zip(batch_papers, embeddings):
                objects_to_add.append(
                    MedicalAbstract(
                        pmid=paper['pmid'],
                        title=paper['title'],
                        abstract=paper['abstract'],
                        publication_date=paper['publication_date'],
                        embedding=embedding.tolist() # Convert numpy array to list
                    )
                )
            
            # 4. Add and commit to the database
            session.add_all(objects_to_add)
            session.commit()
            print(f"  ... Committed batch {i // BATCH_SIZE + 1} ({min(i + BATCH_SIZE, len(papers))}/{len(papers)} papers)")
            
            # Be polite to APIs and databases
            time.sleep(0.5) 
            
    print("Data loading complete!")

def main():
    try:
        # Connect to the database
        engine = create_engine(settings.DATABASE_URL)
        
        # 1. Initialize DB and pgvector extension
        initialize_database(engine)
        
        # 2. Load the (free) AI embedding model
        print(f"Loading embedding model: '{EMBEDDING_MODEL}'...")
        # This will download the model once and cache it
        model = SentenceTransformer(EMBEDDING_MODEL)
        print("Embedding model loaded.")
        
        # 3. Fetch papers from PubMed
        papers = fetch_pubmed_abstracts()
        
        if not papers:
            print("No papers found. Exiting.")
            sys.exit(0)
            
        # 4. Embed papers and load into the database
        load_data_into_db(engine, papers, model)
        
        print("\n--- SUCCESSFULLY POPULATED YOUR VECTOR DATABASE ---")
        print(f"Your Supabase DB now contains {len(papers)} medical abstracts, each with a 384-dimension vector embedding.")
        print("You are now ready for Part 2: Building the RAG API.")
        
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your DATABASE_URL in the .env file and ensure your Supabase project is active.")

if __name__ == "__main__":
    main()
