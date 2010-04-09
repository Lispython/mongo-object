# MongoDB object wrapper for python

## About

mongomodels is a cocktail of the Django ORM mixed with JavaScript dot 
object notation. Every document is returned as object that can be traversed 
using the objects attributes. It is based on the awesome pymongo lib by
mike from mongodb.

A simple JSON document

    {
        'me': {'age': 24}, 
        'name': 'john', 
        'friends': ['mike', 'dwight', 'elliot']
    }
   
can now be accessed like this
   
    >>> print doc.name
    john
    >>> print doc.friends[0]
    mike
    >>> print doc.me.age
    24
   
For those who are familar with the Django ORM, mongodb-object behaves very
similar.

## Getting started

### Installation

    git clone git://github.com/Deepwalker/mongodb-object.git
    cd mongodb-object
    sudo python setup.py install
    
### Do the mambo

Let's start with a simple demonstration in the Python interactive console.
Open a MongoDB connection and start with a mongodb-object collection. The
collection is the base container for our work with mongodb-object.

    >>> import pymongo
    >>> from mongomodels import Model, Manager
    
    >>> db = pymongo.Connection().test_db
    >>> class User(Model):
            pass
    >>> manager = Manager(db, User)

Now we create a new document using an empty document template from the
collection. This is necessary because the document needs to know to which
collection it belongs

    >>> doc = User(name='John')
    >>> doc.name = 'john'
    >>> doc.person = {}
    >>> doc.person.age = 24
    >>> doc.person.gender = 'male'
    >>> manager.save(doc)
        ObjectId('4bbeccd863a9f01309000000')
    >>> doc
    User({'person': {'gender': 'male', 'age': 24}, '_id': ObjectId('4bbeccd863a9f01309000000'), 'name': 'John'})
    
We can also reference documents on the fly. Retrieval is powered by lazy
loading. Only when you select an attribute of a referenced document, the
document will be retrieved.

    >>> doc2 = User()
    >>> doc2.friends = [doc]
    >>> manager.save(doc2)
    ObjectId('4bbecd3863a9f01309000001')
    >>> doc2.friends
    [DBRef('User', ObjectId('4bbeccd863a9f01309000000'))]
    >>> doc2.friends[0].get().person.age
    24
    
### Finding documents

As a collection holds all documents, we have to ask the collection when
we want to find a special document.

    >>> manager.find_one(person__age=24)
    User({u'person': {u'gender': u'male', u'age': 24}, u'_id': ObjectId('4bbeccd863a9f01309000000'), u'name': u'John'})
    >>> manager.find_one(person__age__lt=25)
    User({u'person': {u'gender': u'male', u'age': 24}, u'_id': ObjectId('4bbeccd863a9f01309000000'), u'name': u'John'})
    >>> manager.find_one(person__age__lt=24)
    None
    >>> manager.find_one(person__age=24, name='john')
    User({u'person': {u'gender': u'male', u'age': 24}, u'_id': ObjectId('4bbeccd863a9f01309000000'), u'name': u'John'})
    
As you can see, we emulate the dot notation of embedded documents using
the __ chars like Django does. We can also append query operators 
($lt, $lte, $gt, $gte, $ne, $nin, $in, $all, $size) at the end.

You cannot only query for one document, you can retrieve also a list of
documents using find() instead of find_one(). find(), query() and all() return 
lazy Query object, and query doesnot actually act on db.

    >>> query = manager.find()
    >>> query
    <mongomodels.query.Query object at 0x8893e6c>
    >>> query.count()
    2
    >>> for doc in query:
    ...     print doc, doc.keys()
    ...
    User({u'person': {u'gender': u'male', u'age': 24}, u'_id': ObjectId('4bbeccd863a9f01309000000'), u'name': u'John'}) [u'person', u'_id', u'name']
    User({u'_id': ObjectId('4bbecd3863a9f01309000001'), u'friends': [DBRef(u'User', ObjectId('4bbeccd863a9f01309000000'))]}) [u'_id', u'friends']
    
find() accepts the same parameters as find_one() does.

### Bulk update and remove

To do a bulk update or remove, we use the query() method.

    >>> manager.find(name='John').update(set__name='jack')
    >>> manager.find_one(name='jack').name
    jack
    >>> manager.find(name='jack').remove()
    >>> manager.find().count()
    1

update() makes use of the MongoDB update operators 
($set, $inc, $push, $pushAll, $pull, $pullAll). You have to prefix the 
document key with one of the operators above. Embedded docs can be
accessed using the previously mentiond __ chars. For example:

    set__person__gender=10
    
### Document list options (count, skip, limit, sort)

Using the find() method, you get a list of documents. This list can be
sorted, or paginated using the known methods from pymongo.

    >>> manager.find(name='jack').count()
    1
    >>> manager.find().skip(1).limit(1).next()
    Doc(id=fecc8d4a41950c83e9010000)
   
    >>> for doc in manager.find().sort(friends=1):
    ...    print doc
    Doc(id=82cd8d4a41950c8fe9000000)
    Doc(id=82cd8d4a41950c8fe9010000)
    
And now sort on another key.
    
    >>> for doc in manager.find().sort(name=1):
    ...    print doc
    Doc(id=82cd8d4a41950c8fe9010000)
    Doc(id=82cd8d4a41950c8fe9000000)
    
### Document operations

A single document can be modified and afterwards saved without any 
restrictions. You can also delete the document, return its keys or
get a dict represntation.

    >>> manager.find_one(name='jack').keys()
    ['name', 'person']
    >>> doc = manager.find_one(name='jack')
    >>> doc.name = 'harry'
    >>> manager.save(doc)
    >>> manager.find_one(name='harry').name
    harry
    >>> manager.delete(doc)
    >>> manager.find_one(name='jack')
    None
