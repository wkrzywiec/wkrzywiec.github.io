---
title: "Why Spring framework is so cool"
date: 2018-07-01
summary: "Sell points of Spring framework"
description: "For several years Spring is the most widely used software ecosystem for Java Enterprise Edition developers, it covers almost every aspect and makes it more simple and quicker to do than in a ‘standard’ way. It works as an overlord, or a platform that manage the lifecycle of all objects that are in its ecosystem in a very lightweight way, so developers can focus on more important things, like business logic."
tags: ["java", "spring", "library-project"]
canonicalUrl: "https://wkrzywiec.medium.com/why-spring-framework-is-so-cool-8472ceabaab1"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/why-spring-framework-is-so-cool-8472ceabaab1).
{{< /alert >}}

![Photo by [Rodion Kutsaev](https://unsplash.com/@frostroomhead?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/11090/0*AXu0iDLORhLJ0TCc)*Photo by [Rodion Kutsaev](https://unsplash.com/@frostroomhead?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*For several years Spring is the most widely used software ecosystem for Java Enterprise Edition developers, it covers almost every aspect and makes it more simple and quicker to do than in a ‘standard’ way. It works as an overlord, or a platform that manage the lifecycle of all objects that are in its ecosystem in a very lightweight way, so developers can focus on more important things, like business logic.*

## Why Spring?

All right, enough of revealing nothing words and let me explain in a simple words what Spring framework is for me.
> To fully understands what Spring is I first need to explain what problem it resolves.

As I’ve already mentioned Spring is widely used for building enterprise software that are for:

* [Customer Relationship Management (CRM)](https://en.wikipedia.org/wiki/Customer_relationship_management)

* [Enterprise Resource Management (ERP)](https://en.wikipedia.org/wiki/Enterprise_resource_planning)

* [Master Data Management (MDM)](https://en.wikipedia.org/wiki/Master_data_management)

* [and many more…](https://en.wikipedia.org/wiki/Enterprise_software)

In the early 00s most of them were created using **Java Platform, Enterprise Edition (J2EE)** that had many drawbacks i.a. applications were really heavy even though they’re business logic was really small. Also time spent on them was not proportionate to the outcome, because many of configurations had to made by the developer. So to sum up:
> The main goal of Spring framework is to simplify the development of enterprise software so it can be done quicker, because most of boilerplate configuration code are handled by the framework.

To achieve it Spring relays on these following concepts:

* Plain Old Java Objects (POJOs)

* Dependency Injection/Inversion of Control (IoC)

* Convention over configuration

* Modular Architecture

## Plain Old Java Objects (POJOs)

POJOs are simple Java Objects that do not contains any dependencies in it. They don’t implement any interface or extend any class as it is required by many frameworks.

The benefits of such approach is that a solution to a problem is not directly tied to the framework or it is not directly tied to other solutions, so if I change some part of the application other part won’t be affected. It modularize the whole application, so the objects can act as a black boxes, they connects with themselves using inputs and outputs, but each of them don’t know how other components (objects) are working. And Spring is taking care of connecting these objects together.

**Inversion of Control (IoC)/Dependency Injection**
> But how Spring is taking care of these loosely coupled objects?

It is using the concept of Inversion of Control. The idea is to pass the control of the program lifecycle and process flow from developer to the framework. Spring is taking care of them and if you want to use them, you need to call Spring that will do it for you. To achieve it we need to create some code and then register it into the framework and from that point Spring is creating, using and destroying objects that are within it.

To make sure that certain classes are registered within Spring context it uses specific configuration templates. And there are several ways to do that: with annotations, extending certain framework classes or by using external configuration files (like XML).

Implementation of IoC in Spring is Dependency Injection. With this pattern we don’t need to hard coded creation of the object, framework is doing it for us. For example, when controller class is making use of service class it requires it requires the latter to be created at the first place. But what happens if service class requires another class? For example DAO class? Or maybe it requires several other classes? If it is a small application this dependencies management is doable, but on a large, company scale it is really hard to achieve the most efficient solution.

To illustrate it here is sample code of ‘regular’ approach.

```java
public class UserService {
  
  private UserDAO  userDAO = new UserDAO(); 
  
  public User getUser(String username) {
    return userDAO.getUserByUsername(username); 
  }
}
```

In Spring, instead of creating objects with *new Object(…)* syntax, we can add *@Autowired* annotation to the private field so the framework will inject if for us. And by injecting I mean that it will create it on our behalf or use the already existing one.

```java
@Component
public class UserService {
  
  @Autowired
  private UserDAO userDAO;
  
  public User getUser(String username) {
   return userDAO.getUserByUsername(username); 
  }
}
```

You may notice that above class is annotated with another, special annotation — *@Component*. This one is used to tell Spring that this class needs to be added to the context.
> This approach makes our classes loosely coupled, which makes it more flexible and not implementation-relevant. And that might be very useful when in some time we’ll want to change the code environment, so code re-write won’t be necessary.

Finally it enables easy unit testing, chiefly because we don’t need to worry about dependencies that are included within the class. To illustrate this, imagine that a service class has a DAO class for connecting to a database. With the regular approach (via *new* operator) we hardcoded DAO class into a service, so to test it we need first to create DAO class, which might end up with complicated preparing phase for testing. And that is not welcomed in unit testing.

## Convention over configuration
> So how to achieve this dependency injection thing? Probably there are a lot of configuration prep work that is pretty exhausting.

Here is the best thing of Spring framework. Most of configuration job will be provided by default and if we want to customize it is really easy to do just by modifying one particular thing and not the container configuration.

There are several convenient approaches to achieve it. The most popular ones are based on XML file and Java class code. There is also another way to achieve it — auto scanning for components using Java annotations.

**XML configuration**

First one is considered as an old-fashioned. It was introduced in first releases of Spring, so you can find it in the old projects, but it is still used. The idea is to have single or multiple XML files that contains a list of Beans (i.e. Java objects) that can be registered into Spring container. Next, during project deployment, these files must be uploaded to the Spring context.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.springframework.org/schema/beans
    	http://www.springframework.org/schema/beans/spring-beans.xsd">

	<bean id="john" class="com.wkrzywiec.library.model.User">
		<property name="firstName" value="John" />
		<property name="lastName" value="Snow" />
		<property name="email" value="john.snow@winterfell.com" />
  		<property name="address">
      			<ref local="johnAddress"/>
   		 </property>
	</bean>

  	<bean id="johnAddress" class="com.wkrzywiec.library.model.Address">
    		<propery name="city" value="Winterfell" />
    		<property name="building" value="Castle" />
  	</bean>

</beans>
```

Above there is a simple user Java class and config XML file snippet. Let’s focus on config file. All beans must be declared within <beans> tag with a <bean> tag and within it there are several attributes:

* **id** — indicates the unique name of the bean, under which it will be registered in Spring container,

* **class** — defines what class is the object,

* `<property>` — User class contains some fields that can populated with values using *name* (what field) and *value* (what value) attributes,

* **ref** - this one is used to include one bean in another, so in other words to set up dependency between them

* **scope** - defines beans’ lifecycle scope, e.g. singleton (single object for entire Spring container), request (life cycle of HTTP request), session (lifecycyle of HTTP Sesssion) and other.

Finally to add it to the application context and retrieve bean with specific id use following code:

```java
public class ApplicationStart {
  
    public static void main( String[] args ){
      
        ApplicationContext ctx = new ClassPathXmlApplicationContext("configuration.xml");
        User user = (User) ctx.getBean("john");
        System.out.println(user.toString());
    }
}
```

**Java Class**

Another way to register beans into the Spring container is Java-based approach, which in many cases is more convenient way (as it is more readable).

```java
@Configuration
public class AppConfig {
	
    @Bean(name="john")
    @DependsOn("johnAddress")
    public User user() {
        User user = new User();
        user.setFirstName("John");
        user.setLastName("Snow");
        user.setEmail("john.snow@winterfell.com");
    
        user.setAddress(address());
        return user;
    }
	
	@Bean(name="johnAddress")
	public Address address(){
		
		Address address = new Address();
      		address.setCity("Winterfell");
      		address.setBuilding("Castel");
		return address;
	}
}
```

Above Java class has special annotation — @Configuration — that tells Spring that it is a config file. Another one, @DependsOn is telling that the User bean will be created after the Address, not before.

And finally to add beans defined in Java config class add use following code:

```java
public class ApplicationStart {
  
	public static void main(String[] args)  {
    
		AnnotationConfigApplicationContext ctx = new AnnotationConfigApplicationContext();
 		ctx.register(AppConfig.class);
		ctx.refresh();
    
		User user = (User) ctx.getBean("john");
   		System.out.println(user.toString());		
	}
}  
```

**Component scanning**

Main drawback of previous examples is that first we need to create specific Java class and then register it in Spring container in config file. Maybe it is not so much work, but still it is not really convenient.

That’s why there is another way to achieve it. Either in XML file or in Java config class we can declare that Spring will scan for Java classes with special annotations. So from this point we only add annotation above class name and the framework will do all the work for us.

To enable auto scanning add following code to config files:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<beans xmlns="http://www.springframework.org/schema/beans"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.springframework.org/schema/beans
    http://www.springframework.org/schema/beans/spring-beans.xsd">
	
	<context:component-scan base-package="com.wkrzywiec.library" />

</beans>
```

```java
@Configuration
@ComponentScan(basePackages="com.wkrzywiec.library")
public class Config {
 
  //other configurations
}
```

Using one of these set ups Spring will recursively find all annotated class within the package and its sub packages.

To add object to the Spring container just add one of the following annotation above its name:

* **@Component** — it is a standard annotation and can be added to any type of Java class, next ones are more specialized, but in most cases they can be replaced by this one,

* **@Repository** — it is used for Data Access Objects (DAO) that are responsible for retrieving information from the database,

* **@Service** — this one is used for service layer classes, they working as a middleman between UI and DAO and responsible for processing data and whole business logic,

* **@Controller** — classes with these annotations are taking care of user requests in UI.

Except for registering beans config files covers other tasks, like database connection configuration, adding external resources, enabling web MVC framework etc.

## Modular Architecture
> Ok, I know how I can use Spring, but how it works? What is the architecture and what else I can do?

The whole idea of Spring is to modularize whole framework into smaller pieces that are responsible for other aspect of the applications. There are about 20 modules that are grouped by role they play. The most important are presented on the following diagram.

![](https://cdn-images-1.medium.com/max/2000/1*XVe1noRCMtr-Z-Hwrsh0DA.png)

**Core Container.** You probably noticed that I used this expression in previous section. It is the most important part of the framework, because it provides IoC feature and it can read configuration. It is like a factory for creating beans and managing them.

**Data Access/Integration.** As you might think these modules are responsible for transaction management and communicating with SQL and NoSQL data sources. It allows to connect to them using standard JDBC approach or ORM way with Hibernate.

**Web.** It is also very intuitive. It covers all the aspects related to web applications, like connection, handling HTTP requests, creating REST web service and so on. Container includes also the Spring MVC framework, which I used in my Library Portal project.

**Test.** Spring supports Test Driven Development by providing mock-up objects for unit testing and also many features that allows to make integration tests.

**Aspect Oriented Programming (AOP)**. In short, it is taking care of some common task that are shared within multiple objects, like logging, transaction management, security, etc.
> So everything is clear now? I guess not.

At the beginning all of these might be a little bit overwhelming and not so concrete as it could be. Chiefly because Spring is very big and diverse platform, so it is really hard to describe it in a few words. The way I like to look on it is that for me it is a programming platform that allows me to build some components that will be glued together with this framework. And the good thing is that such glue is applicable into many solutions. More or less it is like OS for your business logic, you only add part of the software, but all other tasks (like booting the system in OS) is handled by Spring.

I might sound a little bit obvious, but the best way to learn it is to play around it and try as many features that it can offer. Don’t try (like me) to understand all at once, read and try piece by piece to fully understand the whole concept. There are several guides on official website how to resolve the most common problems, which you can use (link in the References).

Finally I’m aware that I skipped some important topics, like annotations types, bean scope, Spring application context , but I wanted to have this entry really condensed. I’ll try to extend some of them in next blog posts.

## Writing code
> In this section I want to show how to create vanilla Spring project that is Java based config

It is not related to my project, Library Portal, because it is a Spring MVC project. As a web application it requires some additional introduction, which I would like to omit here, but I’ll cover it in next blog post.

### Step 1. Create Gradle project

All of my projects are Gradle-based, because it makes really easy to manage all external libraries that are included into the project. Basic information about integrating Gradle with Eclipse IDE can be found [here](http://www.vogella.com/tutorials/EclipseGradle/article.html).

In Eclipse select **File -> New -> Other…** and in a new window type *“Gradle”*. Then proceed with instructions that appears on the screen, so new project will be created.

### Step 2. Add dependecies to build.gradle

Next, open build.gradle file and in section dependencies provide following code:

```gradle
compile 'org.springframework:spring-core:5.0.7.RELEASE'
compile 'org.springframework:spring-context:5.0.7.RELEASE'
```

Then right-click on project name in **Project Explorer** and select **Gradle -> Refresh Gradle Project.** So now you’ve all external libraries downloaded into your project.

### Step 3. Create Java config file

I would like to make a use of Java Bean auto scan feature, so my Java config class is really simple:

```java
package com.wkrzywiec.simplespring;

import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;

@Configuration
@ComponentScan(basePackages="com.wkrzywiec.simplespring")
public class ConfigApp {

}
```

@ComponentScan annotation tells Spring context that it must search for beans within certain project package.

### Step 4. Create simple Bean

In this example I create simple Person class that has one method — *sayHello()* that prints her/his introduction in the console.

```java
package com.wkrzywiec.simplespring;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

@Component("john")
public class Person {

	@Value("John")
	private String name;
	
	public String sayHello() {
		
		return "Hi, my name is: " + name;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	@Override
	public String toString() {
		return "Person [name=" + name + "]";
	}
}
```

So let me explain a little bit of above code. First class was annotated with @Component with a name *“john”*, under which it is register in Spring context. Next field name was annotated with @Value(“John”), because I wanted to inject specific value into this field. If I didn’t do that this field would remain empty (null).

Other part is a single method *sayHello()* and standard getters and setters.

### Step 5. Testing

Finally we need to test if everything works ok, so I’ve created following simple class:

```java
package com.wkrzywiec.simplespring;

import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class MainApp {

	public static void main(String[] args) {
		
		AnnotationConfigApplicationContext context = new AnnotationConfigApplicationContext();
		context.register(ConfigApp.class);
		context.refresh();
		
		Person john = (Person) context.getBean("john");
		System.out.println("\n" + john.sayHello() + "\n");
		
		context.close();
	}
}
```

The output is:

    lip 01, 2018 11:59:45 AM org.springframework.context.support.AbstractApplicationContext prepareRefresh

    INFO: Refreshing org.springframework.context.annotation.AnnotationConfigApplicationContext@108c4c35: startup date [Sun Jul 01 11:59:45 CEST 2018]; root of context hierarchy

    Hi, my name is: John

    lip 01, 2018 11:59:45 AM org.springframework.context.support.AbstractApplicationContext doClose

    INFO: Closing org.springframework.context.annotation.AnnotationConfigApplicationContext@108c4c35: startup date [Sun Jul 01 11:59:45 CEST 2018]; root of context hierarchy

First and last two lines are Spring related, but the line in a middle is our own, that was called by the bean.

And that’s it. Whole code of above example can be found here:

[**wkrzywiec/simple-spring** | github.com](https://github.com/wkrzywiec/simple-spring)

This post is part of my Library Portal project, which can be found here:

[**wkrzywiec/Library-Spring** | github.com](https://github.com/wkrzywiec/Library-Spring)

## References

* [**Spring Framework Documentation** | docs.spring.io](https://docs.spring.io/spring/docs/current/spring-framework-reference/index.html)
* [**Spring Guides** | spring.io](https://spring.io/guides)
* [**Java, Spring and Web Development tutorials** | baeldung.com](http://www.baeldung.com/)
* [**What Is Spring Framework | Spring Framework Architecture | Edureka** | edureka.co](https://www.edureka.co/blog/what-is-spring-framework/)
* [**Spring: A Head Start 🔥— Introduction (Part 1)** | medium.com](https://medium.com/omarelgabrys-blog/spring-a-head-start-introduction-part-1-130aa1b41e47)
* [**Spring & Hibernate for Beginners | Udemy** | udemy.com](https://www.udemy.com/spring-hibernate-tutorial/)
* [**TechnionYP5777/SmartCity-Market** | github.com](https://github.com/TechnionYP5777/SmartCity-Market/wiki/Dependency-Injection-and-Unit-Testing-With-Mockito)
* [**Spring @Component Annotation Example** | javarticles.com](http://www.javarticles.com/2016/01/spring-component-annotation-example.html)
