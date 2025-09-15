---
title: "Building AI-Powered Software: Model Embeddings"
date: 2025-12-12
summary: "Learn how to build an AI agentic software that utilized vectorized knowledge database"
description: ""
tags: ["ai", "ai-agents", "generative-ai", "model-embeddings", "openai", "rag", "retrieval-augmented-generation", "java", "kotlin", "spring-boot", "python", "database", "postgresql", "vectors", "pgvector" ]
---

* https://www.datacamp.com/tutorial/introduction-to-text-embeddings-with-the-open-ai-api?dc_referrer=https%3A%2F%2Fcommunity.openai.com%2F
  * podstawy czym jest embedding, czym sa vectory
  * oraz to: https://www.tigerdata.com/blog/a-beginners-guide-to-vector-embeddings
* https://www.tigerdata.com/blog/postgresql-as-a-vector-database-using-pgvector
  * długi i bardzo szczegłowy artykuł - skupia się na samych vectorach i postgresie
  * oraz https://severalnines.com/blog/vector-similarity-search-with-postgresqls-pgvector-a-deep-dive
  * oraz https://www.postgresql.fastware.com/blog/how-to-store-and-query-embeddings-in-postgresql-without-losing-your-mind?utm_source=perplexity
  * oraz https://www.tigerdata.com/learn/using-pgvector-with-python
* https://www.tigerdata.com/blog/which-rag-chunking-and-formatting-strategy-is-best?utm_source=perplexity
  * chunkowanie danych raga
  * oraz https://mastra.ai/en/docs/rag/chunking-and-embedding
* https://neptune.ai/blog/building-llm-applications-with-vector-databases
  * jak pisac apki wykorzystujące raga, ogólne
* https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb
  * using embeddings in prompts



* wstęp
  * ~~wstęp do nowej serii (kolejnej, zobaczymy czy nie porzucę jej po 1-2 wpisach :P)
  * ~~dodać disclaimer - nie jestem ai engienerem
* vectorize db data
  * czym sa vectory i dlaczego sa wazne
  * jak ja to zrobiłem
    * co poza postgresem
  * chunking startegy
* aplikacja
  * search
  * dodanie wyników do prompta
* dodatkowe rozkminy
  * inne opcje na tworzenie vectorów
    * w bazie danych
    * on the fly, przez aplikację (robiąc update/insert kalkuowanie vectora)
  * wyliczanie kwoty, ile to będzie kosztowało
  * further optimizations - te dziwne indeksy
  * czy vector db jest potrzebny dla ustrukturyzowanych danych?


===========
WSTĘP

===========

![cover](cover.jpg)

The AI revolution is here. The release of ChatGpt in November 2022 ignited a new revolution in software, where generative AI plays a central role. New tools and patterns emerged which enables us, software engineers, to build new, exciting projects. It's so hard to keep up with it because almost every week a new thing comes up. 

At least for me it is sometimes hard to keep up with all new things. Hence to fight off my fear-of-missing-out and to extend my professional toolbox I have created this series in which I will describe how to build an application that is powered by the AI. But before that keep in mind I am not an AI engineer and I have only a basic knowledge on machine learning. I am not an expert in this field but I hope that with this series it will become a little bit more clear to me and perhpaps you, the reader, will also learn something too. 

(And I hope that this series won't share the fate of previous series that I abondend after one or two entries 😜🤞)

=====meme


## The Project - 👨‍🍳 Nutri Chef AI

I like to learn based on close to real-life projects. Hence I've decided to built a nutrition assistance application, which will help me plan all my meals for the entire week. I want to keep my meals healthy balanced with all needed macronutrients on a good level.

Because I already has a large number of favourite recipies I don't want to really on something that is on the Internet. I want my AI nutrition assistant to plan my meals based on my prompt and cookbook.

```
OBRAZEK że ja odpytuję AIa, a on sprawdza mi w ksiązce kucharskiej i daje listę
```

This requirement brings us to a first problem - how to provide my entire cookbook to the AI? 

## Retrieval-Augmented Generation (RAG)


### pattern

### what are vectors?

### Storing vectors

## Vectorize db data

```python
import json
import os
from pathlib import Path
import logging
from typing import Any, Dict, List
import psycopg2
import openai
import tiktoken     
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration options
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "meal_planner",
    "user": "postgres",
    "password": "postgres"
}
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"

CHUNK_TYPES = ["name", "description", "ingredients", "instructions", "tags"]

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, client_encoding='UTF8')

def fetch_recipes(conn) -> List[Dict[str, Any]]:
    logger.info("Fetching recipes from database...")
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, description, ingredients, instructions, tags FROM recipe")
        columns = [desc[0] for desc in cur.description]
        recipes = [dict(zip(columns, row)) for row in cur.fetchall()]
        return recipes

def chunk_recipe(recipe: Dict[str, Any]) -> List[Dict[str, Any]]:
    logger.debug(f"Chunking recipe {recipe['id']}...")
    chunks = []
    for chunk_type in CHUNK_TYPES:
        content = recipe.get(chunk_type)
        if content:
            chunks.append({
                "recipe_id": recipe["id"],
                "chunk_type": chunk_type,
                "content": content
            })
    logger.debug(f"Created {len(chunks)} chunks for recipe {recipe['id']}")
    return chunks

def prepare_jsonl_file(chunks: List[Dict[str, Any]], base_output_path: str) -> str:
    record_count = 0
    with open(path, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            record = {
                "custom_id": f"{chunk['recipe_id']}_{chunk['chunk_type']}",
                "method": "POST",
                "url": "/v1/embeddings",
                "body": {
                    "model": EMBEDDING_MODEL,
                    "input": str(chunk["content"])
                }
            }
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
            record_count += 1
    
    logger.info(f"Created file with {record_count} records, path: {path}")
    return path

def main():
    logger.info("Starting embedding process...")
    
    # Create temp directory for JSONL files if it doesn't exist
    temp_dir = Path("batch-files")
    temp_dir.mkdir(exist_ok=True)
    logger.info(f"Created temporary directory at: {temp_dir}")
    
    try:
        # Connect to database and fetch recipes
        conn = get_db_connection()
        recipes = fetch_recipes(conn)
        
        # Chunk recipes
        logger.info("Starting recipe chunking process...")
        all_chunks = []
        for recipe in recipes:
            all_chunks.extend(chunk_recipe(recipe))
        logger.info(f"Created total of {len(all_chunks)} chunks from {len(recipes)} recipes")
        
        # Prepare JSONL files
        base_jsonl_path = temp_dir / "recipes_for_embedding.jsonl"
        jsonl_path = prepare_jsonl_file(all_chunks, str(base_jsonl_path))

        job_id = start_batch_job(jsonl_path, EMBEDDING_MODEL)
        logger.info(f"Batch job created with ID: {job_id}")
    
        # Save job ID for tracking
        save_job_id(job_id, jsonl_path, temp_dir)

    except Exception as e:
        logger.error(f"Error during embedding generation: {str(e)}")
        raise
    finally:
        # Cleanup
        logger.info("Performing cleanup")
        if 'conn' in locals():
            conn.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
   main()
```

### Chunking data

## Utilizing vectors in application

### Search best fitting recipes

### Enriching prompt with knowledge base data

## Going deeper