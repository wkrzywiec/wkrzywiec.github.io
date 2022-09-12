---
title: "I‘m going back to my old project — WaWa Tabor"
date: 2018-10-19
summary: "Going back to my old Android app"
description: "More than a year ago (in late 2017) I was working on my first, Android app. It taught me a lot, but honestly it wasn’t a good product. Now I want to fix it, and here is my “big” plan what I want to do."
tags: ["java", "android", "project"]
canonicalUrl: "https://wkrzywiec.medium.com/i-m-going-back-to-my-old-project-wawa-tabor-599c5cdeebf4"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/i-m-going-back-to-my-old-project-wawa-tabor-599c5cdeebf4).
{{< /alert >}}  


![“tower clock building” by [silviannnm](https://unsplash.com/@silvianm?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/4896/0*9ChLr4WoGK6TJAjK)*Photo by [silviannnm](https://unsplash.com/@silvianm?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*More than a year ago (in late 2017) I was working on my first, Android app. It taught me a lot, but honestly it wasn’t a good product. Now I want to fix it, and here is my “big” plan what I want to do.*

### WaWa Tabor — what’s that?

First, you may wander what’s the project. The app was designed to show users the location of buses and trams around Warsaw (Poland). It helps finding a nearest bus or tram in order to get to your destination as fast as you could.

You can check it on your own by downloading it from the Google Play store:

[**WaWa Tabor - Apps on Google Play** | play.google.com](https://play.google.com/store/apps/details?id=com.wawa_applications.wawa_tabor)

### Background

As already mentioned, my app was my first Android app, but also was one of my first app ever (I’ve started to learn Java at the end of 2016). So as you might guess, it wasn’t designed in a right way.

Just before this project I’ve finished the [Udacitys’ Android free course](https://eu.udacity.com/course/new-android-fundamentals--ud851) (which is great by the way, I totally recommend it for beginners), during which I’ve learnt how to create a weather app that uses most of the common Android building blocks (RecyclerView, Intents, Content Providers, etc.).

So my idea was to create a similar app on what I’ve learnt. And at the time it was a good idea, but moving forward with the knowledge I’ve got arround Android app development I’ve seen that it’s not *sexy *enough. It was working, but wasn’t implementing the [MVVM pattern](https://developer.android.com/topic/libraries/architecture/viewmodel), wasn’t making use of [RxJava](https://www.androidhive.info/RxJava/android-getting-started-with-reactive-programming/) library, etc.

Also, and this is more important from the user perspective, it isn’t working as expected. The position of the bus should be refreshed each 10–15 seconds, but sometimes it stops for some reason or the data are never fetched from the server. These and other small bugs were report by me or users and must be fixed.

### The Plan

Before I proceed with that I’ve come up with the plan.

The idea is to split my work into three phases (yes, just like the Marvel Cinematic Universe).

In a first one, I want to migrate the app to MVVM pattern with RxJava. So purely it will be backend fix, which I hope will result in a better performance. Probably it’ll be the most tricky part. Maybe the legacy code is not so long, but it might be quite challenging to make sure that all works with no errors. And speaking of the devil, I plan to cover most of the code with unit JUnit) and UI tests (Expresso). And yes, I’ll try to TDD as most as I could.

Then, in 2. phase, I’ll focus on the user interface. I plan to refactor the app to the single Activity model with multiple Fragments. After this phase there will be only one search field (and not as it is now, where I have two of them, each for different mean of transport). Also Google maps display preferences will be removed. I’ve added them, because I’ve thought it was a nice thing, but after a while I think it isn’t so necessary.

In the last phase I want to add new features to the application. On of them, would be information about the direction of the bus. Unfortunately the API that I’m using does not provide such information, so the idea is to calculate it on my own with a Spring Boot microservice app deployed on a server (or Google Cloud) and then information would be sent to the mobile app.

As a result of the third phase I would like to have following ecosystem of the WaWa Tabor.

![](https://cdn-images-1.medium.com/max/27868/1*BYfW3n2OKybuyBmwnjNvmw.png)

* **WaWa Tabor** — the core product, that will be downloaded by the user. It ill be getting information from the API (GPS location) and my microservices (calculated properties, like bus direction).

* [**ZTM API**](https://api.um.warszawa.pl/)— open API, which provides on-line data about bus/tram locations.

* 
**Microservices** — these will be fetching the data from the API (scheduled task) and also it will be providing calculated values to the mobile app.

Moreover, I would like to add [Firebase](https://firebase.google.com/) chiefly for [Google Analytics](https://firebase.google.com/products/analytics/) and [A/B Testing](https://firebase.google.com/products/ab-testing/) to play around with them a little bit.

### What about Kotlin?

Yes, where is [Kotlin](https://kotlinlang.org/) in my great plan? It’s a big thing now in Android development world and I shouldn’t omit it, you would say.

And I agree, as [Google announced in 2017](https://android-developers.googleblog.com/2017/05/android-announces-support-for-kotlin.html) Kotlin was added as official programming language along with Java. Since then number of Kotlin-based projects skyrockets and as well as number of job offers that requires it.

So why I don’t want to refactor my project into Kotlin? Trust me, I do.

The only reason I don’t do it right away is that, I don’t know it yet 😉. It’s not my excuse, I plan to migrate to Kotlin after all, but I won’t do it right now.

As it is possible to mix Java and Kotlin in one project I’ll plan to successively replace Java code with this new language.

### All necessary links

You can track the development progress on my [Kanban board](https://trello.com/b/k5JcwEmt/wawa-tabor), check what I’m currently working on and what are my further steps.

Apart from that after each phase, or major change (like migration to MVVM architecture) I plan to write a blog post with some retrospectives thoughts. All of them will be listed in this blog post below.

* [**wkrzywiec/WaWa-Tabor** | github.com](https://github.com/wkrzywiec/WaWa-Tabor)
* [**Trello — WaWa Tabor Board** | trello.com](https://trello.com/b/k5JcwEmt/wawa-tabor)
* [**WaWa Tabor - Apps on Google Play** | play.google.com](https://play.google.com/store/apps/details?id=com.wawa_applications.wawa_tabor&hl=en)
