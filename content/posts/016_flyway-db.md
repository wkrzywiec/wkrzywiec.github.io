---
title: "How to deploy web app and database in one click with Flyway (on Tomcat server)"
date: 2018-09-12
summary: "Database migration with Flyway"
description: "I’ve came to this situations many times. Before deploying my Spring MVC application (for testing) on Tomcat server I need to make some changes in the database that is connected to it. It requires few steps to perform (like open database visual tool, execute the script etc.). Right now it might sound silly, but if do it several times per day it would be better to automate, so my app and database are deployed simultaneously with one click."
tags: ["java", "spring", "database", "flyway", "library-project"]
canonicalUrl: "https://wkrzywiec.medium.com/how-to-deploy-web-app-and-database-in-one-click-with-flyway-on-tomcat-server-26b580e09e38"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/how-to-deploy-web-app-and-database-in-one-click-with-flyway-on-tomcat-server-26b580e09e38).
{{< /alert >}}

![“person using phone leaning on wall in silhouette photography” by [Warren Wong](https://unsplash.com/@wflwong?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/12000/0*achPuTVTpPZO5-Ie)*Photo by [Warren Wong](https://unsplash.com/@wflwong?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*I’ve came to this situations many times. Before deploying my Spring MVC application (for testing) on Tomcat server I need to make some changes in the database that is connected to it. It requires few steps to perform (like open database visual tool, execute the script etc.). Right now it might sound silly, but if do it several times per day it would be better to automate, so my app and database are deployed simultaneously with one click.*

In this blog post I would like to introduce to you how I’ve managed to establish this idea.

To express what I want to achieve let me describe my development routine. In my project, Library Portal, I cover all the tasks — creating database, backend and frontend of the application. So whenever I want to test my app I need to deploy it on a web server. Sometimes this task requires also database modification that must be done in a database visual design tool (like MySQL Workbench). This approach is ok, but I really want to work only in one tool and that will be Eclipse (Java IDE).

Therefore I need to somehow integrate app IDE with database IDE so all the work could be done in only one of them. Luckily it can be achieved with Flyway framework, which could be added to Gradle build task list.

Moreover, thanks to Flyway, we can establish almost one-step-deployment process of web application. So when we share our project, e.g. on Github, we don’t need to prepare lenghty instructions how to run it.

Without further ado let me show you how it can be achieved.

## Create user and database in MySQL Workbench

Before we can move to Eclispe, we need to first create the user and the database (schema). For this go to [MySQL Workbench](https://www.mysql.com/products/workbench/) and login to it as a *root* user.

![](https://cdn-images-1.medium.com/max/2000/1*e1kNGhx8IibWzl68UhPlgQ.png)

Then we need run following script. Unfortunately this step is necessary to be done outside the Flyway script, but it will be done only once, so after that you won’t need to use it.

```sql
CREATE USER 'library-spring'@'localhost' IDENTIFIED BY 'library-spring';

GRANT ALL PRIVILEGES ON  *.* TO 'library-spring'@'localhost';

SET GLOBAL EVENT_SCHEDULER = ON;
```

In first two lines we create a user for our app and grants ‘him’ all privileges. Next we sets Scheduler to be on (in the migration script there are some events that are scheduled).

**Notice**, that there is no need to create a schema here, Flyway will do it for us.

## Add dependencies to build.gradle

First we need to add Flyway dependencies and also define flyway section in the build.gradle. **NOTE** that for simplicity reason I didn’t provide all required dependencies (e.g. for Tomcat, Spring, etc), all of them could be found in a final project (link at the end of the post).

```gradle
apply plugin: 'org.flywaydb.flyway'

buildscript {
    repositories {
        jcenter()
    }

    dependencies {
        classpath 'mysql:mysql-connector-java:6.0.6'
        classpath 'org.flywaydb:flyway-gradle-plugin:5.1.4'
    }
}

dependencies {

    compile 'mysql:mysql-connector-java:6.0.6'
}

flyway {
	driver = 'com.mysql.cj.jdbc.Driver'
    url = 'jdbc:mysql://localhost:3306?autoReconnect=true&useSSL=false&useUnicode=true&useJDBCCompliantTimezoneShift=true&useLegacyDatetimeCode=false&serverTimezone=UTC'
    user = 'library-spring'
    password = 'library-spring'
    schemas = ['library_db']
}

tomcat {
	httpPort = 8080
	enableSSL = true
	contextPath = '/library-spring'
}

tomcatRun.dependsOn flywayMigrate
apply plugin: 'org.flywaydb.flyway'

buildscript {
    repositories {
        jcenter()
    }

    dependencies {
        classpath 'mysql:mysql-connector-java:6.0.6'
        classpath 'org.flywaydb:flyway-gradle-plugin:5.1.4'
    }
}

dependencies {

    compile 'mysql:mysql-connector-java:6.0.6'
}

flyway {
	driver = 'com.mysql.cj.jdbc.Driver'
    url = 'jdbc:mysql://localhost:3306?autoReconnect=true&useSSL=false&useUnicode=true&useJDBCCompliantTimezoneShift=true&useLegacyDatetimeCode=false&serverTimezone=UTC'
    user = 'library-spring'
    password = 'library-spring'
    schemas = ['library_db']
}

tomcat {
	httpPort = 8080
	enableSSL = true
	contextPath = '/library-spring'
}

tomcatRun.dependsOn flywayMigrate
```

Flyway requires two things to be added: plugin (line 1) and buildscript dependency (line 10).

Next, within flyway rackets, we need to define connection properties, like type of database (in our case MySQL), URL, user with password and a schema name (they have been created in a first step). And that’s basic configuration that I want to establish. You can also tune other properties like change location of a migration script, set up migration script file prefix etc. All the options are available [here](https://flywaydb.org/documentation/gradle/migrate).

The last part of the build.gradle is related to Tomcat server deployment. In short, I want to deploy the project and migrate database with one click. To do that we need to define tomcat connection properties. The last line tells Gradle that before running tomcatRun task (i.e. deploying the app) we want to run flywayMigratetask execute SQL script (if necessary).

## Add SQL scripts to the project

In order to create database tables we need to prepare SQL scripts, like the following:

```sql
CREATE TABLE `book` (
	`id` int(12) NOT NULL AUTO_INCREMENT,
    	`google_id` varchar(100) NOT NULL UNIQUE,
    	`title` varchar(200) NOT NULL,
    	`publisher` varchar(200) DEFAULT NULL,
    	`published_date` varchar(100) DEFAULT NULL,
    	`isbn_id` int(12) DEFAULT NULL,
    	`page_count` int(6) DEFAULT NULL,
    	`rating` real(4,1) DEFAULT NULL,
    	`image_link` varchar(1000) DEFAULT NULL,
    	`description` text DEFAULT NULL,
   
    	PRIMARY KEY (`id`),
    
    	CONSTRAINT `FK_ISBN` FOREIGN KEY (`isbn_id`)
    	REFERENCES `isbn` (`id`)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE TABLE `book` (
	`id` int(12) NOT NULL AUTO_INCREMENT,
    	`google_id` varchar(100) NOT NULL UNIQUE,
    	`title` varchar(200) NOT NULL,
    	`publisher` varchar(200) DEFAULT NULL,
    	`published_date` varchar(100) DEFAULT NULL,
    	`isbn_id` int(12) DEFAULT NULL,
    	`page_count` int(6) DEFAULT NULL,
    	`rating` real(4,1) DEFAULT NULL,
    	`image_link` varchar(1000) DEFAULT NULL,
    	`description` text DEFAULT NULL,
   
    	PRIMARY KEY (`id`),
    
    	CONSTRAINT `FK_ISBN` FOREIGN KEY (`isbn_id`)
    	REFERENCES `isbn` (`id`)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

As it was already mentioned, migration takes place during flywayMigrate task is executed. It scannes the project for the particular location (by default it’s src/main/resources/db/migration) and executes file that has matches specific [naming convention](https://flywaydb.org/documentation/migrations#naming).

By default, migration file needs to match following pattern:

![](https://cdn-images-1.medium.com/max/2000/1*6SnBZK0C6abOwxj3vqVKoQ.png)

* **Prefix** — (default V ) all the files must start with it, otherwise they will be skipped (this prefix could be change).

* **Version** — indicates version number of the migration file. First file would be *1*, next 2 and so on. It’s really important to provide it because based on it Flyway will know if changes were made in the script.

* **Separator** — (default __ — two underscores), this is could be also configured.

* **Description** — it’s a simple name of migration file.

* **Suffix** — (.sql) indicates type of the file.

So in our case the migration file will be V1__library.sql.

## Run tomcatRun Gradle task

And that’s it! We only need to run tomcatRun task to perform both app deployment on Tomcat web server and database migration.

If you don’t know how to assign this task to Run button in Eclipse, [check my other blog post](https://medium.com/@wkrzywiec/setting-up-gradle-spring-project-in-eclipse-on-tomcat-server-77d68454fd8d#c527).

![](https://cdn-images-1.medium.com/max/2000/1*McAdoEi3_zq3w_s2y-k9DA.png)

## New database version

Once we’re done with our first migration we could perform next one :). So let’s suppose that we want to add a new table (user) and to update the old one (book). Therefore we need to create a new file, *V2__library.sql*.

```sql
ALTER TABLE `book`
DROP COLUMN `rating`
;

CREATE TABLE `user` (
    `id` int(6) NOT NULL AUTO_INCREMENT,
    `username` varchar(64) NOT NULL UNIQUE,
    `password` varchar(100) NOT NULL,
    `email` varchar(60) NOT NULL UNIQUE,
    `enable` boolean NOT NULL,
    `first_name` varchar(60) DEFAULT NULL,
    `last_name` varchar(60) DEFAULT NULL,
    `phone` varchar(60) DEFAULT NULL,
    `birthday` date DEFAULT NULL,
    `address` varchar(120) DEFAULT NULL,
    `postal` varchar(60) DEFAULT NULL,
    `city` varchar(60) DEFAULT NULL,
    `record_created` timestamp DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (`id`)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

Once we execute above script the database is updated and we have now two tables.

Last thing that is worth mentioned is that Flyway is logging each migration in the flyway_schema_history table (where it was succesful of not). This table is automatically created during first run.

![](https://cdn-images-1.medium.com/max/2000/1*7ncRcAzUelQwCQYWBSEMSg.png)

Code of my whole project, Library Portal, can be found here:

[**wkrzywiec/Library-Spring** | github.com](https://github.com/wkrzywiec/Library-Spring)

## References

* [**Flyway by Boxfuse * Database Migrations Made Easy.** | flywaydb.org](https://flywaydb.org/documentation/)
* [**Flyway by Boxfuse * Database Migrations Made Easy.** | flywaydb.org](https://flywaydb.org/documentation/gradle/)
* [**Flyway, Gradle, Oracle JDBC** | dennis-stepp.com](https://www.dennis-stepp.com/post/flywaygradle/)
