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

opisać cały proces, z diagramami
odesłać do innych podejść

```python
import json
import os
from pathlib import Path
from typing import Any, Dict, List
import psycopg2
import openai  
from datetime import datetime
from dotenv import load_dotenv


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
    print("Fetching recipes from database...")
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, description, ingredients, instructions, tags FROM recipe")
        columns = [desc[0] for desc in cur.description]
        recipes = [dict(zip(columns, row)) for row in cur.fetchall()]
        return recipes

def chunk_recipe(recipe: Dict[str, Any]) -> List[Dict[str, Any]]:
    print(f"Chunking recipe {recipe['id']}...")
    chunks = []
    for chunk_type in CHUNK_TYPES:
        content = recipe.get(chunk_type)
        if content:
            chunks.append({
                "recipe_id": recipe["id"],
                "chunk_type": chunk_type,
                "content": content
            })
    print(f"Created {len(chunks)} chunks for recipe {recipe['id']}")
    return chunks

def prepare_jsonl_file(chunks: List[Dict[str, Any]], path: str) -> str:
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
    
    print(f"Created file with {record_count} records, path: {path}")
    return path

def start_batch_job(file_path: str, model: str) -> str:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    file_response = client.files.create(
        file=open(file_path, "rb"),
        purpose="batch"
    )
    file_id = file_response.id
    print(f"File uploaded successfully with ID: {file_id}")
    
    descr = datetime.now().strftime("%Y%m%d_%H%M%S") + " - nutri chef embedding"
    batch_response = client.batches.create(
        input_file_id=file_id,
        endpoint="/v1/embeddings",
        completion_window="24h",
        metadata={
            "description": descr
        }
    )
    job_id = batch_response.id
    print(f"Batch job created with ID: {job_id}")
    return job_id

def main():
    print("Starting embedding process...")
    
    temp_dir = Path("batch-files")
    temp_dir.mkdir(exist_ok=True)
    print(f"Created temporary directory at: {temp_dir}")
    
    try:
        conn = get_db_connection()
        recipes = fetch_recipes(conn)
        
        print("Starting recipe chunking process...")
        all_chunks = []
        for recipe in recipes:
            all_chunks.extend(chunk_recipe(recipe))
        print(f"Created total of {len(all_chunks)} chunks from {len(recipes)} recipes")
        
        base_jsonl_path = temp_dir / "recipes_for_embedding.jsonl"
        jsonl_path = prepare_jsonl_file(all_chunks, str(base_jsonl_path))

        job_id = start_batch_job(jsonl_path, EMBEDDING_MODEL)
    

    except Exception as e:
        print(f"Error during embedding generation: {str(e)}")
        raise
    finally:
        # Cleanup
        print("Performing cleanup")
        if 'conn' in locals():
            conn.close()
        print("Database connection closed")

if __name__ == "__main__":
   main()
```

```bash
Starting embedding process...
Created temporary directory at: batch-files
Fetching recipes from database...
Starting recipe chunking process...
Created total of 25 chunks from 5 recipes
Created file with 25 records, path: batch-files\recipes_for_embedding.jsonl
HTTP Request: POST https://api.openai.com/v1/files "HTTP/1.1 200 OK"
File uploaded successfully with ID: file-HvRA1M3FMHtiW2CkU9ijhp
HTTP Request: POST https://api.openai.com/v1/batches "HTTP/1.1 200 OK"
Batch job created with ID: batch_68c8f2bfcdac8190b762a7a096aa21f7
Performing cleanup
Database connection closed
```

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

batch_id = ""

batch = client.batches.retrieve(batch_id)
print(f"Batch response:\n {batch.to_json()}")
```


batch status
```json
{
  "id": "batch_68c8f2bfcdac8190b762a7a096aa21f7",
  "completion_window": "24h",
  "created_at": 1757999807,
  "endpoint": "/v1/embeddings",
  "input_file_id": "file-HvRA1M3FMHtiW2CkU9ijhp",
  "object": "batch",
  "status": "completed",
  "cancelled_at": null,
  "cancelling_at": null,
  "completed_at": 1757999947,
  "error_file_id": null,
  "errors": null,
  "expired_at": null,
  "expires_at": 1758086207,
  "failed_at": null,
  "finalizing_at": 1757999941,
  "in_progress_at": 1757999869,
  "metadata": {
    "description": "20250916_071647 - nutri chef embedding"
  },
  "output_file_id": "file-BhMQY4umjMy228GzgVqvgB",
  "request_counts": {
    "completed": 25,
    "failed": 0,
    "total": 25
  },
  "usage": {
    "input_tokens": 3533,
    "output_tokens": 0,
    "total_tokens": 3533,
    "input_tokens_details": {
      "cached_tokens": 0
    },
    "output_tokens_details": {
      "reasoning_tokens": 0
    }
  }
}
```


```python
from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

file_name = "file-BhMQY4umjMy228GzgVqvgB"

file_response = client.files.content(file_name)

output_dir = Path("batch-files")

output_file = output_dir / f"{file_name}.jsonl"

with open(output_file, "w", encoding='utf-8') as f:
    f.write(file_response.text)

print(f"Response saved to: {output_file}")
```

```bash
Response saved to: batch-files\file-BhMQY4umjMy228GzgVqvgB.jsonl
```



```json
{"id": "batch_req_68c8f34a2aa08190948f212848e33ab5", "custom_id": "e4d52600-5a9a-48fc-8afe-af3ed6d835dd_tags", "response": {"status_code": 200, "request_id": "8724e1825b5baa0ac74cf4d11c77d513", "body": {"object": "list", "data": [{"object": "embedding", "index": 0, "embedding": [-0.0075121797, 0.016524209, 0.012069914, -0.032091618]}], "model": "text-embedding-3-small", "usage": {"prompt_tokens": 13, "total_tokens": 13}}}, "error": null}

```


```python
import json
import psycopg2
import tiktoken
from typing import List, Dict, Any
from pathlib import Path

embedding_file = "file-BhMQY4umjMy228GzgVqvgB.jsonl"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "meal_planner",
    "user": "postgres",
    "password": "postgres"
}
EMBEDDING_MODEL = "text-embedding-3-small"

_loaded_request_data = None

def get_token_count(text: Any, model: str) -> int:
    if text is None:
        text = ""
    if not isinstance(text, str):
        text = str(text)
    
    text = text.replace('\x00', '')
    
    enc = tiktoken.encoding_for_model(model)
    try:
        token_count = len(enc.encode(text))
        print(f"Token count: {token_count:,} for text of length {len(text):,}")
        return token_count
    except Exception as e:
        print(f"Error counting tokens for text: {text[:100]}... Error: {str(e)}")
        return 0

def load_request_data():
    global _loaded_request_data
    if _loaded_request_data is None:
        _loaded_request_data = []
        with open('batch-files/recipes_for_embedding.jsonl', 'r', encoding='utf-8') as file:
            for line in file:
                _loaded_request_data.append(json.loads(line))

def find_content(custom_id):
    load_request_data()
    
    for item in _loaded_request_data:
        if item.get('custom_id') == custom_id:
            return item.get('body', {}).get('input')
    
    print(f"Content not found for custom_id: {custom_id}")
    return None

def load_embeddings(file: str) -> List[Dict[str, Any]]:
    all_embeddings = []
    
    file_path = Path("batch-files") / file
    if not file_path.exists():
        print(f"Embedding file not found: {file_path}")
        return all_embeddings
    
    print(f"Loading embeddings from file: {file_path}")
    with open(file_path, "r", encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                custom_id = record.get("custom_id", {})
                recipe_id, chunk_type = custom_id.split('_', 1)

                embedding = record.get("response", []).get("body", []).get("data", [])[0].get("embedding", [])
                content = find_content(custom_id)
                token_count = get_token_count(content, EMBEDDING_MODEL)
                
                all_embeddings.append({
                    "recipe_id": recipe_id,
                    "chunk_type": chunk_type,
                    "embedding": embedding,
                    "token_count": token_count
                })
                    
            except json.JSONDecodeError as e:
                print(f"JSON parsing error in {file_path}: {str(e)}")
            except Exception as e:
                print(f"Error processing line in {file_path}: {str(e)}")
    
    print(f"Loaded total of {len(all_embeddings)} embeddings from all files")
    return all_embeddings


def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    print("Database connection established successfully")
    return conn


def store_embeddings(conn, embeddings: List[Dict[str, Any]]):
    print("Starting to store embeddings in database")
    with conn.cursor() as cur:
        for idx, emb in enumerate(embeddings, 1):
            cur.execute("""
                INSERT INTO recipe_embeddings (recipe_id, chunk_type, embedding, token_count)
                VALUES (%s, %s, %s, %s)
            """, (emb["recipe_id"], emb["chunk_type"], emb["embedding"], emb["token_count"]))
        conn.commit()
    print(f"Successfully stored all {len(embeddings)} embeddings in database")

def main():
    try:

        all_embeddings = load_embeddings(embedding_file)
        conn = get_db_connection()

        if all_embeddings:
            print(f"Storing total of {len(all_embeddings)} embeddings from all files")
            store_embeddings(conn, all_embeddings)
        else:
            print("No embeddings were generated")
    
    except Exception as e:
            print(f"Error during embedding generation: {str(e)}")
            raise
    finally:
        print("Performing cleanup")
        if 'conn' in locals():
            conn.close()
            print("Database connection closed")


if __name__ == "__main__":
    main()
```



```bash
Loading embeddings from file: batch-files\file-BhMQY4umjMy228GzgVqvgB.jsonl
Token count: 11 for text of length 28
Token count: 36 for text of length 89
Token count: 210 for text of length 509
Token count: 348 for text of length 855
Token count: 79 for text of length 181
Token count: 6 for text of length 16
Token count: 32 for text of length 83
Token count: 168 for text of length 390
Token count: 547 for text of length 1,367
Token count: 33 for text of length 74
Token count: 16 for text of length 39
Token count: 39 for text of length 95
Token count: 224 for text of length 554
Token count: 455 for text of length 1,119
Token count: 34 for text of length 74
Token count: 11 for text of length 28
Token count: 34 for text of length 91
Token count: 185 for text of length 433
Token count: 370 for text of length 915
Token count: 51 for text of length 121
Token count: 10 for text of length 24
Token count: 27 for text of length 72
Token count: 134 for text of length 339
Token count: 460 for text of length 1,168
Token count: 13 for text of length 31
Loaded total of 25 embeddings from all files
Database connection established successfully
Storing total of 25 embeddings from all files
Starting to store embeddings in database
Successfully stored all 25 embeddings in database
Performing cleanup
Database connection closed
```



### Chunking data

## Utilizing vectors in application

### Search best fitting recipes

### Enriching prompt with knowledge base data

## Going deeper