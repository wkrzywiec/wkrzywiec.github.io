---
title: "How to start with Spring MVC"
date: 2018-09-07
summary: "Step-by-step guide for creating a Spring MVC application"
description: "In this blog post I would like to introduce you to the Spring MVC framework, how it works, what are the pros and what are the possibilities it gives to us, developers. At the end I will show most of the important features in a simple project."
tags: ["java", "spring", "mvc", "library-project"]
canonicalUrl: "https://wkrzywiec.medium.com/how-to-start-with-spring-mvc-309dec3c59fd"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/how-to-start-with-spring-mvc-309dec3c59fd).
{{< /alert >}}

![“green leafed plant” by [Ash from Modern Afflatus](https://unsplash.com/@modernafflatusphotography?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/10368/0*bTMFaeE6_KP1raNf)*Photo by [Ash from Modern Afflatus](https://unsplash.com/@modernafflatusphotography?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*In this blog post I would like to introduce you to the Spring MVC framework, how it works, what are the pros and what are the possibilities it gives to us, developers. At the end I will show most of the important features in a simple project.*

## Introduction

As you might guess it already, Spring MVC implements very common architecture pattern — *Model-View-Controller*. Its key concept is to organize entire application into three modules. **View** is responsible for User Interface, which in our case will be HTML page (or more specific JSP file). **Controller** is taking care of HTTP requests and delegates tasks (e.g. fetching data from database) to other components. And finally a **Model,** it structurises the data and represents business logic of an application. More information, presented in a funny way, about MVC pattern could be found [here](https://medium.freecodecamp.org/model-view-controller-mvc-explained-through-ordering-drinks-at-the-bar-efcba6255053).

In Spring MVC View is represented by JSP files, the Controller by the class with special annotation and the Model are Beans. In this post I would like to concentrate on a key part of this framework — Controller.

Before I jump to talk over the Controller class first I would need to explain how it really works under the hood. I don’t want to go much into details how it really works, because I want to keep it simple and that’s not aim of my post. But if you are interested in more in-depth explanation (with information about DispatacherServlet etc.) I would recommend this article [How Spring Web MVC Really Works](https://stackify.com/spring-mvc/?utm_referrer=https%3A%2F%2Fmedium.com%2Fr%2F%3Furl%3Dhttps%253A%252F%252Fstackify.com%252Fspring-mvc%252F).

In short, Spring MVC app works with a servlet thats receives HTTP requests and process it. In Spring MVC world it is called DispatcherServlet and it facilitate request mapping to certain methods from Controller class to process certain tasks (like connecting to the database, process forms, etc.).

If it is not clear, don’t worry. I’ll explain it on following examples.

NOTE: In a following section I’ll show few examples of the Controller. To keep it simple I avoid configuration steps, these could be found at the end of the post, where I present all the steps necessary to set up Spring MVC project.

### Structure

First thing first, **how Controller looks like?** It’s a really simple Java class with specific notifications and declaration rules regarding public methods (i.e. their return type and arguments). Below there is a code of a single method class that acts as a Controller.

```java
@Controller
public class LibraryController {
 
    @GetMapping("/home")
    public String showHome() {
                // do something 
        return "home";
    }
}
```

First, you see a@Controller annotation that lets Spring know that this class will be the controller. Next, in the body of class there is a single method named `showHome()`. It’s annotated with @GetMapping which means that it will be called when a servlet receives a GET request (type of HTTP request) that matches pattern “basicURI/home”. If you run your servlet on a local machine it probably looks as follows “http://localhost:8080/home” or if you run it on your server with bought domain “http://your-awsome-page.com/home”.

Accordingly, if you want to map any other type of HTTP request just use one of the followings: @PostMapping, @PutMapping, @DeleteMapping, @PatchMapping.

Finally, above method has a simple String as a return value, which indicates what JSP file to send to the requestor. In our case it will be *home.jsp* file which is included in the project (more information about how to set up will be described in next sections).

And that’s it! Controller class structure is really simple and the whole process of defining each method could be sum up to following steps:

1. Create public method
2. Add HTTP request mapping to this method
3. Add arguments to the method (if necessary)
4. Write method body

### URI pattern syntax

First things first, we need to to map HTTP requests to the methods in the Controller class. Under the hood, when a Spring MVC app receives a request it is handled by the *DispatcherServlet *which delegates them to according handler, which will be Controller class.

Sometimes those requests are rather simple, like as it’s in above code snippet. Whole request path is static, which means that in order to call this method we need to provide this exact path. What if we would like to make it more dynamic? For example we’ve got bunch of similar URIs that should be mapped to one method.

To achieve that we can add ***?*** sign to the annotation path like:

```java
@GetMapping("/book?")
```
Above we tell Spring that each URI that ends with “/book” + any other single sign should be processed by this method. So if it ends with “/book1”, “/book^” or whatever it will be handled by this.

Sometimes we want to match more than one character and for that we can use * or ** wildcard. First one matches all the characters within path segment (between two “/”), the latter can match multiple segments. To illustrate this see below examples:

```java
@GetMapping("/book*")

@GetMapping("/book**")
```

First mapping will match the URI “/bookGameOfThrones” and second one will match “/book/GameOfThrones”.

Ok, but what if I would like to get information from the URI? It could contains the name or id of the book that we want to fetch. How to solve it? Very easily, by using either @PathVariable or @RequestParam annotation.

**@PathVariable** — some segments of the URI can be dynamize, for example if we want to get *bookId*=348 and *authorId*=2 from the path “*baseURI/book/348/author/2*” the mapping will look like this:

```java
@GetMapping("/book/{book}/author/{author}")
public String showBookAndAuthorDetails (  
    @PathVariable("book") Long bookId,
    @PathVariable("author") Long authorId) {
  
// do some stuff with bookId and authorId
}
```

Both Ids are stored in their variables and can be used in the method’s body. Please notice that dynamic part of the URI must be surrounded with curly brackets *“{}”* in the mapping and this part should has the same name as the argument of the annotation.

**@RequestParam** — another way to pass some information thru URI is by request parameter. You’ve probably see it in lots of them. For example, link “[https://www.youtube.com/watch?v=s7L2PVdrb_8&t=10s](https://www.youtube.com/watch?v=s7L2PVdrb_8&t=10s)” is made of two pieces. First is regular “https://www.youtube.com/watch”, which is static, and a second “[v=s7L2PVdrb_8&t=10s](https://www.youtube.com/watch?v=s7L2PVdrb_8&t=10s)”, which is dynamic and has two arguments: ***v*** — it’s video Id and ***t***-it’s a second when the video should starts. Both pieces are separated with ***?*** sign and arguments are separated with ***&*** character.

If we wanted to get the *bookId* and *authorId*, as it was in the previous example, but this time using @RequestParam annotation the URI could look like this “*/book?id=348&author=2*”, so the mapping:

```java
@GetMapping("/book")
public String showBookAndAuthorDetails (
    @RequestParam(value="id", required=true) Long bookId,
    @RequestParam(value="author", required=false) Long authorId) {
  
 //do some stuff with bookId and authorId 
}
```

Notice that *author* request parameter is not required so mapped argument, *authorId*, might be null.

And the last thing, in all above examples arguments are Long type, but they can be also String or Integer.

### Return types

Once the mapping is set up we need to assign what resource our web app will return. In our case it will be some sort of data bundle that contains HTML, CSS, JS files or data model objects, which in WWW world is called HTTP Response. It contains three parts: Status-Line (basically protocol version), Response Header (includes server info and [Status code](https://httpstatuses.com/), like famous ‘404 Not found Error’) and Response Body.

Depending on how much into detail we would like to go there are several return types that Controller method can have.

**String** — this is the simplest case. By typing the JSP file name in return statement we can indicate which one we want to send. In other words it works the best when we don’t need to attach any model object into the HTTP response (it’s not 100% true because we can do that by adding special argument to the Controller method).

```java
@Controller
public class LibraryController {
 
    @GetMapping("/home")
    public String showHome() {
                // do something 
        return "home";
    }
}
```

In above example I provide simple “home” String, which means that as a Response I want to send a *home.jsp* file that is located somewhere in my project. How to configure Spring so by typing only the ‘main’ part of the file path we can get it? Please check [here](https://medium.com/p/309dec3c59fd#a35a).

**ModelAndView** — as the name suggest it’s holding two types of objects: Model and View. First one, is some sort of container that holds information that will be displayed as a View (JSP file). Second is a model that wraps some information that can be used by a View. In other words View acts as a template and a Model populate it with a data (e.g. fetched from the database).

```java
@Controller
public class LibraryController {
 
   @GetMapping("/home")
    public ModelAndView showHome() {
 
        ModelAndView mv = new ModelAndView()
        mv.setViewName("home");  //indicates which view file will be sent
        mv.getModel().put("message", "Hello friend! I hope you have a nice day!");  
        //in above method model is added to the respond under key "message" with a second argument as a value
      
        return mv;
    }
}
```

In above code snippet, the View is set up to “home” (works similar to previous example) and the Model contains one key-value pair. First argument, “message”, is a key and the second is a value. Here its value is a String object, but it can any class that you want (for example book model that holds data about the book, like author, title, page count, etc.).

You might wonder how JSP file enters the data stored in the Model class? The answer to that is: using [JSP Expression Language](https://www.journaldev.com/2064/jsp-expression-language-el-example-tutorial).

And that’s the basics. If you look into the [Spring docs](https://docs.spring.io/spring/docs/current/spring-framework-reference/web.html#mvc-ann-return-types) you’ve probably see other types, like ***HttpEntity*** (to enable respond header modification), ***RxJava*** Observable (for asynchronous request processing) or ***model class annotated with @RespondBody*** (method with this annotation will return XML/JSON or other representation of the object). The last one is used chiefly for building REST API apps (e.g. for microservices) and I’ll cover it in one of my next post, when I’ll create API for Library Portal.

### Arguments

Another thing that you might want to add to controllers methods are arguments. They allow to enter objects that are part of the HTTP request, like the model, request parameters, form validator etc. Most of them could be done in other way. For example, if you want to enter the model, you better set a return type of a model as a ModelAndView not a String, which will result in fewer number of parameters in the method.

In this part I skipped those that I’ve already mentioned — @PathVariable and @RequestParam.

**Model** — key role of the Model in HTTP Response is to provide data that can be used for rendering a view. In other words it a view (JSP file) takes some data from it and insert into its body. Data are usually fetched from the database using a service object, like it is shown below.

```java
@GetMapping("/user")
public String showUserDetails( @RequestParam("id") Long userId,
                               Model model) {
    
    UserDTO user = userService.getUser(userId);
    model.addAttribute("user", user); 
  
    return "user-details";
}
```

**ModelMap** — this one is similar to previous one. It has all functionality that *Model* has but also it allows to add request parameter to the output request. It is worth notice that *ModelMap *is actually an implementation of the *Model* interface, which is the reason of their similarities.

It might be useful when the user provide only partial URL, but the website requires some parameters. Therefore we can add default value using *put(key,value)* method. Like in the following example, list of all books is sorted descending by default.

```java
@GetMapping("/allBooks")
public String showAllBooks(ModelMap map) {
  
    List<BookDTO> books = bookService.getAllBooks();
    
    map.addAttribute("books", books);
    map.put("sort", "desc");  
  
    return "books";
}
```

**@ModelAttribute** — is used to bind the object from the HTTP Request Model to the argument in the method. Chiefly it is used while processing form. For example, when registering new user we need to get the User object to retrieve data that were input.

```java
@PostMapping("/register-user")
public String processRegisterForm(
		@ModelAttribute("user") UserDTO userDTO) {
		
	userService.saveNewUser(userDTO);
  
  	return "loginPage";
}
```

**BindingResult** — it is tightly connected with previous one and together with @Valid annotation is used for form detecting errors in a form (to be precise, object attached to the request). Thanks to that we can easily check if the form contains any error.

Also it is worth notice that this parameter needs to be right after the object that is validated.

```java
@PostMapping("/register-user")
public String processRegisterForm(
		@Valid @ModelAttribute("user") UserDTO userDTO,
		BindingResult bindingResult,
		Model model) {
		
	if (bindingResult.hasErrors()){
      		//there are some errors in the form, so go back
		return "register-user";
	} else {
      		//everything is fine, so register new user
		return "success";
	}
}
```

**RedirectAttributes** — sometimes we need to redirect HTTP request from one method to another method. To do so we can need to need add *“redirect:”* prefix followed by the request URL. If we want to redirect to a simple method, that’s fine. The problem begins when we want send also request parameters (attributes) to the next method. And therefore we’ve got RedirectAttributes object into which we can pass attributes that will be processed by target method.

```java
@GetMapping("/add-book")
public String addNewBook( @RequestParam("book") String googleBookId,
                          RedirectAttributes attributes) {
  
  //fetch data from Google Book API
  //add new book to the library
  
  attributes.addAttribute("googleBook", googleBookId);
  
  return "redirect:/book-details";
}

@GetMapping("/book-details")
public String showBookDetails( @RequestParam("googleBook") String googleBookId,
                          Model model) {
  
  //find book in the database using it's Google Book Id
  //add it to the model
  
  return "book-details";
}
```

Above code shows an example of such redirection. First method focus mainly on adding new book do the database (data are taken from Google Book API) and then it is redirected to the more general method that presents book detailed page.

**@CookieValue** — in some cases we want to enter HTTP cookies that are included in the request. To access it just add this annotation to the argument (usually it will be String or numeric) which will be binded to cookie with specified name. In the following example a value of cookie with a name *“session”* is stored in a *sessionKey* String variable and then printed in the console.

```java
@GetMapping("home")
public String showHomePge(
	@CookieValue(value = "session", defaultValue = "hash") String sessionKey) {

	System.out.println(sessionKey);
}
```

**HttpServlerResponse** — this is one allows to enter the whole response that will be send, so you are able to modify almost everything, like the header, cookie, attached objects and more.

### Exceptions handling

Another good thing that Spring MVC provides is error handling. Imagine that for some reason user has provided incorrect path, or maybe she/he bump into a bug in your procedures and get whole stack trace, which might not be the best thing to show to the customer. Instead we can gracefully redirect to better looking error page.

To achieve it basically we can choose one of two approaches. In a first one, we can add error handling methods into particular Controller class. The main disadvantage of this solution is when we have multiple Controllers in the project we need to multiple those methods in each one of them. To overcome this problem we can create custom error handling object that will take care it globally.

If our project is rather small, we could do without making separate error handling class. Therefore we need to add **@ExceptionHandler** annotation to the particular method.

```java
@ExceptionHandler(NullPointerException.class)
public String handleException() {
      //maybe log something?
      return "error-page";
}
```

While the project become bigger and bigger it might be a good idea to split one main Controller into few smaller ones based on the concern. Together with that we would also need to create one global object that handles all the errors. In order to do that we need to create new class that is annotated with **@ControllerAdvice**. And the good thing about it is that works similar to Spring Controller (same return types, etc.).

```java
@ControllerAdvice
public class GlobalExceptionHandlerController {

      @ExceptionHandler(NullPointerException.class)
      public String handleException() {
            //maybe log something?
            return "error-page";
      }

      @ExceptionHandler(ResourceNotFoundException.class)
      @ResponseStatus(HttpStatus.NOT_FOUND)
      public String handleNoResourceFound() {

            return "error-notfound";
      }
  
}
```

Above example shows how to handle two types of errors. First, popular NullPointerException, returns 500 HTTP Status and second returns status 404. The main difference between those two is that in a latter I’ve added new annotation — **@ResponseStatus**. Using that we manually set a response status in the response header. In above case it is set up to 404, because without it the web browser would receive 200 (OK) status, because it was handled by ControllerAdvice class.

And that’s it. All the basics were covered so let’s move to implementation of a simple example.

## Writing code

### Create Gradle project in the Eclipse

First we need to create a new Gradle project. In Eclipse (in my case, Oxygen version) go to **File->New->Project…** and from the wizard select **Gradle**. In a following screens keep all as defaults, in one of them provide project name.

### Add dependencies to build.gradle

Once the project is created we need to download some libraries. Except for obvious one, Spring MVC, I’ve decided to use a [Gradle-Tomcat plugin](https://github.com/bmuschko/gradle-tomcat-plugin) that allows to rapid deployment of the application on the Tomcat server. Moreover, [Eclipse-WTP](https://docs.gradle.org/current/userguide/eclipse_plugin.html) plugin was added to tell Gradle that we work in Eclipse.

```gradle
apply plugin: 'java-library'
apply plugin: 'war'
apply plugin: 'com.bmuschko.tomcat'
apply plugin: 'eclipse-wtp'


repositories {
    jcenter()
}

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
    	def springWebMvcVersion = '5.0.2.RELEASE'
    
    	tomcat "org.apache.tomcat.embed:tomcat-embed-core:${tomcatVersion}",
           "org.apache.tomcat.embed:tomcat-embed-logging-juli:${tomcatVersion}",
           "org.apache.tomcat.embed:tomcat-embed-jasper:${tomcatVersion}"
    
    	providedCompile 'javax.servlet:javax.servlet-api:4.0.0'
	compile 'javax.servlet:jstl:1.2'
	compile 'javax.servlet.jsp:javax.servlet.jsp-api:2.3.1'
	compile "org.springframework:spring-webmvc:${springWebMvcVersion}"
	compile "org.springframework:spring-test:${springWebMvcVersion}"

    	testImplementation 'junit:junit:4.12'
}

tomcat {

	httpPort = 8080
	enableSSL = true
	contextPath = '/simple-spring-mvc'
}
```

Finally refresh project by right-clicking on it’s name then **Gradle->Refresh Gradle Project**, so new libraries will be downloaded.

### Spring MVC configuration

I know what you say. Why don’t you use Spring Boot for this task? Instead of few clicks you bother to get it done in a hard way. The answer to that is because I would like to go thru this standard way, like it was days before Spring Boot.

Therefore, create a new package, let’s call it config, an in it create simple Java class — AppConfig.

```java
@Configuration
@EnableWebMvc
@ComponentScan(basePackages="com.wkrzywiec.simplespringmvc")
public class AppConfig implements WebMvcConfigurer {

	@Bean
	public ViewResolver viewResolver() {
		InternalResourceViewResolver viewResolver = new InternalResourceViewResolver();
		
		viewResolver.setPrefix("/WEB-INF/views/");
		viewResolver.setSuffix(".jsp");
		return viewResolver;
	}
}
@Configuration
@EnableWebMvc
@ComponentScan(basePackages="com.wkrzywiec.simplespringmvc")
public class AppConfig implements WebMvcConfigurer {

	@Bean
	public ViewResolver viewResolver() {
		InternalResourceViewResolver viewResolver = new InternalResourceViewResolver();
		
		viewResolver.setPrefix("/WEB-INF/views/");
		viewResolver.setSuffix(".jsp");
		return viewResolver;
	}
}
```

@Configuration and @ComponentScan annotations are telling Spring context that it is a config class and where to scan for beans respectivaley. More intresting are @EnableWebMvc annotation with WebMvcConfigurer interface implementation that enables Spring MVC features in our project.

Finally above config class contains one method for setting *ViewResolver* properties. In it, we provide prefix and sufix of a view name. So from now on, in Controller class you don’t need to provide full name of the view, just significant part of it. So instead of *“/WEB-INF/views/**home**.jsp”* we can provide short “**home**” and *ViewResolver* will know which JSP file to look for.

```java
public class SimpleSpringMVCServletDispatcherInitializer extends AbstractAnnotationConfigDispatcherServletInitializer {

	@Override
	protected Class<?>[] getRootConfigClasses() {
		return null;
	}

	@Override
	protected Class<?>[] getServletConfigClasses() {
		return new Class[] {AppConfig.class};
	}

	@Override
	protected String[] getServletMappings() {
		return new String [] {"/"};
	}

}
```

Another class that we need to add is that extends *DispatcherServletInitializer*, which replaces mandatory web.xml file in the project and makes it totaly XML-free.

### Prepare simple view

After configuration we can focus on a fun part — views and controller. Therefore we create first, simple JSP file in Eclipse, which will look like follows.

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
	<h1>Welcome!</h1>
	<p>This is home page of Simple Spring MVC project!</p>
</body>
</html>
```

A file should be located in a directory: *src/main/webapp/WEB-INF/views/.*

### Create Spring Controller

Finally we need to create new package, called controller, and add new class. For now it will contains only one method for the URL *http://localhost:8080/simple-spring-mvc/.*

```java
@Controller
public class SimpleSpringMVCController {

	@GetMapping("/")
	public String showHomePage() {
		
		return "home";
	}
}
```

Note: If you don’t know where the base URL is defined check the Gradle file for Tomcat configuration.

### Testing

To run it we need first we need to run a specific Gradle task called* tomcatTun. *To make it as easy as it could be go to ***Run/Run Configurations…,*** click **New** icon and enter following inputs:

* Name: *Simple Spring MVC — run*

* Gradle Task: *tomcatRun*

* Working Directory: *${workspace_loc:/*spring-mvc-simple*}*

![](https://cdn-images-1.medium.com/max/2052/1*-xj_8_DoNMWaeHFmgl2Zxg.png)

We have now easy access to the task which can be started using **Run** button in Eclipse. Once you run this task and wait for all init jobs to be finished you can type URL *http://localhost:8080/simple-spring-mvc/* in the browser and get following page:

![](https://cdn-images-1.medium.com/max/2000/1*HVdXMWn4SeX1qFR5rtcNcg.png)

### Add more features

Ok we now that everything is working so let’s make it more complex/cooler. I would like to implement some of the features that were menationed in the article.

**@PathVariable**

Let’s make a new Controller method that will map URL *[http://localhost:8080/simple-spring-mvc/](http://localhost:8080/simple-spring-mvc/.)meme/{name}* which will direct us to a website that has certain meme depending on the name in the last part of URL. Therefore first we need to create 3 new views, one of them is:

```html
<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>
<%@taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<title>Works on my machine</title>
</head>
<body>
	<div class="container" style="margin-top: 30px;">
		<a href="${pageContext.request.contextPath}/">&#8592; Go back </a>
	</div>
	
	<div class="container" style="margin: 50px 50px 50px 50px">
		<img src="<c:url value="/resources/img/works.jpg" />"/>
	</div>
</body>
</html>
```

Some of the lines requires some exaplanation. In 3 line we add new library to allow [JSTL](https://www.tutorialspoint.com/jsp/jsp_standard_tag_library.htm) features.

Next, in line 12 there is a link to the home page, which is dynamic, so if we change our base URL (for example when we want to move the app from local to the server, we’ll don’t need to update all views). In our case it’s just telling to go to the *[http://localhost:8080/simple-spring-mvc/.](http://localhost:8080/simple-spring-mvc/.)*

Finally, in 16 line there is an image file path. To be able to use it first we need to do two things. First we need to add one method to AppConfig class that will map resource folder.

```java
public class AppConfig implements WebMvcConfigurer {
  
  //other config
	@Override
	public void addResourceHandlers(ResourceHandlerRegistry registry) {
		registry.addResourceHandler("/resources/**").addResourceLocations("/resources/");
	}
}
```

Second we need to add images to the project to a folder *src/main/webapp/resources/img.*

Finally we need to add method to Controller class.

```java
@Controller
public class SimpleSpringMVCController {
  
  //other methods
  
  @GetMapping("/meme/{name}")
	public String showNotsure(@PathVariable("name") String name) {
		
		if (name.equals("notsure")) {
			return "notsure";
		} else if (name.equals("instead")) {
			return "instead";
		} else {
			return "works";
		}
	}
}
```

Here is the sample of one of these pages:

![](https://cdn-images-1.medium.com/max/2000/1*m1U6a_VIzWS-94EGolQInA.png)

**@RequestParam & Model**

Moving forward, I’d like to add a box where we can input our name, than submit it so our name will appear in the URL and on the website.

So first we need to create two views — one for a form and another for a result.

```html
<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<title>Provide your name</title>
</head>
<body>
	<form action="processNameForm" method="GET">
		<div class="container" style="margin-left: 15px; margin-top: 15px;">
			<div class="row">
				<div class="col">
					<input type="text" class="form-control" name="name" placeholder="What's your name?" />
				</div>
				<div class="col">
					<input type="submit" class="btn btn-success" role="button"/ value="Submit">
				</div>
			</div>
			<div class="row">
				<div class="col">
					<a href="${pageContext.request.contextPath}/">&#8592; Go back </a>
				</div>
			</div>
		</div>
	</form>
	
	
</body>
</html>
```

Above is presented code of a form. The most important tag is <form> which wraps two inputs, one for a text box and another for submit button. This tag also have two attributes — action and method. First one indicates the URL of the result page (which will be *baseURL/processNameForm*) and second is telling what HTTP request to use.

```html
<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<title>Your name is ${param.name}</title>
</head>
<body>
		<h1>Hi ${param.name}!</h1>
		<p>Your name in upper cases looks like this ${upperName}.</p>
		<a href="${pageContext.request.contextPath}/name">&#8592; Go back </a>
</body>
</html>
```

HTML code of result page is shown above. Here, we will print the exact value of a request parameter with a name *“name”* that was passed using form on a previous page. Also we’ll get an attribute from the Model attached to the request — *“upperName”*, which you might already guess it, will be written using upper case letters. This attribute will be added from the Controller class.

```java
@Controller
public class SimpleSpringMVCController {
	
	//other methods

	@GetMapping("/name")
	public String showInputName() {
		return "name";
	}
	
	@GetMapping("/processNameForm")
	public String processInputName(
				@RequestParam("name") String name,
				Model model) {
		
		String upperName = name.toUpperCase();
		model.addAttribute("upperName", upperName);
		
		return "name-display";
	}
}
```

It contains two methods, one for each page. When we run the project we get

![Page where you provide your name.](https://cdn-images-1.medium.com/max/2000/1*jR3Ao1Cz77fioSroFrrH_g.png)*Page where you provide your name.*

![The URL after submitting the form.](https://cdn-images-1.medium.com/max/2000/1*WoXxlOFG0QfdR_sxTnsJzA.png)*The URL after submitting the form.*

![Page content after processing the form.](https://cdn-images-1.medium.com/max/2000/1*0xTzBJLo_QDceh45PAYtyA.png)*Page content after processing the form.*

**@ExceptionHandler and ModelAndView**

Last thing that I want to test is handling very popular Exception — NullPointerException. I want to redirect user to the error page and also print the exception stack trace in the console. Therefore we need to add following method to the Controller.

```java
@Controller
public class SimpleSpringMVCController {
  
  @ExceptionHandler(NullPointerException.class)
	public ModelAndView handleNullException(NullPointerException ex) {
	    
	    ModelAndView modelView = new ModelAndView("error");
	    modelView.addObject("message", "Some major error has occured.");
	    System.out.println(ex.getMessage());
	    
	    return modelView;
	}
  
  //other methods
}
```

This time we use ModelAndView class to pass the view name and add an attribute that is required by the JSP file.

```html
<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>
<%@taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<title>NullPointerException has been thrown!</title>
</head>
<body>
		<h1>Aye yai yai yai yai yai yai! </h1>
		<p>${message}</p>
		<img src="<c:url value="/resources/img/error.jpg" />"/>
		<a href="${pageContext.request.contextPath}/">&#8592; Go back </a>
</body>
</html>
```

Finally to test it we need to add button to the home page (with links to other features mentioned in this section).

```html

<%@ page language="java" contentType="text/html; charset=ISO-8859-1"
    pageEncoding="ISO-8859-1"%>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1">
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
<title>Home page</title>
<style>
	.container {
		margin-left: 15px;
		width: 500px;
	}
	
	.row {
		margin-bottom: 10px;
	}
</style>
</head>
<body>
	<h1>Welcome!</h1>
	<p>This is home page of Simple Spring MVC project!</p>
	
	<div class="container">
		<div class="row">
			<div class="col">
				Test @PathVariable - show meme pages
			</div>
		</div>
		<div class="row">
			<div class="col">
				<a href="${pageContext.request.contextPath}/meme/notsure" class="btn btn-info" role="button">Not sure</a>
			</div>
			<div class="col">
				<a href="${pageContext.request.contextPath}/meme/instead" class="btn btn-warning" role="button">Instead</a>
			</div>
			<div class="col">
				<a href="${pageContext.request.contextPath}/meme/works" class="btn btn-light" role="button">Works on my machine!</a>
			</div>
		</div>
		<div class="row">
			<div class="col">
				Test @RequestParam & Model - get name from the box
			</div>
		</div>
		<div class="row">
			<div class="col">
				<a href="${pageContext.request.contextPath}/name" class="btn btn-success" role="button">Provide your name</a>
			</div>
		</div>
		<div class="row">
			<div class="col">
				Test Exception Handler
			</div>
		</div>
		<div class="row">
			<div class="col">
				<a href="${pageContext.request.contextPath}/exception" class="btn btn-danger" role="button">Throw Exception</a>
			</div>
		</div>
	</div>
</body>
</html>
```

And finally, we need to map the request that will throw NullPointerException.

```java
@Controller
public class SimpleSpringMVCController {

    //other methods
  @GetMapping("/exception")
  public void thoreNullPointerException() {
   throw new NullPointerException(); 
  }
}
```

All these features are now available from the main page.

![](https://cdn-images-1.medium.com/max/2000/1*Q0GKJfu3DptCT7S9efGFag.png)

After clicking the last one we get an error page:

![](https://cdn-images-1.medium.com/max/2000/1*sq7UAlSY1nRYkrHTPBSwcw.png)

Whole project can be found here:

[**wkrzywiec/Simple-Spring-MVC** | github.com](https://github.com/wkrzywiec/Simple-Spring-MVC)

## References

* [**How Spring MVC Really Works** | stackify.com](https://stackify.com/spring-mvc/)
* [**Quick Guide to Spring Controllers | Baeldung** | baeldung.com](https://www.baeldung.com/spring-controllers)
* [**Web on Servlet Stack** | docs.spring.io](https://docs.spring.io/spring/docs/current/spring-framework-reference/web.html#spring-web)
* [**14 Tips for Writing Spring MVC Controller** | codejava.net](http://www.codejava.net/frameworks/spring/14-tips-for-writing-spring-mvc-controller)
* [**Spring MVC Cookie example. Spring Http Cookie Tutorial** | viralpatel.net](https://viralpatel.net/blogs/spring-mvc-cookie-example/)
* [**Spring MVC and the @ModelAttribute Annotation | Baeldung** | baeldung.com](https://www.baeldung.com/spring-mvc-and-the-modelattribute-annotation)
* [**Model, ModelMap and ModelView in Spring MVC | Baeldung** | baeldung.com](https://www.baeldung.com/spring-mvc-model-model-map-model-view)
* [**Error Handling for REST with Spring | Baeldung** | baeldung.com](https://www.baeldung.com/exception-handling-for-rest-with-spring)
* [**How to use Spring Exception Handler for SpringMVC: @ExceptionHandler, @ResponseStatus…** | grokonez.com](https://grokonez.com/spring-framework/spring-mvc/use-spring-exception#1_ResponseStatus)
* [**Spring MVC: How to return custom 404 errorpages?** | stackoverflow.com](https://stackoverflow.com/questions/21061638/spring-mvc-how-to-return-custom-404-errorpages)
* [**Using @ResponseStatus to Set HTTP Status Code | Baeldung** | baeldung.com](https://www.baeldung.com/spring-response-status)
