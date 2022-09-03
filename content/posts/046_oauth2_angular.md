# Step-by-step guide how integrate Keycloak with Angular application

*If you're building a large enterprise application or an application that is publicly available you may want to introduce a concept of users, so that they will be able login to their accounts, put their information and do some stuff with your app, if they're allowed to. With this blog post I would like to show how it could be implemented in Angular application using OAuth 2.0 and OpenID Connect frameworks which is implemented in a popular, open source identity provider - Keycloak.*

This is a fourth and the last part of my series on OAuth 2.0. If you're not familiar with I would recommend to stop here and go check the first one ????? link ?????. 

The aim of this post is to show you a basic set up an *Angular* application so that it will be integrated with *Keycloak* and it will be able to consume protected HTTP resource that requires an access token. A full description of how to set up *Keycloak* instance and how to create a simple protected resource with *Spring Boot* I've described in previous two articles. But don't worry if you don't want to do that, I'll explain it later how.

### The goal

For a purpose of this article I've prepared a very simple application which could be used to find out information about movies and display them in a table. Application supports two actions - either fetch all the data or select a single movie by its id.

![movie details](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/6tak7byxdo7iync0t9tb.png)

All data are served by *Java* application, which requires to provide  a valid *OAuth 2.0* access token. If anything goes wrong, for example user will not be allowed to consume certain resource a toast message at the bottom of the screen will show up.

![toast](https://dev-to-uploads.s3.amazonaws.com/i/uyoys8fsgilv6mvsskyp.png)

Apart from frontend app there are two other components in this project. Backend application and Keycloak. First one was already mentioned, in second there are defined users and clients, which are necessary when issuing for an access token.

Both parts are crucial to make our *Angular* application work. I assume that you might not be interested in going thru my previous tutorials to implement everything by yourself and that's why I've prepared *Docker* compose file which will allow to start all necessary applications with a single command with my default configuration. Therefore clone below repository and checkout to a [frontend-start-blog branch](https://github.com/wkrzywiec/keycloak-security-example/tree/frontend-start-blog). It will be our starting point.

Once you've got that we need to start both services, so go to the terminal and in the root directory of a project run following command:

```bash
> docker-compose up -d backend
```

In a first run it could take a little while, but after that it should be good. To check if the applications are running you can use command:

```bash
>  docker ps
IMAGE                               STATUS              PORTS                              NAMES
keycloak-security-example_backend   Up About a minute   0.0.0.0:9000->8080/tcp             backend
jboss/keycloak:11.0.2               Up About a minute   0.0.0.0:8080->8080/tcp, 8443/tcp   keycloak
postgres:13.0-alpine                Up About a minute   0.0.0.0:5432->5432/tcp             postgres
```

All three containers are `Up` so we're good to proceed with configuring a **hosts** file on your machine. Its location depends on the OS:

* [Linux (Ubuntu)](http://manpages.ubuntu.com/manpages/trusty/man5/hosts.5.html)
* [Windows 10](https://www.groovypost.com/howto/edit-hosts-file-windows-10/)
* [Mac](https://www.imore.com/how-edit-your-macs-hosts-file-and-why-you-would-want#page1)

So please find it, open in an admin mode or relevant and add following line:

```
127.0.0.1	keycloak
```

This step is necessary because the address of Keycloak server is different depending on the point of view. From the point of view of an app that is running in the web browser it'll be `http://localhost:8080`, but from the perspective of `backend` application that is running inside the Docker network it will be `http://keycloak:8080`. To overcome it above config is necessary.

If you like you can add similar entries for `frontend` and `backend` (IP address remains the same), because the side effect of it will be that instead of using for example `http://localhost:4200` you can use more meaningful `http://frontend:4200`. But it's totally optional and depends on your preferences.

### Register frontend application in Keycloak

> If you're running my preconfigured Keycloak instance you can skip this part or just quickly go thru it.

Based on OAuth 2.0 protocol we need to register our application in Keycloak, because only allowed services can issue an access token.

Therefore, open the Keycloak page - http://localhost:8080, select **Administration Console** and provide following credentials:

```
username: admin
password: admin
```

After login, in the top right corner there will be displayed a name of a realm into which you're logged in. Make sure that *Test* is selected. 

Now go to the **Clients** page (it's located in the left menu) and click **Create** button located on a right.

![clients](https://dev-to-uploads.s3.amazonaws.com/i/n8nopn650ylqq56atd3a.png)

In a new view we need to provide only a client name, which will be **frontend**.

![frontend client](https://dev-to-uploads.s3.amazonaws.com/i/xugaik0chc7ur6envec6.png)

After hitting the **Save** button a detailed page for newly created client will show up. To finish configurating *frontend* client we need first to make sure that *Access Type* is set to **public**. It indicates that our client is public and will not require secret to get access token. This config is valid for client-side frontends which are not able to securely store secrets for their clients (because the entire code of an application is running in users browser).

Apart from that we need to set up a *Root URL* to *http://localhost:4200* which is a root URL of our application. Also we need to provide a *Valid Redirect URIs* which is very important from security point of view, because here we're defining into which URLs Keycloak can redirect after successfull authentication. We should provide here only our application's URLs, to prevent hackers from doing messy stuff. Therefore here I've got 3 entries: `http://localhost:80/*`, `http://localhost:4200/*`, `http://localhost/*`.

The last thing that needs to be configured is *Web Origins* parameter and here I'm providing `+` which will handle the CORS problem.

![frontend client](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/2a63y9lyaziu15em7r61.png)

After that click **Save** button at the bottom of the screen to finish Keycloak configuration (all other steps, like user and roles definition was already covered in previous blog posts).

### Main view of a page

Now we can deep dive into Angular project. It has only one component (apart from `AppComponent`) - `ContentComponent`.

```js
@Component({
  selector: 'app-content',
  templateUrl: './content.component.html',
  styleUrls: ['./content.component.css']
})
export class ContentComponent {

  movies: Movie[] = []
  displayedColumns: string[] = ['title', 'director', 'year']; 
  
  @ViewChild(MatTable) table: MatTable<any>;

  constructor(
    private backend: MovieBackendService,
    private snackBar: MatSnackBar) {}

  logout() {
    console.log('Logout button was clicked')
  }

  getAllMovies() {
    this.backend.getAllMovies().subscribe(
        
        response => {
          this.movies = response
          this.table.renderRows();          
        },

        error => {
          this.handleError(error.error)
        })
  }

  onMovieIdChange(event: any){
    this.getMovieById(event.value);
  }

  private getMovieById(id: number) {
    this.backend.getMovieById(id).subscribe(
          
        response => {
          this.movies = [response]
          this.table.renderRows();
        },
        
        error => {
          this.handleError(error.error)
        })
  }

  private handleError(error: any) {
    this.displayError(error.code + ' ' + error.reason + ". " + error.message)
  }

  private displayError(message: string) {
    this.snackBar.open(message, 'Close', { duration: 5000})
  }

}
```

To keep you sane and to keep this post short I'll skip showing HTML and CSS files, as the aim of the project is not to look nice. 

From the above code you can see that in order to connect to the backend application it uses the `MovieBackendService` which encapsulates HTTP requests:

```typescript
export interface Movie {
  title: string;
  director: string;
  year: number;
}

export interface Problem {
  code: number;
  reason: string;
  timestamp: string;
  message: string;
}

@Injectable({
  providedIn: 'root'
})
export class MovieBackendService {

  private readonly backendUrl = '/movies'

  constructor(private http: HttpClient) { }

  getAllMovies(): Observable<Array<Movie>> {
    return this.http.get<Array<Movie>>(this.backendUrl);
  }

  getMovieById(id: number): Observable<Movie> {
    return this.http.get<Movie>(this.backendUrl + '/' + id);
  }
}
```

Again, fairly simple.

To make it work I've also set up a proxy configuration, both for development and  production mode. For a first one I've created a `proxy.conf.dev.json` file:

```json
{
    "/movies": {
        "target": "http://localhost:9000",
        "secure": false,
        "logLevel": "debug",
        "changeOrigin": true
    }
}
```

The target field indicates under which address the backend service is available. To apply it I've also modified the `start` script in  `package.json` file:

```json
{
  "name": "frontend",
  "version": "0.0.0",
  "scripts": {
    "ng": "ng",
    "start": "ng serve --proxy-config src/assets/proxy.conf.dev.json",
    "build": "ng build --prod",
    "test": "ng test",
    "lint": "ng lint",
    "e2e": "ng e2e",
    "postinstall": "ngcc"
  },
  //// other part of json file
}
```

For production proxy config I've created the `default.conf` file, which is a configuration of *Nginx* server:

```
server {
    listen 80;
    server_name frontend;
    root /usr/share/nginx/html;
    index index.html index.html;

    location /movies {
        proxy_pass http://backend:9000/movies;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

The `http://backend:9000/movies` is an address of the backend service (if a backend service is running in the same Docker network, or in the same Kubernetes cluster with the same Service name).

Having all of that we can now proceed with adding and configuring Keycloak libraries.

### Basic configuration of Keycloak libraries

First step would be to add [keycloak-angular](https://github.com/mauriciovigolo/keycloak-angular) dependencies to the project, therefore in a terminal run following command:

```bash
> npm install keycloak-angular keycloak-js
```

Having it we now need to config it with our application. What is important here, before running our own code first we need to authenticate a user, show Keycloak's login page and so on. To achieve it we will use an Angular's special `InjectionToken` called `APP_INITIALIZER`. A function, which will be assigned to this token will be executed before loading the rest of an application. 

To create a custom function, that we will than assign to `APP_INITIALIZER` just run this command:

```bash
> ng g class init/keycloak-init --type=factory --skip-tests
CREATE src/app/init/keycloak-init.factory.ts (22 bytes)
```

A new file was created. Open it and paste following content:

```typescript
import { KeycloakService } from "keycloak-angular";

export function initializeKeycloak(
  keycloak: KeycloakService
  ) {
    return () =>
      keycloak.init({
        config: {
          url: 'http://localhost:8080' + '/auth',
          realm: 'test',
          clientId: 'frontend',
        }
      });
}
```

Above function takes as an argument a `KeycloakService` which is an object from `keycloak-angular` library so that we can use it in a body of a function to config it by providing URL to the server, realm name and application's client id which was created a step before.

For now all values are hardcoded here, which of course is not good, but we'll tackle this problem later on.

Next we need to register this function in the `app.module.ts` file, as a `provider`:

```typescript
@NgModule({
  declarations: [
    AppComponent,
    ContentComponent
  ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatSelectModule,
    MatTableModule,
    MatSnackBarModule,
    HttpClientModule,
    KeycloakAngularModule,
    NgbModule,
    AppRoutingModule
  ],
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: initializeKeycloak,
      multi: true,
      deps: [KeycloakService],
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

Take a closer look in the `imports` section. There is `KeycloakAngularModule` added there.

Next step would be to create a *Guard* that will protect routes in an application. The library that we're using is already providing a preconfigured, abstract `KeycloakAuthGuard` class from which we will extend ours. But first let's create one:

```bash
> ng g guard guard/auth --skip-tests

? Which interfaces would you like to implement? CanActivate
CREATE src/app/guard/auth.guard.ts (458 bytes)
```

The content of this *Guard* would be:

```typescript
import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, RouterStateSnapshot, UrlTree, Router } from '@angular/router';
import { KeycloakAuthGuard, KeycloakService } from 'keycloak-angular';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard extends KeycloakAuthGuard {
  
  constructor(
    protected readonly router: Router,
    protected readonly keycloak: KeycloakService
  ) {
    super(router, keycloak);
  }
  
  async isAccessAllowed(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Promise<boolean | UrlTree> {
    
    if (!this.authenticated) {
      await this.keycloak.login({
        redirectUri: window.location.origin + state.url,
      });
    }

    return this.authenticated;
  }
}
```

In the `isAccessAllowed` method we're adding the piece that will redirect a user to a login page if she/he is not authenticated yet. 

To finish this part, the only thing to do is to add this *Guard* to the `app-routing.module.ts`.

```typescript
const routes: Routes = [
  { path: '', component: ContentComponent , canActivate: [AuthGuard]},
  { path: '**', redirectTo: '' }
];

@NgModule({
  declarations: [],
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
```

Having all of that we can test it! Make sure that both backend and Keycloak services needs to be running ( `docker-compose up -d backend` ) and run the command:

```bash
> npm start

> frontend@0.0.0 start .\keycloak-security-example\frontend
> ng serve --proxy-config src/assets/proxy.conf.dev.json

- Generating browser application bundles...[HPM] Proxy created: /movies  ->  http://localhost:9000
[HPM] Subscribed to http-proxy events:  [ 'error', 'close' ]
√ Browser application bundle generation complete.

Initial Chunk Files   | Names         |      Size
vendor.js             | vendor        |   5.11 MB
styles.css, styles.js | styles        | 562.38 kB
polyfills.js          | polyfills     | 493.08 kB
main.js               | main          |  40.76 kB
runtime.js            | runtime       |   6.15 kB

                      | Initial Total |   6.18 MB

Build at: 2021-02-20T15:55:55.362Z - Hash: 360dd85cc05c08ec0698 - Time: 14478ms

** Angular Live Development Server is listening on localhost:4200, open your browser on http://localhost:4200/ **


√ Compiled successfully.
```

Now if you open the `http://localhost:4200/` page you should be redirected to the login page:

![Alt Text](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/499boolg86uty2m6s8fz.png)

And provide credentials:

```
username: han/luke
password: password
```

After that you should be able to enter the main page! If you now try to play around with an app, by clicking `All movies` button or selecting movie by id, in one of the cases you'll get this kind of an error:

![unauthorized](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/nu2vs0zrbgbt4vmtf0d6.png)

This toast message inform the user that she/he doesn't have sufficient roles. But how application knows that? 

First of all after successful login OAuth2.0 tokens were fetched from the Keycloak server and stored in your web browser. Now if there is any request made to the backend service our great Keycloak library is adding the `Authorization` HTTP header with an access token. And such is required to be consumed by the backend application. It validates a content of a token and returns OK response if everything is fine, or returns an error if token is corrupted or user is not allowed to consume specific endpoint (because she/he doesn't have sufficient roles).

### Productionize Keycloak configuration

So far so good, we've got a working piece of code. But there is one problem with this approach. If we would need to change the Keycloak's URL, realm name or client (development, test and production environment can be different) we would be forced to change it in the code for each version, as all these values are hardcoded.

To overcome this problem we need to externalize configuration of an app. My approach would be to pass those values from the environment variable during startup of an application. Because we're using Docker it's quite easy to achieve.

First step is to create separate configuration files for two cases - development and production. Therefore in the **assets** folder create a new **config** folder inside of which place these two following files:

* **config.dev.json**

```json
{
    "KEYCLOAK_URL": "http://localhost:8080",
    "KEYCLOAK_REALM": "test",
    "KEYCLOAK_CLIENT_ID": "frontend"
}
```

* **config.prod.json**

```json
{
    "KEYCLOAK_URL": "${KEYCLOAK_URL}",
    "KEYCLOAK_REALM": "${KEYCLOAK_REALM}",
    "KEYCLOAK_CLIENT_ID": "${KEYCLOAK_CLIENT_ID}"
}
```

In the latter config file there are no hardcode values, just a placeholder for environment variables, which will be replaced during the startup of an application.

Next step would be to make use of these two configuration. Therefore got to **environments** directory and add a `configFile` value which will point out to a different config file.

* **environment.ts**

```typescript
export const environment = {
  production: false,
  configFile: 'assets/config/config.dev.json'
};
```

* **environment.prod.ts**

```typescript
export const environment = {
  production: true,
  configFile: 'assets/config/config.json'
};
```

Also create a new file, **environment.dev.ts** which will be the same as the default one:

```typescript
export const environment = {
  production: false,
  configFile: 'assets/config/config.dev.json'
};
```

Having that we could now move on to the code and make use of it, but after the *dev* environment is not fully setup. We need to add this new environment to an Angular configuration.

Therefore open the **angular.json** file and locate the `projects.frontend.architect.build.configurations` section and add `dev` configuration which will be replacing the default `environment.ts` file with `environment.dev.ts`: 

```json
{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "frontend": {
      "projectType": "application",
      "schematics": {...},
      "root": "",
      "sourceRoot": "src",
      "prefix": "app",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:browser",
          "options": {...},
          "configurations": {
            "dev": {
              "fileReplacements": [
                {
                  "replace": "src/environments/environment.ts",
                  "with": "src/environments/environment.dev.ts"
                }
              ]
            },
            "production": {...}

// further configuration
```

In the same file, scroll down a little bit to the `serve` section and in `configurations` add new `dev` entry with `browserTarget`:

```json
"architect": {
        "build": {...},
        "serve": {
          "builder": "@angular-devkit/build-angular:dev-server",
          "options": {...},
          "configurations": {
            "dev": {
              "browserTarget": "frontend:build:dev"
            },
            "production": {
              "browserTarget": "frontend:build:production"
            }
          }
        },

// further configuration
```

Finally we can go to the **package.json** file in which we can specify that when we want to run the `start` script we would like to enable the `dev` profile, by adding the `-c dev` parameter.

```json
{
  "name": "frontend",
  "version": "0.0.0",
  "scripts": {
    "ng": "ng",
    "start": "ng serve --proxy-config src/assets/proxy.conf.dev.json -c dev",
    "build": "ng build --prod",
    "test": "ng test",
    "lint": "ng lint",
    "e2e": "ng e2e",
    "postinstall": "ngcc"
  },
  //// other part of json file
}
```

After this change once we run the `npm start` the Angular app will be build with `dev` configuration. 

If we run an application right now nothing will change, because we only registered a new application profile, but haven't make a use of it in the code. Therefore let's now focus on the code itself.

Right now we're initializing `KeycloakService` before the entire application. What we need to do now is to load configuration before `KeycloakService`. To do that first let's create a `ConfigInitService` which will load a configuration file and assign it's values to a variable.

```bash
> ng g service init/config-init --skip-tests
CREATE src/app/init/config-init.service.ts (140 bytes)
```

And the content of this service class in which we're using the environment's value that points out to the correct configuration file (dev or prod).

```typescript
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ConfigInitService {

  private config: any;

  constructor(private httpClient: HttpClient) {}

  public getConfig(): Observable<any> {
    return this.httpClient
        .get(this.getConfigFile(), {
          observe: 'response',
        })
        .pipe(
          catchError((error) => {
            console.log(error)
            return of(null)
          } ),
          mergeMap((response) => {
            if (response && response.body) {
              this.config = response.body;
              return of(this.config);
            } else {
              return of(null);
            }
          }));
  }

  private getConfigFile(): string {
    return environment.configFile
  }
}
```

Next, we need to go back to the *keycloak-init.factory.ts* and adjust it so that `getConfig()` method of above service is invoked before `KeycloakService` initialization.

```typescript
export function initializeKeycloak(
  keycloak: KeycloakService,
  configService: ConfigInitService
  ) {
    return () =>
      configService.getConfig()
        .pipe(
          switchMap<any, any>((config) => {

            return fromPromise(keycloak.init({
              config: {
                url: config['KEYCLOAK_URL'] + '/auth',
                realm: config['KEYCLOAK_REALM'],
                clientId: config['KEYCLOAK_CLIENT_ID'],
              }
            }))
              
          })
        ).toPromise()
}
```

This time a code is a little bit complicated. `confiService` is returning the `config` object from which we can get necessary values.

Last thing to do in the app code is to register a `ConfigInitService` in `app.module.ts` and pass it to the `APP_INITIALIZER`.

```typescript
@NgModule({
  declarations: [...],
  imports: [...],
  providers: [
    ConfigInitService,
    {
      provide: APP_INITIALIZER,
      useFactory: initializeKeycloak,
      multi: true,
      deps: [KeycloakService, ConfigInitService],
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

If we run the `npm start` command the app will start up and works as previously. Awesome, we're in the same situation as we were previously.

Let's move forward and change the Docker image definition. If you look at the `Dockerfile` for frontend app it looks pretty straightforward:

```dockerfile
### STAGE 1: Build ###
FROM node:12.7-alpine AS build
WORKDIR /usr/src/app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

### STAGE 2: Run ###
FROM nginx:1.19.3-alpine
COPY default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /usr/src/app/dist/frontend /usr/share/nginx/html
EXPOSE 80
```

It's a two stage Dockerfile, in first step a project is build to HTML, CSS and JSes and in the second step all these files are copied to an *NGINX* server together with simple server configuration in *default.conf* file. 

What we need to change in above file is to somehow replace placeholders from *config.prod.json* with relevant environment variables that will injected into Docker container during startup. Apart from that it would be to do similar thing with *default.conf* file in which we've got a `proxy_pass` defined which routes traffic to the backend service. Instead of hardcoding the backend URL we can allow to dynamically assigning it during container startup.

Therefore in `default.conf` file we need to replace the `http://backend:900` value to `${BACKEND_BASE_PATH}`.

```
server {
    listen 80;
    server_name frontend;
    root /usr/share/nginx/html;
    index index.html index.html;

    location /movies {
        proxy_pass ${BACKEND_BASE_PATH}/movies;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

But we still have a problem, how to replace those placeholders with values from environment variables? Nothing simpler, we can use [envsubt](https://www.gnu.org/software/gettext/manual/html_node/envsubst-Invocation.html) bash command.

First, let's create a bash script located in the root folder of frontend project and call it **replace_placeholders.sh**:

```bash
#!/bin/bash

envsubst < /usr/share/nginx/html/assets/config/config.prod.json > /usr/share/nginx/html/assets/config/config.json
envsubst "\$BACKEND_BASE_PATH" < /temp/default.conf > /etc/nginx/conf.d/default.conf

exec "$@"
```

In a first line we're replacing the placeholders from **config.prod.json** and as a result it generates a **config.json** file with values from environment variables (which holds Keycloak url, realm and client info). With the second line we're replacing only one placeholder with a base url to the backend application in **default.conf** - NGINX server configuration.

Having it setup we can change **Dockerfile** definition, so that it will copy a script to a container and run it during the startup. 

```dockerfile
### STAGE 1: Build ###
FROM node:12.7-alpine AS build
WORKDIR /usr/src/app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

### STAGE 2: Run ###
FROM nginx:1.17.1-alpine
COPY default.conf /temp/default.conf
COPY replace_placeholders.sh /
COPY --from=build /usr/src/app/dist/frontend /usr/share/nginx/html
EXPOSE 80
ENTRYPOINT [ "sh", "/replace_placeholders.sh" ]
CMD ["nginx",  "-g", "daemon off;"]
```

Finally to run the application we need to declare those environment variables. Depending on how you would like to run the application there are many ways to achieve it. For example they can be declared in OS, passing them as parameters using Docker commands, using Docker Compose file or be declared in Kubernetes Deployment or ConfigMap. 

For me the most convenient is to use Docker Compose (*docker-compose.yaml* file located in the project root) 

```yaml
version: "3.8"

services:
  
  frontend:
    build: ./frontend
    container_name: frontend
    ports:
      - 80:80
    environment: 
      - KEYCLOAK_URL=http://keycloak:8080
      - KEYCLOAK_REALM=test
      - KEYCLOAK_CLIENT_ID=frontend
      - BACKEND_BASE_PATH=http://backend:9000
    depends_on:
      - keycloak
      - backend

  # definitions of other services
```

Now run the following command and a Docker container will be created and then started.

```bash
> docker-compose up -d frontend
```

To check if everything is working we can list Docker containers:

```bash
> docker ps

CONTAINER ID    STATUS          PORTS                              NAMES
1840d7564aeb   Up 46 seconds   0.0.0.0:80->80/tcp                 frontend
cba18013881c   Up 47 seconds   0.0.0.0:9000->9000/tcp             backend
01f15608d210   Up 47 seconds   0.0.0.0:8080->8080/tcp, 8443/tcp   keycloak
ac67959019f9   Up 48 seconds   0.0.0.0:5432->5432/tcp             postgres
```

Than go to a web browser and type `http://localhost` so it will redirect you to the login page and once you login you can play around with an app.

![Alt Text](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/092we36k38ii8tx3dvf9.png)

That's it for today and for entire series about OAuth 2.0 framework. I hope you've enjoyed and learnt some new things. Please let me know in the comments what do you think. 

The entire code for this project can be found in my GitHub repository:

* https://github.com/wkrzywiec/keycloak-security-example

??? Lista pozostałych blogów ???

## References

* [**mauriciovigolo/keycloak-angular** on github.com](https://github.com/mauriciovigolo/keycloak-angular)

https://medium.com/@ryanchenkie_40935/angular-authentication-using-route-guards-bf7a4ca13ae3    