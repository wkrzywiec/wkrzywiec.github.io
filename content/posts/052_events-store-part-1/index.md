---
title: "Is event sourcing hard? Part 1. Let's have a event store thingy"
date: 2024-04-27
summary: "How and when to user flatmap function in Java stream"
description: ""
tags: ["java", "craftmanship", "architecture", "events", "event-sourcing", "event-store", "postgresql", "database"]
---

What if I told you that there is a different way of storing business entities other than as entries in tables of relationship database or JSONs in document key-values stores or graphs in graph databases? Of course people can invent anything but the key is - will it be useable?

And the answer is - yes, there is another way which is not yet another way of doing the same thing but it also adds value to "traditional" ways of storing entities. This another way is a called **event sourcing** and is getting its momentum nowadays. 

This is my first article of  "Is event sourcing hard?" series in which I'll take a practical approach and try to implement key concepts of *event sourcing* in Java. In each article I will tackle different aspect of it. E.g. in this I'm focusing on explaining what event sourcing is and show how it could look like in the code. In next ones I'll focus on adding additional elements connected with *event sourcing*, like events store or outbox. Moreover I'll explore more advanced concepts like how to version events, how to create snapshot events or how to handle bi-temporal events. But that's not everything that I have planned for this series!

My article is of course not the first on this topic. In fact if you google it you will find a plethora of great resources far more advanced and deeper into it than this one. For instance a great blog by [Oskar Dudycz - event-driven.io](https://event-driven.io/) is an awesome source of information on *event sourcing*.

With my series I'm not trying to broader this topic. It's just my take on it, on how I understand it with a little bit of playing around with its concepts.

### What is event souring?

In the essence the concept is very simple. Instead of storing information about our models as database entries we store facts about them. Instead of storing properties of an entity we're storing all events that pertain to it. 

To visualize it let's check on an example and let's say that we want to model a delivery for a service that provides food to home. Here are some business events that can occur:

![events example](1-events.png)

Now, the idea is to store them as they are in an **events store**. When a new action needs to be performed on a specific delivery (e.g. it needs to be canceled) the application needs first to load all events and then process them to rebuild the current state of a delivery:

![event-sourcing](2-event-sourcing.png)

There are multiple ways on how it could be achieved in the code. Here is an example of the `Delivery` class which has a static factory method `from(List<Event> events)` which accepts a list of events and produces the domain object:

```java
@Getter  
@EqualsAndHashCode  
@ToString  
public class Delivery {  
    private String orderId;  
    private String customerId;  
    private String farmId;  
    private String deliveryManId;  
    private DeliveryStatus status;  
    private String address;  
    private List<Item> items;  
    private BigDecimal deliveryCharge = new BigDecimal(0);  
    private BigDecimal tip = new BigDecimal(0);  
    private BigDecimal total = new BigDecimal(0);  
    private Map<String, String> metadata = new HashMap<>();

    private Delivery() {};

    public static Delivery from(List<Event> events) {
        Delivery delivery = null;
        
        for (Event event: events) {
            switch (event.body()) {
                case DeliveryCreated created -> {
                    delivery = new Delivery();

                    delivery.orderId = created.orderId();
                    delivery.customerId = created.customerId();
                    delivery.farmId = created.farmId();
                    delivery.status = DeliveryStatus.CREATED;
                    delivery.address = created.address();
                    delivery.items = mapItems(created.items());
                    delivery.deliveryCharge = created.deliveryCharge();
                    delivery.total = created.total();

                    Map<String, String> metadata = new HashMap<>();
                    metadata.put("creationTimestamp", event.header().createdAt().toString());
                    delivery.metadata = metadata;
                    return delivery;
                }

                case DeliveryManAssigned deliveryManAssigned -> {
                    delivery.deliveryManId = deliveryManAssigned.deliveryManId();
                }

                case FoodWasPickedUp foodWasPickedUp -> {
                    var metadata = delivery.getMetadata();
                    metadata.put("foodPickedUpTimestamp", event.header().createdAt().toString());

                    delivery.metadata = metadata;
                    delivery.status = DeliveryStatus.FOOD_PICKED;
                }

                case FoodDelivered foodDelivered -> {
                    var metadata = delivery.getMetadata();
                    metadata.put("foodDeliveredTimestamp", event.header().createdAt().toString());

                    delivery.metadata = metadata;
                    delivery.status = DeliveryStatus.FOOD_DELIVERED;
                }

                case TipAddedToDelivery tipAddedToDelivery -> {
                    delivery.tip = tipAddedToDelivery.tip();
                    delivery.total = tipAddedToDelivery.total();
                }

                default -> throw new IllegalStateException("Failed to replay events to build delivery object. Unhandled events: " + event.body().getClass());
            }
        }
        return delivery;
    }

    private static List<Item> mapItems(List<io.wkrzywiec.fooddelivery.delivery.domain.incoming.Item> items) {
        return items.stream().map(dto -> Item.builder()
                .name(dto.name())
                .amount(dto.amount())
                .pricePerItem(dto.pricePerItem())
                .build()).toList();
    }
}
```

The idea is quite simple. The factory method iterates through the entire list of events (it's important that events are sorted by they occurence) and creates a new object from information stored in an event and/or previous state of a delivery.

To understand it better let's have a closer look. First step of a method is to define the variable for a resulting `Delivery` which at begining is pointing to a `null`. Then interation through events begins which starts from the `DeliveryCreated` event which holds all necessary data:

```java
public record DeliveryCreated (
    String orderId, String customerId,
    String farmId, String address, List<Item> items,
    BigDecimal deliveryCharge, BigDecimal total ) { }
```

based on which a private constructor is used to create an empty `Delivery` object and then set all initial fields:

```java
    public static Delivery from(List<Event> events) {
        Delivery delivery = null
        
        for (Event event: events) {
            switch (event.body()) {

                case DeliveryCreated created -> {
                    delivery = new Delivery();

                    delivery.orderId = created.orderId();
                    delivery.customerId = created.customerId();
                    delivery.farmId = created.farmId();
                    delivery.status = DeliveryStatus.CREATED;
                    delivery.address = created.address();
                    delivery.items = mapItems(created.items());
                    delivery.deliveryCharge = created.deliveryCharge();
                    delivery.total = created.total();

                    Map<String, String> metadata = new HashMap<>();
                    metadata.put("creationTimestamp", event.header().createdAt().toString());
                    delivery.metadata = metadata;
                    return delivery;
                }
            }
        }
        return delivery;
    }
```

All following events will be mutating the `delivery` object but in a very limited way. For instance `FoodWasPickedUp` event contains only two information `orderId` and what happened business wise which is represented by the class name:

```java
public record FoodWasPickedUp(String orderId) implements DomainEventBody {}
```

Going back to the event replaying loop - if an event is of the `FoodWasPickedUp` type the delivery status is changed to `FOOD_PICKED` and the metadata is updated:

```java
    public static Delivery from(List<Event> events) {
        Delivery delivery = // existing object recreated from previous events
        
        for (Event event: events) {
            switch (event.body()) {

                case FoodWasPickedUp foodWasPickedUp -> {
                    var metadata = delivery.getMetadata();
                    metadata.put("foodPickedUpTimestamp", event.header().createdAt().toString());

                    delivery.metadata = metadata;
                    delivery.status = DeliveryStatus.FOOD_PICKED;
                }
            }
        }
        return delivery;
    }
```

And the same goes with all other events which either change the status of a delivery or one of its property, for instance adding a tip to a delivery results in changing tip value and overall cost of a delivery:

```java
    public static Delivery from(List<Event> events) {
        Delivery delivery = // existing object recreated from previous events
        
        for (Event event: events) {
            switch (event.body()) {

                case TipAddedToDelivery tipAddedToDelivery -> {
                    delivery.tip = tipAddedToDelivery.tip();
                    delivery.total = tipAddedToDelivery.total();
                }
            }
        }
        return delivery;
    }
```

And this is it. In the essence this is how the current state of an entity can be rebuild from events.

Are there any other ways than this? Sure they are. For instance the entire method could be extracted from a domain object and moved to a separate factory class:

```java
public class DeliveryFactory {

    public static Delivery from(List<Message> events) {
        Delivery delivery = null;
        for (Message event: events) {
            switch (event.body()) {
                case DeliveryCreated created -> {
                    delivery = new Delivery();

                    delivery.setOrderId(created.orderId());
                    delivery.setCustomerId(created.customerId());
                    delivery.setFarmId(created.farmId());
                    delivery.setStatus(DeliveryStatus.CREATED);
                    delivery.setAddress(created.address());
                    delivery.setItems(mapItems(created.items()));
                    delivery.setDeliveryCharge(created.deliveryCharge());
                    delivery.setTotal(created.total());

                    Map<String, String> metadata = new HashMap<>();
                    metadata.put("creationTimestamp", event.header().createdAt().toString());
                    delivery.setMetadata(metadata);
                    return delivery;
                }

                case DeliveryManAssigned deliveryManAssigned -> {
                    delivery.setDeliveryManId(deliveryManAssigned.deliveryManId());
                }

                // all other cases

                default -> throw new IllegalStateException("Failed to replay events to build delivery object. Unhandled events: " + event.body().getClass());
            }
        }
        return delivery;
    }


}
```

The problem with this approach is that it enforces to create setters for each property of an object, which opens up the object to be modified in other parts of a code. And if we want to have our domain object written in the Domain Driven Design fashion, not as a simple Data Transfer Object, this can't happen. Modification of any property of an object must go thrugh special business methods in `Delivery` which are protecting business rules. Methods like:

```java
public class Delivery {  

    public void assignDeliveryMan(String deliveryManId) {
        if (this.deliveryManId != null) {
            throw new DeliveryException(format("Failed to assign delivery man to an '%s' order. There is already a delivery man assigned with an orderId %s", orderId, this.deliveryManId));
        }

        if (List.of(DeliveryStatus.CANCELED, DeliveryStatus.FOOD_PICKED, DeliveryStatus.FOOD_DELIVERED).contains(status)) {
            throw new DeliveryException(format("Failed to assign a delivery man to an '%s' order. It's not possible do it for a delivery with '%s' status", orderId, status));
        }

        this.deliveryManId = deliveryManId;
    }
}
```

Ok, so you now know how to implement event sourcing, you know what implementation could look like, therefore select the approach you like the most, code it and push it to production, right? What possibly could go wrong if so many people says that event sourcing is such great techique? 

jak widzidzie jest dużo powtórzeń dla kodu biznesowego oraz do otwarzania eventów; można to połączyć apply commands - te same metody do obsługi biznesowych reguł co do otworzenia encji - https://github.com/eugene-khyst/postgresql-event-sourcing - ale jakieś refleksje są tutaj używane....


duplication, więc może reużycie biznesowych metod

* https://github.com/oskardudycz/EventSourcing.JVM
    * https://github.com/oskardudycz/EventSourcing.JVM/tree/main/workshops/introduction-to-event-sourcing - wyjaśnienie tego workshopa
* https://event-driven.io/en/how_to_get_the_current_entity_state_in_event_sourcing/
* https://github.com/cer/event-sourcing-examples/tree/master/java-spring
    * chris richardson - ale to jest dziwne, i że to jakaś dziwnie stara biblioteka
* https://github.com/eugene-khyst/postgresql-event-sourcing
    * odtwarzanie eventów tymi samymi metodami co biznesowa obsługa
* https://github.com/mguenther/spring-kafka-event-sourcing-sampler
    * jakieś to dziwne... 
* https://github.com/ddd-by-examples/event-source-cqrs-sample
    * wspólne użycie metod do otwarzania eventów jak i do obsługi commandów
* https://github.com/ddd-by-examples/library
* https://event-driven.io/en/this_is_not_your_uncle_java/?utm_source=Architecture_Weekly&utm_medium=email

#### Event sourcing in application

event structure

Event Sourcing is a pattern for storing data as events in an append-only log. This simple definition misses the fact that by storing the events, you also keep the context of the events; you know an invoice was sent and for what reason from the same piece of information. In other storage patterns, the business operation context is usually lost, or sometimes stored elsewhere.

jak wygląda flow serwisu - zrefatorować do jakiegoś generalnego podejścia

events from method invokation
events in service
events as separate list inside

sealed interface

### Why using it?

ledger - natural candidate

https://www.eventstore.com/use-cases

* change in domain object doesn't mean that data migration is needed - it just need a different approach to replay events
* https://event-driven.io/en/never_lose_data_with_event_sourcing/
    * event sourcing prevent from losing information that usually we don't think of - when it was modified. it highly regulated market it might be very important (e.g. in fincance for money laundery) or just to understand how the system is used (what actions brings to the currecnt state - learn how users are using the - finding pesimistic scenarios), create analytics based on that for better ux or turn over the product selling - 
    * events gives an extra dimension - change in time
* audit, time travel (All state changes are kept, so it is possible to move systems backward and forwards in time which is extremely valuable for debugging and “what if” analysis.), Root cause analysis
* events are facts, only needed info, projecttions and how we shape data can be changed, without any data migrations (models can be changed)
* fault tolleratn - if an event is bad, replay state from before the bad event occurs
* https://event-driven.io/en/audit_log_event_sourcing/
    * What makes it unique is the multiple things that you’re getting out of the box, like:
        * easier modelling of business process,
        * not losing business data,
        * extended diagnostics both technical and business,
        * projections to interpret the same facts in multiple ways.
    * Having the needs for those scenarios can be a driver to use Event Sourcing. Just audit needs may not be enough

### Why not using it?

* https://event-driven.io/pl/when_not_to_use_event_sourcing/
        * `What do I mean by _“supportive modules”_? I mean, for instance, a CMS (_Content Management System_), e.g., Confluence, WordPress, OneNote or even Excel. Such systems can be treated as bags for data. You put some data in there, sometimes in plain text, sometimes a table, sometimes a photo. We do not intend to perform advanced data analysis: we just want to store and retrieve data. It’s not essential to know the type of data we’re storing. All will be aligned and handled with the same patterns, e.g. a grid with data, edit form. We create, update, read or delete records. We can use such systems both for everything from wedding planning to warehouse inventory and budgeting.`
        * 1. The team is doing well with the current approach.
            1. The team could benefit from Event Sourcing but thinks they don’t need it.
            2. The team thinks that it needs Event Sourcing, but the team doesn’t have the competence and experience.

----
refactor `Message` -> `Event` (np na liście eventów z metody statycznej)
refactor `DomainMessageBody` -> `DomainEventBody`