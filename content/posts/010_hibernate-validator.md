
# How to check if user exist in database using Hibernate Validator
> Source: https://wkrzywiec.medium.com/how-to-check-if-user-exist-in-database-using-hibernate-validator-eab110429a6

During work on my current project, Library Portal, I have encounter a problem with checking if a user is already in the database during registering new one, i.e. if her/his username or email is used by another user. There are many approaches to solve this, but I’ve decided to create custom Hibernate Validator annotation that will take care of this (as it is also taking care of other validation aspects in my application).

![“A spread of various sliced fruits.” by [Brooke Lark](https://unsplash.com/@brookelark?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/7860/0*lChQ2_ikAmhCTGg_)*“A spread of various sliced fruits.” by [Brooke Lark](https://unsplash.com/@brookelark?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

## Table of content

### How it works?

* [Overview](https://medium.com/p/ad71319c35d5#0beb)

* [Custom annotation](https://medium.com/p/eab110429a6#5791)

* [Custom validator](https://medium.com/p/eab110429a6#3c81)

### Code writting

* [Step 1. Add dependencies to build.gradle](https://medium.com/p/eab110429a6#fb9f)

* [Step 2. Create annotation class](https://medium.com/p/eab110429a6#60b1)

* [Step 3. Create validator class](https://medium.com/p/eab110429a6#8474)

* [Step 4. Create appropiate methods in Service and DAO class](https://medium.com/p/eab110429a6#8ccf)

### Overview

Before I start to explain how I want to achieve it, I’ll explain how I want to make it in my project. So, during registration on a website, *UserDTO* object is filled with the data provided by a user. Then, after hitting registration button, this object is send to the server that will take care of validation if all the inputs are correct, e.g. password length, empty fields, etc. And for this work can be achieved by adding Hibernate annotations to fields in the model class, for example by adding **@Size(min=5, max=45) **on username field** **we make sure that this field will contains Strings with a number of letters between 5 and 45. This and other annotations are provided by Hibernate Validator and their list can be found here:
[**Hibernate Validator 6.0.10.Final - JSR 380 Reference Implementation: Reference Guide**
*Hibernate Validator, Annotation based constraints for your domain model - Reference Documentation*docs.jboss.org](https://docs.jboss.org/hibernate/stable/validator/reference/en-US/html_single/#section-builtin-constraints)
[**Java Bean Validation Basics | Baeldung**
*In this quick article, we'll go over the basics of validating a Java bean with the standard framework - JSR 380, also…*www.baeldung.com](http://www.baeldung.com/javax-validation)

Unfortunately there is no annotaion for validation of the uniqueness of an email in the data store, but luckily Hibernate Validator allows to create own custom annotation that will cover this topic.

### Custom annotation

To achieve it first we need to create custom annotation class called UniqueEmail, it will be the name of annotation. It should looks like as follows:

<iframe src="https://medium.com/media/fe5190c46729a8c2b1b01696034c85ec" frameborder=0></iframe>

This class is annotated as following:

* **@Constraint(…)** —indicates what class is implementing the constraint for validation, more about it is covered in next part of the post,

* **@Retention(…)** — in short, it indicates how long annotation will be making impact on our code (before or after compilation), in above case — RetentionPolicy.RUNTIME — it means that this annotation will be available after the runtime,

* **@Target(…) **— indicates where this annotation can be applied, i.e. on a class, field, method.

In the class body we need to declare all the parameters that can be add to annotation (like in previous example of @Size(…) annotation, where *“min”* and *“max”* arguments are present). In above example I decided to add only one parameter — message — that it responsible for displaying error message when email is already in use. By default it says: *“There is already user with this email!”.*

Other two methods are specific for validation, and are copy-pasted to make sure that it works.

### Custom validator

Once it is set up we need to create validator class that will contain whole constrains logic.

<iframe src="https://medium.com/media/1390bfb70f262cb0eb727c516033c9e2" frameborder=0></iframe>

Above class is implementing *ConstraintValidator<A extends Annotation,T> *interface that has only one method — *isValid(String value, ConstraintValidatorContext context)*. Above class declaration there is a @Component annotation that is Spring framework specific. Also user service object is injected to this class, which has a method called *isEmailAlreadyInUse(String email) *that is checking with the database if the email is used or not.

So this is it, no other steps are required. We have covered more or less unique email validation, so in next part I will show the whole implementation of unique username.

### Step 1. Add dependencies to build.gradle

As usual, first we need to add dependencies to the project.

<iframe src="https://medium.com/media/cd725636163c7ba1385328619eaa3fde" frameborder=0></iframe>

### Step 2. Create annotation class

Next we create an annotation class.

<iframe src="https://medium.com/media/80548ccfa673116a875f2825761cc010" frameborder=0></iframe>

### Step 3. Create validator class

And then a validator class, similar to previous one.

<iframe src="https://medium.com/media/297c336bd3e1f34253a7f149a351ebb8" frameborder=0></iframe>

### Step 4. Create appropriate methods in Service and DAO class

Validator class is making use of UserService class that also make use of UserDAO class to communicate with the database. It is not my intention to explain all the code how it works (I will cover it in some next blog posts), but I hope it is self-explanatory.

<iframe src="https://medium.com/media/b530aed4d810b19c880fd2d268c66d23" frameborder=0></iframe>

<iframe src="https://medium.com/media/b8589a83dadc468310b7720c65440a28" frameborder=0></iframe>

And that’s it!

As usual, link to my project:
[**wkrzywiec/Library-Spring**
*Library-Spring - The library website where you can borrow books.*github.com](https://github.com/wkrzywiec/Library-Spring)

If you are looking for more of my posts related to Library Portal project check full list of entries here:
[**Library Portal — Spring Project Overview**
*Hi Everyone!*medium.com](https://medium.com/@wkrzywiec/library-portal-spring-project-overview-ddbf910dcb95)

## References
[**Spring MVC Custom Validation | Baeldung**
*Generally, when we need to validate user input, Spring MVC offers standard predefined validators. However, when we need…*www.baeldung.com](http://www.baeldung.com/spring-mvc-custom-validator)
[**Unique Field Validation Using Hibernate and Spring**
*There are quite a few approaches to validating whether or not a given value already exists in a data store or not. In…*codingexplained.com](https://codingexplained.com/coding/java/hibernate/unique-field-validation-using-hibernate-spring)
