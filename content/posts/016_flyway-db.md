
# How to deploy web app and database in one click with Flyway (on Tomcat server)
> Source: https://wkrzywiec.medium.com/how-to-deploy-web-app-and-database-in-one-click-with-flyway-on-tomcat-server-26b580e09e38

I’ve came to this situations many times. Before deploying my Spring MVC application (for testing) on Tomcat server I need to make some changes in the database that is connected to it. It requires few steps to perform (like open database visual tool, execute the script etc.). Right now it might sound silly, but if do it several times per day it would be better to automate, so my app and database are deployed simultaneously with one click.

![“person using phone leaning on wall in silhouette photography” by [Warren Wong](https://unsplash.com/@wflwong?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/12000/0*achPuTVTpPZO5-Ie)*“person using phone leaning on wall in silhouette photography” by [Warren Wong](https://unsplash.com/@wflwong?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

In this blog post I would like to introduce to you how I’ve manged to establish this idea.

To express what I want to achieve let me describe my development routine. In my project, Library Portal, I cover all the tasks — creating database, backend and frontend of the application. So whenever I want to test my app I need to deploy it on a web server. Sometimes this task requires also database modification that must be done in a database visual design tool (like MySQL Workbench). This approach is ok, but I really want to work only in one tool and that will be Eclipse (Java IDE).

Therefore I need to somehow integrate app IDE with database IDE so all the work could be done in only one of them. Luckily it can be achieved with Flyway framework, which could be added to Gradle build task list.

Moreover, thanks to Flyway, we can establish almost one-step-deployment process of web application. So when we share our project, e.g. on Github, we don’t need to prepare lenghty instructions how to run it.

Without further ado let me show you how it can be achieved.

### Create user and database in MySQL Workbench

Before we can move to Eclispe, we need to first create the user and the database (schema). For this go to [MySQL Workbench](https://www.mysql.com/products/workbench/) and login to it as a *root* user.

![](https://cdn-images-1.medium.com/max/2000/1*e1kNGhx8IibWzl68UhPlgQ.png)

Then we need run following script. Unfortunately this step is necessary to be done outside the Flyway script, but it will be done only once, so after that you won’t need to use it.

<iframe src="https://medium.com/media/c325e404662dd8a24351a4e02cff71f6" frameborder=0></iframe>

In first two lines we create a user for our app and grants ‘him’ all privileges. Next we sets Scheduler to be on (in the migration script there are some events that are scheduled).

**Notice, **that there is no need to create a schema here, Flyway will do it for us.

### Add dependencies to build.gradle

First we need to add Flyway dependencies and also define flyway section in the build.gradle. **NOTE** that for simplicity reason I didn’t provide all required dependencies (e.g. for Tomcat, Spring, etc), all of them could be found in a final project (link at the end of the post).

<iframe src="https://medium.com/media/5ff6aa336ae7e566b22b47604b06c9db" frameborder=0></iframe>

Flyway requires two things to be added: plugin (line 1) and buildscript dependency (line 10).

Next, within flyway* *brackets, we need to define connection properties, like type of database (in our case MySQL), URL, user with password and a schema name (they have been created in a first step). And that’s basic configuration that I want to establish. You can also tune other properties like change location of a migration script, set up migration script file prefix etc. All the options are available [here](https://flywaydb.org/documentation/gradle/migrate).

The last part of the build.gradle is related to Tomcat server deployment. In short, I want to deploy the project and migrate database with one click. To do that we need to define tomcat connection properties. The last line tells Gradle that before running tomcatRun task (i.e. deploying the app) we want to run flywayMigratetask execute SQL script (if necessary).

### Add SQL scripts to the project

In order to create database tables we need to prepare SQL scripts, like the following:

<iframe src="https://medium.com/media/71ee998f733fe556623f760556b4ac69" frameborder=0></iframe>

As it was already mentioned, migration takes place during flywayMigrate task is executed. It scannes the project for the particular location (by default it’s src/main/resources/db/migration) and executes file that has matches specific [naming convention](https://flywaydb.org/documentation/migrations#naming).

By default, migration file needs to match following pattern:

![](https://cdn-images-1.medium.com/max/2000/1*6SnBZK0C6abOwxj3vqVKoQ.png)

* **Prefix — **(default V ) all the files must start with it, otherwise they will be skipped (this prefix could be change).

* **Version —** indicates version number of the migration file. First file would be *1, *next 2 and so on. It’s really important to provide it because based on it Flyway will know if changes were made in the script.

* **Separator —** (default __ — two underscores), this is could be also configured.

* **Description —** it’s a simple name of migration file.

* **Suffix — (**.sql) indicates type of the file.

So in our case the migration file will be V1__library.sql.

### Run tomcatRun Gradle task

And that’s it! We only need to run tomcatRun task to perform both app deployment on Tomcat web server and database migration.

If you don’t know how to assign this task to Run button in Eclipse, [check my other blog post](https://medium.com/@wkrzywiec/setting-up-gradle-spring-project-in-eclipse-on-tomcat-server-77d68454fd8d#c527).

![](https://cdn-images-1.medium.com/max/2000/1*McAdoEi3_zq3w_s2y-k9DA.png)

### New database version

Once we’re done with our first migration we could perform next one :). So let’s suppose that we want to add a new table (user) and to update the old one (book). Therefore we need to create a new file, *V2__library.sql*.

<iframe src="https://medium.com/media/819c49ed82082a0a803af6c8f2f1843d" frameborder=0></iframe>

Once we execute above script the database is updated and we have now two tables.

Last thing that is worth mentioned is that Flyway is logging each migration in the flyway_schema_history table (where it was succesful of not). This table is automatically created during first run.

![](https://cdn-images-1.medium.com/max/2000/1*7ncRcAzUelQwCQYWBSEMSg.png)

Code of my whole project, Library Portal, can be found here:
[**wkrzywiec/Library-Spring**
*The library website where you can borrow books. Contribute to wkrzywiec/Library-Spring development by creating an…*github.com](https://github.com/wkrzywiec/Library-Spring)

## References
[**Flyway by Boxfuse * Database Migrations Made Easy.**
*Supported databases are Oracle, SQL Server (including Amazon RDS and Azure SQL Database, DB2, MySQL (including Amazon…*flywaydb.org](https://flywaydb.org/documentation/)
[**Flyway by Boxfuse * Database Migrations Made Easy.**
*The Flyway Community Edition and Flyway Pro Edition Gradle plugin support Gradle 3.x and Gradle 4.x running on Java 8…*flywaydb.org](https://flywaydb.org/documentation/gradle/)
[**Flyway, Gradle, Oracle JDBC**
*I'm writing this blog post to hopefully help out some poor soul who is trying to automate their Oracle database…*www.dennis-stepp.com](https://www.dennis-stepp.com/post/flywaygradle/)
