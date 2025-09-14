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

### Chunking data

## Utilizing vectors in application

### Search best fitting recipes

### Enriching prompt with knowledge base data

## Going deeper