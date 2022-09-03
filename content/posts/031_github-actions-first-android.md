
# GitHub Actions for Android: First Approach
> Source: https://wkrzywiec.medium.com/github-actions-for-android-first-approach-f616c24aa0f9

In this blog post I would like to show you a simple set up for my Android project of GitHub Actions — new feature of well-known host of Git repositories — which can help you automate test execution and build your application.

![Photo by [Ant Rozetsky](https://unsplash.com/@rozetsky?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/11168/0*72pUuXCLIR1JFwPI)*Photo by [Ant Rozetsky](https://unsplash.com/@rozetsky?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

### The problem

Before jumping to the GitHub Actions let me first explain what problem does it solves.

You’ve may heard of **CI/CD**, which stands for *Continuous Integration* and *Continuous Delivery. *Both relates to broader topic which is ***DevOps** — a** ***set of practices that’s main goal is to create and release software in smaller peaces, faster and more reliably. The key concepts of it are based on [Lean Manufacturing](https://en.wikipedia.org/wiki/Lean_manufacturing), firstly introduced in the Japanese manufacturing industry. If you want more about the *DevOps* I recommend you to read [*The Project Phoenix](https://www.amazon.com/Phoenix-Project-DevOps-Helping-Business/dp/0988262592)* and [*The DevOps Handbook](https://www.amazon.com/DevOps-Handbook-World-Class-Reliability-Organizations/dp/1942788002)*, or find more information on the Internet.

As I mentioned, one of the fundamental goals of *DevOp*s is to make release of the software fast. And such can be reached by automating its building process. To achieve it *CI/CD* practice can be introduced which covers frequently commits to the main application branch, testing it and then releasing it. Some companies, [like *Facebook](https://engineering.fb.com/web/rapid-release-at-massive-scale/)*, with this approach has reached hundreds of releases on production environment per day!

Nowadays there are several tools that can help us, developers, automate all this stuff. One of the most popular are [*Jenkins](https://jenkins.io/)*, [*GitLab](https://about.gitlab.com/)*, [*Travis CI](https://travis-ci.org/)*, [*CircleCI](https://circleci.com/)* or [*TeamCity](https://www.jetbrains.com/teamcity/)*. And lately a new-old player has joined the market - ***GitHub*** with its ***GitHub Actions***.

### GitHub Actions
> - So what the GitHub Actions really is?

I like to think about it as an assembly line in a factory. For instance, in the Ford automobile factory there was a moving **assembly line** on which there was a car which goes thru **several workstations** in each different parts were added to the car.

<iframe src="https://medium.com/media/88836c8d87aaa5cae206062273cc64aa" frameborder=0></iframe>

In our case the car is a software application and the assembly line is the *CI/CD* tool. With *GitHub Actions* we can define workflow(s) how our application can be build, tested and then deployed (e.g. on *AWS*, *GCP*, etc.).

When I’m writing this post *GitHub Actions* is in the limited public beta phase, which means that for now it’s not recommended to use it for crucial business purposes. But I think it’s starting to have its momentum and is worth to learn, especially because it’s so easy!

Please keep in mind that it’s still beta version, so some of the solutions and pricing (now it’s free with some limitations) might be different at the time you’re reading this.
> - So finally, the last question before moving to the example. How to get it?

For now you need to sign up to be a beta tester. It’s free (with some limitations) but still you might wait couple of days for the approval (as it was in my case) and it can be done here: [https://github.com/features/actions](https://github.com/features/actions).

***Feature* & *master* branch workflows**

In order to explain to you what I would like to achieve first I need to make sure that you understand the common [Git Feature Branch Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow). The main idea behind it is to have one main git branch, usually the *master.* All new features and bug fixes must be done on a separate branches and then, using *pull requests,* could be merged into the *master* branch (after code review by other developers).

Such approach is one of the common practice in the business for development teams.

![](https://cdn-images-1.medium.com/max/2000/1*oe58qC1cN87Ak-Y18OT4XA.png)

Now, *GitHub Actions* introduces **workflows** that can have multiple **jobs** and such workflows can be triggered by an **event **(commit, pull request, etc.) or can be scheduled.

What I try to achieve is to have two types of such *workflows* which will be triggered depending on which git branch the new code is committed. First for *master* branch and when creating a pull requests, second for all other branches (features and bug fixes).

*Note: All examples that are following next are taken from my [GitHub project](https://github.com/wkrzywiec/WaWa-Tabor/tree/210f49c608fd764021837fe339720438aa37aad7).*

### Android Feature Branch CI

In order to enable workflows in your GitHub repository first you need to sign up for it, as I mentioned before, than you need to add .github/workflows folder into the root of your repository.

You can add there multiple YAML files which will hold definitions of all workflows (one file per workflow).

So, create a first one and call it android-feature.yml and copy paste lines:

<iframe src="https://medium.com/media/fd55492101eca9aff7a98114b08731c2" frameborder=0></iframe>
> But what they mean?

No worrier, I’ll cover it. Or if you prefer you can go right away and check this syntax in [the official documentation](https://help.github.com/en/github/automating-your-workflow-with-github-actions/workflow-syntax-for-github-actions).

So, first we’re defining a value of thename parameter, which is the full name of your workflow.

    name: Android Feature Branch CI

Next, we need to provide on what event workflow will be triggered. In my case I want to run it when someone is pushing commits to a branch other than *master* (main trunk) or which starts with *release* in its name.

    on:
      push:
        branches: 
         - '*' 
         - '!master' 
         - '!release*'

Than we can move to defining jobs. Each workflow can have multiple **jobs **which by default are running in parallel, but it could be changed to have specific sequence of them (for instance if one step relays on the outcome of the previous one).

What is worth to know that each job runs on a different instance of a virtual machine. At this point you can pick from ubuntu , windows and macOS .

In my case I want to keep my workflow short (and therefore quick) so I create only one job with IDtest. I’ve also provided it’s full name ( name) and virtual machine on which it should run ( runs-on ).

    jobs:
      test:
        name: Run Unit Tests
        runs-on: ubuntu-18.04

And finally I’ve defined steps that are included in a job. They’re tasks that are executed in sequence in the same virtual machine.

In my test job I’ve got three steps, each one created a little bit differently. First one, — uses: actions/checkout@1 , is an **action** — an atomic build block of a workflow. It’s reusable unit which is provided by GitHub, you or other public repository. More about it you can found [in official documentation](https://help.github.com/en/github/automating-your-workflow-with-github-actions/configuring-a-workflow#using-the-checkout-action). The list of some cool actions can be found on [this page](https://github.com/sdras/awesome-actions).

The goal of the first action is to allow a workflow to access the content of the repository.

Second step is more complex, but have simple goal — set up a JDK version to be Java 8.

    - name: set up JDK 1.8
          uses: actions/setup-java@v1
          with:
            java-version: 1.8

Finally a third step runs unit tests located in the project. As it is the Android project it uses [Gradle](https://gradle.org/) for build lifecycle, therefore to run the test we need to use *Gradle Wrapper *file. The command is the same as you would do it in the terminal on your PC.

    - name: Unit tests
      run: **bash ./gradlew test --stacktrace**

Everything is set up, so let’s test it! To do so, we need to create a new branch and make a commit. For presentation purposes I’m doing a simple change in the R*EADME.md* file directly in GitHub editor, but if you prefer you can make changes on your PC and then push it to GitHub. The outcome will be same — workflow will run.

So, after committing small change I go immediately to **Actions **tab in my project to check whether the workflow has been triggered:

![](https://cdn-images-1.medium.com/max/2000/1*Zvq1leBicfn2s59VtWXBVA.gif)

Hurrah! We’ve got it! And after more than a minute workflow successfully finished.

![](https://cdn-images-1.medium.com/max/2622/1*AvhqoKPxqU5jrgqPuBQ__g.png)

### Android Pull Request & Master CI

First workflow is done, so we can move ahead to second one. Just to remind you, a new one should be triggered after creating the pull request and after introducing changes on master branch (after approving the pull request).

Similarly to previous one, we need to create a new android-master.yml file in the same directory .github/workflows.

<iframe src="https://medium.com/media/f4c1d525e1390562b38114dad9e19eb0" frameborder=0></iframe>

Similarly to previous one it starts with its name .

In on element we define that we type of an event should be a trigger of a workflow:

* when we create a pull request onto *master* branch,

* when we commit some changes on the *master* branch.

    on:
      pull_request:
        branches:
          - 'master'
      push:
        branches: 
         - 'master'

Then, moving forward to jobs section you can see that it has two of them. First, test , is the same as in previous example, so I skip it here.

Second, apk, is a new one and its main purpose is to build an Android application into APK, so it can be installed on mobile device.

As in the first job, we define the name and on which virtual machine this job should ran ( runs-on ).

    apk:
        name: Generate APK
        runs-on: ubuntu-18.04

Then there are the steps. First two are the same as in test job — we allow workflow to access files in the repository and are setting JDK version.

A third job is a new one, but similar to the last from test. This time we’re not running the test Gradle task, but assembleDebug which will result with built Android APK file.

    - name: Build debug APK
      run: **bash ./gradlew assembleDebug --stacktrace**

The last step ensures that the built APK file will be persisted (not removed) after workflow finishes. In the with element we indicate which file (in path) should be saved. GitHub calls such persisted files **artifacts**.

    - name: Upload APK
      uses: actions/upload-artifact@v1
      with:
          name: app
          path: app/build/outputs/apk/debug/app-debug.apk

Now let’s trigger the pipeline again. This time we need to create a pull request (the best approach would be to merge the branch that you already has with *master*).

![](https://cdn-images-1.medium.com/max/2000/1*cHFmyFFpwWqUh9i3sU3D8w.gif)

This time you can see on the left side that there are two running job in parallel — *Run Unit Tests* & *Generate APK*.

After successfully passed workflow you can download the artifact with APK file, an icon will show up right above the workflow console log.

![](https://cdn-images-1.medium.com/max/2000/1*S1LteudpMHmkA5zUGpgeVw.png)

And that’s everything for today!

My workflows are still pretty simple, but I’m planning to change it in near future. Maybe I’ll add some jobs for **static code analysis** (e.g. with [*Sonar Cloud](https://sonarcloud.io/about)*), generating nice looking **test results report** (e.g. in [*Allure Test Reports](http://allure.qatools.ru/)*), mail notification or which might be tricky, but there helpful — introduce the job for **instrumented unit tests** (in [*Firebase Test Lab](https://firebase.google.com/docs/test-lab/?authuser=2)*).

But let’s see, I’ll work now on it and definitely share with you my results.

You can try my progress in this matter in my project:
[**wkrzywiec/WaWa-Tabor**
*WaWa Tabor is a small app that is desiganted to provide online location of all buses and trams in Warsaw each 10 - 15…*github.com](https://github.com/wkrzywiec/WaWa-Tabor)

## References
[**Automating your workflow with GitHub Actions**
help.github.com](https://help.github.com/en/github/automating-your-workflow-with-github-actions)
