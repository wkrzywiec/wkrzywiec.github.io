---
title: "Library Portal — Spring Project Overview"
date: 2018-03-11
summary: "The first blog entry on my new Spring MVC project — Library Portal"
description: "This is my first blog entry on my new Spring MVC project — Library Portal — and also it is my first blog entry ever. I am a little bit nervous, but I hope you will gone like it."
tags: ["java", "spring", "project"]
canonicalUrl: "https://wkrzywiec.medium.com/library-portal-spring-project-overview-ddbf910dcb95"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/library-portal-spring-project-overview-ddbf910dcb95).
{{< /alert >}}

![](https://miro.medium.com/max/700/0*uwHYGnR-0oNsDWDv.) *Photo by [Gabriel Ghnassia](https://unsplash.com/@gabrielghnassia) on [Unsplash](unsplash.com)*


“A large library or study filled with lots of books, ornate ceilings, and two levels in Chantilly” by Gabriel Ghnassia on Unsplash

**Hi Everyone!**

This is my first blog entry on my new Spring MVC project — Library Portal — and also it is my first blog entry ever. I am a little bit nervous, but I hope you will gone like it.

Let me shortly introduce myself to you. My name is Wojtek and I leave in Warsaw (Poland). I would like to become a Java Software Developer in future and I hope this blog will help me achiving this. For now I am focused on this project, but in future I hope I will share with you my other ones. All of them can be found in my [GitHub repository](https://github.com/wkrzywiec).

The key objective of this post is to give you some insight of my first Spring MVC project with all steps and difficulties I have faced during it. Thanks to that approach I think I will be able to learn more and memorize all challenges that I have faced (I will be honest with you — I am not good with remembering most of the stuff ;) ). So this entry and those that will be after it are chiefly for me. In next ones I will be focusing on different aspects/features of this project. But of course if you will find something useful for you I will be more than happy to help you.

And also if you have any question/suggestion please do not hesitate to reach me.

## Project Description

From the project name you probably guess that I am trying to make somekind of Library Customer Relationship Management (CRM) platform that can be used in libraries to manage users and stored books. It will also track of all actions that were made in it, like borrowing books, creating new user, etc., to give more insight for library managers.

I have divided all portal users into three categories: Readers, Librarians and Admins. And depending on a user the portal will be giving a different experience.

### **Readers**

This is the most numerous group of users. After login to their profile they will be able to find and borrow some books from library. They will have a limit of 5 books lend at the same time. They can keep them only for one month, otherwise they will be charged 0.05$ per day. So the user will be able to track their book history and her/his penalties. Finally they can return books, if they kept them for less than a month. If they have some penalties book can be returned only by the librarian.

### Librarians

These users will be able to add new books to the library. Using one of the Books Open API (I have not decided which one I would like to use) they will be able to find it and mark as available. Also they will be able to check each book if it is lend or not and check when the book should be returned to the library (it will be the last day when the penalties will not be charged). Finally they will be able to mark that reader has settled the payments (if there was any).

### Admin

This kind of users will be able to manage users, like inactivating them, creating new librarians (regular users will be able to register manually) or updating their info. I am considering adding dashboards that presents some basic data (like user traffic, book statistics), but I will think about it later.

These are all my assumptions that I have come up so far. Probably some of them will change slightly during the working on it, but I hope they will stay as they are.

## Technology Stack

![Photo by [Fabian Grohs](https://unsplash.com/@grohsfabian?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/11150/0*j6vYG_yaSmz_DYMR.)*Photo by [Fabian Grohs](https://unsplash.com/@grohsfabian?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

Finally I get to this part! As a Java developer I will focus on creating backend in Java using [Spring MVC framework](https://spring.io/). The database will be created in MySQL. From a frontend perspective, I will be using JSP (JavaServer Page) to create HTML websites. To make it prettier I will take an advantage of [Bootrstrap](https://getbootstrap.com/) library and JavaScript.

The whole project will be build using [Gradle](https://gradle.org/) to manage dependencies and also quickly run in on Tomcat server.

As I mentioned before, from Spring framework I would like to use Spring MVC pattern, but also I will take an advantage of Spring Security (for managing user logging).

For connecting with MySQL database I will use [Hibernate ORM](http://hibernate.org/orm/).

Some actions that are made in the portal will be recorded, and for this purpose I will be using [Apache Log4j2](https://logging.apache.org/log4j/2.x/).

## Posts related to this project:

### General

* [Why Spring framework is so cool](https://medium.com/@wkrzywiec/why-spring-framework-is-so-cool-8472ceabaab1)

* [How to start with Spring MVC](https://medium.com/@wkrzywiec/how-to-start-with-spring-mvc-309dec3c59fd)

### **Configurations**

* [Project development history lesson with git.](https://medium.com/@wkrzywiec/project-development-history-lesson-with-git-424b9940ad84)

### **Clean code**

* [Project Lombok — how to make your model class simple](https://medium.com/@wkrzywiec/project-lombok-how-to-make-your-model-class-simple-ad71319c35d5)

### **Features**

**User Log Events**

* [Creating user logs with Apache Log4j2](https://medium.com/@wojciechkrzywiec/creating-user-logs-with-apache-log4j2-90bfeb8a0d3f)

* [Moving into next level in User Log Events with Spring AOP](https://medium.com/@wkrzywiec/moving-into-next-level-in-user-log-events-with-spring-aop-3b4435892f16)

**Full-text Search**

* [Full-text search with Hibernate Search (Lucene) — part 1](https://medium.com/@wkrzywiec/full-text-search-with-hibernate-search-lucene-part-1-e245b889aa8e)

**User registration**

* [How to check if user exist in database using Hibernate Validator](https://medium.com/@wkrzywiec/how-to-check-if-user-exist-in-database-using-hibernate-validator-eab110429a6)

**Add book to library**

* [Making use of open REST API with Retrofit](https://medium.com/@wkrzywiec/making-use-of-open-rest-api-with-retrofit-dac6094f0522)

### Deployment

* [Setting up Gradle web project in Eclispe (on Tomcar server)](https://medium.com/@wojciechkrzywiec/setting-up-gradle-spring-project-in-eclipse-on-tomcat-server-77d68454fd8d)

* [Deployment of Spring MVC app on a local Tomcat server for beginners](https://medium.com/@wkrzywiec/deployment-of-spring-mvc-app-on-a-local-tomcat-server-for-beginners-3dfff9161908)

* [How to deploy web app and database in one click with Flyway (on Tomcat server)](https://medium.com/@wkrzywiec/how-to-deploy-web-app-and-database-in-one-click-with-flyway-on-tomcat-server-26b580e09e38)

Code of the whole project can be found here:
[**wkrzywiec/Library-Spring**
*Library-Spring - The library website where you can borrow books.*github.com](https://github.com/wkrzywiec/Library-Spring)
