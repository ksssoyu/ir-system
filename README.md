# Fairy Tale & Folktale Information Retrieval System

This system has been developed as part of an assignment for the Natural Language Processing and Information Retrieval course at Chung-Ang University.

## Introduction
The **Fairy Tale & Folktale IR System** is a specialized information retrieval (IR) system designed for efficiently searching and retrieving fairy tales and folktales based on titles, summaries, full text, and book metadata.

This project was inspired by my personal interest in **reading English fairy tales and folktales** as a way to improve my language skills. When selecting a topic for this assignment, I was encouraged to choose a domain based on my own interests. Since I had already been exploring fairy tales and folktales, I thought it would be useful to create a system that allows users to **easily search for and retrieve these stories based on specific conditions**. This system aims to provide an efficient and structured way for users to navigate a diverse collection of folklore.

## Data Collection & Crawling Rules
To build the Fairy Tale & Folktale IR System, a total of 441 fairy tales and folktales were collected from World of Tales. The dataset consists of a diverse selection of fairy tales from Andrew Lang's collections, Grimm's fairy tales, and traditional folktales from various cultures.

### Crawling Rules
To ensure the integrity and organization of the collected data, the following crawling rules were applied:

✅ **Data Source**

- The stories were scraped from **World of Tales** (📖 link: https://www.worldoftales.com/), specifically from categorized collections such as European, Asian, African, and American folktales.

✅ **Extracted Information**

- **Title**: The title of each fairy tale or folktale was extracted from the `<h1>` tag with different possible class names (GXL font, GXL, GL).

- **Summary**: The summary section was extracted from the `<div>` tag with the class "box4". If no summary was available, it was marked as "None".

- **Story Text**: The main content of the story was retrieved from the `<div>` tag with the class "GM" and id="text". Only paragraphs (`<p>`) inside this section were stored as the main text.

- **Book Information**: Additional book metadata was extracted from the `<div>` tag with the class "books". If no information was available, it was marked as "None".

✅ **File Naming & Storage**

- Special characters were removed from titles to ensure safe file names.

- The format of the saved text files follows a structured layout:

```
Title: [Story Title]

Summary:
[Story Summary]

Story Text:
[Full Story Text]

Book Info:
[Book Metadata]
```
