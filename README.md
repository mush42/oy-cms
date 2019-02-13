[![Build Status](https://travis-ci.org/mush42/oy-cms.svg?branch=master)](https://travis-ci.org/mush42/Oy-cms)

## Oy content management system

**Oy** is a lightweight, modular, and extensible content management system (CMS) based on the **Flask** micro-framework.

**oy** provides you with a flexible, full-fledged CMS engine with the following features:

* A base **Page** model containing comprehensive metadata fields
* Pages are managed in a tree using nested sets which allows for faster querying for descendants and ancestors
* Routing to any page type is handled transparently using the familiar decorator syntax
* The ability to apply middlewares to modify page responses
* Model **Mixins**, a lot of them, to easily build your custom content types
* Editable settings that users can edit in runtime (e.g, through the admin dashboard) which the developer can use in code or templates.
* An optional module system which augment **Flask Blueprints** with additional behavior
* Makes use of some of the best flask extensions out there (Flask-Admin, Flask-SQLAlchemy, Flask-Security...)

## Additional Features

In addition to the core, **oy** provides extra functionality through several packages under the **oy.contrib** package, including:

- * *oy.contrib.admin* providing the administration dashboard (based on Flask-Admin).
- **oy.contrib.media** manage user uploads (images, and documents) through an intuitive interface, and attach them to models  (uses the excellent file depot package).
- **oy.contrib.form** easily design forms and publish them as pages, and view and download  submissions through the admin
- **oy.contrib.redirects** setup custom redirects
- **oy.contrib.users** provides user management with an extensible user profiles.


## Quick Start

First things first, install **oy** via pip:

```bash
$ pip install oy
```

**Oy** supplies you with a command to scaffold your projects. To create a project with the default template, navigate to your projects directory and run:

```bash
$ oyinit mysite
```

```bash

Creating a new project called `mysite`
Using project template: default.
~~~~~~~~~~~~
New project created at /home/projects/mysite

```

Then cd to the project directory and create the database with some demo content:

```bash
$ cd mysite
$ oy createall
```

```bash

~~~~~~~~~~~~
Creating database tables...
Database tables created.
Creating a new super user account...

super User created successfully.


^^^^^^^^^^^^
Superuser account details: username=admin, password=adminpass
Please change the default password.
^^^^^^^^^^^^

Adding some demo data to the database
~~~~~~~~~~~~

Adding demo data from module: oy.contrib.form
Adding demo data from module: oy.contrib.demo_content
Adding demo data from module: mysite.home_page

============
Finished adding all available demo data.
~~~~~~~~~~~~

```

Finally run the server:

```bash
$ flask run
```

Then visit your newly created site at  [http://127.0.0.1:5000](http://127.0.0.1:5000) you will be greeted with the default home page. To edit the site content visit the administration dashboard at [http://127.0.0.1:5000/admin/](http://127.0.0.1:5000/admin/) and use the default account details: username=admin, password=adminpass.

## Why is it called **oy**?

I thought you already know. But in case you don't, here is a hint:

> The Midwest, a deserted village, an already dead boy, a junky teenager, a black woman with two faces, and a serious man whom you don't want to mess with.


## Contributing

**oy** content management system is still in _alpha status_, contributions are more than wellcome. Help needed in perfecting existing features as well as adding new ones.

Help is needed in the following areas:

* Fixing minor css regressions in the admin frontend
* Increasing test coverage
* Implementing a RESTFUL API with sensible defaults
* Migrating the **Gutenberg** block editor to be used as the default rich-text widget
* Using a modren javascript framework to implement some admin widgets (inline fields, image and document choosers...etc)
* Translations (i18n)
