---
title: "Making use of open REST API with Retrofit"
date: 2018-07-07
summary: "How to start using Retrofit library"
description: "If you look on application landscape in any big company you probably see that it is composed of multiple separate applications that communicate with each other. And such communication might be quite challenging if there is no standard way, protocol, to resolve it. Luckily, Application Programming Interface (API) is for a rescue!"
tags: ["java", "api", "rest", "library-project"]
canonicalUrl: "https://wkrzywiec.medium.com/making-use-of-open-rest-api-with-retrofit-dac6094f0522"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/making-use-of-open-rest-api-with-retrofit-dac6094f0522).
{{< /alert >}}

![Photo by [G. Crescoli](https://unsplash.com/@freegraphictoday?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/8000/0*jL8PCIHLw5gTft16)*Photo by [G. Crescoli](https://unsplash.com/@freegraphictoday?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*If you look on application landscape in any big company you probably see that it is composed of multiple separate applications that communicate with each other. And such communication might be quite challenging if there is no standard way, protocol, to resolve it. Luckily, Application Programming Interface (API) is for a rescue!*

> So what exactly is API?

In short **it is a set of rules, functions, by which applications can interacts with each other**. And by interacting I mean fetching the data (usually in a form of JSON or XML files) or by changing state of receiving system (modify database etc.).
> Ok, now what is REST?

It stands for **Re**presentational **S**tate **T**ransfer and is a design pattern that is typically used in web application to expose its state and resources to the clients and it relays on HTTP protocol methods (GET, POST, PUT, DELETE).

In other words, REST API is a service of an application that expose its functionality and make it accessible for other applications via HTTP requests. And a good thing is that it is us, developers, who can define what part of the application we would like to expose. Do you want to allow others to see only small part of your application? No problem, it is you who defines what to show.

In this blog post I will focus on receiving part of the communication. Building own REST API is much more complex topic, but I’ll cover it in future, in my next project.
> Everything is a little bit abstract. Do you have any example?

Sure, there are plenty open source API that can be used. A cool list can be found [here](https://github.com/toddmotto/public-apis), where all of them are sorted by categories. Many organizations from outside this list provide free API, so if you are interested in particular field just try to dig in it on their website.

For example, you can use [YouTube API](https://developers.google.com/youtube/v3/) to search for videos, updating them to service and so on. Most of them, like YouTube, requires additional authentication to make it more secure or to manage its traffic. The most popular ways are:

* API key included in the request URL or header,

* Basic authorization,

* OAuth 2.0 protocol.

A way to achieve is very different depending on API provider, but usually it is only a simple registration (for open source).

In my project, Library Portal, I want to make use of a [Random Quote API](https://talaikis.com/random_quotes_api/) to inspire users whenever they log into the application 😉. One of a reason why I’ve chosen this API is that it is free and really simple to use.

From official website we can read that in order to get a random quote you need to use bellow address:

[https://talaikis.com/api/quotes/random/](https://talaikis.com/api/quotes/random/)

As we want to fetch the data, we want to use GET method of HTTP protocol, the same that web browser use to get HTML page. And so if it is the same method, we can test it on our web browser. After typing above URL you should get something like this:

```json
{
  "quote":"Love is the ability and willingness to allow those that you care for to be what they choose for themselves without any insistence that they satisfy you.",
  "author":"Wayne Dyer",
  "cat":"love"
}
```

As a result we receive a simple JSON file that contains three pairs of key-value separated with colon `:` that describes a Random Quote object. If you need more information about JSON syntax check this [link ](https://www.digitalocean.com/community/tutorials/an-introduction-to-json)(also in the References section).

## Retrofit 2.0 — simple way to consume REST API
> All right, I get what REST API is and what could be the respond, but how to translate it into Java code?

Your first idea probably was to create own JSON parser, but such approach could be error prone and it could take a lot of time, especially in more complex cases. Luckily we’ve got *Retrofit 2.0* library that allows us to mange it really smoothly.

Work on implementing Retrofit can be divided into three stages:

* Map REST respond to the Java model class

* Define interface for REST API methods

* Create class that will use REST API interface and respond model

**Map REST respond to the Java model class**

REST API respond can be represented in Java with simple POJO, so its fields name will be keys of JSON respond. In our example it looks as follows:

```java
public class RandomQuoteResponse {

	private String quote;
	private String author;
  
  //getters and setters
}
```

You may notice that I’ve omitted `cat` key. One of the cool things of Retrofit is that you don’t need to map all keys, only those that you need.

Our example is very simple, but in usually the JSON structure is not so simple, which makes mapping very arduous. To overcome it you can visit a website which will generate a POJO for you, just by providing the sample JSON.

[**jsonschema2pojo** | jsonschema2pojo.org](http://www.jsonschema2pojo.org/)

**Define interface for REST API methods**

Next we need to map REST API request to the Java interface class. Below there is a snippet for Random Quotes:

```java
import com.wkrzywiec.spring.library.retrofit.model.RandomQuoteResponse;

import retrofit2.Call;
import retrofit2.http.GET;

public interface RandomQuoteAPI {

	@GET("/api/quotes/random/")
	public Call<RandomQuoteResponse> getRandomQuote();
}
```

Each method in the interface represents one possible API call. In our example we make a use on one of them and therefore we have only single method.

This method is annotated with @GET, which tells Retrofit to use HTTP GET method on specific web resource (`/api/quotes/random/`) of a base URL (it will be introduced in next step).

Except for @GET annotation there @POST, @DELETE, @PUT that are used for correspond HTTP methods.

The return type of interface method must be always Call<T>, where T is an object that represents the API respond (defined in previous section).

Our example is really simple. It doesn’t contain any dynamic path or parameter, but most APIs requires to provide information what resource we would like to fetch/modify. We can take care of it in two ways.

First, we can add markup into resource path, which will be specified between two brackets {}. For example, URL for retrieving book from Google Book API is [https://www.googleapis.com/books/v1/volumes/{googleId}](https://www.googleapis.com/books/v1/volumes/{googleId},) where in a place of ***{googleId}*** should be a resource unique key. Another way to specify resource would be via request parameter at the end of the URL.

Below there is a code snippet of both these ways.

```java
public interface GoogleBookAPI {

	@GET("/books/v1/volumes/{googleId}")
	public Call<BookDetailsRespond> getBookDetails(
        @Path("googleId") String googleId,
		@Query("key") String key)
} 
```

In order to pass value either to resource path or request parameter we need to add arguments to the method that are annotated with @Path and @Query respectively. With a base URL, googleId (“wrOQLV6xB-wC”) and API key (“Top_Secret_Key”) a resulting URL would be:

    https://www.googleapis.com/wrOQLV6xB-wC?key=Top_Secret_Key

**Create class that will use REST API interface and respond model**

Finally we need to put together both classes. Here is the method that covers this task.

```java
public class RandomQuoteService {

	public RandomQuoteResponse getRandomResponse() {
		
		RandomQuoteResponse randomQuote = null;
		
		OkHttpClient.Builder httpClient = new OkHttpClient.Builder();
		Retrofit retrofit = new Retrofit.Builder()
		  .baseUrl("https://talaikis.com/")
		  .addConverterFactory(GsonConverterFactory.create())
		  .client(httpClient.build())
		  .build();
		
		RandomQuoteAPI randomQuoteAPI = retrofit.create(RandomQuoteAPI.class);
		Call<RandomQuoteResponse> callSync = randomQuoteAPI.getRandomQuote();
		
		try {
			Response<RandomQuoteResponse> response = callSync.execute();
			randomQuote = response.body();
		} catch (IOException e) {
			e.printStackTrace();
		}
		 
		return randomQuote;
	}
}
```

Above code will be valid most of the time. First we need to create a Retrofit object. It requires several parameters like base URL or converter factory. The latter one depends on the respond type (JSON, XML, etc.). The most popular for JSON is GsonConverterFactory. List of available converter factories can be found [here](https://github.com/square/retrofit/tree/master/retrofit-converters).

Another object that can be passed to Retrofit object is an adapter, which extends Retrofit capability to integrate with some external libraries, e.g. with RxJava 2. List of available adapters can be found [here](https://github.com/square/retrofit/tree/master/retrofit-adapters).

In next part we create object that implements our interface (Retrofit is doing that) and make a synchronous call to retrieve RandomQuoteResponse object.

We could also make an asynchronous call which would like as follows:

```java
public class RandomQuoteService {
  //create retrofit object
  
  RandomQuoteAPI randomQuoteAPI = retrofit.create(RandomQuoteAPI.class);
  Call<RandomQuoteResponse> callAsync = randomQuoteAPI.getRandomQuote()

  callAsync.enqueue(new Callback<RandomQuoteResponse>() {
      @Override
      public void onResponse(Call<RandomQuoteResponse> call, Response<RandomQuoteResponse> response) {
        RandomQuoteResponse randomQuote = response.body();
      }
 
      @Override
      public void onFailure(Call<RandomQuoteResponse> call, Throwable throwable) {
        System.out.println(throwable);
      }
  });
}
```

## Writing code

In previous section I’ve shown a simple API example, now I’ll cover all steps that for more complex one — Google Book. In the Library Portal I want to be able to search for books in Google’s API and then adding them to the library. To achieve it I make a use of Retrofit.

The URL to fetch data from Google API is:

[https://www.googleapis.com/](https://www.googleapis.com/) books/v1/volumes?langRestrict=en&maxResults=40&printType=books&key=My_Key&q=book_title

There are several parameters that I’ve included in the URL:

* **langRestrict** — defines in which language I want to find resources,

* **maxResults** — number of maximum results per query, maximum allowable value is 40,

* **printType** — what print type (books, newspaper, etc.) to find,

* **key** — Google API key

* **q** — query to search for a book

There are more parameters available than above ones. The whole list with examples could be find on official the website of Google Book API here:

[**Using the API | Google Books APIs | Google Developers** | developers.google.com](https://developers.google.com/books/docs/v1/using#query-params)


### Step 0. Get an API key from Google

This step will vary depending on an API provider. In my case it is Google, which provides two types of authorization: API key and OAuth2. I’ve decided to use API key, as it is more simple way 😉.

To get an API key first you need to have Google Account. To create it go to:
[**Create your Google Account**
*Edit description*accounts.google.com](https://accounts.google.com/signup/v2/webcreateaccount?continue=https%3A%2F%2Faccounts.google.com%2FManageAccount&flowName=GlifWebSignIn&flowEntry=SignUp)

After registration (if you don’t how an account), go to Credentials page:

[**Google Cloud Platform** | console.developers.google.com](https://console.developers.google.com/apis/credentials?project=_)

During first login, you will be asked to create new project so create it. Next, on the left-hand side you should have a menu, from which select **Credentials.**

![](https://cdn-images-1.medium.com/max/2000/1*7U_4zDfHilPBT0lcjKxlDg.png)

You should get a screen where **Create credentials** button is visible. Click it and from the list pick **API key**. Your key should appear on a screen.

If you need more information about using Google Books APIs go to:

[**Using the API | Google Books APIs | Google Developers** | developers.google.com](https://developers.google.com/books/docs/v1/using)

### Step 1. Add dependencies to build.gradle file

First, add dependency to the Gradle build file (within dependencies brackets) in your project.

```gradle
compile 'com.squareup.retrofit2:retrofit:2.4.0' 
compile 'com.squareup.retrofit2:converter-gson:2.4.0'
```

### Step 2. Create model classes

Before creating model classes we need to analyze the API respond, so if we want to find books that are related to *‘game of thrones’ *we would use following query (sign *%20* is equivalent of blank space):

    https://www.googleapis.com/books/v1/volumes?langRestrict=en&maxResults=40&printType=books&key=My_Key&q=game%20of%20thrones

and as a result we get following JSON (for better readability I advice to install web browser plugin for JSONs when you will be testing API on your own):

```json
{
  kind: "books#volumes",
  totalItems: 422,
  items: [
    {
      kind: "books#volume",
      id: "l6xMUQ88vLAC",
      etag: "VSXB8iRfRxQ",
      selfLink: "[https://www.googleapis.com/books/v1/volumes/l6xMUQ88vLAC](https://www.googleapis.com/books/v1/volumes/l6xMUQ88vLAC)",
      volumeInfo:{
        title: "Re-Reading a Game of Thrones",
        subtitle: "A Critical Response to George R. R. Martin's Fantasy Classic",
        authors:[ "Remy J. Verhoeve" ],
        publisher: "Nimble Books LLC",
        publishedDate: "2011-04",
        description: "In 1996, George R.R. Martin electrified fantasy fans around the world when he published A Game of Thrones, the first book in his acclaimed A Song of Ice and Fire series. Since then, Martin has published three more books in the series. The engrossing tale Martin spun with these first novels in his saga has gained more and more fans across the world and has resulted in a number of spin-off products, such including HBO's TV series, card and board games, computer games, sword replicas, comic books and calendars. Perhaps paradoxically, the number of years between each time Martin publishes a new book in the series has increased. Fans have been clamoring for the fifth volume, A Dance with Dragons, since 2005: A book that promises to pick up the storylines of fan-favorite characters left hanging since 1999. As Martin struggles to reach the finish line, or indeed even the halfway point in his epic, his fans wait for the next fix. One way to keep sane during the long waits is to re-read the already published novels. Journey to Westeros with Remy J. Verhoeve as he celebrates his tenth reading of A Game of Thrones. Chapter by chapter, the author, a Dutch-Norwegian English teacher and self-confessed fantasy geek, is both fellow traveler and tour guide as he shares his insightful reflections on Martin's writing techniques, major - and seemingly minor - plot points and characters, and much more. True to its origins as a blogging project undertaken while not-so-patiently waiting for A Dance With Dragons, the author does not hold back in this unauthorized companion book that is both an unabashed homage to the novel that started it all, as well as a candid - and at times controversial - commentary on the issues surrounding the delayed release of the fifth book. Whether or not they agree with everything the author has to say, all fans of A Song of Ice and Fire, from those who have loved the series since its inception in 1996 to those who have only just discovered it through the HBO series, will enjoy this thought-provoking and outspoken book.",
        industryIdentifiers: [
          {type: "ISBN_13", identifier: "9781608881154"},
          {type: "ISBN_10", identifier: "1608881156"}
        ],
        readingModes**: {
          text: true,
          image: true
        },
        pageCount: 372,
        printType: "BOOK",
        categories:[ "Literary Criticism" ],
        averageRating: 5,
        ratingsCount: 1,
        maturityRating: "NOT_MATURE",
        allowAnonLogging: true,
        contentVersion: "0.0.1.0.preview.3",
        panelizationSummary:{
          containsEpubBubbles: false,
          containsImageBubbles: false
        },
        imageLinks:{
          smallThumbnail: "[http://books.google.com/books/content?id=l6xMUQ88vLAC&printsec=frontcover&img=1&zoom=5&edge=curl&source=gbs_api](http://books.google.com/books/content?id=l6xMUQ88vLAC&printsec=frontcover&img=1&zoom=5&edge=curl&source=gbs_api)",
          thumbnail: "[http://books.google.com/books/content?id=l6xMUQ88vLAC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api](http://books.google.com/books/content?id=l6xMUQ88vLAC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api)"
        },
        language: "en",
        previewLink: "[http://books.google.pl/books?id=l6xMUQ88vLAC&printsec=frontcover&dq=game+of+thrones&hl=&as_pt=BOOKS&cd=1&source=gbs_api](http://books.google.pl/books?id=l6xMUQ88vLAC&printsec=frontcover&dq=game+of+thrones&hl=&as_pt=BOOKS&cd=1&source=gbs_api)",
        infoLink: "[http://books.google.pl/books?id=l6xMUQ88vLAC&dq=game+of+thrones&hl=&as_pt=BOOKS&source=gbs_api](http://books.google.pl/books?id=l6xMUQ88vLAC&dq=game+of+thrones&hl=&as_pt=BOOKS&source=gbs_api)",
        canonicalVolumeLink: "[https://books.google.com/books/about/Re_Reading_a_Game_of_Thrones.html?hl=&id=l6xMUQ88vLAC](https://books.google.com/books/about/Re_Reading_a_Game_of_Thrones.html?hl=&id=l6xMUQ88vLAC)"
      },
      saleInfo:{
        country: "PL",
        saleability: "NOT_FOR_SALE",
        isEbook: false
      },
      accessInfo:{
        country: "PL",
        viewability: "PARTIAL",
        embeddable: true,
        publicDomain: false,
        textToSpeechPermission: "ALLOWED",
        epub:{
          isAvailable: true,
          acsTokenLink: "[http://books.google.pl/books/download/Re_Reading_a_Game_of_Thrones-sample-epub.acsm?id=l6xMUQ88vLAC&format=epub&output=acs4_fulfillment_token&dl_type=sample&source=gbs_api](http://books.google.pl/books/download/Re_Reading_a_Game_of_Thrones-sample-epub.acsm?id=l6xMUQ88vLAC&format=epub&output=acs4_fulfillment_token&dl_type=sample&source=gbs_api)"
        },
        pdf:{
          sAvailable: true,
          acsTokenLink: "[http://books.google.pl/books/download/Re_Reading_a_Game_of_Thrones-sample-pdf.acsm?id=l6xMUQ88vLAC&format=pdf&output=acs4_fulfillment_token&dl_type=sample&source=gbs_api](http://books.google.pl/books/download/Re_Reading_a_Game_of_Thrones-sample-pdf.acsm?id=l6xMUQ88vLAC&format=pdf&output=acs4_fulfillment_token&dl_type=sample&source=gbs_api)"
        },
        webReaderLink: "[http://play.google.com/books/reader?id=l6xMUQ88vLAC&hl=&as_pt=BOOKS&printsec=frontcover&source=gbs_api](http://play.google.com/books/reader?id=l6xMUQ88vLAC&hl=&as_pt=BOOKS&printsec=frontcover&source=gbs_api)",
        accessViewStatus: "SAMPLE",
        quoteSharingAllowed: false
      },
      searchInfo:{
        textSnippet: "In 1996, George R.R. Martin electrified fantasy fans around the world when he published A Game of Thrones, the first book in his acclaimed A Song of Ice and Fire series. Since then, Martin has published three more books in the series."
      }
    },
  ///more results

  ]
}
```
From above output you can see that API provides a huge variety of information. I don’t want to map all of them, just the most essentials for my purpose, so my classes contain only these fields. For simplicity I haven’t included any getters and setters method that are required (or you can use [project Lombok](https://medium.com/@wkrzywiec/project-lombok-how-to-make-your-model-class-simple-ad71319c35d5)).

```java

public class GoogleBookRespond {

	private List<ItemAPIModel> items;
}
```

```java
public class ItemAPIModel {

	private String id;
	private VolumeInfoModel volumeInfo;
}
```

```java
public class VolumeInfoModel {

	private String title;
	private List<String> authors;
	private String publisher;
	private String publishedDate;
	private String description;
	private List<IsbnAPIModel> industryIdentifiers;
	private int pageCount;
	private List<String> categories;
	private double averageRating;
	private ImageLinksAPIModel imageLinks;
}
```

```java
public class IsbnAPIModel {

	private String type;
	private String identifier;
}
```

```java
public class ImageLinksAPIModel {

	private String thumbnail;
}
```

### Step 3. Create API interface

Once we have model classes than we need to create an interface for specific API call, which should like this:

```java
import com.wkrzywiec.spring.library.retrofit.model.*;
import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Path;
import retrofit2.http.Query;

public interface GoogleBookAPI {

	@GET("/books/v1/volumes?langRestrict=en&maxResults=40&printType=books")
	public Call<GoogleBookRespond> searchBooks(	
              @Query("q") String searchText,
							@Query("key") String key);

} 
```

### Step 4. Create API service

And next we need to design API Service class to create new Retrofit object and retrieve data.

```java
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.PropertySource;
import org.springframework.stereotype.Component;

import com.wkrzywiec.spring.library.dto.BookDTO;
import com.wkrzywiec.spring.library.retrofit.GoogleBookAPI;
import com.wkrzywiec.spring.library.retrofit.model.*;

import okhttp3.OkHttpClient;
import retrofit2.Call;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

@Component
@PropertySource(value = {"classpath:properties/googleAPI.properties"})
public class GoogleBookServiceImpl implements GoogleBookService {
	
	@Value("${googleAPI.key}")
	private String googleAPIKey;

	@Override
	public List<ItemAPIModel> searchBookList(String searchText) {
		
		List<ItemAPIModel> itemsAPIList = null;
		itemsAPIList = this.searchAPIItemsList(searchText);
    
		return itemsAPIList;
	}
  
	private List<ItemAPIModel> searchAPIItemsList(String searchText){
		
		List<ItemAPIModel> bookList = null;
		GoogleBookRespond respond = null;
		
		OkHttpClient.Builder httpClient = new OkHttpClient.Builder();
		Retrofit retrofit = new Retrofit.Builder()
		  .baseUrl("https://www.googleapis.com/")
		  .addConverterFactory(GsonConverterFactory.create())
		  .client(httpClient.build())
		  .build();
		
		GoogleBookAPI googleBookApi = retrofit.create(GoogleBookAPI.class);
		Call<GoogleBookRespond> callSync = googleBookApi.searchBooks(searchText, googleAPIKey);
		
		try {
			Response<GoogleBookRespond> response = callSync.execute();
			respond = response.body();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		bookList = respond.getItems();
		
		return bookList;
	}
}
```

You’ve probably notice @Component and @PropertySource above class declaration. These are Spring-specific, first one is responsible for registering class to Spring context, latter for getting properties file which contains my API key, which Spring will inject for me (with @Value annotation).

### Step 5. Test

And finally we can make a test for above implementation that will be:

```java
@RunWith(SpringJUnit4ClassRunner.class)
@ContextConfiguration(classes= LibraryConfig.class)
@WebAppConfiguration("src/main/java")
public class GoogleBookAPITest {

	@Autowired
	private GoogleBookService googleBookService;
	
	@Test
	public void givenAppContext_WhenAutowire_ThenClassesAreAvailble(){
		assertNotNull(googleBookService);
	}
	
	@Test
	public void givenBookService_WhenFindBook_ThenReceiveBooksList() {
		
		//given
		List<ItemAPIModel> list = null;
		//when
		list = googleBookService.searchBookList("game of thrones");
		//then
		System.out.println(list);
		assertNotNull(list);
	}
	
}
```

First, it tests if Google Books Service bean has been injected, and then if it retrieves a result for a search query *“game of thrones”*. Both tests passed and the outcome in the console is:

```bash
[
  ItemAPIModel(
    id=l6xMUQ88vLAC,
    volumeInfo=VolumeInfoModel(
      title=Re-Reading a Game of Thrones,
      authors=[Remy J. Verhoeve],
      publisher=Nimble Books LLC,
      publishedDate=2011-04,
      description=In 1996, George R.R. Martin electrified fantasy fans around the world when he published A Game of Thrones, the first book in his... //further description
      industryIdentifiers=[
        IsbnAPIModel(type=ISBN_13, identifier=9781608881154)
        IsbnAPIModel(type=ISBN_10, identifier=1608881156)
      ],
      pageCount=372,
      categories=[Literary Criticism],
      averageRating=5.0,
      imageLinks=ImageLinksAPIModel(thumbnail=http://books.google.com/books/content?id=l6xMUQ88vLAC&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api))),

///more results

]
```

As usual, here is a link to project source code:

[**wkrzywiec/Library-Spring** | github.com](https://github.com/wkrzywiec/Library-Spring)

## References

* [**A Beginner's Tutorial for Understanding RESTful API** | mlsdev.com](https://mlsdev.com/blog/81-a-beginner-s-tutorial-for-understanding-restful-api)
* [**How authorization works with APIs** | idratherbewriting.com](http://idratherbewriting.com/2015/09/04/authorizing-apis/)
* [**An Introduction to JSON | DigitalOcean** | digitalocean.com](https://www.digitalocean.com/community/tutorials/an-introduction-to-json)
* [**Retrofit** | square.github.io](https://square.github.io/retrofit/)
* [**Retrofit - Getting Started and Creating an Android Client** | futurestud.io](https://futurestud.io/tutorials/retrofit-getting-started-and-android-client)
* [**Using Retrofit 2.x as REST client - Tutorial** | vogella.com](http://www.vogella.com/tutorials/Retrofit/article.html)
* [**Introduction to Retrofit | Baeldung** | baeldung.com](http://www.baeldung.com/retrofit)
