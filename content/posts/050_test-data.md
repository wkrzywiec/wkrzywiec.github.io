---
title: "Test Data Builder"
date: 2023-09-02
summary: "Discover the benefits of using Test Data Builder to improve test code readability"
description: "Discover the power of Test Data Builder for clearer test code! Dive into this article to explore its benefits and learn how to implement it in Java, making it versatile for both unit and integration tests."
tags: ["java", "tests", "data", "craftsmanship", "database", "hibernate", "jdbc", "quality", "test-data-builder"]
---

https://www.arhohuttunen.com/test-data-builders/
https://blog.codeleak.pl/2014/06/test-data-builders-and-object-mother.html?m=1

```
TODO - znaleźć obrazek
```
![Cover](jason-leung-V-HPvi4B4G0-unsplash.jpg)
> Cover image by [Jason Leung](https://unsplash.com/@ninjason) on [Unsplash](https://unsplash.com)


*Many of us have been in a situation where writing application code is quick, easy, and enjoyable. However, when it comes to test code, it often turns out to be time-consuming, tedious, and boring. There can be several reasons for this, one of which is the necessity of preparing a set of test data. In some extreme cases, this data preparation may consume a significant portion of the test body. This not only becomes inconvenient when we only want to test a small part of the code but also decreases the overall readability of the test. In this post, I'll demonstrate how this issue can be simplified using Test Data Builder.*

## Setting test data is boring and tedious!

Let's be honest, how familiar does this code look to you?   

```java
class DeliveryTest {

    @Test
    void delivery_is_canceled_if_was_just_created() {
        //given
        Food pizza = new Food("Pizza Margherita", 1);
        Food coke = new Food("Coke", 1);
        Delivery delivery = new Delivery(UUID.randomUUID(), List.of(pizza, coke), "Main Street 1, Naples");

        //when
        delivery.changeStatus(CANCELED);

        //then
        assertEquals(CANCELED, delivery.status());
    }
}
```

Even for a seemingly simple test case, we must create the `Delivery`` class with all its necessary fields. Now, envision if this class were significantly more complex, perhaps requiring an address represented by a separate class (possibly with GPS coordinates); it would swiftly become challenging to manage.

Furthermore, it would complicate the readability and comprehension of the code. Why should we input an address when the sole purpose of the test is to validate the cancellation of a delivery? Our tests should clearly convey their intent and the preconditions required to fulfill them.

One way to tackle these problems is to move all setup steps into a private method so that it is not only encapsulated in an elegant method but also can be reused across other test cases.


```java

class DeliveryTest {

    @Test
    void delivery_is_canceled_if_was_just_created() {
        //given
        Delivery delivery = aNewDelivery();

        //when
        delivery.changeStatus(CANCELED);

        //then
        assertEquals(CANCELED, delivery.status());
    }

    private Delivery aNewDelivery() {
        Food pizza = new Food("Pizza Margherita", 1);
        Food coke = new Food("Coke", 1);
        return new Delivery(UUID.randomUUID(), List.of(pizza, coke), "Main Street 1, Naples");
    }
}
```

Such approach solves the problem of tedious work for test setup but only partially. What if each test requires a slightly different setup? Arguments can be added to this method to make it more customizable, but in a very large set of tests, the number of arguments may quickly become very large and hard to maintain.

```java
private Delivery aNewDelivery(String address, List<Food> foods) {
    return new Delivery(UUID.randomUUID(), foods, address);
}
```

Is there a different approach to it? Is there a way to avoid all this setup and at the same time give a flexibility for adjustments of our test data? 

## Test Data Builder - a way to simplify our tests

Let's introduce a Test Data Builder object which will be responsible for generating test data. 

```java
class DeliveryTest {

    @Test
    void delivery_is_canceled_if_was_just_created() {
        //given
        Delivery delivery = DeliveryTestData.aNewDelivery().entity();

        //when
        delivery.changeStatus(CANCELED);

        //then
        assertEquals(CANCELED, delivery.status());
    }
}
```

It is somehow easier to read if we compare with a first approach, but it looks a little bit off with this `entity()` at the end. Without it would look pretty close to the second approach. Where is a gain here?

Let's have another test example to see the benefit of using Test Data Builder:


```java
class DeliveryTest {

    @Test
    void delivery_can_not_be_completed_if_was_canceled() {
        //given
        Delivery delivery = aDelivery()
                                .withStatus(CANCELED)
                                .entity();

        //when & then
        assertThrows(
            IllegalStateException.class, 
            () -> delivery.changeStatus(COMPLETED));
    }
}
```

Here, the `Delivery` object is instantiated with all default values except for one – its status. The Test Data Builder offers a an easy to use method to override these values. By using it, we can concentrate on the essence of this test – it becomes evident that only the status affects the test's outcome. Other properties, having no such impact, are not explicitly provided here. This results in a cleaner and more comprehensible test.

Furthermore, the way this object is set up closely resembles natural language. If we omit the brackets in the previous example, we obtain a clear statement: `a delivery with status canceled`. Comparing this to the initial approach with numerous constructor arguments, it becomes evident which is easier to read.

The last benefit and the essential reason why to use the discussed pattern is that it allows to construct objects for various classes. Typically, projects contains a subset of entities, data transfer objects (DTOs), domain classes, messaging classes, and more. While they serve different purposes, they often share common data fields/schemes. The logic for initializing each of them can be encapsulated in a method that takes all required data (whether default or overriden) stored in the Test Data Builder and invokes the class's constructor to yield a new instance. This is the purpose of the previously mentioned entity() method in the examples — it prepares an entity class for use in the test.


## How to achieve it ?

data holders
* new class
* private fields with default values
* static constructor
* with

transformer
* entity, message, dto - zaznaczyć, że jeśli nie są do siebie podobne to obiekty to zrobić odrębne klasy
* opisać jak wolisz to nazywać

## Where else it can be good to use?

* used both for unit and integration tests
    * same approach
    * easy to move tests from unit to integration
    * no @Sql (easier to read)
    * repozytorium do zapisu danych ()

## Kiedy nie używać

* mały projekt
* dużo maintainence

## summary

benefits - wypunktować
