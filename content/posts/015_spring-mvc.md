
# How to start with Spring MVC
> Source: https://wkrzywiec.medium.com/how-to-start-with-spring-mvc-309dec3c59fd

In this blog post I would like to introduce you to the Spring MVC framework, how it works, what are the pros and what are the possibilities it gives to us, developers. At the end I will show most of the important features in a simple project.

![“green leafed plant” by [Ash from Modern Afflatus](https://unsplash.com/@modernafflatusphotography?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/10368/0*bTMFaeE6_KP1raNf)*“green leafed plant” by [Ash from Modern Afflatus](https://unsplash.com/@modernafflatusphotography?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

## Table of content

### Overview

* [Structure](https://medium.com/p/309dec3c59fd#bc18)

* [URI pattern syntax](https://medium.com/p/309dec3c59fd#9128)

* [Return types](https://medium.com/p/309dec3c59fd#7329)

* [Arguments](https://medium.com/p/309dec3c59fd#c48b)

* [Exceptions handling](https://medium.com/p/309dec3c59fd#6198)

### Writting code

* [Create Gradle project in the Eclipse](https://medium.com/p/309dec3c59fd#49fc)

* [Add dependencies to build.gradle](https://medium.com/p/309dec3c59fd#84c1)

* [Spring MVC configuration](https://medium.com/p/309dec3c59fd#a35a)

* [Prepare simple view](https://medium.com/p/309dec3c59fd#f8b0)

* [Create Spring Controller](https://medium.com/p/309dec3c59fd#2d6e)

* [Testing](https://medium.com/p/309dec3c59fd#6497)

* [Add more features](https://medium.com/p/309dec3c59fd#7348)

As you might guess it already, Spring MVC implements very common architecture pattern — *Model-View-Controller*. Its key concept is to organize entire application into three modules. **View **is responsible for User Interface, which in our case will be HTML page (or more specific JSP file). **Controller** is taking care of HTTP requests and delegates tasks (e.g. fetching data from database) to other components. And finally a **Model, **it structurises the data and represents business logic of an application. More information, presented in a funny way, about MVC pattern could be found [here](https://medium.freecodecamp.org/model-view-controller-mvc-explained-through-ordering-drinks-at-the-bar-efcba6255053).

In Spring MVC View is represented by JSP files, the Controller by the class with special annotation and the Model are Beans. In this post I would like to concentrate on a key part of this framework — Controller.

Before I jump to talk over the Controller class first I would need to explain how it really works under the hood. I don’t want to go much into details how it really works, because I want to keep it simple and that’s not aim of my post. But if you are interested in more in-depth explanation (with information about DispatacherServlet etc.) I would recommend this article [***How Spring Web MVC Really Works](https://stackify.com/spring-mvc/?utm_referrer=https%3A%2F%2Fmedium.com%2Fr%2F%3Furl%3Dhttps%253A%252F%252Fstackify.com%252Fspring-mvc%252F)***.

In short, Spring MVC app works with a servlet thats receives HTTP requests and process it. In Spring MVC world it is called DispatcherServlet and it facilitate request mapping to certain methods from Controller class to process certain tasks (like connecting to the database, process forms, etc.).

If it is not clear, don’t worry. I’ll explain it on following examples.

NOTE: In a following section I’ll show few examples of the Controller. To keep it simple I avoid configuration steps, these could be found at the end of the post, where I present all the steps necessary to set up Spring MVC project.

### Structure

First thing first, **how Controller looks like? **It’s a really simple Java class with specific notifications and declaration rules regarding public methods (i.e. their return type and arguments). Below there is a code of a single method class that acts as a Controller.

<iframe src="https://medium.com/media/9236efb44d09e769be7238e1cf7d4c9c" frameborder=0></iframe>

First, you see a@Controller annotation that lets Spring know that this class will be the controller. Next, in the body of class there is a single method named “showHome()”. It’s annotated with @GetMapping which means that it will be called when a servlet receives a GET request (type of HTTP request) that matches pattern “basicURI/home”. If you run your servlet on a local machine it probably looks as follows “http://localhost:8080**/home**” or if you run it on your server with bought domain “http://your-awsome-page.com**/home**”.

Accordingly, if you want to map any other type of HTTP request just use one of the followings: @PostMapping, @PutMapping, @DeleteMapping, @PatchMapping.

Finally, above method has a simple String as a return value, which indicates what JSP file to send to the requestor. In our case it will be *home.jsp* file which is included in the project (more information about how to set up will be described in next sections).

And that’s it! Controller class structure is really simple and the whole process of defining each method could be sum up to following steps:

1. Create public method

1. Add HTTP request mapping to this method

1. Add arguments to the method (if necessary)

1. Write method body

### URI pattern syntax

First things first, we need to to map HTTP requests to the methods in the Controller class. Under the hood, when a Spring MVC app receives a request it is handled by the *DispatcherServlet *which delegates them to according handler, which will be Controller class.

Sometimes those requests are rather simple, like as it’s in above code snippet. Whole request path is static, which means that in order to call this method we need to provide this exact path. What if we would like to make it more dynamic? For example we’ve got bunch of similar URIs that should be mapped to one method.

To achieve that we can add ***?*** sign to the annotation path*** ***like:

    @GetMapping("/book?")

Above we tell Spring that each URI that ends with “/book” + any other single sign should be processed by this method. So if it ends with “/*book1”, “/book^” *or whatever it will be handled by this.

Sometimes we want to match more than one character and for that we can use * or ** wildcard. First one matches all the characters within path segment (between two “/”), the latter can match multiple segments. To illustrate this see below examples:

    @GetMapping("/book*")

    @GetMapping("/book**")

First mapping will match the URI “/bookGameOfThrones” and second one will match “/book/GameOfThrones”.

Ok, but what if I would like to get information from the URI? It could contains the name or id of the book that we want to fetch. How to solve it? Very easily, by using either @PathVariable or @RequestParam annotation.

**@PathVariable — **some segments of the URI can be dynamize, for example if we want to get *bookId*=348 and *authorId*=2 from the path “*baseURI/book/348/author/2*” the mapping will look like this:

<iframe src="https://medium.com/media/49515a38c367c115dc1ff06ecf72d40e" frameborder=0></iframe>

Both Ids are stored in their variables and can be used in the method’s body. Please notice that dynamic part of the URI must be surrounded with curly brackets *“{}” *in the mapping and this part should has the same name as the argument of the annotation.

**@RequestParam** — another way to pass some information thru URI is by request parameter. You’ve probably see it in lots of them. For example, link “[https://www.youtube.com/watch?v=s7L2PVdrb_8&t=10s](https://www.youtube.com/watch?v=s7L2PVdrb_8&t=10s)” is made of two pieces. First is regular “https://www.youtube.com/watch”, which is static, and a second “[v=s7L2PVdrb_8&t=10s](https://www.youtube.com/watch?v=s7L2PVdrb_8&t=10s)”, which is dynamic and has two arguments: ***v*** — it’s video Id and ***t***-it’s a second when the video should starts. Both pieces are separated with ***?*** sign and arguments are separated with ***&*** character.

If we wanted to get the *bookId* and *authorId*, as it was in the previous example, but this time using @RequestParam annotation the URI could look like this “*/book?id=348&author=2*”, so the mapping:

<iframe src="https://medium.com/media/07a818ea07db959a03711258d0a93220" frameborder=0></iframe>

Notice that *author* request parameter is not required so mapped argument, *authorId*, might be null.

And the last thing, in all above examples arguments are Long type, but they can be also String or Integer.

### Return types

Once the mapping is set up we need to assign what resource our web app will return. In our case it will be some sort of data bundle that contains HTML, CSS, JS files or data model objects, which in WWW world is called HTTP Response. It contains three parts: Status-Line (basically protocol version), Response Header (includes server info and [Status code](https://httpstatuses.com/), like famous ‘404 Not found Error’) and Response Body.

Depending on how much into detail we would like to go there are several return types that Controller method can have.

**String** — this is the simplest case. By typing the JSP file name in return statement we can indicate which one we want to send. In other words it works the best when we don’t need to attach any model object into the HTTP response (it’s not 100% true because we can do that by adding special argument to the Controller method).

<iframe src="https://medium.com/media/9236efb44d09e769be7238e1cf7d4c9c" frameborder=0></iframe>

In above example I provide simple “home” String, which means that as a Response I want to send a *home.jsp* file that is located somewhere in my project. How to configure Spring so by typing only the ‘main’ part of the file path we can get it? Please check [here](https://medium.com/p/309dec3c59fd#a35a).

**ModelAndView — **as the name suggest it’s holding two types of objects: Model and View. First one, is some sort of container that holds information that will be displayed as a View (JSP file). Second is a model that wraps some information that can be used by a View. In other words View acts as a template and a Model populate it with a data (e.g. fetched from the database).

<iframe src="https://medium.com/media/1f48d84b547f632a3d529751cbab5986" frameborder=0></iframe>

In above code snippet, the View is set up to “home” (works similar to previous example) and the Model contains one key-value pair. First argument, “message”, is a key and the second is a value. Here its value is a String object, but it can any class that you want (for example book model that holds data about the book, like author, title, page count, etc.).

You might wonder how JSP file enters the data stored in the Model class? The answer to that is: using [JSP Expression Language](https://www.journaldev.com/2064/jsp-expression-language-el-example-tutorial).

And that’s the basics. If you look into the [Spring docs](https://docs.spring.io/spring/docs/current/spring-framework-reference/web.html#mvc-ann-return-types) you’ve probably see other types, like ***HttpEntity*** (to enable respond header modification), ***RxJava*** Observable (for asynchronous request processing) or ***model class annotated with @RespondBody*** (method with this annotation will return XML/JSON or other representation of the object). The last one is used chiefly for building REST API apps (e.g. for microservices) and I’ll cover it in one of my next post, when I’ll create API for Library Portal.

### Arguments

Another thing that you might want to add to controllers methods are arguments. They allow to enter objects that are part of the HTTP request, like the model, request parameters, form validator etc. Most of them could be done in other way. For example, if you want to enter the model, you better set a return type of a model as a ModelAndView not a String, which will result in fewer number of parameters in the method.

In this part I skipped those that I’ve already mentioned — @PathVariable and @RequestParam.

**Model — **key role of the Model in HTTP Response is to provide data that can be used for rendering a view. In other words it a view (JSP file) takes some data from it and insert into its body. Data are usually fetched from the database using a service object, like it is shown below.

<iframe src="https://medium.com/media/54d0eccc505f91ea6bf892ac34b2eb63" frameborder=0></iframe>

**ModelMap — **this one is similar to previous one. It has all functionality that *Model* has but also it allows to add request parameter to the output request. It is worth notice that *ModelMap *is actually an implementation of the *Model* interface, which is the reason of their similarities.

It might be useful when the user provide only partial URL, but the website requires some parameters. Therefore we can add default value using *put(key,value)* method. Like in the following example, list of all books is sorted descending by default.

<iframe src="https://medium.com/media/a902621dee8a7a40c7c86deb03109208" frameborder=0></iframe>

**@ModelAttribute — **is used to bind the object from the HTTP Request Model to the argument in the method. Chiefly it is used while processing form. For example, when registering new user we need to get the User object to retrieve data that were input.

<iframe src="https://medium.com/media/db4c653cee7e9cc19036eae0aac1bfc3" frameborder=0></iframe>

**BindingResult **— it is tightly connected with previous one and together with @Valid annotation is used for form detecting errors in a form (to be precise, object attached to the request). Thanks to that we can easily check if the form contains any error.

Also it is worth notice that this parameter needs to be right after the object that is validated.

<iframe src="https://medium.com/media/7ffecff12a546ae7f0fe319889da6c9c" frameborder=0></iframe>

**RedirectAttributes — **sometimes we need to redirect HTTP request from one method to another method. To do so we can need to need add *“redirect:”* prefix followed by the request URL. If we want to redirect to a simple method, that’s fine. The problem begins when we want send also request parameters (attributes) to the next method. And therefore we’ve got RedirectAttributes object into which we can pass attributes that will be processed by target method.

<iframe src="https://medium.com/media/5d9ce8ee95978ea87ac8f588f7c490f3" frameborder=0></iframe>

Above code shows an example of such redirection. First method focus mainly on adding new book do the database (data are taken from Google Book API) and then it is redirected to the more general method that presents book detailed page.

**@CookieValue — **in some cases we want to enter HTTP cookies that are included in the request. To access it just add this annotation to the argument (usually it will be String or numeric) which will be binded to cookie with specified name. In the following example a value of cookie with a name *“session”* is stored in a* sessionKey* String variable and then printed in the console.

<iframe src="https://medium.com/media/4723706afd588980971b31ec85ac12c0" frameborder=0></iframe>

**HttpServlerResponse — **this is one allows to enter the whole response that will be send, so you are able to modify almost everything, like the header, cookie, attached objects and more.

### Exceptions handling

Another good thing that Spring MVC provides is error handling. Imagine that for some reason user has provided incorrect path, or maybe she/he bump into a bug in your procedures and get whole stack trace, which might not be the best thing to show to the customer. Instead we can gracefully redirect to better looking error page.

To achieve it basically we can choose one of two approaches. In a first one, we can add error handling methods into particular Controller class. The main disadvantage of this solution is when we have multiple Controllers in the project we need to multiple those methods in each one of them. To overcome this problem we can create custom error handling object that will take care it globally.

If our project is rather small, we could do without making separate error handling class. Therefore we need to add **@ExceptionHandler** annotation to the particular method.

<iframe src="https://medium.com/media/0b1c101ceadafe6b782d0530b5b50e1b" frameborder=0></iframe>

While the project become bigger and bigger it might be a good idea to split one main Controller into few smaller ones based on the concern. Together with that we would also need to create one global object that handles all the errors. In order to do that we need to create new class that is annotated with **@ControllerAdvice**. And the good thing about it is that works similar to Spring Controller (same return types, etc.).

<iframe src="https://medium.com/media/58dd55efd882c8e4efc33ddd70914783" frameborder=0></iframe>

Above example shows how to handle two types of errors. First, popular NullPointerException, returns 500 HTTP Status and second returns status 404. The main difference between those two is that in a latter I’ve added new annotation — **@ResponseStatus**. Using that we manually set a response status in the response header. In above case it is set up to 404, because without it the web browser would receive 200 (OK) status, because it was handled by ControllerAdvice class.

And that’s it. All the basics were covered so let’s move to implementation of a simple example.

## Writting code

### Create Gradle project in the Eclipse

First we need to create a new Gradle project. In Eclipse (in my case, Oxygen version) go to **File->New->Project…** and from the wizard select **Gradle**. In a following screens keep all as defaults, in one of them provide project name.

### Add dependencies to build.gradle

Once the project is created we need to download some libraries. Except for obvious one, Spring MVC, I’ve decided to use a [Gradle-Tomcat plugin](https://github.com/bmuschko/gradle-tomcat-plugin) that allows to rapid deployment of the application on the Tomcat server. Moreover, [Eclipse-WTP](https://docs.gradle.org/current/userguide/eclipse_plugin.html) plugin was added to tell Gradle that we work in Eclipse.

<iframe src="https://medium.com/media/63f4fe5a2d2c80c3e1e986315711cd3c" frameborder=0></iframe>

Finally refresh project by right-clicking on it’s name then **Gradle->Refresh Gradle Project**, so new libraries will be downloaded.

### Spring MVC configuration

I know what you say. Why don’t you use Spring Boot for this task? Instead of few clicks you bother to get it done in a hard way. The answer to that is because I would like to go thru this standard way, like it was days before Spring Boot.

Therefore, create a new package, let’s call it config, an in it create simple Java class — AppConfig.

<iframe src="https://medium.com/media/714a179bb028544dda1d01a4249db39f" frameborder=0></iframe>

@Configuration and @ComponentScan annotations are telling Spring context that it is a config class and where to scan for beans respectivaley. More intresting are @EnableWebMvc annotation with WebMvcConfigurer interface implementation that enables Spring MVC features in our project.

Finally above config class contains one method for setting *ViewResolver* properties. In it, we provide prefix and sufix of a view name. So from now on, in Controller class you don’t need to provide full name of the view, just significant part of it. So instead of *“/WEB-INF/views/**home**.jsp” *we can provide short *“**home**” *and* ViewResolver *will know which JSP file to look for.

<iframe src="https://medium.com/media/27c8e8deb56cde7cddf806ddaa84f5fb" frameborder=0></iframe>

Another class that we need to add is that extends *DispatcherServletInitializer, *which replaces mandatory web.xml file in the project and makes it totaly XML-free.

### **Prepare simple view**

After configuration we can focus on a fun part — views and controller. Therefore we create first, simple JSP file in Eclipse, which will look like follows.

<iframe src="https://medium.com/media/32ccb5cdaa1bacb5cfbf621244fe1e74" frameborder=0></iframe>

A file should be located in a directory:* src/main/webapp/WEB-INF/views/.*

### Create Spring Controller

Finally we need to create new package, called controller, and add new class. For now it will contains only one method for the URL *http://localhost:8080/simple-spring-mvc/.*

<iframe src="https://medium.com/media/a87a58c705164326e6cdcda10a0f8acc" frameborder=0></iframe>

Note: If you don’t know where the base URL is defined check the Gradle file for Tomcat configuration.

### Testing

To run it we need first we need to run a specific Gradle task called* tomcatTun. *To make it as easy as it could be go to ***Run/Run Configurations…, ***click **New** icon and enter following inputs:

* Name: *Simple Spring MVC — run*

* Gradle Task: *tomcatRun*

* Working Directory: *${workspace_loc:/*spring-mvc-simple*}*

![](https://cdn-images-1.medium.com/max/2052/1*-xj_8_DoNMWaeHFmgl2Zxg.png)

We have now easy access to the task which can be started using **Run** button in Eclipse. Once you run this task and wait for all init jobs to be finished you can type URL *http://localhost:8080/simple-spring-mvc/ *in the browser and get following page:

![](https://cdn-images-1.medium.com/max/2000/1*HVdXMWn4SeX1qFR5rtcNcg.png)

### Add more features

Ok we now that everything is working so let’s make it more complex/cooler. I would like to implement some of the features that were menationed in the article.

**@PathVariable**

Let’s make a new Controller method that will map URL [*http://localhost:8080/simple-spring-mvc/](http://localhost:8080/simple-spring-mvc/.)meme/{name} *which will direct us to a website that has certain meme depending on the name in the last part of URL. Therefore first we need to create 3 new views, one of them is:

<iframe src="https://medium.com/media/6a5e39034c1d8dc168bc2c57855f2cf5" frameborder=0></iframe>

Some of the lines requires some exaplanation. In 3 line we add new library to allow [JSTL](https://www.tutorialspoint.com/jsp/jsp_standard_tag_library.htm) features.

Next, in line 12 there is a link to the home page, which is dynamic, so if we change our base URL (for example when we want to move the app from local to the server, we’ll don’t need to update all views). In our case it’s just telling to go to the [*http://localhost:8080/simple-spring-mvc/.](http://localhost:8080/simple-spring-mvc/.)*

Finally, in 16 line there is an image file path. To be able to use it first we need to do two things. First we need to add one method to AppConfig class that will map resource folder.

<iframe src="https://medium.com/media/a66a982b9c0e21284aa7c4df37c4f983" frameborder=0></iframe>

Second we need to add images to the project to a folder *src/main/webapp/resources/img.*

Finally we need to add method to Controller class.

<iframe src="https://medium.com/media/31497dbd140ffd67ea4d696595178a06" frameborder=0></iframe>

Here is the sample of one of these pages:

![](https://cdn-images-1.medium.com/max/2000/1*m1U6a_VIzWS-94EGolQInA.png)

**@RequestParam & Model**

Moving forward, I’d like to add a box where we can input our name, than submit it so our name will appear in the URL and on the website.

So first we need to create two views — one for a form and another for a result.

<iframe src="https://medium.com/media/b150487b3a2a197ffba953e2b54ba85e" frameborder=0></iframe>

Above is presented code of a form. The most important tag is <form> which wraps two inputs, one for a text box and another for submit button. This tag also have two attributes — action and method. First one indicates the URL of the result page (which will be *baseURL/processNameForm*) and second is telling what HTTP request to use.

<iframe src="https://medium.com/media/b8194090709bc30d6a543e7d0bdd645b" frameborder=0></iframe>

HTML code of result page is shown above. Here, we will print the exact value of a request parameter with a name *“name” *that was passed using form on a previous page. Also we’ll get an attribute from the Model attached to the request — *“upperName”, *which you might already guess it, will be written using upper case letters. This attribute will be added from the Controller class.

<iframe src="https://medium.com/media/9be4cb68696fa158e668faa6f2c777a6" frameborder=0></iframe>

It contains two methods, one for each page. When we run the project we get

![Page where you provide your name.](https://cdn-images-1.medium.com/max/2000/1*jR3Ao1Cz77fioSroFrrH_g.png)*Page where you provide your name.*

![The URL after submitting the form.](https://cdn-images-1.medium.com/max/2000/1*WoXxlOFG0QfdR_sxTnsJzA.png)*The URL after submitting the form.*

![Page content after processing the form.](https://cdn-images-1.medium.com/max/2000/1*0xTzBJLo_QDceh45PAYtyA.png)*Page content after processing the form.*

**@ExceptionHandler and ModelAndView**

Last thing that I want to test is handling very popular Exception — NullPointerException. I want to redirect user to the error page and also print the exception stack trace in the console. Therefore we need to add following method to the Controller.

<iframe src="https://medium.com/media/ea0b2a73af448542b0199d73f764f2cf" frameborder=0></iframe>

This time we use ModelAndView class to pass the view name and add an attribute that is required by the JSP file.

<iframe src="https://medium.com/media/6400d3e50cfaac969600c730ebc89885" frameborder=0></iframe>

Finally to test it we need to add button to the home page (with links to other features mentioned in this section).

<iframe src="https://medium.com/media/897fdb6e05b3902fd670c93a43903b76" frameborder=0></iframe>

And finally, we need to map the request that will throw NullPointerException.

<iframe src="https://medium.com/media/6bb471bc534ac6ff19aecc59dd923dd5" frameborder=0></iframe>

All these features are now availbale from the main page.

![](https://cdn-images-1.medium.com/max/2000/1*Q0GKJfu3DptCT7S9efGFag.png)

After clicking the last one we get an error page:

![](https://cdn-images-1.medium.com/max/2000/1*sq7UAlSY1nRYkrHTPBSwcw.png)

Whole project can be found here:
[**wkrzywiec/Simple-Spring-MVC**
*Contribute to wkrzywiec/Simple-Spring-MVC development by creating an account on GitHub.*github.com](https://github.com/wkrzywiec/Simple-Spring-MVC)

## References
[**How Spring MVC Really Works**
*Throughout this article, we'll use the latest and greatest Spring Framework 5. We're focusing here on the Spring's…*stackify.com](https://stackify.com/spring-mvc/)
[**Quick Guide to Spring Controllers | Baeldung**
*In this article we'll focus on a core concept in Spring MVC - Controllers. Let's start by taking a step back and having…*www.baeldung.com](https://www.baeldung.com/spring-controllers)
[**Web on Servlet Stack**
*This part of the documentation covers support for Servlet stack, web applications built on the Servlet API and deployed…*docs.spring.io](https://docs.spring.io/spring/docs/current/spring-framework-reference/web.html#spring-web)
[**14 Tips for Writing Spring MVC Controller**
*Details Last Updated on 14 November 2017 &nbsp | &nbsp Print Email Today we are going to share with you some…*www.codejava.net](http://www.codejava.net/frameworks/spring/14-tips-for-writing-spring-mvc-controller)
[**Spring MVC Cookie example. Spring Http Cookie Tutorial**
*In this post we will see how to access and modify http cookies of a webpage in Spring MVC framework. Spring 3 MVC…*viralpatel.net](https://viralpatel.net/blogs/spring-mvc-cookie-example/)
[**Spring MVC and the @ModelAttribute Annotation | Baeldung**
*One of the most important Spring-MVC annotations is the @ModelAttribute annotation. The @ModelAttribute is an…*www.baeldung.com](https://www.baeldung.com/spring-mvc-and-the-modelattribute-annotation)
[**Model, ModelMap and ModelView in Spring MVC | Baeldung**
*In this article, we'll look at the use of the core org.springframework.ui.Model , org.springframework.ui.ModelMap and…*www.baeldung.com](https://www.baeldung.com/spring-mvc-model-model-map-model-view)
[**Error Handling for REST with Spring | Baeldung**
*This article will illustrate how to implement Exception Handling with Spring for a REST API. We'll look at both the…*www.baeldung.com](https://www.baeldung.com/exception-handling-for-rest-with-spring)
[**How to use Spring Exception Handler for SpringMVC: @ExceptionHandler, @ResponseStatus…**
*Spring provides a cross-cutting concern solution for handling Java Excepion. So in the tutorial, JavaSampleApproach…*grokonez.com](https://grokonez.com/spring-framework/spring-mvc/use-spring-exception#1_ResponseStatus)
[**Spring MVC: How to return custom 404 errorpages?**
*I'm looking for a clean way to return customized 404 errorpages in Spring 4 when a requested resource was not found…*stackoverflow.com](https://stackoverflow.com/questions/21061638/spring-mvc-how-to-return-custom-404-errorpages)
[**Using @ResponseStatus to Set HTTP Status Code | Baeldung**
*In Spring MVC, we have many ways to set the status code of an HTTP response. In this short tutorial, we will see the…*www.baeldung.com](https://www.baeldung.com/spring-response-status)
