---
title: "Is Event Sourcing hard? Part 2: How to store events"
date: 2024-06-25
summary: "Learn how to build a simple event store in PostgreSQL"
description: ""
tags: ["events", "event-sourcing", "event-store", "java", "craftmanship", "architecture", "database", "postgresql", "kafka"]
---

*You have decided that event sourcing is a great fit for your project. It meets all your needs. The next thing to do would be to figure out how to persist events. There are several tools available that could be picked from the shelf, but what if you could build your own event store technology? In this article I'm covering how to build a very first version of such solution based on PostgreSQL and that can be utlizied in Java applications.*

The key thing in event sourcing are (suprise, suprise) events. They are created after each business action is performed on a domain object (aggregate) after which they need to be persisted somewhere. Also they used to rebuild state of domain objects but first they need to be fetched from some kind of a storage. For these (and other) reasons the cental piece of event sourcing system is **event store**.

And if you don't know what event sourcing is, go check my previous article on that topic - [Is Event Sourcing hard? Part 1: Let's build a domain object from events](http://localhost:1313/posts/052_event-sourcing-part-1/?utm_source=blog).

## What is an event store?

Ok, so event store is important in event sourcing applications. What requirements should it have?

* **Event store should allow to store events**
* **Events stored in event store can't be modified** - events are business actions that occured in the past. We cannot change the history and we cannot change events stored in event store, therefore everything stored there remains there as it was at the begining.
* **Events must be added to the end of a stream** - every event persisted must be order at least within a stream. The stream is a collection of events that refers a single domain object. Event store should forbid saving any event in any position but the end of a stream.
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

## Core implementation

Let's get our hands dirty and implement those concepts in Java application using PostgreSQL as a storage technology.

> And one more thing - the following implementation is only one of mulitple possible ones. Dependeing on a project, requirements and team preferences it may look differently. There are no one implementation to rule them all. I want you to keep it that in mind, this is my preferable solution for my pet project. But of course you're more than welcome to share your opinion so we all can learn from each other.

### Creating a database table

First step would be to define a table where all events will be persisted. Here is the SQL statement to create a simple `events` table:

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

* `id` - is an identification of an event,
* `stream_id` - is an id of a domain object that events pertains,
* `type` - is a definition of an event type (e.g. `EventCompleted`),
* `data` - all information that are part of an event are stored here. The `JSONB` column type indicates that it is stored in a JSON format,
* `added_at` - is a timestamp of when the event was added/occured.

This statement can be part of a data migration tool, e.g. Liquibase or Flyway.

And that's pretty much it (at least for now) we have a very simple table where we can store events. Therefore, let's move on to implement the part of the code that is reposible for saving events.

### Storing events

First step is to define the interface of the event store, so that we could have multiple implementation of it:

```java
public interface EventStore {

    void store(EventEntity event);

    default void store(List<EventEntity> events) {
        events.forEach(this::store);
    }
}
```

Nothing fancy here. Class that will implement it would need to cover the `store(EventEntity event)` method. And in case of list of events the interface is already providing a default implementation.

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

The `DomainEvent` in my case is an interface. Each event holds its own set of data, but must provide information the id of a stream into which event will be stored:

```java
public interface DomainEvent {
    UUID streamId();
}
```

And an example of the concrete class which is a Java record:

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

Since in the context of a delivery the `streamId` is the same thing as `orderId` a method defined in an interface is returning the `orderId`.

Going back to the `EventStore` interface here is an implementation of `store(EventEntity event)` method:

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

Since my application is written with Spring Boot the `NamedParameterJdbcTemplate` was used to integrate with PostgreSQL. Apart from that the only other role of the method it transform the Java object of the `DomainEvent` into its JSON String representation and for that Jackson ObjectMapper is used.

If you would like to test if this code is really working you may check the integration test that I've written and is available here: [PostgresEventStoreIT.groovy](https://github.com/wkrzywiec/farm-to-table/blob/master/services/commons/src/test/groovy/io/wkrzywiec/fooddelivery/commons/infra/store/PostgresEventStoreIT.groovy).

### Loading events

Persisting events is covered, let's now implement the code for fetching them. Therefore first we need to add a method definition to an interface:

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

Nothing fancy here, except for already mentioned `EventPostgresRowMapper` and `EventClassTypeProvider`. These are components responsible for deserializing information stored in database into `EventEntity` and its `data` part (`DomainEvent`) respectively.


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

The implementation of the `EventPostgresRowMapper` is pretty generic and can be reused. It extends Spring's `RowMapper` in which we tell how the `ResultSet` from a database should be used to build an `EventEntity`.

The only part that must be adjusted to specific `DomainEvent`s is an `EventClassTypeProvider` which is an interface which helps `ObjectMapper` cast the result from `data` column into a proper Java class:

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

Same as before test for this functionality are available in [PostgresEventStoreIT.groovy](https://github.com/wkrzywiec/farm-to-table/blob/master/services/commons/src/test/groovy/io/wkrzywiec/fooddelivery/commons/infra/store/PostgresEventStoreIT.groovy) class.

## Optimistic locking for Strong Consistency

Implentation that we have so far is pretty basic. It may work for a small side project, used by only one person, but it may not fit the needs to a larger solution (and I'm not claiming the production ready yet!) in which multiple users may try to store different event to the same stream at the same moment.

The foundaition of the event store is that all evebts are stored in order of they occurence. And what happens if at the same time two threads wants to append to the same stream? Which one should be accepted? Maybe both? If it would be a bank transaction do we want to accept two events that would reduce account balance below 0? How to make sure that events that should not happen are not stored in event store?

One way of doing it would be a pesymistic locking. It's a database mechanism that prevents row (or entire table) from being read or modified if another transaction is making changes to them. If there is any chance that thread that is reading data perform it in the moment when update is occuring, a database will force reading thread to wait until the update thread finishes.

This could be a good candidate for handling conflicts for events store, however besides the inheritated problem with possible dead-lock occurence it introduces additional limitation. Locking the entire table would introduce a bottle-neck to the entire application, because in case of adding new event, reading them (or adding new to other stream) won't be possible due to the lock. It would make event store really slow, especially in case of lots of write operations.

The better approach would be to use an optimistic locking. This is not a built-in database mechanism however. It's a strategy of handling concurrent operations. In "regular" approach to store business information optimistic locking is realized by introducing an additional integer column - `version`. An application first needs to load data from database including a version and then it does task based on it and as a result it updates the same row in a database. Within an update statement the currecnt version of a row must be provided. If it is the same as in database the row is updated and a `version` column is increased by one. If one of the threads tries to update a row but with an old version the database should forbid it.

With event store we don't follow this pattern since we don't modify rows but we can use optimisic locking to make sure that only correct events are stored and they are ordered.

First step is to add a *BIGINT* `version` column to the `events` table:

```sql
CREATE TABLE IF NOT EXISTS events
 (
    stream_id           UUID NOT NULL,
    version             BIGINT NOT NULL,
    ... other columns

    UNIQUE (stream_id, version)
);
```

Please not that besides adding a new column I've added a unique constraint on pair of `stream_id` and `version` columns. This way we will make sure that there are no row with pair of same values.

It's however not the only change that needs to be made. A concept of versions must be introduced to the code itself. And the decision how deep this concept will penatrate in code is an important decision to made.

The least invasive method would be to extend the storing method of `EventStore` interface with the `latestVersion` parameter. It still needs to be taken from somewhere. REST endpoints must include them and in message-based system incoming messages must include them. But the good news is - version is not leaking into the domain logic.

I, however, have decided to go in oposite direction. I have introduced versions also into domain logic, mainly because I wanted to encapsulate versioning logic within domain layer to keep application layer as thin as possible. Was it a good decision? Maybe. Maybe not. I'll see in the future with a project evolution.

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

Versioning introduction enforces to increment it whenever a domain object is modified (hence the `increaseVersion()` method). It also enforces to introduce version to each `DomainEvent`:

```java
public interface DomainEvent {
    UUID streamId();
    int version();
}
```

And that's pretty much what I have peculiar in my project. Other parts should be the same or close to similar. So let's jump into the new implementation of the `EventStore`.

But before that, let's list all requirements that it needs to cover because optimistic locking introduces such:

* only event with succeeding to the latest version within a stream can be stored,
* events with already stored version can't be persisted,
* there should not be gaps between versions,
* loaded events are ordered by version.

Having all of it in mind, let's see the implementation:

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

Few, that's a lot of code! Let's unwrap it.

First of all we need to know which is the latest version in a stream, hence the Common Table Expressions (CTE), `WITH latest_version`, was added to fetch it. Then it is used in the `WHERE` clause to verify that version provided in the event is exactly larger by 1 from the latest version. There is also another condition which checks if an event is a first one in a stream, for such previous condition is not needed.

The `jdbcTemplate.update(...)` method was wrapped with `try ... catch ..` block because the unique key constraint for `stream_id` and `version` was introduced. If it happens the custom `InvalidEventVersionException` is thrown. 

The same event is thrown if nothing was persisted in a database. This may happen if any of mentioned conditions is not met.

The above implementation covers all requirements and if you would like to verify it, there are test available in the [PostgresEventStoreIT.groovy](https://github.com/wkrzywiec/farm-to-table/blob/master/services/commons/src/test/groovy/io/wkrzywiec/fooddelivery/commons/infra/store/PostgresEventStoreIT.groovy) class.

> Please note that these are not the only changes that are needed. The ones that I have skipped are adding `version` field to the `EventEntity`, adding deserialization logic for this field in `EventPostgresRowMapper` or adjusting loading events in the `PostgresEventStore` class to order events by `version`. These changes are very simple so I have kept it out of this article but can be reviewed in the repository [wkrzywiec/farm-to-table](https://github.com/wkrzywiec/farm-to-table).

## Microservice world - one or per-service event store?

I realy like the shape of an event store that we have so far, so let's add another twist to it - how to fit an event store in a microservice world?

The rule of thumb in microservice world is that shared databases must be avoided. Services should have their own databases and communicate between each other using an established API. sooner or later shared database will bring down to the situation in which one of the services needs to introduce the non backward-compatible change (e.g. rename/delete a column) and since other services are using the same database they also needs to change something on their side. This makes independent service deployment impossible. Deployment of all services must be done at the same moment as data migration.

For this main reason most microservices have their own databases. So in case of event store we should follow the same pattern, right? As always, it depends.

Let's play the devil advocate and try to figure out if a shared event store is a good idea. First of all the problem mentioned above is rather non-existing in event store because the schema of it is rather stable. Moreover event stores are append-only logs, so once we save data there it should not be modified, which also limits the need for data migration. Beside addressing major pain point of shared database, a common event store may be very helpful in integrating services. By introducing subscribtion mechanism services may start to listen for certain events that are stored and act upon them. So there would be no need to have a fancy event bus (like Kafka or Rabbit). Also having data in a single place makes it a way easier to query, which may be very helpful in troubleshooting or preparing various reports.

Of course having a single database has its downsizes too. It is a single point of failure - if it does not work the most parts of your system is not working too. Also with large amount of microservices it must be prepared to handle a large number of concurrent connections which might be quite a challange even for medium sized distributed system. And finally I've told that database schema is stable and does not change but it may not be true. It can evolve with time especially when new concepts must be introduced (like global ordering or bi-temporal events) but wasn't planned up ahead.

There might be of course other factors than the one mentioned above. So whenever you need to decide which solution don't limit yourself to one way or another. Try to weight all pros and cons and decide what approach is better for your.

In my pet project I have decided to use the shared event store, cheifly because it is a small project, single event store removes unnecessary task of managing multiple databases and finally it gives me an opportunity to try to implement the subscription mechanism.

As a consequence of this decision a new column to the `events` table was added. The `channel` *VARCHAR* column stores information which service is writing to the particualr stream. In my case if it's an *ordering* service a value is `ordering` and if it's a *delivery* service a value if `delivery`. Pretty straight-forward.

The implementation of it is also pretty straight-forward (it is only addition of a new column) therefore I'll skip it here but if you would like to check the final solution go check the code in the [wkrzywiec/farm-to-table](https://github.com/wkrzywiec/farm-to-table) repository.

## And why not Kafka?

Before the wrap up let dive into one more, very polarizing, issue - *is Kafka a good candidate for an event store?*

Let's check requirements that were mentioned earlier which an event store needs to fullfill:

* ✅ **Event store should allow to store events** - by default Kafka is storing messages for 2 weeks, but it is possible to extend retention time to the infinite.
* ✅ **Events stored in event store can't be modified** - every message stored in Kafka can't be modified.
* ✅ **All events in a stream are ordered** - Kafka has topic partitions and makes sure that all messages within a given partion (in our case it could be a streamId) are ordered.
* ✅ / ❌ **Events must be added to the end of a stream** - in a highly concurrent system, where multiple producers writes to the same topic partition it is not possible to have control what will be the order of messages within it or to disallow the incorrect ones. There is a a proposal [KAFKA-2260](https://issues.apache.org/jira/browse/KAFKA-2260) to be able to provide an offset during the write, but up till this day it is still open.
* ✅ / ❌ **Events can be fetched till a certain point of time** - there is no built-in functionality, but there is a way to achieve it.
* ❌ **Events are globally ordered** - Kafka guarantees order of messages only within a single partition, events stored within a single or multiple topics would not be ordered. 
* ✅ **Notify subscribers about changes in a stream** - Kafka allows subsribe to its topics and notify the consumers about adding new messages.
* ✅ **Store bi-temporal events**

Most of the points are green so say go ahead with Kafka, right? Not so fast.

Depending on the situation a lack of one of these capabilities may be a show stoper. The biggest, in my eyes, is the fact that Kafka does not support and does not have a way to introduce the optimistic locking, meaning that in case of concurrent writes there will be no mechanism to protect one of these writes. For instance let's say that we have a delivery which is canceled and updated in 2 separate threads. With Kafka we could end up with a situation when the updated will be written to the stream after the delivery is canceled (which from a business point of view should never happen).

Also lack of global ordering may be blocker for those systems which needs to merge events from multiple streams.

Therefore, in my opinion, for small systems it may be a good candidate to consider but there are cases it's better to keep it away. But still Kafka is a great tool designed to move data from one place to another and for that (not storage) is the best solution.

## Summary

I hope that after reading this article you know more about event store and how it can be implemented in Java application using PostgreSQL database. I would encourage you to try it yourself, maybe with a little different approach to get a full experience of learning its all bits and peaces.

If you would like to check the entire code of my project, go check the GitHub repository - wkrzywiec/farm-to-table.

And if you would like to learn more about event stores and event sourcing check links from below.

## References

* [Building an Event Storage | Greg Young](https://cqrs.wordpress.com/documents/building-event-storage/)
* [Let's build event store in one hour! | event-driven.io](https://event-driven.io/pl/lets_build_event_store_in_one_hour/)
* [Implementing event sourcing using a relational database | softwaremill.com](https://softwaremill.com/implementing-event-sourcing-using-a-relational-database/)
* [Fixing the past and dealing with the future using bi-temporal EventSourcing | blog.arkency.com](https://blog.arkency.com/fixing-the-past-and-dealing-with-the-future-using-bi-temporal-eventsourcing/)
* [Event Streaming is not Event Sourcing! | event-driven.io](https://event-driven.io/en/event_streaming_is_not_event_sourcing/)
