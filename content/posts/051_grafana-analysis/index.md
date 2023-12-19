---
title: "Start learning JVM internals with Grafana dashboard"
date: 2023-10-09
summary: "Explore a Grafana dashboard that can serve as your initial entry point into understanding JVM internals, like garbage collection, class loading and more."
description: "This post provides a practical, hands-on guide on deciphering a widely used Grafana dashboard for JVM internals. After going through it, you'll have the knowledge to take your first steps in monitoring and tuning Java applications."
tags: ["java", "jvm", "performance", "garbage-collector", "cpu", "memory", "class-loader", "monitoring", "prometheus", "grafana", "micrometer"]
---

sprawdzić, co pogrubić, co wykursować, co wielką a co małą literą
ustalic czym jest dla mnie GC, collector czy collection

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

Why these two metrics are that important? First of all we need to know that Java is object-oriented language. It means that every program is a set of objects which interact with each other. They have methods that are invoked by other objects and they also hold data. And in the real applications number of objects may be very large. The latter indicator is accountable for measuring memory use of non-object related things, which in some cases are also worth to monitor.

![jvm-memory](jvm-memory.png)

Moving on, let's read the charts above, which are showing how memory usage has changed in time. It shows the actual memory usage (`used`) in a given moment, the maximum available (`max`) and the amount memory guaranteed to be available for JVM (`committed`).

So what we can read from the chart for a Heap memory? Certainly the `used` memory can't reachout to the `max` value. The dengarous situation would be when increasing number of memory in the Heap area suggests that many objects are created and their are never destroyed (collected by the Garbage Collection, which will be mention later). If this happens an app would start to act slower and eventually it will crash and throws the `java.lang.OutOfMemoryError`.

Besides Heap data, JVM has a second data area, called Non-Heap (or Off-Heap or Native Memory). It stores various data which can be divded into following spaces:

* Metaspace (aka Method Area) - it holds class-related information about classes code, their fields and methods after being loaded by classloader (more about it in the article). It also contains information about constants (in Constant Pool).
* Code Cache - is an area where optimized native code produced by Just-In-Time compiler is stored.
* Program Counters - is pointing the address of current executed instruction (each thread it's own Program Counter), 
* Stacks - the LIFO stack of frames for each executed method, it contains primitives variables and references to the objects on the heap.

Usually it is the heap that may be too small, but we need to understand that memory problems with non-heap data could also crash an pp. Too much classes loaded into Metaspace may cause `java.lang.OutOfMemoryError` and too much frames in the Stack may end up with `java.lang.StackOverflowError` thrown.

### JVM Memory Pools (Heap)

![jvm-memory-heap](jvm-memory-heap.png)

Let's now drill down into the Heap usage. But first we need to understand how Heap is structured, because it is not a monloith. Heap divided into spaces depending on the type of Garbage Collector that is used. Above we can see 3 charts of *Eden Space*, *Survivor Space* and *Old Gen* that are used by the **G1** Garbage Collector.

But why Heap is splited into spaces? It comes from something called *weak generational hypothesis*. It presumes that a life-span of objects varies. Most of them are very short lived. They are used only once and then the memory they occupy can be freed. Others, usually the smaller fraction, are the ones that are constantly used which and can't be destroyed. Due to this fact Garbage Collector (GC) is splitting heap into generations (spaces) where short-lived objects resides in the young generation (*Eden Space* and *Survivor Space*) and long-lived objects in old generation (*Old Gen*).

The rationale is simple. To avoid doing one, long garbage collection on the entire heap GC is performing it only on subset of it at the time. Also the frequency is different in each generation - the *Eden Space* is more often cleaned than the *Old Gen*, beacuse objects located there are needed only for a short period.

The above screenshot confirms that. We can see that the plot for `used` memory in *Eden Space* is formed in the characteristic jigsaw. It quickly fills up with new objects (which is expresed as rising plot on a chart) and once it reaches a certain threshold it is emptied (which causes the plot to go down).

On the contrarory, the *Survivor Space* and *Old Gen* are much more stable. There are some changes in them, but they are very subtle.

These three charts gives us vital information about content of the heap. We can read how often new objects are created and removed. If the cleanup for them is done very often and the old objects are kept on relatively same level it is tempting to increase the ratio of young to old generation size. The larger the young generation is the cleanup will be done less often. But on the other hand, it will be bigger, so the cleanup may take a little bit longer. The same goes for old generations - the smaller it gets the most frequent it is cleaned. So we must keep balance of it.

To adjust it use `-XX:NewRatio=N` (which is a ration of a young and old generations, e.g. `N=2` means that young generation is twice as big as an old one) or `-XX:NewSize=N` (which is an initial size of the young generation - all remaining will be assigned to the old genration).

### Garbage Collection

![garbage-collection](gc.png)

The previous already mentioned about the garbage collector (GC) which we will have a closer look now. It is a key part of JVM, because in contrast too languages like C++ we, developers, don't need to worry about freeing memory once an object is no longer needed. The role of the GC is to decide which objects should be destroyed and which should be preserved.

All new objects are allocated first in the *Eden Space* but during the next garbage collection they are promoted to the one of the *Survivor Space* if they are still in use. Then during next garbage collections they're again checked if they're shoud be promoted to next subspace of the *Survivor Space* or even to the *Old Gen*.

The first plot in the above screenshot tells us how often the certain type of garbage collection occurs in a second. We can see there that only one minor GC (only a young generation of the heap is cleaned) is happening, but it is also showing major GC (the objects from old generation are cleaned then). So by reading this chart we can figure out how often each GC is happening and if it's too often it may give a hint that one of the spaces is filling too quickly with a large number of objects.

But even if a number of GC is relatively high it's not always a bad situation. If each one if them takes a very short time and do not affect the overall application performance we have nothing to worry about. Hence, to make sure that it is really the case we can look into the second plot which facilities us with information about the average time of each garbage collection.

The last plot is showing us how much memory was used to allocate objects in the young generation and how much of it was promoted to older generations. This is really helpful information when we want to learn about memory load that GC needs to deal with in each cycle.


jakie są w javie 21, różne dla różnych wydań javy
ale można je podzielić na parallel vs serial, concurrent vs stop the world, incremental vs monolithic (garbage collector minibook)
generations, niektóre nie mają

major attr, choosing gc - strona 58, infoq gc minibook
choosing gc - str 113, performance book

So how objects are splitted into generations? First, a newly created object is allocated in the young generation. When a young generation fills up with new objects, Garbage Collector stops the application thread, cleans heap from unsued objects and 

czy ten usuwa też coś z native memory? załodowane klasy, które nie są potrzebne już?

### JVM Memory Pools (Non-Heap)

method area (metaspace) - bigger application with lots of different classes = bigger metaspace; default metaspace size is unlimted - size it to not take it too much memory; garbage collector is clearing it?

code cache - https://www.baeldung.com/jvm-code-cache

stacks - `StackOverflow`

![jvm-memory-non-heap](jvm-memory-non-heap.png)



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
