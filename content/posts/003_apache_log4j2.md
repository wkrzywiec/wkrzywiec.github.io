
# Creating user logs with Apache Log4j2
> Source: https://wkrzywiec.medium.com/creating-user-logs-with-apache-log4j2-90bfeb8a0d3f

One of the feature that I would like to implement in my Library Spring project is the ability to track some of the most important actions that can be made in the portal (like creating/modifying user, borrowing/adding the book, etc.). From the business perspective it is very common to use it, so the admins/managers can have some insight of the traffic on their websites.

![Photo by [rawpixel.com](https://unsplash.com/@rawpixel?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/5000/0*en6t2XC6GJArJaqh.)*Photo by [rawpixel.com](https://unsplash.com/@rawpixel?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

## Table of content

[Framework overview](https://medium.com/p/90bfeb8a0d3f#0f63)

[Step 1. Create table in MySQL database](https://medium.com/p/90bfeb8a0d3f#2963)

[Step 2. Add dependecies to build.gradle into the project](https://medium.com/p/90bfeb8a0d3f#4ee9)

[Step 3. Create ConnectionFactory class](https://medium.com/p/90bfeb8a0d3f#1491)

[Step 4. Configure Log4j2 using XML file](https://medium.com/p/90bfeb8a0d3f#22e9)

[Step 5. Use Logger in Service class](https://medium.com/p/90bfeb8a0d3f#1126)

[References](https://medium.com/p/90bfeb8a0d3f#8c84)

In this post I would like to show how I’ve managed to establish logging feature with Apache Log4j2 framework. I know that in Spring there is the Spring AOP module that helps with this feature, but in this entry I would like to focus on Log4j2 library. In my next post I will says something more about Spring AOP.

So first let me explain what I had wanted to achieve. Log entries are used to store information about the traffic within application. It usually gives information like who? where? what? when? make any crucial action in the system. For example in my Library Portal I would like to have information when each user was created or when he/she make has updated their personal details. Also I would like to track all the traffic regarding books, which book is the most popular, which of them is kept the longest, or maybe who borrows the largest number of them. There are many indicators that can be used to help library managers get an insight of their library to make it better.

From technology point of view I wanted to store all the logs in the MySQL database, as I think it is the most convenient way to do that. To achieve it I’ve decided to use popular logging framework Log4j2. It is really powerful tool to use, which allows to monitor when the particular part of the code is executed and then print and/or save it in the most convenient way. In my application logs are stored in MySQL database, but it could be save in a file (as a new line), printed in a console or send via email (for example when an error occur). These are the most common options, but there are more of them available.

## Framework overview

In Log4j2 there are three objects that cover different aspect of the logging functionality, they are: Loggers, Layouts and Appenders. In next sections I will try to explain what is the task of each of them. I don’t want to go much into details, like what is the details architecture of all objects (including LogManager, LoggerConfig, etc.), these can be find on the websites that I provide at the end of this post.

### Loggers

In short these objects are responsible for creating log entires and prioritized them. To visualize I will use below code snippet of the method that is used add new user to the database.

<iframe src="https://medium.com/media/301d9da27747a65bf8dc033766330a1f" frameborder=0></iframe>

As it shows the whole process of creating new logs is pretty clean and straightforward. At this point the only concern would be that *.info* part. To explain that I need to introduce the concept of logging levels. There are different kinds of them depending of how crucial they are. For example those logs with event level FATAL are used to warn about the most crucial events that can cause the stop of the entire application. On the other hand there is a level INFO that can be used for following the process workflows. Here is the list of all default event levels, from the most specific to the most general.

* FATAL

* ERROR

* WARN

* INFO

* DEBUG

* TRACE

* ALL

For example if in code we define that the event is on level WARN, it means that it will be processed further (to appender to be saved in database, as it is in my case) if the logger is set up on WARN, INFO, DEBUG, TRACE, and ALL levels. Similarly if the event has been marked with a level INFO, but the logger will be set up to process only those logs that are on ERROR level that means that it won’t be passed further (to appender to be save in database in my case).

Another aspect of Loggers are their hierarchy. The main Logger is the RootLogger, which is the required. Besides this main logging object there can be other ones that are ancestor to the previous, which will inherite all their set up regarding level, unless there are set up otherwise.

The default root Logger is assigned to ERROR level.

### Appenders

Appenders covers where the logs should be published, for example they will be printed in the console or saved as a new line in database or specific file. Unlike Loggers they are not inserted into code, but they are configurated in a config file. There are different types of the appenders, but the most popular are: *ConsoleAppender* (it prints logs in the console, like System.out…), *FileAppender* (creates new line into one or many files), *JDBCAppender* (writes new entries into the database) and *SMTPAppender* (sends emails). The whole list is available in the official documentation (link at the end of the post), but there is also possibility to make own Appender based on abstract class *AppenderSkeleton*.

The nice feature of all Appenders is that a single Logger can be connected to multiple appenders, which means that based on one event we can make several actions, for example both saving entries into database and append correct file.

The default Appender class is *ConsoleAppender*.

### Layouts

This kind of objects are responsible for editing the layout of published logs, how it will be formatted. For example *HTMLLayou*t will produce the HTML table, *PatternLayout* will structure the output string (it is the most common Layout, so I will talk more about in next paragraph), *JSONLayout* and *XMLLayout will create *JSON and XML response respectively.

Most commonly used is PatternLayout, which I also will use in my project. For such we need to define the template of the respond. To do that we can use some predefine conversion specifiers. Such specifier contains the precentage sign (*%*) with following character or short text and can represent information like date (when log was created — *%d*), message (that was added in code — *%m*), location (where in the code log was created — *%l*) and much more. So when I set up this pattern **[%p] %c — %m — Date: %d %n **and after calling it from the code you will get below input:

    loger.debug("Hello World!")

    
    //the respond on the console

    [DEBUG] root - Hello world - Date: 2018-03-21 18:13:28,149

Except for default specifiers there is possibility to customize your own, so more information will be included in the printed logs. To achieve it you need to use the *%X{key}* specifier, where the key will be a short String. In the Java code value of specific key must be added to the *ThreadContex*t object so it will be availble to be printed, here is an example:

<iframe src="https://medium.com/media/0828ee750da32fc900e49ec5861a48e3" frameborder=0></iframe>

With a pattern **%d | %m: %X{username}** the outcome will be:

    2018-03-21 18:13:28,149 | New user: donkey_kong

<iframe src="https://medium.com/media/75e580a46a2ed92a508236fc3142971e" frameborder=0></iframe>

Ok, that was long. But here is my step by step adding it to my project.

## Setting up Log4j2 into Library Portal

### Step 1. Create table in MySQL database

As I mentioned before my goal was to add log entry whenever user record is created or modified. Here I will show only one scenario, when new one is created, but other ones can be done with similar approach.

So first I’ve created the MySQL ‘*user_logs’* table using below insert. Don’t bother the contraint part of the query. I’ve added acknowledge database that the *username* field is a foreign key, that is in the ‘*user’* table.

<iframe src="https://medium.com/media/3947a9402faaea8e9115ada2521e477e" frameborder=0></iframe>

![‘user_logs’ table has a username constraint with ‘user’ table](https://cdn-images-1.medium.com/max/2000/1*veV4-Mkm6NPuIkrBbCiinQ.jpeg)*‘user_logs’ table has a username constraint with ‘user’ table*

### Step 2. Add dependecies to build.gradle into the project

Once I had had a table set up I went back to the project. First I needed to add external libraries, so I’ve added these lines into **build.gradle** file and refreshed the project.

<iframe src="https://medium.com/media/a2df8dc97c6102d3cdf00b9f0628c119" frameborder=0></iframe>

### Step 3. Create ConnectionFactory class

Logging into database has one specific step to be performed. It requires the class that has a method that returns *Connection.class*. So to achieve it I’ve created this class with connection parameters.

<iframe src="https://medium.com/media/df63705f8890afbb8107762d5593fea4" frameborder=0></iframe>

### Step 4. Configure Log4j2 using XML file

Log4j2 can be configurated in many ways. I could be done via XML, properties file, JSON or YAML. I’ve decided to do it with XML and here is the code snipped.

<iframe src="https://medium.com/media/bfa3cab36c957963afb40b4d91eb9189" frameborder=0></iframe>

Let me explain how it was done. Config file contains two parts *<Appenders> *and *<Loggers>*. In first one there is a list of Appenders that contains a *ConsoleAppender* and *JDBCAppender*. First one is for printing the information on the console, the latter is to write it into database. This appender requires a ConnectionFactory parameter to be defined (it is a class that was created in a previous step) and database column mapping to the parameters from the Logger. Also it is worth mentioned that argument *tableName* in *JDBC* clause is mandatory and must be the same as the name of the table in the database.

Next part is the list of Loggers. I’ve defined two of them. First one, *root*, which is mandatory and second one, *userLoggerDB*, that I will use for logging changes in the people’s profiles. Logger requires at least one Appender to be linked with. In my application userLoggerDB is connected to *consoleAppender* and *userAppenderDB*, so during creating a log entry two action will be performed — printing info on the console and creating new entry in database.

Oh, and it is really important to stick to the name convention of the xml file — so *log4j2.xml* is the best choice. And it is located here:

    src/main/resources/log4j2.xml

### Step 5. Use Logger in Service class

At last I can add logging code into the method. Here is the snipped from the service class:

<iframe src="https://medium.com/media/9287f5fbfcb1ba15a1486b7df3157d8e" frameborder=0></iframe>

The syntax is pretty straightforward. To get the Logger I use private **Logger userLogger = LogManager.getLogger(“userLoggerDB”)**, where ‘*userLoggerDB*’ is the name of the Logger that was provided in the XML file. Then whenether I want to create log I just use **userLogger.info(“New user”). **In my project I am using also *ThreadContext* to store more information of the user, like his/her username and other staff to be 100% sure which user was created. Also at the end I clean all the additional info from *ThreadContext*.

And that’s it! The only thing that has left was to test it and then add logging feature in other parts of the code (like for updating some field), but it can be done similar to the above case so I will skipp it for this post.

After creating new user in the Library Portal I’ve got these two information.

![Both outputs from console and the database.](https://cdn-images-1.medium.com/max/2000/1*SgzM074aK-p1G2YCmA5zqw.jpeg)*Both outputs from console and the database.*

The whole code can be find here.
[**wkrzywiec/Library-Spring**
*Library-Spring - The library website where you can borrow books.*github.com](https://github.com/wkrzywiec/Library-Spring/tree/83ed44cad514e74010f6d35b69e79d948b6e3d01)

If you are looking more posts related to my Library Portal project, please go to this entry, where there is a list of all of them.
[**Library Portal — Spring Project Overview**
*Hi Everyone!*medium.com](https://medium.com/@wojciechkrzywiec/library-portal-spring-project-overview-ddbf910dcb95)

## References

Here are some sources, which I found usefull for this topic:
[**Log4j - Overview - Apache Log4j 2**
*Log4j 2 is designed to be usable as an audit logging framework. Both Log4j 1.x and Logback will lose events while…*logging.apache.org](https://logging.apache.org/log4j/2.x/manual/index.html)
[**log4j Tutorial**
*log4j Tutorial for Beginners - Learn log4j in simple and easy steps starting from basic to advanced concepts with…*www.tutorialspoint.com](https://www.tutorialspoint.com/log4j/index.htm)
[**Effective logging with Log4J**
*Sooner or later every Java programmer realizes that using System.out.print is neither effective nor efficient way of…*www.javaexpress.pl](http://www.javaexpress.pl/article/show/Log4j__czyli_jak_skutecznie_tworzyc_logi_w_aplikacjach_javowych?lang=en)
[**Log4J2: How It Works and How to Get the Most Out Of It**
*Log4j2 is the updated version of the popular and influential log4j library, used extensively throughout the Java…*stackify.com](https://stackify.com/log4j2-java/)
[**Java Logging with Mapped Diagnostic Context (MDC) | Baeldung**
*In this article, we will explore the use of Mapped Diagnostic Context (MDC) to improve the application logging. The…*www.baeldung.com](http://www.baeldung.com/mdc-in-log4j-2-logback)
