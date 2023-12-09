---
title: "Start learning JVM internals with Grafana dashboard"
date: 2023-10-09
summary: "Explore a Grafana dashboard that can serve as your initial entry point into understanding JVM internals, like garbage collection, class loading and more."
description: "This post provides a practical, hands-on guide on deciphering a widely used Grafana dashboard for JVM internals. After going through it, you'll have the knowledge to take your first steps in monitoring and tuning Java applications."
tags: ["java", "jvm", "performance", "garbage-collector", "cpu", "memory", "class-loader", "monitoring", "prometheus", "grafana", "micrometer"]
---

![cover](cover.jpg)

> Photo by [NEOM](https://unsplash.com/@neom) on [Unsplash](https://unsplash.com/photos/a-person-swimming-in-the-ocean-with-a-mountain-in-the-background-s6g6ZSxM3kQ)

*Software engineering is not only about coding. It involves selecting the appropriate solution, implementing it, and verifying its alignment with specific goals. Non-functional requirements, a category often unspoken of, encompass a range of capabilities that a system must fulfill. One of them is performence. Some systems needs to handle lots of users at the same time, while others must process a bulk amount of data within tight timeframes. Numerous factors influence this, including the code itself and how the JVM is configured in the case of JVM applications.* 

*This blog post aims to guide you through the interpretation of one of the most widely used JVM Grafana dashboards, shedding light on key elements that warrant daily monitoring.* 

## Not enough memory

Learning a programming language can be a rough road. First a basic syntax needs to be known to achieve standard tasks. But unless we don't want stop here and not pursuite the software engineer job. Otherwise the next step is to learn one or two popular frameworks in a given ecosystem to be seen in a job market. Once we land in the dream job we find out that knowing basics of a programming language and popular frameowrk is not enough. Things like best practices, design patterns or system desing are also key eleemtns to become a successful expert in software development. 

And finally, a day comes when you knew all this stuff (or at least you think, you know it) you get a call from operations team that your application is way too successful and it can't keep up with a large number requests from users. None of the previous step did not prepare you for a skyrcoketing CPU usage or memory. You're panically trying to recall why all these parts are needed and what they have to do with your state of the art application. 

## Look into inside

Does it sound familiar?

How can you prevent this from happening? The first step is to initiate app monitoring to observe trends and receive alerts when key metrics approach dangerous thresholds. Additionally, understanding how the app responds under various types of pressure is crucial.

Numerous tools can be employed for this purpose. Some are built into the JDK, such as *Java Flight Recorder* with *Java Mission Control*, while others can be downloaded, like *JProfiler*, and some are cloud platforms, such as *Datadog*. It's easy to feel overwhelmed initially, as each tool provides different types of information, often at a very low level.

So, where do you begin with monitoring app performance? Which tool should you choose first?

## Grafana dashboard

I recommend starting with Prometheus and Grafana. Both tools are open source and non-invasive, meaning there's no need add any special tool/agent that may affect the overall performance. They only require adding metrics libraries to a project. The setup is relatively straightforward, as I've outlined in a previous article - [How to set up monitoring tools for JVM](https://wkrzywiec.is-a.dev/posts/048_jvm-monitoring/#setting-up-jvm-dashboards-in-grafana). 

Mentioned post covers also how to import one of the most popular JVM dashboard - [JVM (Micrometer)](https://grafana.com/grafana/dashboards/4701-jvm-micrometer/) - this is will be the subject of this post. It'll walk you around key metrics and explain when and why they're important.  

The dashboard consists of sections that will be described in the following parts, which I group and change order a little bit.


## JVM Memory

![intro](intro.png)

```
>> here read and check once again
```

If you ever wonder what's the first thing that you must keep eye on when monitoring Java application in most of the case it would be the memory usage. This is a vital information about the health of an app, since JVM needs it to run it. 

Therefore it is not a suprise thet this is a first information that is provided by the dashboard - the percentage of how much heap and non-heap memory is fillied up (along with data about how long the app is running). 

In most applications, these two metrics are the ones we should keep an eye on. They have a significant impact on its performance and can quickly explain why the app is running slow or even crashing.

Why these two metrics are that important? First of all we need to know that Java is object-oriented language. It means that every program is a set of objects which interact with each other. They have methods that are invoked by other objects and they also hold data. And in the real applications number of objects may be very large. 

JVM is storing all objects in memory space called heap. Apart from objects JVM needs to load other things to memory, things like metadata for classes, code cache produced by Just-In-Time (JIT) compiler and others (they will be listed later on).

![jvm-memory](jvm-memory.png)

So what we can read from here? The dengarous situation would be when increasing number of memory in the heap area suggests that many objects are created and their are never destroyed (collected by the Garbage Collection, which will be mention later). If this happens an app would start to act slower and eventually it will crash and throws the `java.lang.OutOfMemoryError`. 

Besides heap data, JVM has a second data area, called non-heap (or off-heap or Native Memory). It stores various data which can be divded into following spaces:

* Metaspace (aka Method Area) - it holds class-related information about classes code, their fields and methods after being loaded by classloader (more about it in the article). It also contains information about constants (in Constant Pool) 
* Code Cache - is an area where optimized native code produced by Just-In-Time compiler is stored.
* Program Counters - is pointing the address of current executed instruction (each thread it's own Program Counter), 
* Stacks - the LIFO stack of frames for each executed method, it contains primitives variables and references to the objects on the heap.

Usually it is the heap that may be too small, but we need to understand that memory problems with non-heap data could also crash an pp. Too much classes loaded into Metaspace may cause `java.lang.OutOfMemoryError` and too much frames in the Stack may end up with `java.lang.StackOverflowError` thrown.    

### JVM Memory Pools (Heap)

![jvm-memory-heap](jvm-memory-heap.png)

generative (?) theory

rysunek z podziałem na generacje

można sterować udziałami każdej z generacji; duża young generation jeśli tworzymy dużo obiektów, które są tylko tymczasowe; można też ustalić jak długo obiekty będę w której generacji? (to już dla hardcorów?)


### JVM Memory Pools (Non-Heap)

method area (metaspace) - bigger application with lots of different classes = bigger metaspace; default metaspace size is unlimted - size it to not take it too much memory; garbage collector is clearing it?

code cache - https://www.baeldung.com/jvm-code-cache

stacks - `StackOverflow`

![jvm-memory-non-heap](jvm-memory-non-heap.png)
### Garbage Collection

![garbage-collection](gc.png)

czy ten usuwa też coś z native memory? załodowane klasy, które nie są potrzebne już?

### What if the app is consuming too much memory?

How to mitigate it? The easiest way would be to change the maximu size of the heap. Bigger heap means all needed objects will fit it. This can be achieved by providing the `-Xmx` followed by the size number of memory that will be reserver for a heap. E.g. `-Xmx1024m` will alocated 1024 MB for heap. 

Changing the maximum size of a heap may be the remedy, but it many cases it's rather covering the symptoms than treating the real cause of a problem. Increasing number of objects may suggest that there is a memory leak somewhere in an application. This place in the code needs to be found and fixed.

Other options may be that too much data has been tried to be loaded into the memory. It can be either because of inefficient data structure or simple large volume of data, which was not predicted. In the first case the solution would be to optimize how we store data in JVM and for the latter it would be to increase the heap size or think about how to chunk the large amount of data into smaller pieces.

Depends on the type. If heap is increasing - too much objects, or they are too big.

heap memory best practises:
* use less memory
    * reduce object size - too much data, too much variables? maybe instead of String use boolean? instead of Object use the primitive (sprawdź prezentacje Kubryńskiego, albo książki na str 189); even null consumes space   
* lazy initialization of fields (str 192)
* avoid immutable object - do not create copy if needed (if object is used only once, or in a small method, maybe make it mutable)
* avoid String that are the same

## I/O Overview

![io](io.png)

## Classloading

![classloading](classloading.png)

## JVM Misc

![jvm-misc](jvm-misc.png)



## Conclusion