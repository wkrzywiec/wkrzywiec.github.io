---
title: "Full-text search with Hibernate Search (Lucene) — part 1"
date: 2018-05-06
summary: "Introduction to basic git operations used on a daily basis"
description: "How it happens that Google or any other browsers in on the websites know what I’ve meant by typing in a search bar? Clearly they are not using SQL approach, which is [table].[field] LIKE ‘query’. They are using special algorithms that, for me, are special kind of art and are called search engines. Basically it thanks to amazing search engine Google is nowadays the leader of IT sector. In my Library Portal project I want to take an advantage of some search engine to fetch users and books from database. Unfortunately, Google algorithm is their top secret asset, so I want be able to use it, but luckily there are other open-source engines, like Solr, Lucene and Elasticsearch that can be implemented with Hibernate."
tags: ["software", "tools", "git", "version-control-system"]
canonicalUrl: "https://wkrzywiec.medium.com/full-text-search-with-hibernate-search-lucene-part-1-e245b889aa8e"
---

![Photo by [Alex Block](https://unsplash.com/@alexblock?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/8504/0*uptWe3eK9q_vcDoK.)*Photo by [Alex Block](https://unsplash.com/@alexblock?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*How it happens that Google or any other browsers in on the websites know what I’ve meant by typing in a search bar? Clearly they are not using SQL approach, which is [table].[field] LIKE ‘query’. They are using special algorithms that, for me, are special kind of art and are called search engines. Basically it thanks to amazing search engine Google is nowadays the leader of IT sector. In my Library Portal project I want to take an advantage of some search engine to fetch users and books from database. Unfortunately, Google algorithm is their top secret asset, so I want be able to use it, but luckily there are other open-source engines, like Solr, Lucene and Elasticsearch that can be implemented with Hibernate.*

## Introduction

In this blog post I want to focus on implementing full-text search only for users, because it is more simple to do, so it gives me a quick start in Hibernate Search. Full-text search of books I’ll cover later one, in another post.

**Ok, so why to use some fancy full-text search feature?** Why I need this additional thing in my application, instead of using standard approach, which is SQL *LIKE* phrase?

As a users we have get used to one search box on the website or application. Also when we input our queries we sometimes made spelling errors that with ‘traditional’ approach would not give us results that we are looking for, because our app would search for exact match in the database. Another thing is that on the old-fashioned websites there are multiple search box, each related to a different field in the database, e.g. if we want to find a book we can looked for its title, author or ISBN, so each of book property will have own search box.

Moreover, full-text search analyze our data so it can more preciously match to the query. It matches sound-like word, e.g. “kat” and “cat”. Synonyms (“pretty”, “beautiful”) or word conjugations (“do”, “did”, “done”) are also considered as matching queries. Finally it can order results by relevance or even search for information in text filed (.docx/.pdf).

Of course there are some situations when multiple, non-full-text search is still useful, but in my project I would like to make use of this nice feature.

For *Library Portal* project I’ll use Hibernate Search, which extends *Hibernate ORM* (which is implementation of JPA) and integrates with *Apache Lucene.*

Ok, but how it works?

In general, full-text search depends on two tasks: indexing and searching. First database(or files) is scanned so all words present in it are listed with their indication (link), where they can be found. Once indexes are created searching can be performed. During performing specific query it is not connecting directly to the data source but to indexes, that has references to it, which next is converted to results that we receive as an output.

In next part I will try to focus showing a short walk-through full-text search engine capabilities and then I will move on to implementing it in my project.

## Indexing

As mentioned before first stage is indexing specific fields in the database. To do define them we use annotations in entity classes— @Indexed, @Field, @DateBridge, @IndexedEmbedded. First one, **@Indexed**, must be added on top of the class name, which will tell that these entity must be tokenized.

Next we need to declare which properties we would like to index using **@Field** annotation. In other words, here we declare fields on which we will be able to perform searching, so all skipped fields in entity classes will be omitted as search results. This annotation has several attributes that can be use to configure the indexing process, for example:

* **index** — indicates whether this field is indexed or not; by default value for this attribute is **Index.YES** (same output can be achieved by not annotating a field;

* **analyze** — indicates whether you want to analyze this field or not (in other words do you want to search this field as is or in more ‘intelligent’ way); by default value of this attribute is **Analyze.YES**;

* **store** — indicates whether actual data will be stored in index or not; by default value is **Store.NO**, which means that in index are stored only identifiers of matching entities, which are used to retrieve specific entity. If you choose **Store.YES** entity data will be indexed, so there will no need to query database for whole entity data (by this approach indexes will be bigger);

* **name** — indicates under which alias property will be stored; be default it will be property name, which matches JavaBeans convention.

Next thing comes up when we want to index field with a different type, then String. Apache Lucene indexes are String based, so Hibernate Search must convert other types of data to String, with taking into account that such field sorting might be different than in String.

To illustrate it, let’s assume that we have given array of integers: 2, 21, 11. After sorting them as number we would have the outcome: 2, 11, 21. But if we sort them as String we would get 11, 2, 21. Therefore for number use **@NumericField** together with @Field annotation. For dates use **@DateBridge** also with @Field. If it is necessary, you can define specific accuracy of date field. For example, they can be sorted by whole days or tiny milliseconds. To set up this there is an attribute resolution.

```java
import org.hibernate.search.annotations.*;

@Entity
@Table(name="user")
@Indexed
public class User {
  
  @Column(name="username")
  @Field
  private String username;

  @Column(name="email")
  @Field(index=Index.YES, analyze=Analyze.NO, store=Store.NO)
  private String email;
  
  @Field(index = Index.YES, analyze=Analyze.NO, store = Store.YES)
  @DateBridge(resolution = Resolution.DAY)
  private Date createDate;
  
}
```

Finally there is **@IndexedEmbedded** annotation that is used for fields that are associated with other entities. To make it more clear, in JPA we add fields that are responsible for relationship maintenance of database tables (marked with annotations @OneToOne, @OneToMany or @ManyToMany, etc.). So for example, when I index Book entity I’ll index fields like title or category, but also I will want to index author’s details that are represented by Author entity. So above field Author property I’ll add @IndexedEmbedded annotation to make sure that it will be indexes and associated to appropriate book. On Book entity side I will add @Field annotation to lastName field. NOTE — in this situation @Indexed annotation is not required!

Additionally **@ContainedIn** added on Book field in Author entity will make sure that when changes will be made on Author entity it will be reflected on Book indexes.

Finally @IndexedEmbedded has two important attributes that are used for configuration:

* **depth** — indicates depth of relationship indexing, so we can indicate to which level of object dependency we want to map; for example if we choose 1 as an argument, only next level entities will be considered to be indexed;

* **prefix** — string passed to this argument will override default naming convention of the field for building a query; by default, when we create a query, field names are the same as properties in entity class, but we can modify it

```java
import org.hibernate.search.annotations.*;


@Entity
@Table(name="user")
@Indexed
public class User {
  
  //other fields
  
  	@OneToOne()
	@JoinColumn(name="user_detail_id")
	@IndexedEmbedded(depth=1)
	private UserDetail userDetail;
}

@Entity
@Table(name="user_detail")
public class UserDetail {
  
  //other fields
 
	@ContainedIn
	private User user;
}
```

Once all entities are taged we need to initialize indexes for a data that are already in a database. It can be done using following Java code (in Spring):

```java
import javax.persistence.*;
import org.hibernate.search.jpa.*;

@PersistenceContext
private EntityManager entityManager;

FullTextEntityManager fullTextEntityManager = Search.getFullTextEntityManager(entityManager);
fullTextEntityManager.createIndexer().startAndWait();
```

After that indexes are present in initialized and from now on, when changes will be made in the database through Hibernate all indexes will be automatically updated. Please be aware that if you change data directly in database indexes won’t be updated. You need to explicitly tell Hibernate to updated it. More info can be found [here](https://docs.jboss.org/hibernate/stable/search/reference/en-US/html_single/#manual-index-changes).

## Searching

When we finally built indexes we can move on to building queries. Basic approach is to create a Lucene Query object and then wrap it into Hibernate Query Object and execute it.

First we need to get **FullTextEntityManager** object using JPA EntityManager (and this is injected by Spring context), from which we can get QueryBuilder, which will be used to build advanced queries. Here is the sample code.

```java

@Autowired
private EntityManager entityManager;

...

//inside UserDAO method

FullTextEntityManager fullTextEntityManager = Search.getFullTextEntityManager(entityManager);
	
QueryBuilder queryBuilder = fullTextEntityManager.getSearchFactory()
				                  .buildQueryBuilder()
				                  .forEntity(User.class)
				                  .get();
```

It important to provide the class of the entity that we would like to fetch from database in .forEntity(User.class) step.

Once the QueryBuilder is initiated, we could move on to fun part.

The simplest query would be as follows:

```java
org.apache.lucene.search.Query luceneQuery = queryBuilder
              .keyword()
              .onField("email")
              .matching("edard.stark@winterfell.com")
              .createQuery();
```

Parameter *.onField(“email”)* relates to a property with a name “email” and that was marked with annotation @Field.

If we want to get to the field that is in other table, but our current table has a relationship with it we can access it using prefix propertyName(main_class).propertyName (relation_class). In my case User class has One-To-One relation with UserDetail and I would like to search for last name of the user that is in UserDetail, so field name will be *userDetail.lastName.*

Second parameter is *.matching(“edard.stark@winterfell”) *that is the phrase that we want to look for in the database.

In above example query is hardcoded, but it can be omitted by passing it as a String object and concatenate with a wildcard (*). Also it is required to add *.wildcard()* step when query is build.

```java
org.apache.lucene.search.Query luceneQuery = queryBuilder
			.keyword()
			.wildcard()		//it is necessary if we want to make use of wildcards
			.onFields("username", "email", "userDetail.lastName")
				.boostedTo(5f)
			.andField("userDetail.firstName")
			.matching(searchText + "*")
			.createQuery();
```

In above code snipet there are some new parameters added. First one, *.onFields(…)* is the same as *.onField(…)*, but here we can provide multiple field names.

Next there is *.boostedTo(5f),*which is responsible for changing calculation of revelancy of marked fields. In mentioned query “username”, “email” and “userDetail.lastName” fields has 5-fold the weight relative to “userDetail.firstName” field.

Finally there is *.andField(…)*, again similar to *.onField(…) *but it usually used when we want to boost some fields.

Another cool feature is looking for values that are in a certain range. For example we would like to find users with IDs between 50 and 100. The query should like this:

```java
org.apache.lucene.search.Query luceneQuery = queryBuilder
			.keyword()
			.onField("id")
			.from(50).to(100)
			.createQuery();
```

It can be applied also to Strings or Dates.

## Sorting

By default our results will be order by relevancy, but we can override it. For example users wants to display books by the date of their release. To do that we need to create new Sort object and then add it to the query object.

```java
Sort sort = builder
  .sort()
    .byField("release_date")
    .andByField("title").desc()
  .createSort();

query.setSort(sort);
```

By default records are sorted ascending, but we can modify it by adding *.desc()* to the field, like it is shown on above example.

In some specific situations we don’t want to index entity fields, but we want to be able to sort by them (for example in case of entity ID). To achieve it we can use **@SortableField** annotation on a property in the entity class.

## Fuzzy Search

At this point I only want to make a note that Hibernate Search allows to configure and implement ‘intelligent’ search and it can be done via **@Analyzer** annotation. In this blog entry I don’t want to dive into this topic, as it won’t be useful for me for users search. Probably I will implement it in books search, but it is a story for another post.

In my Library Portal I wanted to have possibility to search for users and edit their profiles through the admin account. Therefore I’ve created a simple page that has single search box to find proper user. So let’s move on to my implementation of this concept.

## Creating index
### Step 1. Add dependencies to build.gradle file.

As usual, first I need to add some external libraries using build.gradle. I already had Hibernate core lib, so only search is required.

```gradle
compile 'org.hibernate:hibernate-search-orm:5.9.1.Final'
```

### Step 2. Config Hibernate and .gitignore file

Next I need to add two parameters for Hibernate that indicates where index files will be stored. I’ve added follwing lines to Sping properties.

    hibernate.search.default.directory_provider = filesystem
    hibernate.search.default.indexBase = FOLDER_PATH

I’ve decided to store them in a folder inside my project, but I don’t want to track these files with git, so new line was added to .gitignore file:

    /indexes/*

### Step 3. Create indexing procedure.

At a first time I need to index the data that are already in the database and to do that I need to run simple Java procedure. I’ve decided to run it during initialization of the Spring Context, therefore I’ve created new class that implements* ApplicationListener<ContextRefreshedEvent> *interface, so its method, onApplicationEvent, will be called when I start my application.

```java
import javax.persistence.*;
import javax.transaction.*;

import org.hibernate.search.jpa.*;
import org.springframework.context.ApplicationListener;
import org.springframework.context.event.ContextRefreshedEvent;
import org.springframework.stereotype.*;


@Component
public class UsersHibernateSearchInit implements ApplicationListener<ContextRefreshedEvent> {

	@PersistenceContext
	private EntityManager entityManager;
	

	@Override
	@Transactional
	public void onApplicationEvent(ContextRefreshedEvent event) {
		
		FullTextEntityManager fullTextEntityManager = Search.getFullTextEntityManager(entityManager);
		try {
			fullTextEntityManager.createIndexer().startAndWait();
		} catch (InterruptedException e) {
			System.out.println("Error occured trying to build Hibernate Search indexes "
					+ e.toString());
		}
	}
}
```

### Step 4. Add Hibernate Search annotations to entity classes.

I want to make only some of the User fields available to be search by. For example, I would like to find them by their email, or name, but I don’t want to do it by their address. For this reason only some of fields are marked with proper annotation. Here is the outcome:

```java
import javax.persistence.*;
import org.hibernate.search.annotations.*;

@Entity
@Table(name="user")
@Indexed
public class User {

	@Id
	@GeneratedValue(strategy=GenerationType.IDENTITY)
	@Column(name="id")
	private int id;
	
	@Column(name="username", unique=true)
	@Field
	private String username;
	
	@Column(name="password")
	private String password;
	
	@Column(name="email", unique=true)
	@Field
	private String email;
	
	@Column(name="enable")
	private boolean enable;
	
	@OneToOne(cascade=CascadeType.ALL)
	@JoinColumn(name="user_detail_id")
	@IndexedEmbedded(depth=1)
	private UserDetail userDetail;
  
  //getters and setters
}
```

```java

import javax.persistence.*;
import org.hibernate.search.annotations.*;

@Entity
@Table(name="user_detail")
public class UserDetail {

	@Id
	@GeneratedValue(strategy=GenerationType.IDENTITY)
	@Column(name="id")
	private int id;
	
	@Column(name="first_name")
	@Field
	private String firstName;
	
	@Column(name="last_name")
	@Field
	private String lastName;
	
	@Column(name="phone")
	private String phone;
	
	@Column(name="birthday")
	private Date birthday;
	
	@Column(name="address")
	private String address;

	@Column(name="postal")
	private String postalCode;
	
	@Column(name="city")
	private String city;
	
	@OneToOne(mappedBy="userDetail",
			cascade=CascadeType.ALL)
	@ContainedIn
	private User user;
  
  //getters and setters
}
```

### Step 5. Add new method to LibraryController class.

Once I’ve got it set up I could move to the controller, in which I would like to call UserService methods ( implementation in next step) to get:

* total number of users that match the query

* total number of pages (I don’t want to show all users on a single page, I prefer to divide them into several, where only 20 results are showed on a single page)

* list of users that match the query

To achive it, when query is provided in a search box it is passed to the HTTP Request Parameter (“search”), so it can be read from the controller method. During first call also “pageNo” paramert is initiated, which represents page number.

```java
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.wkrzywiec.spring.library.service.LibraryUserDetailService;

@Controller
public class LibraryController {
	
	public static final int USERS_PER_PAGE = 20;
	
	@Autowired
	LibraryUserDetailService userService;
  
  	@GetMapping("/admin-panel")
	public String showAdminPanel(	@RequestParam(value="search", required=false) String searchText,
					@RequestParam(value="pageNo", required=false) Integer pageNo,
					ModelMap model){
		
			if (searchText == null && pageNo == null) {
				return "admin-panel";
			}
			
			if (searchText != null && pageNo == null){
				pageNo = 1;
				model.put("pageNo", 1);
			}
			
			model.addAttribute("resultsCount", userService.searchUsersResultsCount(searchText));
			
			model.addAttribute("pageCount", userService.searchUserPagesCount(searchText, USERS_PER_PAGE));
			
			model.addAttribute("userList", userService.searchUsers(searchText, pageNo, USERS_PER_PAGE));
			return "admin-panel";
	}
```

### Step 6. Add new methods to the UserService class.

And here are new created methods in a service (first they were defined in a proper interface, that my class is implementing).

```java
@Service("userDetailService")
public class LibraryUserDetailService implements UserDetailsService, UserService {

  	@Autowired
	private UserDAO userDAO;
  
  	@Override
	public List<com.wkrzywiec.spring.library.entity.User> searchUsers(String searchText, int pageNo,
			int resultsPerPage) {
		
		List<com.wkrzywiec.spring.library.entity.User> userList = userDAO.searchUsers(searchText, pageNo, resultsPerPage);
		
		return userList;
	}

	@Override
	public int searchUserPagesCount(String searchText, int resultsPerPage) {
		
		long userCount = searchUsersResultsCount(searchText);
		int pageCount = (int) Math.floorDiv(userCount, resultsPerPage) + 1;
		
		return pageCount;
	}

	@Override
	public int searchUsersResultsCount(String searchText) {
		
		int userCount = userDAO.searchUsersTotalCount(searchText);
		
		return userCount;
	}
  
}
```

### Step 7. Add new methods to the UserDAO class.

As you see, above service class is making use of some DAO methods, which are:

```java
@Repository
public class UserDAOImpl implements UserDAO {

	@PersistenceContext
	private EntityManager entityManager;
  
  
  	@Override
	@Transactional
	public List<User> searchUsers(String searchText, int pageNo, int resultsPerPage) {
		
		FullTextQuery jpaQuery = searchUsersQuery(searchText);
		
		jpaQuery.setMaxResults(resultsPerPage);
		jpaQuery.setFirstResult((pageNo-1) * resultsPerPage);
		
		List<User> userList = jpaQuery.getResultList();
		
		return userList;
	}

	@Override
	@Transactional
	public int searchUsersTotalCount(String searchText) {
		
		FullTextQuery jpaQuery = searchUsersQuery(searchText);
		
		int usersCount = jpaQuery.getResultSize();
		
		return usersCount;
	}
	
	private FullTextQuery searchUsersQuery (String searchText) {
		
		FullTextEntityManager fullTextEntityManager = Search.getFullTextEntityManager(entityManager);
		QueryBuilder queryBuilder = fullTextEntityManager.getSearchFactory()
				.buildQueryBuilder()
				.forEntity(User.class)
				.get();
				
		org.apache.lucene.search.Query luceneQuery = queryBuilder
			.keyword()
			.wildcard()
			.onFields("username", "email", "userDetail.lastName")
				.boostedTo(5f)
			.andField("userDetail.firstName")
			.matching(searchText + "*")
			.createQuery();
		
		FullTextQuery jpaQuery = fullTextEntityManager.createFullTextQuery(luceneQuery, User.class);
		
		return jpaQuery;
	}
  
  }
```

### Step 8. Create JSP file responsible for visualization of the results list.

Because I’m bad front end developer I don’t want to embarrass myself with my lame JSPs (mainly beacause I’m not doing it correct), but it can be found [here](https://github.com/wkrzywiec/Library-Spring/blob/163fbbac65750b199cc665a2ba61fd4b80fc2ff6/src/main/webapp/WEB-INF/views/admin-panel.jsp), if you want to see the whole picture of the project.

Note that *Edit* button is not implemented yet.

### Step 9. Testing.

Everything is set up, so I can deployed my app, login into it as an admin and search for particular user.

![](https://cdn-images-1.medium.com/max/2724/1*M04EpLkH1mWVemPf7QzauA.png)

Link to my repository:
[**wkrzywiec/Library-Spring** | github.com](https://github.com/wkrzywiec/Library-Spring/tree/163fbbac65750b199cc665a2ba61fd4b80fc2ff6)

## Side story: SessionFactory vs EntityManager

When I was looking through the Internet for examples of Hibernate Search implementation I’ve found that all of them make use of EntityManager class for Object-Relational Mapping, instead of SessionFactory. When I’ve searched more deeply I’ve found that EntityManager is better to use, becasue it is a JPA standard and SessionFacotory is only Hibernate-specific. Therefore I’ve made few correction in the code. Here you can found all of them.

[**wkrzywiec/Library-Spring** | github.com](https://github.com/wkrzywiec/Library-Spring/tree/91cc4efd7b5165163983e91e4c14164cbb6d2776)

## References
* [**Full Text Search Engines vs. DBMS | Lucidworks** | lucidworks.com](https://lucidworks.com/2009/09/02/full-text-search-engines-vs-dbms/)
* [**Hibernate Search 5.9.1.Final: Reference Guide** | docs.jboss.org](https://docs.jboss.org/hibernate/stable/search/reference/en-US/html_single/)
* [**Getting started with Hibernate Search - Hibernate Search** | hibernate.org](http://hibernate.org/search/documentation/getting-started/)
* [**Introduction to Hibernate Search** | javaworld.com](https://www.javaworld.com/article/2077880/data-storage/data-storage-introduction-to-hibernate-search.html)
* [**Getting Started with Hibernate Search - DZone - Refcardz** | dzone.com](https://dzone.com/refcardz/getting-started-with-hibernate?chapter=1)
* [**Red Hat Customer Portal** | access.redhat.com](https://access.redhat.com/documentation/en-us/red_hat_jboss_data_grid/6.2/html/infinispan_query_guide/indexedembedded)
* [http://www.darksleep.com/lucene/](http://www.darksleep.com/lucene/)
