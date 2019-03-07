[![Build Status](https://travis-ci.org/mush42/oy-cms.svg?branch=master)](https://travis-ci.org/mush42/oy-cms)

## Oy content management system

**Oy** is a lightweight, modular, and extensible content management system (CMS) based on the **Flask** micro-framework.

**Oy** provides you with a flexible, full-fledged CMS engine, without hiding away the elegant Flask API behind a custom facade.

**oy** implements the following content management features:

* A base **Page** model containing comprehensive metadata fields
* Pages are managed in a tree using nested sets which allows for faster traversal of the page tree
* Routing to any page type is handled transparently using the familiar decorator syntax
* The ability to apply middlewares to modify page responses
* A wide range of **Model Mixins** to easily build custom content types
* Editable settings that users can edit in runtime (e.g, through the admin dashboard) which the developer/designer can use in code or templates.
* An optional module system which augment **Flask Blueprints** with additional behavior
* Makes perfect use of some of the best flask extensions (Flask-Admin, Flask-SQLAlchemy, Flask-Security..etc.)

## Core Extensions

Building on the top of this powerful core, **oy** provides most of it's functionality via **contrib packages** which use the familiar  flask extension API.

Extensions under the **oy.contrib** package supplies you with the following additional features:

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

**Oy** provides the **oyinit** command to help you scaffold your new projects. To create a project with the default template, navigate to your projects directory and run:

```bash
$ oyinit mysite
```

```bash

Creating a new project called `mysite` from `...`
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
User account details: the username is: admin and the password is the chosen password
Please change the default password.
^^^^^^^^^^^^


Adding some demo data to the database
~~~~~~~~~~~~

Adding demo data from module: oy.contrib.media
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

## Development

To develop oy locally, first clone the repo:

```bash
$ git clone https://github.com/mush42/oy-cms.git
$ cd oy-cms
```

Create a virtual environment and install the required packages from PYPI:

```bash
$ virtualenv .venv
$ source .venv/bin/activate
$ pip install -r requirements-dev.txt
```
 
Then cd to the frontend directory and install the frontend components:

```bash
$ cd frontend
$ yarn install
# or if you don't have yarn installed
$ npm install
```

Static assets are not pushed to the repository because they are generated automatically using **gulp**

Install gulp-cli globally, and then use gulp to build and copy the static files:

```bash
# install the gulp command line interface globally
$ yarn global add gulp-cli
# or if you don't have yarn installed
$ npm -g -i gulp-cli

# Then build and copy the static assets
$ gulp clean
$ gulp build
$ gulp copy
```
 
Finally install **oy** in editable mode:

```bash
$ cd ..
$ pip install -e .
```

## Contributing

**oy** content management system is still in _alpha status_, contributions are more than wellcome. Help is needed in perfecting existing features as well as adding new ones.

Currently we are workon on the following areas:

* Increasing test coverage
* Implementing a RESTFUL API with sensible defaults
* Migrating the **Gutenberg** block editor to oy in order for it to be used  as the default rich-text widget
* Using **React.js** to implement some admin widgets (inline fields, image and document choosers...etc)
* Translations (i18n)

## Why is it called **oy**?

We thought you already know. But in case you don't, here is a hint:

> The Midwest, a deserted village, an already dead boy, a junky teenager, a black woman with two faces, and a serious man whom you don't want to mess with.

## Licence

**Oy CMS** is copyright (c) 2019 Musharraf Omer and oy contributers. It is licenced under the [MIT License](https://github.com/mush42/oy-cms/blob/master/LICENSE).
