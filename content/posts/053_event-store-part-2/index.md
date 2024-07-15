---
title: "Is Event Sourcing hard? Part 2: How to store events"
date: 2024-06-25
summary: "Learn how to build a simple event store in Java using PostgreSQL as the database."
description: ""
tags: ["events", "event-sourcing", "event-store", "java", "craftmanship", "architecture", "database", "postgresql", "kafka"]
---

*You have decided that event sourcing is a great fit for your project and meets all your needs. The next step is to figure out how to persist events. While there are several tools available off the shelf, what if you could build your own event store technology? In this article, I will cover how to build the very first version of such a solution based on PostgreSQL, which can be utilized in Java applications.*

![cover](cover.jpg)

The key element in event sourcing are (surprise, surprise) events. These events are created after each business action is performed on a domain object (aggregate) and need to be persisted somewhere. They are also used to rebuild the state of domain objects, but first, they need to be fetched from some kind of storage. For these (and other) reasons, the central piece of an event sourcing system is the **event store** which will be built through out this post.

If you are not familiar with event sourcing, please check my previous article on that topic. - [Is Event Sourcing hard? Part 1: Let's build a domain object from events](http://localhost:1313/posts/052_event-sourcing-part-1/?utm_source=blog).

## What is an Event Store?

An event store is crucial in event sourcing applications. But what requirements should it meet?

* **Event store should allow storing events.**
* **Events stored in the event store can't be modified** - Events are business actions that occurred in the past. We cannot change history, and we cannot change events stored in the event store. Therefore, everything stored there remains as it was.
* **Events must be added to the end of a stream** - Every event persisted must be ordered, at least within a stream. A stream is a collection of events that refer to a single domain object. The event store should forbid saving any event in any position other than the end of a stream.
* **All events in a stream are ordered** - Not only must storing events preserve their order, but loading them must also maintain the order of their occurrence. This is crucial for replaying them to rebuild the state of a domain object.

These are the requirements that will be covered by the implementation of the event store in this article. Fully-fledged event stores provide other capabilities, such as:

* **Events can be fetched up to a certain point in time** - Sometimes, there is a need to see how the domain object looked in the past. Therefore, only a subset of events can be loaded, starting from the beginning and finishing at the event that occurred before the given point in time. That's real time traveling in practice!
* **Events are globally ordered** - It's beneficial to order events not only within a stream but also across streams, especially when interaction between domain objects is needed or building projections from multiple streams.
* **Notify subscribers about changes in a stream** - An event store may not only play the role of data storage but also act as a pub-sub solution. Whenever a new event is appended to a stream, subscribers (e.g., a service responsible for updating projections) are notified about it to perform their tasks.
* **Store bi-temporal events** - An event store may not only store information about the past but can also be used to store facts about the future! Bi-temporal event sourcing is a technique of adding a new property `validAt` to events, representing when they are valid and not when they were stored. This allows storing events from the future, which may be beneficial if we're sure that something will happen at a certain point in time. For example, a discount can be applied to a product in an e-commerce shop before Black Friday, but it will be valid only on that day.

These are only examples of capabilities. There are certainly more, and you can check them in one of the off-the-shelf solutions, which are either fully operational databases or frameworks built on top of popular databases (e.g., PostgreSQL):

* [EventStoreDB](https://www.eventstore.com/eventstoredb)
* [Axon Server](https://www.axoniq.io/products/axon-server)
* [Marten](https://martendb.io/)
* [Rails Event Store](https://railseventstore.org/)

That's it for the core concepts of an event store. There are, of course, more nuances, but for this blog post, I'll limit it to the basics.

## Core implementation

Let's get our hands dirty and implement these concepts in a Java application using PostgreSQL as the storage technology.

> **Readers discretion is adivsed** - the following implementation is only one of many possible ones. Depending on the project, requirements, and team preferences, it may look different. There is no one implementation to rule them all. I want you to keep that in mind; this is my preferred solution for my pet project. But of course, you're more than welcome to share your opinion so we can all learn from each other.

### Creating a Database Table

The first step is to define a table where all events will be persisted. Here is the SQL statement to create a simple `events` table:

```sql
CREATE TABLE IF NOT EXISTS events
 (
    id                  UUID NOT NULL,
    stream_id           UUID NOT NULL,
    type                VARCHAR(256) NOT NULL,
    data                JSONB NOT NULL,
    added_at            TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
);
```

Where:

* `id` - is the identification of an event,
* `stream_id` -  is the ID of the domain object that the event pertains to,
* `type` - is the definition of the event type (e.g., `OrderDelivered`),
* `data` - all information that is part of an event is stored here. The `JSONB` column type indicates that it is stored in a JSON format,
* `added_at` - is the timestamp of when the event was added/occurred.

This statement can be part of a data migration tool, such as Liquibase or Flyway.

And that's pretty much it (at least for now). We have a very simple table where we can store events. Therefore, let's move on to implementing the part of the code that is responsible for saving events.

### Storing Events

The first step is to define the interface of the event store so that we can have multiple implementations of it:

```java
public interface EventStore {

    void store(EventEntity event);

    default void store(List<EventEntity> events) {
        events.forEach(this::store);
    }
}
```

Nothing fancy here. The class that will implement this interface will need to cover the `store(EventEntity event)` method. In the case of a list of events, the interface already provides a default implementation.

The `EventEntity` object represents the record from the database table that was just defined:

```java
@Data
public class EventEntity {

    protected UUID id;
    protected UUID streamId;
    protected String type;
    protected DomainEvent data;
    protected Instant addedAt;
}
```

The `DomainEvent` in my case is an interface. Each event holds its own set of data but must provide information about the ID of the stream into which the event will be stored:

```java
public interface DomainEvent {
    UUID streamId();
}
```

And here is an example of a concrete class, which is a Java record:

```java
record DeliveryCanceled(
        UUID orderId,
        String reason
) implements DomainEvent {

    @Overrides
    default UUID streamId() {
        return orderId();
    }
}
```

Since in the context of a delivery the `streamId` is the same as the `orderId`, the method defined in the interface returns the `orderId`.

Returning to the `EventStore` interface, here is an implementation of the `store(EventEntity event)` method:

```java
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.jdbc.core.namedparam.SqlParameterSource;

import java.sql.Timestamp;
import java.util.List;

@Slf4j
public class PostgresEventStore implements EventStore {

    private final NamedParameterJdbcTemplate jdbcTemplate;
    private final ObjectMapper objectMapper;

    public PostgresEventStore(NamedParameterJdbcTemplate jdbcTemplate, ObjectMapper objectMapper) {
        this.jdbcTemplate = jdbcTemplate;
        this.objectMapper = objectMapper;
    }

    @Override
    public void store(EventEntity event) {
        log.info("Saving event in a store. Event: {}", event);

        var bodyAsJsonString = mapEventData(event.data());

        SqlParameterSource parameters = new MapSqlParameterSource()
                .addValue("event_id", event.id())
                .addValue("stream_id", event.streamId())
                .addValue("type", event.type())
                .addValue("data", bodyAsJsonString)
                .addValue("added_at", Timestamp.from(event.addedAt()));

        jdbcTemplate.update("""
                INSERT INTO events(id, stream_id, type, data, added_at)
                SELECT :event_id, :stream_id, :type, :data::jsonb, :added_at
                """,
                parameters)
        );
        log.info("Event was stored.");
    }

    private String mapEventData(DomainEvent domainEvent) throws RuntimeException {
        try {
            return objectMapper.writeValueAsString(domainEvent);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed to map DomainEvent to JSON before storing event.", e);
        }
    }
}
```

Since my application is written with Spring Boot, the `NamedParameterJdbcTemplate` was used to integrate with PostgreSQL. Apart from that, the only other role of the method is to transform the Java object of the `DomainEvent` into its JSON String representation, for which the Jackson `ObjectMapper` is used.

If you would like to test if this code is really working, you can check the integration test that I've written, which is available here: [PostgresEventStoreIT.groovy](https://github.com/wkrzywiec/farm-to-table/blob/master/services/commons/src/test/groovy/io/wkrzywiec/fooddelivery/commons/infra/store/PostgresEventStoreIT.groovy)

### Loading Events

Persisting events is covered, so let's now implement the code for fetching them. First, we need to add a method definition to the interface:

```java
public interface EventStore {

    List<EventEntity> loadEvents(UUID streamId);
}
```

And concrete implementation of it:

```java
@Slf4j
public class PostgresEventStore implements EventStore {

    private final NamedParameterJdbcTemplate jdbcTemplate;
    private final EventPostgresRowMapper eventPostgresRowMapper;
    private final ObjectMapper objectMapper;

    public PostgresEventStore(NamedParameterJdbcTemplate jdbcTemplate, ObjectMapper objectMapper, EventClassTypeProvider eventClassTypeProvider) {
        this.jdbcTemplate = jdbcTemplate;
        this.objectMapper = objectMapper;
        this.eventPostgresRowMapper = new EventPostgresRowMapper(objectMapper, eventClassTypeProvider);
    }

    @Override
    public List<EventEntity> loadEvents(UUID streamId) {

        return jdbcTemplate.query("""
                SELECT id, stream_id, type, data, added_at
                FROM events
                ORDER BY added_at ASC;
                """,
                eventPostgresRowMapper,
                streamId);
    }
}
```

Nothing fancy here, except for the `EventPostgresRowMapper` and `EventClassTypeProvider`. These components are responsible for deserializing information stored in the database into `EventEntity` and its `data` part (`DomainEvent`), respectively.

```java
@RequiredArgsConstructor
@Slf4j
class EventPostgresRowMapper implements RowMapper<EventEntity> {

    private final ObjectMapper objectMapper;
    private final EventClassTypeProvider caster;

    @Override
    public EventEntity mapRow(ResultSet rs, int rowNum) throws SQLException {
        String eventType = rs.getString("type");
        DomainEvent event = extractData(rs, eventType);
        return new EventEntity(
                rs.getString("id"),
                rs.getString("stream_id"),
                eventType,
                event,
                extractInstant(rs, "added_at")
        );
    }

    private static Instant extractInstant(ResultSet rs, String columnName) throws SQLException {
        if (rs.getTimestamp(columnName) == null) {
            return null;
        }
        return rs.getTimestamp(columnName).toInstant();
    }

    private DomainEvent extractData(ResultSet rs, String eventType) throws SQLException {
        String bodyAsString = rs.getString("data");
        JsonNode bodyAsJsonNode = mapToJsonNode(bodyAsString);
        return mapEventBody(bodyAsJsonNode, eventType);
    }

    private JsonNode mapToJsonNode(String eventAsString) {
        try {
            return objectMapper.readTree(eventAsString);
        } catch (JsonProcessingException e) {
            log.error("Failed to parse event to json: {}", eventAsString);
            throw new RuntimeException("Parsing error", e);
        }
    }

    private DomainEvent mapEventBody(JsonNode eventBody, String eventType) {
        Class<? extends DomainEvent> classType = caster.getClassType(eventType);
        return mapEventBody(eventBody, classType);
    }

    private <T extends DomainEvent> T mapEventBody(JsonNode eventBody, Class<T> valueType) {
        try {
            return objectMapper.treeToValue(eventBody, valueType);
        } catch (JsonProcessingException e) {
            log.error("Failed to parse event json: {} to '{}' class", eventBody, valueType.getCanonicalName());
            throw new RuntimeException("Parsing error", e);
        }
    }
}
```

The implementation of the `EventPostgresRowMapper` is quite generic and can be reused. It extends Spring's `RowMapper`, where we define how the `ResultSet` from the database should be used to build an `EventEntity`.

The only part that must be adjusted to specific `DomainEvents` is the `EventClassTypeProvider`, which is an interface that helps the `ObjectMapper` cast the result from the `data` column into the appropriate Java class:

```java
public interface EventClassTypeProvider {

    Class<? extends DomainEvent> getClassType(String type);
}
```

And an example of its implementation:

```java
@Slf4j
class DeliveryEventClassTypeProvider implements EventClassTypeProvider {

    @Override
    public Class<? extends DomainEvent> getClassType(String type) {
        return switch (type) {
            case "DeliveryCanceled" -> DeliveryEvent.DeliveryCanceled.class;
            default -> {
                log.error("There is not logic for mapping {} event from a store", type);
                throw new IllegalArgumentException();
            }
        };
    }
}
```

As before, tests for this functionality are available in [PostgresEventStoreIT.groovy](https://github.com/wkrzywiec/farm-to-table/blob/master/services/commons/src/test/groovy/io/wkrzywiec/fooddelivery/commons/infra/store/PostgresEventStoreIT.groovy) class.

## Optimistic Locking for Strong Consistency

The implementation we have so far is pretty basic. It may work for a small side project used by only one person, but it may not fit the needs of a larger solution (and I'm not claiming it's production-ready yet!) where multiple users may try to store different events to the same stream at the same moment.

The foundation of the event store is that all events are stored in the order of their occurrence. But what happens if, at the same time, two threads want to append to the same stream? Which one should be accepted? Maybe both? If it were a bank transaction, do we want to accept two events that would reduce the account balance below zero? How do we ensure that events that should not happen are not stored in the event store?

One way of handling this would be pessimistic locking. It's a database mechanism that prevents a row (or an entire table) from being read or modified if another transaction is making changes to it. If there is any chance that a thread reading data performs it at the moment when an update is occurring, the database will force the reading thread to wait until the update thread finishes.

This could be a good candidate for handling conflicts in the event store. However, besides the inherent problem of possible deadlock occurrence, it introduces additional limitations. Locking the entire table would introduce a bottleneck to the entire application because, in the case of adding a new event, reading them (or adding new ones to another stream) won't be possible due to the lock. It would make the event store really slow, especially in the case of lots of write operations.

A better approach would be to use optimistic locking. This is not a built-in database mechanism, however. It's a strategy for handling concurrent operations. In the "regular" approach to storing business information, optimistic locking is realized by introducing an additional integer column - `version`. An application first needs to load data from the database, including the version, and then it performs tasks based on it. As a result, it updates the same row in the database. Within an update statement, the current version of the row must be provided. If it is the same as in the database, the row is updated, and the `version` column is increased by one. If one of the threads tries to update a row but with an old version, the database should forbid it.

With the event store, we don't follow this pattern since we don't modify rows, but we can use optimistic locking to ensure that only correct events are stored and they are ordered.

The first step is to add a *BIGINT* `version` column to the `events` table:

```sql
CREATE TABLE IF NOT EXISTS events
 (
    stream_id           UUID NOT NULL,
    version             BIGINT NOT NULL,
    ... other columns

    UNIQUE (stream_id, version)
);
```

Please note that besides adding a new column, I've added a unique constraint on the pair of `stream_id` and `version` columns. This way, we will ensure that there are no rows with the same pair of values.

However, this is not the only change that needs to be made. The concept of versions must be introduced to the code itself. The decision on how deeply this concept will penetrate the code is an important one to make.

The least invasive method would be to extend the storing method of the `EventStore` interface with the `latestVersion` parameter. This version still needs to be obtained from somewhere. REST endpoints must include it, and in a message-based system, incoming messages must include it. But the good news is that the version does not leak into the domain logic.

I, however, have decided to go in the opposite direction. I have introduced versions into the domain logic as well, mainly because I wanted to encapsulate the versioning logic within the domain layer to keep the application layer as thin as possible. Was it a good decision? Maybe. Maybe not. I'll see in the future as the project evolves.

From [the previous article](https://wkrzywiec.is-a.dev/posts/052_event-sourcing-part-1/), you may remember that I generate `DomainEvent` within each domain method, e.g.:

```java
public class Delivery {

    private int version;
    private DeliveryStatus status;
    List<DomainEvent> changes = new ArrayList<>();

    public void cancel(String reason) {
        if (status != DeliveryStatus.CREATED) {
            throw new DeliveryException(format("Failed to cancel a %s delivery. It's not possible do it for a delivery with '%s' status", orderId, status));
        }
        this.status = DeliveryStatus.CANCELED;

        increaseVersion();
        changes.add(new DeliveryEvent.DeliveryCanceled(orderId, version, reason));
    }

    private void increaseVersion() {
        this.version = this.version + 1;
    }
}  
```

The introduction of versioning requires incrementing the version whenever a domain object is modified (hence the `increaseVersion()` method). It also necessitates introducing a version to each `DomainEvent`:

```java
public interface DomainEvent {
    UUID streamId();
    int version();
}
```

And that's pretty much what is peculiar in my project. Other parts should be the same or quite similar. So let's jump into the new implementation of the `EventStore`.

But before that, let's list all the requirements that it needs to cover because optimistic locking introduces these:

* Only events with a version succeeding the latest version within a stream can be stored.
* Events with an already stored version can't be persisted.
* There should not be gaps between versions.
* Loaded events are ordered by version.

With all of this in mind, let's see the implementation:

```java
public class PostgresEventStore implements EventStore {

    @Override
    public void store(EventEntity event) {
        log.info("Saving event in a store. Event: {}", event);

        var bodyAsJsonString = mapEventData(event.data());

        SqlParameterSource parameters = new MapSqlParameterSource()
                .addValue("event_id", event.id())
                .addValue("stream_id", event.streamId())
                .addValue("version", event.version())
                .addValue("type", event.type())
                .addValue("data", bodyAsJsonString)
                .addValue("added_at", Timestamp.from(event.addedAt()));

        int insertedRowsCount = 0;
        try {
            insertedRowsCount = jdbcTemplate.update("""
                WITH latest_version AS (
                    SELECT MAX(version) AS value
                    FROM events
                    WHERE stream_id = :stream_id
                )
                INSERT INTO events(id, stream_id, version, type, data, added_at)
                SELECT :event_id, :stream_id, :version, :type, :data::jsonb, :added_at
                FROM latest_version
                WHERE :version = value + 1 OR :version = 0
                """,
                    parameters
            );
        } catch (DuplicateKeyException exception) {
            log.error("Failed to persist event in event store due to duplicate key violation", exception);
            throw new InvalidEventVersionException();
        }

        if (insertedRowsCount == 0) {
            log.error("Event was not stored due to invalid event version");
            throw new InvalidEventVersionException();
        }
        log.info("Event was stored");
    }
}
```

Phew, that's a lot of code! Let's unwrap it.

First of all, we need to know which is the latest version in a stream. Hence, the Common Table Expressions (CTE), `WITH latest_version`, was added to fetch it. Then it is used in the `WHERE` clause to verify that the version provided in the event is exactly one larger than the latest version. There is also another condition that checks if an event is the first one in a stream; for such events, the previous condition is not needed.

The `jdbcTemplate.update(...)` method is wrapped with a `try ... catch ...` block because the unique key constraint for `stream_id` and `version` was introduced. If a violation occurs, a custom `InvalidEventVersionException` is thrown.

The same exception is thrown if nothing is persisted in the database. This may happen if any of the mentioned conditions are not met.

The above implementation covers all requirements, and if you would like to verify it, there are tests available in the [PostgresEventStoreIT.groovy](https://github.com/wkrzywiec/farm-to-table/blob/master/services/commons/src/test/groovy/io/wkrzywiec/fooddelivery/commons/infra/store/PostgresEventStoreIT.groovy) class.

> Please note that these are not the only changes that are needed. The ones that I have skipped include adding the `version` field to the `EventEntity`, adding deserialization logic for this field in `EventPostgresRowMapper`, and adjusting the loading of events in the `PostgresEventStore` class to order events by `version`. These changes are very simple, so I have kept them out of this article, but they can be reviewed in the repository [wkrzywiec/farm-to-table](https://github.com/wkrzywiec/farm-to-table).

## Microservice world - one or per-service event store?

I really like the shape of the event store that we have so far, so let's add another twist to it: how to fit an event store in a microservice world?

The rule of thumb in the microservice world is that shared databases must be avoided. Services should have their own databases and communicate with each other using an established API. Sooner or later, a shared database will lead to a situation where one of the services needs to introduce a non-backward-compatible change (e.g., rename/delete a column). Since other services are using the same database, they also need to change something on their side. This makes independent service deployment impossible. Deployment of all services must be done simultaneously with data migration.

For this main reason, most microservices have their own databases. So in the case of an event store, should we follow the same pattern? As always, it depends.

Let's play devil's advocate and try to figure out if a shared event store is a good idea. First of all, the problem mentioned above is rather non-existent because **an event store schema is relatively stable**. Moreover, event stores are append-only logs, so once we save data there, it should not be modified, which also limits the need for data migration. Besides addressing the major pain point of a shared database, a **common event store may be very helpful in integrating services**. By introducing a subscription mechanism, services may start to listen for certain events that are stored and act upon them. So there would be no need to have a fancy event bus (like Kafka or RabbitMQ). Also, having data in a single place makes it much easier to query, which may be very helpful in troubleshooting or preparing various reports.

Of course, having a single database has its downsides too. **It is a single point of failure** — if it does not work, most parts of your system are not working either. Also, with a large number of microservices, **it must be prepared to handle a large number of concurrent connections**, which might be quite a challenge even for a medium-sized distributed system. And finally, I mentioned that the database schema is stable and does not change, but that may not be true. It can evolve over time, especially when new concepts must be introduced (like global ordering or bi-temporal events) but weren't planned ahead.

There might be, of course, other factors than the ones mentioned above. So whenever you need to decide which solution to use, don't limit yourself to one way or another. Try to weigh all the pros and cons and decide which approach is better for you.

In my pet project, I have decided to use the shared event store, chiefly because it is a small project. A single event store removes the unnecessary task of managing multiple databases and finally gives me an opportunity to try to implement the subscription mechanism.

As a consequence of this decision a new column to the `events` table was added. The `channel` *VARCHAR* column stores information which service is writing to the particualr stream. In my case if it's an *ordering* service a value is `ordering` and if it's a *delivery* service a value if `delivery`. Pretty straight-forward.

As a consequence of this decision, a new column was added to the `events` table. The `channel` *VARCHAR* column stores information about which service is writing to the particular stream. In my case, if it's an *ordering* service, the value is `"ordering"`, and if it's a *delivery* service, the value is `"delivery"`. Pretty straightforward.

The implementation of this is simple (it is only the addition of a new column), so I'll skip it here. But if you would like to check the final solution, go check the code in the [wkrzywiec/farm-to-table](https://github.com/wkrzywiec/farm-to-table) repository.

## And Why Not Kafka?

Before we wrap up, let's dive into one more very polarizing issue: *Is Kafka a good candidate for an event store?*

At the first glance it is and there are lots of people that confirm that. But let's check the requirements that were mentioned earlier, which an event store needs to fulfill, to figure it out on our own:

* ✅ **Event store should allow storing events** - By default, Kafka stores messages for 2 weeks, but it is possible to extend the retention time infinitely.
* ✅ **Events stored in the event store can't be modified** - Every message stored in Kafka can't be modified.
* ✅ **All events in a stream are ordered** - Kafka has topic partitions and ensures that all messages within a given partition (in our case, it could be a streamId) are ordered.
* ✅ / ❌ **Events must be added to the end of a stream** - In a highly concurrent system where multiple producers write to the same topic partition, it is not possible to control the order of messages within it or to disallow incorrect ones. There is a proposal [KAFKA-2260](https://issues.apache.org/jira/browse/KAFKA-2260) to be able to provide an offset during the write, but as of today, it is still open.
* ✅ / ❌ **Events can be fetched up to a certain point in time** - There is no built-in functionality, but there is a way to achieve it.
* ❌ **Events are globally ordered** - Kafka guarantees the order of messages only within a single partition. Events stored within a single or multiple topics would not be ordered.
* ✅ **Notify subscribers about changes in a stream** - Kafka allows subscribing to its topics and notifies consumers about adding new messages.
* ✅ **Store bi-temporal events**

Most of the points are green, so should we go ahead with Kafka? Not so fast.

Depending on the situation, a lack of one of these capabilities may be a showstopper. The biggest, in my eyes, is the fact that Kafka does not support and does not have a way to introduce optimistic locking. This means that in the case of concurrent writes, there will be no mechanism to protect one of these writes. For instance, let's say that we have a delivery that is canceled and updated in 2 separate threads. With Kafka, we could end up with a situation where the update is written to the stream after the delivery is canceled (which, from a business point of view, should never happen).

Also, the lack of global ordering may be a blocker for those systems that need to merge events from multiple streams.

Therefore, in my opinion, for small systems, it may be a good candidate to consider, but there are cases where it's better to keep it away. But still, Kafka is a great tool designed to move data from one place to another, and for that (not storage), it is the best solution.

## Summary

I hope that after reading this article, you know more about event stores and how they can be implemented in a Java application using a PostgreSQL database. I encourage you to try it yourself, perhaps with a slightly different approach, to get the full experience of learning all its bits and pieces.

If you would like to check the entire code of my project, visit the GitHub repository: [wkrzywiec/farm-to-table](https://github.com/wkrzywiec/farm-to-table).

And if you would like to learn more about event stores and event sourcing, check the links below.

## References

utm links with campaing - event-sourcing-series
gifs?

* [Building an Event Storage | Greg Young](https://cqrs.wordpress.com/documents/building-event-storage/)
* [Let's build event store in one hour! | event-driven.io](https://event-driven.io/pl/lets_build_event_store_in_one_hour/)
* [Implementing event sourcing using a relational database | softwaremill.com](https://softwaremill.com/implementing-event-sourcing-using-a-relational-database/)
* [Fixing the past and dealing with the future using bi-temporal EventSourcing | blog.arkency.com](https://blog.arkency.com/fixing-the-past-and-dealing-with-the-future-using-bi-temporal-eventsourcing/)
* [Event Streaming is not Event Sourcing! | event-driven.io](https://event-driven.io/en/event_streaming_is_not_event_sourcing/)
