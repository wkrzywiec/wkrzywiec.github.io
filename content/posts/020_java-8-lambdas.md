---
title: "What was added to Java 8? Lambda expressions"
date: 2018-11-05
summary: "Introduction to lambda expressions in Java"
description: "With this article I start a short series that will explain what features were added to Java 8 update. Today I’ll focus on the major buzz of this release — lambda expression (a.k.a. lambdas)."
tags: ["java", "lambda", "syntax-sugar"]
canonicalUrl: "https://wkrzywiec.medium.com/what-was-added-to-java-8-lambda-expressions-7b2735efb287"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/what-was-added-to-java-8-lambda-expressions-7b2735efb287).
{{< /alert >}}  

![“person standing on grass field near mountain” by [Iswanto Arif](https://unsplash.com/@iswanto?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/10368/0*UrWaLnPnSFgqFo_F)*Photo by [Iswanto Arif](https://unsplash.com/@iswanto?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*With this article I start a short series that will explain what features were added to Java 8 update. Today I’ll focus on the major buzz of this release — lambda expression (a.k.a. lambdas).*

These series will be divided into three parts (links will be updated once each blog post will be published):

* **Part 1**. *Lambda expression (this one)*

* **Part 2.** *Streams (soon)*

* **Part 3.** *Optional (soon)*

### Lambda expression

When you start to learn Java and you have already passed command line examples you probably wants to create a desktop application. And for this you probably use [JavaFX](https://en.wikipedia.org/wiki/JavaFX) library (at least it was my case).

In most of JavaFX applications we need to handle events that can be triggered by the users. For example, when they press a button it’ll create an Event object that need to be handled.

Therefore we need to assign an action which will be triggered once user click the button. For this task we usually declare [anonymous inner class](https://www.geeksforgeeks.org/anonymous-inner-class-java/), which has only one method that performs necessary actions.

```java
button.setOnAction(new EventHandler<ActionEvent>() {
       @Override
       public void handle(ActionEvent e) {
           System.out.println("Button clicked");
       }
});
```

Even if above code is pretty straightforward it requires lots of writing and when code starts to grow it’s also becomes hard to ready. Luckily, thanks to lambda expression we can write it in a more compact way:

```java
button.setOnAction( (e) -> System.out.println("Button clicked") );
```

Whoa! That’s short, but what’s going on there?

Lambda expression syntax is made of three parts. First one are brackets, `(e)` , that contains (or not) parameters of the abstract method of an *anonymous inner class*. **It’s really important to remember that lamdas can be used only when a single abstract method**.

In our case *ActionEvent* object is represented by `e` reference. If the method doesn’t have any parameter we can use simple `()` instead, like for [*Runnable*](https://docs.oracle.com/javase/8/docs/api/java/lang/Runnable.html) interface.

```java
Runnable r1 = () -> System.out.println("I'm in outside main thread!");
```

Finally method can have more than one arguments, like [Comperator<T>](https://docs.oracle.com/javase/8/docs/api/java/util/Comparator.html) interface method `compare`.

```java
Comparator<User> userComperator = 
(User first, User second) ->  first.email().compareTo(second.email());
```

In above example we could also don’t include argument types (User), but for clarity reasons it good to be added.

Next, after the arguments there is a newly introduce right arrow `->` operator.

And finally there is a body of the implemented method. Usually it’s a one line of code, but if we require more we can surround it with `{}` brackets.

```java
button.setOnAction( (e) ->  {
  System.out.println("Button clicked");
  label.setText("Clicked");
});
```

If a method should return a value we can use `return` statement as it’s in regular methods

### Method reference (::)

Another topic that is tightly related and was introduced together with lambda expression is referencing the method. In short, with new operator `::` we can assign method to a reference, just like the object or primitive type. This approach allow us to extract the method from the object and pass it in another place without executing them.

```java
Object objectInstance = new Object();
IntSupplier equalsMethodOnObject = objectInstance::hashCode;
System.out.println(equalsMethodOnObject.getAsInt());
```

Above we assign a *hashCode* method to a reference [IntSupplier](https://docs.oracle.com/javase/8/docs/api/java/util/function/IntSupplier.html). Then it can be passed wherever we want in the code.

With method reference we can also assign static methods (without creating instance of the class) or constructor.

### References

* [**Java 8: Lambdas, Part 1** on oracle.com](https://www.oracle.com/technetwork/articles/java/architect-lambdas-part1-2080972.html)
* [**Java Lambda Expressions** on tutorials.jenkov.com](http://tutorials.jenkov.com/java/lambda-expressions.html)
* [**Java 8 Method Reference: How to Use it** on codementor.io](https://www.codementor.io/eh3rrera/using-java-8-method-reference-du10866vx)
* [**JavaFX 8 Event Handling Examples** on code.makery.ch](https://code.makery.ch/blog/javafx-8-event-handling-examples/)
