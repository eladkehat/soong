# Soong - PostgreSQL utility library for AWS Lambda

The purpose of this library is to let Lambda functions connect to PostgreSQL on RDS and run queries against it.

⚠️ Soong is currently in active development and should be considered work in progress. Do not use in production! ⚠️

Porting Soong to support a different RDBMS (like MySQL) should be fairly straightforward, but isn't a current project
goal.


## How working with a relational DB on Lambda is different

In server-full applications, it is a best practice to manage a connection pool that lets various modules in the
application re-use database connections. When you decompose an application into serverless-style functions,
there is usually no point in a connection _pool_, because every function mostly likely needs just one connection.
So the first difference is that we need a single connection per function, rather than a pool.

This does not mean that there is no connection re-use. Code that runs outside of the _handler_ function gets re-used
if the container remains warm and is re-used by another invocation of the function.


## Why "Soong"?

Soong is an infrastructure library for database access. The name is a reference to
[Noonien Soong][Noonien Soong on Wikipedia], the human cyberneticist who created
[Data][Data on Wikipedia], the android character in _Star Trek: The Next Generation_.

[Noonien Soong on Wikipedia]: https://en.wikipedia.org/wiki/List_of_Star_Trek_characters_(N–S)#Noonien_Soong
[Data on Wikipedia]: https://en.wikipedia.org/wiki/Data_(Star_Trek)
