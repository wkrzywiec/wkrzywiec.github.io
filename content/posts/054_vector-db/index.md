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