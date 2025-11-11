# 🩺 MedQuery: The AI Medical Research Bot

**MedQuery** is an intelligent, open-source application that allows you to "chat" with a database of verified medical research. It uses a **Retrieval-Augmented Generation (RAG)** pipeline to provide trustworthy, citable answers to complex medical questions, drawing *only* from a curated vector database of PubMed abstracts.

This project solves the problem of information overload and misinformation in health research by providing answers that are synthesized directly from scientific sources, complete with citations.



## ✨ Features

* **Trustworthy Answers:** The AI is restricted to *only* use the verified medical abstracts in its database. It cannot "make up" answers.
* **Direct Citations:** Every fact in a generated answer is linked directly to the PubMed abstract(s) it came from.
* **Vector Search:** Powered by `pgvector`, MedQuery understands the *semantic meaning* of your question, not just keywords.
* **Built-in Data Pipeline:** Includes a Python script to automatically download papers from the PubMed API, embed them, and load them into the database.
* **100% Free & Open-Source:** Built entirely on a modern, free-tier-friendly stack.

---

## 🚀 The RAG Architecture

This project is a complete RAG system built from scratch.

1.  **Data Ingestion (One-Time Script):**
    * `load_data.py` fetches abstracts from the **PubMed API**.
    * A **Hugging Face Sentence Transformer** (`all-MiniLM-L6-v2`) converts each abstract into a 384-dimension vector.
    * The abstracts and their vectors are loaded into a **Supabase PostgreSQL** database with the `pgvector` extension.

2.  **Live Query (The RAG Pipeline):**
    * A user asks a question in the **Next.js** frontend.
    * The **FastAPI** backend embeds the user's question into a vector.
    * FastAPI queries the **Supabase** vector database to "Retrieve" the 5 most semantically similar abstracts.
    * These abstracts (the "Context") are "Augmented" into a prompt for a **free, open-source LLM**.
    * The LLM "Generates" a final answer based *only* on the provided context.



---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | **Next.js (React)** | Interactive chat UI. Deployed on **Vercel**. |
| **Backend** | **FastAPI (Python)** | The RAG API, model-serving, and business logic. |
| **Database** | **Supabase (PostgreSQL)** | Primary database. |
| **Vector Search** | **`pgvector`** | For efficient semantic similarity search. |
| **Data Source** | **PubMed API** | Source of all medical abstracts. |
| **AI (Embedding)** | **Hugging Face `sentence-transformers`** | To create vectors (e.g., `all-MiniLM-L6-v2`). |
| **AI (Generation)**| **Hugging Face Inference API** | To run a free, open-source LLM (e.g., `TinyLlama`).|

---

## 🏁 Getting Started

You can get this entire project running for $0. It is broken into two main parts: the `medquery_dataloader` and the `medquery_app`.

### Part 1: Load The Data

First, you need to populate your vector database.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR-USERNAME/medquery.git](https://github.com/YOUR-USERNAME/medquery.git)
    cd medquery/medquery_dataloader
    ```

2.  **Set up Supabase:**
    * Create a free account on [Supabase.com](https://supabase.com).
    * Create a new project (e.g., "medquery").
    * Go to the **SQL Editor** and run this query to enable vector search:
        ```sql
        create extension if not exists vector;
        ```
    * Go to **Project Settings** > **Database** and copy your `psql` connection string.

3.  **Install & Configure:**
    * Create a `.env` file in the `medquery_dataloader` folder and add your connection string:
        ```env
        DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres"
        ```
    * Create a virtual environment and install the requirements:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        pip install -r requirements.txt
        ```

4.  **Run the Pipeline:**
    * This script will create the tables, download the embedding model, fetch papers from PubMed, and load them into your database.
    ```bash
    python load_data.py
    ```
    Your "smart" database is now ready!

### Part 2: Run the Application (Coming Soon)

*(This section is a placeholder for when you build the API and Frontend)*

1.  **Configure the Backend:**
    * Navigate to the `medquery_app/backend` folder.
    * Create a `.env` file with your `DATABASE_URL` and a `HF_TOKEN` from Hugging Face.
    * Install requirements and run: `uvicorn main:app --reload`

2.  **Configure the Frontend:**
    * Navigate to the `medquery_app/frontend` folder.
    * Create a `.env.local` file pointing to your FastAPI backend URL.
    * Install dependencies and run: `npm run dev`

---

## 🤝 How to Contribute

Contributions are welcome! This project is for learning and building a useful, open-source tool.

1.  **Fork the repository.**
2.  **Create a new feature branch:** `git checkout -b feat/YourAmazingFeature`
3.  **Commit your changes:** `git commit -m 'feat: Add YourAmazingFeature'`
4.  **Push to the branch:** `git push origin feat/YourAmazingFeature`
5.  **Open a Pull Request.**

Please adhere to this project's `CODE_OF_CONDUCT.md`.

---

## 📜 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

## 🙏 Acknowledgments

* The **Supabase** team for their amazing platform and `pgvector` support.
* **Hugging Face** for democratizing access to state-of-the-art models.
* The **National Center for Biotechnology Information (NCBI)** for providing public access to the PubMed database.
