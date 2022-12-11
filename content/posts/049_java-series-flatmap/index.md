---
title: "Java Series: Flatmap"
date: 2021-12-12
summary: "How and when to user flatmap function in Java stream"
description: ""
tags: ["java", "stream", "data", "java-series", "data-processing", "optional", "basic"]
---

{{< alert "link" >}}
This article is part of "Java Series", which covers useful Java functions from standard and popular Java libraries. More posts on that can be found [here](https://wkrzywiec.is-a.dev/tags/java-series/).
{{< /alert >}}

![Cover](jason-leung-V-HPvi4B4G0-unsplash.jpg)
> Cover image by [Jason Leung](https://unsplash.com/@ninjason) on [Unsplash](https://unsplash.com)

*Java 8 was a great step forward towards modern programing language. One of the key feature added in this release was Java streams. It provides convenient operations for data processing. One of them is a `flatMap()` used very widely to unwrap and merge multiple collections into one.*

## Problem statement

Many times when we work with Java code we end up with a following Plain Old Java Object (POJO):

```java
public record Parent(List<Child> childs) {}
```
They can represent entities from a database or data transfer objects (DTOs). In general they're used to structure data. Let's say that we got the list of `Parent` objects, but we want to operate on a list of all `Child` that are part of the `Parent`. How we could extract `Child` objects from all `Parent` objects and combine into a single list? The naive approach would be to use a loop:

```java
List<Child> children = new ArrayList<>();

for (Parent parent: parents) {
    List<Child> bs = parent.childs();
    children.addAll(bs);
}
```

But it doesn't look nice and clean. Instead we could use the Java stream:

This problem is even more severe when we would like to do it with Java stream, because it requires to end stream processing.

```java
List<Child> children = new ArrayList<>();

parents.stream()
    .map(parent -> parent.Childs())
    .forEach(list -> children.addAll(list));
```

But it has a drawback too. Let's say that once we get a list of all `Child` objects we would like to modify them, aggregate or do some calculations. Most of it can be achieved with a Java stream. Unfortunately the `forEach()` method in above example is ending the stream processing, which makes it impossible to process `Child` records in the same stream.

It would be nice chain all operations starting from a list of `Parent` objects till the modified `Child` objects in a single stream.

## Solution

Luckily Java creators foreseen this problem and introduced a `flatMap()` function that is part of a `java.util.stream.Stream` class.

The idea is pretty straight forward. It does two things with every element of a stream:

* maps - transforms one element from a stream into multiple streams, so as a result there would be a stream of streams,
* flattens - results of a previous operation are merged into a one stream.

To visualize it consider following situation:

![Map function](map-fx.png)

Let's say that we have a stream or `Author` objects, that has a methods called `books()` which returns a list of `Book` objects. And now let's say that we would like to have access to all books written by all authors to make further operations on them. If we would use the `map()` function within which we would call the `books()` method we would get a stream of lists of `Book` objects. This is not what we want to have. 

What we would like is a stream of `Book` objects, not stream of their lists. How we can overcome it? Using `flatmap()` instead:


![Flatmap function](flatmap-fx.png)

As previously we need to invoke `books()` method of `Author` class to get a list of `Books`. The only difference is that an input needs to be converted into multiple values represented by a Java stream. This is the requirement of the `flatMap()` method. Whatever operations we do within it needs to return a `Stream<T>` object.

The same situation can be reflected with a code:

```java
List<List<Book>> listsOfListOfBooks = authors.stream()
    .map(Author::books)
    .toList();

List<Book> listOfBooks = authors.stream()
    .flatMap(author -> author.books().stream())
    .toList();
```

To translate a list of `Book` objects the standard `Collection.stream()` method was used.


## When to use it?

### Unwrap & operate

The most common case when the `flatMap()` method might be handy is when one of the stream operations produces a collection of objects and we would like to make further actions on each one of them. 

To visualize it let's go back to the previous example with `Book` and `Author` records. Here are their definitions:


```java
public record Book(String title) {}
public record Author(String name, List<Book> books) {}
```

Now let's say that we want to create a method that takes a list of `Author` objects as an input and produces the list of all book titles that these authors wrote:


```java
List<String> getAllBookTitles(List<Author> authors) {
return authors.stream()
    .flatMap(author -> author.books().stream())
    .map(Book::title)
    .toList();
}
```

After making a list of `Author` a stream the `flatMap()` operation is used in which first the `books()` method is invoked to get their list and then it's changed into stream. The `flatMap()` is then merging all resulting streams into one so next the `title()` is called to get a String representation of a book title. Finally the results of each element in a stream is collected into the list.

Above method can be written a little bit different. We can split invoking `books()` and `stream()` methods into two operations - `map()` and `flatMap()` respectively - to get a nice looking code: 

```java
List<String> getAllBookTitles(List<Author> authors) {
return authors.stream()
    .map(Author::books)
    .flatMap(List::stream)
    .map(Book::title)
    .toList();
}
```

### Merge lists

Another case when `flatMap()` can be very useful is when we would like to combine two or more lists (or any other `java.util.Collection`).

```java
List<String> mergeLists(List<String> left, List<String> right) {
return Stream.of(left, right)
    .flatMap(List::stream)
    .toList();
}
```

A big plus for this approach is that after `flatMap()` we don't need to close the stream immediately. Instead we can apply other operations on every object, like filtering, mapping, aggregating etc. Which makes it cleaner and more efficient.

how java stream is processed and efficient

### Get value from nested Optional

Apart from Java streams `flatMap()` method can be invoked on an `Optional` object. It's used to unwrap an `Optional` from inside another `Optional`. 

Let's say that we've got a following record:

```java
public record Address(String street, String buildingNo, Optional<String> apartmentNo) {}
```

Now suppose we would have an `Optional<Address>` and would like to extract a value of an `apartmentNo` the code without `flatMap()` could look like this:

```java
String extractApartmentNo(Optional<Address> address) {
    if (address.isEmpty()) {
        return "";
    }

    return address.get().apartmentNo().orElse("");
}
```

First step is to unwrap value from the `Optional`, which might be empty. Only after checking it we can proceed with unwrapping (and handling empty values) an apartment address. 

This approach is ok, but can be done better with `flatMap()`:

```java
String extractApartmentNo(Optional<Address> address) {
return address
        .flatMap(Address::apartmentNo)
        .orElse("");
}
```

This approach is much cleaner. Both Optionals - parent and child - are validated wheather they hold a `null` value in a single expression. 

## Summary

Introducing streams into Java made Data processing easier. It brings us a lot of handy operations. `flatMap()` is one of them which gives us a possibility to merge multiple streams into one or flatten a nested streams into a one. It's a very common pattern and is used many times in a real projects.  

## References

* [Part 2: Processing Data with Java SE 8 Streams | Oracle.com](https://www.oracle.com/java/technologies/architect-streams-pt2.html)
* [Interface Stream<T> | Docs Oracle.com](https://docs.oracle.com/javase/8/docs/api/java/util/stream/Stream.html#flatMap-java.util.function.Function-)
* [Tired of Null Pointer Exceptions? Consider Using Java SE 8's "Optional"! | Oracle.com](https://www.oracle.com/technical-resources/articles/java/java8-optional.html)