---
title: "Project Lombok — how to make your model class simple"
date: 2018-05-27
summary: "Get rid of boilerplate code with Lombok"
description: "Many Java frameworks nowadays requires to access Object values through standard getter/setter approach. It’s not recommended to create public fields through which we can access, but through these standard methods, so we have control of what data can come in and out from the Object. Another thing good to add, especially to model class, are toString() and hashCode() methods used to differ Object instances of the same class. These recommendations results in multiline code of even simple class. Also when we want to update such classes it will require to re-write comparing methods, which is time consuming and not really creative. Luckily there is Project Lombok!"
tags: ["java", "lombok", "library-project"]
canonicalUrl: "https://wkrzywiec.medium.com/project-lombok-how-to-make-your-model-class-simple-ad71319c35d5"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/project-lombok-how-to-make-your-model-class-simple-ad71319c35d5).
{{< /alert >}}

![No, not this kind of Lombok (Indonesian island) :( (by [Jeremy Bishop](https://unsplash.com/@tentides?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral))](https://cdn-images-1.medium.com/max/10944/0*fAF519zfEY1MVSJz.) *Photo by [Jeremy Bishop](https://unsplash.com/@tentides?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*Many Java frameworks nowadays requires to access Object values through standard getter/setter approach. It’s not recommended to create public fields through which we can access, but through these standard methods, so we have control of what data can come in and out from the Object. Another thing good to add, especially to model class, are toString() and hashCode() methods used to differ Object instances of the same class. These recommendations results in multiline code of even simple class. Also when we want to update such classes it will require to re-write comparing methods, which is time consuming and not really creative. Luckily there is Project Lombok!*

## How it works?

Lombok is relatively small project that using special annotations insert boilerplate parts of code. In contrast to similar solutions Lombok is not using reflection, but all these methods are generated automatically during compilation.

And that’s it! Whole philosophy!

Ok, ok, ok…By what is boilerplate code? In short it is some part of the code that is necessary to be added (e.g. by frameworks), but such code is really long (verbose), repeatable and boring to maintain. Such as getters/setter, equals and these kind of stuff.

Alright, so let me show you some examples.

### @Getter/@Setter

First one are the most obvious. By adding @Getter and @Setter annotation we don’t need to worry about those methods, which drastically shorten the model class.

```java
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class User {
  
  private String username;
  private String email;
  private String firstName;
  private String lastName;
}
```

### @EqualsAndHashCode

Another nice thing to add model class are equals() and hashCode() methods that are used to identify unique instances of the class. By default all objects inherit them from Object class, but it is a good practice to override them.

```java
import lombok.EqualsAndHashCode;

@EqualsAndHashCode
public class User {
  
  private String username;
  private String email;
  private String firstName;
  private String lastName;
}
```

### @ToString annotation

Another good thing is to override toString methods that returns text representation of the class. Usually it will be values of all its fields. Using Lombok we can generate it using one annotation and if you want to exclude some of them we can provide it in *exclude *parameter. As an argument of this parameter must be provided field name.

```java
import lombok.ToString;

@ToString(exclude="email")
public class User {
  
  private String username;
  private String email;
  private String firstName;
  private String lastName;
}
```

### @NoArgsConstructor

Last annotation that I want to mention is used for auto generating class constructor with no arguments. By default Java compiler is inserting it for you unless you have already implement any other constructor. For example, if you declare constructor that has some arguments it means that compiler won’t implicitly declare no-args constructor for you. You need to do it on your own. And for this reason we can add this annotation.

```java
import lombok.NoArgsConstructor;

@NoArgsConstructor
public class User {
  
  private String username;
  private String email;
  private String firstName;
  private String lastName;
}
```

### Other annotations

Above annotations that I wanted to make a use in my project. But there some other cool stuff, like:

* @NonNull — this annotation removes necessity of add checking of null within method,

* @Log — there are several variants of using it by in short it creates a Logger object for us (there is Log4j2 variant),

* @Data — this annotation combines @Getter, @Setter, @ToString, @EqualsAndHashCode and @RequiredArgsConstructor into one. The last one generates constructor with all final fields.

## Usage

### Step 1. Install Project Lombok plugin in Eclipse

In my project I use Eclipse IDE, which requires external plugin installation (it is not available through Marketplace). If you use Intellij (which I should switch to) it will be a lot simplier, instructions could be found on [official website](https://projectlombok.org/setup/intellij).

To get installation file go to [official website](https://projectlombok.org/setup/eclipse) and download installation file. Double click on it and select Eclipse directory. It should found it for you, but you can also manually point the path. Then follow the instructions (it should be really quick).

**Side story.** During this step I’ve faced some difficulties with save/update privileges of destination folder (Program files in Windows). Unfortunately the OS doesn’t allow me to install it on default location. I’ve tried to overcome it by installing it through command line, but with no success. Finally I’ve decided to move Eclipse folder to new one, which is not so restricted, and also updated Eclipse to Oxygen version, which I was delaying for a quite time. So that’s a good implication of above problem😊.

### Step 2. Add dependencies

Next I’ve added below line to *build.gradle* file.

```bash
compileOnly 'org.projectlombok:lombok:1.16.20'
```

### Step 3. Annotate model class

After that I’ve created some model classes that were annotated with necessary annotations. In below example I present User class, which was set up in a standard way (getters/setters, equals, no argument constructor), but toString() method should not show password (which is encrypted, but still it is not good idea to expose it).

```java
@Getter
@Setter
@EqualsAndHashCode
@ToString(exclude="password")
@NoArgsConstructor
public class User {

	private int id;
	private String username;
	private String password;
	private String email;
	private boolean enable;
	private String firstName;
	private String lastName;
	private String phone;
	private Date birthday;
	private String address;
	private String postalCode;
	private String city;
	private Timestamp recordCreated;

}
```

And that’s it! It will generate all the boring stuff for us! Just imagine, how long would be this class, if I won’t use it. Creating model classes can be fun again!

As usual, link to my project:

[**wkrzywiec/Library-Spring** | github.com](https://github.com/wkrzywiec/Library-Spring/tree/7260c81cd7cb48486e22d3ee388cef143698fa44)

## References

* [**Project Lombok** | projectlombok.org](https://projectlombok.org/)
* [**Introduction to Project Lombok | Baeldung** | baeldung.com](http://www.baeldung.com/intro-to-project-lombok)
* [**How to write less and better code, or Project Lombok** | codeburst.io](https://codeburst.io/how-to-write-less-and-better-code-or-project-lombok-d8d82eb3e80a)
