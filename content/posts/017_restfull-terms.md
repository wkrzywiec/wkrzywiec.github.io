
# REST, RESTful web service, API, SOAP…what’s the difference?
> https://wkrzywiec.medium.com/rest-restful-web-service-api-soap-whats-the-difference-4f101953d0bd

Recently I’ve worked on my first RESTful web service build with Spring Boot. Many times during it I’ve came accross of those specific terms like HTTP, SOAP, REST, API and many more. With this blog posts I would like to explain how understand all of them.

![“person on skyscraper taking a photo of building below during nighttime” by [Yiran Ding](https://unsplash.com/@yiranding?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/8420/0*kIXzCKenqP2vkR81)*“person on skyscraper taking a photo of building below during nighttime” by [Yiran Ding](https://unsplash.com/@yiranding?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

## **HTTP**

It stands for **H**yper**T**ext **T**ransfer **P**rotocol. You might know it from a web browser. When you type http://9gag.com you will be directed to the page with funny photos.
> In a simple words, HTTP defines how machines (server and client) communicate with each other the Internet.

Imagine, if we don’t have such well defined standard, what would happened if a client communicate with a server with unknown dialect? Server would probably won’t understand it and it could ignore it or send a *response *in different form to a client.

That’s why HTTP standard was developed by the Internet pioneers.

In short, it follows client-server model, where **client** (web browser) sends a message (called **request**) to the server to access specific resource (e.g. HTML document). As a result client recieves a structurized **response**. Both requests and response have their own structure.

Requests are made of:

* **HTTP method **— verbs like GET , POST , PUT , DELETE . They define the action which we would like to perform on a resource. For example, when we would like to fetch the HTML docs of this post we use GET method. But if we would like to add new one to the server, we would need to use POST . Of course, depending on a web server, such action could be allowed or not.

* **Resource path **—** **in order to perform any action on a resource we need to first indicate it’s path (address). Without that server would not know what resource we would like to fetch, update or delete.

* **HTTP protocol version** — during years HTTP evolves, today most of web servers are still supporting HTTP/1.1.

* **Header (optional) **— consists some additional information for a server, like in what langauage response will be accepted, what type of data should be sent back, cookie and authorization information, and other. The whole list could of fields that can be added are [here](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers).

* **Body (optional) **—is usually used when we would like to send something, POST , to a server.

A typical request looks as follows:

![](https://cdn-images-1.medium.com/max/2000/0*mtSEkGAfGzRkwbMU.png)

Response looks similar to it and contains:

* **HTTP protocol version**

* **Status code **— these are the codes that indicates the success of the request. Apart from the popular 200 (OK status) or 404 (resource not found). There are others like 201 (resources created) or 500 (developers hate this one in particular 😉, it means that a server throw an exception). Their list can be found [here](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status).

* **Status message**— the description of each code, e.g. 404 is *Not Found.*

* **Headers** — similar to the request, but here it is required.

* **Body (optional) **— contains the resource that we would like to fetch, e.g. HTML doc, JSON or XML file, image, video, etc.

A typical, JSON, response looks as follows:

<iframe src="https://medium.com/media/01cc70140afefd98302884988b999daa" frameborder=0></iframe>

If you’re looking for more information about HTTP check [MDN web docs](https://developer.mozilla.org/en-US/docs/Web/HTTP).

## Web service

When you think about the Internet you probably have in mind all these nice-looking websites. All of them were designed for, let’s say, human-machine interaction, so we, humans, could better understand the content.

If we use same approach for machine-machine (or aplication-application) interaction this could be not so efficient, because machines does not require pretty websites. They prefer more structurize responses in XML, JSON, CSV etc. And for that web services are utilized.

Also, but you probably already guess that, the communication is taking place over the web.

## API

Next, let’s introduce an **A**pplication **P**rogramming** I**nterface concept. In HTTP paragraph I’ve talked about communication protocol, but it isn’t everything that is necessary to establish communication. The server must define what actions can be proceed by the user. The sets of rules, methods and libraries can be called an API.

In our case I focus chiefly on web solutions, like [OpenWeatherMap API](https://openweathermap.org/api), where content provider defines what HTTP requests are allowed, with what request format and specifies how the outcome will look like. But we can think of an API not only in the context of the web, but also more general, it can be used in any hardware and software too. For example, for IoT devices you need to know what’s the device API in order to get data from it.

Going back to the web context, there are two types of API — SOAP and REST which are used to access resources shared other the internet.

## SOAP

**S**imple **O**bject **A**ccess **P**rotocol is an XML-based protocol and unlike REST, it tightly defines the structure of the request and response.

The SOAP message is called an Envelope and it consists of a Header (contains e.g. authentication information) and a Body (the XML response). It requires multiple XML identifiers, which are required even in a simple requests/responses. And for this reason SOAP is considered as very lengthy and error prone protocole, which might be really tricky in case of more complex systems.

Another term assosiacted with SOAP is WSDL (Web Services Description Language). Each SOAP web service is obliged to provide to a client a WSDL file which gives information like how sevice works and how to access it’s resources. It’s like a menu in the restaurant, the client receives a list of all actions that he/she is allowed to perform.

If you want to know more aout SOAP, with messages examples, go and check [the website](https://developers.google.com/ad-manager/api/soap_xml).

## REST

Another approach presents **RE**presentational **S**tate **T**ransfer. First of all it gets rid of rigid structure of the request and response. Also it is not limited to XML format, messages can be sent in multiple formats, like JSON or CSV.

REST relays heavily on HTTP to make the best use of its methods. It exposes the server resources to the clients, who can interact (get, add, update, delete) with them using those methods.

It’s important to understand that REST and SOAP are not complementary. First one is an architectural style (or design patern) and SOAP is an XML structurized message.

If you want to know more differences between those two check one of the following links:

* [Understanding SOAP and REST Basics And Differences](https://smartbear.com/blog/test-and-monitor/understanding-soap-and-rest-basics/)

* [SOAP vs REST 101: Understand The Differences](https://www.soapui.org/learn/api/soap-vs-rest-api.html)

**RESTful webservice**

What it means that a webservice is RESTful? Chiefly it means that a webservice is implementing REST architecture style, so it covers all of these points:

* Expose resources via URL, like /users/3 ,

* Make use of HTTP methods, like GET , DELETE and so on,

* Provides information about the response in a response code,

* Each respond should also provides hyperlinks to other resources, so the client will be able to navigate the API. In simple words, if parent resource has a child it is a good thing to add URL to a child resource.

**RESTful webservice with Spring Boot**

How we can make a RESTful webservice on your own really quick? For this task we can make use of [Spring Boot](https://spring.io/projects/spring-boot) which sets up most of configuration for us so we can focus on building business part of the project.

Below there is a step-by-step tutorial how create great RESTful webservice.
[**Building REST services with Spring**
*this tutorial is designed to be completed in 2-3 hours, it provides deeper, in-context explorations of enterprise…*spring.io](https://spring.io/guides/tutorials/bookmarks/)

Also if you are interested in my first REST project check my GitHub repository.
[**wkrzywiec/Library-API**
*A REST API for my other project - Library Spring. Contribute to wkrzywiec/Library-API development by creating an…*github.com](https://github.com/wkrzywiec/Library-API)

## References
[**What Are RESTful Web Services? - The Java EE 6 Tutorial**
*RESTful web services are built to work best on the Web. Representational State Transfer (REST) is an architectural…*docs.oracle.com](https://docs.oracle.com/javaee/6/tutorial/doc/gijqy.html)
[**Describing RESTful Applications**
*If servers control their own namespace without a fixed resource hierarchy, how do clients, and more importantly client…*www.infoq.com](https://www.infoq.com/articles/subbu-allamaraju-rest)
