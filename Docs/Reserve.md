> 
 By writing custom resolvers, you can extend Firebase SQL Connect to support
other data sources in addition to Cloud SQL. You can then combine
multiple data
sources (Cloud SQL and the data sources provided by your custom
resolvers) into
a single query or mutation.

The concept of a "data source" is flexible. It includes:

- Databases other than Cloud SQL, such as Cloud Firestore, MongoDB, and others.
- Storage services such as Cloud Storage, AWS S3, and others.
- Any API-based integration, such as Stripe, SendGrid, Salesforce, and others.
- Custom business logic.

Once you have written custom resolvers to support your additional data sources,
your SQL Connect queries and mutations can combine them in many ways,
providing benefits such as:

- A unified authorization layer for your data sources. For example, authorize access to files in Cloud Storage using data stored in Cloud SQL.
- Type-safe client SDKs for web, Android, and iOS.
- Queries that return data from multiple sources.
- Restricted function invocations based on your database state.

## Prerequisites

To write your own custom resolvers, you need the following:

- Firebase CLI v15.9.0 or higher
- Firebase Functions SDK v7.1.0 or higher

In addition, you should be familiar with writing functions using
[Cloud Functions for Firebase](https://firebase.google.com/docs/functions), which is how you will implement
the logic of your custom resolvers.

## Before you begin

You should already have a project set up to use SQL Connect.

You can follow one of the Quickstart guides to get set up if you are not
already:

- [Quickstart](https://firebase.google.com/docs/sql-connect/quickstart)
- [React quickstart](https://firebase.google.com/docs/sql-connect/quickstart/react)
- [Flutter quickstart](https://firebase.google.com/docs/sql-connect/quickstart/flutter)

## Write custom resolvers

At a high level, writing a custom resolver has three parts: first, defining a
schema for your custom resolver; second, implementing your resolvers using Cloud
Functions; and finally, using your custom resolver fields in queries and
mutations, possibly in tandem with Cloud SQL or other custom
resolvers.

Follow the steps in the next few sections to learn how to do so. As a motivating
example, suppose you have public profile information for your users stored
outside of Cloud SQL. The exact datastore is not specified in these
examples,
but it could be something like Cloud Storage, a MongoDB instance, or anything
else.

The following sections will demonstrate a skeleton implementation of a custom
resolver that can bring that external profile information into
SQL Connect.

### Define the schema for your custom resolver

1. In your Firebase project directory, run:

       firebase init dataconnect:resolver

   The Firebase CLI will prompt you for a name for your custom resolver, and ask
   whether to generate example resolver implementations in either TypeScript or
   JavaScript. If you are following this guide, accept the default name and
   generate TypeScript examples.

   The tool will then create an empty `dataconnect/schema_resolver/schema.gql`
   file and add your new resolver configuration to the `dataconnect.yaml` file.
2. Update this `schema.gql` file with a GraphQL schema that defines the queries
   and mutations your custom resolver will provide. For example, here is a schema
   for a custom resolver that can retrieve and update a user's public profile,
   stored in a datastore other than Cloud SQL:

        #
   ```dataconnect/schema_resolver/schema.gql

       type PublicProfile {
         name: String!
         photoUrl: String!
         bioLine: String!
       }

       type Query {
         # This field will be backed by your Cloud Function.
         publicProfile(userId: String!): PublicProfile
       }

       type Mutation {
         # This field will be backed by your Cloud Function.
         updatePublicProfile(
           userId: String!, name: String, photoUrl: String, bioLine: String
         ): PublicProfile
       }

### Implement the custom resolver logic

Next, implement your resolvers using Cloud Functions. Under the hood, you will
be creating a GraphQL server; however, Cloud Functions has a helper method,
`onGraphRequest`, that handles the details of doing so, so you will only need to
write the resolver logic that accesses your data source.

1. Open the file `functions/src/index.ts`.

   When you ran `firebase init dataconnect:resolver` above, the command created
   this Cloud Functions source code directory and initialized it with sample code
   in `index.ts`.
2. Add the following definitions:
   ```ts
       import {
         FirebaseContext,
         onGraphRequest,
       } from "firebase-functions/dataconnect/graphql";

       const opts = {
         // Points to the schema you defined earlier, relative to the root of your
         // Firebase project.
         schemaFilePath: "dataconnect/schema_resolver/schema.gql",
         resolvers: {
           query: {
             // This resolver function populates the data for the "publicProfile" field
             // defined in your GraphQL schema located at schemaFilePath.
             publicProfile(
               _parent: unknown,
               args: Record<string, unknown>,
               _contextValue: FirebaseContext,
               _info: unknown
             ) {
               const userId = args.userId;

               // Here you would use the user ID to retrieve the user profile from your data
               // store. In this example, we just return a hard-coded value.

               return {
                 name: "Ulysses von Userberg",
                 photoUrl: "https://example.com/profiles/12345/photo.jpg",
                 bioLine: "Just a guy on a mountain. Ski fanatic.",
               };
             },
           },
           mutation: {
             // This resolver function updates data for the "updatePublicProfile" field
             // defined in your GraphQL schema located at schemaFilePath.
             updatePublicProfile(
               _parent: unknown,
               args: Record<string, unknown>,
               _contextValue: FirebaseContext,
               _info: unknown
             ) {
               const { userId, name, photoUrl, bioLine } = args;

               // Here you would update in your datastore the user's profile using the
               // arguments that were passed. In this example, we just return the profile
               // as though the operation had been successful.

               return { name, photoUrl, bioLine };
             },
           },
         },
       };

       export const resolver = onGraphRequest(opts);

These skeleton implementations show the general shape that a resolver function
must take. To create a fully functioning custom resolver, you will need to fill
in the commented sections with code that reads and writes to your data source.

### Use custom resolvers in queries and mutations

Now that you have defined the schema of your custom resolver and you have
implemented the logic that backs it, you can use the custom resolver in your
SQL Connect queries and mutations. Later, you will use these operations
to automatically generate a custom client SDK that you can use to access all of
your data, whether backed by Cloud SQL, your custom resolvers, or a
combination.

1. In `dataconnect/example/queries.gql`, add the following definition:

       query GetPublicProfile($id: String!)
           @auth(level: PUBLIC, insecureReason: "Anyone can see a public profile.") {
         publicProfile(userId: $id) {
           name
           photoUrl
           bioLine
         }
       }

   This query retrieves a user's public profile, using your custom resolver.
2. In `dataconnect/example/mutations.gql`, add the following definition:
   ```gql
       mutation SetPublicProfile(
         $id: String!, $name: String, $photoUrl: String, $bioLine: String
       ) @auth(expr: "vars.id == auth.uid") {
         updatePublicProfile(userId: $id, name: $name, photoUrl: $photoUrl, bioLine: $bioLine) {
           name
           photoUrl
           bioLine
         }
       }
   ```
   This mutation writes a new set of profile data to the datastore, again using
   your custom resolver. Note that the schema makes use of
   SQL Connect's `@auth` directive to ensure that users can
   only update their own profiles. Because you are accessing your datastore
   through SQL Connect, you automatically can take advantage of
   SQL Connect features such as this.

In the examples above, you have defined SQL Connect operations that access data
from your datastore using your custom resolvers. However, you are not limited
in your operations to accessing data from either Cloud SQL or from
a single
custom data source. See the [Examples](https://firebase.google.com/docs/sql-connect/custom-resolvers#examples) section for some more advanced
use cases that combine data from multiple sources.

Before that, continue to the next section to see your custom resolvers in
action.

### Deploy your custom resolver and operations

As when making any changes to your SQL Connect schemas, you must
deploy them for them to take effect. Before you do so, first deploy the custom
resolver logic that you implemented using Cloud Functions:

    firebase deploy --only functions

Now you can deploy the updated schemas and operations:

    firebase deploy --only dataconnect

After making changes to your SQL Connect schemas, you must also
generate new client SDKs:

    firebase dataconnect:sdk:generate

## Examples

These examples show how to implement some more advanced use cases, and how to
avoid common pitfalls.

### Authorizing access to a custom resolver using data from Cloud SQL

One of the benefits of integrating your data sources into SQL Connect
using custom resolvers is that you can write operations that combine data
sources.

In this example, suppose you are building a social media app, and you have a
mutation implemented as a custom resolver, that sends a nudge email to a user's
friend if they have not engaged with the user in some time.

To implement the nudge feature, create a custom resolver with a schema like the
following:
   ```gql
    # A GraphQL server must define a root query type per the spec.
    type Query {
      unused: String
    }

    type Mutation {
    sendEmail(id: String!, content: String): Boolean
    }
   ```
This definition is backed by a Cloud Function, such as the following:
   ```ts
    import {
      FirebaseContext,
      onGraphRequest,
    } from "firebase-functions/dataconnect/graphql";

    const opts = {
      schemaFilePath: "dataconnect/schema_resolver/schema.gql",
      resolvers: {
        mutation: {
          sendEmail(
            _parent: unknown,
            args: Record<string, unknown>,
            _contextValue: FirebaseContext,
            _info: unknown
          ) {
            const { id, content } = args;

            // Look up the friend's email address and call the cloud service of your
            // choice to send the friend an email with the given content.

           return true;
          },
        },
      },
    };

    export const resolver = onGraphRequest(opts);
   ```
Because sending email is both costly to you and a potential vector for abuse,
you want to make sure that the intended recipient is already in the user's
friend list before using your `sendEmail` custom resolver.

Suppose that in your app, friend list data is stored in Cloud SQL:
   ```sql
    type User @table {
      id: String! @default(expr: "auth.uid")
      acceptNudges: Boolean! @default(value: false)
    }

    type UserFriend @table(key: ["user", "friend"]) {
      user: User!
      friend: User!
    }
   ```
You can write a mutation that first queries Cloud SQL to ensure that
the sender
is in the recipient's friends list before using the custom resolver to send the
email:

    # Send a "nudge" to a friend as a reminder. This will only let the user send a
    # nudge if $friendId is in the user's friends list.
    mutation SendNudge($friendId: String!) @auth(level: USER_EMAIL_VERIFIED) {
      # Step 1: Query and check
      query @redact {
        userFriend(
          key: {userId_expr: "auth.uid", friendId: $friendId}
        # This checks that $friendId is in the user's friends list.
        ) @check(expr: "this != null", message: "You must be friends to nudge") {
          friend {
            # This checks that the friend is accepting nudges.
            acceptNudges @check(expr: "this == true", message: "Not accepting nudges")
          }
        }
      }
      # Step 2: Act
      sendEmail(id: $friendId, content: "You've been nudged!")
    }

As an aside, this example also illustrates that a data source in the context of
custom resolvers can include resources other than databases and similar systems.
In this example, the data source is a cloud email sending service.

### Ensuring sequential execution by using mutations

When combining data sources, you will often need to ensure that a request to one
data source completes before making a request to a different data source. For
example, suppose you have a query that dynamically transcribes a video on demand
using an AI API. An API call such as this can be expensive, so you want to gate
the call behind some criteria, such as that the user owns the video, or that the
user has purchased some kind of premium credits in your app.

A first attempt at achieving this might look something like this:
   ```gql
    # This won't work as expected.
    query BrokenTranscribeVideo($videoId: UUID!) @auth(level: USER_EMAIL_VERIFIED) {
      # Step 1: Check quota using SQL.
      # Verify the user owns the video and has "pro" status or credits.
      checkQuota: query @redact {
        video(id: $videoId)
        {
          user @check(expr: "this.id == auth.uid && this.hasCredits == true", message: "Unauthorized access") {
            id
            hasCredits
          }
        }
      }

      # Step 2: Trigger expensive compute
      # Only triggers if Step 1 succeeds? No! This won't work because query field
      # execution order is not guaranteed.
      triggerTranscription: query {
        # For example, might call Vertex AI or Transcoder API.
        startVideoTranscription(videoId: $videoId)
      }
    }
   ```
This approach won't work because **the execution order of query fields is not
guaranteed** ; the GraphQL server expects to be able to resolve fields in any
order, to maximize concurrency. On the other hand, **the fields of a mutation
are always resolved in order**, because the GraphQL server expects that some
fields of a mutation might have side effects when resolved.

Even though the first step of the example operation does not have side effects,
you can define the operation as a mutation in order to take advantage of the
fact that mutation fields are resolved in order:
   ```gql
    # By using a mutation, we guarantee the SQL check happens FIRST.
    mutation TranscribeVideo($videoId: UUID!) @auth(level: USER_EMAIL_VERIFIED) {
      # Step 1: Check quota using SQL.
      # Verify the user owns the video and has "pro" status or credits.
      checkQuota: query @redact {
        video(id: $videoId)
        {
          user @check(expr: "this.id == auth.uid && this.hasCredits == true", message: "Unauthorized access") {
            id
            hasCredits
          }
        }
      }

      # Step 2: Trigger expensive compute
      # This Cloud Function will ONLY trigger if Step 1 succeeds.
      triggerTranscription: query {
        # For example, might call Vertex AI or Transcoder API.
        startVideoTranscription(videoId: $videoId)
      }
    }

## Limitations
   ```
The custom resolvers feature is released as an experimental public preview. Note
the following current limitations:

#### No CEL expressions in custom resolver arguments

You cannot use CEL expressions dynamically in the arguments to a custom
resolver. For example, the following is not possible:
   ```gql
    mutation UpdateMyProfile($newName: String!) @auth(level: USER) {
      updateMongoDocument(
        collection: "profiles"
        # This isn't supported:
    id_expr: "auth.uid"
        update: { name: $newName }
      )
    }
   ```
Instead, pass standard variables (for example, `$authUid`) and validate them at
the operation level using the securely evaluated `@auth(expr: ...)` directive.
```gql
    mutation UpdateMyProfile(
      $newName: String!, $authUid: String!
    ) @auth(expr: "vars.authUid == auth.uid") {
      updateMongoDocument(
        collection: "profiles"
        id: $authUid
        update: { name: $newName }
      )
    }
   ```
Another workaround is to move all of your logic into a custom resolver and
complete all of your data operations from Cloud Functions.

For example, consider this example, which won't currently work:
   ```ts
    mutation BrokenForwardToEmail($chatMessageId: UUID!) @auth(level: USER_EMAIL_VERIFIED) {
      query {
        chatMessage(id: $chatMessageId) {
          content
        }
      }
      sendEmail(
        title: "Forwarded Chat Message"
        to_expr: "auth.token.email" # Not supported.
        content_expr: "response.query.chatMessage.content" # Not supported.
      )
    }
   ```
Instead, move both the Cloud SQL query and the call to the email
service into
one mutation field, backed by a function:
   ```gql
    mutation ForwardToEmail($chatMessageId: UUID!) @auth(level: USER_EMAIL_VERIFIED) {
      forwardChatToEmail(
        chatMessageId: $chatMessageId
      )
    }
   ```
Generate an admin SDK for your database and use it in the function to perform
the Cloud SQL query:

    const opts = {
     schemaFilePath: "dataconnect/schema_resolver/schema.gql",
     resolvers: {
       query: {
         async forwardToEmail(
           _parent: unknown,
           args: Record<string, unknown>,
           _contextValue: FirebaseContext,
           _info: unknown
         ) {
           const chatMessageId = args.chatMessageId as string;

           let decodedToken;
           try {
             decodedToken = await getAuth().verifyIdToken(_contextValue.auth.token ?? "");
           } catch (error) {
             return false;
           }

           const email = decodedToken.email;
           if (!email) {
             return false;
           }

           const response = await getChatMessage({chatMessageId});
           const messageContent = response.data.chatMessage?.content;

           // Here you call the cloud service of your choice to send the email with
           // the message content.

           return true;
         }
       },
     },
    };
    export const resolver = onGraphRequest(opts);

#### No input object types in custom resolver parameters

Custom resolvers don't accept complex GraphQL input types. Parameters must be
basic scalar types (`String`, `Int`, `Date`, `Any`, etc.) and `Enum`s.

    input PublicProfileInput {
      name: String!
      photoUrl: String!
      bioLine: String!
    }

    type Mutation {
      # Not supported:
      updatePublicProfile(userId: String!, profile: PublicProfileInput): PublicProfile

      # OK:
      updatePublicProfile(userId: String!, name: String, photoUrl: String, bioLine: String): PublicProfile
    }

#### Custom resolvers cannot precede SQL operations

In a mutation, placing a custom resolver before standard SQL operations
results in an error. All SQL-based operations must appear before any custom
resolver invocations.

#### No transactions (@transaction)

Custom resolvers cannot be wrapped inside a `@transaction` block with standard
SQL operations. If the Cloud Function backing the resolver fails after an SQL
insert succeeds, the database won't automatically roll back.

To achieve transactional safety between SQL and another data source, move the
SQL operation logic inside the Cloud Function, and handle validation and
rollbacks using the Admin SDK or direct SQL connections.
