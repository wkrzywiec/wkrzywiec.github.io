---
title: "What was added to Java 8? Streams"
date: 2018-11-18
summary: "Introduction to Streams from standard library from Java"
description: "Many programming tasks can be described as data processing i.e. we’ve got a collection of values which we want modify, like filter, transform or group. Until Java 8 this task was really painful (required multiple loops) and was not such efficient. Luckily there is new concept — Streams."
tags: ["java", "streams", "syntax-sugar"]
canonicalUrl: "https://wkrzywiec.medium.com/what-was-added-to-java-8-streams-1d1f86c0628f"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/what-was-added-to-java-8-streams-1d1f86c0628f).
{{< /alert >}}  


![Photo by [Samuel Sianipar](https://unsplash.com/@samthewam24?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/10422/0*HPS68K6O8U_93aOo)*Photo by [Samuel Sianipar](https://unsplash.com/@samthewam24?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*Many programming tasks can be described as data processing i.e. we’ve got a collection of values which we want modify, like filter, transform or group. Until Java 8 this task was really painful (required multiple loops) and was not such efficient. Luckily there is new concept — Streams.*

This is a three-part series on Java 8 new features, other blog posts can be found here:

* [Lambda expression](https://medium.com/@wkrzywiec/what-was-added-to-java-8-lambda-expressions-7b2735efb287)

* Streams (current)

* [Optional<T> class](https://medium.com/@wkrzywiec/what-was-added-to-java-8-optional-t-class-97d87728a537)

Java 8 introduced new pipeline-mechanism for data processing. It’s usually compared to pipeline or assembly line, because on start as an argument we provide a data collection and then we pass it thru the operations that will modify it and get another output.

To give you a picture of what stream capabilities are see below example. It compares the same task that was made with “standard” and stream based approach.

```java
List<Tshirt> tshirtCollection = shop.getTshirtCollection();
List<String> selectedTshirts = new ArrayList<String>();

// without Streams
for(Tshirt tshirt: tshirtCollection){
  if (tshirt.getColor().equals("RED")) {
   if (tshirt.getSize().equals("M")) {
    if (new BigDecimal(50).compareTo(tshirt.getPrice() > 0){
      selectedTshirts.add(tShirt.getName().toUpperCase());
   }
  }
}
        
//with Streams
tshirtCollection.stream()
        .filter(tshirt -> tshirt.getColor().equals("RED"))
        .filter(tshirt -> tshirt.getSize().equals("M"))
        .filter(tshirt -> new BigDecimal(50).compareTo(tshirt.getPrice() > 0)
        .map(s -> s.getName().toUpperCase())
        .collect(Collectors.toList());
```

Even if I haven’t introduce the syntax yet we can see major benefits already. First of all, the code is much simplier and cleaner. And even if we don’t know all the operators yet they’re easy to understand.

To cover all these tasks Oracle team introduced new package [java.util.stream](https://docs.oracle.com/javase/8/docs/api/java/util/stream/package-summary.html) that contains [Stream<T>](https://docs.oracle.com/javase/8/docs/api/java/util/stream/Stream.html) class. In above example method *stream()* was called on collection, which results in a *Stream<TShirt>* — it means that a stream of t-shirt objects has been created from their list 👕.

All methods related to Streams can be categorized into three groups:

* Stream producing methods,

* Stream operating methods (intermediate methods),

* Stream terminal methods.

### Stream producing methods

Before we can operate on the objects stream first we need to create it. With a Java update Oracle has added a new method to [Collection](https://docs.oracle.com/javase/8/docs/api/java/util/Collection.html) interface with a name ***stream()*** which converts object that implements this interface (like Lists, Maps or Sets) into the Stream.

The above statement indicates that only objects, like *ArrayList*, or *HashSet* can be converted into Stream.

We could also want to generate it from an array, using static method of the Arrays class — ***Arrays.stream(T[] array)***.

```java
String[] arrayOfExpressions = {"Hello World!", "Hi everyone!", "Good Morning!", "How u doin'?"};

Stream<String> streamfromArray = Arrays.stream(arrayOfExpressions);
```

If we don’t have a list of objects we can create an infinite stream of integers that will start from 2 and will be increment by 3. To do so we can use static method of the *Stream<T>* class — ***iterate()***.

```java
Stream<Integer> infiniteStream = Stream
                                  .iterate(2, i -> i + 3)
                                  .limit(10);
```

The ***limit()*** step is necessary to end the infinite loop and it tells that we want to obtain a stream of 10 elements.

Another way to create a stream is to use static ***generate()*** method of *Stream<T>* class. Below code will result in a 10-elements stream where each element is a *“text”* String.

```java
Stream<String> stream = Stream
                          .generate(() -> "text")
                          .limit(10);
```

### Stream operating methods (intermediate methods)

Once a stream is created we can perform multiple manipulation on it’s elements. The key concept for this is that we can create several operations that are chained together so they’re executed one after the another. It’s possible, because each operation returns a new instance of *Stream<T>* class.

Here is the list of some (but not all) operations that can be performed on the Stream:

* ***filter()***— works similarly to WHERE clause in the SQL, it filters elements that match condition.

```java
tshirtCollection.stream()
        .filter(tshirt -> tshirt.getColor().equals("RED"))
```

* ***map()*** — it’s used when we want to transform each element in a Stream. For example, when we want to extract a value from a field in an object (*name* from the Tshirt class) or convert one value to another (kilograms to pounds).

```java
Stream<String> tshirtNameStream = tshirtCollection.stream()
                                    .map(Tshirt::getName);

Stream<Double> tshirtPoundWeightStream = tshirtCollection.stream()
                                    .map(Tshirt::getKilogramWeight)
                                    .map(kg -> kg/2.205);
```

* ***flatMap()*** — this operation is very similar to *map()*, but it also perform “flatten” task. It’s required when a body of *map()* operation returns a list or an array of values (not a single value as it was previously). If we use *map()* operation to perform such task we would receive a Stream of the Streams, each for an each element in a result list. But if we use *flatMap()* all of these Streams will be combined into single Stream.

```java
String[] arrayOfExpressions = {"Hello World!", "Hi everyone!", "Good Morning!", "How u doin'?"};

Stream<Stream<String>> streamOfStreamsOfWords = Arrays.stream(arrayOfExpressions)
                                                  .map(exp -> exp.split("\\s+"));

Stream<String> streamOfWords = Arrays.stream(arrayOfExpressions)
                                                  .flatMap(exp -> exp.split("\\s+"));
```

* ***sorted()*** — works similar to ORDER BY clause in the SQL, it sorts elements ascending/descending. If we don’t provide any argument to this method, all records will be natural ordered ascending. But if we input ***Comparator.reverseOrder()*** as an argument it will be order descending.

```java
Stream<Integer> infiniteStream = Stream
                                  .iterate(2, i -> i + 3)
                                  .limit(10);

Stream<Integer> ascOrderedStream = infiniteStream.sorted();

Stream<Integer> dscOrderedStream = infiniteStream.sorted(Comparator.reverseOrder());
```

It might do a trick, when we need to sort Strings or digits, but if we won’t to order complex objects we need to create a Comperator object that will indicate which object field should be used for sorting.

```java
Stream<Tshirt> ascOrderedTshirts = tshirtCollection.stream()
                                    .sorted(Comparator.comparing(Tshirt::getSize));

Stream<Tshirt> dscOrderedTshirts = tshirtCollection.stream()
                                    .sorted(Comparator.comparing(Tshirt::getSize).reversed());
```

* ***distinct()*** — returns a Stream without any duplicate elements, all elements are unique.

### Stream terminal methods

After performing all these transformation operation on a Stream we want to see a result of it. Stream<T> class is just a wrapper so to get value from it we need to perform one of terminating actions listed below.

* ***collect()*** —Stream can be compared to a list of elements, so this operation is used to convert Stream to a list (or any other collection instance). By passing an argument to it (it’s [Collector](https://docs.oracle.com/javase/8/docs/api/java/util/stream/Collector.html) object) we can specify what will be the result.

For example, if we use static method ***Collector.toList()*** to get a list of objects, or using ***Collector.toSet()*** will result in Set object.

```java
List<Tshirt> redTshirtsList = tshirtCollection.stream()
                            .filter(tshirt -> tshirt.getColor().equals("RED"))
                            .collect(Collectors.toList());

Set<Tshirt> mediumTshirtSet = tshirtCollection.stream()
                                .filter(tshirt -> tshirt.getSize().equals("M"))
                                .collect(Collectors.toSet());
```

Apart from build-in Collector method we can use more sophisticated approach. We can use ***Collector.toColleaction()*** method we can specify a Collection object type (e.g. HashSet).

```java
Set<Tshirt> mediumTshirtSet = tshirtCollection.stream()
                                .filter(tshirt -> tshirt.getSize().equals("M"))
                                .collect(toCollection(HashSet::new));
```

But it’s not everything that we can do with this method. For example, we can group (like in SQL) results to get their count, max value by the specific field. Or we can sum all values from specific fields. These an other examples can be found in the [Oracle article](https://www.oracle.com/technetwork/articles/java/architect-streams-pt2-2227132.html).

* ***toArray()*** — works similar to previous one, but here it results in an array of objects, not a Collection.

* ***forEach()*** — with this method we don’t return any object (return type is void), but we can perform some action on each element that is in a Stream. For example we can print names in the console or perform an action on each of element.

```java
tshirtCollection.stream()
             .filter(tshirt -> tshirt.getColor().equals("RED"))
             .map(Tshirt::getName)
             .forEach(System.out::println);
```

And that’s it. With this article I’ve only touched the surface of Java Stream but it’s a good point to start with. If you want to know more check the official documentation and play around it to know all the capabilities that it can offer.

---

## References
* [**Processing Data with Java SE 8 Streams, Part 1** on oracle.com](https://www.oracle.com/technetwork/articles/java/ma14-java-se-8-streams-2177646.html)
* [**Part 2: Processing Data with Java SE 8 Streams** on oracle.com](https://www.oracle.com/technetwork/articles/java/architect-streams-pt2-2227132.html)
* [**The Java 8 Stream API Tutorial | Baeldung** on baeldung.com](https://www.baeldung.com/java-8-streams)
* [**Java 8: Replace traditional for loops with IntStreams** on deadcoderising.com](http://www.deadcoderising.com/2015-05-19-java-8-replace-traditional-for-loops-with-intstreams/)
