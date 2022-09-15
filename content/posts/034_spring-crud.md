---
title: "How to create RESTful CRUD application with Spring Boot even faster"
date: 2020-02-10
summary: "Build, test and publish Java application"
description: "Today I want to share with you one of my side projects in which I’ve used a new approach to generate couple basic REST endpoints with only few lines of code."
tags: ["java", "spring-boot", "crud"]
canonicalUrl: "https://wkrzywiec.medium.com/how-to-create-restful-crud-application-with-spring-boot-even-faster-389e5ff00c88"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/how-to-create-restful-crud-application-with-spring-boot-even-faster-389e5ff00c88).
{{< /alert >}}

![Photo by [Andreea Popa](https://unsplash.com/@elfcodobelf?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/12000/0*mYnq0dyo7sLOuDpB)*Photo by [Andreea Popa](https://unsplash.com/@elfcodobelf?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*Today I want to share with you one of my side projects in which I’ve used a new approach to generate couple basic REST endpoints with only few lines of code.*

## Notice Board

> First what is my side project?

It’s very simple, it’s called a [NoticeBoard](https://github.com/wkrzywiec/NoticeBoard)and as the name can tell you it’s software representation of notice board (*if you don’t know what’s that* — it was used in dark, 20th century, ages where you could find announcements, ads or job advertisements).

The data model consists of 3 entities — *Board*, *Notice* & *Author*. And the relationship between them is as follows.

![](https://cdn-images-1.medium.com/max/2000/1*T16ztOi7uWy6ii94Y_-x4g.png)

For each of the data entities I wanted to have basic CRUD endpoints, e.g. for *Notice* there would be:

* GET {baseURL}/notices/ - lists all *Notices* (as Json array),

* GET {baseURL}/notices/{id} - gets single *Notice* (as Json) by its {id},

* POST {baseURL}/notices/ - creates a new *Notice* which is passed (as Json) in the BODY of the request,

* PUT {baseURL}/notices/{id} - updates an existing *Notice* (with an {id}) with Notice passed in the BODY of the request,

* DELETE {baseURL}/notices/{id}- deletes an existing *Notice* by its {id}.

## Implementation

Similar list would be for two remaining entities. And now my problem.
> How to achieve it? How to generate those endpoints without typing boilerplate code?

Here is how I’ve tackled it.

If you’re familiar with Spring you probably know about the [CrudRepository<T,ID>](https://docs.spring.io/spring-data/commons/docs/current/api/org/springframework/data/repository/CrudRepository.html) interface which provides several methods that allows interaction with the database out of the box.

For instance, the method `findAll()` returns list of all instances of given entity (indicated with generic type T), `save()` saves new or updates existing one and so on.

But there is no such thing for REST Controllers. Therefore I’ve decided to create it on my own!

Therefore I’ve created an abstract `CrudController<T extends BaseDTO>`:

```java
package com.wkrzywiec.medium.noticeboard.controller;

import com.wkrzywiec.medium.noticeboard.controller.dto.BaseDTO;
import com.wkrzywiec.medium.noticeboard.service.CrudService;
import io.swagger.annotations.ApiOperation;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

public abstract class CrudController<T extends BaseDTO> {

    private CrudService<T> service;

    public CrudController(CrudService<T> crudService){
        this.service = crudService;
    }

    @GetMapping("/")
    @ApiOperation(value = "List all")
    public ResponseEntity<List<T>> getAll(){
        return new ResponseEntity<>(service.findAll(), HttpStatus.OK);
    }

    @GetMapping("/{id}")
    @ApiOperation(value = "Get by Id")
    public ResponseEntity<T> getById(@PathVariable Long id){
        Optional<T> optionalT = service.findById(id);
        return optionalT.map(T ->
                new ResponseEntity<>(T, HttpStatus.OK))
                .orElse(new ResponseEntity<>(null, HttpStatus.NOT_FOUND));
    }

    @PostMapping("/")
    @ApiOperation(value = "Create a new one")
    public ResponseEntity<T> save(@RequestBody T body){
        return new ResponseEntity<>(service.save(body), HttpStatus.CREATED);
    }

    @DeleteMapping("/{id}")
    @ApiOperation(value = "Delete by Id")
    public ResponseEntity<String> delete(@PathVariable Long id){
        Optional<T> optional = service.findById(id);
        return optional.map(T ->
                new ResponseEntity<>("Object with the id " + id + " was deleted.", HttpStatus.NO_CONTENT))
                .orElse(new ResponseEntity<>(HttpStatus.NOT_FOUND.getReasonPhrase(), HttpStatus.NOT_FOUND));
    }

    @PutMapping("/{id}")
    @ApiOperation(value = "Update by Id")
    public ResponseEntity<String> update(@PathVariable Long id, @RequestBody T body){
        Optional<T> optional = service.findById(id);
        optional.ifPresent(n -> service.update(id, body));
        return optional.map(n ->
                new ResponseEntity<>("Object with id " + id + " was updated.", HttpStatus.OK))
                .orElse(new ResponseEntity<>(HttpStatus.NOT_FOUND.getReasonPhrase(), HttpStatus.NOT_FOUND));
    }
```

As I mentioned before, it provides 5 basic endpoints for reading and manipulating entities.

In order to make a concrete class from it you need to have two things:

* a ***DTO (Data Transfer Object)*** class that extends from BaseDTO class,

* and Service class that implements interface `CrudService<T>`.

BaseDTO is an abstract DTO class that has two fields ( id and creationDate ) that I wanted to include in each child class:

```java
import io.swagger.annotations.ApiModelProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.experimental.SuperBuilder;

import java.util.Date;

@SuperBuilder
@Data
@NoArgsConstructor
@AllArgsConstructor
public abstract class BaseDTO {

    @ApiModelProperty(value = "The id of the object")
    private Long id;

    @ApiModelProperty(value = "The date when the object was created")
    private Date creationDate;
}
```

Moreover the child of the *CrudController* requires to pass in the constructor a Service class that implements the interface of *CrudService<T>*. It’s a class that is an intermediate layer between *CrudController* and *CrudRepository.*

And the definition of such interface looks as follows:

```java
import com.wkrzywiec.medium.noticeboard.controller.dto.BaseDTO;

import java.util.List;
import java.util.Optional;

public interface CrudService<T extends BaseDTO> {

    List<T> findAll();

    Optional<T> findById(Long id);

    T save(T dto);

    void delete(Long id);

    T update(Long id, T dto);
}
```

The reason I didn’t want to create an abstract class as it was for *CrudController*, is because the Service class is usually responsible for holding business logic and mapping of DTOs to database Entities. And such will be different for each project, so I thought that it doesn’t make sens to create a default implementation for it.

This is a scaffolding, building blocks, of my application and now we can move on to implementing all the application layers for **Notice** entity.

Therefore here is the code of **NoticeController**:

```java
package com.wkrzywiec.medium.noticeboard.controller;

import com.wkrzywiec.medium.noticeboard.controller.dto.NoticeDTO;
import com.wkrzywiec.medium.noticeboard.service.NoticeService;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/notices")
public class NoticeController extends CrudController<NoticeDTO> {

    public NoticeController(NoticeService noticeService) {
        super(noticeService);
    }
}
```

*Pretty slim, isn’t it?* Now, let’s move on a little bit deeper, to the **NoticeService** layer:

```java

package com.wkrzywiec.medium.noticeboard.service;

import com.wkrzywiec.medium.noticeboard.controller.dto.NoticeDTO;
import com.wkrzywiec.medium.noticeboard.entity.Notice;
import com.wkrzywiec.medium.noticeboard.repository.NoticeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static com.wkrzywiec.medium.noticeboard.mapper.NoticeMapper.*;

@Service
@RequiredArgsConstructor
public class NoticeService implements CrudService<NoticeDTO> {

    private final NoticeRepository noticeRepository;

    @Override
    public List<NoticeDTO> findAll() {
        List<NoticeDTO> noticeDTOList = new ArrayList<>();
        noticeRepository.findAll().forEach(notice -> noticeDTOList.add(INSTANCE.noticeToDto(notice)));
        return noticeDTOList;
    }

    @Override
    public Optional<NoticeDTO> findById(Long id) {
        Optional<Notice> noticeOptional = noticeRepository.findById(id);
        return noticeOptional.map(INSTANCE::noticeToDto);
    }

    @Override
    @Transactional
    public NoticeDTO save(NoticeDTO noticeDTO) {
        Notice notice = INSTANCE.dtoToNotice(noticeDTO);
        return INSTANCE.noticeToDto(noticeRepository.save(notice));
    }

    @Override
    @Transactional
    public void delete(Long id){
        noticeRepository.deleteById(id);
    }

    @Override
    @Transactional
    public NoticeDTO update(Long id, NoticeDTO noticeDTO){
        Notice savedNotice = noticeRepository.findById(id).orElseThrow();
        Notice noticeToUpdate = INSTANCE.dtoToNotice(noticeDTO);

        savedNotice.setTitle(noticeToUpdate.getTitle());
        savedNotice.setDescription(noticeToUpdate.getDescription());

        return INSTANCE.noticeToDto(noticeRepository.save(savedNotice));
    }
}
```

Yep, here are more lines of code than before. And like I mentioned before it’s because I didn’t wanted to create some default implementation for a Service. If you suggest to create one, please share it with me in the comments 😉.

In my case the implementation of *NoticeService* methods are covering only mapping the DTO class to the Entity (NoticeDTO -> Notice ), which are pretty the same (usually it’s not that good practice to have 1–1 mapping of all fields between DTO and Entity, but this a small project, which is not running anywhere).

And finally the **NoticeRepository** class:

```java
package com.wkrzywiec.medium.noticeboard.repository;

import com.wkrzywiec.medium.noticeboard.entity.Notice;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface NoticeRepository extends CrudRepository<Notice, Long> {
}
```

There is nothing new here, it’s a standard *Repository* class that extends Spring’s *CrudRepository* abstract class.

As a result, when you run the application and open Swagger UI page ([http://localhost:8080/swagger-ui.html](http://localhost:8080/swagger-ui.html)) in a browser there will be a list of available endpoints for a Notice.

![](https://cdn-images-1.medium.com/max/2000/1*5mCPlKOIpDSHFFSQHezgSA.png)

## Conclusion

Generating basic REST endpoints may accelerate your development tremendously. It makes development easier and faster so you can focus on more important parts of the application.

But keep in mind that this approach might not be good for some cases. Yes, generating endpoints is cool, but creates also the risk that some endpoints might not have business purpose and could be potientially security vulnerability, e.g. some could use DELETE endpoint to clean the database.

As always here is the link to my GitHub repository:

[**wkrzywiec/NoticeBoard** | github.com](https://github.com/wkrzywiec/NoticeBoard)

## References

* [**Spring Projects** | spring.io](https://spring.io/projects/spring-data#overview)
* [**Spring Data Repositories compared | Baeldung** | baeldung.com](https://www.baeldung.com/spring-data-repositories)
