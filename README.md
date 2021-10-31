# Library μService
A Python version of the [library service](https://github.com/vinceynhz/library-service) leveraging Flask.

The purpose of this service is to provide simple access to the database that will host all of the library related 
entities.

## Content
- [Installing](#installing)
- [Data Model](#data-model)

## Installing

This project uses virtual environments. After cloning repo run

```
make dev-init
```

This will setup the local virtual environment, activate it, install requirements and
install the current project as a dependency as well.

For new sessions on the command line, the following can be run:

```
make dev
```

This enables the virtual environment for development

To run testing
```
make test
```

For prod install
```
make init
```

To run the application using gunicorn (available in the virtual environment)
```
make run
```

## Data Model

The purpose of this document is to describe the list of all concepts related to the data definition, access and usage

## Definitions

The following definitions are applicable throughout the whole system:

- **[book](https://en.wikipedia.org/wiki/Book):** a medium that represents information in the form of writing, images, a 
verbal narration or a combination of them.

- **book format:** the kind of physical existence of a book. We differentiate the following formats: 
  - **_hardback_**
  - **_paperback_**
  - **_ebook_**
  - **_audiobook_**
  
- **book features:** optional characteristics of a book that make a difference among other copies of the 
relative same book. A book may contain 0 or more features. The features we identify are:
  - **_[graphic novel](https://en.wikipedia.org/wiki/Graphic_novel):_** we encompass single periodical issues as well as
  collected editions 
  - **_[anthology](https://en.wikipedia.org/wiki/Anthology):_** a collection of literary works
  - **_revised edition:_** a new version of a book previously published by the same author with additional or modified 
  content from the original edition
  - **_complete edition:_** a new version of a book that includes material not included in previous versions  
  - **_illustrated:_** a special version with illustrations of a book previously published only in writing. Note that 
  this is different than children's books tha are _created_ to have illustrations.   
  - **_variant cover:_** a special version of a book with a cover made by a particular artist; this is mostly applicable
  in graphic novels
  - **_large print:_** a special version of a book with a larger lettering for ease of readability
  
- **book language:** the language in which a specific book is written into. This may not correspond to the or

- **contributor:** a being (human or otherwise) that worked actively in the creation of a _book_. We claim a difference 
in the process of book _creation_ to that of book _production_. As part of the book creation we consider the following 
contributors:
  - **_authors_** 
  - **_illustrators_**
  - **_editors_** (only when many editors may have created different versions of the original manuscript)
  - **_translators_** (only when the translations provide significant differences from the original book)

- **[library](https://en.wikipedia.org/wiki/Library):** a collection of books belonging to a user or group of users

- **user:** a being (human or otherwise) partaking in the interactions of the present system

- **catalog:** a sorted list of entities in the system (books, contributors, users, libraries)

## Authority Control

Although the concept sounds overly strict and sober, it refers to transformations done to the attributes of an entity to
ease with the cataloguing of library materials ([ref](https://en.wikipedia.org/wiki/Authority_control)).

We consider the following rules:

### Capitalization:

The capitalization of a word occurs in the following manner:

1. If the given word contains two or more upper case letters (such as the case of acronyms or initials) the word will be
left as is with no changes
2. If the word is a valid roman numeral the word will be converted to upper case
3. Articles will be converted to lower case (unless of the special case of the first word of a book title)
4. Finally, the first alphabetical character of the word will be converted to upper case, the rest to lower case

The articles recognized currently are those of the English language: `"a"`, `"an"`, `"of"`, `"the"`, `"is"`, `"in"` and
`"to"`.

### Uniform Title

The [uniform title](https://en.wikipedia.org/wiki/Uniform_title) of a book is determined by capitalizing each word in 
the title.

If the first word on a book title is an article, this will be capitalized regardless of the rule previously defined in
the capitalization flow described above.

### Uniform Name

The uniform name of a contributor is determined by the capitalization of each word in the contributors name. Please note
that honorific are preserved in this form. In this sense the following hypothetical contributors reflect 
separate beings:

* Dr. Helen Boingrad
* Helen Boingrad III
* Helen Boingrad 

### Contributor Uniqueness

A contributor is uniquely identified in the system by:

- uniform name

### Book Uniqueness

A book is uniquely identified by:

- uniform title
- format
- contributors
- features (if any)
- language (if any)

### Cataloguing

Within the system, books and contributors should be searchable and organizable according to a simplified version of the
cataloguing rules.

In the case of books:

- the book title is normalized to remove any non alphanumeric characters and set to lowercase
- if the first word of the title is one of these articles: `a`, `an`, `the`, it is ignored

In the case of contributors:
 
- name is normalized to remove any non alphanumeric characters, honorifics and roman numerals
- first word is considered last in the order of words that integrate a name. For example:
  
  - `Neil deGrasse Tyson` is catalogued as `degrasse tyson, neil`
  - `Mary Higgins Clark` is catalogued as `higgins clark, mary`
  - `Sir Arthur Conan Doyle` is catalogued as `conan doyle, arthur`
  
## ERD

The following entities are defined in the data model for this service.

![ERD](https://raw.githubusercontent.com/vinceynhz/library-service/master/doc/ERD.png)

### Relationships

Please note that referential integrity is not enforced by the service. For simplicity of the application and for the 
matter of exercise, the relationships between entities is left for the client application and/or the front end to
implement, validate and guarantee. 

WIP: API documentation

The following relationships are recognized by the model:
 
#### Books by Contributor

- One book can have many contributors
- One contributor can have many books

Ideally, the sha256 unique id should be used to match records

### Contributor alias

- One contributor can have many aliases
