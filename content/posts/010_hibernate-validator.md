---
title: "How to check if user exist in database using Hibernate Validator"
date: 2018-06-22
summary: "Input validation for database row modification using Hibernate"
description: "During work on my current project, Library Portal, I have encounter a problem with checking if a user is already in the database during registering new one, i.e. if her/his username or email is used by another user. There are many approaches to solve this, but I’ve decided to create custom Hibernate Validator annotation that will take care of this (as it is also taking care of other validation aspects in my application)."
tags: ["java", "database", "hibernate", "spring", "validation", "library-project"]
canonicalUrl: "https://wkrzywiec.medium.com/how-to-check-if-user-exist-in-database-using-hibernate-validator-eab110429a6"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/how-to-check-if-user-exist-in-database-using-hibernate-validator-eab110429a6).
{{< /alert >}}

![“A spread of various sliced fruits.” by [Brooke Lark](https://unsplash.com/@brookelark?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/7860/0*lChQ2_ikAmhCTGg_)*Photo by [Brooke Lark](https://unsplash.com/@brookelark?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*During work on my current project, Library Portal, I have encounter a problem with checking if a user is already in the database during registering new one, i.e. if her/his username or email is used by another user. There are many approaches to solve this, but I’ve decided to create custom Hibernate Validator annotation that will take care of this (as it is also taking care of other validation aspects in my application).*

## Overview

Before I start to explain how I want to achieve it, I’ll explain how I want to make it in my project. So, during registration on a website, *UserDTO* object is filled with the data provided by a user. Then, after hitting registration button, this object is send to the server that will take care of validation if all the inputs are correct, e.g. password length, empty fields, etc. And for this work can be achieved by adding Hibernate annotations to fields in the model class, for example by adding **@Size(min=5, max=45)** on username field we make sure that this field will contains Strings with a number of letters between 5 and 45. This and other annotations are provided by Hibernate Validator and their list can be found here:

* [**Hibernate Validator 6.0.10.Final - JSR 380 Reference Implementation: Reference Guide** | docs.jboss.org](https://docs.jboss.org/hibernate/stable/validator/reference/en-US/html_single/#section-builtin-constraints)
* [**Java Bean Validation Basics | Baeldung** | baeldung.com](http://www.baeldung.com/javax-validation)

Unfortunately there is no annotation for validation of the uniqueness of an email in the data store, but luckily Hibernate Validator allows to create own custom annotation that will cover this topic.

## Custom annotation

To achieve it first we need to create custom annotation class called UniqueEmail, it will be the name of annotation. It should looks like as follows:

```java
import java.lang.annotation.*;
import java.lang.annotation.*;
import javax.validation.*;

@Constraint(validatedBy = UniqueEmailValidator.class)
@Retention(RetentionPolicy.RUNTIME)
@Target({ ElementType.FIELD })
public @interface UniqueEmail {

	public String message() default "There is already user with this email!";
	
	public Class<?>[] groups() default {};
	
	public Class<? extends Payload>[] payload() default{};

}
```

This class is annotated as following:

* **@Constraint(…)** —indicates what class is implementing the constraint for validation, more about it is covered in next part of the post,

* **@Retention(…)** — in short, it indicates how long annotation will be making impact on our code (before or after compilation), in above case — RetentionPolicy.RUNTIME — it means that this annotation will be available after the runtime,

* **@Target(…)** — indicates where this annotation can be applied, i.e. on a class, field, method.

In the class body we need to declare all the parameters that can be add to annotation (like in previous example of @Size(…) annotation, where *“min”* and *“max”* arguments are present). In above example I decided to add only one parameter — message — that it responsible for displaying error message when email is already in use. By default it says: *“There is already user with this email!”.*

Other two methods are specific for validation, and are copy-pasted to make sure that it works.

## Custom validator

Once it is set up we need to create validator class that will contain whole constrains logic.

```java
import javax.validation.*;
import org.springframework.beans.factory.annotation.Autowired;
import com.wkrzywiec.spring.library.service.LibraryUserDetailService;

public class UniqueEmailValidator implements ConstraintValidator<UniqueEmail, String> {

	@Autowired
	private LibraryUserDetailService userService;

	@Override
	public boolean isValid(String value, ConstraintValidatorContext context) {
		return value != null && !userService.isEmailAlreadyInUse(value);
	}
}
```

Above class is implementing *ConstraintValidator<A extends Annotation,T>* interface that has only one method — *isValid(String value, ConstraintValidatorContext context)*. Above class declaration there is a @Component annotation that is Spring framework specific. Also user service object is injected to this class, which has a method called *isEmailAlreadyInUse(String email)* that is checking with the database if the email is used or not.

So this is it, no other steps are required. We have covered more or less unique email validation, so in next part I will show the whole implementation of unique username.

## Implementation 
### Step 1. Add dependencies to build.gradle

As usual, first we need to add dependencies to the project.

```gradle
compile 'org.hibernate:hibernate-validator:6.0.7.Final'
compile 'javax.validation:validation-api:2.0.1.Final'
```

### Step 2. Create annotation class

Next we create an annotation class.

```java
import static java.lang.annotation.ElementType.FIELD;
import static java.lang.annotation.ElementType.METHOD;
import static java.lang.annotation.RetentionPolicy.RUNTIME;

import java.lang.annotation.Retention;
import java.lang.annotation.Target;

import javax.validation.Constraint;
import javax.validation.Payload;

@Constraint(validatedBy = UniqueUsernameValidator.class)
@Retention(RUNTIME)
@Target({ FIELD, METHOD })
public @interface UniqueUsername {
	
	public String message() default "There is already user with this username!";
	
	public Class<?>[] groups() default {};
	
	public Class<? extends Payload>[] payload() default{};

}
```

### Step 3. Create validator class

And then a validator class, similar to previous one.

```java
import javax.validation.ConstraintValidator;
import javax.validation.ConstraintValidatorContext;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import com.wkrzywiec.spring.library.service.LibraryUserDetailService;

@Component
public class UniqueUsernameValidator implements ConstraintValidator<UniqueUsername, String>{

	@Autowired
	private LibraryUserDetailService userService;

	@Override
	public boolean isValid(String value, ConstraintValidatorContext context) {
		return value != null && !userService.isUsernameAlreadyInUse(value);
	}
}
```

### Step 4. Create appropriate methods in Service and DAO class

Validator class is making use of UserService class that also make use of UserDAO class to communicate with the database. It is not my intention to explain all the code how it works (I will cover it in some next blog posts), but I hope it is self-explanatory.

```java
@Service("userDetailService")
public class LibraryUserDetailService implements UserDetailsService, UserService {

  	@Override
	@Transactional
	public boolean isUsernameAlreadyInUse(String username){
		
		boolean userInDb = true;
		if (userDAO.getActiveUser(username) == null) userInDb = false;
		return userInDb;
	}
}
```

```java
@Repository
@Scope(proxyMode = ScopedProxyMode.INTERFACES)
public class UserDAOImpl implements UserDAO {

  	@Override
	public User getActiveUser(String username) {
		
		User user;
		
		try {
			user = (User) entityManager.createQuery("from User u where u.username = :username")
					.setParameter("username", username)
					.getSingleResult();
		} catch (NoResultException e) {
			user = null;
		}
		
		return user;
	}
}
```

And that’s it!

As usual, link to my project:

[**wkrzywiec/Library-Spring** | github.com](https://github.com/wkrzywiec/Library-Spring)

If you are looking for more of my posts related to Library Portal project check full list of entries here:

[**Library Portal — Spring Project Overview** | medium.com](https://medium.com/@wkrzywiec/library-portal-spring-project-overview-ddbf910dcb95)

## References

* [**Spring MVC Custom Validation | Baeldung** | baeldung.com](http://www.baeldung.com/spring-mvc-custom-validator)
* [**Unique Field Validation Using Hibernate and Spring** | codingexplained.com](https://codingexplained.com/coding/java/hibernate/unique-field-validation-using-hibernate-spring)
