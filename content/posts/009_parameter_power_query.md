---
title: "Passing source folder path as parameter to query code in Power Query"
date: 2018-06-13
summary: "How to face changing data source file in MS Excel Power Query"
description: "During Power Query report creation you probably face the problem that you need to change data source file directory. It requires to go to the editor and manually, change static value of the source directory. Usually this approach will works fine, but it could be time consuming and error prone. So to overcome it, I externalize path to a file from query code into Excel table, which makes changing path directory more simple"
tags: ["excel", "power-query"]
canonicalUrl: "https://wkrzywiec.medium.com/passing-source-folder-path-as-parameter-to-query-code-in-power-query-19ec60797d94"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/passing-source-folder-path-as-parameter-to-query-code-in-power-query-19ec60797d9).
{{< /alert >}}

![Photo by [Zoshua Colah](https://unsplash.com/@zoshuacolah?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/9796/0*m87beTMJlJZgvk6t)*Photo by [Zoshua Colah](https://unsplash.com/@zoshuacolah?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*During Power Query report creation you probably face the problem that you need to change data source file directory. It requires to go to the editor and manually, change static value of the source directory. Usually this approach will works fine, but it could be time consuming and error prone. So to overcome it, I externalize path to a file from query code into Excel table, which makes changing path directory more simple.*

To fully understand what I want to achieve, please see my [previous post](https://medium.com/@wkrzywiec/getting-data-from-the-latest-file-in-a-folder-using-power-query-51dfa4bff711), where I explain my data-upload workflow.

In short, I want to extract the latest file that is in a particular folder, open it and load into my report spreadsheet. Thanks to that I won’t need to replace source file with a new version, just copy-paste new one to destination folder and Power Query will do all the work for me.

### Step 1. Prepare standard query table

To begin create regular query table to access latest Excel file in a particular folder. I’ve covered it in [previous blog post](https://medium.com/@wkrzywiec/getting-data-from-the-latest-file-in-a-folder-using-power-query-51dfa4bff711).

### Step 2. Create table in working Excel file

Next we need to create table (in separate WorkSheet) that will contain folder paths where input files are stored.

My order table contains columns:

* **Index**

* **Source** — my custom name of the folder

* **Path** — folder, where files are stored

* **Tab_name** — name of the tab, which contains necessary data

![](https://cdn-images-1.medium.com/max/2000/1*hr0IW52MZEHJ9EbD8OOD5g.png)

Make sure that you remember table name. My is *tableConfig*.

### Step 3. Create custom function to load folder path from config table

Within Query Editor, in the *Queries* list (left hand side) right click on *Other Queries* folder and select *New Query -> Other Sources -> Blank Query.*

![](https://cdn-images-1.medium.com/max/2000/1*FLTMQ4xXjTVm5bK65ndrZQ.png)

Next, optionally, rename query. I’ve named it *fParam*.

Once it is set up open **Advanced Editor** (should be in Home ribbon) and copy paste below code:

    let Parameter=(TableName as text,RowNumber as number) =>

    let

         Source = Excel.CurrentWorkbook(){[Name=TableName]}[Content],
         value = Source{RowNumber-1}[Path]

    in

         value

    in Parameter

Above function contains two arguments:

* **TableName** —name of the config table that contains folder path (this table was created in previous step),

* **RowNumber** — number of the row, which contains specific folder path.

Notice, that in line 4 (value = Source{RowNumber-1}[Path]) text “*Path*” refers to column name in *tableConfig*. Other columns are only for my information, further implementation.

After clicking *Close & Load* new Worksheet will be created. You can delete it, the query will remain saved.

### Step 4. Create intermediate query table to load folder content

This is tricky part. In an ideal world we could use above function directly in the query. Unfortunately, when we replace source code path we get following error:

![](https://cdn-images-1.medium.com/max/2344/1*hK_NU8ZWR6TQwn3XDpORfw.png)

It is due to the fact that we are using two kinds of data sources in the query. More about this problem can be found [here](https://www.excelguru.ca/blog/2015/03/11/power-query-errors-please-rebuild-this-data-combination/). As a workaround we need to create intermediate query table that contains info about files in a folder.

As in a previous step, create blank query (with a name *OrderList*) and copy paste following code:

    let
        Source = Folder.Files(fParam("tableConfig", 1))
    in
        Source

![](https://cdn-images-1.medium.com/max/3838/1*68ZMkI91xGEMiz9f0zp4vA.png)

Similar to Step 3, hide this query by removing its tab.

### Step 5. Replace static data source path with paths from dynamic table

Finally open query that was created in step 1 and in **Advanced Editor** replace following line:

    Source = Folder.Files("D:\New folder (2)"),

with

    Source = OrderList,

*OrderList* is a query table that was created in step 4.

And that’s it!

Next time, I’ll show how to dynamically load data source worksheet name from configuration table to the query.
