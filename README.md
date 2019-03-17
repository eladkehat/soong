# Soong - PostgreSQL utility library for AWS Lambda

The purpose of this library is to let Lambda functions connect to PostgreSQL on RDS and run queries against it.

⚠️ Soong is currently in active development and should be considered work in progress. Do not use in production! ⚠️


## How working with a relational DB on Lambda is different

1. [Authentication](#authentication)
1. [Connection Reuse](#connection-reuse)
1. [Resource Constraints](#resource-constraints)


### Authentication

#### Non-Secret Parameters
Database connection parameters, such as the host, port, database name and user name, should be passed to your lambda
functions using environment variables. Soong supports this pattern by automatically detecting those variables.

If you are using [SAM](https://aws.amazon.com/serverless/sam/), you can assign those parameters to all of your
functions in the global section of the template, as shown below. Soong will pick these variables automatically.
```yaml
Globals:
  Function:
    Environment:
      Variables:
        PG_HOST: "postgres1.abcde123.us-east-1.rds.amazonaws.com"
        PG_DBNAME: database1
        PG_USER: jane_doe
```

#### Password
A database password however, **should not be used at all!** Instead, use IAM authentication, as explained in the
[RDS user guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.html).

Soong supports this authentication pattern by automatically generating an auth token when running in the Lambda
environment.

In order to enable this pattern, you must:
1. Enable IAM db authentication for your RDS instance
([user guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Enabling.html)).
1. Create a database user that uses IAM authentication
([user guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.DBAccounts.html)).
You can also `GRANT rds_iam` to an existing user.
1. Create an IAM policy for IAM database access
([user guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.IAMPolicy.html)).
Make sure that the policy covers the user from the previous step.
1. Assign that policy to the role under which your functions execute
([user guide](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html?shortFooter=true)).

Finally, you must use RDS API to generate an auth-token to use in place of a password. Soong does that for you
behind the scenes whenever you create a connection.

#### Code Example
If you did all of the above, connecting to the database from your code is now a breeze:
```python
import soong
# The fancy cursor_factory is optional
with soong.connect(cursor_factory=psycopg2.extras.NamedTupleCursor) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT 'Hello, world!' AS hello;")
        assert cursor.fetchone().hello == 'Hello, world!'
```

### Connection Reuse
In server-full applications, it is a best practice to manage a connection pool that lets various modules in the
application reuse database connections. When you decompose an application into serverless-style functions,
there is usually no point in a connection _pool_, because every function most likely needs just one connection.
This is why Soong makes it simple to connect, but does not provide a connection pool.

This does not mean that there is no connection reuse. Code that runs outside of the _handler_ function gets reused
if the container remains warm and is reused by another invocation of the function.

#### Code Example
Generate the connection at the module scope, outside of the _handler_, so it can be reused:
```python
import soong

pg_conn = soong.connect()

def lambda_handler(event, context):
    with pg_conn:
        # Run some queries inside a transaction
        pass
```

Note that you can also generate connections inside the handler if you want them to close rather than remain open for
reuse. There are some scenarios where this is the better option, such as when your function rarely gets called, so
there is no connection reuse in practice, but every invocation keeps a connection hanging for a while, wasting
resources on your database server.


### Resource Constraints
With Lambda you pay directly for the CPU/Memory and execution time. Therefore it is important to limit resource
utilization to the minimum necessary. In addition, code in lambda functions tends to be short and simple.

In my opinion, with most lambda functions it makes sense to avoid ORM tools, such as
[SQL Alchemy](https://www.sqlalchemy.org), and opt for a more direct approach that is also more lightweight.

The Soong `query` and `dml` modules provide some well-documented utility functions that save you from writing a lot
of boilerplate code in the most common database access use cases.

#### Code Example
```python
import soong

pg_conn = soong.connect(cursor_factory=psycopg2.extras.NamedTupleCursor)

# Get the gizmo with id 42 from the gizmos table
gizmo42 = soong.query.get(pg_conn, 'gizmos', 42)
print(f'Got gizmo {gizmo42.name}')

# Now rename it
soong.dml.update(pg_conn, 'gizmos', 42, {'name': 'Gizmo42: The Next Generation'})

# Add a new gizmo
id = soong.dml.insert(pg_conn, 'gizmos', {'name': 'Best gizmo ever!', 'color': 'Bright red'}, returning='id')

# Run a SELECT
for gizmo in soong.query.select(pg_conn, 'gizmos', {'color': 'pink'}):
    print(gizmo.name)

# You can also run an arbitrary query, without the boilerplate
for gizmo in soong.query.execute(pg_conn, 'SELECT * FROM gizmos WHERE color = %s', ('pink', )):
    print(gizmo.name)
```


## Why "Soong"?
The name is a reference to [Noonien Soong][Noonien Soong on Wikipedia], the human cyberneticist who created
[Data][Data on Wikipedia], the android character in _Star Trek: The Next Generation_.

[Noonien Soong on Wikipedia]: https://en.wikipedia.org/wiki/List_of_Star_Trek_characters_(N–S)#Noonien_Soong
[Data on Wikipedia]: https://en.wikipedia.org/wiki/Data_(Star_Trek)
