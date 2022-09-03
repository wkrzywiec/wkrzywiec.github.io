
# Ports & Adapters architecture on example
> Source: https://wkrzywiec.medium.com/ports-adapters-architecture-on-example-19cab9e93be7

How you can write your application accordingly to Ports & Adapters (aka Hexagonal) architecture and why you should give it a try.

![Photo by [Bonniebel B](https://unsplash.com/@bonniebelb?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/8064/0*1rZARCVapOCMRiAf)*Photo by [Bonniebel B](https://unsplash.com/@bonniebelb?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

## Introduction

Let’s assume that you’re a freshman at university and you’ve just got first internship in a software engineer company. Or maybe you’re more experience developer who have joined a new company. It doesn’t matter.

Following story is written from the perspective of a newcomer, who makes her/his first steps into new project. Probably it’s a very common for you and I would like to introduce you in this as a way into the *Ports & Adapters *architecture pattern.

As my primary technology is Java, all examples are presented in this language.

### Day 1. Where are controllers, services and repositories packages?

That’s my first day in a new company and right away I’m starting to work on a new project called — *“library”*. It seems to be pretty simple — it’s a management system for handling books & users in a local library. It’s code is publicly available [on GitHub](https://github.com/wkrzywiec/library-hexagonal).

First task, given from John, other developer for this project, was to get familiar with a project, to know it’s structure and how it’s organized, because they’re using less common approach called *Ports & Adapters* mixed with a *Domain Driven Design (DDD)*.

![](https://cdn-images-1.medium.com/max/2000/1*wZ_LKEjmKmsXIl_HEUc7oQ.png)

My first thought? Where are all necessary layers of the application? In all previous projects there were very fine separation between layers and their purpose i.e. ***controllers*** were designed to handle requests from the users, ***repositories*** for fetching and persisting data in a database and ***services*** play role of a middle man, mapping the request from controllers to repositories and adding some logic.

But here? There are no such packages. That’s why I’ve asked John, what the heck. And he told that it might more clear for me if I pick one of domains and take a dip dive in it. As John was explaining, a domain can be described as a small part of an application, but the split is made based on business context. An application was splitted into several domains and each one of them is responsible for a different part of a business logic. E.g. **user** domain is responsible for user management, **inventory** for adding and removing books and **borrowing** for all that it’s related to reserving, borrowing and returning books. That helps to understand what does each of this part from the business perspective. John advised me to first take a look on a simple one — **user**.

![](https://cdn-images-1.medium.com/max/2000/1*7yIjXccTOVzm-HQlCJz_ew.png)

Yes! Finally I see controller, repository and service. They’re named a little bit different, for instance *UserService* is here called here *UserFacade *and they are in a strange sounding packages — **application**, **core** and **infrastructure**. I need to ask John, what they are and why they are not controller, service and repository.

In a meantime I’ve also checked the structure of other *domains* and it seems that this pattern is applied for each domain, like in a *borrowing*:

![](https://cdn-images-1.medium.com/max/2000/1*yxr3Yp5fCQjHaX4IJ1w5DQ.png)

Moving back to the user domain I’ve started to analyzing code from controller (obviously) and here is what I saw:

![](https://cdn-images-1.medium.com/max/2000/1*ZDTr1uwU4wtetwciE1E1mg.png)

Very strange. Instead of a *UserFacade* (service) dependency there is here something called (and names with a verb!) *AddNewUser*, which happens to be only an interface:

![](https://cdn-images-1.medium.com/max/2000/1*J_5zzilbWjsWy14JF4U8Zg.png)

Therefore I’ve checked the *UserFacade* code and it looks like that it’s implementing this interface.

![](https://cdn-images-1.medium.com/max/2000/1*ag2s99yKbduUpaqjQK45QA.png)

The logic seems quite simple, I would say an obvious one. But again a strange thing, *UserDatabase*, a dependency of this class is again an interface!

![](https://cdn-images-1.medium.com/max/2000/1*MR6UpqiheYlzw2NWY5WPMQ.png)

They need to kidding me! Why they’re creating so many interfaces and classes? I would ask John about it, but he already left and went home. Therefore I need to figure it out on my own.

![](https://cdn-images-1.medium.com/max/2000/1*kqi5iltqbyyws_fXUnpqcg.png)

![](https://cdn-images-1.medium.com/max/2000/1*XWfZ5OpW707M4GdRtvozhQ.png)

An implementation of a *UserDatabase*, called *UserDatabaseAdapter*, has a dependency to [*Spring CrudRepository](https://docs.spring.io/spring-data/commons/docs/current/api/org/springframework/data/repository/CrudRepository.html)* which are doing actual job — saving the user. But why it’s done this way? Why they haven’t just used *UserRepository *inside the *UserFacade*?

I think I won’t figure it out today, probably tomorrow John will shed more light on it for me.

### Day 2. Application, core & infrastructure

New day, therefore, after morning coffee and quick chit-chat at the kitchen I asked John if he could explain to me the concept of the *Ports & Adapters* as it’s still blurry for me.

He agreed and started explaining how it goes in their previous project, where business logic where really complicated, there were lots of strange use cases and exceptions. And with it in mind they tried to squeeze somehow this logic into the standard, multi-layer convention which ends up a disaster. Chiefly because there were no single place where such logic was sitting, it was spread across all layers — controllers, services & data persistence.

For these reason they’ve tried a different approach — *Ports & Adapters* (a.k.a. *Hexagonal*) architecture.

The basic concept, and here he started to draw it on a paper, is to divide your application into three main parts:

* **application** — *defines how the outside world interact with an application*, it is a gateway to an application core. It might be by Rest controllers, but it could be also by some kind of a message service (like Kafka, RabbitMQ, etc.), command line client or else,

* **core** — here sits the business logic of your application.** ***The goal is to have it written in a plain language* so that an analyst or even non-technical person could understand. Inside of it we use a domain specific language, which can be easily understand by business people. And another thing,* it should be agnostic of any Java framework* (like *Spring, Jakarta EE, Quarkus, Micronau*t), because these are only scaffolding of an application. And the core is the heart of an application, something that encapsulates the logic.

* **infrastructure** — it’s the last part, most of the applications does not only contain business logic but usually they also need to use some external systems, like database, queue, sFTP server, other application and so on. In this part we say *how* this communication will will be implemented (in a core we only say *what is needed*). For example, in order to persist data in a database we can use several approaches like [Hibernate](https://hibernate.org), [plain Jdbc](https://docs.oracle.com/javase/tutorial/jdbc/basics/index.html), [jOOQ](https://www.jooq.org) or whatever framework we like.

![](https://cdn-images-1.medium.com/max/2230/1*JIDX2XM15YfqRR0NIaZpag.png)
> How it differ from the ‘normal’ layered application? Clearly these ‘parts’ are just controllers, services and repositories, but with odd names. — I’ve asked.

Yeah, a little bit — he replied — they might seem similar concepts, but there is one key difference. *Core* doesn’t know about an *application* and *infrastructure* layers. It should not know anything about the outside world.
> Wait, what? How it could be achieved? — I was a little bit surprised.

Very simple. Inside the *core* we define something that it’s called **Port **it defines all the interactions that a core will have with anything outside. These ports are like contracts (or APIs) and can be divided into two groups** incoming** (primary) and **outgoing** (secondary). First one are responsible of how you can interact with business core (what commands you can use on it) and latter are used by the core to talk to the outside world.

![](https://cdn-images-1.medium.com/max/2000/1*YRdz_q9ojLQQpmTlUmN1uw.png)

To define them we use Java Interfaces, for example here is the definition of one of them, which defines the method for reserving book:

![](https://cdn-images-1.medium.com/max/2000/1*IGgLmXbnYEQt7k3H6XAThA.png)

And the example of outgoing port, will be the database methods:

![](https://cdn-images-1.medium.com/max/2000/1*O4G9X4TCWYVURyy-8e2tpw.png)

Both of them they are located in the ports package in outgoing and incoming sub-packages. Like it’s done here:

![](https://cdn-images-1.medium.com/max/2000/1*94WSGZ65300GoCklZxlXnQ.png)

As you can see **ports are only definitions of *what* we would like to do. They are not saying of *how* to achieve them**.

This problem is taken by an **adapter**. These are implementation of the ports, for example here is the implementation of ReserveBook port, inside the BorrowingFacade.java class, which is a business core of the application:

![](https://cdn-images-1.medium.com/max/2000/1*OYOq1Hvxclb6dbasVaDyBA.png)

You can easily read what’s happening here, what is the business process workflow.

But above method requires to have adapters for two outgoing ports — *database* & *eventPublisher*. For a first one and its first method (for getting *AvailableBook*) implementation could look as follow:

![](https://cdn-images-1.medium.com/max/2000/1*3p7oGvG0zlek8jJjDCspFA.png)

Of course this might be not the only solution. Maybe, depending on the case, it would be easier to implement it with *Hibernate*.

And that’s a beauty and elegance of the solution. We can define multiple adapters for a single port, because the business logic should not care how you get/save data from/to database, if you’re using *Jdbc*, *Hibernate* or other. Also the business should also not be concerned what type of a database you’re using. Whether t it’s PostgreSQL, MySQL, Oracle, MongoDB or any other type of a database.

And what’s more you can implement your own adapters only for testing. It might be very useful to have a very fast and easy database implementation just for unit testing of a business *core.*

![](https://cdn-images-1.medium.com/max/2000/1*TFe4zYxFZqk3Z8tQfHJ8PQ.png)

So at the end we can have multiple adapters for a single port, which we can switch whenever we want.

![](https://cdn-images-1.medium.com/max/2000/1*5G8MkEEjRDSQhl04DM6NoA.png)
> Ok John, take it easy! Slow down, I need to think about it. But thank you for introduction — I said and until the end of a day I was checking the code and reading about this patter over the Internet.

### Day 3. Implementing business core

Today, I’ve got my first, real assignment! Yay!

John said that our team analyst, Irene will contact me, and together we will work on a business core functionality of a new feature — canceling overdue reservation.

When she comes we have moved straight away to implement the problem. First we defined a new interface class which will be responsible for checking for overdue reservation and making them back available.

<iframe src="https://medium.com/media/8fd1683266646561847fc89373ac1b8f" frameborder=0></iframe>

Nothing complicated. Then we have added this port to the BorrowingFacade.java class (which is an adapter for above port):

<iframe src="https://medium.com/media/f30a84e34a1ffa89e6a466d8520a0373" frameborder=0></iframe>

Then we started to discuss what we should do here. Irene told me that we need to find all books that are kept as reserved for more than 3 days and then make them automatically available. And we’ve ended up with this code.

<iframe src="https://medium.com/media/21a3bc8eb0e0d8fec39fde881c205b7d" frameborder=0></iframe>

It’s really simple and it’s using the two methods from the database. One of them, to make book available, is already declared an implemented. The second one — database.findReservationsForMoreThan was not declared yet, therefore I’ve added it to the database outgoing port.

<iframe src="https://medium.com/media/70bf3777382426bab21b7594aac0170a" frameborder=0></iframe>

For now we didn’t care about how it will be implemented (in other words what SQL query we need to use get these).

And right away we moved on to prepare some unit tests. We have prepared two simple tests, one for overdue reservation, and second when a reservation has not reached due date:

<iframe src="https://medium.com/media/5cc35049b66d66bf6096c0151fde23ba" frameborder=0></iframe>

In above class we were forced to use Java reflection because a filed reservedDate is a private field which can not be changed after creating the ReservedBook object.

To make above code work, we also needed to create an InMemoryBorrowingDatabase class which has implementation of two outgoing, database ports which are required for business logic.

<iframe src="https://medium.com/media/8c7bf6148c6f05b2ae57f382c8435015" frameborder=0></iframe>

From code above we can see that the “database” implementation for unit tests is a just a simple map, which makes them execute really really fast. Something which is worth fighting for 😉.

After that my session with Irene has came to the end, as she needed to move to another meeting, but the most important job was already done. We’ve created a core business logic, so tomorrow I can focus on writing database adapter to connect to real database.

### Day 4. Database adapter and dependency injection

I’ve started a new day with reminding myself what I need to do. Therefore I’ve went to the database port definition once again and checks that a findReservationsForMoreThan method is still not implemented.

<iframe src="https://medium.com/media/70bf3777382426bab21b7594aac0170a" frameborder=0></iframe>

Therefore I’ve opened a class named BorrowingDatabaseAdapter and added implementation for a new method. All methods there were using Spring’s JdbcTemplate and I figure out that in my case it will also be the most suitable. After struggling for couple of minutes with an SQL query I’ve come across with a solution:

<iframe src="https://medium.com/media/bc3986e4d7c4ee4088a75d3579ad8ad5" frameborder=0></iframe>

And then I’ve prepared an integration test for it (as in it I want to touch an H2 database) in which I’ve used some test helpers and SQL scripts to set up the state of a database before running actual test.

<iframe src="https://medium.com/media/b63da2417b6f195b5050e2e4622d546c" frameborder=0></iframe>

Ohhh right! Everything went green! Nice 😏.

The last thing that I need to do is to write the code for **application** part, which will be triggering the whole process.

I decided to use the Spring Scheduler, which in every 1 minute will check for overdue books:

<iframe src="https://medium.com/media/a20ce055c54f2737a57e5d9a73e4c1ca" frameborder=0></iframe>

The OverdueReservationScheduler class is very simple. In every minute it runs the method cancelOverdueReservations on the incoming port CancelOverdueReservations which is an API of the *business core*.

But there is here one more thing to do. CancelOverdueReservations object is just an interface, it’s not an implementation. Therefore we need to inject it thru the dependency injection in a configuration class.

<iframe src="https://medium.com/media/af2c6cf0fd774b86a49b017b300101f3" frameborder=0></iframe>

With that we tell Spring context, that implementation of that interface should be taken from the BorrowingFacade class. Which in turn, requires to have an implementation of BorrowingDatabase interface, which is done in the BorrowingDatabaseAdapter class.

And that’s it! After deploying my changes on test environment and making some manual test it seems that might changes worked! What a week!

## Conclusion

I hope you enjoy this “story”. I would like to point couple of things that sells Ports & Adapters (at least for me):

* at least part of a code (*business core*) can be understandable by non-programmers (business analysts, product owners, your parents, etc.),

* the *core* code is decoupled from the *infrastructure* which makes very easy to replace the adapters without changing the business core code (I found this very useful especially in microservice world, when your app depends on several other APIs which are constantly changing their versions),

* the core is agnostic of an application framework, the old one can be replaced to Spring Boot, Jakarta EE, Quarkus, Micronaut or whatever other framework is popular at the moment,

* writing unit tests for the core is very simple and fast, we don’t need to create framework-specific test set up (e.g. in Spring, we don’t need to add @SpringBootTest annotation and build the entire Spring context just to test small part of an application), simple Java will be enough.

As usual a full code is available on GitHub.
[**wkrzywiec/library-hexagonal**
*written in Hexagonal (Ports & Adapters) Architecture This is a small application that provides basic REST endpoints for…*github.com](https://github.com/wkrzywiec/library-hexagonal)

## References
[**DDD, Hexagonal, Onion, Clean, CQRS, ... How I put it all together**
*In my last posts I've been writing about many of the concepts and principles that I've learned and a bit about how I…*herbertograca.com](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/)
[**Ports and Adapters in a monolith - DEVelopments**
*Some time ago I wrote about Ports and Adapters architecture, where domain logic is completely separated from…*lmonkiewicz.com](https://lmonkiewicz.com/posts/ports-and-adapters-in-a-monolith/)
[**Hexagonal Architecture with Java and Spring**
*The term "Hexagonal Architecture" has been around for a long time. Long enough that the primary source on this topic…*reflectoring.io](https://reflectoring.io/spring-hexagonal/)
[**Domain-Driven Design and the Hexagonal Architecture**
*Learn how to use the hexagonal architecture to turn your domain model into a complete application*vaadin.com](https://vaadin.com/learn/tutorials/ddd/ddd_and_hexagonal)
[**Hexagonal Architecture, DDD, and Spring | Baeldung**
*In this tutorial, we'll implement a Spring application using DDD. Additionally, we'll organize layers with the help of…*www.baeldung.com](https://www.baeldung.com/hexagonal-architecture-ddd-spring)
[**Title**
*Edit description*jakubn.gitlab.io](https://jakubn.gitlab.io/keepitclean/#1)
[**ddd-by-examples/library**
*This is a project of a library, driven by real business requirements. We use techniques strongly connected with Domain…*github.com](https://github.com/ddd-by-examples/library)
[**alien11689/ports-and-adapters-example**
*Contribute to alien11689/ports-and-adapters-example development by creating an account on GitHub.*github.com](https://github.com/alien11689/ports-and-adapters-example)
[**hirannor/spring-boot-hexagonal-architecture**
*Spring-Boot application based on hexagonal architecture - POC - hirannor/spring-boot-hexagonal-architecture*github.com](https://github.com/hirannor/spring-boot-hexagonal-architecture)
[**gshaw-pivotal/spring-hexagonal-example**
*A spring-boot based example of hexagonal design (also known as the ports and adapters design). Through the use of…*github.com](https://github.com/gshaw-pivotal/spring-hexagonal-example)
