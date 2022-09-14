---
title: "GitHub Actions and Firebase Test Lab"
date: 2019-11-24
summary: "Automate running instrumentation test on Firebase Test Lab with GitHub Actions"
description: "In this blog post I am going to show you how to create a GitHub Actions CI/CD workflow that will run Android instrumentation tests on Firebase Test Lab."
tags: ["java", "android", "github-action", "devops", "ci-cd", "github", "firebase"]
canonicalUrl: "https://medium.com/firebase-developers/github-actions-firebase-test-lab-4bc830685a99"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://medium.com/firebase-developers/github-actions-firebase-test-lab-4bc830685a99).
{{< /alert >}}


![Photo by [chuttersnap](https://unsplash.com/@chuttersnap?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/11484/0*BIKfr03R8rw6WmRU)*Photo by [chuttersnap](https://unsplash.com/@chuttersnap?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

## GitHub Actions: Firebase Test Lab

*In this blog post I am going to show you how to create a GitHub Actions CI/CD workflow that will run Android instrumentation tests on [Firebase Test Lab](https://firebase.google.com/products/test-lab/).*


I assume you’ve got a basic understanding of [GitHub Actions](https://github.com/features/actions), but don’t worry if you don’t — you will be able to follow along easily. If you’d like to learn more about GitHub Actions, check out my article “[GitHub Actions for Android: First Approach](https://medium.com/@wkrzywiec/github-actions-for-android-first-approach-f616c24aa0f9)”.

In Android application development world people usually list [three levels of testing](https://developer.android.com/training/testing/fundamentals#write-tests): *unit tests*, *integration tests* and *UI tests*. Each one with an increasing number of tested components and increasing time of execution.

Today I want to tackle the last type — UI tests, also know as end-to-end (E2E) tests. Like I mention above, they’re pretty heavy-weight, and their execution can take up a lot of time. But they’re very important to validate if the application is working correctly. The reason for that is that they should be run on a real device (mobile phone), emulator or on cloud-based service, such as [Firebase Test Lab](https://firebase.google.com/products/test-lab/).
> So, what will we cover in this article?

We will look at the steps to set up a CI/CD workflow based on GitHub Actions and Firebase Test Lab:

* First, we’ll create a new Firebase project

* Then, we will set up GitHub Actions and connect them with our Firebase project

* Finally, we will run our UI tests and make sure everything works fine

### Create a Firebase project

To create a Firebase project, you first need a Google account. If you don’t have one, [you can sign up here](https://accounts.google.com/signup/v2/webcreateaccount), and then go to the Firebase website and click the **Create a project** button.

![](https://cdn-images-1.medium.com/max/2164/1*spIZeghA4qhhZjD0Rex8bw.png)

On the next page provide your project name. I’m creating one for [WaWa Tabor](https://github.com/wkrzywiec/WaWa-Tabor), my Android application.

![](https://cdn-images-1.medium.com/max/2604/1*xtG1EfnDeftoXsBwB1ysgg.png)

Then you’ll be asked if you want to enable Google Analytics for your project. I don’t need it for my project, but if you want you can keep it enabled (it’s free of charge).

![](https://cdn-images-1.medium.com/max/2604/1*gO2bW0wP8r_Lbs37IHTIgg.png)

After clicking the **Create project,** your project will be created and a couple seconds later it will be ready. And that’s everything we need from Firebase for the moment.

![](https://cdn-images-1.medium.com/max/2604/1*z15dh9sOTUWhlIP7lg-ThA.png)

### Create GitHub Actions release workflow

First, let’s look at what we want to achieve.

In my project I have a convention that whenever I want to release my application to the Google Play store I create a new separate branch which starts with release in its name.

So when I do that I want to run a custom CI/CD workflow that will check the quality of release application by running unit and UI tests. Both of them are located inside my project, the former in the [app/src/main/test](https://github.com/wkrzywiec/WaWa-Tabor/tree/master/app/src/test/java/com/wawa_applications/wawa_tabor/viewmodel) directory and the latter in [app/src/main/androidTest](https://github.com/wkrzywiec/WaWa-Tabor/tree/master/app/src/androidTest/java/com/wojciechkrzywiec/wawa_tabor).

We can run unit tests by using a simple Gradle command. But in the case of UI tests, an additional step is required before we can actually run the tests. In this step, we’ll be creating two additional APKs for the application and the tests themselves.

See the following picture for how this looks like. Because unit and UI tests are independent I decided to run them in parallel.

![](https://cdn-images-1.medium.com/max/2000/1*YQ7T4gGisawcNi30dR9c7A.png)

Now we can move to the code. As mentioned before, I will be using my [WaWa Tabor](https://github.com/wkrzywiec/WaWa-Tabor) for demonstration purposes. I’ve tried to keep my workflow as generic as possible be so you should be able to follow all the steps with your own project.

In order to add a new workflow we need to create a YAML file inside .github/workflows (this folder should be located in the root directory of your project). You can name it as you like, in my case it’s android-release.yml.

```yaml
name: Android Release

on:
  push:
    branches:
      - 'release*'

jobs:

  test:
    name: Unit Tests
    runs-on: ubuntu-18.04

    steps:
      - uses: actions/checkout@v1
      - name: Set up JDK 1.8
        uses: actions/setup-java@v1
        with:
          java-version: 1.8
      - name: Run Unit tests
        run: bash ./gradlew test --stacktrace

  sonar:
    name: SonarCloud Scan
    runs-on: ubuntu-18.04

    steps:
      - uses: actions/checkout@v1
      - name: SonarCloud Scan
        run: bash ./gradlew jacocoUnitTestReport sonarqube -Dsonar.login=${{ secrets.SONAR_TOKEN }} --stacktrace
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - name: Link to SonarCloud Report
        run: echo "https://sonarcloud.io/dashboard?id=wkrzywiec_WaWa-Tabor"

  apk:
    name: Generate APK
    runs-on: ubuntu-18.04

    steps:
      - uses: actions/checkout@v1
      - name: Set up JDK 1.8
        uses: actions/setup-java@v1
        with:
          java-version: 1.8

      - name: Assemble app debug APK
        run: bash ./gradlew assembleDebug --stacktrace
        env:
          ZTM_API_KEY: ${{ secrets.ZTM_API_KEY }}
      - name: Upload app APK
        uses: actions/upload-artifact@v1
        with:
          name: app-debug
          path: app/build/outputs/apk/debug/app-debug.apk

      - name: Assemble Android Instrumentation Tests
        run: bash ./gradlew assembleDebugAndroidTest
        env:
          ZTM_API_KEY: ${{ secrets.ZTM_API_KEY }}
      - name: Upload Android Test APK
        uses: actions/upload-artifact@v1
        with:
          name: app-debug-androidTest
          path: app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk


  firebase:
    name: Run UI tests with Firebase Test Lab
    needs: apk
    runs-on: ubuntu-18.04

    steps:
      - uses: actions/checkout@v1

      - name: Download app APK
        uses: actions/download-artifact@v1
        with:
          name: app-debug

      - name: Download Android test APK
        uses: actions/download-artifact@v1
        with:
          name: app-debug-androidTest

      - name: Login to Google Cloud
        uses: GoogleCloudPlatform/github-actions/setup-gcloud@master
        with:
          version: '270.0.0'
          service_account_key: ${{ secrets.GCLOUD_AUTH }}

      - name: Set current project
        run: gcloud config set project ${{ secrets.FIREBASE_PROJECT_ID }}

      - name: Run Instrumentation Tests in Firebase Test Lab
        run: gcloud firebase test android run --type instrumentation --app app-debug/app-debug.apk --test app-debug-androidTest/app-debug-androidTest.apk --device model=Pixel2,version=28,locale=pl,orientation=portrait
```
> Ok, ok, but what does it all mean?

Don’t worry I’m just to explain what everything means.

### Step 0. Definition of the workflow
```yaml
    name: Android Release

    on: 
      push:
        branches:
          - 'release*'
```
First, we need to provide the name of the workflow, which in my case is Android Release.

Next we specify on what git action this workflow will be triggered. In my case it‘s whenever code is pushed (committed) on any branch starting with release. So for instance, it will be triggered for all commits on the release-9 *branch*.

### Step 1. Unit test job
```yaml
    jobs:
      test:
        name: Unit Tests
        runs-on: ubuntu-18.04

        steps:
          - uses: actions/checkout@v1
          - name: Set up JDK 1.8
            uses: actions/setup-java@v1
            with:
              java-version: 1.8
          - name: Run Unit tests
            run: bash ./gradlew test --stacktrace
```
After defining basic meta data of the workflow we can move on to the jobs section.

The first one has the ID test and name Unit Tests and its purpose is to run the unit tests of this project. If you want to know more about this step, check out my previous blog post around this topic: [GitHub Actions for Android: First Approach](https://medium.com/@wkrzywiec/github-actions-for-android-first-approach-f616c24aa0f9), where cover this topic in more detail.

### Step 2. Generate APK job
```yaml
    apk:
      name: Generate APK
      runs-on: ubuntu-18.04

      steps:
        - uses: actions/checkout@v1
        - name: Set up JDK 1.8
          uses: actions/setup-java@v1
          with:
            java-version: 1.8
    

        - name: Assemble app debug APK
          run: bash ./gradlew assembleDebug --stacktrace
          env:
            ZTM_API_KEY: ${{ secrets.ZTM_API_KEY }}

        - name: Upload app APK
          uses: actions/upload-artifact@v1
          with:
            name: app-debug
            path: app/build/outputs/apk/debug/app-debug.apk
    

        - name: Assemble Android Instrumentation Tests
          run: bash ./gradlew assembleDebugAndroidTest
          env:
            ZTM_API_KEY: ${{ secrets.ZTM_API_KEY }}

        - name: Upload Android Test APK
          uses: actions/upload-artifact@v1
          with:
            name: app-debug-androidTest
            path: app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
```
This job is more complex, but what it does is generate two APK (Android Package) files:

* one of them contains the compiled and packaged Android app, so it can be installed on a mobile device,

* the other one contains the compiled instrumentation tests

Just like before, the first step in the job is to set the Java version to 8.

The following two steps are called Assemble app debug APK and Upload app APK. In the first one, we assemble (create) the application APK file using the Gradle Wrapper command ./gradlew assembleDebug .

In order to properly assemble my application I need to provide an API key (for a REST API service that app is using) in the system variable ZTM_API_KEY. Therefore, there is an additional declaration in env section:

* ZTM_API_KEY: ${{ secrets.ZTM_API_KEY }} — this means the workflow job variable ZTM_API_KEY should get its value from GitHub’s secret vault.
> But how I can add this secret?

Don’t worry, it’s not so hard. In the GitHub project go to **Settings** and then **Secrets.** Next, click on **Add a new secret** and provide its name (ZTM_API_KEY in my case) and value (I won’t show it to you 😉).

![](https://cdn-images-1.medium.com/max/2602/1*rVDb7Qtjyfd6vLg1OYU6rw.png)

And with this, the workflow should be able to assemble an application APK.

Next, we need to make the generated APK available to the proceeding workflow job (the one which will run it on Firebase Test Lab).

For that I’m using an existing GitHub Action — [actions/upload-artifact](https://github.com/actions/upload-artifact). It was developed by some contributors of GitHub community and it’s a very nice feature of this new CI/CD tool. Instead of re-inventing the wheel or building scripts on our own we can use some of actions available on [GitHub Marketplace](https://github.com/marketplace?type=actions).

The actions/upload-artifact action defines two arguments that we need to provide in thewith section:

* name — defines the name of the artifact (we can set it up as we want),

* path — defines the path inside the runner machine where the artifact is located.

Following there are two similar steps covering assembling the Android tests into an APK file and uploading it from the workflow as an artifact so they will be available in the next job.

They’re pretty much the same, the only difference being the Gradle Wrapper command that we’re using:

    ./gradlew assembleDebugAndroidTest

In the last step, we’re uploading the assembled test artifact.

### Step 3. Run tests on Firebase Test Lab job

And finally we are able to run our tests on the [Firebase Test Lab](https://firebase.google.com/products/test-lab/) service.
```yaml
    firebase:
      name: Run UI tests with Firebase Test Lab
      needs: apk
      runs-on: ubuntu-18.04
      steps:
        - uses: actions/checkout@v1

        - name: Download app APK
          uses: actions/download-artifact@v1
          with:
            name: app-debug

        - name: Download Android test APK
          uses: actions/download-artifact@v1
          with:
            name: app-debug-androidTest

        - name: Login to Google Cloud
          uses: GoogleCloudPlatform/github-actions/setup-gcloud@master
          with: 
            version: `270.0.0` 
            service_account_key: ${{ secrets.GCLOUD_AUTH }}

        - name: Set current project
          run: gcloud config set project ${{ secrets.FIREBASE_PROJECT_ID }}

        - name: Run Instrumentation Tests in Firebase Test Lab
          run: gcloud firebase test android run --type instrumentation --app app-debug/app-debug.apk --test app-debug-androidTest/app-debug-androidTest.apk --device model=Pixel2,version=28,locale=pl,orientation=portrait
```
Before moving on to explain all the steps in this script, you may notice that in the job definition section, apart from the name and runs-on fields there is a new one - needs: apk. It tells the GitHub Actions runner that it can be started only when apk job (that assembles APK files) has finished.

Moving on to the steps, first we need to download all the artifacts we generated in the previous step. To do so, we’ll be using actions/download-artifact@v1 .

Next we need to connect to Firebase, which — as you may already know — is part of the Google Cloud ecosystem. The [Cloud SDK](https://cloud.google.com/sdk/) provides a commandline utility to interact with Google Cloud and its services. One of them is to [run tests on Firebase Test Lab](https://cloud.google.com/sdk/gcloud/reference/firebase/test/android/run).

But before we will be able to use it we need to make sure we meet some prerequisites.

First we need to install the *Cloud SDK* on the machine running the tests. Lucky for us there is no need to do that, thanks to a GitHub Action just for that — [GoogleCloudPlatform/github-actions/setup-gcloud](https://github.com/GoogleCloudPlatform/github-actions/tree/master/setup-gcloud).

This Action covers also login into Google Cloud and requires your special key.
```yaml
    - name: Login to Google Cloud
      uses: GoogleCloudPlatform/github-actions/setup-gcloud@master
      with:
       version: `270.0.0` 
       service_account_key: ${{ secrets.GCLOUD_AUTH }}
```
> Ok, but how to get such key?

So first, go back to the main page of your project on Firebase website, and select **Project settings**.

![](https://cdn-images-1.medium.com/max/2000/1*wvDz--2miL8yQikpjg81EA.png)

Then, click on **Service accounts** and then on **Manage service account permissions**.

![](https://cdn-images-1.medium.com/max/2084/1*w0ENOkGbeA_YFmesSwhFBg.png)

On the next page there should be a table with two service accounts. Pick the one titled *Firebase Admin SDK Service Agent,* click the **Actions** dots from the last column and **Create key** from the menu.

![](https://cdn-images-1.medium.com/max/2000/1*jd4udsphehx_HP7YIFKS1w.png)

A new dialog will show up — select the **key type** as **JSON**. After clicking **OK** a JSON file will be downloaded.

We cannot use this file straightaway — instead, we first need to encode it using Base64. If you’re Linux user, you can use following method in a terminal:

```bash
 base64 google-cloud-key.json > encoded-key.txt
```

Or you can use the website: [https://www.base64encode.org/](https://www.base64encode.org/).

As a result you should get something like this:

    WkdhNU1cbmF6d1ZlSjFrMUpocHVjT2xLUzJ2UHozNXc1U0pENU4zcG5aZ0xLcjRWQmNSSnZNVFIxWU5VdFI0SlhGU1lBNGhcbkJvY24wQTUzdVpWeGl5WHBUSmJ2NFhqVi9SMUlTOGRhL3NJM1ArQ3l3UUtCZ1FEKzJobGZXRXFmZVhVZDdEUDZcbkxERUdQeno5NTdpY29EelV5MnV1cXpBRkRLZHF1b3VscTJ6cjAr...

Once you have this, you can add it to your GitHub’s Secrets vault the same way as before.

Ok, we’re done with the authentication, let’s proceed with setting up the project on which we will work on.

For that we’ll be using the [gcloud CLI](https://cloud.google.com/sdk/gcloud/).

    - name: Set current project
      run: gcloud config set project ${{ secrets.FIREBASE_PROJECT_ID }}

To set the current project, we’ll use the gcloud config set project {project_id} action ([docs](https://cloud.google.com/sdk/gcloud/reference/config/set)). The project ID can be found on the Firebase website on the main page of the **Project Settings**.

And finally, we can run the tests:
```yaml
    - name: Run Instrumentation Tests in Firebase Test Lab
      run: gcloud firebase test android run --type instrumentation --app app-debug/app-debug.apk --test app-debug-androidTest/app-debug-androidTest.apk --device model=Pixel2,version=28,locale=pl,orientation=portrait
```
Like before, we’re using a standard Cloud SDK command — gcloud firebase test android run ([docs](https://cloud.google.com/sdk/gcloud/reference/firebase/test/android/run)). But this time, we’re providing some additional parameters:

* --type instrumentation — indicates the type of tests to be run, in our case the UI tests,

* --app app-debug/app-debug.apk — tells the tool where to find the application’s debug APK,

* --test app-debug-androidTest/app-debug-androidTest.apk — where to find the test APK,

* --device model=Pixel12,version=28,locale=pl,orientation=portrait — specifies on which mobile device the tests should be run, which Android version should be installed, what system language should be set up and which orientation the mobile device should be in. To get the full list of all available variants, you can rungcloud firebase test android models list .

And we’re done! Let’s now test the workflow.

To do that just create a new branch, making sure that it’s name starts with release,and a couple of minutes later, your tests should finish running successfully.

![](https://cdn-images-1.medium.com/max/2000/1*ACBqN8q2uHvwJYfClBQP3w.png)

Now if you go to the **Test Lab** page on your Firebase project, you should be able to see the full test report:

![](https://cdn-images-1.medium.com/max/2598/1*KZu1TP3gPXMycXpdqk8iXQ.png)
> Note: If for some reasons your workflow is not able to run the gcloud firebase test run command due to a 403 error response make sure that the Google Cloud service account that you’ve created matches all requirements listed in the official documentation:
[**Using Firebase Test Lab with Continuous Integration Systems | Firebase** | firebase.google.com](https://firebase.google.com/docs/test-lab/android/continuous#requirements)

## Conclusion

As you’ve seen in this article, setting up a CI/CD pipeline for your Android app is pretty straightforward using GitHub Actions and Firebase Test Lab.

I’ve been using this for the past couple of weeks, and have been very happy with the experience. Using a CI workflow has increased my confidence in my code base, and has helped me catch more bugs than before.

If you’re interested in the source code of my application and GitHub Action workflows, check out my repository:

[**wkrzywiec/WaWa-Tabor** | github.com](https://github.com/wkrzywiec/WaWa-Tabor)

***26.01.2020 Update**. Depreciated GitHub Actions actions/gcloud were replaced by new one — GoogleCloudPlatform/github-actions.*

## References

* [**Get started with Firebase Test Lab from the gcloud Command Line** | firebase.google.com](https://firebase.google.com/docs/test-lab/android/command-line)
* [**gcloud firebase test android run | Cloud SDK | Google Cloud** | cloud.google.com](https://cloud.google.com/sdk/gcloud/reference/firebase/test/android/run)
* [**GoogleCloudPlatform/github-actions** | github.com](https://github.com/GoogleCloudPlatform/github-actions)
* [**Using Firebase Test Lab with Continuous Integration Systems | Firebase** | firebase.google.com](https://firebase.google.com/docs/test-lab/android/continuous)
