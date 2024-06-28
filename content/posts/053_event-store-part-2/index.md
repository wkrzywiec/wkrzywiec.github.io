---
title: "Is Event Sourcing hard? Part 2: How to store events"
date: 2024-06-25
summary: "Learn how to build a simple event store in PostgreSQL"
description: ""
tags: ["events", "event-sourcing", "event-store", "java", "craftmanship", "architecture", "database", "postgresql"]
---

*You have decided that event sourcing is a great fit for your project. It meets all your needs. The next thing to do would be to figure out how to persist events. There are several tools available that could be picked from the shelf, but what if you could build your own event store technology? In this article I'm covering how to build a very first version of such solution based on PostgreSQL and that can be utlizied in Java applications.*

The key thing in event sourcing are (suprise, suprise) events. They are created after each business action is performed on a domain object (aggregate) after which they need to be persisted somewhere. Also they used to rebuild state of domain objects but first they need to be fetched from some kind of a storage. For these (and other) reasons the cental piece of event sourcing system is **event store**.

    todo add utm source
And if you don't know what event sourcing is, go check my previous article on that topic - [Is Event Sourcing hard? Part 1: Let's build a domain object from events](http://localhost:1313/posts/052_event-sourcing-part-1/).

## What is an event store?

Ok, so event store is important in event sourcing applications. What requirements should it have?

* **Event store should allow to store events**
* **Events stored in event store can't be modified** - events are business actions that occured in the past. We cannot change the history and we cannot change events stored in event store, therefore everything stored there remains there as it was at the begining.
* **Events must be added to the end of a stream** - every event persisted must be order at least within a stream. The stream is a collection of events that pertains a single domain object. Event store should forbid saving any event in any position but the end of a stream.
* **All events in a stream are ordered** - not only storing events but also loading them must preserve the order of their occurance. It is very crucial for replaying them to rebuild the state of a domain object.

These are requirements that will be covered by implementation of event store in this article. Fully fledge event stores are providing other capabilities like:

* **Events can be fetched till a certain point of time** - sometimes there is a need to see how the domain object looked in the past, therefore only a subset of events needs to be loaded starting from the begining and finishing at the event that has occured before the given point of time.
* **Events are globally ordered** - it's beneficial to order events not only within a stream but also across stream in cases when interaction between domain object is needed or when we build projections from multiple streams.
* **Notify subscribers about changes in a stream** - event store may not only play a role of a data storage but also be a pub-sub solution. Whenever a new event is appended to a stream subsribers (e.g. service responsible for updating projections) is notified about it to do its task.
* **Store bi-temporal events** - event store may not only store information about the past but it can also be used to store facts about the future! Bi-temporal event sourcing is a technique of adding a new property `validAt` to events that represents when they are valid and not when they were stored. This allows to store events from the future which may be beneficial if we're sure that something will happen in a certain point of time. E.g. the discount can be applied to a product in e-commerce shop before the Black Friday but it will be valid only at that day.

These are only examples of capabilities. There are certainly more and you can check it in of the out-off-the-shelve solutions which are either a full operational databases or frameworks that are build on top of popular databases (e.g. PostgreSQL):

* [EventStoreDB](https://www.eventstore.com/eventstoredb)
* [Axon Server](https://www.axoniq.io/products/axon-server)
* [Marten](https://martendb.io/)
* [Rails Event Store](https://railseventstore.org/)

That's it for core concepts of event store. There are of course more niuances but for this blog post I'll limit to the basics.

## The core implementation

### Creating a database table

### Storing events

### Loading events

## Versioning

## Microservice world - one or per-service event store?

## And why not Kafka?

## References

* [Building an Event Storage | Greg Young](https://cqrs.wordpress.com/documents/building-event-storage/)
* [Let's build event store in one hour!](https://event-driven.io/pl/lets_build_event_store_in_one_hour/)
* [Implementing event sourcing using a relational database | softwaremill.com](https://softwaremill.com/implementing-event-sourcing-using-a-relational-database/)
* [Fixing the past and dealing with the future using bi-temporal EventSourcing | blog.arkency.com](https://blog.arkency.com/fixing-the-past-and-dealing-with-the-future-using-bi-temporal-eventsourcing/)
