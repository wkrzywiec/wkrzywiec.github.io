---
title: "Implementing OAuth 2.0 access token validation with Spring Security"
date: 2021-03-15
summary: "Validate JWT in Spring Boot application"
description: "Would you like to know some basic concepts of Spring Security that can be implemented in a modern, micorservice application? If so this article is for you! In it I'll guide you how to add step-by-step OAuth 2.0 access token validation to REST API endpoints of your Spring Boot application."
tags: ["oauth2", "authorization", "authentication", "security", "keycloak", "jwt", "java", "spring-boot"]
canonicalUrl: "https://wkrzywiec.medium.com/implementing-oauth-2-0-access-token-validation-with-spring-security-64c797b42b36"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/implementing-oauth-2-0-access-token-validation-with-spring-security-64c797b42b36).
{{< /alert >}}

![Cover](https://miro.medium.com/max/2400/0*QjMKXAltDg8GiEeY)
> Cover image by [Lucas Gallone](https://unsplash.com/@lucasgallone) on [Unsplash](https://unsplash.com)

*Would you like to know some basic concepts of Spring Security that can be implemented in a modern, micorservice application? If so this article is for you! In it I'll guide you how to add step-by-step OAuth 2.0 access token validation to REST API endpoints of your Spring Boot application.*

This is part 3 of my series on OAuth 2.0 in which I'm describing how *OAuth 2.0* works and give an example implementations of key actors. If you're looking for theoretical introduction to it, go check my first blog post. 

In a second article of this series I've described how to set a Keycloak server which works as an authorization server and in short is responsible for issuing an access token. It's not necessary for you to read a previous article, but be aware that you might require to do that if you would like to manually test the authorization logic of what will be build in this post.

After this introduction, let me described what will be build in this post.

## Movies backend application

To make it simple I've prepared a small Spring Boot application which servers two REST endpoints to the outside world:

```java
@RestController
public class MovieController {

    Map<Long, Movie> movies;

    public MovieController() {
        movies = Map.of(
                1L, new Movie("Star Wars: A New Hope", "George Lucas", 1977),
                2L, new Movie("Star Wars: The Empire Strikes Back", "George Lucas", 1980),
                3L, new Movie("Star Wars: Return of the Jedi", "George Lucas", 1983));
    }

    @GetMapping("/movies")
    public List<Movie> getAllMovies(){
        return new ArrayList<>(movies.values());
    }

    @GetMapping("/movies/{id}")
    public Movie getMovieById(@PathVariable("id") String id){
        return movies.get(Long.valueOf(id));
    }
}
```

First one `/movies` provide a list of all movies and the latter, `movies/{id}`, provides a single movie information if you provide it's `id`. Quite simple.

And now the goal is to protect both endpoints so only authorized user and external applications (clients) can use them. To achieve it we will force all consumers of the API to provide a valid JWT access token in each request.

> And what does it mean a valid access token? 

The answer to this question would be probably different and depends on a case, but for my simple project, a valid token is when:

* its type is JWT,
* its signature is correct (it assures that nobody has changed a content of a token),
* it's not expired,
* it contains roles and scopes information.

A valid token is not everything. In order to consume each of these endpoint inside the access token a certain role should be present. In example, only users with `ADMIN` role should be allowed to get information from the `/movies` endpoint and only users with `VISITOR` role can get information from a second endpoint. Therefore I would like to establish a different validation which will check if certain role is present inside an access token.

And these are all features that will be covered in this article, so let's start implementing it!

## Access token validation with Spring Security

Like many other problems this one could be resolved in many ways. For instance it would be possible to not use Spring Security at all and implement everything from the scratch. Another approach would be to use some additional library, built on top of the Spring Security which would magicaly do most of the job, but possibly it won't allow to do some custom stuff.

For learning purposes I've decided to do something in the middle. I'll use Spring Security, but most of a configuration and validation I'll do by myself. If you think that my approach add complexity, you're probably right. After all I could use some open sourced libraries, like [keycloak-spring-boot-starter](https://github.com/keycloak/keycloak-documentation/blob/master/securing_apps/topics/oidc/java/spring-boot-adapter.adoc) or [spring-boot-starter-oauth2-resource-server](https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-starter-oauth2-resource-server), which would do the job with only couple lines of code. But again, this project was for me to learn something new and in your project you can select the solution that is the most suitable for you.

Ok, enough of all these explanations and introductions, let's code something!

First step, would be to add Spring Boot Security starter dependency to the **pom.xml** (if you use Maven):

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
	<artifactId>spring-boot-starter-security</artifactId>
	<version>2.3.4.RELEASE</version>
</dependency>
```

If you now run the application and try to use one of the endpoints, let's say `/movies`, you will be redirected to the login page:

![login page](https://dev-to-uploads.s3.amazonaws.com/i/3og3f3qvo8ucmsmk3ecw.png)

Cool! By simply adding this library our endpoint is now secured! Only authorized can use this endpoint. But is it what we would like to achieve? Is it OAuth 2.0 approach? Unfortunately not.

Before going to the solution let's first add necessary libraries right away:

```xml
<!-- OAuth 2.0 dependencies -->
<dependency>
    <groupId>com.auth0</groupId>
	<artifactId>java-jwt</artifactId>
	<version>3.11.0</version>
</dependency>
<dependency>
	<groupId>com.auth0</groupId>
	<artifactId>jwks-rsa</artifactId>
	<version>0.15.0</version>
</dependency>

<!-- Utils dependencies -->

<dependency>
	<groupId>org.zalando</groupId>
	<artifactId>logbook-spring-boot-starter</artifactId>
	<version>2.4.1</version>
</dependency>
<dependency>
	<groupId>org.projectlombok</groupId>
	<artifactId>lombok</artifactId>
	<version>1.18.12</version>
	<optional>true</optional>
</dependency>
<dependency>
	<groupId>com.google.code.gson</groupId>
	<artifactId>gson</artifactId>
	<version>2.8.6</version>
</dependency>
<dependency>
	<groupId>com.google.guava</groupId>
	<artifactId>guava</artifactId>
	<version>30.0-jre</version>
</dependency>
```

So how to tackle this problem? We need to change a default Spring Security configuration but first let me briefly explain the concept of `Filters`.

The main idea behind filter in Spring Security is build on top of the aspect-oriented programming, in Spring it's Spring AOP. In short, when any HTTP request is received by an application first thing that Spring does is it pass it first to the one or many filters (FilterChain). Those filters are components that can validate incoming request and block it if something is not right, so that the request will never reach a controller.

Therefore our task is quite simple - create a new filter that will check if in the incoming request there is an **Authorization** header and then validates if it contains access token in a proper format.

Our custom filter needs to extend `AbstractAuthenticationProcessingFilter` class and override two methods: `attemptAuthentication` and `successfulAuthentication`.

```java
class AccessTokenFilter extends AbstractAuthenticationProcessingFilter {


    @Override
    public Authentication attemptAuthentication(HttpServletRequest request,
                                                HttpServletResponse response) {

        // here will be logic for validating incoming request
    }

    @Override
    protected void successfulAuthentication(HttpServletRequest request,
                                            HttpServletResponse response,
                                            FilterChain chain,
                                            Authentication authResult) throws IOException, ServletException {

    
        // here will be the logic if authentication finshed successfully
    }
}
```

Both methods name are self explanatory, but in short in a first one we will put a logic for validating if in an incoming request there is valid access token and in the second one there will be the logic of what will be done when the authentication ends with success.

And here is the implementation of both methods:

```java
@Slf4j
class AccessTokenFilter extends AbstractAuthenticationProcessingFilter {

    private final JwtTokenValidator tokenVerifier;

    public AccessTokenFilter(
            JwtTokenValidator jwtTokenValidator,
            AuthenticationManager authenticationManager) {

        super(AnyRequestMatcher.INSTANCE);
        setAuthenticationManager(authenticationManager);
        this.tokenVerifier = jwtTokenValidator;
    }

    @Override
    public Authentication attemptAuthentication(HttpServletRequest request,
                                                HttpServletResponse response) {

        log.info("Attempting to authenticate for a request {}", request.getRequestURI());

        String authorizationHeader = extractAuthorizationHeaderAsString(request);
        AccessToken accessToken = tokenVerifier.validateAuthorizationHeader(authorizationHeader);
        return this.getAuthenticationManager()
                            .authenticate(new JwtAuthentication(accessToken));
    }

    @Override
    protected void successfulAuthentication(HttpServletRequest request,
                                            HttpServletResponse response,
                                            FilterChain chain,
                                            Authentication authResult) throws IOException, ServletException {

        log.info("Successfully authentication for the request {}", request.getRequestURI());

        SecurityContextHolder.getContext().setAuthentication(authResult);
        chain.doFilter(request, response);
    }

    private String extractAuthorizationHeaderAsString(HttpServletRequest request) {
        try {
            return request.getHeader("Authorization");
        } catch (Exception ex){
            throw new InvalidTokenException("There is no Authorization header in a request", ex);
        }
    }
}
```

Starting from the top you can see that this class requires two other dependencies, provided in the constructor - `JwtTokenValidator` and `AuthenticationManager`. First one is a custom class that encapsulates entire logic of validating access token, I'll show it just in a minute. The second is a Spring Security interface which is responsible for processing of `Authentication` object that is a result of `attemptAuthentication` if everything went successful. I'll mention it once again, when we'll move to configuration, but now, let's move on to the `JwtTokenValidator`.

The only public method of the validator is `validateAuthorizationHeader` in which we need to pass a content of the *Authorization* header that should be part of the incoming request.

```java
public class JwtTokenValidator {

    public AccessToken validateAuthorizationHeader(String authorizationHeader) throws InvalidTokenException {
        String tokenValue = subStringBearer(authorizationHeader);
        validateToken(tokenValue);
        return new AccessToken(tokenValue);
    }

    ... //other, private methods

}
```

The result of a validation is an `AccessToken` object, which is a holder of a raw token, plus it has a helper method that returns a `Collection` of `GrantedAuthorities`, in our case Keycloak roles. 

```java
@RequiredArgsConstructor
public class AccessToken {

    public static final String BEARER = "Bearer ";

    private final String value;

    public String getValueAsString() {
        return value;
    }

    public Collection<? extends GrantedAuthority> getAuthorities() {
        DecodedJWT decodedJWT = decodeToken(value);
        JsonObject payloadAsJson = decodeTokenPayloadToJsonObject(decodedJWT);

       return StreamSupport.stream(
                payloadAsJson.getAsJsonObject("realm_access").getAsJsonArray("roles").spliterator(), false)
                .map(JsonElement::getAsString)
                .map(SimpleGrantedAuthority::new)
                .collect(Collectors.toList());
    }

    private DecodedJWT decodeToken(String value) {
        if (isNull(value)){
            throw new InvalidTokenException("Token has not been provided");
        }
        return JWT.decode(value);
    }

    private JsonObject decodeTokenPayloadToJsonObject(DecodedJWT decodedJWT) {
        try {
            String payloadAsString = decodedJWT.getPayload();
            return new Gson().fromJson(
                    new String(Base64.getDecoder().decode(payloadAsString), StandardCharsets.UTF_8),
                    JsonObject.class);
        }   catch (RuntimeException exception){
            throw new InvalidTokenException("Invalid JWT or JSON format of each of the jwt parts", exception);
        }
    }
}
```

Going back to the `JwtTokenValidator`, first step in `validateAuthorizationHeader` is to extract a token from *Authorization* header as a String with a private method `subStringBearer`:

```java
private String subStringBearer(String authorizationHeader) {
    try {
        return authorizationHeader.substring(AccessToken.BEARER.length());
    } catch (Exception ex) {
        throw new InvalidTokenException("There is no AccessToken in a request header");
    }
}
```

The reason for that is becuasue the schema of *Authorization* header looks like this: `Bearer <token>`, therefore we need to remove the `Bearer ` part. What remains, which is token itself looks as follows:

```
eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJXYmdnRkNBNzJ4UG5KYWNUZTRHMzdEN1NDWFpJOW8wQVZMTWd0d0tfamhRIn0.eyJleHAiOjE2MTM2Mjc1NzYsImlhdCI6MTYxMzYyNzI3NiwianRpIjoiZjkzODVlMDMtYzRjOC00NzY0LWIyMDgtYzBhYWFiMjIyODEyIiwiaXNzIjoiaHR0cDovL2tleWNsb2FrOjgwODAvYXV0aC9yZWFsbXMvdGVzdCIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiIwODhjNTdiMy1mNGJlLTQwOTQtOGQzNC00Y2UyNWQ1OGUzY2IiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ0ZXN0X2NsaWVudCIsInNlc3Npb25fc3RhdGUiOiJlMTYxMTNjZi0wZGI5LTRlZDMtOGJjMC0yNWRmNDY4MDU2NjkiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJ0ZXN0X2NsaWVudCI6eyJyb2xlcyI6WyJ1bWFfcHJvdGVjdGlvbiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiY2xpZW50SWQiOiJ0ZXN0X2NsaWVudCIsImNsaWVudEhvc3QiOiIxNzIuMTguMC4xIiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VydmljZS1hY2NvdW50LXRlc3RfY2xpZW50IiwiY2xpZW50QWRkcmVzcyI6IjE3Mi4xOC4wLjEifQ.ihCQGFWRdr1NR7el7zsnnXZFwonOpFgEE_MHBlYSq07s2JhjsLJauvQ9erTM5YV_gmY-Q-QpmpRI-qq4miF9hem8qxXzxBkei7cXyYYQeiz44MwkusUW75VChfsYljgRNUSJM5G4_O636xWQNc2ET5v8508CPpgVIvl4QFKYQui3J2BADH8AyDihgaOcF5hfrutuEpH6AINvBmUebUKOLG3ZyST81Q3GjmSZmBaL7RK29uTm94i1HVqfXgRLIuf5zxLucq_gU4KM8c3mB5d8ZfJOMl8nOnYDbEbiGVEP_coz9x3iF2Lf3Fp8K2zez59w4yvGTy39Whns-KhtX02yAQ
```

Not very informative, isn't it? No problem, we can decode it using for example jwt.io page:

![jwt decoded](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/k17pi98fc6jhyxvqh0nv.png)

It contains lots of information, like user information, including roles. If you want to know more about JWT and tokens in particular, go check my previous blog post where I've introduced all of these concepts - ???? link do poprzedniego bloga ????

Next, having a raw token we can make a real validation of it in a new private method:

```java
private void validateToken(String value) {
    DecodedJWT decodedJWT = decodeToken(value);
    verifyTokenHeader(decodedJWT);
    verifySignature(decodedJWT);
    verifyPayload(decodedJWT);
}
```

And here a first step is to decode gibberish token into understandable Java object, therefore we use a convenient library - [com.auth0:java-jwt](https://github.com/auth0/java-jwt), which returns a `DecodedJWT` object.

```java
private DecodedJWT decodeToken(String value) {
    if (isNull(value)){
        throw new InvalidTokenException("Token has not been provided");
    }

    DecodedJWT decodedJWT = JWT.decode(value);
    log.debug("Token decoded successfully");
    return decodedJWT;
}
```

Next, having token decoded we can verify its content and starting from the header we would like first to validate if this is a JWT token.

```java
private void verifyTokenHeader(DecodedJWT decodedJWT) {
    try {
        Preconditions.checkArgument(decodedJWT.getType().equals("JWT"));
        log.debug("Token's header is correct");
    } catch (IllegalArgumentException ex) {
        throw new InvalidTokenException("Token is not JWT type", ex);
    }
}
```

Moving on, we have now very important part - validating a signature. If a signature will not be valid it will mean that somebody has done something funky with a token. Maybe an attacker tried to modify its payload to get to the wanted resource? That's one of the possibilities from which signature is trying to protect.  

In short, signing is a cryptographic operations in which as an input header, payload and special secret are provided and the result is a signature. If anything changes in the any of these three elements, singature needs also to be changed. There are variuos ways to validate if signature is correct and one of them, which I would like to use is **RS256** signature. With this approach we've got a pair of keys (secrets), first is used for creating a signature and a second could be used only for validating if a signature is correct. 

And that is we would like to achieve, to verify if a signature is correct we need to somehow get a public key (JSON Web Key - JWK) and verify it with what is inside the token. 

```java
private void verifySignature(DecodedJWT decodedJWT) {
    try {
        Jwk jwk = jwkProvider.get(decodedJWT.getKeyId());
        Algorithm algorithm = Algorithm.RSA256((RSAPublicKey) jwk.getPublicKey(), null);
        algorithm.verify(decodedJWT);
        log.debug("Token's signature is correct");
    } catch (JwkException | SignatureVerificationException ex) {
        throw new InvalidTokenException("Token has invalid signature", ex);
    }
}
```

In above code snippet you can see that there are two objects that might be a little mistic - `JWK` and `jwkProvider`. First one is a representation of a public key and the second one (which is an implementation of an `JwkProvider` interface) is responsible for getting it. Both classes are defined in a [com.auth0:jwks-rsa](https://github.com/auth0/jwks-rsa-java) library.

The `JwkProvider` is just an interface therefore we need to write our own implementation. In our case a provider of the public key is Keycloak (which is also generating tokens), therefore the relevant class was named `KeycloakJwkProvider`.

```java
public class KeycloakJwkProvider implements JwkProvider {

    private final URI uri;
    private final ObjectReader reader;

    public KeycloakJwkProvider(String jwkProviderUrl) {
        try {
            this.uri = new URI(jwkProviderUrl).normalize();
        } catch (URISyntaxException e) {
            throw new IllegalArgumentException("Invalid jwks uri", e);
        }
        this.reader = new ObjectMapper().readerFor(Map.class);
    }

    @Override
    public Jwk get(String keyId) throws JwkException {
        final List<Jwk> jwks = getAll();
        if (keyId == null && jwks.size() == 1) {
            return jwks.get(0);
        }
        if (keyId != null) {
            for (Jwk jwk : jwks) {
                if (keyId.equals(jwk.getId())) {
                    return jwk;
                }
            }
        }
        throw new SigningKeyNotFoundException("No key found in " + uri.toString() + " with kid " + keyId, null);
    }

    private List<Jwk> getAll() throws SigningKeyNotFoundException {
        List<Jwk> jwks = Lists.newArrayList();
        final List<Map<String, Object>> keys = (List<Map<String, Object>>) getJwks().get("keys");

        if (keys == null || keys.isEmpty()) {
            throw new SigningKeyNotFoundException("No keys found in " + uri.toString(), null);
        }

        try {
            for (Map<String, Object> values : keys) {
                jwks.add(Jwk.fromValues(values));
            }
        } catch (IllegalArgumentException e) {
            throw new SigningKeyNotFoundException("Failed to parse jwk from json", e);
        }
        return jwks;
    }

    private Map<String, Object> getJwks() throws SigningKeyNotFoundException {
        try {

            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(this.uri)
                    .headers("Accept", "application/json")
                    .GET()
                    .build();

            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

            return reader.readValue(response.body());

        } catch (IOException | InterruptedException e) {
            throw new NetworkException("Cannot obtain jwks from url " + uri.toString(), e);
        }
    }
}
```

The `JwkProvider` defines only one method `public Jwk get(String keyId)` which returns JSON Web Key (JWK) representation by a given `kid` which is available in the header of the access token. It's an identifier of a public key if an authorization server supports multiple keys.

In the constructor of this class there is `jwkProviderUrl` String which represtens an URL that needs to be called by an application to fetch a JWK. And what `KeycloakJwkProvider` is actually doing is using this public URL to fetch JWK(s) and produce a Java `Jwk` representation of it. An example of such URL for Keycloak would be:

```
{keycloak_base_url}/auth/realms/{realm_name}/protocol/openid-connect/certs
```

where `keycloak_base_url` is Keycloak's base URL (in my case `localhost:8080`) and `realm_name` is the name of a realm (in my case `test`). 

An example of a response from such endpoint would be:


```json
{
    "keys": [{
        "kid": "WbggFCA72xPnJacTe4G37D7SCXZI9o0AVLMgtwK_jhQ",
        "kty": "RSA",
        "alg": "RS256",
        "use": "sig",
        "n": "k96-hliB-mYJx47V4wPqnWi89IsSYfmCXjiWgHG4e4VAEcLqZ33V9aQ3nConMf0AWbG9zcQZUtqSTtXVKeUvtx_7QH9Rgzwoj0XDOU3K21hcZCs7ShMK-2kROk2jnZpM5I6r7GeloR52fPXIck-sXcR3acmeUgZyR_y7TtlYYCn4GUt2kjrwyL_qdNdvQoDXvHTnxv4wk3_-Zff7I3xK3lnPE8uIz6gxjFMZ20-ruU_5-umpUvF9B6NUPf3LQTlMm864MBw1narN6QrWTp9c9DF0SeGcN8r_XMo0jDkMDjTWwrHiumnA8Il50hbmcp_WdMV8ivuVoONGLc_5Q6-uUQ",
        "e": "AQAB",
        "x5c": [
            "MIIClzCCAX8CBgF3GcqCYDANBgkqhkiG9w0BAQsFADAPMQ0wCwYDVQQDDAR0ZXN0MB4XDTIxMDExOTA4MzUzOFoXDTMxMDExOTA4MzcxOFowDzENMAsGA1UEAwwEdGVzdDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAJPevoZYgfpmCceO1eMD6p1ovPSLEmH5gl44loBxuHuFQBHC6md91fWkN5wqJzH9AFmxvc3EGVLakk7V1SnlL7cf+0B/UYM8KI9FwzlNyttYXGQrO0oTCvtpETpNo52aTOSOq+xnpaEednz1yHJPrF3Ed2nJnlIGckf8u07ZWGAp+BlLdpI68Mi/6nTXb0KA17x058b+MJN//mX3+yN8St5ZzxPLiM+oMYxTGdtPq7lP+frpqVLxfQejVD39y0E5TJvOuDAcNZ2qzekK1k6fXPQxdEnhnDfK/1zKNIw5DA401sKx4rppwPCJedIW5nKf1nTFfIr7laDjRi3P+UOvrlECAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAN+QZvSPXUP6Q9JxpYOzl6U7TXLAWmQPznf+gdSc4rmHQD5gKr2s8zeNuJrx+cIIxPGsMk04VGdNjKf8bRYvB7ta+POxQ5VRnHZS5XuEyGBFeSWbbzwZnQY+cWjY3AmyReenJ4QKal4iFZgNvkYbVaw9SX1qDXTXQTn6OXyz/Cp8SbMUW8fy7GqdGFLGKYhX1Irq4Reiidkw4pKVgGHblcjB2hIRfpC7TYnv0jL9RK8iymvPGYRQYka2ks8J/+HNudKO8MoOwghtP9jwTHEygioc9gAyf8DMS9cGnsFnisCz4B/etTyvyzuhyBgTili5WzXjOk1Y0NqaxY50618BvPg=="],
        "x5t": "KQ4zgovMGPVesO36mzxvI9UTfdQ",
        "x5t#S256": "F4xuZVX7WsxcdXAetwwTOOI2ElV-hH9Gl_G25hANAaE"
    }]
}
```

Let's go back to the `JwtTokenValidator` class, to the `verifySignature(DecodedJWT decodedJWT)` method. Thanks to the `KeycloakJwkProvider` we've got a JWK representation, therefore we can now do a validation of a signature with a public key. For that we again use helper classes from the `com.auth0:java-jwt` library first to select a signing algorithm and then to do a verification.

```java
private void verifySignature(DecodedJWT decodedJWT) {
    try {
        Jwk jwk = jwkProvider.get(decodedJWT.getKeyId());
        Algorithm algorithm = Algorithm.RSA256((RSAPublicKey) jwk.getPublicKey(), null);
        algorithm.verify(decodedJWT);
        log.debug("Token's signature is correct");
    } catch (JwkException | SignatureVerificationException ex) {
        throw new InvalidTokenException("Token has invalid signature", ex);
    }
}
```

Great! After validating that a signature is correct we can be sure that all information inside of the payload are secured. Before moving on, we need also to validate a payload if a token has not expired, holds user roles and has scope information.


```java
private void verifyPayload(DecodedJWT decodedJWT) {
    
    JsonObject payloadAsJson = decodeTokenPayloadToJsonObject(decodedJWT);

    if (hasTokenExpired(payloadAsJson)) {
        throw new InvalidTokenException("Token has expired");
    }
    log.debug("Token has not expired");

    if (!hasTokenRealmRolesClaim(payloadAsJson)) {
        throw new InvalidTokenException("Token doesn't contain claims with realm roles");
    }
    log.debug("Token's payload contain claims with realm roles");

    if (!hasTokenScopeInfo(payloadAsJson)) {
        throw new InvalidTokenException("Token doesn't contain scope information");
    }
    log.debug("Token's payload contain scope information");
}
```

Before verifying a payload of a token, first I'm decoding it to the Gson's `JsonObject`:

```java
private JsonObject decodeTokenPayloadToJsonObject(DecodedJWT decodedJWT) {
    try {
        String payloadAsString = decodedJWT.getPayload();
        return new Gson().fromJson(
            new String(Base64.getDecoder().decode(payloadAsString), StandardCharsets.UTF_8),
            JsonObject.class);
    } catch (RuntimeException exception){
        throw new InvalidTokenException("Invalid JWT or JSON format of each of the jwt parts", exception);
    }
}
```

One of the fundamental rule of OAuth 2.0 framework is the fact that an access token should be a short live creature, usually for couple of minutes. It is because it may be a possibility that an attacker stills an access token and gets a pernament access to the resource owner. To reduce a blast radius access tokens are short lived so even if this situation occur an attacker will have an access only for a very limited time.

In a payload of a token I'm expecting a `exp` claim (field) that will hold information until when a token is valid, which is a standard way of adding such information to JWT.

```java
private boolean hasTokenExpired(JsonObject payloadAsJson) {

    Instant expirationDatetime = extractExpirationDate(payloadAsJson);
    return Instant.now().isAfter(expirationDatetime);
}

private Instant extractExpirationDate(JsonObject payloadAsJson) {
    try {
        return Instant.ofEpochSecond(payloadAsJson.get("exp").getAsLong());
    } catch (NullPointerException ex) {
        throw new InvalidTokenException("There is no 'exp' claim in the token payload");
    }
}
```

Next point is to validate if inside of a token there are information about user roles that were assigned in Keycloak. I want to do this validation because we'll require them for the REST endpoints.

Roles in JWT generated by Keycloak are inside of the `roles` array field, which is part of the `realm_access` object field.

```java
private boolean hasTokenRealmRolesClaim(JsonObject payloadAsJson) {
    try {
        return payloadAsJson.getAsJsonObject("realm_access").getAsJsonArray("roles").size() > 0;
    } catch (NullPointerException ex) {
        return false;
    }
}
```

And the last thing that I want to check if inside of a payload there is a `scope` field.

```java
private boolean hasTokenScopeInfo(JsonObject payloadAsJson) {
    return payloadAsJson.has("scope");
}
```

At that's a full implementation of `JwtTokenValidator`. I think that it's more than enough validation for a start, but it could be easily extended if there will a need to do that.

```java
@Slf4j
@RequiredArgsConstructor
public class JwtTokenValidator {

    private final JwkProvider jwkProvider;

    public AccessToken validateAuthorizationHeader(String authorizationHeader) throws InvalidTokenException {
        String tokenValue = subStringBearer(authorizationHeader);
        validateToken(tokenValue);
        return new AccessToken(tokenValue);
    }

    private void validateToken(String value) {
        DecodedJWT decodedJWT = decodeToken(value);
        verifyTokenHeader(decodedJWT);
        verifySignature(decodedJWT);
        verifyPayload(decodedJWT);
    }

    private DecodedJWT decodeToken(String value) {
        if (isNull(value)){
            throw new InvalidTokenException("Token has not been provided");
        }
        DecodedJWT decodedJWT = JWT.decode(value);
        log.debug("Token decoded successfully");
        return decodedJWT;
    }

    private void verifyTokenHeader(DecodedJWT decodedJWT) {
        try {
            Preconditions.checkArgument(decodedJWT.getType().equals("JWT"));
            log.debug("Token's header is correct");
        } catch (IllegalArgumentException ex) {
            throw new InvalidTokenException("Token is not JWT type", ex);
        }
    }

    private void verifySignature(DecodedJWT decodedJWT) {
        try {
            Jwk jwk = jwkProvider.get(decodedJWT.getKeyId());
            Algorithm algorithm = Algorithm.RSA256((RSAPublicKey) jwk.getPublicKey(), null);
            algorithm.verify(decodedJWT);
            log.debug("Token's signature is correct");
        } catch (JwkException | SignatureVerificationException ex) {
            throw new InvalidTokenException("Token has invalid signature", ex);
        }
    }

    private void verifyPayload(DecodedJWT decodedJWT) {
        JsonObject payloadAsJson = decodeTokenPayloadToJsonObject(decodedJWT);
        if (hasTokenExpired(payloadAsJson)) {
            throw new InvalidTokenException("Token has expired");
        }
        log.debug("Token has not expired");

        if (!hasTokenRealmRolesClaim(payloadAsJson)) {
            throw new InvalidTokenException("Token doesn't contain claims with realm roles");
        }
        log.debug("Token's payload contain claims with realm roles");

        if (!hasTokenScopeInfo(payloadAsJson)) {
            throw new InvalidTokenException("Token doesn't contain scope information");
        }
        log.debug("Token's payload contain scope information");
    }

    private JsonObject decodeTokenPayloadToJsonObject(DecodedJWT decodedJWT) {
        try {
            String payloadAsString = decodedJWT.getPayload();
            return new Gson().fromJson(
                    new String(Base64.getDecoder().decode(payloadAsString), StandardCharsets.UTF_8),
                    JsonObject.class);
        }   catch (RuntimeException exception){
            throw new InvalidTokenException("Invalid JWT or JSON format of each of the jwt parts", exception);
        }
    }

    private boolean hasTokenExpired(JsonObject payloadAsJson) {
        Instant expirationDatetime = extractExpirationDate(payloadAsJson);
        return Instant.now().isAfter(expirationDatetime);
    }

    private Instant extractExpirationDate(JsonObject payloadAsJson) {
        try {
            return Instant.ofEpochSecond(payloadAsJson.get("exp").getAsLong());
        } catch (NullPointerException ex) {
            throw new InvalidTokenException("There is no 'exp' claim in the token payload");
        }
    }

    private boolean hasTokenRealmRolesClaim(JsonObject payloadAsJson) {
        try {
            return payloadAsJson.getAsJsonObject("realm_access").getAsJsonArray("roles").size() > 0;
        } catch (NullPointerException ex) {
            return false;
        }
    }

    private boolean hasTokenScopeInfo(JsonObject payloadAsJson) {
        return payloadAsJson.has("scope");
    }

    private String subStringBearer(String authorizationHeader) {
        try {
            return authorizationHeader.substring(AccessToken.BEARER.length());
        } catch (Exception ex) {
            throw new InvalidTokenException("There is no AccessToken in a request header");
        }
    }
}
```

The last thing that I haven't mentioned yet is `InvalidTokenException` class, which is a custom exception object which I want to throw whenever something wrong is with an access token.

```java
public class InvalidTokenException extends AuthenticationException {
    public InvalidTokenException(String message) {
        super(message);
    }

    public InvalidTokenException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

It extends a Spring Security abstract class `AuthenticationException` which is a superclass for all exceptions related to authentication.

Let's go back to the `AccessTokenFilter` class from which everything has started. After validating incoming access token as string `JwtTokenValidator` returns an `AccessToken` object, but the `attemptAuthentication` must return an `Authentication` object, therefore I've created a wrapper class that extends `AbstractAuthenticationToken` (which extends `Authentication` interface) and holds `AccessToken` object.

```java
public class JwtAuthentication extends AbstractAuthenticationToken {

    private final AccessToken accessToken;

    public JwtAuthentication(AccessToken accessToken) {
        super(accessToken.getAuthorities());
        this.accessToken = accessToken;
    }

    @Override
    public Object getCredentials() {
        return null;
    }

    @Override
    public Object getPrincipal() {
        return accessToken.getValueAsString();
    }
}
```

And an implementation of `attemptAuthentication` method will be:

```java
@Slf4j
class AccessTokenFilter extends AbstractAuthenticationProcessingFilter {

    ... //other methods and fields
    
    @Override
    public Authentication attemptAuthentication(HttpServletRequest request,
                                                HttpServletResponse response) {

        log.info("Attempting to authenticate for a request {}", request.getRequestURI());

        String authorizationHeader = extractAuthorizationHeaderAsString(request);
        AccessToken accessToken = tokenVerifier.validateAuthorizationHeader(authorizationHeader);
        return this.getAuthenticationManager()
                            .authenticate(new JwtAuthentication(accessToken));
    } 
}
```

 The logic of creating and `Authentication` object has been described. What has left is to implement the logic `successfulAuthentication` method which will be invoked if previous one will end with success.

```java
@Slf4j
class AccessTokenFilter extends AbstractAuthenticationProcessingFilter {

    ... //other methods and fields

    @Override
    protected void successfulAuthentication(HttpServletRequest request,
                                            HttpServletResponse response,
                                            FilterChain chain,
                                            Authentication authResult) throws IOException, ServletException {

        log.info("Successfully authentication for the request {}", request.getRequestURI());

        SecurityContextHolder.getContext().setAuthentication(authResult);
        chain.doFilter(request, response);
    }
}
```

The implementation of this method is quite straightforward, after successful authentication an `Authentication` object (in our case it's `JwtAuthentication` class) is added to the `SecurityContextHolder`, which stores all information about the current user user who is making a request.

All right, all the building blocks have been created, now, let's put it together in a configuration class to enable it in an application. To do that let's create a `SecurityConfig` class that will extends `WebSecurityConfigurerAdapter`, which allows us with only few lines of code to make a security configuration. The `WebSecurityConfigurerAdapter` has multiple methods that could be override to make magic happened.

```java
@Order(1)
@EnableWebSecurity
@RequiredArgsConstructor
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Value("${spring.security.ignored}")
    private String nonSecureUrl;

    @Value("${keycloak.jwk}")
    private String jwkProviderUrl;

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
                .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                .and()
                .csrf().disable()
                .cors()
                .and()
                .addFilterBefore(
                        new AccessTokenFilter(
                                jwtTokenValidator(keycloakJwkProvider()),
                                authenticationManagerBean()),
                        BasicAuthenticationFilter.class);
    }

    @Override
    public void configure(WebSecurity web) throws Exception {
        web.ignoring().antMatchers(nonSecureUrl);
    }

    @ConditionalOnMissingBean
    @Bean
    @Override
    public AuthenticationManager authenticationManagerBean() throws Exception {
        return super.authenticationManagerBean();
    }

    @Override
    public void configure(AuthenticationManagerBuilder auth) throws Exception {
        auth.authenticationProvider(authenticationProvider());
    }

    @Bean
    public AuthenticationProvider authenticationProvider() {
        return new KeycloakAuthenticationProvider();
    }

    @Bean
    public JwtTokenValidator jwtTokenValidator(JwkProvider jwkProvider) {
        return new JwtTokenValidator(jwkProvider);
    }

    @Bean
    public JwkProvider keycloakJwkProvider() {
        return new KeycloakJwkProvider(jwkProviderUrl);
    }
}
```

Let's break above config into smaller peaces to understand it better.

* `@Order(1)` annotation - as I mentioned before, one of the key concept of Spring Security are filters that could be combine into a chain. If we need to define multiple filters we can specify which one will be used in which order. By adding this annotation we tell that our filter has the biggest priority (a lower the number the bigger priority),

* `@EnableWebSecurity` annotation - this annotation tells Spring that this is a configuration class and enables security features defined by `WebSecurityConfigurerAdapter` superclass,

* `String nonSecureUrl` field - holds information which of served URLs by the application should be excluded from checking the access token. Those values (comma seperated) can be passed to `application.properties` or `application.yaml` file under `spring.security.ignored` key. For my application I've decided to exclude all *actuator* endpoints to allow external services to collect metrics.

  * Url values defined in above variable are than used in the `configure(WebSecurity web)` method, where we configure Spring Security to ignore validation for provided endpoints

* `String jwkProviderUrl` field - this holds a base URL of the authorization server, Keycloak in our case, that provides a public key needed for validating signature of an access token,

  * value that is holded by above variable is used to create a Spring bean in `JwkProvider keycloakJwkProvider()`,

* `configure(HttpSecurity http)` - this is the most important method in this class, because here we're applying the `AccessTokenFilter` to the filter chain with `addFilterBefore` method. Apart from that I've also decided to add following configs:

    * `.sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)` - I would like to have a stateless application, which means that user info are not stored in-memory between requests and prevents Spring from creating HTTP sessions,

    * `.csrf().disable()` - because I want to have a stateless and relatively simple application I decided to disable CSRF protection, if you need to know more about protecting from this kind of attacks go check [the Spring official docs](https://docs.spring.io/spring-security/site/docs/current/reference/html5/#servlet-csrf-using)

    * `cors()` - with this config we will allow other origin (domain, server, port) to use endpoints; in simplier words if we would not add it our frontend app (that will be build in upcoming post) would not be able to consume REST API because it'll be running on a different port (when I'll start it locally),

* `AuthenticationManager authenticationManagerBean()` - here we're defining the `AuthenticationManager` bean,

* `configure(AuthenticationManagerBuilder auth)` - having already the `AuthenticationManager` we need to register an `AuthenticationProvider`, which is defined as a bean in following config method,

* `AuthenticationProvider authenticationProvider()` - in our case we would like to define `KeycloakAuthenticationProvider` as a provider,

* `JwtTokenValidator jwtTokenValidator(JwkProvider jwkProvider)` - here we're defining the class responsible for token validation.

The last thing that we need to set up is to assign some variable in *application.yaml* (or if you prefer *application.properties*) file.

```yaml
spring:
    security:
        ignored: "/actuator/**"

keycloak:
    url: http://localhost:8080
    realm: test
    jwk: ${keycloak.url}/auth/realms/${keycloak.realm}/protocol/openid-connect/certs

server:
    port: 8081
```

First property are for indicating which endpoints should be excluded from access token verification. Second one points out to the endpoint from which public keys could be fetched. Third one indicates on which port I would like to run my application (it's not a default, because I run my Keycloak instance on 8080 port). 


## Manual testing

In order to test E2E our solution we will need a Keycloak instance up and running. In my previous blog post ???????? link ???? I've described how it can be achieved using Docker, but if you don't want go back here, in short are what we need to have.

First of all clone my repository - [keycloak-security-example](https://github.com/wkrzywiec/keycloak-security-example) inside of which there is a *docker-compose.yaml*. The interesting part is the following:

```yaml
version: "3.8"
services:
  
  keycloak:
    image: jboss/keycloak:11.0.2
    container_name: keycloak
    ports:
      - 8080:8080
    environment:
      - KEYCLOAK_USER=admin
      - KEYCLOAK_PASSWORD=admin
      - DB_VENDOR=postgres
      - DB_ADDR=postgres
      - DB_DATABASE=keycloak
      - DB_USER=keycloak
      - DB_PASSWORD=keycloak
      - KEYCLOAK_IMPORT=/tmp/realm-test.json
    volumes:
      - ./infra/keycloak/realm-test.json:/tmp/realm-test.json
    command: ["-Dkeycloak.profile.feature.upload_scripts=enabled"]
    depends_on:
      - postgres

  postgres:
    image: postgres:13.0-alpine
    container_name: postgres
    ports:
      - 5432:5432
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres:/var/lib/postgresql/data
      - ./infra/postgres:/docker-entrypoint-initdb.d

volumes:
  postgres:
```

With these two services (keycloak and postgres) you can start up Keycloak with predefined realm, client, users and roles. To do that just run the command:

```bash
> docker-compose up -d keycloak
Starting postgres ... done
Starting keycloak ... done
```

To test it together with an application there is still one more thing. We need to adjust **hosts** file, which location depends on the OS:

* [Linux (Ubuntu)](http://manpages.ubuntu.com/manpages/trusty/man5/hosts.5.html)
* [Windows 10](https://www.groovypost.com/howto/edit-hosts-file-windows-10/)
* [Mac](https://www.imore.com/how-edit-your-macs-hosts-file-and-why-you-would-want#page1)

Once you found it add following line:

```
127.0.0.1	keycloak
```

This step is necessary because the address of Keycloak server is different depending on the point of view. From the point of view of an app running in the web browser it'll be `http://localhost:8080`, but from the perspective of `backend` application that is running inside the Docker network it will be `http://keycloak:8080`. To overcome it above config is necessary.

To test if everything is working go to the `http://localhost:8080` and you should see Keycloak's admin panel (`username: admin, password: admin`).

![keycloak admin](https://dev-to-uploads.s3.amazonaws.com/i/9gvseqfb16ajr3l2rkjh.png)

Now, let's test our backend application! First let's see if `/actuator` endpoint is really not protected, therefore using web browser, Postman or whatever other tool you like.

![actuator](https://dev-to-uploads.s3.amazonaws.com/i/trexcnk2ptvjpinjlzmi.png)

All right, it's not protected. Fine. Let's now check other two endpoints - `/movies` and `/movies/1`.

![unauthorized](https://dev-to-uploads.s3.amazonaws.com/i/rr6af111ulwlzsygzlna.png)

In both cases we're receiving the **401 Unauthorized** response, great! Let's now get the authorization by having an access token. 

To achieve it we will need to make a request to the token endpoint exposed by Keycloak - `{keycloak}/auth/realms/{realm}/protocol/openid-connect/token`, which in our case is `http://localhost:8080/auth/realms/test/protocol/openid-connect/token`. 

To get an access token we need to pass credentials. Accordingly to the OAuth 2.0 flow there are multiple ways to get an access token. I'll use one of the simplets grant type - `password`. With it we need to provide only for which `scope` we would like to be authorized together with `client_id` and `client_secret`. Moreover we need to have a user credentials - `username` and `password`.

If you're running Keycloak using my *docker-compose.yaml* file you can use following credentials, but if not I'm describing how to find it on Keycloak UI.

```
client_id       test_client
client_secret   8ac27a39-fa84-46b9-8c30-b485056e0cea
username        luke
password        password
```

`client_id` is a name of an application (`frontend`) and `client_secret` can be found after logging in to the *Test* Keycloak realm and by clicking following links **Clients** > **test_client** > **Credentials**.

![secret](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/bzk9xhu7n90ovyaix0u1.png)

If you see only **** characters just click *Regenerate Secret* button and a new one will be created.

To create eligible user go to the **User** menu and click **Add user** button which will guide you thru very short user registration. To set up password after creating user go to **Credentials** tab and set a new one. Make sure that **Temporary** toggle is switched off.

![han](https://dev-to-uploads.s3.amazonaws.com/i/p3jqvsfkbnanw27gz4m5.png)

Having all these information we can now use **POST** HTTP method to already mentioned URL inside the body and send it with a content type *application/x-www-form-urlencoded*. 

![token request](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/decmp6exttu3z1wj8gcd.png)

As a result we'll receive a JSON response with bunch of information including access, identity and refresh token token.

Having an access token copy it now to a new request that will be made to our backend application (let's say `/movies` endpoint). It needs to be added to a HTTP header called **Authorization** where value will be `Bearer <token>`.

![with access token](https://dev-to-uploads.s3.amazonaws.com/i/j00izezwhks3864h5qe1.png)

Awesome! We've got information about favourite movies! 🎉

## Handling AuthenticationException

In the test case when we haven't provided an access token our application returns only the HTTP code 401, which is kind of an information but still it's not really verbose. It doesn't tell why request was not authorized.

Luckily we can easily fix it by creating our custom `AuthenticationFailureHandler` and add it to the `AccessTokenFilter`.

Let's first create a handle class - `AccessTokenAuthenticationFailureHandler` which implements `AuthenticationFailureHandler` interface.

```java
class AccessTokenAuthenticationFailureHandler implements AuthenticationFailureHandler {

    @Override
    public void onAuthenticationFailure(HttpServletRequest request,
                                        HttpServletResponse response,
                                        AuthenticationException e) throws IOException {


        response.setStatus(HttpStatus.UNAUTHORIZED.value());
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write(createErrorBody(e));
    }

    private String createErrorBody(AuthenticationException exception) {
        JsonObject exceptionMessage = new JsonObject();
        exceptionMessage.addProperty("code", HttpStatus.UNAUTHORIZED.value());
        exceptionMessage.addProperty("reason", HttpStatus.UNAUTHORIZED.getReasonPhrase());
        exceptionMessage.addProperty("timestamp", Instant.now().toString());
        exceptionMessage.addProperty("message", exception.getMessage());
        return new Gson().toJson(exceptionMessage);
    }
}
```

`AuthenticationFailureHandler` interface has one method that is here implements. It'll be called when the `AuthenticationException` is thrown (in our app `InvalidTokenException` is extending this abstract class) and in it a response is modified to return 401 UNAUTHORIZED HTTP code with a JSON body with an explanation.

Once we're having it we need to assign it to the `AccessTokenFilter` by adding an extra parameter to the constructor.

```java
class AccessTokenFilter extends AbstractAuthenticationProcessingFilter {
    
    public AccessTokenFilter(
        JwtTokenValidator jwtTokenValidator,
        AuthenticationManager authenticationManager,
        AuthenticationFailureHandler authenticationFailureHandler) {

    ... //other code
    setAuthenticationFailureHandler(authenticationFailureHandler);
    }
}
```

Method `setAuthenticationFailureHandler(AuthenticationFailureHandler failureHandler)` is defined in the superclass `AbstractAuthenticationProcessingFilter` from which `AccessTokenFilter` inherits.

Finally we need to modify `SecurityConfig` class to define new exception handler as a Spring bean and add it to a `AccessTokenFilter` constructor.

```java
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
                .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                .and()
                .csrf().disable()
                .cors()
                .and()
                .addFilterBefore(
                        new AccessTokenFilter(
                                jwtTokenValidator(keycloakJwkProvider()),
                                authenticationManagerBean(),
                                authenticationFailureHandler()),
                        BasicAuthenticationFilter.class);
    }

    @Bean
    public AuthenticationFailureHandler authenticationFailureHandler() {
        return new AccessTokenAuthenticationFailureHandler();
    }

    ... //other beans definitions
}
```

Now if we run an application once again and for example provide an expired token to the request we should get nice looking information what went wrong.

![error handling](https://dev-to-uploads.s3.amazonaws.com/i/416tojy46tr4sh3a8r5b.png)

## Protecting REST API endpoints by user role

Next step into full-secured application is to allow only selected users to use certain REST API endpoints. In order to define those special users we need to assign roles to their accounts. In my previous article about Keycloak set up I've created two roles and assign each on of them to different user. Now looking at the movie backend application let's say that an endpoint `/movies` can be used only by a user with `ADMIN` role, and an endpoint `/movies/{id}` only by the users with `VISITOR` role. That's the target.

To achieve it let's create a custom aspect annotation which we can than add to the controller method so that before invoking it we will check is a user has valid roles inside of an access token.

Therefore, first we need to creat an annotation `AllowedRoles`:

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface AllowedRoles {

    String[] value();
}
```

Then, we need to create an Spring aspect (remember to add `spring-boot-starter-aop` dependency to your Maven/Gradle definition) that will do all validations:

```java
@Aspect
@Component
public class RolesAspect {

    @Before("@annotation(io.wkrzywiec.keycloak.backend.infra.security.annotation.AllowedRoles)")
    public void before(JoinPoint joinPoint) {

        String[] expectedRoles = ((MethodSignature) joinPoint.getSignature()).getMethod().getAnnotation(AllowedRoles.class).value();

        Collection<? extends GrantedAuthority> grantedAuthorities =
                Optional.ofNullable(SecurityContextHolder.getContext().getAuthentication())
                        .map(Authentication::getAuthorities)
                        .orElseThrow(() -> new AccessDeniedException("No authorities found"));

        List<String> roles = grantedAuthorities.stream()
                .map(GrantedAuthority::getAuthority)
                .collect(Collectors.toList());

        if (!roles.containsAll(Arrays.asList(expectedRoles))) {
            throw new AccessDeniedException(String.format("Unauthorized request. Expected to have %s roles, but have %s", Arrays.asList(expectedRoles), roles));
        }
    }
}
```

What's happening here? First we get a list of roles that certain method requires from the `value` passed to the annotation. Than we gets from SecurityContext the list of roles that user is assigned to. And finally we check if a user has all required roles. If yes, everything is fine. If not an `AccessDeniedException` is thrown.

Finally we can add annotations to the controller methods:

```java
public class MovieController {

    @GetMapping("/movies")
    @AllowedRoles("ADMIN")
    public List<Movie> getAllMovies(){
        SecurityContext sc = SecurityContextHolder.getContext();
        sc.getAuthentication().getAuthorities().forEach(b -> log.info(b.toString()));
        return new ArrayList<>(movies.values());
    }

    @GetMapping("/movies/{id}")
    @AllowedRoles("VISITOR")
    public Movie getMovieById(@PathVariable("id") String id){
        return movies.get(Long.valueOf(id));
    }
}
```

Like before, to gently handle an authorization exception (`AccessDeniedException` to be precise) and to inform the user why she/he can't access certain endpoint we need to be create a new kind of a handler, which will be almost a copy-paste from `AccessTokenAuthenticationFailureHandler`. This time our `AuthorizationAccessDeniedHandler` will be implementing the `AccessDeniedHandler` interface. 

```java
public class AuthorizationAccessDeniedHandler implements AccessDeniedHandler {

    @Override
    public void handle(HttpServletRequest request, HttpServletResponse response, AccessDeniedException accessDeniedException) throws IOException, ServletException {

        response.setStatus(HttpStatus.FORBIDDEN.value());
        response.setContentType("application/json;charset=UTF-8");
        response.getWriter().write(createErrorBody(accessDeniedException));
    }

    private String createErrorBody(AccessDeniedException exception) {
        JsonObject exceptionMessage = new JsonObject();
        exceptionMessage.addProperty("code", HttpStatus.FORBIDDEN.value());
        exceptionMessage.addProperty("reason", HttpStatus.FORBIDDEN.getReasonPhrase());
        exceptionMessage.addProperty("timestamp", Instant.now().toString());
        exceptionMessage.addProperty("message", exception.getMessage());
        return new Gson().toJson(exceptionMessage);
    }
}
```

It also requires to amend the `SecurityConfig` class with `exceptionHandling()..accessDeniedHandler(...)`:

```java
public class SecurityConfig extends WebSecurityConfigurerAdapter {

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http
                .sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS)
                .and()
                .csrf().disable()
                .cors()
                .and()
                .exceptionHandling()
                .accessDeniedHandler(accessDeniedHandler())
                .and()
                .addFilterBefore(
                        new AccessTokenFilter(
                                jwtTokenValidator(keycloakJwkProvider()),
                                authenticationManagerBean(),
                                authenticationFailureHandler()),
                        BasicAuthenticationFilter.class);
    }


    @Bean
    public AccessDeniedHandler accessDeniedHandler() {
        return new AuthorizationAccessDeniedHandler();
    }

    ... // other beans definitions
```

Now, if we test the `/movies` endpoint using *luke*'s (`VISITOR` role) access token we should get follwoing result:

![unauthorized](https://dev-to-uploads.s3.amazonaws.com/i/sm6bas1h0jfpmi8qf86a.png)

Awesome! Apart from having information that user is not allowed to get access to the specific resource our backend application also returns the reason.

## Unit and E2E tests

That could be the end of this blog post, but as it's a good practice to have tests for a code we write let's do some of these.

Becuase most of the things that we created are requiring the entire Spring context most cases that we will write will actual E2E test, where we spin up our application together with Keycloak and run some tests. But there is a small part of the code for which we could write fast unit tests - `JwtTokenValidator`.

As you may already forget (yes I know that this post is rather long), `JwtTokenValidator` is a class which holds the entire logic of validating an access token. As an input it takes a value from `Authorization` HTTP header and returns an `AccessToken` object. It doesn't need to have an entire Spring context up and running, and it's the most complex part of what was written, which needs multiple test cases to be checked.

Units test for the `JwtTokenValidator` class I'll write with Spock test framework (Groovy language). If you don't know it, don't worry. I've tried to keep it simple and it's not that far from good old Java.

```groovy
@Title("Token validation rules")
@Subject(JwtTokenValidator)
class JwtTokenValidatorSpec extends Specification {

    private JwtTokenValidator validator
    private JwkProvider jwkProvider

    def setup() {
        jwkProvider = Stub(KeycloakJwkProvider)
        validator = new JwtTokenValidator(jwkProvider)
    }

    def "Create AccessToken from String value"() {

        given: "Generate RSA Key Pair"
        KeyPair keyPair = generateRsaKeyPair()
        stubJsonWebKey(keyPair)

        and: "Generate correct JWT Access token"
        def token = generateAccessToken(keyPair)

        when: "Validate access token"
        def accessToken = validator.validateAuthorizationHeader(AccessToken.BEARER + token)

        then: "AccessToken has been created"
        accessToken.valueAsString == token
    }

    def "AccessToken with incorrect signature"() {

        given: "Generate first RSA Key Pair"
        KeyPair firstKeyPair = generateRsaKeyPair()

        and: "Generate second RSA Key Pair"
        KeyPair secondKeyPair = generateRsaKeyPair()
        stubJsonWebKey(secondKeyPair)

        and: "Generate JWT Access token"
        def token = generateAccessToken(firstKeyPair)

        when: "Validate access token"
        validator.validateAuthorizationHeader(AccessToken.BEARER + token)

        then: "Token has invalid signature"
        def exception = thrown(InvalidTokenException)
        exception.message == 'Token has invalid signature'
    }

    def "Expired Access Token"() {

        given: "Generate RSA Key Pair"
        KeyPair keyPair = generateRsaKeyPair()
        stubJsonWebKey(keyPair)

        and: "Generate JWT Access token"
        def jwtBuilder = JWT.create()
                .withExpiresAt(Date.from(Instant.now().minusSeconds(60)))

        def token = generateAccessToken(keyPair, jwtBuilder)

        when: "Validate access token"
        validator.validateAuthorizationHeader(AccessToken.BEARER + token)

        then: "Token has invalid signature"
        def exception = thrown(InvalidTokenException)
        exception.message == 'Token has expired'
    }

    def "Access Token without scope information"() {

        given: "Generate RSA Key Pair"
        KeyPair keyPair = generateRsaKeyPair()
        stubJsonWebKey(keyPair)

        and: "Generate JWT Access token"
        def jwtBuilder = JWT.create()
                .withExpiresAt(Date.from(Instant.now().plusSeconds(5 * 60)))
                .withClaim("realm_access", Map.of("roles", List.of('ADMIN')))

        def token = generateAccessToken(keyPair, jwtBuilder)

        when: "Validate access token"
        validator.validateAuthorizationHeader(AccessToken.BEARER + token)

        then: "Token has invalid signature"
        def exception = thrown(InvalidTokenException)
        exception.message == "Token doesn't contain scope information"
    }

    def "Access Token without user roles information"() {

        given: "Generate RSA Key Pair"
        KeyPair keyPair = generateRsaKeyPair()
        stubJsonWebKey(keyPair)

        and: "Generate JWT Access token"
        def jwtBuilder = JWT.create()
                .withExpiresAt(Date.from(Instant.now().plusSeconds(5 * 60)))
                .withClaim("scope", List.of("openid"))


        def token = generateAccessToken(keyPair, jwtBuilder)

        when: "Validate access token"
        validator.validateAuthorizationHeader(AccessToken.BEARER + token)

        then: "Token has invalid signature"
        def exception = thrown(InvalidTokenException)
        exception.message == "Token doesn't contain claims with realm roles"
    }

    private static KeyPair generateRsaKeyPair() {

        def keygen = KeyPairGenerator.getInstance("RSA")
        RSAKeyGenParameterSpec spec = new RSAKeyGenParameterSpec(2048, RSAKeyGenParameterSpec.F4)
        keygen.initialize(spec)
        KeyPair keyPair = keygen.generateKeyPair()

        return keyPair
    }

    private void stubJsonWebKey(KeyPair keyPair) {
        def jwk = Stub(Jwk)
        jwk.getPublicKey() >> keyPair.getPublic()
        jwkProvider.get(_) >> jwk
    }

    private static String generateAccessToken(KeyPair keyPair) {

        Algorithm algorithm = Algorithm.RSA256(keyPair.getPublic() as RSAPublicKey, keyPair.getPrivate() as RSAPrivateKey)
        return JWT.create()
                .withExpiresAt(Date.from(Instant.now().plusSeconds(5 * 60)))
                .withClaim("scope", List.of("openid"))
                .withClaim("realm_access", Map.of("roles", List.of('ADMIN')))
                .sign(algorithm)
    }

    private static String generateAccessToken(KeyPair keyPair, JWTCreator.Builder builder) {

        Algorithm algorithm = Algorithm.RSA256(keyPair.getPublic() as RSAPublicKey, keyPair.getPrivate() as RSAPrivateKey)
        return builder.sign(algorithm)
    }
}
```

In all these tests first we generate an access token (valid or not) using `com.auth0` libraries mentioned before and than checking if an `AccessToken` object was created or an exception was thrown with specific message.

For broader and longer tests I have decided to go back to Java's JUnit5 and use Spring's `MockMvc`. Becuase the entire application will be spinned up we need to somehow spin up Keycloak. Luckily we can use [Testcontainers](https://www.testcontainers.org) which allows to run it inside a Docker container, similar to the one that is defined in the *docker-compose.yaml* (with small change of database type).

```java
@SpringBootTest(properties = {"spring.main.allow-bean-definition-overriding=true"})
@AutoConfigureMockMvc
@Testcontainers
public class MovieControllerSecurityE2ETest {

    @Container
    private static GenericContainer keycloak = new GenericContainer(DockerImageName.parse("jboss/keycloak:11.0.2"))
            .withExposedPorts(8080)
            .withEnv("KEYCLOAK_USER", "admin")
            .withEnv("KEYCLOAK_PASSWORD", "admin")
            .withEnv("DB_VENDOR", "h2")
            .withEnv("KEYCLOAK_IMPORT", "/tmp/realm-test.json")
            .withClasspathResourceMapping("keycloak/realm-test.json", "/tmp/realm-test.json", BindMode.READ_ONLY)
            .withCommand("-Dkeycloak.profile.feature.upload_scripts=enabled")
            .waitingFor(Wait.forHttp("/auth/realms/master"));

    @Autowired
    private MockMvc mockMvc;

    @Test
    @DisplayName("Try to get all movies (request without Authorization header)")
    void requestAllMoviesWithoutAuthorizationHeader() throws Exception {

        mockMvc.perform(
                get("/movies"))
                .andDo(print())
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("Get all movies (request with Authorization header)")
    void getAllMoviesWithAuthorizationHeader() throws Exception {

        String accessToken = fetchAccessToken("ADMIN");

        mockMvc.perform(
                get("/movies")
                        .header("Authorization", "Bearer " + accessToken))
                .andDo(print())
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("Get a single movie (request with Authorization header)")
    void getSingleMovieWithAuthorizationHeader() throws Exception {

        String accessToken = fetchAccessToken("VISITOR");

        mockMvc.perform(
                get("/movies/1")
                        .header("Authorization", "Bearer " + accessToken))
                .andDo(print())
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("Try to get a single movie having wrong role (request with Authorization header)")
    void getSingleHavingIncorrectUserRole() throws Exception {

        String accessToken = fetchAccessToken("VISITOR");

        mockMvc.perform(
                get("/movies")
                        .header("Authorization", "Bearer " + accessToken))
                .andDo(print())
                .andExpect(status().isForbidden());
    }

    private String fetchAccessToken(String role) {

        String username = role.equals("ADMIN") ? "han" : "luke";

        String keycloakUrl = "http://" + keycloak.getHost() + ":" + keycloak.getMappedPort(8080) + "/auth/realms/test";

        Map<String, String> formParams = Map.of(
                "grant_type", "password",
                "scope", "openid",
                "client_id", "test_client",
                "client_secret", "8ac27a39-fa84-46b9-8c30-b485056e0cea",
                "username", username,
                "password", "password"
        );

        var response =
                given()
                    .contentType("application/x-www-form-urlencoded")
                    .accept("application/json, text/plain, */*")
                    .formParams(formParams)
                        .log().all()
                .when()
                    .post(keycloakUrl + "/protocol/openid-connect/token")
                        .prettyPeek()
                .then();

        response.statusCode(200);

        return response.extract().body().jsonPath().getString("access_token");
    }

    @org.springframework.boot.test.context.TestConfiguration
    static class TestConfiguration {

        @Bean
        @Primary
        public JwkProvider keycloakJwkProvider() {
            String jwkUrl = "http://" + keycloak.getHost() + ":" + keycloak.getMappedPort(8080) + "/auth/realms/test" + "/protocol/openid-connect/certs";
            return new KeycloakJwkProvider(jwkUrl);
        }
    }
}
```

All the tests are pretty straightforward. First we gets a new access token for particular user, attaches it to the request's header and check the response.

That would be it! With this long blog post I've tried to show you how to implement OAuth 2.0 a protected resource application with Spring Boot that will work with popular identity provider. I hope you've learn couple of things about Spring Security or OAuth 2.0 in general so I can invite you for the last part of my short series where I describe how to consume protected resource in Angular application.

Code for entire project can be found in my GitHub repository:

* [**wkrzywiec/keycloak-security-example**](https://github.com/wkrzywiec/keycloak-security-example)

---

## References


* [**Implementing JWT with Spring Boot and Spring Security** on medium.com](https://medium.com/@xoor/jwt-authentication-service-44658409e12c)

* [**Exploring Spring-Boot and Spring-Security: Custom token based authentication of REST services with Spring-Security and pinch of Spring Java Configuration and Spring Integration Testing** on kariera.future-processing.pl](https://kariera.future-processing.pl/blog/exploring-spring-boot-and-spring-security-custom-token-based-authentication-of-rest-services-with-spring-security-and-pinch-of-spring-java-configuration-and-spring-integration-testing/)

* [**Securing Spring Boot REST APIs with Keycloak** on medium.com](https://medium.com/devops-dudes/securing-spring-boot-rest-apis-with-keycloak-1d760b2004e)

* [**Java JWT** on github.com](https://github.com/auth0/java-jwt)

* [**Spring Security with JWT for REST API** on toptal.com](https://www.toptal.com/spring/spring-security-tutorial)

* [**Spring Boot 2 JWT Authentication with Spring Security** on bezkoder.com](https://bezkoder.com/spring-boot-jwt-mysql-spring-security-architecture/)

* [**Verifying JWT signed with the RS256 algorithm using public key in Spring Boot** on stackoverflow.com](https://stackoverflow.com/questions/61527560/verifying-jwt-signed-with-the-rs256-algorithm-using-public-key-in-spring-boot)


* [**Implementing JWT Authentication on Spring Boot APIs** on auth0.com](https://auth0.com/blog/implementing-jwt-authentication-on-spring-boot/)
