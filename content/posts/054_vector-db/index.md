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

First step in building the Nutri Chef AI application is to vectorize recipe data. I already have it in the PostgreSQL database so the plan is to retrieve from it, prepare the request for the embedding process, execute it and then store the results in the the PostgreSQL database.

My data is relatively static. I don't change it too often, therefore I've decided that vectorinzing data will be a one-off job. The application will be using the OpenAI model therefore embedding I'm also using the ChatGPT API. 

To achieve this task I could use [a simple endpoint for creating embeddings](https://platform.openai.com/docs/api-reference/embeddings/create) which is fast, the reply with vectors is immediate. But in my case I can wait a little bit longer for results and if it would be cheaper it would be even better. For these reasons I've decided to go with [OpenAI Batch API](https://platform.openai.com/docs/guides/batch). This API in essence is processing request in the same fashion as the standard one but it allows to combine multiple request into one. They are then executed asynchronously and the results are returned after couple of minutes or hours (depending on how large the dataset it). It may give an additional overhead to the process (because we need to monitor the async process) but it wil come with a lower price per each embeddding. 

The overall process looks like this:

![](./embedding-process.png)

And the steps are:
1. Using Python script the data will be fetched from PostgreSQL database and prepared in the `.jsonl` format that is accepted by the OpenAI Batch API.
2. Prepared `.jsonl` file will be sent to OpenAI and then a process of embedding will be started.
3. Using the Python script the batch process will be monitored and once it's done the resulting file will be downloaded and vectors will be inserted to the database.

This is one of many approaches we could take. If you would like to learn what are the others, go check the ````TODOTODOTODOTODOTODOTODOTODOTODOTODOTODO```` section.

Before moving on to implementation of the scripts first we need to prepare the database. We need to install the `pgvector` extension by executing the SQL script:

```sql
CREATE EXTENSION vector;
```

Be aware that this extension is not built-in into the standard PostgreSQL version. You need to put the installation files into your PostgreSQL instance first. Or you could use the Docker image provided by creators of the extension:

```bash
docker pull pgvector/pgvector:pg17-trixie
```

More information on how to provide the installation files to the PostgreSQL instance could be found in [the GitHub repository of the pgvector extension](http://github.com/pgvector/pgvector).

### 📦 Prepare batch file

Database is prepared so we could start writing a script for preparing `.jsonl` file for the batch job. This format is the only accepted by the OpenAI API and it looks somethig like this:

```json
{"custom_id": "61bf11bb_name", "method": "POST", "url": "/v1/embeddings", "body": {"model": "text-embedding-3-small", "input": "Apple pie"}}
{"custom_id": "61bf11bb_ingredients", "method": "POST", "url": "/v1/embeddings", "body": {"model": "text-embedding-3-small", "input": "apples, flour, butter, sugar"}}
```

As you can see it is just a file with regular JSONs wher each line represents a separate request to the OpenAI API. We've got:

* `custom_id` - which is unique accross a file, represents the id of a request,
* `method`, `url` & `body`- which are respectively HTTP method, path and body from "regular" API,

So here is the Python script that generates it:

```python
import json
from pathlib import Path
from typing import Any, Dict, List
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "meal_planner",
    "user": "postgres",
    "password": "postgres"
}
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

And after running it we've got an output:

```bash
Starting embedding process...
Created temporary directory at: batch-files
Fetching recipes from database...
Starting recipe chunking process...
Created total of 25 chunks from 5 recipes
Created file with 25 records, path: batch-files\recipes_for_embedding.jsonl
Performing cleanup
Database connection closed
```

Simple as that. From the script you may tell that I'm using the OpenAI API and I've picked the `text-embedding-3-small` embedding model. You can choose from different models, which varies by generation, performance and price. In the moment of writing this article there are also `text-embedding-ada-002` and `text-embedding-3-large`. A current list of supported models could be found on [the official OpenAI Models website](https://platform.openai.com/docs/models).

Going back to the script, if you look closer you may see and ask why I have chunked the data. Why each recipe was splitted into pieces which resulted in more batch requests.

#### 🪚 Chunking your data

`TODOTODOTODOTODOTODOTODOTODOTODO`


### 🚀Start batch job

An input file is prepared so we have nothing left but to write a script to first upload it and then start the batch job:

```python
import os
from pathlib import Path
import openai  
from datetime import datetime
from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
file_path =  Path("batch-files")  / "recipes_for_embedding.jsonl"

def main():
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
    

if __name__ == "__main__":
   main()
```

The output after running the script:


```bash
HTTP Request: POST https://api.openai.com/v1/files "HTTP/1.1 200 OK"
File uploaded successfully with ID: file-HvRA1M3
HTTP Request: POST https://api.openai.com/v1/batches "HTTP/1.1 200 OK"
Batch job created with ID: batch_68c8f2bf
```

Great! 🎉🎉🎉 The only thing we can do now is to sit and relax. The batch job is executed in the backrogund, so how we get to know when it finishes? 🤔


### 🔍 Monitor batch job status

Depending on how large your dataset is the batch process may take from several minutes to several hours. To verify it the OpenAI API could be used:

```python
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

batch_id = "batch_68c8f2bf"

batch = client.batches.retrieve(batch_id)
print(f"Batch response:\n {batch.to_json()}")
```

This simple Python script will print out the batch job information:

```json
{
  "id": "batch_68c8f2bf",
  "completion_window": "24h",
  "created_at": 1757999807,
  "endpoint": "/v1/embeddings",
  "input_file_id": "file-HvRA1M3",
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
  "output_file_id": "file-BhMQY4",
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

The most important information for us is the `status`. Above it states that it is `completed` and we can see that it also contains information about the `output_file_id` - a file with all results.

Before completing it a batch may have various statuses, all of them are listed [here](https://platform.openai.com/docs/guides/batch#4-check-the-status-of-a-batch). Most likely you will see one of these: 

* `in_progress` - batch is running,
* `finalizing` - all requests have been executed and the results are being prepared,
* `completed` - all requests have been executed and the results are available to be downloaded.

### 💾 Download batch job results

Having the id of an output file we can downlaod it with this simple script:

```python
from openai import OpenAI
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

file_name = "file-BhMQY4"

file_response = client.files.content(file_name)

output_dir = Path("batch-files")

output_file = output_dir / f"{file_name}.jsonl"

with open(output_file, "w", encoding='utf-8') as f:
    f.write(file_response.text)

print(f"Response saved to: {output_file}")
```

The output:

```bash
Response saved to: batch-files\file-BhMQY4.jsonl
```

After opening the resulting file we would get something like this:

```json
{"id": "batch_req_68c8f34a2aa", "custom_id": "61bf11bb_name", "response": {"status_code": 200, "request_id": "8724e1825b5baa0", "body": {"object": "list", "data": [{"object": "embedding", "index": 0, "embedding": [-0.0075121797, 0.016524209, 0.012069914, -0.032091618, ......]}], "model": "text-embedding-3-small", "usage": {"prompt_tokens": 13, "total_tokens": 13}}}, "error": null}
```

It contains a list of responses for each request, where each one of them contains a vector representation of each chunk which will be extracted and inserted into database in the next step.

### Insert vector data into database

The last step is to insert the embeddings into the PostgreSQL database. We could use the already existing table with recipes but because each recipe was chunked into 5 pieces, let's have a new one:

```sql
CREATE TABLE recipe_embeddings (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipe_id               UUID NOT NULL REFERENCES recipe(id),
    chunk_type              VARCHAR(255),
    token_count             INTEGER,
    embedding               VECTOR(1536)
);
```

where:
* `id` - is an id of a reo,
* `recipe_id` -  is an id of a recipe,
* `chunk_type` - tells kind of a chunk it is, values, like `name`, `description`, `ingredients`, `instructions`, `tags`,
* `token_count` - tells of how many tokens this chunk translates to,
* `embedding` - is a stored vector.

Having this table set we can execute a following Python script:

```python
import json
import psycopg2
import tiktoken
from typing import List, Dict, Any
from pathlib import Path

embedding_file = "file-BhMQY4.jsonl"

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

The logic of the script is simple:
1. It loads both the request and output files.
2. It iterates through each line in the output file and extracts recipe_id, chunk_type and embedding. It also retieve the content of an input in order to calculate its token count.
3. Loaded data is then inserted into the database.

Here is the exemplary output from the script:

```bash
Loading embeddings from file: batch-files\file-BhMQY4umjMy228GzgVqvgB.jsonl
Token count: 11 for text of length 28
Token count: 36 for text of length 89
Token count: 210 for text of length 509
Token count: 348 for text of length 855
....
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