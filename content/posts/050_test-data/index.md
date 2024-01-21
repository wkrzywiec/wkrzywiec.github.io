---
title: "Prepare Test Data Quicker with Test Data Builder!"
date: 2023-10-08
summary: "Discover the benefits of using Test Data Builder to improve test code readability"
description: "Discover the power of Test Data Builder for clearer test code! Dive into this article to explore its benefits and learn how to implement it in Java, making it versatile for both unit and integration tests."
tags: ["java", "tests", "data", "craftsmanship", "database", "hibernate", "jdbc", "quality", "test-data-builder"]
---

{{< imgh src="050_test-data-cover.jpg" alt="cover" >}}

> Photo by [Rachel Park](https://unsplash.com/@therachelstory) on [Unsplash](https://unsplash.com)


*Many of us have been in a situation where writing application code is quick, easy, and enjoyable. However, when it comes to test code, it often turns out to be time-consuming, tedious, and boring. There can be several reasons for this, one of which is the necessity of preparing a set of test data. In some extreme cases, this data preparation may consume a significant portion of the test body. This not only becomes inconvenient when we only want to test a small part of the code but also decreases the overall readability of the test. In this post, I'll demonstrate how this issue can be simplified using Test Data Builder.*

## Preparing test data is boring and tedious!

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

Such approach solves the problem of tedious work for test setup but only partially. What if each test requires a slightly different setup? Arguments can be added to this method to make it more customizable, but in a very large set of tests, the number of arguments may quickly become very big and hard to maintain.

```java
private Delivery aNewDelivery(String address, List<Food> foods) {
  return new Delivery(UUID.randomUUID(), foods, address);
}
```

Is there a different approach to it? Is there a way to avoid all this setup and at the same time give a flexibility for adjustments of our test data? 

## So let's use the magic tool...

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

It is somehow easier to read if we compare with a first approach, but it looks a little bit off with this `entity()` at the end. Without it would look pretty close to the second approach. Where is a gain here then?

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

The last benefit and the essential reason why to use the discussed pattern is that it allows to construct objects for various classes. Typically, projects contain a subset of entities, data transfer objects (DTOs), domain classes, messaging classes, and more. While they serve different purposes, they often share common data fields/schemes. The logic for initializing each of them can be encapsulated in a method that takes all required data (whether default or overriden) stored in the Test Data Builder and invokes the class's constructor to yield a new instance. This is the purpose of the previously mentioned `entity()` method in the examples — it prepares an entity class for use in the test.


## ...which is not a magic at all...

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

Notice that each method returns the instance of modified class ("classic" setter method is always `void`). This little trick enables chaing `with()` methods, for example for the test we would like to override two default properties:

```java
class SomeTest {

  void test() {
      
    var delivery = aDelivery()
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

The final step is to enable the reading of values from private fields so that they can be used in test assertions. This can be achieved either by creating them manually or generating them using an IDE, as demonstrated here with the [Lombok](https://projectlombok.org/) annotation:


```java
import lombok.Getter;

@Getter
class DeliveryTestData {

  //content of the class    
}
```

## ...and can be used in Integration tests!

Test Data Builders are excellent for unit tests, but what about integration tests? In the setup phase of an integration test, we often need to insert data into the database. Can we also use these types of classes for that purpose? The answer is - absolutely!

Let's assume we want to create an integration test for a custom repository method in a Spring Data repository. For instance, we have a method to retrieve the count of deliveries for a specific type of food:

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

A test can take this form, assuming that within the IntegrationTest class, there is code responsible for launching the database using Testcontainers (exemplary code can be found [here](https://github.com/wkrzywiec/farm-to-table/blob/master/services/delivery/src/test/groovy/io/wkrzywiec/fooddelivery/delivery/IntegrationTest.groovy)). This allows us to skip the setup here:


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

The test above is very similar to the unit tests written earlier. All the setup phases are consolidated into one place, and it's straightforward: two deliveries with the same food are created and then saved into a database. There is no need to create any SQL inserts to make this test work. So, what's the key to this structure of an integration test? The `TestRepository` class.

As the name suggests, its purpose is to be used during tests to persist the Test Data Builder object in a database. There are several ways to implement it. Here's one way it could be implemented for a Postgres database using Spring Data's repository:

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

Here, you can see that the `TestRepository` is a straightforward wrapper for Spring Data's repository. It takes on this role because the object graph (comprising `Delivery` and a list of `Food`) is relatively simple. However, when dealing with more complex data structures or intricate ORM mappings (such as bidirectional many-to-one associations), it becomes beneficial to centralize entity preparation and persistence logic within the `TestRepository` class.

Of course, you're not limited to the above solution. Instead of using Hibernate, you can implement it using JDBC (or Spring's `JdbcTemplate`), jOOQ, or any other tool of your choice.
So, should we use it everywhere?

Like any other tool, Test Data Builder should be employed where it fits best. Does it fit every project? Certainly not!

## When should you avoid using it?

First and foremost, improved readability comes at the cost of higher maintenance. To use it, you need to create it first. If a data model is extensive (meaning many properties or elements in the object graph), it will take some time to set up Test Data Builder. Moreover, if the data model changes frequently, it will require more effort to keep up with these changes (though the same challenge applies to the classic approach).

Using it for a small project (e.g., serverless functions) might be overkill as well. In such cases, where a project has a small number of use cases, it may be quicker and easier to prepare specific data for each test case. The same holds true if a particular object graph is only used a couple of times. There's no sense in creating a Test Data Builder and then using it just a few times. It's better to set up those tests without it.

Lastly, not all projects follow the pattern of fetching data, modifying it, persisting it, and notifying an invoker of this action's result. Some projects are less typical and may require a special approach.

Aside from these three cases, I encourage you to give Test Data Builder a try in your applications. With a little effort, you can reap the benefits described earlier.

## Let's wrap up

It's time to wrap up this post with a quick summary of why Test Data Builders are worth using:

* They provide a convenient and efficient way to prepare test data.
* They enhance test readability by introducing notation close to natural language.
* They conceal irrelevant parts of test data preparation, allowing you to focus only on the key aspects important for a particular test.
* They offer a single location for initializing various data transfer objects used in tests.
* Thanks to them, unit and integration tests can closely resemble each other.

Of course, it's important to remember that for certain projects, this pattern may not be the best choice. Especially for small or rapidly changing projects, the maintenance effort can be significant.

If you're looking for more examples of Test Data Builders, feel free to check out my project on GitHub - [wkrzywiec/farm-to-table](https://github.com/wkrzywiec/farm-to-table).


## And if you need more sources

* [How to Create a Test Data Builder | Code With Arho](https://www.arhohuttunen.com/test-data-builders/)
