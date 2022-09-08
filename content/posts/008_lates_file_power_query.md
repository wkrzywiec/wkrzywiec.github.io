---
title: "Getting data from the latest file in a folder using Power Query"
date: 2018-06-13
summary: "Automate loading data from the latest file in MS Excel"
description: "One of the most common tasks of Power Query is to set up automated data refresh from multiple sources. One of them are folders, which retrieve basic information about files (e.g. create date, extension, size, etc.), but also allows to enter one or more files, which is very powerful feature. On a daily basis I download/receive similar reports for processing so to avoid reoccuring tasks (copy/past, filtering and transforming data) I use Power Query to get the latest file from the folder and prepare it for me for further analysis."
tags: ["excel", "power-query"]
canonicalUrl: "https://wkrzywiec.medium.com/getting-data-from-the-latest-file-in-a-folder-using-power-query-51dfa4bff711"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/getting-data-from-the-latest-file-in-a-folder-using-power-query-51dfa4bff711).
{{< /alert >}}

![“Charts with statistics on the screen of a laptop on a glossy surface” by [Carlos Muza](https://unsplash.com/@kmuza?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/4852/0*fwxCIDYhu7pg61pS)*Photo by [Carlos Muza](https://unsplash.com/@kmuza?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*One of the most common tasks of Power Query is to set up automated data refresh from multiple sources. One of them are folders, which retrieve basic information about files (e.g. create date, extension, size, etc.), but also allows to enter one or more files, which is very powerful feature. On a daily basis I download/receive similar reports for processing so to avoid reoccuring tasks (copy/past, filtering and transforming data) I use Power Query to get the latest file from the folder and prepare it for me for further analysis.*


Here is the process workflow, what I want to achieve.

1. User prepare/download input report and copy-paste it into specific folder (e.g. on a shared drive). This folder will store only one type of data source, so if we want to have multiple data sources we need to create folder for each of them.

1. Next user opens prepared Power Query report and refresh it with the latest file that is in folder.

Here are the steps describing how I have managed to achieve that.

### Step 1. Create “Get Data from Folder” query

First we need to create standard query that will give us a list of files in specific folder. Select *Data->Get Data -> From File -> From Folder *and in a new window input folder path and click **OK**.

![](https://cdn-images-1.medium.com/max/2000/1*rHcYT21nIoGGYffGpcWOMg.png)

Next window will show up and click **Edit**.

![](https://cdn-images-1.medium.com/max/2000/1*kLfJEN6ulVl0SkfFkXRSMw.png)

### Step 2. Extract the latest file from the folder

We are now in Query Editor, where we need to define steps required to get the latest file in a folder. To do that sort all records descending by column *Date created.*

![](https://cdn-images-1.medium.com/max/2000/1*2HT1HxjigQgsBLzFjg_Kfw.png)

Then we need to exclude all temporary files that are created while the file is opened (it is hidden file). In column *Name *select *Text Filer -> Does Not Begin With *and in inputbox type **~$ **(this prefix is added to each temporary Excel file).

![](https://cdn-images-1.medium.com/max/2000/1*8qkUshbnSxKFhTRW3JNPNw.png)

![](https://cdn-images-1.medium.com/max/2000/1*geJ3NMAlgepImPhMLdUbug.png)

Finally we want only to get into the top file, so click on the top-left corner of the table and select **Keep Top Rows… **and then, in message box, input **1**.

![](https://cdn-images-1.medium.com/max/2000/1*aXGdpCZTWsWUEGb0HQKZ9w.png)

![](https://cdn-images-1.medium.com/max/2000/1*zO2Hue0cYRjVgk5ZpAfvNg.png)

### Step 3. Enter the latest file from Query Editor

Once we’ve got only single file we can open it. To do that double-click on the symbol of the *Content* column, so it will be expanded.

![](https://cdn-images-1.medium.com/max/2000/1*8g_NnQUUGmwpZjBWFxrdAQ.png)

Combine Files wizard will show up, where we need to define worksheet where the data are stored. In our case it will be *Sheet1, *so select it and click **OK**.

![](https://cdn-images-1.medium.com/max/2000/1*HgnMARw3rrJwXJOPDo-bsw.png)

A voile! And that’s it. You can now *Close & Load *query, so the new query table will be created and during each refresh data will be taken from the latest file in specified folder.

![](https://cdn-images-1.medium.com/max/2000/1*a2IhcBAlmXWsQZZPotQYNg.png)

In [next blog post](https://medium.com/@wkrzywiec/passing-source-folder-path-as-parameter-to-query-code-in-power-query-19ec60797d94), I explain how to pass a folder path as a parameter to the query, so it won’t be directly incorporate in query code.
