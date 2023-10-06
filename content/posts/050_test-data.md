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
dodać personal touch... - że to dla mnei jest wygodne
```
![Cover](jason-leung-V-HPvi4B4G0-unsplash.jpg)
> Cover image by [Jason Leung](https://unsplash.com/@ninjason) on [Unsplash](https://unsplash.com)


*Many of us have been in a situation where writing application code is quick, easy, and enjoyable. However, when it comes to test code, it often turns out to be time-consuming, tedious, and boring. There can be several reasons for this, one of which is the necessity of preparing a set of test data. In some extreme cases, this data preparation may consume a significant portion of the test body. This not only becomes inconvenient when we only want to test a small part of the code but also decreases the overall readability of the test. In this post, I'll demonstrate how this issue can be simplified using Test Data Builder.*

## Preparing test data is boring and tedious

Let's be honest, how familiar does this code look to you?   

```java
class DeliveryTest {

  @Test
  void delivery_is_canceled_if_was_just_created() {
    //given
    Food pizza = new Food("Pizza Margherita", 1);
    Food coke = new Food("Coke", 1);
    Delivery delivery = new Delivery(UUID.randomUUID(), List.of(pizza, coke), "Main Street 1, Naples")    
    
    //when
    delivery.changeStatus(CANCELED)    
    
    //then
    assertEquals(CANCELED, delivery.status());
  }
}
```

Even for a seemingly simple test case, we must create the `Delivery` class with all its necessary fields. Now, envision if this class were significantly more complex, perhaps requiring an address represented by a separate class (possibly with GPS coordinates); it would swiftly become challenging to manage.

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

## So let's use the magic tool!

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

The last benefit and the essential reason why to use the discussed pattern is that it allows to construct objects for various classes. Typically, projects contains a subset of entities, data transfer objects (DTOs), domain classes, messaging classes, and more. While they serve different purposes, they often share common data fields/schemes. The logic for initializing each of them can be encapsulated in a method that takes all required data (whether default or overriden) stored in the Test Data Builder and invokes the class's constructor to yield a new instance. This is the purpose of the previously mentioned `entity()` method in the examples — it prepares an entity class for use in the test.


## Which is not a magic at all!

```
todo - got to the insights, zajrzeć w bebechy, etc.
```

Let's have our hands dirty and and dive into creating the Test Data Builder for delivery objects, as mentioned in the previous section.

The first step is to create a class with fields designed to hold the default values necessary for constructing the `Delivery` object:

```java
import java.util.UUID;

import static io.delivery.domain.DeliveryStatus.CREATED;
import static io.delivery.domain.FoodTestData.anFood;

class DeliveryTestData {

  private UUID id = UUID.randomUUID();
  private DeliveryStatus status = CREATED;
  private String address = "Main Street 1, Naples";
  private List<FoodTestData> foods = List.of(aFood());
}
```

It's up to you how to name this class. Personally, I tend to use the suffix `TestData`, but other options like `Builder` work equally well. What's crucial is maintaining consistent naming conventions throughout the entire project.

It's worth noting that the `DeliveryTestData` class contains a list of `FoodTestData`. This represents another builder for classes associated with food, and it is structured as follows:

```java
class FoodTestData {

  private String name = "Pizza Margherita";
  private int amount = 1;
}
```

The next step is to prohibit the creation of `DeliveryTestData` using the default constructor and, instead, enable its creation using the `aDelivery()` static factory method:

```java
class DeliveryTestData {

  private UUID id = UUID.randomUUID();
  private DeliveryStatus status = CREATED;
  private String address = "Main Street 1, Naples";
  private List<FoodTestData> foods = List.of(aFood());  
  
  private DeliveryTestData() {};  
  
  public static DeliveryTestData aDelivery() {
    return new DeliveryTestData();
  }
}
```

The same thing needs to be done in the second builder class - `FoodTestData`, but let's skip it here and all other further steps, to keep this post short.

Since all fields are private we need to allow to modify them. Instead of creating setters let's create `with...` methods for each one of them:

```java
class DeliveryTestData {

  private UUID id = UUID.randomUUID();
  private DeliveryStatus status = CREATED;
  private String address = "Main Street 1, Naples";
  private List<FoodTestData> foods = List.of(aFood());  
  
  private DeliveryTestData() {};  
  
  public static DeliveryTestData aDelivery() {
    return new DeliveryTestData();
  }

  public DeliveryTestData withId(UUID id) {
    this.id = id;
    return this;
  }

  public DeliveryTestData withStatus(DeliveryStatus status) {
    this.status = status;
    return this;
  }

  public DeliveryTestData withAddress(String address) {
    this.address = address;
    return this;
  }

  public DeliveryTestData withFoods(FoodTestData... foods) {
    this.foods = Arrays.asList(foods);
    return this;
  }

}
```

Notice that each method returns the instance of modified class ("classic" setter method is always `void`). This little trick enables chaing `with()` methods, for example for teh test we would like to override two default properties:

```java
class SomeTest {

  void test() {
      
    aDelivery()
      .withStatus(COMPLETED)
      .withAddress("Main Road 2");
  }
}
```

Next, crucial, part is to prepare methods that will be responsible for creating target objects. In my case I want to allow to create an entity and DTO (for controller) classes, but you can create more if needed.

```java
class DeliveryTestData {

  private UUID id = UUID.randomUUID();
  private DeliveryStatus status = CREATED;
  private String address = "Main Street 1, Naples";
  private List<FoodTestData> foods = List.of(aFood());  
  
  private DeliveryTestData() {};  
  
  public static DeliveryTestData aDelivery() {
    return new DeliveryTestData();
  }

  public DeliveryEntity entity() {
    DeliveryEntity entity = new DeliveryEntity();
    entity.setId(id);
    entity.setStatus(status);
    entity.setAddress(address);
    entity.setFoods(
      foods.stream()
        .map(FoodTestData::entity)
        .toList()
    );

    return entity;
  }

  public DeliveryDTO dto() {
    return new DeliveryEntity(
        id,
        status,
        address,
        foods.stream()
            .map(FoodTestData::dto)
            .toList()
    );
  }

  //all with...(...) methods
}
```

The last step is to allow to read values from private fields so they can be used in test assertions. For that either create it manually (or generate them using an IDE) as it's done here - using [Lombok](https://projectlombok.org/) annotation:

```java
import lombok.Getter;

@Getter
class DeliveryTestData {

  //content of the class    
}
```

## And can be used in Integration tests

Test Data Builders are great for unit tests, but how about integration tests when in the set up phase of a test data needs to be inserted into the database? Can we use this types of classes as well here? The answer is - of course!

Let's say that we would like to write an integration test for a custom repository method (in a Spring Data repository). For example, we have a method to get the count of deliveries of a certain food:

```java
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;


interface DeliveryRepository extends JpaRepository<Delivery, UUID> {


  @Query(nativeQuery = true, value = """
  SELECT count(*) 
  FROM delivery d 
  LEFT JOIN delivery_food df ON d.id = df.delivery_id
  WHERE df.food_name = ':foodName'
  """)
  long totalDeliveriesCountForFood(@Param("foodName") String foodName);
}
```

And a test can look like this, assuming that in the `IntegrationTest` class there is code responsible for spinning up the database using the Testcontainers (exemplary code can be found [here](https://github.com/wkrzywiec/farm-to-table/blob/master/services/delivery/src/test/groovy/io/wkrzywiec/fooddelivery/delivery/IntegrationTest.groovy)) so that we can skip the setup here:

```java
import org.springframework.beans.factory.annotation.Autowired;

class DeliveryRepositoryIntegrationTest extends IntegrationTest {

  @Autowired
  private DeliveryRepository deliveryRepository;
  private TestRepository testRepository;  
  
  @Before
  void init() {
      testRepository = new TestRepository(deliveryRepository);
  } 

  void two_delivieres_are_returned_if_two_were_made() {
    //given
    String foodName = "Pierogi";  
    DeliveryTestData delivery1 = aDelivery()
      .withFood(
        aFood()
          .withName(foodName)
      );  
    
    DeliveryTestData delivery2 = aDelivery()
      .withFood(
        aFood()
          .withName(foodName)
      );  
    
    testRepository.saveAll(delivery1, delivery2);  
    
    //when
    long result = deliveryRepository.totalDeliveriesCountForFood(foodName);  
    
    //then
    assertEquals(2, result);
  }
}
```

The above test is very similiar to the unit tests written before. All the setup phase is done in one place and it's starightforward - 2 delivieres are created with the same food and then saved into a database. There are no need to create any SQL inserts to make this test happening. What's the key to this shape of an integration test? The `TestRepository` class.

As the name may suggest the purpose of it is to be used during tests to persist the Test Data Builder object in a database. There are several ways how it could be implemented, here is how it could be implemented for Postgres database using Spring Data's repository:

```java
import org.springframework.transaction.annotation;

public class TestRepository {

  private final DeliveryRepository deliveryRepository;  
  
  public TestRepository(DeliveryRepository deliveryRepository) {
    this.deliveryRepository = deliveryRepository;
  }

  @Transactional
  public List<Delivery> saveAll(DeliveryTestData... deliveries) {
    return Arrays.stream(deliveries)
      .map(this::save)
      .toList();
  }

  @Transactional
  public Delivery save(DeliveryTestData testData) {
    Delivery entity = testData.entity();
    return deliveryRepository.save(entity);
  }
}  
```

As you can see the `TestRepository` is a simple wrapper for Spring Data's repository. It is in this case, beacuse the object graph (of `Delivery` and list of `Food`) is relatively simple. When we have more complicated data structure or complex ORM mapping (e.g. bidirectional many-to-one association) it is beneficial to keep entity preparation and persitence logic inside the `TestRepository` class.

And of course we don't need to be limited to the above solution. E.g. instead of using Hibernate it can be implemented using JDBC (or Spring's `JdbcTemplate`), jOOQ or any other way tool of your choice. 

## So should we use it everywhere?

Like every other tool Test Data Builder needs to be used when it fits the most. Does it fit in every project? Of course not!

So when not to use it?

First of all the better readeability comes with a price of a higher maintanance. In order to use it first needs to be created. If a data model is large (there are lots of properties or there are lots of elements in the object graph) it will require some time to shadow it with Test Data Builder. Also, if it changes frequently it will also require more work to keep truck with changes (but on the other hand, the same situation will be in the classic approach).

Also using it for a small project (e.g. serverless functions) it might be an overkill. If a project has small number of usecases it might be quicker, and easier to read, to prepare specific data for each test case. The same goes if a particualr object graph is used only a couple times. It is no sense to prepare a Test Data Builder and then use it 3-4 times. It's better to set up those tests without it. 

Finally not every projects follow the pattern - fetch data, modify it, persist it and notify an invoker of this action of a result. There are projects which are less typical and may need special approach. 

Apart from these three cases I would encourage you to give a try to a Test Data Builder in your applications. With a little bit of effort you can gain a lot of benefits described previously.

## Let's wrap up

It's time to conclude this post with quick summary why Test Data Builders are worth be used:

* they give a convenient and quick way to prepare data for test
* they increase the readability of test by introducing notation close to the natural language
* they're hiding irrelevant parts of test data preparation letting to focus only on the key parts that are important for a particualr test
* they provide a single place for initilizing various data transfer objects used in the test
* thanks to them unit and integration tests may be very similar to each other

Of course we also need to remember that for some projects it's better not to use this pattern. Especially for small or constantly changing ones the maintanace may very large.

If you need more examples of Test Data Builder go check my project on GitHub - [wkrzywiec/farm-to-table](https://github.com/wkrzywiec/farm-to-table). 


## And if you need more sources

* [How to Create a Test Data Builder | Code With Arho](https://www.arhohuttunen.com/test-data-builders/)

dodać info a grafach? jak zapisywać? jak traktować? jak tworzyć te obiekty- że zawsze zaczynać od roota

spradzić w chat gpt od `And can be used in Integration tests``