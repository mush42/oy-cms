[![Build Status](https://travis-ci.org/mush42/oy-cms.svg?branch=master)](https://travis-ci.org/mush42/Oy-cms)

## Oy content management system

**Oy** is a lighweight, modular, and extensible content management system (CMS) based on the **Flask** micro-framework.

**oy** provides you with a flexible, full-fledged CMS engine with the following features:

* Makes use of some of the best flask extensions (Flask-Admin, Flask-SQLAlchemy...)
* A base **Page** model containing comprehensive metadata fields
* Pages are managed in a tree using nested sets which allows for faster querying for descendants and ancestors
* Routing to any page type is handled transparently using the familiar decorator syntax
* The ability to apply middlewares to modify page responses
* Model **Mixins**, alot of them, to easily build your custom content types
* Editable settings that users can edit in runtime (e.g, through the admin dashboard) which the developer can use in code or templates.
* An optional module system which augment **Flask Blueprints** with additional behavior

## Additional Features

In addition to the core, **oy** provides extra functionality through several packages under the **oy.contrib** package, including:

- * *oy.contrib.admin* providing the administration dashboard (based on Flask-Admin).
- **oy.contrib.media** manage user uploads (images, and documents) through an intuitive interface, and attach them to models  (uses the excellent file depot package).
- **oy.contrib.form** easily design forms and publilsh them as pages, and view and download  submissions through the admin
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
Creating project mysite...
Using project template: /home/.../oy/project_templates/default...

.........................

New project created at /home/projects/mysite
```

Then cd to the project directory and create the database with some demo content:

```bash
cd mysite
oy createall
```

```bash
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Creating database tables...
Database tables created.
Creating a new super user account...

super User created successfully.


^^^^^^^^^^^^^^^^^^^^^^^^
Superuser account details: (username=admin) (password=adminpass)
please change the default password
^^^^^^^^^^^^^^^^^^^^^^^^

Installing fixtures in the database
~~~~~~~~~~~~~~~~~

Installing fixtures for module: oy.contrib.form
Installing fixtures for module: oy.contrib.demo_content
Installing fixtures for module: my.home_page

===============
Finished installing all available fixtures.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
```

Finally run the server:

```bash
$ flask run
```

Then visit your newly created site at  [http://127.0.0.1:5000](http://127.0.0.1:5000) you will be greeted with the default home page. To edit the site content visit the administration dashboard at [http://127.0.0.1:5000/admin/](http://127.0.0.1:5000/admin/) and use the default account details: username=admin, password=adminpass.

## Why is it called **oy**?

I thought you already know. But in case you don't, here is a hint:

> The Midwest, a deserted village, an already dead boy, another junky boy, a black woman with two faces, and a serious man whom you don't want to mess with.


## Contributing

**oy** content management system is still in alpha status, contributions are more than wellcome. Help needed in perfecting existing features as well as adding new ones.
