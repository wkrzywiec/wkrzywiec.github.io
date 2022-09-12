---
title: "Your first blockchain in a matter of minutes using Hyperledger Composer"
date: 2019-06-14
summary: "Implementing a simple blockchain"
description: "In this blog post I would like to show you how easily you can run your first private blockchain based on popular framework for prototyping them called Hyperledger Composer."
tags: ["blockchain", "database", "hyperledger"]
canonicalUrl: "https://wkrzywiec.medium.com/your-first-blockchain-in-a-matter-of-minutes-using-hyperledger-composer-4e6e41d0ea0b"
---

{{< alert "link" >}}
This article was originally published on [Medium](https://wkrzywiec.medium.com/your-first-blockchain-in-a-matter-of-minutes-using-hyperledger-composer-4e6e41d0ea0b).
{{< /alert >}}  

![Photo by [redcharlie](https://unsplash.com/@redcharlie?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)](https://cdn-images-1.medium.com/max/12272/0*MBWcYwB1lVe5plf-)*Photo by [redcharlie](https://unsplash.com/@redcharlie?utm_source=medium&utm_medium=referral) on [Unsplash](https://unsplash.com?utm_source=medium&utm_medium=referral)*

*In this blog post I would like to show you how easily you can run your first private blockchain based on popular framework for prototyping them called Hyperledger Composer.*

In recent years blockchain becomes more and more not only the buzz world but it also growing to be a real solution for some common problems. For the most successful projects are cryptocurrency related, like *Bitcoin* or *Ethereum*, but many companies are already investing in other fields, like [Walmart in supply chain area](https://www.hyperledger.org/resources/publications/walmart-case-study), [Circulor in tantalum mining](https://www.hyperledger.org/resources/publications/tantalum-case-study), [Sony Global Education in education](https://www.hyperledger.org/wp-content/uploads/2017/12/Hyperledger_CaseStudy_Sony.pdf) or [Visa in international money transfers](https://blockonomi.com/visa-payments-network-hyperledger-fabric-blockchain/).

Unlike the *Bitcoin*, these four exemplary blockchains are private (permissioned) and they work differently than public blockchains (like *Bitcoin*).

## Ok, but first what blockchain really is?

In short (and I know that it might not give a full picture), **blockchain is a network of members where each of them has the same database on their** **machines**, unlike the traditional approach where database is located on a single machine to which users are connecting.

Moreover, it’s not a regular database (ledger). [**It’s immutable**](https://hackernoon.com/why-blockchain-immutability-matters-8ce86603914e), which means that you can’t modify the record that has been already saved in it. You can only append it or read entries, but don’t update or delete them.

*But how each member of a blockchain can have the same database? How it make sure that all users has the same version of it?* The answer is by **consensus**. It’s an algorithm that is needed in blockchain to make an agreement around all parties and keep them synchronized. [There are several types of consensuses](https://101blockchains.com/consensus-algorithms-blockchain) and each blockchain solutions may implement different kind of it. In Bitcoin it’s [Proof of Work](https://medium.com/coinmonks/proof-of-work-for-dummies-5abad1cd744) and in private blockchain (like in Hyperledger Fabric) it could be [Practical Byzantine Fault Tolerance (PBFT)](https://medium.com/kokster/understanding-hyperledger-fabric-byzantine-fault-tolerance-cf106146ef43) mechanism.

These are not the only attributes of blockchain, for example I’m skipping the cryptography part, but to keep this entry simple I would like to stop right here. If you want to have more comprehensive view on blockchain in general I recommend this review/blog post/video .

The last thing I would like you to know that blockchains can be classified into public and private. Anyone can join a first one, but it’s done anonymously, so nobody knows who all network members are. On the opposite, in private blockchains all users are known to each other and only allowed parties can join it.

Another difference of private (sometimes called permissioned) blockchains is that they allow to restrict activities on a blockchain based on the user roles. In other words each member could have different access rights, for example single member can see only transactions that it’s involved in. And this property makes it very promising for enterprise solutions, where privacy and security plays key role.

Note that [some experts claims that private blockchain is not a real blockchain](https://www.wired.com/story/theres-no-good-reason-to-trust-blockchain-technology/) and to some point they’re right, but again, this isn’t a topic of this blog post, but if you want to learn more about pros and cons of public and private blockchain I advice you to read this article.

[**The Battle Between Public Blockchains vs Private Blockchains** | medium.com](https://medium.com/@LindaCrypto/the-battle-between-public-blockchains-vs-private-blockchains-d76ee976dd46)

[**Public Vs Private Blockchain In A Nutshell** | medium.com](https://medium.com/coinmonks/public-vs-private-blockchain-in-a-nutshell-c9fe284fa39f)

## Hyperledger project

Moving forward with the blog post let’s not focus on how we can create our own blockchain. I would like to show you how you can model a private blockchain and there are several technologies that can help to achieve it. One of them, which I’m going to show you, is [**Hyperledger Composer**](https://hyperledger.github.io/composer/latest/) which is part of larger ecosystem of the [**Hyperledger**.](https://www.hyperledger.org/)

![Source: [Hyperledger.org](https://www.hyperledger.org/)](https://cdn-images-1.medium.com/max/6768/1*UVFTJQLaU7kfIVmroKjh7Q.png)*Source: [Hyperledger.org](https://www.hyperledger.org/)*

Of course there are several other frameworks available, like JPMorgan’s [Quorum](https://github.com/jpmorganchase/quorum), but it looks like that, at least for now, *Hyperledger* is the leader.

So what is *Hyperledger*? It’s a huge project that is hosted by [The Linux Foundation](https://www.linuxfoundation.org/), the biggest open-source community. It was built by several big companies in 2015 to make first truly production-ready blockchain development platform. Up to date [many other companies joined this project](https://www.hyperledger.org/members), because they see it as the most promising in this area. The more detailed description of *Hyperledger* could be found in their [whitepaper](https://www.hyperledger.org/members).

As you can see from above picture within *Hyperledger* there are several tools and frameworks. In this blogpost I’m focusing on *Hyperledger Composer*, but keep in mind that it’s not a production-ready solution (at least not in June 2019, when I’m writing it) and in my case I’m not creating a real blockchain solution. Hyperledger Composer can be connected with real blockchain, [Hyperledger Fabric](https://hyperledger-fabric.readthedocs.io/en/latest/), but in this tutorial I want to show you a quick way to prototype your blockchain so you’ll get a regular app that can be connected to the real blockchain and then amend it.

## Devil’s deals network

To make it more fun I’ve decided that my network (it’s how in Hyperledger’s slang is called blockchain) could be used by a devil to manage deals that he made with humans. This inspiration came to me after watching *Lucifer*, TV series.

![Source: giphy.com](https://cdn-images-1.medium.com/max/2000/1*ba5FoD8P11_NhFblOZHjHQ.gif)*Source: giphy.com*

### What will be built?

So what is the architecture of my solution? I’ve tried to keep it simple, so we have only three types of participants, each one of them with different access rights:

* **Human** — mortals, who needs to make a deal, e.g. to gain some magical powers, immortality, love, wealth, etc.

* **Devil** (or demon) — personification of evil, makes a deal with human and in return he could takes mortal’s soul forever.

* **Admin** — chiefly can do anything 😜.

Each member can do different actions (transactions) on the domain objects (assets) that are defined in the network. And there are three types of them:

* **Soul** — every *Human* should have it, *Devil* can collect it after full filing the *Deal*.

* **Proposal** — every *Human* can raise it so the *Devil* can review it and then decide whether to accept, and make a *Deal*, or reject it. *Human* can raise as many *Proposals* as she/he would like.

* **Deal** — only *Devil* can raise it (using transaction) based on *Proposal* made by a *Human*. Each *Human* can have only one *Deal*, because in exchange of the *Deal* *Devil* will take her/his *Soul* and that *Human* can have only one.

And finally here are some actions (transactions) that can be performed and they will be stored in blockchains’ log.

* **Give a Birth** — only *admin* can raise it and in this transaction *Human* participant is created with a *Soul* (*admin* can still add participant to the network, but she/he needs to remember to create also *Soul* in separate step).

* **Reject a Proposal** — *Devil* can do not accept the *Proposal* raised by a *Human*.

* **Make a Deal** — only *Devil* can make this transaction, based on *Proposal*.

* **Take a Soul** — only *Devil* can raise it, once a person make a deal *Devil&* can take person’s *Soul* depending on the terms of an agreement (e.g. when person dies, do something special). The *Soul* is added to *Devil’s* collection.

Apart from that *Human* can create a *Proposal,* but in *Hyplerledger Composer* creation of single asset is not a transaction that needs to be defined explicitly.

The picture that illustrate all actors and assets with possible transaction can be found below.

![Diagram created based on the icons made by [Smashicons](https://www.flaticon.com/authors/smashicons) and F[reepik](https://www.flaticon.com/).](https://cdn-images-1.medium.com/max/3840/1*yYzQI4opgX-a6EXaXt4SFg.png)*Diagram created based on the icons made by [Smashicons](https://www.flaticon.com/authors/smashicons) and [Freepik](https://www.flaticon.com/).*

### Defining the model

Finally we can move to the most interesting part — implementing blockchain. All *Hyperledger Composer*’s projects have specific structure that we need to follow. It contains few files and only three of them are interesting in particular (they are marked with bold font).

    devil-deals-network/
    ├── features/              // ignore this folder right now
    │   ├── support/
    │   |  └── index.js
    │   ├── sample.feature
    │   
    ├── lib/                   // transactions logic
    │   └── logic.js           
    │   
    ├── models/                // members and assets definitions
    |   └── org.hell.devil.cto 
    |
    ├── test/                  // unit tests for transactions
    |    └── logic.js
    |
    ├── .eslintrc.yml          // ignore this file right now
    ├── package.json           // key project info and dependencies
    ├── permissions.acl        // access rights definitions
    └── README.md              // easy to ready file

First, the most important file is located in **models** folder. As you might already guess it contains the definitions of all objects in the network, which are participants, assets and transactions.

First two participants are pretty straightforward. They are identified by their id, first and last name. *Devil* also can have a collection of *Souls,* he also have additional field with the array.

    participant Devil identified by devilId {
      o String devilId
      o String firstName
      o String lastName
      --> Soul[] souls
    }

    participant Human identified by humanId {
      o String humanId
      o String firstName
      o String lastName
    }

If you wonder what programming language it’s used here — it’s specific [Hyperledger Composer’s modeling language](https://hyperledger.github.io/composer/latest/reference/cto_language).

Next, there are the assets, like *Soul*, *Proposal* and *Deal*. There is also a *ProposalStatus* which is a enumeration of possible statuses of the *Proposal.* Some of the assets could be created with default value.

    asset Soul identified by soulId {
      o String soulId
      --> Human human
    }

    asset Proposal identified by **proposalId** {
      o String proposalId
      --> Human human
      o String favour
      o String terms
      o ProposalStatus status default = "WAITING_FOR_APPROVAL"
    }

    enum ProposalStatus {
      o WAITING_FOR_APPROVAL
      o REJECTED
      o ACCEPTED
    }

    asset Deal identified by dealId {
      o String dealId
      o DateTime dateTime
      --> Human human
      --> Devil devil
      o String favour
      o String terms
      o Boolean isFulfilled default = false
    }

And finally transactions. Each of them, apart from declaring its name, contains few fields without which it can’t be processed, they’re arguments.

    transaction GiveBirthToHuman {
      o String humanId
      o String firstName
      o String lastName
    }

    transaction RejectProposal {
      --> Devil devil
      --> Proposal proposal
      o DateTime dateTime
    }

    transaction MakeDeal {
      --> Devil devil
      --> Proposal proposal
      o DateTime dateTime
    }

    transaction TakeSoul {
      --> Devil devil
      --> Deal deal
      --> Soul soul
      o DateTime dateTime
      o String description
    }

### Defying transactions (smart contracts) logic

Next let’s move on to implementing the logic of each transactions. It can be done in *logic.js* file which is written in *JavaScript*.

Each function needs to have a decorator with metadata above the function’s name. It must contains the human readable description of what it is doing, in next line followed by @param which indicates the definitions of the parameter and in the last line there is a @transaction parameter.

In the code you might see objects like [AssetRegistry](https://hyperledger.github.io/composer/latest/api/runtime-assetregistry) or [ParticipantRegistry](https://hyperledger.github.io/composer/latest/api/client-participantregistry). They are specific for assigning the Asset or Participant to the variable. More about transaction’s logic can be found in [official tutorial ](https://hyperledger.github.io/composer/latest/reference/js_scripts)or documentation.

```js
'use strict';
/**
 * Devil's deals transactions logic
 */

/**
 * Admin can give birth to human - flesh and soul are created
 * @param {org.hell.devil.GiveBirthToHuman} giveBirth
 * @transaction
 */
async function giveBirth(giveBirth) {
    
    var factory = getFactory();
    var human = factory.newResource('org.hell.devil', 'Human', giveBirth.humanId);
    human.firstName = giveBirth.firstName;
    human.lastName = giveBirth.lastName;
    
    let humanRegistry = await getParticipantRegistry('org.hell.devil.Human');
    await humanRegistry.add(human);

    var soul = factory.newResource('org.hell.devil', 'Soul', giveBirth.humanId);
    soul.human = human;
    soul.soulId = giveBirth.humanId;
    let soulRegistry = await getAssetRegistry('org.hell.devil.Soul');
    await soulRegistry.add(soul);
}

 /**
 * Devil can reject proposal made by human
 * @param {org.hell.devil.RejectProposal} rejectProposal
 * @transaction
 */
async function rejectProposal(rejectProposal) {
    
    let proposal = rejectProposal.proposal;
    proposal.status = "REJECTED";
    
    let proposalRegistry = await getAssetRegistry('org.hell.devil.Proposal');
    await proposalRegistry.update(proposal);
}

/**
 * Devil can accept proposal made by human
 * @param {org.hell.devil.MakeDeal} makeDeal
 * @transaction
 */
async function makeDeal(makeDeal) {
    
    let proposal = makeDeal.proposal;
    proposal.status = "ACCEPTED";
    
    let proposalRegistry = await getAssetRegistry('org.hell.devil.Proposal');
    await proposalRegistry.update(proposal);

    let human = proposal.human;
    let dealId = human.firstName + ':' + human.lastName + ':' + human.humanId;
    
    var factory = getFactory();
    var deal = factory.newResource('org.hell.devil', 'Deal', dealId);

    deal.dateTime = makeDeal.dateTime;
    deal.human = human;
    deal.devil = makeDeal.devil;
    deal.favour = proposal.favour;
    deal.terms = proposal.terms;

    let dealRegistry = await getAssetRegistry('org.hell.devil.Deal');
    await dealRegistry.add(deal);
}

/**
 * Devil can take human soul to hell after fullfilling the terms of a deal
 * @param {org.hell.devil.TakeSoul} takeSoul
 * @transaction
 */
async function takeSoul(takeSoul) {
    
    let deal = takeSoul.deal;
    deal.isFulfilled = true;
    let dealRegistry = await getAssetRegistry('org.hell.devil.Deal');
    await dealRegistry.update(deal);

    let devil = takeSoul.devil;
    let souls = devil.souls;
    let soul = takeSoul.soul;
    if (typeof souls === 'undefined') {
        souls = new Array();
    }
    souls.push(soul);
    devil.souls = souls;
    let devilRegistry = await getParticipantRegistry('org.hell.devil.Devil');
    await devilRegistry.update(devil);
}
```

### Defying permissions

Finally we can specify access rights of both participants. By design *Human* and *Devil* could perform different actions. For example, *Human* can raise a *Proposal*, but could not create a *Deal*.

    /**
     * Access control list of Devil's Deal network.
     */
    
     rule DevilReadAndUpdateAccessToOwnProfile {
        description: "Allow devil to read access to her/his profile info"
        participant(p): "org.hell.devil.Devil"
        operation: UPDATE, READ
        resource(r): "org.hell.devil.Devil"
        condition: (p.getIdentifier() === r.getIdentifier())
        action: ALLOW
    }
    
    rule DevilCanReadEverything {
        description: "Allow Devil to read access to all resources"
        participant: "org.hell.devil.Devil"
        operation: READ
        resource: "org.hell.devil.*"
        action: ALLOW
    }
    
    rule DevilCanRejectProposalTransaction {
        description: "Allow Devil to reject Proposal"
        participant(p): "org.hell.devil.Devil"
        operation: ALL
        resource(r): "org.hell.devil.RejectProposal"
        condition: (p.getIdentifier() === r.devil.getIdentifier() 
                    && r.proposal.status === "WAITING_FOR_APPROVAL")
        action: ALLOW
    }
    
    rule DevilMakeDealTransaction {
        description: "Allow Devil make a Deal with human based on Proposal"
        participant(p): "org.hell.devil.Devil"
        operation: ALL
        resource(r): "org.hell.devil.MakeDeal"
        condition: (p.getIdentifier() === r.devil.getIdentifier() 
                  && r.proposal.status === "WAITING_FOR_APPROVAL")
        action: ALLOW
    }
    
    rule DevilCanModifyProposal {
        description: "Allow Devil to modify Proposal"
        participant: "org.hell.devil.Devil"
        operation: UPDATE
        resource: "org.hell.devil.Proposal"
        action: ALLOW
    }
    
    rule DevilCanModifyDeal {
        description: "Allow Devil to modify Proposal"
        participant: "org.hell.devil.Devil"
        operation: ALL
        resource: "org.hell.devil.Deal"
        action: ALLOW
    }
    
    rule DevilCanTakeSoulTransaction {
        description: "Allow Devil to TakeSoul transaction"
        participant(p): "org.hell.devil.Devil"
        operation: ALL
        resource(r): "org.hell.devil.TakeSoul"
        condition: (p.getIdentifier() === r.devil.getIdentifier())
        action: ALLOW
    }
    
    rule HumanReadAndUpdateAccessToOwnProfile {
        description: "Allow human to read access to her/his profile info"
        participant(p): "org.hell.devil.Human"
        operation: UPDATE, READ
        resource(r): "org.hell.devil.Human"
        condition: (p.getIdentifier() === r.getIdentifier())
        action: ALLOW
    }
    
    rule HumanReadAccessToDevilAndDeamonsList {
        description: "Allow human to know devil participant list"
        participant: "org.hell.devil.Human"
        operation: READ
        resource: "org.hell.devil.Devil"
        action: ALLOW
    }
    
    rule HumanCanCreateAndReadOwnProposal {
        description: "Allow human to make a proposal"
        participant(p): "org.hell.devil.Human"
        operation: CREATE, READ
        resource(r): "org.hell.devil.Proposal"
        condition: (p.getIdentifier() === r.human.getIdentifier())
        action: ALLOW
    }
    
    rule SystemACL {
      description:  "System ACL to permit all access"
      participant: "org.hyperledger.composer.system.Participant"
      operation: ALL
      resource: "org.hyperledger.composer.system.**"
      action: ALLOW
    }
    
    rule NetworkAdminUser {
        description: "Grant business network administrators full access to user resources"
        participant: "org.hyperledger.composer.system.NetworkAdmin"
        operation: ALL
        resource: "**"
        action: ALLOW
    }
    
    rule NetworkAdminSystem {
        description: "Grant business network administrators full access to system resources"
        participant: "org.hyperledger.composer.system.NetworkAdmin"
        operation: ALL
        resource: "org.hyperledger.composer.system.**"
        action: ALLOW
    }

In general, there are two types of access right rules with and without condition. First ones are more general, they are applied to all users. For example the rule **HumanReadAccessToDevilAndDeamonsList** tells that all *Humans* can see whole list of *Devils*, no matter to which one they had raised *Proposal* before.

Later type of access right contains a condition and usually it’s used to stress out that a particular user can only see her/his own assets. For example, rule **HumanCanCreateAndReadOwnProposal** covers that *Human* can raise a *Proposal* only for herself/himself and can only see own *Proposals*.

[More about Hyperledger Composer’s Access Control Language can be found in documentation.](https://hyperledger.github.io/composer/latest/reference/acl_language)

### Running the Playground

*Prerequisites*. In order to follow my instructions you need to have installed two tools: git and Docker. First one is a version control system and could be downloaded [from here](https://git-scm.com/downloads). Second is a container tool for packaging app so they can be ran anywhere. If you don’t have Docker go check out one of the following instructions for [Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/), [Windows](https://docs.docker.com/docker-for-windows/install/) or [Mac](https://docs.docker.com/docker-for-mac/install/).

Now let’s run a [Playground environment](https://hyperledger.github.io/composer/latest/playground/playground-index). To keep it simple, so you don’t need to install any Hyperledger Composer tools, I’ve decided to download Docker image with predefined environment (still, if you want to have installed all necessary tools on your machine go check [official documentation](https://hyperledger.github.io/composer/latest/installing/development-tools.html)).

To run the environment with a container open terminal app and type:

```bash
docker run --name composer-playground --publish 8080:8080 --detach hyperledger/composer-playground
```

Above command will download and run the composer-playground Docker file.

After the above command has finished go to the web browser and type localhost:8080, so the web Playground will open.

![](https://cdn-images-1.medium.com/max/2704/0*cd8WHekeqS96cW_l.png)

If so, that’s great! Now git clone this project using the command:

```bash
git clone https://github.com/wkrzywiec/devil-deals-network.git
```

After that you should have devils-deals-network@0.0.1.bna that can be deployed to the *Hyperledger Composer Playground*. To do so, go back to *Playground* in your web browser and then click *Deploy a new business network*.

![](https://cdn-images-1.medium.com/max/2000/0*fR-eokXJPPyEdot9.png)

There scroll down to the section where you can drop or browse the file to upload.

![](https://cdn-images-1.medium.com/max/2000/0*0xMh1g_PvfU8XTUg.png)

After choosing the file click *Deploy* button on the right side.

![](https://cdn-images-1.medium.com/max/2000/0*HAmgqbcK6LJLE5pZ.png)

This blockchain was successfully deployed!

![](https://cdn-images-1.medium.com/max/2000/1*ddxpLCUwhT7J8hAcbvWj2Q.gif)

If you happen to stop the container (in e.g. when turning off your PC) you can rerun it with command:

```bash
docker start --interactive composer-playground
```

### Play around with blockchain

Blockchain is deployed now, so let’s add some transactions!

First we need to login as an admin and create two user accounts — one for a devil and one for a human. Therefore go to the main page where will be a business connection card for an admin. At the bottom, there is **Connect now** link.

Then, go to **Test** (at the top of the page) and click **Create New Participant** icon at the top right corner.

![](https://cdn-images-1.medium.com/max/2550/1*oUOUAhwEgb6vflznEQHJug.png)

First we create a devil’s account, where we need to provide *devilId* (it’s generated automatically, but I advise to type your own, that will be better to remember), *firstName* and *lastName*. After providing it click **Create New** button.

![Creating devil’s user account.](https://cdn-images-1.medium.com/max/2000/1*OBKbQeMxBYfd76R0UYF9WA.png)*Creating devil’s user account.*

![](https://cdn-images-1.medium.com/max/2000/1*TQgPfv6AKjHpCX1DCrLzYw.png)

Next, we need to create Human account. It could be done similarly to the devils’, but it would require to create also a Soul in separate step. Therefore to do it in one step, click on **Submit Transaction** button at the bottom left.

It’ll open similar window as for creating a devil participant but in this case make sure that from the drop down list **GiveBirthToHuman** is picked. And then provide similar data as for a devil and click **Submit**.

For this demo, I’ll replicate to the polish legend about a man[, Pan Twardowski, who made a bargain with a devil.](https://en.wikipedia.org/wiki/Pan_Twardowski)

![](https://cdn-images-1.medium.com/max/2000/1*eOGfJxlvkPeOx4AhF4aWPQ.png)

Once both users are created and saved on blockchain, let’s create network business cards, which allows them to login. To do that go to **admin** (at the top right corner) and from the list pick **ID Registry**. On a new page click **Issue New ID** and in a pop-up window, in a field **Participant,** start typing devil’s ID so the list of available users will appear. Then provide username in the ID Name field and apply it by clicking **Create New** button.

![](https://cdn-images-1.medium.com/max/2000/1*7wvgdo1RqAfeSVUKwwNtsQ.png)

Same steps repeat for Pan Twardowski’s account. After that, on the same page, there is a list of available users and from it pick Human’s account by clicking Use **Now button** when you hover on it’s label.

![](https://cdn-images-1.medium.com/max/2530/1*5qrRRSCq4XS0n8Enh5z9Vg.png)

We’re logged as a Human so now we would like to raise a Proposal by clicking on **Proposal** icon on the left panel and then by clicking the **+Create New Asset** button at the top right corner. In new window provide proposalId, human (Twardowski’s Id), description of a favour and terms when soul could be taken to hell.

![](https://cdn-images-1.medium.com/max/2000/1*FmHaP52-2NohwhPJ_v0xtA.png)

Proposal was saved, so now we should switch to devil’s user. Once you’re logged as a devil you can submit a new transaction **RejectProposal** or **MakeDeal**. I choose to go with latter one. An input for a transaction are ids of a devil and Proposal.

![](https://cdn-images-1.medium.com/max/2000/1*YptaLwZ_sTDinC1bcH71-g.png)

Deal has been done, Proposal has changed status to accepted and also all details from it has been copied to the Deal. To check that go to Deal’s asset tab (left menu).

![](https://cdn-images-1.medium.com/max/2564/1*ydIKfU3uxvsbd-iV0CzgYg.png)

And finally, still logged as a devil, we can submit *TakeSoul* transaction.

![](https://cdn-images-1.medium.com/max/2000/1*7SfnBOAbLfQV9bYzOgeuFw.png)

After this transaction Deal’s field isFuillfield is now true and Devil’s account contains first Soul.

![](https://cdn-images-1.medium.com/max/2548/1*TvfHbaTEhZfrjLPJ39sTrw.png)

If you want to check the history log (the ledger) for this blockchain go to **All Transactions** tab (left menu).

![](https://cdn-images-1.medium.com/max/2548/1*r6--pyX8K9hoL1g7-68drw.png)

This was a simple example of how you can play around with my blockchain. If you want go check other scenarios like rejecting the Proposal or raising a Deal without it (which is not possible).

### How to create you own blockchain?

If you’ve made it to reach this point, you’re probably eager to know how to create your own blockchain. You can modify mine, if you want, by clicking **Define** button at the top bar, where are all files that define assets, transactions logic and permission rules. You can adjust them as you want and then redeploy it to test them.

Another way would be to create your own network from scratch or from prepared samples. Both options are available from **Deploy New Business Network** site which is available under [http://localhost:8080/login?ref=web-%24default#deploy](http://localhost:8080/login?ref=web-%24default#deploy).

If you want more insight on all capabilities of *Hyperledger Composer* go to the official documentation site.

[**Introduction | Hyperledger Composer** | hyperledger.github.io](https://hyperledger.github.io/composer/latest/introduction/introduction)

Full code of my project is available on GitHub:

[**wkrzywiec/devil-deals-network** | github.com](https://github.com/wkrzywiec/devil-deals-network)

## References
* [**Unlocking Economic Advantage with Blockchain: A guide for asset managers | *J.P. Morgan* Securities** | jpmorgan.com](https://www.jpmorgan.com/global/cib/markets-investor-services/blockchain-economics)
* [**Blockchain Beyond the Hype** | weforum.org](https://www.weforum.org/whitepapers/blockchain-beyond-the-hype)
* [**Why blockchain is a terrible idea for applications** | hackernoon.com](https://hackernoon.com/why-blockchain-is-a-terrible-idea-for-applications-8393d44f6cab)
* [**Comparison of Permissioned Blockchains** | medium.com](https://medium.com/coinmonks/comparison-of-permissioned-blockchains-6537a0694df0)
