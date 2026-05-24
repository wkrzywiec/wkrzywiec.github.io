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

Options we have:

* standard **HTTP** - which may be realized with following mechanisms:
  * **Server-Sent Events** - SSE
  * **Newline Delimited JSON** - NDJSON
* **Websockets**

All approaches allows to have a long-living connection with a server and are able to send messages in chunks.

Apart from mentioned protocols we could count the **gRPC** as well but the strengths of this protocol shines the most in cross-agent communication of multi-agent system, when one agent needs to interact with another one. Therefore I'll skip this protocol for this post.

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

Today the SSE is the most popular mechanism for AI chats simply because OpenAI is using it in their streaming API. OpenAI was the first, widely used LLM chat, every company/tool wanted to integrated with it so they adopted the SSE on their side which made the SSE the de facto standard in the AI chat industry. [!!!! Perplexity]

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

Sometimes one-way communication, from server to client only, is too limiting. For instance, systems where AI agent needs to interact with human e.g. to ask permissions or ask to review plan/task progress (human-in-the-loop). Such systems require to send data from server to client and vice-versa all the time so it's beneficial to establish long-lived, bi-directional communication. This way a burden of having plethora of HTTP requests can be avoided for a single communication channel. It's a great protocol not only for chats but alos in plethora real-time collaboration system, like *Miro* or *Figma*.

Both HTTP and websockets protocols are built on the same fundation - TCP (Transmission Control Protocol) which is a core protocol of the Internet. Websocket communication starts with an HTTP handshake in which client asks server to upgrade the connection to long-lasting websocket communication. If server agrees the same TCP channel remains open and is replaced to websoocket connection. It last until client or server terminates it. In HTTP client opens TCP connection, sends data and once it receives data back from server the connection is often closed.

{{< mermaid >}}
sequenceDiagram
    participant Client
    participant Server
    Client->>Server: HTTP Upgrade Request
    Server-->>Client: 101 Switching Protocols
    Note over Client,Server: WebSocket Connection Established
    Client->>Server: send("Hello")
    Server-->>Client: send("Hello back")
    Client->>Server: send("Data payload")
    Server-->>Client: send("Acknowledged")
    Client->>Server: Close Frame
    Server-->>Client: Close Frame
    Note over Client,Server: Connection Closed
{{< /mermaid >}}

Websocket supports various data types and the most interesting for us is a simple text type which allows to shape messages that are sent back and forth from client and server wherever we like. Here is another example of message exchange for chat application, this time messages are sent in the JSON format.

In the AI agentic world websockets are used in various products. For example, I saw that Perplexity is using it to give completion suggestions to what user is typing - when I hit a letter on a keyboard Perplexity is already suggesting me what i may want to type.

```json
// Client -> Server
{"type":"join", "room":"general", "user":"wojtek"}

// Client -> Server
{"type":"chat", "room":"general", "user":"wojtek", "message":"hello everyone"}

// Server -> Client
{"type":"chat", "room":"general", "user":"alice", "message":"hello Wojtek", "timestamp":"2026-05-12T10:15:00Z"}

// Server -> Client
{"type":"ping"}

// Client -> Server
{"type":"pong"}
```

The `ping`/`pong` messages are so-called heartbeats - this a simple mechanism for client and server to make sure that connection is still operating. The others are the "regular" messages sent between client and server.

### Shaping response structure

Once a transportation mechnism is picked there is one more thing that must be selected - how a final response will be streamed to a client. By that I mean a strategy for picking on how AI agent will be sending parts of a a final structurted output in every chunk.

To visulize it, let's say that a final response for a meal planner AI agent looks like this:

```json
{
    "response": "Thank you for your meal planning request for healthy and fulfilling meals.",
    "suggestedFollowUps": [
        "Prepare a shopping list for the ingredients needed for the selected recipes."
    ],
    "recipes": [
        {
            "recipe": {
                "id": "6464b6f5-17bf-4744-90f6-dbaab3af9983",
                "name": "Mexican Quinoa",
                "description": "...",
                "ingredients": [
                    {
                        "section": "all",
                        "ingredients": [...]
                    }
                ],
                "instructions": [...],
                "sourceUrl": "https://www.bbcgoodfood.com/",
                "source": "bbc_good_food",
                "imageUrl": "https://www.bbcgoodfood.com/quinoa.jpg",
                "servings": "2 portions",
                "tags": [
                    "Lunch",
                ],
                "similarityScore": 0.6430065
            }
        }
    ]
}
```

It is a large JSON, with lots of information in it. In order to have a seamless experience a proper strategy for making such responses smaller chunks should be picked, so they can be then streamed to a client. Here are couple patterns to select from:

* snowballing final response - 
* incrementally emit JSON parts - a full response is send token by token starting from the first character until the last one. !!!  Client must handle partial/incomplete JSON
* incrementally emit JSON structured parts - like previously but more constrained - each chunk returns the structured part of a JSON, i.e only one field at a time (or message/event types)
* delta patching - Each chunk is a diff/patch applied to the previous state

#### Snowballing final response

```sse
data: {"response":


data: {"response": "Thank you 


data: {"response": "Thank you for your
```


#### Incrementally emit JSON parts


```sse
data: {"response":


data:  "Thank you 


data: for your
```

#### Emit structured JSON parts (events)

```sse
event: response
data: {"response": "Thank you for your meal planning request for healthy and fulfilling meals."}


event: suggestedFollowUps
data: {"suggestedFollowUps": ["Prepare a shopping list for the ingredients needed for the selected recipes."]}

event: recipe
data: {"recipe": {"id": "6464b6f5-17bf-4744-90f6-dbaab3af9983","name": "Mexican Quinoa", ... }
```

#### Delta patching


```sse
data: {"type":"response.token","payload":"Thank you"}


data: {"type":"response.token","payload":"for your"}
```

Or even more complicated

* `{"v": [{"p": "/message/content/parts/0", "o": "append", "v": " systems combine:\n\n```\nSemantic chunking"}, {"p": "/message/metadata/token_count", "o": "replace", "v": 1018}]}`
* `[{"op": "add", "path": "/chunks/2", "value": " up?"}]}}]`


* zobaczyć jak sa wysyłane
  * chatgpt
    * różnicówka
    * event stream
  * perplexity
  * my
  * inne?


różnicówka - perplexity

```json
{"backend_uuid": "b1fc625d-8db1-431b-a84e-a2d38ce56276", "context_uuid": "3f405c77-e998-4410-99f7-84a2f2604ba1", "uuid": "9a2a69c1-efc2-4337-9e28-ea1842f1986a", "frontend_context_uuid": "45e6802a-7b84-4c5d-8f25-cdad4b3a1dfb", "display_model": "turbo", "mode": "CONCISE", "search_focus": "internet", "source": "default", "attachments": [], "read_write_token": "e0e17cb3-445e-4038-9243-d1600baa4eaf", "thread_url_slug": "b1fc625d-8db1-431b-a84e-a2d38ce56276", "expect_search_results": "false", "gpt4": false, "text_completed": false, "blocks": [{"intended_usage": "ask_text_0_markdown", "diff_block": {"field": "markdown_block", "patches": [{"op": "replace", "path": "", "value": {"progress": "IN_PROGRESS", "chunks": ["hey there \ud83d\ude42 "], "chunk_starting_offset": 0, "answer": null, "media_items": null, "inline_token_annotations": []}}]}}, {"intended_usage": "ask_text", "diff_block": {"field": "markdown_block", "patches": [{"op": "replace", "path": "", "value": {"progress": "IN_PROGRESS", "chunks": ["hey there \ud83d\ude42 "], "chunk_starting_offset": 0, "answer": null, "media_items": null, "inline_token_annotations": null}}]}}], "message_mode": "STREAMING", "answer_modes": [{"answer_mode_type": "SEARCH", "has_preview": false}, {"answer_mode_type": "IMAGE", "has_preview": false}], "structured_answer_block_usages": ["ask_text_0_markdown"], "reconnectable": true, "image_completions": [], "cursor": "06a03510-e96d-71cb-8000-c52ea8abf774", "classifier_results": {"personal_search": false, "skip_search": true, "widget_type": "GENERAL", "hide_nav": false, "hide_sources": false, "image_generation": false, "time_widget": false, "mhe_predictions": {"skip_search": true, "image_generation_intent": false, "time_widget": false, "places_search_intent": false, "shopping_intent": false, "movie_lists_intent": false, "image_preview": false, "video_preview": false, "nav_intent": false, "personal_search": false, "weather_widget": false, "finance_widget_gating": false, "calculator_widget": false, "comet_nav_widget_combined_target": false, "finance_agent_gating": false}, "mhe_predictions_full": {"skip_search": {"is_true": true, "probability": 0.93359375, "threshold": 0.4}, "image_generation_intent": {"is_true": false, "probability": 0.00023078918, "threshold": 0.98}, "time_widget": {"is_true": false, "probability": 1.4722347e-05, "threshold": 0.8}, "places_search_intent": {"is_true": false, "probability": 0.004211426, "threshold": 0.85}, "shopping_intent": {"is_true": false, "probability": 5.4836273e-05, "threshold": 0.8}, "movie_lists_intent": {"is_true": false, "probability": 0.0008544922, "threshold": 0.65}, "image_preview": {"is_true": false, "probability": 0.0018692017, "threshold": 0.42}, "video_preview": {"is_true": false, "probability": 0.0013275146, "threshold": 0.5}, "nav_intent": {"is_true": false, "probability": 0.0005531311, "threshold": 0.5}, "personal_search": {"is_true": false, "probability": 0.00390625, "threshold": 0.050000000000000044}, "skip_personal_search": {"is_true": true, "probability": 0.99609375, "threshold": 0.95}, "weather_widget": {"is_true": false, "probability": 0.00031471252, "threshold": 0.4}, "finance_widget_gating": {"is_true": false, "probability": 0.0018081665, "threshold": 0.53}, "calculator_widget": {"is_true": false, "probability": 3.5017729e-06, "threshold": 0.3}, "comet_nav_widget_combined_target": {"is_true": false, "probability": 0.012817383, "threshold": 0.5}, "domain_subdomain": {"label": "OTHER/OTHER", "probability": 0.98046875}, "finance_agent_gating": {"is_true": false, "probability": 2.4318695e-05, "threshold": 0.7}}}, "search_implementation_mode": "fast", "telemetry_data": {"has_displayed_search_results": false, "has_first_output_token": true, "has_first_token": true, "country": "PL", "is_followup": false, "source": "default", "engine_mode": "auto", "search_implementation_mode": "fast", "has_widget_data": false, "has_useful_renderable_content": true, "region": "us-east-1", "has_nav_results": false, "early_nav_v3_call": false}, "search_mode": "SEARCH", "status": "PENDING", "final_sse_message": false}

{"backend_uuid": "b1fc625d-8db1-431b-a84e-a2d38ce56276", "context_uuid": "3f405c77-e998-4410-99f7-84a2f2604ba1", "uuid": "9a2a69c1-efc2-4337-9e28-ea1842f1986a", "frontend_context_uuid": "45e6802a-7b84-4c5d-8f25-cdad4b3a1dfb", "display_model": "turbo", "mode": "CONCISE", "search_focus": "internet", "source": "default", "attachments": [], "read_write_token": "e0e17cb3-445e-4038-9243-d1600baa4eaf", "thread_url_slug": "b1fc625d-8db1-431b-a84e-a2d38ce56276", "expect_search_results": "false", "gpt4": false, "text_completed": true, "blocks": [{"intended_usage": "ask_text_0_markdown", "diff_block": {"field": "markdown_block", "patches": [{"op": "add", "path": "/chunks/2", "value": " up?"}]}}, {"intended_usage": "ask_text", "diff_block": {"field": "markdown_block", "patches": [{"op": "add", "path": "/chunks/2", "value": " up?"}]}}], "message_mode": "STREAMING", "answer_modes": [{"answer_mode_type": "SEARCH", "has_preview": false}, {"answer_mode_type": "IMAGE", "has_preview": false}], "structured_answer_block_usages": ["ask_text_0_markdown"], "reconnectable": true, "image_completions": [], "cursor": "06a03510-eb5e-7d7b-8000-d498cc241797", "classifier_results": {"personal_search": false, "skip_search": true, "widget_type": "GENERAL", "hide_nav": false, "hide_sources": false, "image_generation": false, "time_widget": false, "mhe_predictions": {"skip_search": true, "image_generation_intent": false, "time_widget": false, "places_search_intent": false, "shopping_intent": false, "movie_lists_intent": false, "image_preview": false, "video_preview": false, "nav_intent": false, "personal_search": false, "weather_widget": false, "finance_widget_gating": false, "calculator_widget": false, "comet_nav_widget_combined_target": false, "finance_agent_gating": false}, "mhe_predictions_full": {"skip_search": {"is_true": true, "probability": 0.93359375, "threshold": 0.4}, "image_generation_intent": {"is_true": false, "probability": 0.00023078918, "threshold": 0.98}, "time_widget": {"is_true": false, "probability": 1.4722347e-05, "threshold": 0.8}, "places_search_intent": {"is_true": false, "probability": 0.004211426, "threshold": 0.85}, "shopping_intent": {"is_true": false, "probability": 5.4836273e-05, "threshold": 0.8}, "movie_lists_intent": {"is_true": false, "probability": 0.0008544922, "threshold": 0.65}, "image_preview": {"is_true": false, "probability": 0.0018692017, "threshold": 0.42}, "video_preview": {"is_true": false, "probability": 0.0013275146, "threshold": 0.5}, "nav_intent": {"is_true": false, "probability": 0.0005531311, "threshold": 0.5}, "personal_search": {"is_true": false, "probability": 0.00390625, "threshold": 0.050000000000000044}, "skip_personal_search": {"is_true": true, "probability": 0.99609375, "threshold": 0.95}, "weather_widget": {"is_true": false, "probability": 0.00031471252, "threshold": 0.4}, "finance_widget_gating": {"is_true": false, "probability": 0.0018081665, "threshold": 0.53}, "calculator_widget": {"is_true": false, "probability": 3.5017729e-06, "threshold": 0.3}, "comet_nav_widget_combined_target": {"is_true": false, "probability": 0.012817383, "threshold": 0.5}, "domain_subdomain": {"label": "OTHER/OTHER", "probability": 0.98046875}, "finance_agent_gating": {"is_true": false, "probability": 2.4318695e-05, "threshold": 0.7}}}, "search_implementation_mode": "fast", "search_mode": "SEARCH", "status": "PENDING", "final": true, "final_sse_message": false}
```

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