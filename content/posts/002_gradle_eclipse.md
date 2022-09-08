---
title: "Setting up Gradle web project in Eclipse (on Tomcat Server)"
date: 2018-03-18
summary: "Setting up Spring application with Gradle"
description: "In this post I’ll focus on the most annoying part of the software project — configuration. I’m going to show you how I had set up basic environment to code, build, deploy and run my Spring MVC project — Library Portal. I ‘ll go thru each step of the whole process, from brand new web project to first ‘Hello World!’ that will show up on the test page. Let’s get hands dirty!"
tags: ["java", "spring", "project", "gradle", "eclipse", "tomcat", "library-project"]
canonicalUrl: "https://wkrzywiec.medium.com/setting-up-gradle-spring-project-in-eclipse-on-tomcat-server-77d68454fd8d"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/setting-up-gradle-spring-project-in-eclipse-on-tomcat-server-77d68454fd8d).
{{< /alert >}}

![Photo by [Kelvyn Ornettte Sol Marte](https://unsplash.com/@kelvyn?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/12032/0*LNSi5DpmPc-8IZAt.)*Photo by [Kelvyn Ornettte Sol Marte](https://unsplash.com/@kelvyn?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

In this post I’ll focus on the most annoying part of the software project — configuration. I’m going to show you how I had set up basic environment to code, build, deploy and run my Spring MVC project — Library Portal. I ‘ll go thru each step of the whole process, from brand new web project to first ‘Hello World!’ that will show up on the test page. Let’s get hands dirty!

### Step 1. Installing Java SE Development Kit (JDK) and Eclipse IDE

First things first, I needed to to have both of these to run any Java application (including Spring project). JDK is a neccessary toolkit for any Java project and *Eclipse IDE* is a really practical tool to make coding more comfortable and more efficient.

I don’t want go into details with installation of both these things, as they are pretty straightforward. Here are the links, where can be found their latest releases to download:

***Java SE Development Kit*** - [**Java SE - Downloads | Oracle Technology Network | Oracle**
*Java SE downloads including: Java Development Kit (JDK), Server Java Runtime Environment (Server JRE), and Java Runtime…*www.oracle.com](http://www.oracle.com/technetwork/java/javase/downloads/index.html)

***Eclipse IDE*** - [**Eclipse desktop & web IDEs**
*Eclipse is probably best known as a Java IDE, but it is more: it is an IDE framework, a tools framework, an open source…*www.eclipse.org](https://www.eclipse.org/ide/)

In this project I’ve been interested in *Java EE* edition of the *Eclipse.* When I was writing this post the latest release version was *Oxygen* and could be downloaded from here:
[**Eclipse IDE for Java EE Developers | Packages**
*Tools for Java developers creating Java EE and Web applications, including a Java IDE, tools for Java EE, JPA, JSF…*www.eclipse.org](https://www.eclipse.org/downloads/packages/eclipse-ide-java-ee-developers/oxygen2)

### Step 2. Installing Gradle plugin into Eclipse

In short, Gradle is very useful tool for automating build task of the application and standarization project structure. The main reason that I am using it is for this cool feauture called dependency management. Thanks to ti I don’t need to wonder how to download external libraries to my project. It skips the exhausitng process of finding it on the internet, downloading and then adding it to the project. Instead you need to type single — YES, SINGLE!- line into a ***build.gradle*** file and refresh project. That’s it!

Gradle also support other features like creating own task that can be included during build script of the project, e.g. before running application Gradle can copy some resources into your project, or maybe create database and populate with some basic input that can be used for testing. There are many options to go (for more information, please see the Reference section at the end of my post).

Installing it in Eclipse is also rather straightforward. Here is a video of how to do it:

<center><iframe width="560" height="315" src="https://www.youtube.com/embed/jpEHiRgLIRE" frameborder="0" allowfullscreen></iframe></center>

### Step 3. Building Gradle web project in Eclipse

Once I had all tools set up I’ve moved to the part which was creating basic Gradle project and converting it into Java Web application.

First, I’ve created new standard Gradle project with all defaults parameters in Eclipse. Next I’ve added *Dynamic Web Module* facet into this project. To do that I’ve right clicked on the project name in the *Project Explorer* window and then chose ***Properties***. A new window showed up. On the left there was option tree, from which I’ve picked ***Project Facets.*** From the list on the right side of the window I’ve selected ***Dynamic Web Module***,then ***Apply*** and ***OK*** button (below is the screenshot of Project Properties window).

![](https://cdn-images-1.medium.com/max/2000/1*3P65qMaYdpJmWQS6FL7XjQ.jpeg)

Ok, so now a tricky part. One of the outcomes of previous step was that *Eclipse* created new folder and subfolders where should be stored all frontend files of the application (HTML, JSP, CSS, etc.) — *WebContent*. To make it work with Gradle I would needed to make some configuration in a ***build.gradle*** file, but because I am lazy and most of web tutorials have different folder structure I’ve went with standard Gradle config. So in my case I’ve deleted hole *WebContent *folder and* *create *webapp* folder and its subfolder *WEB-INF* under *src/main. *Also a resource folder was created— it will be used for some other features which I will talk further in my next stories. After thatmy file structure looked like this:

```
library-spring/
    src/
        main/
            java/
            resources/
            webapp/
                    WEB-INF/
        test/
            java/
```

Last task was to tell Gradle that my project is a web application. Thus to convert java project into it I’ve modified **build.gradle** by adding `apply plugin: ‘war’` line into it. I’ve also cleared all comments that were automatically generated by the *Eclipse* so the I had following code:

```gradle
apply plugin: 'java-library'
apply plugin: 'war'

repositories {
          jcenter()
}

dependencies {
         api 'org.apache.commons:commons-math3:3.6.1'
         implementation 'com.google.guava:guava:21.0'
         testImplementation 'junit:junit:4.12'
}
```

To apply this change I’ve right clicked on the ***build.gradle*** file in Project Explorer, found **Gradle** on the list and clicked ***Refresh Gradle Project***.

### Step 4. Installing Gradle Tomcat plugin

So far my project has been created as a web application, but if I want to deploy it on a server each time I would need to convert it to war file and then manually run it on server, which is highly inconvieniet. That’s why I have ended up with installing a Tomcat plugin to Eclipse so, when I build a project via Gradle task it will be automatically deployed on a Tomcat server.

I’ve added following lines to **build.gradle** file and refreshed it:
```gradle
apply plugin: 'com.bmuschko.tomcat'
apply plugin: 'eclipse-wtp'


buildscript {
       repositories {
             jcenter()
       }
       dependencies {
             classpath 'com.bmuschko:gradle-tomcat-plugin:2.4.1'
       }
}


dependencies {
         def tomcatVersion = '8.0.46'
         tomcat "org.apache.tomcat.embed:tomcat-embed-core:${tomcatVersion}",
         "org.apache.tomcat.embed:tomcat-embed-logging-juli:${tomcatVersion}",
         "org.apache.tomcat.embed:tomcat-embed-jasper:${tomcatVersion}"
         api 'org.apache.commons:commons-math3:3.6.1'
}


tomcat {
         httpPort = 8080
         enableSSL = true
         contextPath = '/library-spring'
}
```

Now everything was set up, so in order to deploy the application I need to run it via Gradle task — `tomcatRun`. To make it easier in future, so I would only need to click the Run button in Eclipse to deploy the app I’ve created new run task.

I’ve found ***Run/Run Configurations…*** and after entering it, in the new window picked ***Gradle Project*** folder and clicked ***New*** icon. In the form I have entered following input:

* Name: *Library Spring — Run*

* Gradle Task: *tomcatRun*

* Working Directory: *${workspace_loc:/library-spring}*

![](https://cdn-images-1.medium.com/max/2070/1*KurBABWgx970IS7QYfFE7g.jpeg)

To finalize I’ve clicked ***Apply*** button and ***Run*** it to test it.

### Step 5. Testing simple Java EE application

Finally, let’s find out if all that effort was worth it. To test it I’ve created a simple web project, without any Spring framework code. To achieve it I’ve added two things — JSP and *web.xml* file. The purpose of the first one is pretty straightforward, it is the page that will be displayed in a browser after deploying the app on a server. The latter is more complex. It is so called Web Application Deployment Descriptor (what a scary name!), and it provides some initial parameters (like servlets, welcome files, filters and other components) that a server needs to know.

In my case I’ve created a really simple JSP page (*index.jsp*, it is located in a folder *src/main/webapp*) that has only ‘*Home page*’ in its body.

```html
<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
  <meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
  <title>Home page</title>
  </head>
  <body>
    Home page
  </body>
</html>
```

Next I’ve created the *web.xml* file (located in *src/main/webapp/WEB-INF* folder) that included only one tag: `<welcome-file-list>`. It contains all the files that server will be looking for to display, if no particular file/path will be specified. Important note, the file name on the list must be the same as I have provided above, otherwise file will be skipped and you get HTTP 404 error message.

```xml
<?xml version="1.0" encoding="UTF-8"?>

<web-app version="3.0" xmlns="http://java.sun.com/xml/ns/javaee"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/web-app_3_0.xsd">

	<welcome-file-list>
		<welcome-file>index.jsp</welcome-file>
		<welcome-file>index.html</welcome-file>
	</welcome-file-list>

</web-app>
```

At last, the configuration was over! Once I had run the Gradle deploy task and typed *localhost:8080/library-spring *on my browser* *I have ended up with sweet text printed —* ‘Home page’*!

![Photo by [Andre Hunter](https://unsplash.com/@dre0316?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/6016/0*K6mUtdWFIonkMbHs.)*Photo by [Andre Hunter](https://unsplash.com/@dre0316?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

And that’s it! It doesn’t looks so scary now, but believe me, I was looking for this outcome for quite some time. Here is the link to my GitHub repository, where you can find the whole project that I have created for this entry post:

[**wkrzywiec/Library-Spring** | GitHub.com](https://github.com/wkrzywiec/Library-Spring/tree/vanilla-web-app)

## References

I wouldn’t never manage to achieve this without first searching thru the internet looking for some answers, so here is a list of some resources that I have found really useful:
* [**Eclipse IDE - Tutorial** | vogella.com](http://www.vogella.com/tutorials/Eclipse/article.html)
* [**Gradle Build Tool** | gradle.org](https://gradle.org/)
* [**Building Java Web Applications** | guides.gradle.org](https://guides.gradle.org/building-java-web-applications/)
* [***Create a Gradle Java Web Application and run on Gradle Tomcat Plugin*** | Plugino7planning.org](https://o7planning.org/en/11247/create-a-gradle-java-web-application-and-run-on-gradle-tomcat-plugin)
