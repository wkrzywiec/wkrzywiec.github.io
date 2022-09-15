---
title: "Automating quality checks for Kubernetes YAMLs"
date: 2021-09-02
summary: "Build CI pipline to verify Kubernetes YAMLs"
description: "If you have ever wondered how to make sure that your YAML Kubernetes objects are defined correctly and are following industry best practices, this blog post is for you. In a few paragraphs, I'll show you how to create a GitHub Actions workflow that will first analyze K8s object definitions using Datree, then deploy it on a cluster and run some tests."
tags: ["kubernetes", "helm", "cloud", "devops", "github", "github-actions", "datree", "gcp"]
canonicalUrl: "https://dev.to/wkrzywiec/automating-quality-checks-for-kubernetes-yamls-398"
---

{{< alert "link" >}}
This article was originally published on [Dev.to](https://dev.to/wkrzywiec/automating-quality-checks-for-kubernetes-yamls-398).
{{< /alert >}}

![Cover](https://images.unsplash.com/photo-1526397751294-331021109fbd?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1074&q=80)
> Cover image by [Mark Tegethoff](unsplash.com/@tegethoff) on [Unsplash](https://unsplash.com)

*If you have ever wondered how to make sure that your YAML Kubernetes objects are defined correctly and are following industry best practices, this blog post is for you. In a few paragraphs, I'll show you how to create a GitHub Actions workflow that will first analyze K8s object definitions using Datree, then deploy it on a cluster and run some tests.*

It doesn't matter if you've just started your journey with Kubernetes or you're already an expert in it; writing object definitions is not an easy task. You can very easily make a mistake that could be very costly, if deployed to a production environment. And if you're just starting to learn Kubernetes, you might need help understanding which metadata and specifications should be provided, but, by design, are not mandatory.

The ideal way to navigate these challenges would be to have an experienced colleague perform a review of your code changes. But sometimes you don't have such a person around, or it's very hard to get feedback from them. And even if you do have an amazing person to help you, it still won't prevent you from making mistakes from time to time. 

Instead, I would like to show you another approach: create a simple, automated quality check of your K8s object definitions using [Datree.io](https://www.datree.io/?utm_source=Wojtek&utm_medium=devto+article&utm_campaign=Automating+quality+check+for+Kubernetes+YAMLs&utm_id=influencer), [Google Kubernetes Engine](https://cloud.google.com/kubernetes-engine) and [Github Actions](https://github.com/features/actions).

We'll build a GitHub Actions workflow which will be triggered after each change made on the *master* branch. The workflow will have two stages:

* *Datree* analysis of missing configurations, and quality check,
* Deployment and testing an example application in a real cluster (*GKE*).

So roll up your sleeves and let's automate it!

### Workflow structure

First of all you need a GitHub repository to hold our YAML files. I'm using my old project - [k8s-helm-helmfile](https://github.com/wkrzywiec/k8s-helm-helmfile). This repository has three folders, each containing a different approach to deploy applications into Kubernetes clusters. You can read more about those approaches in my previous blog posts about [vanilla K8s](https://wkrzywiec.medium.com/deployment-of-multiple-apps-on-kubernetes-cluster-walkthrough-e05d37ed63d1), [Helm](https://wkrzywiec.medium.com/how-to-deploy-application-on-kubernetes-with-helm-39f545ad33b8) and [helmfile](https://medium.com/swlh/how-to-declaratively-run-helm-charts-using-helmfile-ac78572e6088) deployments.

To keep this blog post short, I'll show how to create a workflow that will use Helm to deploy an application, but you can easily do this with other approaches, such as those mentioned previously.

The first step is to create a workflow definition file. In the root folder of a repository create a new directory *./github/workflows* inside of which there will be a `master.yaml` file:

```yaml
name: Quality check
on:
  push:
    branches:
      - 'master'
```

It contains following specifications:

* `name` - name of our workflow
* `on` - a condition based on which a workflow will be triggered. A workflow will only be started when changes are committed on the `master` branch.

With that, you can move on to the best part - defining jobs.

### Datree analysis

In this part you will use a free tool called *Datree*, which analyzes K8s definitions and will stop the workflow if it finds any problems. It's very important to have a safety net like this, so you can feel confident that even if you make a mistake, or aren’t aware of best practices, an assistant will keep you on track. 

Before defining a GitHub workflow, let's install *Datree* locally. To do that, go to their [official website](https://www.datree.io/?utm_source=Wojtek&utm_medium=devto+article&utm_campaign=Automating+quality+check+for+Kubernetes+YAMLs&utm_id=influencer) which will guide you how to install the *Datree* CLI. I'm using Linux (or to be precise, WSL), so only the following command is necessary:

```bash
> curl https://get.datree.io | /bin/bash
```

After couple of seconds Datree will be installed. 

To test it out, go to the folder where Kubernetes YAML files are located and run *Datree* test command (in my case I'm using a vanilla K8s file from [k8s-helm-helmfile project](https://github.com/wkrzywiec/k8s-helm-helmfile)):

```bash
> datree test adminer-deployment.yaml
```

where the `adminer-deployment.yaml` file is a Kubernetes object definition. 

Here is the output that I got:

![datree-test](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/6m5xi01xgh0e0ksmnqx9.png)

As you can see, *Datree* has prepared a short summary of how many rules this YAML file violates. It provides a very useful explanation with a hint on how to fix them.

Starting from here, you can work on each issue to make these tests pass. It's a great way to learn and practise. But what if you deliberately chose not to comply with some of the rules? Luckily, *Datree* gives a possibility to prepare a custom policy, a set of rules against which YAML files will be checked.

To set up a policy, you need to go to your dashboard. Your personal link to it is located at the end of each scan, in the summary table, in the last row called `See all rules in policy` (I've marked it in a previous screenshot). It will take you to a login page.

![login-page](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/xelxmef6icptu225cgx3.PNG)

Then you need to login. For convenience, I would suggest using the GitHub account. After successful authorization you will reach a *Policies* page.

![datree-policies](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/7qbfyn3ahvue92qo1a5d.PNG)

Here you can inspect all the rules that you can turn on and off. By default, only some of them are enabled. To activate or deactivate them, use the toggle button visible next to the rule name.

If a name of a rule is too enigmatic, you can check its details by clicking on its name. It will then show more information and a sample output when this rule is violated. 

![datree-rule](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/89zc7kpto2byjjso0thd.PNG)

Another cool feature is that you can define your own tips on how to fix a problem. The defaults should be enough, but if you prefer to extend it, view it in your own language, or add a link to a blog post, Stack Overflow discussion or any other online material, you can put it here by simply clicking an *Edit* button.

Finally, you can create your own set of rules, known as policies, to run for different applications, environments and stages. Simply click the *Create Policy* button at the top of the page.

Let's now check the second page, available on the left panel, called *History*. As the name might suggest, here you can see a convenient summary of all previous test runs. 

![datree-history](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/69nkkly5k1ff1q6abs3d.PNG)

Before writing this post, I’d already played around with *Datree*, which is why I already have several test runs listed in the history panel, but in your case you should have only one.

That would be it for a quick tour around *Datree* dashboard! 

Now let's build a GitHub Actions workflow. 

First, provide your *Datree* token as an environment variable in a workflow. To achieve this, click on your avatar in the top right corner of the *Datree* dashboard, then click **Settings**. It'll guide you to the page where you can find your token.

![datree-token](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/p2p6f2ahpdtd3bwww5lw.png)

Once you’ve copied the token, go to your GitHub project/repository’s **Settings** page. Then select **Secrets** and click the **New repository secret** button. 

In the **Name** field put `DATREE_TOKEN` and in the **Value** field a token copied from *Datree*.

![github-secret](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/drd2msj27pjevkwqe0vs.PNG)

Now you can move on to the workflow's definition file and define the first job:

```yaml
jobs:
  datree:
    name: Validate Helm charts
    runs-on: ubuntu-latest
    container:
      image: dtzar/helm-kubectl:3.6.3
```

It's called `datree`, it runs on the latest Ubuntu inside a [dtzar/helm-kubectl](https://hub.docker.com/r/dtzar/helm-kubectl/) Docker container. I've selected this setup because I would like to run tests against Helm release (and not vanilla K8s as it was done previously). The reason to choose this Docker image is because it contains necessary dependencies (K8s and Helm), so I can skip their installation and make my workflow faster.

Let’s define the next three steps:

```yaml
    steps:
      - name: Checkout 🛎️
        uses: actions/checkout@v2

      - name: Install Datree 🔨
        run: |
          helm plugin install https://github.com/datreeio/helm-datree
      
      - name: Datree test 🔥
        env:
          DATREE_TOKEN: ${{ secrets.DATREE_TOKEN }}
        run: |
          helm datree test ./helm/app -- --values ./helm/adminer.yaml
```

With the first one, `actions/checkout@v2`, you get code from the repository. In step two, you instal the [Datree Helm plugin](https://hub.datree.io/helm-plugin?utm_source=Wojtek&utm_medium=devto+article&utm_campaign=Automating+quality+checks+for+Kubernetes+YAMLs&utm_id=influencer) to run *Datree* tests using Helm. In the third step, you run actual tests using a Helm CLI. The `DATREE_TOKEN` environment variable is added to it so the result will be linked with a *Datree* account. 

Finally, in an actual run script, I provide the location of a Helm template and the location of testing `values.yaml` file.

After that you can commit changes and push it to GitHub. It should trigger a workflow, which will be available in the **Actions** tab.  

![github-datree-fail](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/p7xh2v531ulost9ky22r.PNG)

In my case, several tests are failing, demonstrated by the failing status of a workflow. To find out more, click on the failing job. It will take you to the console output, where you can investigate what went wrong.

![github-datree-fail-details](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/3xe3r20z44t3os1cr3po.PNG)

As well as checking policy check result(s) in the workflow's console, you can go back to [the History page](https://app.datree.io/cli/invocations) in the *Datree* dashboard and analyze errors there.

![datree-fail](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/p0a2rrs2m1cba0ta6jy2.PNG)

If you have a similar screen to mine, stop here, correct mistakes and push changes to GitHub. If you feel that some rules are obsolete for you, turn them off in the *Datree* dashboard, but do not turn off too many!

After fixing all the issues and re-running the workflow, the previously marked red exes [X] will become green check marks [V], indicating that the workflow has passed the validation and policy check.

![github-datree-success](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/0ffa7tcuzol6r1l6v2og.PNG)

And some details about a job:

![github-datree-success-details](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/ib5lwgs6flr3wczw41b4.PNG)

The successful result will be also visible in the *Datree* dashboard:

![datree-success](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/4h8ge9rhf8lv79exyiuo.PNG)

Awesome! We can now move on to the next part.

### Testing on GKE

After making sure that templates are okay from *Datree*’s point of view, move to deploying them to a real Kubernetes cluster (which is not production) and then check if everything is working there, e.g. if a website is available over the internet, etc.

First step would be to have a cluster. I've picked *Google Kubernetes Engine* (*GKE*) because of its [free tier](https://cloud.google.com/free/docs/gcp-free-tier/#kubernetes-engine), but if you have your own cluster (on AWS or any other cloud provider) just use it.

Right now I'll follow with steps that are necessary to set up a job for *GKE*, so if you already have a *GKE* or any other Kubernetes cluster up and running, skip this part.

Before adding a new job to a workflow, you need to set up couple of things in *GKE* (these instructions are based on official [GKE Quickstart guide](https://cloud.google.com/kubernetes-engine/docs/quickstart)):

* Create a Google Cloud account. [You can start from the main page](https://cloud.google.com),
* Create or select an already existing Google Cloud project. It can be done either from [Google Cloud console](https://console.cloud.google.com/home/) or [from Google project selector](https://console.cloud.google.com/projectselector2/home/dashboard).
* Enable billing for a project. You will need to provide your credit card information, [like it's described here](https://cloud.google.com/billing/docs/how-to/modify-project), but don't worry, you won't be charged anything. This step is just to verify that you're a human.
* Enable *GKE* APIs, which [can be done on this page](https://console.cloud.google.com/flows/enableapi?apiid=artifactregistry.googleapis.com,container.googleapis.com).

Until now, all configuration was carried out in a web browser, but now you need to move to either [Google Cloud Shell](https://cloud.google.com/shell), or [install Cloud SDK](https://cloud.google.com/sdk/docs/install) and follow the instructions in a terminal:

Set up basic configuration in `gcloud` tool, like default project, region and zone. In my case, the project name is `k8s-helm-helmfile` and the region is `europe-central2`, but for you it may be different.

```bash
> gcloud config set project k8s-helm-helmfile

> gcloud config set compute/region europe-central2

> gcloud config set compute/zone europe-central2-a
```

Create an [IAM Service Account](https://cloud.google.com/iam/docs/service-accounts), which is an account which will be used in GitHub Action workflow. I've called mine `helm-github-actions-service`:

```bash
> gcloud iam service-accounts create helm-github-actions-service
```

Get an email from the newly created Service Account. You will need it for the next step:

```bash
> gcloud iam service-accounts list
```

Assign roles to a Service Account, where `<EMAIL>` tag is taken from previous step:

```bash
> gcloud projects add-iam-policy-binding k8s-helm-helmfile \
  --member=serviceAccount:<EMAIL> \
  --role=roles/container.admin \
  --role=roles/storage.admin \
  --role=roles/container.clusterAdmin \
  --role=roles/iam.serviceAccountUser \
  --role=roles/container.developer
```

Export the Service Account Key:

```bash
> gcloud iam service-accounts keys create key.json --iam-account=<EMAIL>

> export GKE_SA_KEY=$(cat key.json | base64)
```

Add it as a GitHub Secret to a project (the same way as for `DATREE_TOKEN`) with `GKE_SA_KEY` as key. To see the value of the exported key you can use the command:

 ```bash
> printenv GKE_SA_KEY
 ```

Everything is set up, now go back to workflow definition where you first created a Kubernetes cluster on *GKE*, deploy a sample Helm release, and test it. 

First create a new job called `gke` :

```yaml
gke:
    name: Test Helm chart on GKE 
    needs: datree
    runs-on: ubuntu-latest
    env:
      PROJECT_ID: k8s-helm-helmfile
      GKE_CLUSTER: helm-test
      GKE_REGION: europe-central2
```

Similarly to the previous example, you have `name` and `runs-on` configurations. There is also a `needs` configuration, which means that in order to run this job, the `datree` job needs to first be completed successfully. This prevents spinning up clusters and deploying a sample application if something goes wrong during a *Datree* check. The last part of job configuration are environment variables (`env`), which will be used in workflow steps. They're my GCP project id, K8s cluster name, and my *GKE* region.

Moving on to the next steps:

```yaml
steps:
  - name: Checkout 🛎️
    uses: actions/checkout@v2

  - name: Setup gcloud CLI ⚡
    uses: google-github-actions/setup-gcloud@master
    with:
      service_account_key: ${{ secrets.GKE_SA_KEY }}
      project_id: ${{ env.PROJECT_ID }}
```

The first one is for getting code from the project.
The second is to configure (login and set up project) Google Cloud CLI which will be used in following steps.

```yaml
- name: Create Autopilot GKE cluster 🔨
  run: |
    gcloud container clusters create-auto ${{ env.GKE_CLUSTER }} \
    --project=${{ env.PROJECT_ID }} \
    --region=${{ env.GKE_REGION }}

  - name: Config kubectl for GKE cluster ⚡
    uses: google-github-actions/get-gke-credentials@main
    with:
      cluster_name: ${{ env.GKE_CLUSTER }}
      location: ${{ env.GKE_REGION }}
      credentials: ${{ secrets.GKE_SA_KEY }}
```

The above steps create a new GKE cluster and configure kubectl so it's connected with the newly created cluster. With that, you can move on to the step where an adminer Helm release will be installed:

```yaml
- name: Deploy test Helm release 🚀
  uses: deliverybot/helm@v1
  with:
    release: adminer
    namespace: default
    chart: ./helm/app
    helm: helm3
    value-files: ./helm/adminer.yaml
    values: |
        app:
          service:
            type: LoadBalancer
```

Stop here and analyze what's going on. First of all, you’re using the [deliverybot/helm](https://github.com/deliverybot/helm) GitHub Actions, which provides a convenient way to use Helm. By adding a few parameters, you can deploy an application onto a Kubernetes cluster. The entire list of available parameters can be found on [the official website](https://github.com/deliverybot/helm). 

In the above example, I've used the following steps alone:

* `release` - a release name,
* `namespace` - specifies the K8s namespace where the app will be installed,
* `chart` - gives information about the location of a Helm chart,
* `helm` - indicates which version of Helm will be used,
* `value-files` - file used to override the default values from a Helm chart, in my case it's an Adminer's values.yaml file (the Helm chart I use for testing, which deploys popular database client - [Adminer](https://www.adminer.org)),
* `values` - this parameter works pretty the same as previous one - it's used to override the default values from a Helm chart, but instead of doing it with a file, we can directly specify values that need to be overridden; here, I'm overriding only the Service kind, as by default it's a `ClusterIP`, but I don't want to change it in the adminer.yaml file.

After successful installation, our workflow can proceed with tests. I've decided to run a very simple test, which only checks if a page is opening, but you can of course build a more sophisticated test chain.

```yaml
- name: Test installed application 🔥
  run: |
export IP_ADDRESS=$(kubectl get services -o=jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')
    echo "$IP_ADDRESS"
    curl http://"$IP_ADDRESS":8080
```

The first line in a testing script is for finding out under which IP address the adminer application is exposed. The second is for debugging, and the last for actual testing.

Once the tests are done, you need to destroy a cluster:

```yaml
- name: Delete cluster GKE Cluster 💥
  if: ${{ always() }}
  run: |
    gcloud container clusters delete ${{ env.GKE_CLUSTER }} --zone=${{ env.GKE_REGION }} --quiet
```

The `if: ${{ always() }}` part is very important here. It makes sure that even if any of the previous steps fail, this one will always run. Otherwise you could end up with a bill from Google at the end of a month.

After commiting changes and pushing them to GitHub, a workflow will look like this:

![github-full](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/184zx9c54jvoa2daaayz.PNG)

First a *Datree* step is executed, then the installation is done on *GKE*. To check the details of the second step, click on its name. 

![github-gke-success-details](https://dev-to-uploads.s3.amazonaws.com/uploads/articles/yu83t5ktcwkk2j7oamqd.PNG)

### Conclusion

And that's it for today! I hope that this blog post encourages you to build something like this on your own, give *Datree* (or any other static code analysis tool) a try, and set up a cluster for automated tests, so you will feel more confident about the changes you made in your code base. It can all be set up and operational in a flash.