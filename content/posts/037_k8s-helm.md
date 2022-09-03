# How to deploy application on Kubernetes with Helm
> Source: https://wkrzywiec.medium.com/how-to-deploy-application-on-kubernetes-with-helm-39f545ad33b8

*In this blog post I present step-by-step how to deploy multiple applications on Kubernetes cluster using Helm.*

![Photo by [Andrew Neel](https://unsplash.com/@andrewtneel?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/10468/0*5-etYors2H5neRJt)*Photo by [Andrew Neel](https://unsplash.com/@andrewtneel?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

This is a second part of my series on Kubernetes. It compares three approaches of deploying applications:

* with **kubectl** — [Deployment of multiple apps on Kubernetes cluster — Walkthrough](https://medium.com/@wkrzywiec/deployment-of-multiple-apps-on-kubernetes-cluster-walkthrough-e05d37ed63d1)

* with **Helm** — this one,

* with **helmfile** —[How to declaratively run Helm charts using helmfile](https://medium.com/@wkrzywiec/how-to-declaratively-run-helm-charts-using-helmfile-ac78572e6088).

If you haven’t read it first one, I would advise to do that and then go back to this post. But if you prefer to jump right away to this post, don’t worry, I’ll briefly introduce you to the project.

![cluster](https://dev-to-uploads.s3.amazonaws.com/i/ckgv04imrimtukgqn4er.png)

Above picture presents the target solution. Inside the cluster there will be deployed frontend (*kanban-ui*) and backend (*kanban-app*) services together with postgres database. A source code for both microservices can be found in my GitHub repository — [kanban-board](https://github.com/wkrzywiec/kanban-board).

Additionally I’ve added an *adminer*, which is a GUI client for getting inside the database.

If we focus on one of services, e.g. on *kanban-ui* we can see that it needs to create two Kubernetes objects — *ClusterIP* & *Deployment*. With plain approach, using kubectl we would needed to create two files for each Kubernetes object:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: kanban-ui
  labels: 
    group: backend
spec:
  type: ClusterIP
  selector:
    app: kanban-ui
  ports:
    - port: 80
      targetPort: 80
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kanban-ui
  labels:
    app: kanban-ui
    group: frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kanban-ui
  template:
    metadata:
      labels:
        app: kanban-ui
        group: frontend
    spec:
      containers:
        - name: kanban-ui
          image: wkrzywiec/kanban-ui:k8s
          ports:
            - containerPort: 80
```

The same story is for any other application — they need at least two definition files. Some of them requires even more, like postgres, which needs to have *PersistentVolumeClaims* defined in addition. As a result for even small project we can end up with lots of files which are very similar to each other:

![definitions](https://dev-to-uploads.s3.amazonaws.com/i/i33b21k4m9gxzzjpk3l3.png)


> How to achieve the DRY in this case? Is it possible?

To reduce the number of YAML files we could merge them into one, for example, for *kanban-ui* it will look like this:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: kanban-ui
  labels: 
    group: backend
spec:
  type: ClusterIP
  selector:
    app: kanban-ui
  ports:
    - port: 80
      targetPort: 80
---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: kanban-ui
  labels:
    app: kanban-ui
    group: frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kanban-ui
  template:
    metadata:
      labels:
        app: kanban-ui
        group: frontend
    spec:
      containers:
        - name: kanban-ui
          image: wkrzywiec/kanban-ui:k8s
          ports:
            - containerPort: 80
```

But it still doesn’t fix the major problem — how to avoid copy-pasting entire file just to replace couple of values? It would be great if there is a way to define a blueprint for both objects and then inject values into specific fields.

Luckily there is a solution! [**Helm**](https://helm.sh) to the rescue!

Accordingly to the official website — *Helm* is a package manager for *Kubernetes*. It helps deploy complex application by bundling necessary resources into **Charts**, which contains all information to run application on a cluster.

There are couple approaches how to work with *Helm*. One of them is to download publicly available charts from the [Helm Hub](https://hub.helm.sh). They are prepared by community and are free to use.

For instance, if we would like to run [Prometheus](https://prometheus.io) on a cluster it would just easy as it’s described on this page — [https://hub.helm.sh/charts/stable/prometheus](https://hub.helm.sh/charts/stable/prometheus) — with the single command:

```bash
> helm install stable/prometheus
```

It contains some default configuration, but can be easily overridden with YAML file and passed during installation. The detailed example I’ll show in a minute.

But *Helm* is not only providing some predefined blueprints, you can create your own charts!

It’s very easy and can be done by a single command `helm create <chart-name>` , which creates a folder with a basic structure:

```bash
> helm create example
Creating example
```

![helm chart](https://dev-to-uploads.s3.amazonaws.com/i/e4c9iyaelmygx3i7z8cp.png)

In the templates/ folder there are **Helm templates** that with combination of values.yaml will result in set of Kubernetes objects.

Let’s create a first chart — **postgres**.

But just before that, boring installations and configurations (but promise, it’ll go quick). In my demo I’m using:

* [Docker](https://docs.docker.com/install/),

* locally installed Kubernetes cluster — [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/),

* Kubernetes command line tool —[ kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/),

* [Helm (v3)](https://helm.sh/docs/intro/install/).

When everything is installed you can start up the minikube cluster and enable ingress addon:

```bash
> minikube start

😄  minikube v1.8.1 on Ubuntu 18.04
✨  Automatically selected the docker driver
🔥  Creating Kubernetes in docker container with (CPUs=2) (8 available), Memory=2200MB (7826MB available) ...
🐳  Preparing Kubernetes v1.17.3 on Docker 19.03.2 ...
▪ kubeadm.pod-network-cidr=10.244.0.0/16
❌  Unable to load cached images: loading cached images: stat /home/wojtek/.minikube/cache/images/k8s.gcr.io/kube-proxy_v1.17.3: no such file or directory
🚀  Launching Kubernetes ...
🌟  Enabling addons: default-storageclass, storage-provisioner
⌛  Waiting for cluster to come online ...
🏄  Done! kubectl is now configured to use "minikube"

> minikube addons enable ingress
🌟  The 'ingress' addon is enabled
```

Then you’ll need to edit you **hosts** file. Its location varies on OS:

* [Ubuntu](http://manpages.ubuntu.com/manpages/trusty/man5/hosts.5.html)

* [Windows](https://www.groovypost.com/howto/edit-hosts-file-windows-10/)

* [MacOS](https://www.imore.com/how-edit-your-macs-hosts-file-and-why-you-would-want#page1)

When you find it add following lines:

```
172.17.0.2  adminer.k8s.com
172.17.0.2  kanban.k8s.com
```
To make sure that this config is correct you’ll need to check if an IP address of *minikube* cluster on your machine is the same as it’s above. In order to do that run the command:

```bash
> minikube ip
    172.17.0.2
```

Now we can create first Helm chart:

```bash
> helm create postgres
Creating postgres
```

We will not need generated files inside `./templates` folder, so remove them and also clear all the content inside **values.yaml**.

Now we can roll up our sleeves and define all necessary files to create chart for postgres database. For a reminder, in order to deploy it with *kubectl* we had to have following files:

![postgres files](https://dev-to-uploads.s3.amazonaws.com/i/o4jdmxf8a3dvq7x0f3go.png)

They contain definitions of *ConfigMap, Deployment, PersistentVolumeClaim* and *ClusterIP*. Their full definitions could be found [in a repository](https://github.com/wkrzywiec/k8s-helm-helmfile/tree/master/k8s).

First, let’s create a template for postgres *Deployment* object, therefore inside the `./templates` create a **deployment.yaml** file:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.postgres.name }}
  labels:
    app: {{ .Values.postgres.name }}
    group: {{ .Values.postgres.group }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Values.postgres.name }}
  template:
    metadata:
      labels:
        app: {{ .Values.postgres.name }}
        group: {{ .Values.postgres.group }}
    spec:
      volumes:
        - name: {{ .Values.postgres.volume.name }}
          persistentVolumeClaim:
            claimName: {{ .Values.postgres.volume.pvc.name }}
      containers:
        - name: {{ .Values.postgres.name }}
          image: {{ .Values.postgres.container.image }}  
          ports:
            - containerPort: {{ .Values.postgres.container.port }}
          envFrom:
            - configMapRef:
                name: {{ .Values.postgres.config.name }}
          volumeMounts:             
            - name: {{ .Values.postgres.volume.name }}
              mountPath: {{ .Values.postgres.volume.mountPath }}
```

At first glance you might see these strange parts between two pairs of curly brackets, like `{{ .Values.postgres.name }}` . They are written in [Go template language](https://golang.org/pkg/text/template/) and are referring to a value located in a **values.yaml** which is located inside the root folder of a chart. For mentioned example Helm will try to match it with a value from *values.yaml*:

```yaml
postgres:
    name: postgres
```

Another example. A value for a base Docker image, defined in image: `{{ .Values.postgres.container.image }}` will be taken from:

```yaml
postgres:
    name: postgres
    container:
        image: postgres:9.6-alpine
```

And so on. We can define the structure inside this file whatever we like.

This database Deployment requires a *PersistentVolumeClaim* to be created to reserve some storage on a disk, therefore we need to create a Helm template — **pvc.yaml** inside the `./templates` folder:

```yaml
apiVersion: v1
kind: {{ .Values.postgres.volume.kind }}
metadata:
  name: {{ .Values.postgres.volume.pvc.name }}
spec:
  accessModes:
    - {{ .Values.postgres.volume.pvc.accessMode }}
  resources:
    requests:
      storage: {{ .Values.postgres.volume.pvc.storage }}
```

This one is shorter, and there is nothing new here.

Next template that we need to create is for *ClusterIP*, which will allow other *Pods* inside the cluster to enter the* Pod with postgres — **service.yaml**:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.postgres.name }}
  labels: 
    group: {{ .Values.postgres.group }}
spec:
  type: {{ .Values.postgres.service.type }}
  selector:             
    app: {{ .Values.postgres.name }}
  ports:
    - port: {{ .Values.postgres.service.port }}       
      targetPort: {{ .Values.postgres.container.port }}   
```

And finally *ConfigMap* template needs to be created — **config.yaml**. It’ll hold information about created database, user and its password (yes, not very secure, but for simple example it’s enough).

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Values.postgres.config.name }}
  labels:
    group: {{ .Values.postgres.group }}
data: 
{{- range .Values.postgres.config.data }}
  {{ .key }}: {{ .value }}
{{- end}}
```

Here you might see a strange `{{ -range ... }}` clause, which can be translated as a for each loop known in any programming language. In above example, Helm template will try to inject values from an array defined in *values.yaml*:

```yaml
postgres:
    config:
        data:
        - key: key
          value: value
```

Inside a template, there are only dummy values. If you want to have different ones you would need to override them during installation of this set of objects on a Kubernetes cluster.

The entire *values.yaml* presents as follow:
```yaml
replicaCount: 1

postgres:
    name: postgres
    group: db
    container:
        image: postgres:9.6-alpine
        port: 5432
    service:
        type: ClusterIP
        port: 5432
    volume:
        name: postgres-storage
        kind: PersistentVolumeClaim
        mountPath: /var/lib/postgresql/data
        pvc:
          name: postgres-persistent-volume-claim
          accessMode: ReadWriteOnce
          storage: 4Gi
    config:
        name: postgres-config
        data:
        - key: key
          value: value
```

To finalize creating first chart we need to modify some metadata inside **Chart.yaml** file:

```yaml
apiVersion: v2
name: postgres
description: A Helm chart for PostgreSQL database
type: application
version: 0.1.0
appVersion: 1.16.0
keywords:
  - database
  - postgres
home: https://github.com/wkrzywiec/k8s-helm-helmfile/tree/master/helm
maintainers:
  - name: Wojtek Krzywiec
    url: https://github.com/wkrzywiec
```

Then create a new **kanban-postgres.yaml** file which will hold some specific values. Put it outside the `postgres` chart folder so the file structure can be similar to that:

![postgres chart](https://dev-to-uploads.s3.amazonaws.com/i/w56u3502tqrr04fvhpon.png)

Inside the file put only values that will be specific for this deployment, i.e. postgres database credentials (all other values we can keep as default):

```yaml
postgres:
    config:
        data:
        - key: POSTGRES_DB
          value: kanban
        - key: POSTGRES_USER
          value: kanban
        - key: POSTGRES_PASSWORD
          value: kanban
```

Everything is set up, we can now deploy postgres into a cluster. In a Helm world this step is called creating a new **release**:

```bash
> helm install -f kanban-postgres.yaml postgres ./postgres
NAME: postgres
LAST DEPLOYED: Mon Apr 13 16:13:16 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None

> helm list
NAME     NAMESPACE REVISION  STATUS    CHART          APP VERSION
postgres default   1         deployed  postgres-0.1.0 1.16.0

> kubectl get deployments
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
postgres   1/1     1            1           2m14s
```

Cool, the postgres is up and running! Before moving forward let’s have a closer look on helm install command, what each of an argument means:

![helm install](https://dev-to-uploads.s3.amazonaws.com/i/11c3sxgkvr540ypg0xhy.png)

If you plan to use a chart only to create one Helm release you might wonder what is a value behind using Helm at all.

Let me show you that on another example. Let’s create a new chart called **app** — it will be a template chart for three different releases — *adminer*, *kanban-app* & *kanban-ui*.

```bash
> helm create app
Creating app
```

After removing unnecessary file from `./templates` folder and cleaning the **values.yaml** create a **deployment.yaml** file:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.app.name }}
  labels:
    app: {{ .Values.app.name }}
    group: {{ .Values.app.group }}
spec:
  replicas: {{ .Values.app.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Values.app.name }}
  template:
    metadata:
      labels:
        app: {{ .Values.app.name }}
        group: {{ .Values.app.group }}
    spec:
      containers:
        - name: {{ .Values.app.name }}
          image: {{ .Values.app.container.image }}  
          ports:
            - containerPort: {{ .Values.app.container.port }}
          envFrom:
            {{- range .Values.app.container.config }}
            - configMapRef:
                name: {{ .name }}
            {{- end}}
          env:
            {{- range .Values.app.container.env}}
            - name: {{ .key}}
              value: {{ .value}}
            {{- end}} 
```

Nothing new in particular, only some placeholders for values & two range loops to inject values from *ConfigMap*s or simple values to application container.

All 3 apps require to have also the *ClusterIP* objects to be deployed, therefore here is its template — **service.yaml**:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.app.name }}
  labels: 
    group: {{ .Values.app.group }}
spec:
  type: {{ .Values.app.service.type }}
  selector:             
    app: {{ .Values.app.name }}
  ports:
    - port: {{ .Values.app.service.port }}       
      targetPort: {{ .Values.app.container.port }}  
```

All default values in both templates are injected from **values.yaml**:

```yaml
app:
    name: app
    group: app
    replicaCount: 1
    container:
        image: add-image-here
        port: 8080
        config: []
        env:
        - key: key
          value: value
    service:
        type: ClusterIP
        port: 8080
```

And to close a task of creating app chart — we need to define some metadata in the **Chart.yaml** file:

```yaml
apiVersion: v2
name: app
description: A Helm chart for any application
type: application
version: 0.1.0
appVersion: 1.16.0
keywords:
  - app
  - java
  - javascript
  - angular
home: https://github.com/wkrzywiec/k8s-helm-helmfile/tree/master/helm
maintainers:
  - name: Wojtek Krzywiec
    url: https://github.com/wkrzywiec
```

Then, similarly to previous example, outside the app folder create YAML files with values which will override ones from *values.yaml* inside app chart.

An **adminer.yaml** file looks as follow:

```yaml
app:
  name: adminer
  group: db
  container:
    image: adminer:4.7.6-standalone
    port: 8080
    env:
      - key: ADMINER_DESIGN
        value: pepa-linha
      - key: ADMINER_DEFAULT_SERVER
        value: postgres
```

A **kanban-app.yaml** file:

```yaml
app:
  name: kanban-app
  group: backend
  container:
    image: wkrzywiec/kanban-app:k8s
    config:
      - name: postgres-config
    env: 
      - key: DB_SERVER
        value: postgres
```

A **kanban-ui.yaml** file:

```yaml
app:
  name: kanban-ui
  group: frontend
  container:
    image: wkrzywiec/kanban-ui:k8s
    port: 80
```

A resulting file structure:

![file structure](https://dev-to-uploads.s3.amazonaws.com/i/m2r3s6tzhz5mfffouajs.png)

Now, in order to create three releases for each application use commands:

```bash
> helm install -f adminer.yaml adminer ./app
NAME: adminer
LAST DEPLOYED: Mon Apr 13 16:57:17 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None

> helm install -f kanban-app.yaml kanban-app ./app
NAME: kanban-app
LAST DEPLOYED: Mon Apr 13 16:57:36 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None

> helm install -f kanban-ui.yaml kanban-ui ./app
NAME: kanban-ui
LAST DEPLOYED: Mon Apr 13 16:57:54 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None

> helm list
NAME       NAMESPACE REVISION  STATUS    CHART           APP VERSION
adminer    default   1         deployed  app-0.1.0       1.16.0     
kanban-app default   1         deployed  app-0.1.0       1.16.0     
kanban-ui  default   1         deployed  app-0.1.0       1.16.0     
postgres   default   1         deployed  postgres-0.1.0  1.16.0

> kubectl get deployments
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
adminer      1/1     1            1           112s
kanban-app   1/1     1            1           93s
kanban-ui    1/1     1            1           75s
postgres     1/1     1            1           45m

Perfect! There is one more thing to do — create a chart with *Ingress Controller* — a gateway to a cluster.

Like before, create a new chart:

```bash
> helm create ingress
Creating ingress
```

Remove all files from templates folder and clear content of *values.yaml*. This time, before moving straight away to defining a templates, let’s focus on to **Chart.yaml** first.

```yaml
apiVersion: v2
name: ingress
description: A Helm chart for Ingress Controller
type: application
version: 0.1.0
appVersion: 1.16.0
keywords:
  - ingress
  - nginx
  - api-gateway
home: https://github.com/wkrzywiec/k8s-helm-helmfile/tree/master/helm
maintainers:
  - name: Wojtek Krzywiec
    url: https://github.com/wkrzywiec
dependencies:
  - name: nginx-ingress
    version: 1.36.0
    repository: https://kubernetes-charts.storage.googleapis.com/
```

Here there is a new section — `dependencies`— which has been added. It creates default backend services which enables the *Ingress Controller* features.

But it’s not the only thing we need to do here. This section only defines on what this chart depends on, it won’t download it automatically during the installation. We need to take care of it ourselves. To do that run the command:

```bash
> helm dependency update ./ingress/
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "stable" chart repository
Update Complete. ⎈Happy Helming!⎈
Saving 1 charts
Downloading nginx-ingress from repo [https://kubernetes-charts.storage.googleapis.com/](https://kubernetes-charts.storage.googleapis.com/)
Deleting outdated charts
```

Inside the `ingress/charts` folder a new file will appear — `nginx-ingress-1.36.0.tgz` .

Now we can define a template for Ingress — it will be located inside `./templates` folder and will be called **ingress.yaml**:

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: {{ .Values.ingress.name }}
  annotations:
    kubernetes.io/ingress.class: {{ .Values.ingress.annotations.class }}
spec:
  rules:
  {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
        {{- range .paths }}
          - path: {{ .path }}
            backend:
              serviceName: {{ .backend.serviceName }}
              servicePort: {{ .backend.servicePort }}
        {{- end }}
  {{- end }}
```

The most interesting part is inside specification section. There are two nested loops there which allow to define multiple hosts and multiple paths for each host.

And also, here is a default **values.yaml** file:

```yaml
ingress:
  name: ingress-service
  replicaCount: 1
  annotations: 
    class: nginx
  hosts:
    - host: chart-example.local
      paths: 
        - path: /
          backend:
            serviceName: serviceName
            servicePort: 8080
```

The resulting folder structure:

![ingress chart](https://dev-to-uploads.s3.amazonaws.com/i/sqiwsyhypd72rw0lh082.png)

Outside the `ingress` chart we can now create an *ingress.yaml* file which will hold all routing rules for our cluster.

```yaml
ingress:
  hosts:
    - host: adminer.k8s.com
      paths:
        - path: /
          backend:  
            serviceName: adminer
            servicePort: 8080
    - host: kanban.k8s.com
      paths: 
        - path: /api/
          backend:
            serviceName: kanban-app
            servicePort: 8080
        - path: /
          backend:
            serviceName: kanban-ui
            servicePort: 80
```

And now we’re able to create a Helm release:

```bash
> helm install -f ingress.yaml ingress ./ingress
NAME: ingress
LAST DEPLOYED: Tue Apr 14 07:22:44 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None

> helm list
NAME       NAMESPACE  REVISION  STATUS    CHART          APP VERSION
adminer    default    1         deployed  app-0.1.0      1.16.0     
ingress    default    1         deployed  ingress-0.1.0  1.16.0     
kanban-app default    1         deployed  app-0.1.0      1.16.0     
kanban-ui  default    1         deployed  app-0.1.0      1.16.0     
postgres   default    1         deployed  postgres-0.1.0 1.16.0

> kubectl get deployments
NAME                                    READY  UP-TO-DATE  AVAILABLE
adminer                                 1/1    1           1           
ingress-nginx-ingress-controller        1/1    1           1           
ingress-nginx-ingress-default-backend   1/1    1           1           
kanban-app                              1/1    1           1           
kanban-ui                               1/1    1           1           
postgres                                1/1    1           1           
```

Everything is set up, you can start testing it. Go to the [http://kanban.k8s.com](http://kanban.k8s.com) and you should get this page:

![kanban-ui](https://dev-to-uploads.s3.amazonaws.com/i/icmrf5t4lmmq0i0abnh7.png)

Congrats! 🍾🤘

## Conclusions

In this short entry I’ve presented how, with Helm, you can reduce of copy-pasting tasks and can bring a one single template for deploying multiple applications on a Kubernetes cluster, which might be very handy in a microservice world. I hope you’ve enjoyed it.

But there is still one thing left, which holds us from establishing a fully declarative approach for an infrastructure. In order to deploy each application we still need to run imperative commands, like helm install. But luckily there is another tool — helmfile! But this one I’ll describe in my next story.

For now, here is my GitHub repository with a source code for this project:
[**wkrzywiec/k8s-helm-helmfile** on github.com](https://github.com/wkrzywiec/k8s-helm-helmfile)

And here is a source code of Kanban project:
[**wkrzywiec/kanban-board** on github.com](https://github.com/wkrzywiec/kanban-board)

## References
* [**Docs Home** on helm.sh](https://helm.sh/docs/)
* [**HELM Best practices** on codefresh.io](https://codefresh.io/docs/docs/new-helm/helm-best-practices/)
* [**Package Kubernetes Applications with Helm** on akomljen.com](https://akomljen.com/package-kubernetes-applications-with-helm/)
* [**Drastically Improve your Kubernetes Deployments with Helm** on itnext.io](https://itnext.io/drastically-improve-your-kubernetes-deployments-with-helm-5323e7f11ef8)
* [**alexellis/helm3-expressjs-tutorial** on github.com](https://github.com/alexellis/helm3-expressjs-tutorial)



> Cover image by [Andrew Neel](https://unsplash.com/@andrewtneel) on [Unsplash](https://unsplash.com)](https://cdn-images-1.medium.com/max/10468/0*5-etYors2H5neRJt)

*In this blog post I present step-by-step how to deploy multiple applications on Kubernetes cluster using Helm.*

This is a second part of my series on Kubernetes. It compares three approaches of deploying applications:

* with **kubectl** — [Deployment of multiple apps on Kubernetes cluster — Walkthrough](https://dev.to/wkrzywiec/deployment-of-multiple-apps-on-kubernetes-cluster-walkthrough-32km)

* with **Helm** — this one,

* with **helmfile** — soon.

If you haven’t read it first one, I would advise to do that and then go back to this post. But if you prefer to jump right away to this post, don’t worry, I’ll briefly introduce you to the project.

![cluster](https://dev-to-uploads.s3.amazonaws.com/i/ckgv04imrimtukgqn4er.png)

Above picture presents the target solution. Inside the cluster there will be deployed frontend (*kanban-ui*) and backend (*kanban-app*) services together with postgres database. A source code for both microservices can be found in my GitHub repository — [kanban-board](https://github.com/wkrzywiec/kanban-board).

Additionally I’ve added an *adminer*, which is a GUI client for getting inside the database.

If we focus on one of services, e.g. on *kanban-ui* we can see that it needs to create two Kubernetes objects — *ClusterIP* & *Deployment*. With plain approach, using kubectl we would needed to create two files for each Kubernetes object:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: kanban-ui
  labels: 
    group: backend
spec:
  type: ClusterIP
  selector:
    app: kanban-ui
  ports:
    - port: 80
      targetPort: 80
```

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kanban-ui
  labels:
    app: kanban-ui
    group: frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kanban-ui
  template:
    metadata:
      labels:
        app: kanban-ui
        group: frontend
    spec:
      containers:
        - name: kanban-ui
          image: wkrzywiec/kanban-ui:k8s
          ports:
            - containerPort: 80
```

The same story is for any other application — they need at least two definition files. Some of them requires even more, like postgres, which needs to have *PersistentVolumeClaims* defined in addition. As a result for even small project we can end up with lots of files which are very similar to each other:

![definitions](https://dev-to-uploads.s3.amazonaws.com/i/i33b21k4m9gxzzjpk3l3.png)


> How to achieve the DRY in this case? Is it possible?

To reduce the number of YAML files we could merge them into one, for example, for *kanban-ui* it will look like this:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: kanban-ui
  labels: 
    group: backend
spec:
  type: ClusterIP
  selector:
    app: kanban-ui
  ports:
    - port: 80
      targetPort: 80
---

apiVersion: apps/v1
kind: Deployment
metadata:
  name: kanban-ui
  labels:
    app: kanban-ui
    group: frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kanban-ui
  template:
    metadata:
      labels:
        app: kanban-ui
        group: frontend
    spec:
      containers:
        - name: kanban-ui
          image: wkrzywiec/kanban-ui:k8s
          ports:
            - containerPort: 80
```

But it still doesn’t fix the major problem — how to avoid copy-pasting entire file just to replace couple of values? It would be great if there is a way to define a blueprint for both objects and then inject values into specific fields.

Luckily there is a solution! [**Helm**](https://helm.sh) to the rescue!

Accordingly to the official website — *Helm* is a package manager for *Kubernetes*. It helps deploy complex application by bundling necessary resources into **Charts**, which contains all information to run application on a cluster.

There are couple approaches how to work with *Helm*. One of them is to download publicly available charts from the [Helm Hub](https://hub.helm.sh). They are prepared by community and are free to use.

For instance, if we would like to run [Prometheus](https://prometheus.io) on a cluster it would just easy as it’s described on this page — [https://hub.helm.sh/charts/stable/prometheus](https://hub.helm.sh/charts/stable/prometheus) — with the single command:

```bash
> helm install stable/prometheus
```

It contains some default configuration, but can be easily overridden with YAML file and passed during installation. The detailed example I’ll show in a minute.

But *Helm* is not only providing some predefined blueprints, you can create your own charts!

It’s very easy and can be done by a single command `helm create <chart-name>` , which creates a folder with a basic structure:

```bash
> helm create example
Creating example
```

![helm chart](https://dev-to-uploads.s3.amazonaws.com/i/e4c9iyaelmygx3i7z8cp.png)

In the templates/ folder there are **Helm templates** that with combination of values.yaml will result in set of Kubernetes objects.

Let’s create a first chart — **postgres**.

But just before that, boring installations and configurations (but promise, it’ll go quick). In my demo I’m using:

* [Docker](https://docs.docker.com/install/),

* locally installed Kubernetes cluster — [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/),

* Kubernetes command line tool —[ kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/),

* [Helm (v3)](https://helm.sh/docs/intro/install/).

When everything is installed you can start up the minikube cluster and enable ingress addon:

```bash
> minikube start

😄  minikube v1.8.1 on Ubuntu 18.04
✨  Automatically selected the docker driver
🔥  Creating Kubernetes in docker container with (CPUs=2) (8 available), Memory=2200MB (7826MB available) ...
🐳  Preparing Kubernetes v1.17.3 on Docker 19.03.2 ...
▪ kubeadm.pod-network-cidr=10.244.0.0/16
❌  Unable to load cached images: loading cached images: stat /home/wojtek/.minikube/cache/images/k8s.gcr.io/kube-proxy_v1.17.3: no such file or directory
🚀  Launching Kubernetes ...
🌟  Enabling addons: default-storageclass, storage-provisioner
⌛  Waiting for cluster to come online ...
🏄  Done! kubectl is now configured to use "minikube"

> minikube addons enable ingress
🌟  The 'ingress' addon is enabled
```

Then you’ll need to edit you **hosts** file. Its location varies on OS:

* [Ubuntu](http://manpages.ubuntu.com/manpages/trusty/man5/hosts.5.html)

* [Windows](https://www.groovypost.com/howto/edit-hosts-file-windows-10/)

* [MacOS](https://www.imore.com/how-edit-your-macs-hosts-file-and-why-you-would-want#page1)

When you find it add following lines:

```
172.17.0.2  adminer.k8s.com
172.17.0.2  kanban.k8s.com
```
To make sure that this config is correct you’ll need to check if an IP address of *minikube* cluster on your machine is the same as it’s above. In order to do that run the command:

```bash
> minikube ip
    172.17.0.2
```

Now we can create first Helm chart:

```bash
> helm create postgres
Creating postgres
```

We will not need generated files inside `./templates` folder, so remove them and also clear all the content inside **values.yaml**.

Now we can roll up our sleeves and define all necessary files to create chart for postgres database. For a reminder, in order to deploy it with *kubectl* we had to have following files:

![postgres files](https://dev-to-uploads.s3.amazonaws.com/i/o4jdmxf8a3dvq7x0f3go.png)

They contain definitions of *ConfigMap, Deployment, PersistentVolumeClaim* and *ClusterIP*. Their full definitions could be found [in a repository](https://github.com/wkrzywiec/k8s-helm-helmfile/tree/master/k8s).

First, let’s create a template for postgres *Deployment* object, therefore inside the `./templates` create a **deployment.yaml** file:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.postgres.name }}
  labels:
    app: {{ .Values.postgres.name }}
    group: {{ .Values.postgres.group }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Values.postgres.name }}
  template:
    metadata:
      labels:
        app: {{ .Values.postgres.name }}
        group: {{ .Values.postgres.group }}
    spec:
      volumes:
        - name: {{ .Values.postgres.volume.name }}
          persistentVolumeClaim:
            claimName: {{ .Values.postgres.volume.pvc.name }}
      containers:
        - name: {{ .Values.postgres.name }}
          image: {{ .Values.postgres.container.image }}  
          ports:
            - containerPort: {{ .Values.postgres.container.port }}
          envFrom:
            - configMapRef:
                name: {{ .Values.postgres.config.name }}
          volumeMounts:             
            - name: {{ .Values.postgres.volume.name }}
              mountPath: {{ .Values.postgres.volume.mountPath }}
```

At first glance you might see these strange parts between two pairs of curly brackets, like `{{ .Values.postgres.name }}` . They are written in [Go template language](https://golang.org/pkg/text/template/) and are referring to a value located in a **values.yaml** which is located inside the root folder of a chart. For mentioned example Helm will try to match it with a value from *values.yaml*:

```yaml
postgres:
    name: postgres
```

Another example. A value for a base Docker image, defined in image: `{{ .Values.postgres.container.image }}` will be taken from:

```yaml
postgres:
    name: postgres
    container:
        image: postgres:9.6-alpine
```

And so on. We can define the structure inside this file whatever we like.

This database Deployment requires a *PersistentVolumeClaim* to be created to reserve some storage on a disk, therefore we need to create a Helm template — **pvc.yaml** inside the `./templates` folder:

```yaml
apiVersion: v1
kind: {{ .Values.postgres.volume.kind }}
metadata:
  name: {{ .Values.postgres.volume.pvc.name }}
spec:
  accessModes:
    - {{ .Values.postgres.volume.pvc.accessMode }}
  resources:
    requests:
      storage: {{ .Values.postgres.volume.pvc.storage }}
```

This one is shorter, and there is nothing new here.

Next template that we need to create is for *ClusterIP*, which will allow other *Pods* inside the cluster to enter the* Pod with postgres — **service.yaml**:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.postgres.name }}
  labels: 
    group: {{ .Values.postgres.group }}
spec:
  type: {{ .Values.postgres.service.type }}
  selector:             
    app: {{ .Values.postgres.name }}
  ports:
    - port: {{ .Values.postgres.service.port }}       
      targetPort: {{ .Values.postgres.container.port }}   
```

And finally *ConfigMap* template needs to be created — **config.yaml**. It’ll hold information about created database, user and its password (yes, not very secure, but for simple example it’s enough).

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Values.postgres.config.name }}
  labels:
    group: {{ .Values.postgres.group }}
data: 
{{- range .Values.postgres.config.data }}
  {{ .key }}: {{ .value }}
{{- end}}
```

Here you might see a strange `{{ -range ... }}` clause, which can be translated as a for each loop known in any programming language. In above example, Helm template will try to inject values from an array defined in *values.yaml*:

```yaml
postgres:
    config:
        data:
        - key: key
          value: value
```

Inside a template, there are only dummy values. If you want to have different ones you would need to override them during installation of this set of objects on a Kubernetes cluster.

The entire *values.yaml* presents as follow:
```yaml
replicaCount: 1

postgres:
    name: postgres
    group: db
    container:
        image: postgres:9.6-alpine
        port: 5432
    service:
        type: ClusterIP
        port: 5432
    volume:
        name: postgres-storage
        kind: PersistentVolumeClaim
        mountPath: /var/lib/postgresql/data
        pvc:
          name: postgres-persistent-volume-claim
          accessMode: ReadWriteOnce
          storage: 4Gi
    config:
        name: postgres-config
        data:
        - key: key
          value: value
```

To finalize creating first chart we need to modify some metadata inside **Chart.yaml** file:

```yaml
apiVersion: v2
name: postgres
description: A Helm chart for PostgreSQL database
type: application
version: 0.1.0
appVersion: 1.16.0
keywords:
  - database
  - postgres
home: https://github.com/wkrzywiec/k8s-helm-helmfile/tree/master/helm
maintainers:
  - name: Wojtek Krzywiec
    url: https://github.com/wkrzywiec
```

Then create a new **kanban-postgres.yaml** file which will hold some specific values. Put it outside the `postgres` chart folder so the file structure can be similar to that:

![postgres chart](https://dev-to-uploads.s3.amazonaws.com/i/w56u3502tqrr04fvhpon.png)

Inside the file put only values that will be specific for this deployment, i.e. postgres database credentials (all other values we can keep as default):

```yaml
postgres:
    config:
        data:
        - key: POSTGRES_DB
          value: kanban
        - key: POSTGRES_USER
          value: kanban
        - key: POSTGRES_PASSWORD
          value: kanban
```

Everything is set up, we can now deploy postgres into a cluster. In a Helm world this step is called creating a new **release**:

```bash
> helm install -f kanban-postgres.yaml postgres ./postgres
NAME: postgres
LAST DEPLOYED: Mon Apr 13 16:13:16 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None

> helm list
NAME     NAMESPACE REVISION  STATUS    CHART          APP VERSION
postgres default   1         deployed  postgres-0.1.0 1.16.0

> kubectl get deployments
NAME       READY   UP-TO-DATE   AVAILABLE   AGE
postgres   1/1     1            1           2m14s
```

Cool, the postgres is up and running! Before moving forward let’s have a closer look on helm install command, what each of an argument means:

![helm install](https://dev-to-uploads.s3.amazonaws.com/i/11c3sxgkvr540ypg0xhy.png)

If you plan to use a chart only to create one Helm release you might wonder what is a value behind using Helm at all.

Let me show you that on another example. Let’s create a new chart called **app** — it will be a template chart for three different releases — *adminer*, *kanban-app* & *kanban-ui*.

```bash
> helm create app
Creating app
```

After removing unnecessary file from `./templates` folder and cleaning the **values.yaml** create a **deployment.yaml** file:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.app.name }}
  labels:
    app: {{ .Values.app.name }}
    group: {{ .Values.app.group }}
spec:
  replicas: {{ .Values.app.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Values.app.name }}
  template:
    metadata:
      labels:
        app: {{ .Values.app.name }}
        group: {{ .Values.app.group }}
    spec:
      containers:
        - name: {{ .Values.app.name }}
          image: {{ .Values.app.container.image }}  
          ports:
            - containerPort: {{ .Values.app.container.port }}
          envFrom:
            {{- range .Values.app.container.config }}
            - configMapRef:
                name: {{ .name }}
            {{- end}}
          env:
            {{- range .Values.app.container.env}}
            - name: {{ .key}}
              value: {{ .value}}
            {{- end}} 
```

Nothing new in particular, only some placeholders for values & two range loops to inject values from *ConfigMap*s or simple values to application container.

All 3 apps require to have also the *ClusterIP* objects to be deployed, therefore here is its template — **service.yaml**:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Values.app.name }}
  labels: 
    group: {{ .Values.app.group }}
spec:
  type: {{ .Values.app.service.type }}
  selector:             
    app: {{ .Values.app.name }}
  ports:
    - port: {{ .Values.app.service.port }}       
      targetPort: {{ .Values.app.container.port }}  
```

All default values in both templates are injected from **values.yaml**:

```yaml
app:
    name: app
    group: app
    replicaCount: 1
    container:
        image: add-image-here
        port: 8080
        config: []
        env:
        - key: key
          value: value
    service:
        type: ClusterIP
        port: 8080
```

And to close a task of creating app chart — we need to define some metadata in the **Chart.yaml** file:

```yaml
apiVersion: v2
name: app
description: A Helm chart for any application
type: application
version: 0.1.0
appVersion: 1.16.0
keywords:
  - app
  - java
  - javascript
  - angular
home: https://github.com/wkrzywiec/k8s-helm-helmfile/tree/master/helm
maintainers:
  - name: Wojtek Krzywiec
    url: https://github.com/wkrzywiec
```

Then, similarly to previous example, outside the app folder create YAML files with values which will override ones from *values.yaml* inside app chart.

An **adminer.yaml** file looks as follow:

```yaml
app:
  name: adminer
  group: db
  container:
    image: adminer:4.7.6-standalone
    port: 8080
    env:
      - key: ADMINER_DESIGN
        value: pepa-linha
      - key: ADMINER_DEFAULT_SERVER
        value: postgres
```

A **kanban-app.yaml** file:

```yaml
app:
  name: kanban-app
  group: backend
  container:
    image: wkrzywiec/kanban-app:k8s
    config:
      - name: postgres-config
    env: 
      - key: DB_SERVER
        value: postgres
```

A **kanban-ui.yaml** file:

```yaml
app:
  name: kanban-ui
  group: frontend
  container:
    image: wkrzywiec/kanban-ui:k8s
    port: 80
```

A resulting file structure:

![file structure](https://dev-to-uploads.s3.amazonaws.com/i/m2r3s6tzhz5mfffouajs.png)

Now, in order to create three releases for each application use commands:

```bash
> helm install -f adminer.yaml adminer ./app
NAME: adminer
LAST DEPLOYED: Mon Apr 13 16:57:17 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None

> helm install -f kanban-app.yaml kanban-app ./app
NAME: kanban-app
LAST DEPLOYED: Mon Apr 13 16:57:36 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None

> helm install -f kanban-ui.yaml kanban-ui ./app
NAME: kanban-ui
LAST DEPLOYED: Mon Apr 13 16:57:54 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None

> helm list
NAME       NAMESPACE REVISION  STATUS    CHART           APP VERSION
adminer    default   1         deployed  app-0.1.0       1.16.0     
kanban-app default   1         deployed  app-0.1.0       1.16.0     
kanban-ui  default   1         deployed  app-0.1.0       1.16.0     
postgres   default   1         deployed  postgres-0.1.0  1.16.0

> kubectl get deployments
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
adminer      1/1     1            1           112s
kanban-app   1/1     1            1           93s
kanban-ui    1/1     1            1           75s
postgres     1/1     1            1           45m

Perfect! There is one more thing to do — create a chart with *Ingress Controller* — a gateway to a cluster.

Like before, create a new chart:

```bash
> helm create ingress
Creating ingress
```

Remove all files from templates folder and clear content of *values.yaml*. This time, before moving straight away to defining a templates, let’s focus on to **Chart.yaml** first.

```yaml
apiVersion: v2
name: ingress
description: A Helm chart for Ingress Controller
type: application
version: 0.1.0
appVersion: 1.16.0
keywords:
  - ingress
  - nginx
  - api-gateway
home: https://github.com/wkrzywiec/k8s-helm-helmfile/tree/master/helm
maintainers:
  - name: Wojtek Krzywiec
    url: https://github.com/wkrzywiec
dependencies:
  - name: nginx-ingress
    version: 1.36.0
    repository: https://kubernetes-charts.storage.googleapis.com/
```

Here there is a new section — `dependencies`— which has been added. It creates default backend services which enables the *Ingress Controller* features.

But it’s not the only thing we need to do here. This section only defines on what this chart depends on, it won’t download it automatically during the installation. We need to take care of it ourselves. To do that run the command:

```bash
> helm dependency update ./ingress/
Hang tight while we grab the latest from your chart repositories...
...Successfully got an update from the "stable" chart repository
Update Complete. ⎈Happy Helming!⎈
Saving 1 charts
Downloading nginx-ingress from repo [https://kubernetes-charts.storage.googleapis.com/](https://kubernetes-charts.storage.googleapis.com/)
Deleting outdated charts
```

Inside the `ingress/charts` folder a new file will appear — `nginx-ingress-1.36.0.tgz` .

Now we can define a template for Ingress — it will be located inside `./templates` folder and will be called **ingress.yaml**:

```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: {{ .Values.ingress.name }}
  annotations:
    kubernetes.io/ingress.class: {{ .Values.ingress.annotations.class }}
spec:
  rules:
  {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
        {{- range .paths }}
          - path: {{ .path }}
            backend:
              serviceName: {{ .backend.serviceName }}
              servicePort: {{ .backend.servicePort }}
        {{- end }}
  {{- end }}
```

The most interesting part is inside specification section. There are two nested loops there which allow to define multiple hosts and multiple paths for each host.

And also, here is a default **values.yaml** file:

```yaml
ingress:
  name: ingress-service
  replicaCount: 1
  annotations: 
    class: nginx
  hosts:
    - host: chart-example.local
      paths: 
        - path: /
          backend:
            serviceName: serviceName
            servicePort: 8080
```

The resulting folder structure:

![ingress chart](https://dev-to-uploads.s3.amazonaws.com/i/sqiwsyhypd72rw0lh082.png)

Outside the `ingress` chart we can now create an *ingress.yaml* file which will hold all routing rules for our cluster.

```yaml
ingress:
  hosts:
    - host: adminer.k8s.com
      paths:
        - path: /
          backend:  
            serviceName: adminer
            servicePort: 8080
    - host: kanban.k8s.com
      paths: 
        - path: /api/
          backend:
            serviceName: kanban-app
            servicePort: 8080
        - path: /
          backend:
            serviceName: kanban-ui
            servicePort: 80
```

And now we’re able to create a Helm release:

```bash
> helm install -f ingress.yaml ingress ./ingress
NAME: ingress
LAST DEPLOYED: Tue Apr 14 07:22:44 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None

> helm list
NAME       NAMESPACE  REVISION  STATUS    CHART          APP VERSION
adminer    default    1         deployed  app-0.1.0      1.16.0     
ingress    default    1         deployed  ingress-0.1.0  1.16.0     
kanban-app default    1         deployed  app-0.1.0      1.16.0     
kanban-ui  default    1         deployed  app-0.1.0      1.16.0     
postgres   default    1         deployed  postgres-0.1.0 1.16.0

> kubectl get deployments
NAME                                    READY  UP-TO-DATE  AVAILABLE
adminer                                 1/1    1           1           
ingress-nginx-ingress-controller        1/1    1           1           
ingress-nginx-ingress-default-backend   1/1    1           1           
kanban-app                              1/1    1           1           
kanban-ui                               1/1    1           1           
postgres                                1/1    1           1           
```

Everything is set up, you can start testing it. Go to the [http://kanban.k8s.com](http://kanban.k8s.com) and you should get this page:

![kanban-ui](https://dev-to-uploads.s3.amazonaws.com/i/icmrf5t4lmmq0i0abnh7.png)

Congrats! 🍾🤘

## Conclusions

In this short entry I’ve presented how, with Helm, you can reduce of copy-pasting tasks and can bring a one single template for deploying multiple applications on a Kubernetes cluster, which might be very handy in a microservice world. I hope you’ve enjoyed it.

But there is still one thing left, which holds us from establishing a fully declarative approach for an infrastructure. In order to deploy each application we still need to run imperative commands, like helm install. But luckily there is another tool — helmfile! But this one I’ll describe in my next story.

For now, here is my GitHub repository with a source code for this project:
[**wkrzywiec/k8s-helm-helmfile** on github.com](https://github.com/wkrzywiec/k8s-helm-helmfile)

And here is a source code of Kanban project:
[**wkrzywiec/kanban-board** on github.com](https://github.com/wkrzywiec/kanban-board)

## References
* [**Docs Home** on helm.sh](https://helm.sh/docs/)
* [**HELM Best practices** on codefresh.io](https://codefresh.io/docs/docs/new-helm/helm-best-practices/)
* [**Package Kubernetes Applications with Helm** on akomljen.com](https://akomljen.com/package-kubernetes-applications-with-helm/)
* [**Drastically Improve your Kubernetes Deployments with Helm** on itnext.io](https://itnext.io/drastically-improve-your-kubernetes-deployments-with-helm-5323e7f11ef8)
* [**alexellis/helm3-expressjs-tutorial** on github.com](https://github.com/alexellis/helm3-expressjs-tutorial)

