## Features

* **Document Processing**: Automatically extracts text and tables from `.docx` files, intelligently chunks content, and identifies headings and list items.
* **AI-powered QA Generation**: Uses an OpenAI-compatible LLM to generate relevant question-answer pairs from the processed document chunks.
* **Question Paraphrasing**: Enhances search robustness by generating multiple paraphrased versions of each question, ensuring better semantic matching.
* **Vector Database for Search**: Stores question embeddings in a SQLite database, enabling fast and accurate semantic search for user queries.
* **Conversational Interface**: Provides a simple command-line interface for users to ask questions and receive answers.

## Project Structure

* `chunking.py`: Handles the extraction and intelligent chunking of content from `.docx` files. It parses document structure, identifies headings, lists, and tables, and segments the content into meaningful chunks.
* `embedding.py`: Manages the generation of QA pairs and their embeddings. It interacts with an LLM to create Q&A from chunks, paraphrases questions, and stores them along with their embeddings in a SQLite database (`qa.db`).
* `qa.py`: Provides the core functionality for searching and retrieving answers. It takes a user query, generates its embedding, performs a cosine similarity search against the stored QA embeddings, and returns the most relevant answer.
* `data/`: Directory to store the processed JSON chunks from the `.docx` files.
* `database/`: Directory to store the `qa.db` SQLite database.
* `doc/`: Directory where you should place your input `.docx` documents.
* `requirements.txt`: Lists all the necessary Python packages for the project.
