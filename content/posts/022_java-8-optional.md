
# What was added to Java 8? Optional<T> class
> Source: https://wkrzywiec.medium.com/what-was-added-to-java-8-optional-t-class-97d87728a537

*As a Java developer you’ve probably stomped on NullPointerException many times and usually handling this kind of error takes some time. Luckily thanks to new Optional class it’s much easier now.*

![“top view photography of mug with black liquid” by [Isaac Benhesed](https://unsplash.com/@isaacbenhesed?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/4884/0*eFP8QMp8QbojNSTA)*“top view photography of mug with black liquid” by [Isaac Benhesed](https://unsplash.com/@isaacbenhesed?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

This is a three-part series on Java 8 new features, other blog posts can be found here:

* [Lambda expression](https://medium.com/@wkrzywiec/what-was-added-to-java-8-lambda-expressions-7b2735efb287)

* [Streams](https://medium.com/@wkrzywiec/what-was-added-to-java-8-streams-1d1f86c0628f)

* Optional<T> class (current)

This class works as a class container (or wrapper) which may or may not hold null value. Before introducing Optional class developers to make sure that objects references aren’t null were forced to check it before calling any method (if there were a great chance for it, of course). To illustrate this, see below example.

```java
String pizzaRecipeText = "";
if (cookBook != null){
	Reciepes reiepes = cookBook.getRecipes();
		if (reciepes != null) {
			Reciepe pizzaReciepe = reciepes.getReciepe("Pizza");
			if (pizzaReciepe != null) {
				pizzaRecipeText = pizzaReciepe.getText();
		}
	}
}
```

Even if it’s a simple code it requires lots of boilerplate checking of nulls, which is not either fun to write or read. Also if we forget to check it, it becomes a potential *“dangerous”* part of a code.

So instead calling directly a class method that may or may not return null we can wrap it in Optional class.

```java
CookBook cookBook = new CookBook();
Optional<Reciepes> optReciepes = Optional.ofNullable(cookBook.getReciepes());

optReciepes.ifPresent(reciepes -> System.out.println(reciepes.getReciepe("Pizza")));
```

`CookBook` class doesn’t have `Reciepes` class unless at least one of them was added to it. Therefore, in above example `cookBook.getReciepes()` method will result with a null, which then would result in our favourite exception while getting any reciepe.

Instead we can wrap it with **Optional** class and use **ifPresent** method that checks it for us and if it’s available it’ll proceed. In above example `optReciepes` reference holds null so the 4th line of the code won’t result in printing pizza reciepe, but it also won’t result in **NullPointerException**.

What if we won’t to pass default value instead? We can use **orElse** method.

```java
CookBook cookBook = new CookBook();
Optional<Reciepes> optReciepes = Optional.ofNullable(cookBook.getReciepes());

Reciepes reciepes = optReciepes.orElse(new Reciepes());
Reciepe pizzaReciepe = Optional.ofNullable(reciepes.getReciepe("Pizza")).orElse(new Reciepe());
```

As it was earlier `optReciepes` holds null, but by invoking **orElse** method we create a default instance of a class. A default instance is passed as a parameter of this method.

Another approach for same situation would be throwing different exception, instead of returning a default value. Moving forward with an example, the `Reciepes` class does not have any reciepe yet, so when we call `reciepes.getReciepe("Pizza")` it should throw `ReciepeNotFoundException`.

```java
CookBook cookBook = new CookBook();
Optional<Reciepes> optReciepes = Optional.ofNullable(cookBook.getReciepes());

Reciepes reciepes = optReciepes.orElse(new Reciepes());
Reciepe pizzaReciepe = Optional.ofNullable(reciepes.getReciepe("Pizza")).orElseThrow(ReciepeNotFoundException::new);
```

Except for mentioned above methods to extract the data from the Optional objects we can make it more clear by using **map** operator. Like in below example:

```java
CookBook cookBook = new CookBook();
Optional<Reciepes> optReciepes = Optional.ofNullable(cookBook.getReciepes());

Long reciepesCount = optReciepes.map(Reciepes::getTotalCount);
```

Together with `map` function we can use a `filter` that will automatically reject the output of mapping if it won’t meet certain conditions.

```java
Optional<CookBook> optCookBook = Optional.ofNullable(kitchen.getBook("Italian"));

Optional<Reciepes> optReciepes = optCookBook.map(CookBook::getReciepes)
        .filter(reciepe -> "Pizza".equals(reciepe.getTitle()));
```

To sum up Optional class allows us to handle NullPointerException in more graceful way.

## References
* [**Tired of Null Pointer Exceptions? Consider Using Java SE 8's Optional!** on oracle.com](https://www.oracle.com/technetwork/articles/java/java8-optional-2175753.html)
* [**Guide To Java 8 Optional** on baeldung.com](https://www.baeldung.com/java-optional)
