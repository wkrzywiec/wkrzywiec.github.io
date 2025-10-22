---
title: "Building AI-Powered Software: Model Embeddings"
date: 2025-10-22
summary: "Learn how to build AI agentic software that utilizes a RAG, vectorized knowledge database."
description: "This post provides a hands-on guide to building an AI-powered application using Retrieval-Augmented Generation (RAG), showing step-by-step how to convert your own data into vector embeddings and integrate them into a real Spring Boot project."
tags: ["ai", "ai-agents", "ai-series", "generative-ai", "model-embeddings", "openai", "rag", "retrieval-augmented-generation", "java", "kotlin", "spring-boot", "python", "database", "postgresql", "vectors", "pgvector" ]
---

*Do you want to build your first AI application but don't know how? Are you afraid of missing out on the AI hype train? Don't worry! These were my exact thoughts recently, so I decided to start a new series on this topic. In this article, I want to focus on how to provide your own data to an LLM using RAG. After a short introduction to the topic, we'll dive into a practical guide on how to convert data into vectors and then use it in a real Spring Boot application—so buckle up!*

![cover](cover.jpg)

The AI revolution is here. The release of ChatGPT in November 2022 ignited a new revolution in software, where generative AI plays a central role. New tools and patterns have emerged, enabling us as software engineers to build new, exciting projects. It's hard to keep up because almost every week something new comes out.

At least for me, it's sometimes hard to keep up with all the new things. To fight off my fear of missing out and to extend my professional toolbox, I have created this series in which I will describe how to build an application powered by AI. But before we start, keep in mind I am not an AI engineer and I have only basic knowledge of machine learning. I am not an expert in this field, but I hope that with this series it will become a little bit clearer to me, and perhaps you, the reader, will also learn something too.

(And I hope that this series won't share the fate of previous series that I abandoned after one or two entries 😜🤞)

![abandon-series-meme](series-meme.jpg)

## The Project - 👨‍🍳 Nutri Chef AI

I like to learn based on real-life projects. That's why I've decided to build a nutrition assistance application, which will help me plan all my meals for the entire week. I want to keep my meals healthy and balanced, with all needed macronutrients at a good level.

Because I already have a large number of favorite recipes, I don't want to rely on something from the Internet. I want my AI nutrition assistant to plan my meals based on my prompt and my own cookbook.

![meal-planner-process](meal-planner-process.png)

This requirement brings us to the first problem - **how to provide my entire cookbook to the AI?**

Theoretically, we could add all the knowledge to each prompt, but for several reasons, it may not be a good idea:

* it would increase costs - each token sent to AI costs money (no matter if you pay with a subscription or with the electric power of your locally installed AI model),
* it would introduce latency - large inputs usually require the AI to process for much longer,
* it could result in losing the context window - it is not always good to have as big an input as possible because too large inputs may cause some parts to not be taken into account when generating an answer by the AI model; it is always a matter of balancing the size,
* it would not be accepted by the AI model - each AI model has an input token limit which can't be exceeded.

Instead, we could use only a subset of the knowledge base. We can carefully select only the parts that are most relevant for a task (user prompt). For example, in the *Nutri Chef AI* app, for a prompt like `find all recipes with what is left in my fridge - cheese, ham, egg, paprika, flour, milk`, it is not necessary to attach recipes that require other ingredients. We want to receive only those that match the criteria. So we need something smart enough to get only those parts of data that may be relevant before adding them to the system context.

## How Retrieval‑Augmented Generation (RAG) works

There are two patterns for how we could achieve that:

1. via Retrieval-Augmented Generation (RAG)
2. via tool calling

As you may guess, this article is focused on the first approach (I'll do a separate blog post on the latter topic sometime in the future).

RAG is a technique in which an application retrieves the most relevant pieces of information from an external data source (it could be a database, file, or something else) and attaches it to the AI input along with a user prompt. It is up to the application to select data that may be needed to fulfill the task by the AI agent. The app builds the context specific to each user query.

![rag process](rag.png)

**But how an application can select only relevant data?**

One way could be based on the keywords included in the user input. This is how Google Search, Elasticsearch, or any other "classic" solution works. They try to find the best matches based on key terms from the input. If the input is `low-carb pasta dinner`, it may find all documents that have `low-carb`, `pasta`, and `dinner` terms in them. They only analyze the words included in the query and, based on them, prepare the results. They usually do not search for deeper meaning, so in results for the mentioned query, we could get not only low-carb pasta recipes but also regular pasta recipes and low-carb but non-pasta recipes.

There is another approach that addresses this problem - embedding-based retrieval, also known as semantic retrieval.

### Embedding-based retrieval

In short, an embedding is a compact representation of data in the form of a multidimensional vector. These vectors represent the (semantic, underlying) meaning of the embedded text. In embedding-based retrieval, we compare a user input, represented as a vector, with the entire knowledge base, also represented as vectors. If, by many measures, two vectors are similar to each other, we consider the data they represent to be relevant.

To visualize it, let's check the following graph of the x and y axes, which presents three vectors:

![vectors](vectors.png)

Vectors A and B are similar to each other because they are close together, have a similar angle with the x and y axes, and are of similar length. Vector C, however, does not share those similarities with the other two vectors. If vectors A and B represented two pieces of information, we could say that both of them have a similar meaning.

When can we say that two vectors are similar? There are a couple of ways to calculate the distance metric between two vectors, and thus their similarity. Some of them you may already know from math classes:

* l2 (Euclidean) distance
* cosine distance
* l1 distance
* hamming distance
* jaccard distance

Each distance metric has its strengths and is suitable for different data types. For instance, the Euclidean distance is the distance between two endpoints of a position vector, as shown in the picture below:

![vector distance](vector-distance.png)

The larger the differences in length and angle between two vectors, the greater the distance is between them and the greater the dissimilarity.

Each method focuses on different aspects and should be chosen depending on the case. The best approach is to try out each of them and measure which one behaves the best.

### From text to vectors: producing embeddings

So the app flow is pretty straightforward. When a user submits a query, we need to transform it into a vector and compare it with the stored vectors to find the most similar ones. But how do we make such a conversion of user input and data? With an AI model, of course!

Embedding models are specialized neural networks designed to convert text into vector representations, and are different from large language models used for chat. For instance, OpenAI is offering three at the moment of writing this - `text-embedding-3-small`, `text-embedding-3-large` and `text-embedding-ada-002` . We can select whichever model we like, but we need to keep to these rules:

* Tune the number of dimensions based on purpose - a higher number of dimensions is usually good for capturing nuances in data; similar but still different data may have slightly different vectors and hence search may be more accurate. On the other hand, a higher number of parameters may require more resources to compute search and require more storage for larger vectors.
* Model is self-hosted or consumed via API - like for LLMs, we pick from models that we can install locally or use services exposed by AI providers.
* Input and data must be converted using the same model - each model represents space differently, which makes vectors produced not compatible if two different models were used. If you want to compare which embedding model works best for your use case (e.g., via A/B testing), you need to generate embeddings for your data using each model separately.

If you would like to browse available models, go check https://huggingface.co/blog/mteb, which also measures how powerful they all are.

#### Chunking strategies

One of the problems with data embedding is that the knowledge we would like to embed may be very large, and models may not handle too many input tokens. In fact, each one of them has its own limits.

Therefore, we need to chunk the data into smaller segments. The simple solution would be to split the data by character number. I.e., if a model has a limit of 1000 tokens, we could split the input to be less than that. But it would cause some embeddings to lack the required context, as they would be split in the middle of a sentence or section, which would produce a garbage vector.

Another approach is to chunk input data based on logical units, such as paragraphs, sections, or other meaningful divisions. For instance, the paragraphs of a blog post may be treated as separate chunks, or a section if a paragraph is too granular. This helps preserve context within each chunk, but we still need to ensure that each chunk does not exceed the model's token limit, which can be checked using available libraries.

Next, a more sophisticated approach could be to logically split the data. If data is already structured, like recipes, chunking could be relatively easy since the data is already broken out into smaller pieces. But what if a knowledge base is not structured? We could use the LLM for that! It could split the data based on certain parameters (e.g., not losing context and not exceeding certain limits), which of course comes with additional cost and may not be accurate (as LLMs may produce nondeterministic results).

As we can see, there are various ways to chunk our data. As always, there is no silver bullet, and sometimes it is better to try out various approaches (different chunking strategies, chunk sizes, etc.) and measure their results.

#### Storing vectors

Once we've got vectors produced by the embedding model, we need to save them somewhere. There are a couple of options for doing that, like storing them in:

1. a file - not efficient but a simple solution
2. an existing database which requires extensions installed. Popular solutions that offer it are, for instance, Postgres, Elasticsearch, Redis, and others.
3. a native vector DB - with the AI RAG revolution, new players have emerged offering native vector storing and search solutions. Examples are: [Chroma](https://www.trychroma.com/), [Milvus](https://milvus.io/), [Qdrant](https://qdrant.tech/), [Weaviate](https://weaviate.io/), and others.
4. a cloud provider IaaS - each cloud vendor has its own vector database, e.g. [Amazon S3 Vectors](https://aws.amazon.com/s3/features/vectors/), [Azure AI Search](https://azure.microsoft.com/en-us/products/ai-services/ai-search) or Google's [Vertex AI Vector Search](https://cloud.google.com/vertex-ai/docs/vector-search/overview).

Each one of them comes with pros and cons. Some are free to use, some are paid but are easy to use, more performant, or do not require you to set up the entire infrastructure.

### Using embeddings in applications

Phew, that was a lot of knowledge to be introduced to. Let's now focus on the application that we're building. In the *Nutri Chef AI* app, I want to have two endpoints that would:

* search the best fitting recipes
* propose a meal plan for a day

The workflow for the second one will look like this:

1. User sends a query.
2. The query is transformed into a vector.
3. User input vector is compared with vectors stored in PostgreSQL database. The *n* most similar chunks are returned each with an id of a different recipe.
4. Full recipes are fetched from db using the recipe ids (this is where the 1st endpoint ends and returns recipes as results).
5. Recipes are formatted and added to the system prompt along with AI instructions and a user prompt.
6. The entire prompt is passed to the LLM.
7. The output is returned to the user as a string

This flow is not specific to the *Nutri Chef AI*; it is a pretty generic one and could be used in various cases.

![rag flow](rag-flow.png)

The implementation of this entire flow is described in the [Enriching prompt with recipe data](https://wkrzywiec.is-a.dev/posts/054_vector-db/#enriching-prompt-with-recipe-data) section of this blog post.

## Practical walkthrough

The theoretical introduction is now behind us, so we can move on to implementing a simple RAG in the *Nutri Chef AI* app. I've split this section into two parts:

1. creating embeddings from already stored data
2. implementing RAG flow in the app itself

### Embedding recipe data and inserting into pgvector columns

The first step in building the Nutri Chef AI application is to vectorize the recipe data. I already have it in the PostgreSQL database, so the plan is to retrieve it, prepare the request for the embedding process, execute it, and then store the results in the PostgreSQL database.

My data is relatively static. I don't change it too often, so I've decided that vectorizing the data will be a one-off job. The application will use the OpenAI model, so for embedding I'm also using the ChatGPT API.

To achieve this task, I could use [a simple endpoint for creating embeddings](https://platform.openai.com/docs/api-reference/embeddings/create), which is fast and returns vectors immediately. But in my case, I can wait a little longer for results, and if it's cheaper, that's even better. For these reasons, I've decided to go with the [OpenAI Batch API](https://platform.openai.com/docs/guides/batch). This API essentially processes requests in the same fashion as the standard one, but it allows you to combine multiple requests into one. They are then executed asynchronously, and the results are returned after a couple of minutes or hours (depending on how large the dataset is). It may add some overhead to the process (because we need to monitor the async process), but it comes with a lower price per embedding.

The overall process looks like this:

![embedding process](./embedding-process.png)

And the steps are:

1. Using Python script the data will be fetched from PostgreSQL database and prepared in the `.jsonl` format that is accepted by the OpenAI Batch API.
2. Prepared `.jsonl` file will be sent to OpenAI and then a process of embedding will be started.
3. Using the Python script the batch process will be monitored and once it's done the resulting file will be downloaded and vectors will be inserted to the database.

This is one of many approaches we could take. If you would like to learn what are the others, go check the [Different ways for document embedding process](https://wkrzywiec.is-a.dev/posts/054_vector-db/#different-ways-for-document-embedding-process) section.

Before moving on to implementation of the scripts first we need to prepare the database. We need to install the `pgvector` extension by executing the SQL script:

```sql
CREATE EXTENSION vector;
```

Be aware that this extension is not built-in into the standard PostgreSQL version. You need to put the installation files into your PostgreSQL instance first. Or you could use the Docker image provided by creators of the extension:

```bash
docker pull pgvector/pgvector:pg17-trixie
```

More information on how to provide the installation files to the PostgreSQL instance could be found in [the GitHub repository of the pgvector extension](http://github.com/pgvector/pgvector).

#### 📦 Prepare batch input file

Database is prepared so we could start writing a script for preparing `.jsonl` file for the batch job. This format is the only accepted by the OpenAI API and it looks somethig like this:

```json
{"custom_id": "61bf11bb_name", "method": "POST", "url": "/v1/embeddings", "body": {"model": "text-embedding-3-small", "input": "Apple pie"}}
{"custom_id": "61bf11bb_ingredients", "method": "POST", "url": "/v1/embeddings", "body": {"model": "text-embedding-3-small", "input": "apples, flour, butter, sugar"}}
```

As you can see, it is just a file with regular JSONs where each line represents a separate request to the OpenAI API. We've got:

* `custom_id` - which is unique across a file, represents the id of a request,
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

Simple as that. From the script, you can tell that I'm using the OpenAI API and I've picked the `text-embedding-3-small` embedding model. You can choose from different models, which vary by generation, performance, and price. At the moment of writing this article, there are also `text-embedding-ada-002` and `text-embedding-3-large`. A current list of supported models can be found on [the official OpenAI Models website](https://platform.openai.com/docs/models).

Going back to the script, if you look closer you may see that each recipe's data was split into smaller chunks (name, description, ingredients, instructions, and tags) to make each vector smaller.

#### 🚀Start batch job

An input file is prepared, so we have nothing left but to write a script to first upload it and then start the batch job:

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

Great! 🎉🎉🎉 The only thing we can do now is sit and relax. The batch job is executed in the background, so how do we know when it finishes? 🤔

#### 🔍 Monitor batch job status


Depending on how large your dataset is, the batch process may take from several minutes to several hours. To verify it, the OpenAI API can be used:

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

The most important information for us is the `status`. Above, it states that it is `completed`, and we can see that it also contains information about the `output_file_id` - a file with all results.

Before completing it a batch may have various statuses, all of them are listed [here](https://platform.openai.com/docs/guides/batch#4-check-the-status-of-a-batch). Most likely you will see one of these:

* `in_progress` - batch is running,
* `finalizing` - all requests have been executed and the results are being prepared,
* `completed` - all requests have been executed and the results are available to be downloaded.

#### 💾 Download batch job results

Having the id of an output file, we can download it with this simple script:

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

After opening the resulting file, we would get something like this:

```json
{"id": "batch_req_68c8f34a2aa", "custom_id": "61bf11bb_name", "response": {"status_code": 200, "request_id": "8724e1825b5baa0", "body": {"object": "list", "data": [{"object": "embedding", "index": 0, "embedding": [-0.0075121797, 0.016524209, 0.012069914, -0.032091618, ......]}], "model": "text-embedding-3-small", "usage": {"prompt_tokens": 13, "total_tokens": 13}}}, "error": null}
```

It contains a list of responses for each request, where each one contains a vector representation of each chunk, which will be extracted and inserted into the database in the next step.

#### 📥 Insert vector data into database

The last step is to insert the embeddings into the PostgreSQL database. We could use the already existing table with recipes, but because each recipe was chunked into five pieces, let's have a new one:

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

* `id` - is an id of a row,
* `recipe_id` - is an id of a recipe,
* `chunk_type` - tells what kind of chunk it is, values like `name`, `description`, `ingredients`, `instructions`, `tags`,
* `token_count` - tells how many tokens this chunk translates to,
* `embedding` - is the stored vector.

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

Here’s what’s really happening under the hood (and don’t worry, it’s not as scary as it sounds!):

1. First, the script grabs both the request file (that’s the one with all the original embedding requests) and the output file (the one OpenAI sends back with the results).
2. Then, for each line in the output file, it finds the matching `custom_id` in the request file to pull out the original input text. It also extracts the `recipe_id`, `chunk_type`, and the actual embedding vector, and counts the tokens in the input (because, well, tokens matter!).
3. Finally, it bundles all this info together and pops it into the database.

That’s it! If you’re like me and sometimes get lost in the details, just follow the steps one by one. And if you spot a better way, let me know—I’m always up for learning something new.

Here is an example output from the script:

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

### Utilizing embeddings in application

We have the embeddings prepared, so we can move on to the actual application. I'll be writing it in Kotlin with the Spring framework because I feel the most comfortable with it, and since recently it also has its own AI module that I wanted to try out. If you prefer another language or framework, you can still read it since I've tried to keep the code as simple as possible so it's easy to understand and translate to another language/framework.

#### Search best fitting recipes

The first endpoint that I would like to implement, and which will utilize RAG, is for searching the most matching queries to the user input. It will be the GET `/api/recipes/search?limit=<number of recipes>&prompt=<user input>` which will return a list of recipes in well-structured JSON format. The `limit` query parameter refers to how many recipes a client wants to retrieve, and the `prompt` is a user input string, which could be anything, e.g., `find low-carb options for breakfast`.

Starting from the controller, which is rather standard:

```kotlin
@RestController
@RequestMapping("/api/recipes")
class RecipeController(
    val recipeSearchFacade: RecipeSearchFacade
) {

    @GetMapping("/search")
    fun findRecipes(
        @RequestParam prompt: String?,
        @RequestParam(defaultValue = "10") limit: Int
    ): ResponseEntity<RecipeSearchResponse> {

        lateinit var matches: List<Recipe>

        val duration = measureTimeMillis {
            matches = recipeSearchFacade
                .findRecipes(prompt, limit)
        }

        val response = RecipeSearchResponse(matches = matches, totalFound = matches.size, searchTimeMs = duration)

        return ResponseEntity.ok(response)
    }
}

data class RecipeSearchResponse(
    val matches: List<Recipe> = emptyList(),
    val totalFound: Int = 0,
    val searchTimeMs: Long = 0,
)

data class Recipe(
    val id: UUID,
    val name: String,
    val description: String? = null,
    val ingredients: List<Ingredients>,
    val instructions: List<Instruction>,
    val sourceUrl: String? = null,
    val servings: String? = null,
    val tags: List<String> = emptyList(),
    val similarityScore: Double? = null,
)

data class Ingredients(val section: String, val ingredients: String)

data class Instruction(val steps: List<String>, val section: String)
```

The only thing that may raise an eyebrow is the `measureTimeMillis` block, which I've added to measure the waiting time for a result from the facade, which includes all the steps required to retrieve recipes. And speaking of the steps that the facade implements, here is its code:

```kotlin
@Service
class RecipeSearchFacade(
    private val embeddingEngine: EmbeddingEngine,
    private val repository: RecipeRepository
) {

    companion object {
        private val log = logger {}
    }

    fun findRecipes(prompt: String?, limit: Int): List<Recipe> {
        if (prompt == null || prompt.isBlank()) return emptyList()
        log.info { "Searching for $limit recipes based on a user prompt: '$prompt'..."}

        val promptEmbedding: FloatArray = embeddingEngine.embed(prompt)
        log.info { "User input was embedded. Looking for closest recipes..." }
        return repository.findNearestRecipes(promptEmbedding, limit)
    }
}
```

The role of a facade is to orchestrate the entire process; therefore, it covers first creating the embedding out of user input and then finding the most suitable recipes.

Let's check the code of the `EmbeddingEngine`:

```kotlin
import org.springframework.ai.embedding.EmbeddingModel

interface EmbeddingEngine {
    fun embed(prompt: String): FloatArray
}

@Component
class OpenAIEmbeddingEngine(
    private val embeddingModel: EmbeddingModel
): EmbeddingEngine {
    override fun embed(prompt: String): FloatArray {
        val response = embeddingModel.embedForResponse(listOf(prompt))
        return response.result.output
    }
}
```

Again, there are not that many lines of code here. With `EmbeddingModel`, we can call any embedding model to get the vector representation of a user prompt, which in Kotlin is a `FloatArray` object. It's thanks to the [Spring AI](https://spring.io/projects/spring-ai) framework. The `EmbeddingModel` is Spring's interface for interacting with various embedding models. The only thing that needs to be done to add it is to insert the following dependency to the build tool (Gradle or Maven):

```kotlin
dependencies {
    implementation("org.springframework.ai:spring-ai-starter-model-openai:1.0.1")
    implementation("org.springframework.ai:spring-ai-autoconfigure-model-openai:1.0.1")
}
```

I've selected the OpenAI model to start, so this is the reason both libraries were added. Apart from that, we also need to select which embedding model we want to use (it needs to be the same as was used for embedding data in PostgreSQL) and provide the API key. The simplest way to achieve this is via autoconfiguration, which requires only providing those values to the `application.yaml` file:

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      embedding:
        options:
          model: "text-embedding-3-small"
```

That's pretty much all that needs to be done to enable text embedding.

With `OpenAIEmbeddingEngine`, the user input was transformed into a vector, so the only thing to do now is to pass this vector to the SQL query to find the best matching recipes. The logic of it is encapsulated in the `findNearestRecipes(promptEmbedding: FloatArray, limit: Int = 10)` method of the `RecipeRepository` class:

```kotlin
@Repository
class RecipeRepository(
    private val jdbcTemplate: NamedParameterJdbcTemplate,
) {

    fun findNearestRecipes(promptEmbedding: FloatArray, limit: Int = 10): List<Recipe> {
        val sql = """
            SELECT
              r.id AS recipe_id,
              r.name,
              r.description,
              re.similarity_score,
              r.ingredients,
              r.instructions,
              r.source_url,
              r.servings,
              r.tags
            FROM (
                SELECT
                  recipe_id,
                  MIN(embedding <=> CAST(:prompt_embedding AS vector)) AS similarity_score
                FROM recipe_embeddings
                GROUP BY recipe_id
                ORDER BY similarity_score ASC
                LIMIT :limit
            ) AS re
            JOIN recipe r ON r.id = re.recipe_id
            ORDER BY re.similarity_score ASC;
        """

        val params = MapSqlParameterSource()
            .addValue("prompt_embedding", promptEmbedding)
            .addValue("limit", limit)

        return jdbcTemplate.query(sql, params, rowMapper())
    }

    fun rowMapper() = RowMapper<Recipe> { rs, _ ->
        Recipe(
            id = UUID.fromString(rs.getString("recipe_id")),
            name = rs.getString("name"),
            description = rs.getString("description"),
            ingredients = parseFromJson<Ingredients>(rs.getString("ingredients")),
            instructions =  parseFromJson<Instruction>(rs.getString("instructions")),
            sourceUrl = rs.getString("source_url"),
            servings = rs.getString("servings"),
            tags =  parseFromJson<String>(rs.getString("tags")),
            similarityScore = rs.getDouble("similarity_score"),
        )
    }

    private inline fun <reified T> parseFromJson(jsonString: String?): List<T> {
        if (jsonString.isNullOrBlank()) return emptyList()

        return try {
            jsonString.toObject<List<T>>()
        } catch (e: Exception) {
            emptyList()
        }
    }
```

Here I'm using the `NamedParameterJdbcTemplate` to execute the raw SQL query, which finds the top `n` (10 by default) recipeIds from the `recipe_embeddings` table. The list of retrieved recipeIds is then used to get the full recipe data from the `recipe` table.

The most interesting part is how vectors are compared here:

```sql
SELECT
    recipe_id,
    MIN(embedding <=> CAST(:prompt_embedding AS vector)) AS similarity_score
FROM recipe_embeddings
GROUP BY recipe_id
ORDER BY similarity_score ASC
LIMIT :limit
```

I'm using the `<=>` operator provided by the *pgvector* extension. This particular operator finds the shortest value of cosine distance. The results are then sorted from the smallest to the largest value and limited to only the top `n` results.

*pgvector* offers other methods of comparing vectors which are:

* `<->` - L2 distance
* `<#>` - (negative) inner product
* `<=>` - cosine distance
* `<+>` - L1 distance
* `<~>` - Hamming distance (binary vectors)
* `<%>` - Jaccard distance (binary vectors)

In order to find the best one for your case, you should try out all of them, experiment, and measure which one is the most suitable for you.

The `jsonString.toObject<List<T>>()` function code on the `String` object is an extension method (this is Kotlin's ability to add additional method to a class that is not part of the current codebase):

```kotlin
class ObjectMapperConfig {

    companion object {
        val objectMapper = objectMapper()
    }
}

fun objectMapper() =
    jsonMapper {
        addModule(kotlinModule())
        findAndAddModules()
        serializationInclusion(JsonInclude.Include.NON_NULL)
        defaultDateFormat(StdDateFormat())
        configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
        build()
    }

fun Any.toJson(): String = objectMapper().writeValueAsString(this)

inline fun <reified T> String.toObject(): T = objectMapper().readValue(this)
```

Everything is coded, so after starting the application and running the **GET** `/api/recipes/search?prompt=<my_prompt>` endpoint, where my prompt was a simple `find low-carb options for breakfast`, I got this result:

```json
{
    "totalFound": 10,
    "searchTimeMs": 873,
    "matches": [
        {
            "id": "00280180-a2ca-4d1d-930e-7a8baf6ff187",
            "name": "Scrambled Eggs with Mushrooms on Toast",
            "description": "A tasty breakfast idea. Scrambled eggs and browned small mushrooms are placed on toasts and sprinkled with chopped parsley or chives.",
            "ingredients": [
                {
                "section": "all",
                "ingredients": [
                    "4 eggs",
                    "4 tablespoons butter",
                    "1 tablespoon vegetable oil",
                    "2 cups small mushrooms",
                    "sea salt and freshly ground black pepper",
                    "4 slices of toasted baguette",
                    "2 tablespoons chopped parsley"
                ]
                }
            ],
            "instructions": [
                {
                "section": "all",
                "steps": [
                    "Prepare two small frying pans. Heat the first, add the oil and 2 tablespoons of butter and melt. Add washed and dried mushrooms and fry for a few minutes until nicely browned on each side. Season with salt and pepper.",
                    "Meanwhile, toast the bread slices in a toaster, spread them with butter and place them on two plates.",
                    "Heat the second pan and melt 2 tablespoons of butter in it, crack in the eggs and season with salt. Fry quickly, stirring only 4–5 times. As soon as the whites set, remove from the pan and place on one prepared toast. Put the mushrooms on the other toast. Sprinkle with pepper and parsley."
                ]
                }
            ],
            "sourceUrl": "https://www.kwestiasmaku.com/dania_dla_dwojga/sniadania/jajecznica_pieczarki/przepis.html",
            "servings": "2 servings",
            "tags": [
                "Mushrooms",
                "Eggs",
                "Eggs for breakfast"
            ],
            "similarityScore": 0.365850391911005
        },
        /// other recipes
    ]
}
```

Looks amazing 🤩! As you can see, even with a small amount of work and without really using any LLM, we can "intelligently" query our data to find the best matches! Awesome!

#### Enriching prompt with recipe data

With previous success, let's build a new thing on top of that - a simple diet advisor. Let's use the LLM to act as a dietician that focuses on delivering nutritionally balanced recipes based on the user prompt (assuming that the user will be asking for ideas for a specific meal and giving certain boundaries, like a specific diet or favorite ingredients). It won't generate a full meal plan for the entire week or even a full day—this will be covered in a future blog post.

The first thing to do is to define an endpoint and controller for that:

```kotlin
@RestController
@RequestMapping("/api/planner")
class MealPlannerController(
    private val mealPlanner: MealPlanner
) {

    @GetMapping("/single")
    fun proposeMeal(
        @RequestParam prompt: String,
    ): ResponseEntity<RecipeProposals> {
        val proposals = mealPlanner.proposeMeal(prompt)
        return ResponseEntity.ok(proposals)
    }
}
```


The `MealPlanner` is a service that takes responsibility for orchestrating the entire process, which is - finding the most relevant recipes to the user prompt (we already have that) and adding them to the request made to the AI model. Here is the entire code of this class:

```kotlin
import org.springframework.ai.chat.client.ChatClient

data class RawRecipeProposals(val response: String, val nextActions: List<String>, val recipes: List<RecipeIdWithRationale>)

class RecipeIdWithRationale(val rationale: String, val recipeId: UUID)

data class RecipeProposals(val response: String, val nextActions: List<String>, val recipes: List<RecipeWithRationale>)

data class RecipeWithRationale(val rationale: String, val recipe: Recipe?)

@Service
class MealPlanner(
    private val recipeSearch: RecipeSearchFacade,
    private val builder: ChatClient.Builder
) {

    companion object {
        private val log = logger {}
    }

    fun proposeMeal(userPrompt: String): RecipeProposals? {
        log.info { "Searching for best meal proposals based on user prompt... '$userPrompt'"}
        val recipes = recipeSearch.findRecipes(userPrompt, 10)

        log.info {" Found ${recipes.size} recipes with ids: ${recipes.map { it.id }} "}
        log.info { "Calling an AI agent..."}
        val answer = builder.build().prompt()
            .system(
                """
                You are a nutrition assistant that selects the best fitting recipes for meal planning.
                
                TASK: Analyze the provided recipes and select the most suitable ones based on nutritional benefits and user goals. If no specific goal is provided, assume recommendations for a regular healthy adult diet.
                
                RESPONSE FORMAT: You must respond with valid JSON in exactly this structure:
                {
                  "response": "Brief overall explanation of your selection strategy and nutritional focus",
                  "nextActions": ["suggested action 1", "suggested action 2"],
                  "recipes": [
                    {
                      "recipeId": "recipe-uuid-here",
                      "rationale": "Detailed explanation of why this recipe was selected, focusing on specific nutritional benefits"
                    }
                  ]
                }
                
                REQUIREMENTS:
                - Select 3-5 most suitable recipes from the provided list
                - Focus on nutritional balance, variety, and health benefits
                - Include specific nutritional reasons in each rationale
                - Suggest 2-3 relevant next actions for the user
                - Use the exact recipe IDs provided
                - Respond in the same language as the user's request
                - Return only valid JSON, no additional text
                
                RECIPES: ${recipes.toJson()}
                """.trimIndent()
            )
            .user { u -> u.text("USER_QUERY: \"$userPrompt\"") }
            .call()
            .content()
        log.info { "Response from AI Agent:\n $answer" }
        return answer?.let {
            mapToRawRecipeProposals(it)
        }?.let {
            mapToRecipeProposals(it, recipes)
        }
    }

    private fun mapToRawRecipeProposals(answer: String): RawRecipeProposals? {
        return answer.toObject<RawRecipeProposals>()
    }

    private fun mapToRecipeProposals(raw: RawRecipeProposals, fullRecipes: List<Recipe>): RecipeProposals? {
        return RecipeProposals(
            response = raw.response,
            nextActions = raw.nextActions,
            recipes = raw.recipes.map { RecipeWithRationale(rationale = it.rationale, recipe = fullRecipes.find { recipe -> recipe.id == it.recipeId}) }
        )
    }
}
```

In the first lines of the `fun proposeMeal(userPrompt: String)` method, we're invoking the already existing recipe search code. The result of it is then transformed into JSON and added to the end of the system prompt. For now, let's not focus too much on the prompt itself; the whole topic of how to write a good prompt will be covered in another article.

In this post, I want to focus on two key points - how the recipes are added to the system prompt and how to enforce the AI to respond in a certain format. In the system prompt, I'm adding those retrieved recipes as JSONs, but in your system, you can try to use different formats like XML or something less structured. Because they are added to the prompt, it is always important to keep in mind that the content of each recipe should be relatively small in order to be below the limit of how many tokens can be added in the request to the AI model.

The second important thing in this prompt is how the output result should be returned because further processing of the AI response depends on that. This is a crucial part because if we want to build a complex system with an AI in the middle of it, we need to enforce returning structured responses from it to make it easier to process by other elements of our system (backend or UI code).

To make it work, we also need to specify which AI model we want to use. It needs to be added to the configuration in the `application.yaml` file. I've decided to use OpenAI's `gpt-5-mini` model:

```yaml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: "gpt-5-mini"
          temperature: 1
```

After rebuilding the entire project, we can test the **GET** `/api/planner/single` endpoint with a prompt: `looking for dinner ideas, I'm vegetarian and my favorite vegetable is tomato`. And here is an example result:

```json
{
  "response": "I selected vegetarian dishes from the list that maximize the use of tomatoes while providing balanced nutrients: good sources of plant/animal protein (eggs, cheese, beans), healthy fats (olive oil), fiber, and vitamins and antioxidants (lycopene, vitamin C, vitamin A) from vegetables. I focus on a variety of textures and seasons (warm one-pot dish, pasta, baked cheese, cold soup) so you have options for different moods and energy needs.",
  "nextActions": [
    "Choose 1 of the following recipes for today's dinner and I'll provide a shopping list.",
    "If you want more protein, I can suggest simple modifications (e.g., more beans, addition of nuts/seeds).",
    "Do you want a vegan version of any recipe? I'll suggest substitutes for cheese and eggs."
  ],
  "recipes": [
    {
      "rationale": "Halloumi cheese in tomatoes with beans — a great combination of plant protein (beans) and protein/calcium memory from halloumi. Beans increase fiber, iron, and plant protein content, making the dish more filling and stabilizing blood glucose levels. Tomatoes and spices add lycopene and micronutrients. Note: halloumi is quite salty — if you limit sodium, use less cheese or choose less salty mozzarella/packaged cheese.",
      "recipe": {
        "id": "8fbb8ce5-8367-4660-a984-5f5756ad8780",
        "name": "Halloumi cheese in tomatoes with beans",
        "description": "Halloumi cheese can not only be fried or grilled but also baked or cooked in tomato sauce. Cooking keeps the cheese moist and pleasantly soft.",
        "ingredients": [
          {
            "section": "all",
            "ingredients": [
              "600 g fresh tomatoes (e.g., sauce variety) or 400 g canned peeled",
              "1 tablespoon olive oil",
              "2 garlic cloves",
              "1 can (400 g) white beans",
              "about 200 g halloumi cheese",
              "parsley and chives",
              "spices: 1/2 teaspoon smoked paprika, a pinch of chili flakes, 1 teaspoon oregano, salt and pepper"
            ]
          }
        ],
        "instructions": [
          {
            "section": "all",
            "steps": [
              "Peel fresh tomatoes, cut into quarters, remove stems. Dice the flesh. Cut canned tomatoes into smaller pieces, keep the sauce.",
              "In a large pan, gently fry grated garlic in olive oil. Add chopped fresh or canned tomatoes with the sauce and bring to a boil, season with salt, pepper, and other spices.",
              "Cook until the tomatoes reduce (about 10 minutes for fresh tomatoes or 6 minutes for canned tomatoes).",
              "Add canned beans with the liquid and mix. Cook for about 3 minutes.",
              "Place halloumi cheese on top and cook for another 5 minutes. Sprinkle with chopped parsley and chives."
            ]
          }
        ],
        "sourceUrl": "https://www.kwestiasmaku.com/przepis/pieczony-ser-halloumi-w-pomidorach-z-fasola",
        "servings": "2 servings",
        "tags": [
          "Gluten-free",
          "Warm dinners",
          "halloumi",
          "Greek cuisine",
          "Fit recipes",
          "Dinners",
          "Lunches",
          "Tomatoes",
          "Vegetarian",
          "Beans",
          "Hits of Kwestia Smaku"
        ],
        "similarityScore": null
      }
    },
    //other proposals
}
```

Looks amazing 🤩! As you can see even with small amount of work and with out really using any LLM we can "intelligently" query our data to find best matches! Awesome!

It returns not only the list of matched recipes but also the rationale for each recipe. There is also a text summary for the entire prompt with actions that the user may want to do next to get better results.

## Going deeper

That's pretty much it. With only a few lines of code, we have built a RAG system! It is very simple, but it may already make an impact. So what's next? How could we make it even better? Oh, there are a lot of things that may be done better.

For instance, before providing the user prompt to the recipe semantic search service, we could first ask another AI agent to analyze the user input and produce a better prompt that would be embedded and then used to search for proper recipes. With this technique, we could get even more precise results, focusing on finding the most fitting but also nutritious meals possible from the cookbook.

This is just one of many possible improvements to make the RAG system more precise, faster, or cheaper. Before wrapping up, I want to briefly describe two additional enhancements you can consider.

### Indexing vectors

The knowledge base for this project is relatively small. Finding the most similar vectors across thousands of vectors is a relatively quick operation. But what if we had billions or even trillions of vectors? Definitely, the retrieval process could get significantly longer.

One way of coping with that is to create indexes with *pgvector* that would cluster similar vectors into a smaller number of groups of vectors. With indexes, we do not search for vectors with the shortest distance but for groups of vectors. This way, we lose a little bit of the precision of finding the exact vector, but in return, we gain faster retrieval.

The *pgvector* extension supports two algorithms for creating such indexes - **HNSW** (Hierarchical Navigable Small World) & **IVFFlat** (Inverted File Flat). I won't be going deep into either of them, but you can check these great articles on [the first](https://www.crunchydata.com/blog/hnsw-indexes-with-postgres-and-pgvector) and [the second](https://www.tigerdata.com/blog/nearest-neighbor-indexes-what-are-ivfflat-indexes-in-pgvector-and-how-do-they-work) algorithm respectively.

### Different ways for document embedding process

In the hands-on section of this article, I've described how I wrote the Python script that takes care of creating embeddings. I've decided to go with a Python script and use the batch API of OpenAI because, for my case, it is a one-time job. I don't modify my cookbook too often, so the entire procedure could be done only once and never repeated. However, this is not the case in every system. Data in some systems changes quite often, and if new data should be embedded, then other approaches should be taken.

One of them could be to run a similar script periodically on a monthly, weekly, or daily basis. The script would either wipe down all existing vectors and replace them with new ones or only update and add those that have changed or were added. This, of course, requires further development of a script and good monitoring of it since it becomes a crucial part of the data pipeline for the entire system.

If periodic processing is not enough and we would like to have those vectors stored at the moment of storing the corresponding data, then another approach should be taken. Instead of the script, the logic of creating the embedding should be baked into the application logic itself. When the data is updated/inserted into the database, the application should also create a vector and store it. This approach certainly has advantages, like the data could be searched semantically right away, but the caveat is that since we're introducing the external dependency (embedding model), it may slow down the modification operation or even prevent them from happening. There are, of course, workarounds for those problems, but with the cost of higher complexity of the entire system and slowing down the process of embedding. As always, each solution has its own tradeoffs.

The last solution could be to use the [pgai](https://github.com/timescale/pgai) extension for PostgreSQL. It enables you to create and synchronize vector embeddings directly in the PostgreSQL instance. You don't need to add any logic to the app or create complicated scripts to periodically update the entire database. With a simple configuration, all of that could be achieved inside PostgreSQL. This way, we move the logic from the app to the database, which in some cases could be a good solution, but in others it may be bad because it makes the entire data flow less explicit.

## Summary

This is it for today! I hope you learned something new, like how to transform your data into vector embeddings, how to use them for semantic search, and how to write your first AI agent that leverages your own knowledge base.

The entire codebase for this project can be found on my GitHub: [wkrzywiec/nutri-chef-ai](https://github.com/wkrzywiec/nutri-chef-ai).

Until the next time!

## References

* [AI Engineering | Chip Huyen](https://www.oreilly.com/library/view/ai-engineering/9781098166298/)
* [Introduction to Text Embeddings with the OpenAI API | DataCamp](https://www.datacamp.com/tutorial/introduction-to-text-embeddings-with-the-open-ai-api)
* [A Beginner’s Guide to Vector Embeddings | TigerData](https://www.tigerdata.com/blog/a-beginners-guide-to-vector-embeddings)
* [Vector Similarity Search with PostgreSQL's pgvector | SeveralNines](https://severalnines.com/blog/vector-similarity-search-with-postgresqls-pgvector-a-deep-dive)
* [PostgreSQL as a Vector Database Using pgvector | TigerData](https://www.tigerdata.com/blog/postgresql-as-a-vector-database-using-pgvector)
* [Chunking Strategies to Improve Your RAG Performance](https://weaviate.io/blog/chunking-strategies-for-rag)
* [Question Answering Using Embeddings | OpenAI Cookbook on GitHub](https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb)