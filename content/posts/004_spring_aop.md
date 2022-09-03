
# Moving into next level in user log events with Spring AOP
> Source: https://wkrzywiec.medium.com/moving-into-next-level-in-user-log-events-with-spring-aop-3b4435892f16

In my previous post I described how I had implemented Apache Log4j2 framework into my code. Last time, all Loggers were added directly to the method that triggered logging action, which might be problematic if we want to log different events all over the places in the code, because when there will be new request for some modification it will require to find all of them and copy-paste some amendments in it. And that’s so called code smell, that most of software developers want to avoid. If they do so am I. Thanks to Spring Aspect-Oriented Programming (Spring AOP) module it won’t be the problem as all the logging part will be gathered in one place, so there will be no need to perform unnecessary searching and modification.

![Photo by [Chris Nguyen](https://unsplash.com/@cspek?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/5184/0*h9hreh8hwCactMwR.)*Photo by [Chris Nguyen](https://unsplash.com/@cspek?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

## **Table of content**

### Overview

* [Intro](https://medium.com/p/3b4435892f16#6604)

* [Pointcuts](https://medium.com/p/3b4435892f16#e9cf)

* [Advices](https://medium.com/p/3b4435892f16#3f0c)

### Code writting

* [Step 1. Adding Spring AOP dependency to build.gradle file](https://medium.com/p/3b4435892f16#9d06)

* [Step 2. Adding @EnableAspectJAutoProxy annotation to Spring config file](https://medium.com/p/3b4435892f16#7f78)

* [Step 3. Creating new Aspect class](https://medium.com/p/3b4435892f16#fb93)

* [Step 4. Moving user logging feature from business part of the code to Aspect class](https://medium.com/p/3b4435892f16#1ffe)

* [Step 5. Testing user logs](https://medium.com/p/3b4435892f16#5b82)

## Overview

I like to thing of Spring AOP as a wiretapping. As all the masters of espionage its main task is to monitor and react to actions that are made somewhere else. Also it is really important that all of their actions are made undercover, so the adversary does not know that they are operating. Spring AOP works in a very similar way. It is not incorporated into the business code and it should not have impact on how it works. So it is just listening and eventually report, but does not have impact of the chain of events. At least it is the most desired and say way to use it.

To set up a wiretap spies needs to put the bug in a particular phone. In Spring AOP this phone will be called ***join point*** and it is a part of the code (method, constructor or field assignment) we want to monitor. To achieve it as a programmer we need to create a ***pointcut***, which is a regular expression that matches the *join point*, so the Spring will know that we want monitor this particular part of the code. Once we define the *poincuts* we need to decide what to do with them and for that we use methods that are called ***advices***. A place where several p*ointcuts* are coupled with their *advices* is called an ***aspect***.

In general most of the AOP code is located in one or more POJOs (*aspects*) that contain public methods (*advices*) that are responsible for cross-cutting concerns. In their bodies there is a code that will be excecuted once a business part of the code reaches the *join point*. And these can be defined using *pointcut expression*.

### Pointcuts

*Pointcut* determines the *join point* of interest and in the code it appears as *pointcut* *expression*. It works similarly to regular expressions, using the special syntax it matches methods with *advices*. Also it worth to mentioned that Spring AOP supports only those classes that are Spring beans. If they are not registered as a Spring component, they won’t be available. Here is a *pointcut* *expression* general syntax (those parts that are in red are mandatory) with some examples:

![](https://cdn-images-1.medium.com/max/2812/1*MURK7HxXo8JcrY0PvX5c_Q.png)

From above picture you can figurate out that only return type and the method name pattern are mandatory, other ones are only optional. A wild card for these expressions is *****. Here is some examples of such expressions that should cover most of the cases.

Execution of any public method. First * means that it will match any return type, and ***(..) **means that the expression will match any method, no matter how much arguments it contains.

    execution(**public** * *(..))

Here it is expression that matches all setter methods.

    execution(* **set***(..))

All the methods from AccountService class will be matched.

    execution(* **com.xyz.service.AccountService**.*(..))

A *join point* will be whole service package and its sub-package.

    execution(* **com.xyz.service..*.***(..))

This will be matched only for those methods in the DemoClass, which has* int* as a first parameter.

    execution(public int **DemoClass.***(**int**, ..))

There are also some advance techniques of declaring *pointcuts*. In previous part before expression I’ve used ***execution***, which is a *pointcut designator (PCD)*, which tells Spring what to match. Apart from that there are other PCDs like:

* *within* — as an expression you need to provide package full name, so all the classes and methods from it will be matched (as I showed earlier it can be achieved with *execution*, but in a more simple way).

* *this* and *target* — these are tricky one that I do not fully understand them. Not to mix everything I can only tell that in a *target* we can provide an interface class name so all the classes that implements it will be matched.

* *args* — this will be looking for all the methods that has an argument with a specific type.

* *@annotation*— it limits to the *join points* that has specific annotation. One of the trick is to create own annotation and add it to the particular parts of the code.

* *@args* — it is a combination of last two PCDs, it will look for particular argument type that is passed to the annotation.

* @within, @target, @annotation — yes, again @annotation; it is because for me they do all the same, I was trying to find a good explanation (good = understable for me :) ), but I wasn’t able to find it. I wasn’t using them in my project so far and that’s why I wasn’t thinking about them.

Each of the *point cut* can be linked to an advice in two ways. First one, directly above proper advice, like in below example:

<iframe src="https://medium.com/media/ddd57998834696fd760460800adb976b" frameborder=0></iframe>

Or it could be declared separately and then added to the *advice. *To do that we need to declare unmatched *pointcut* with an annotation @Pointcut and then add its method name to the proper advice annotation. Due to this approach we can combine multiple *pointcuts* into one. For example, I want to match only those *saveUser(User)* methods that has also annotation @Transactional:

<iframe src="https://medium.com/media/3e787334490652619f0cc0903a8115a9" frameborder=0></iframe>

### Advices

Once the *join points* are defined let’s move on to methods that are called when certain constrains are met. They are *advices* and such can be divided into following types depending on when it will be executed:

* **@Before **— Advice will be called before Jointpoint.

* **@After** — Advice will be called after Jointpoint, regardless it has throw an exception or not.

* **@AfterReturning** — Advice will be called after Jointpoint, unless it will throw an exception

* **@AfterThrowing** — Advice will be called after Jointpoint, but only then when it will throe an exception

* **@Around** — This kind of advice can be invoked before and after Jointpoint method is called

**@Before**

It is the simplest kind of advice, that will be executed before the business part. It won’t store any information about the execution of the code and the outcome of it, but it is possible to get input arguments from origin method. So for example, if I want to get to the UserDTO class that are passed to *userService.saveReaderUser(UserDTO userDTO) *method I need to add a *JoinPoint* argument, which provides some metada, so the code for handling it will look like as follows:

<iframe src="https://medium.com/media/64bd4759aa44c5bb4d4e28a933f84fed" frameborder=0></iframe>

But if I wouldn’t want to get such information, and just use it as a plain indicator that code is ran it should be like it is presented below:

<iframe src="https://medium.com/media/426fa5c75bc532d725cf465ff813b3c7" frameborder=0></iframe>

**@AfterThrowing**

Another kind of advices are those that are executed when the method exits with an exception. It can be declared likewise simple @Before advice, but more often we want to get information about the exception. To achieve it we need to add new parameter to the annotation (***throwing***) and new argument to the function (***Exception***) and, it is very crucial, their names have to match!

<iframe src="https://medium.com/media/d87a3fcf41f00973b0f5311a62e5f4c6" frameborder=0></iframe>

Of course if we don’t need to have exception information, and just to be notified that some sort of error occurred, the advice will look simpler:

<iframe src="https://medium.com/media/097cb6b0d1884f88ee2466e484e3a522" frameborder=0></iframe>

Just take one thing into consideration, in above example there is no possibility to define which exception we would like to handle, so all of them, regardless of their type, will be matched.

**@AfterReturning**

This advice is ran only then when the method ends normally, without any exception. As in other types of *advices* it can be declared as simple, no argument method, like the following.

<iframe src="https://medium.com/media/c8eb868ebbf8b8d55ee34420163de2ef" frameborder=0></iframe>

If the method from the business part is returning an object (or primitive type) it is possible to get it and use within the *advice* method body. To do that we need to provide additional parameter into annotation (***returning***) and also add Object input argument to the *advice* method. It is important that the name of the argument and the value of the parameter are the same! Below example assumes that the return type of the *saveUser* method is *Long* and it represents the ID number of saved user, so we can make use of it in *AfterReturning* advice.

<iframe src="https://medium.com/media/d589e7e1df085505c57757d6e463c931" frameborder=0></iframe>

Also it is worth notice that using this annotation you only pass the value of the object, not its reference, so it is not possible to change the outcome of business part. To do that we need to use the last, the most powerful kind of advice — *@Around*.

![Photo by [Joey Nicotra](https://unsplash.com/@joeynicotra?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/6662/0*b9YvztU9ym3KlXZ_.)*Photo by [Joey Nicotra](https://unsplash.com/@joeynicotra?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

**@Around**

At the beginning of my post I’ve told that Spring AOP acts like spy, that listens and monitors the code, but it is not affecting the business part. I wasn’t totally honest with this, but let me tell why. Before I jump into *Around* advice example I would like to explain why it is very important to use it really careful. This type of advice is running both before and after calling the method. It is possible, because Spring AOP is proxy-based, which means that when main application is calling some method in the class it does not doing it directly, it is making it via proxy (factory) that is linked to original business class. I don’t want to go into the details (partly because I’m not 100% sure of it 😉 ), but more information you can get from official documentation.

They key feature of around advice is that it can determine when, how or even if the method will be executed. So thanks to it we have a very powerful tool that can have impact on the workflow of the code. In smaller applications, with small group of developers, it can be really useful, but in a greater group it can end up as a disaster, because in a complex systems it will be hard to track code execution if it will be scattered all over the places. That’s why it should be done really carefully.

As an argument Around advice requires a ProceedingJoinPoint class, which has method proceed() which will cause the execution of underlying method. Before and after calling proceed() method we can do whatever we like, for example we can set up timer so we can track how long the method was working. Also by adding the argument from the original method to the advice we can use and modify the object before the execution.

Here is a code of the simple @Around advice:

<iframe src="https://medium.com/media/b78394e3ce9203f3b37cf80cd9a13948" frameborder=0></iframe>

And also more complex example, before saving the user to the database I would like to clean input (remove unnecessary whitespaces and converted to lower-case) and then proceed with saving in the database. As a result I would get the ID of the user.

<iframe src="https://medium.com/media/439f8c489a329932f1c4a8693770137d" frameborder=0></iframe>

**Aspect ordering**

The last thing I want to write about is ordering *aspects*. Imagine that we have several of them and they for at least one method couple of them can be called. Be default all of them will be executed randomly, with no particular order. To straight this out we need to use @Order annotation with an integer parameter — the lowest number the more important the *aspect* is so it will be executed first. It is not relevant if the ordering numbers are proceeding, so the *aspect* with order levels 1,2,3,.. will be executed in the same order as -13,0,75,… NOTE: unfortunately it is not possible to order *advices* within one *aspect*.

<iframe src="https://medium.com/media/d1cb1719cc12d3c8de0478b2cae41021" frameborder=0></iframe>

So that’s everything for an introduction and lets’s go to configuration and creating first *aspect* in the Library Portal.

### Step 1. Adding Spring AOP dependency to build.gradle file

As usual first I’ve added some dependencies and refreshed the project. You probably wondering why I’ve added AspectJ library. It is because that Spring AOP relates on it. And quick tip for future projects — AspectJ is more robust than Spring AOP and in some cases it is quicker, but for more cases Spring AOP will do the trick. AspectJ should be used in more complex systems (more info in Ref).

<iframe src="https://medium.com/media/1f45c7e3701b403d3ac4eed1ff752903" frameborder=0></iframe>

### Step 2. Adding @EnableAspectJAutoProxy annotation to Spring config file

Next I’ve enabled Spring AOP functionality by adding annotation to the *LibraryConfig* class (of course it can be done also via XML configuration).

<iframe src="https://medium.com/media/74e65957cf292cd32addb31145a48361" frameborder=0></iframe>

### Step 3. Creating new Aspect class

First I’ve created a new package — aspect — that will store all my Aspects (I plan to create at least two of them, one for users and second for books). In my project I am using component scanning for autodetecting components so I’ve annotated new class with *@Aspect* as follows:

<iframe src="https://medium.com/media/396eb08ba11553b780c60469461456b0" frameborder=0></iframe>

### Step 4. Moving user logging feature from business part of the code to Aspect class

Just to remind you, here is the code snipped used of logging events that is incorporated into business part.

<iframe src="https://medium.com/media/9287f5fbfcb1ba15a1486b7df3157d8e" frameborder=0></iframe>

It is located in *LibraryUserDetailService.class* and I wanted to move it to the *UserLoggingAspect*. So first I’ve defined a new method called s*aveNewUserLog *with a proper *pointcut*. I’ve chosen to use *@AfterReturning* advice, because I want to make sure that I’ll get information only when the user will be added to the database successfully. If I would done it before, there could be the chance that during this action some connections issue might occur, so it will cause some discrepancies in the system. Rest of the code is simple copy-pastying from the *LibraryUserService* class to method body. To get user details I am adding it as a parameter.

<iframe src="https://medium.com/media/daf898b0b26a8c6ac0f255ef8c76ae6e" frameborder=0></iframe>

### Step 5. Testing user logs.

And finally after running the application and registering new user via web form I got new line printed in the console and new entry in the database!

![](https://cdn-images-1.medium.com/max/2600/1*E6-dBgDSUgP899aTz2U7Vw.jpeg)

P.S. I don’t know if I made a simple mistake in a pointcut expression or not, but at a first time I wasn’t able to run above code. It didn’ work, so I’ve checked if I register the Spring bean of an *aspect *(by printing the list of it in the console*) *correctly and it was ok, and then finally it runs as aspected. In a meantime I’ve changed a pointcut expression so it might do the trick, but maybe it wasn’t. To be honest I don’t know for sure what was the problem, but I guess that checking bean registration in Spring context might be a good approach.

Whole code of changes made for this post can be found here:
[**wkrzywiec/Library-Spring**
*Library-Spring - The library website where you can borrow books.*github.com](https://github.com/wkrzywiec/Library-Spring.git)

### References
[**Core Technologies**
*Foremost amongst these is the Spring Framework's Inversion of Control (IoC) container. A thorough treatment of the…*docs.spring.io](https://docs.spring.io/spring/docs/current/spring-framework-reference/core.html#aop)
[**Aspect Oriented Programming with Spring Boot**
*A web log on Software Engineering subjects: Java, Spring, Big Data, Cassandra, etc.*niels.nu](http://niels.nu/blog/2017/spring-boot-aop.html)
[**The AspectJTM Programming Guide**
*If you are completely new to AspectJ, you should first read Getting Started with AspectJ for a broad overview of…*www.eclipse.org](https://www.eclipse.org/aspectj/doc/released/progguide/index.html)
[**Introduction to Pointcut Expressions in Spring | Baeldung**
*In this tutorial we will discuss the Spring AOP pointcut expression language. We will first introduce some terminology…*www.baeldung.com](http://www.baeldung.com/spring-aop-pointcut-tutorial)
[**Comparing Spring AOP and AspectJ | Baeldung**
*There are multiple available AOP libraries today, and these need to be able to answer a number of questions: Is it…*www.baeldung.com](http://www.baeldung.com/spring-aop-vs-aspectj)
[**Spring AOP Tutorial - HowToDoInJava**
*Spring AOP enables Aspect-Oriented Programming in spring applications. In AOP, aspects enable the modularization of…*howtodoinjava.com](https://howtodoinjava.com/spring-aop-tutorial/)
