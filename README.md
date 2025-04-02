# Fairy Tale & Folktale Information Retrieval System

This system has been developed as part of an assignment for the Natural Language Processing and Information Retrieval course at Chung-Ang University.

## Introduction
The **Fairy Tale & Folktale IR System** is a specialized information retrieval (IR) system designed for efficiently searching and retrieving fairy tales and folktales based on titles, summaries, full text, and book metadata.

This project was inspired by my personal interest in **reading English fairy tales and folktales** as a way to improve my language skills. When selecting a topic for this assignment, I was encouraged to choose a domain based on my own interests. Since I had already been exploring fairy tales and folktales, I thought it would be useful to create a system that allows users to **easily search for and retrieve these stories based on specific conditions**. This system aims to provide an efficient and structured way for users to navigate a diverse collection of folklore.

To build the Fairy Tale & Folktale IR System, a total of 441 fairy tales and folktales were collected from **World of Tales**(📖 link: https://www.worldoftales.com/). The dataset consists of a diverse selection of fairy tales from Andrew Lang's collections, Grimm's fairy tales, and traditional folktales from various cultures.

## 🔧 How to Run the System
The system consists of two main components:

### 1. Index Builder

This component reads the 441 crawled fairy tale documents and builds an inverted index.

```
python index_builder.py
```

- Downloads necessary NLTK resources if not already installed.

- Preprocesses each document (including tokenization, lemmatization, stopword removal, vocabulary filtering).

- Stores the dictionary and document mapping in JSON files:

  - **index/dictionary.json**: contains term → {df, postings}

  - **index/doc_id_map.json**: maps doc_id to file names


### 2. Search Engine
Launches an interactive search interface that supports both Boolean and Vector Space models.

```
python search_engine.py
```

- **Prompts user to choose between:**

  - **boolean** – exact matching using logical operators

  - **vector** – ranked retrieval using TF-IDF cosine similarity

- **Users can input natural queries like:**

  - brave and princess

  - (queen OR princess) AND NOT (prince OR king)

  - dragon cave fire (vector mode)


### 3. Evaluation
Measures the performance of the **Boolean** IR system using **Precision, Recall, and F<sub>β</sub>-score**.

```
python evaluate.py
```

- Automatically loads a query and its manually constructed ground truth file (in ground_truth/ directory)

- Processes the query using the Boolean model

- **Calculates:**

  - **Precision** – fraction of retrieved documents that are relevant

  - **Recall** – fraction of relevant documents that are retrieved

  - **F<sub>β</sub>-score** – harmonic mean that balances precision and recall, with β=0.5 to emphasize precision

- Output includes:

  - Query used

  - Retrieved and relevant document counts

  - Matched filenames

  - Precision, Recall, and F<sub>β</sub>-score metrics
