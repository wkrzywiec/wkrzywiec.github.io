---
title: "Building AI-Powered Software: Streaming responses"
date: 2026-04-18
summary: "Learn how to build AI agentic software that utilizes a RAG, vectorized knowledge database."
description: "This post provides a hands-on guide to building an AI-powered application using Retrieval-Augmented Generation (RAG), showing step-by-step how to convert your own data into vector embeddings and integrate them into a real Spring Boot project."
tags: ["ai", "ai-agents", "ai-series", "generative-ai", "openai", "streaming", "sse", "server-sent-events", "websockets", "ndjson", "grpc", "chainlit" , "java", "kotlin", "spring-boot"]
---

## Why it is taking so long? Did it crash?

In my previous article in this series (here is a [link](https://wkrzywiec.is-a.dev/posts/054_vector-db/)) I have prepared a simple endpoint that returns a curated by LLM list of recipes that are based on user input. The results is a nice structured response but in order to get it we need to wait even couple of seconds. The reason for that is the entire process of generating a response involves couple of slower steps like embedding a user input or waiting for a response from LLM. And the more complicated the process becomes the more time user may wait for a final result.

Here is how it looks now:

!!! ADDDD video !!!!!

As you spot on, an entire response is returned after completing the entire process. In a meantime there are no fast feedback send to a user what's going on so user may think that something have crashed.

It would be better to send a notification to a user what actually is going on. Something like "Hey, we got your input and working on it" and then followed something like "We found some delicious recipes, in a moment we give the best ones". This way we can avoid the feeling from a user that something stucked.

Additionally, in case of long text outputs produced by LLM it would be good to not wait until everything is generated but return it as it comes from LLM.

All of that will be addressed and explained in this article but before that let's dive into two aspects of solution that will be picked.

## Streaming chunks

several chunks -> 

trzeba utrzymywać po

### Protocols

First decision that we have to make is which communication protocol we would want to select. Or in other worlds how we would like to stream chunks from server to a client.

There are several options:

* standard **HTTP** - which may be realized with following mechanisms:
  * **Server-Sent Events** - SSE
  * **Newline Delimited JSON** - NDJSON
* **Websockets**
* **gRPC**

All approaches allows to have a long-living connection with a server and are able to send messages in chunks.

#### Server-Sent Events

Server-Sent Events is mechanism of uni-direction communication between server and client. It means that only server is able to send data to client. Opposit direction of communication is not possible.

In order to get SSE response client first need to make a standard HTTP call with `Accept: text/event-stream` header, after which an open connection will be established. It will persist until one of the sides (client or server) close it. During the connection server is pushing messages in whatever text form. It could be JSON, but it does not need to be. It can be simple string.

Technically speaking there are no constraints on how a response should be structured. However there is a convention that most clients and servers are following, in order to adhere to it server needs to send:

* a double line (`"\n\n"`) between each message/chunk,
* a message in a format `data: <message>`,
* an optional `event: <event type>` field that describes an event type (like `add`, `remove` but it may be also more business-centric like `addedToCart`, etc.),
* an optional `id: <event id>` field with message identifier

So the response, with 2 events, may look like this:

```sse
id: 1
event: start
data: Hello


id: 2
event: add
data: there!
```

Today the SSE is the most popular mechanism for AI chats simply because OpenAI is using it in their streaming API. OpenAI was the first, widely used LLM chat, every company/tool wanted to integrated with it so they adopted the SSE on their side which made the SSE the de facto standard in the AI chat industry.

Therefore the SSE is the best option if we would like to integrate our app with popular chat UIs, like [Open WebUI](https://openwebui.com/), [Chainlit](https://chainlit.io/), [Ollama Desktop App](https://ollama.com/) or [Jan.ai](https://www.jan.ai/).

#### NDJSON

The NDJSON stand for Newline Delimited JSON which is a data format of multiple of JSON object separated by a newline character `\n`. Each line is a valid JSON and can be treated as a sequence of separated objects/events. This is very simple format, very close to returning a single JSON which is an industry-standard which makes it easier to integrate with already existing tools.

Similarly to the SSE, NDJSON relays on a HTTP with a long-living connection in which each line, JSON is sent. Unlike SSE this format enforces to send data in a structured way which upfront informs that data is sent in certain structure, making it easier to maintain.

For example, here is how an exemplary response could looke like (the `Content-Type` HTTP header would be `application/x-ndjson`):

```json
{ "id": 1, "event": "start", "data": "Hello"}
{ "id": 2, "event": "add", "data": "there!"}
```

The NDJSON format is a bit of a niche but it's used in some systems like Ollama and can be an alternative for SSE.

#### Websockets

#### gRPC


* zobaczyć jak sa wysyłane
  * chatgpt
    * różnicówka
    * event stream
  * perplexity
  * my
  * inne?

### Response structure

* pełne chunki
* przyrostowo chunki
* chunki różnicowo - tekstowe
* budowanie skomplikowanej odpowiedzi różnicowo - jak chatgpt
  * `{"v": [{"p": "/message/content/parts/0", "o": "append", "v": " systems combine:\n\n```\nSemantic chunking"}, {"p": "/message/metadata/token_count", "o": "replace", "v": 1018}]}`

* zobaczyć jak sa wysyłane
  * chatgpt
    * różnicówka
    * event stream
  * perplexity
  * my
  * inne?

## Solution selection

* wybór strategii
  * kontrakt bliski chatgpt - aby można było użyć w chainlit, czy innego rozwiązania


## Implementation

### Spring boot SSE

### Alternative solutions

#### spring boot - streamingresponsebody

#### spring boot - websocket

#### reactive spring

## References

* [Server-sent events | HTML: The Living Standard](https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events)
* [Create a model response | OpenAI API Reference](https://developers.openai.com/api/reference/resources/responses/methods/create)


Is splitting into 3 LLM calls a good idea?
Short answer: no, not for this use case. Here's why:
Problems with 3 separate calls:
- Each call re-sends the full recipe list in the system prompt — 3x the token cost
- Each call is a cold start with no shared context — the recipe selection in call 1 must be re-explained to calls 2 and 3 via prompt engineering, introducing drift risk (call 2 might pick different recipes than call 1 selected)
- Total latency is 3× serial LLM round-trips
- Rationale quality degrades when the model doesn't "remember" why it picked a recipe — you'd have to paste the selection back in as context
Better approach: one call with streaming, parse tokens as they arrive.
Spring AI's ChatClient supports streaming via .stream().content() which returns a Flux<String> (one element per token). You buffer the accumulating JSON string and emit domain events as soon as recognizable boundaries are crossed in the partial JSON.
However, parsing partial streaming JSON reliably is non-trivial. The cleanest practical solution given your desired event flow is:
One streaming call, two-phase token routing:
Phase 1 — stream "response" field tokens  → emit ResponseToken events
Phase 2 — accumulate recipe list silently → once complete, emit RecipesSelected + per-recipe RationaleToken streams
Phase 3 — return nextActions as final event
This keeps one LLM call but gives you the progressive UX you want. The trick is restructuring the JSON schema so streamable fields come first:
{
  "response": "...streamed token by token...",
  "recipes": [
    { "recipeId": "uuid", "rationale": "...streamed..." },
    ...
  ],
  "nextActions": ["...", "..."]
}
With this ordering the LLM generates response first (stream tokens), then recipes (buffer until each } boundary, emit per recipe), then nextActions (emit whole).