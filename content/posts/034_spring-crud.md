# How to create RESTful CRUD application with Spring Boot even faster
> Source: https://wkrzywiec.medium.com/how-to-create-restful-crud-application-with-spring-boot-even-faster-389e5ff00c88

Today I want to share with you one of my side projects in which I’ve used a new approach to generate couple basic REST endpoints with only few lines of code.

![Photo by [Andreea Popa](https://unsplash.com/@elfcodobelf?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/12000/0*mYnq0dyo7sLOuDpB)*Photo by [Andreea Popa](https://unsplash.com/@elfcodobelf?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*
> First what is my side project?

It’s very simple, it’s called a [***NoticeBoard](https://github.com/wkrzywiec/NoticeBoard)*** and as the name can tell you it’s software representation of notice board (*if you don’t know what’s that *— it was used in dark, 20th century, ages where you could find announcements, ads or job advertisements).

The data model consists of 3 entities — *Board*, *Notice* & *Author*. And the relationship between them is as follows.

![](https://cdn-images-1.medium.com/max/2000/1*T16ztOi7uWy6ii94Y_-x4g.png)

For each of the data entities I wanted to have basic CRUD endpoints, e.g. for *Notice *there would be:

* GET {baseURL}/notices/ - lists all *Notices* (as Json array),

* GET {baseURL}/notices/{id} - gets single *Notice* (as Json) by its {id},

* POST {baseURL}/notices/ - creates a new *Notice* which is passed (as Json) in the BODY of the request,

* PUT {baseURL}/notices/{id} - updates an existing *Notice* (with an {id}) with Notice passed in the BODY of the request,

* DELETE {baseURL}/notices/{id}- deletes an existing *Notice* by its {id}.

Similar list would be for two remaining entities. And now my problem.
> How to achieve it? How to generate those endpoints without typing boilerplate code?

Here is how I’ve tackled it.

If you’re familiar with Spring you probably know about the [***CrudRepository<T,ID>](https://docs.spring.io/spring-data/commons/docs/current/api/org/springframework/data/repository/CrudRepository.html) ***interface which provides several methods that allows interaction with the database out of the box.

For instance, the method **findAll() **returns list of all instances of given entity (indicated with generic type T), **save()** saves new or updates existing one and so on.

But there is no such thing for REST Controllers. Therefore I’ve decided to create it on my own!

Therefore I’ve created an abstract ***CrudController<T extends BaseDTO>***:

<iframe src="https://medium.com/media/a674cf1153302151366bdf40c442aafb" frameborder=0></iframe>

As I mentioned before, it provides 5 basic endpoints for reading and manipulating entities.

In order to make a concrete class from it you need to have two things:

* a ***DTO (Data Transfer Object)*** class that extends from BaseDTO class,

* and Service class that implements interface*** CrudService<T>***.

BaseDTO is an abstract DTO class that has two fields ( id and creationDate ) that I wanted to include in each child class:

<iframe src="https://medium.com/media/42475386d2b2c0268c8daec78b4dba27" frameborder=0></iframe>

Moreover the child of the *CrudController *requires to pass in the constructor a Service class that implements the interface of *CrudService<T>*. It’s a class that is an intermediate layer between *CrudController* and *CrudRepository.*

And the definition of such interface looks as follows:

<iframe src="https://medium.com/media/ef8f0866e41ce0b594ec78144fc31ec6" frameborder=0></iframe>

The reason I didn’t want to create an abstract class as it was for *CrudController*, is because the Service class is usually responsible for holding business logic and mapping of DTOs to database Entities. And such will be different for each project, so I thought that it doesn’t make sens to create a default implementation for it.

This is a scaffolding, building blocks, of my application and now we can move on to implementing all the application layers for **Notice** entity.

Therefore here is the code of **NoticeController**:

<iframe src="https://medium.com/media/11c9faa51a5f1fbd2c34efd26d1b0974" frameborder=0></iframe>

*Pretty slim, isn’t it?* Now, let’s move on a little bit deeper, to the **NoticeService** layer:

<iframe src="https://medium.com/media/ec64e212b213694c50867715956c6fcb" frameborder=0></iframe>

Yep, here are more lines of code than before. And like I mentioned before it’s because I didn’t wanted to create some default implementation for a Service. If you suggest to create one, please share it with me in the comments 😉.

In my case the implementation of *NoticeService* methods are covering only mapping the DTO class to the Entity (NoticeDTO -> Notice ), which are pretty the same (usually it’s not that good practice to have 1–1 mapping of all fields between DTO and Entity, but this a small project, which is not running anywhere).

And finally the **NoticeRepository** class:

<iframe src="https://medium.com/media/9f7abd7371795004c8bcd1fa47b559ab" frameborder=0></iframe>

There is nothing new here, it’s a standard *Repository* class that extends Spring’s *CrudRepository* abstract class.

As a result, when you run the application and open Swagger UI page ([http://localhost:8080/swagger-ui.html](http://localhost:8080/swagger-ui.html)) in a browser there will be a list of available endpoints for a Notice.

![](https://cdn-images-1.medium.com/max/2000/1*5mCPlKOIpDSHFFSQHezgSA.png)

### Conclusion

Generating basic REST endpoints may accelerate your development tremendously. It makes development easier and faster so you can focus on more important parts of the application.

But keep in mind that this approach might not be good for some cases. Yes, generating endpoints is cool, but creates also the risk that some endpoints might not have business purpose and could be potientially security vulnerability, e.g. some could use DELETE endpoint to clean the database.

As always here is the link to my GitHub repository:
[**wkrzywiec/NoticeBoard**
*This is a simple RESTful CRUD (Create Read Update Delete) application for managing Boards, Notices and Authors saved in…*github.com](https://github.com/wkrzywiec/NoticeBoard)

## References
[**Spring Projects**
*Spring Data is an umbrella project consisting of independent projects with, in principle, different release cadences…*spring.io](https://spring.io/projects/spring-data#overview)
[**Spring Data Repositories compared | Baeldung**
*In this quick article, we'll focus on different kinds of Spring Data repository interfaces and their functionality…*www.baeldung.com](https://www.baeldung.com/spring-data-repositories)
