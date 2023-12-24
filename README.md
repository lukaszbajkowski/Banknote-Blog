# Banknote Blog

> Banknote blog is a responsive project based on Django and other technologies to create a blog dedicated to content
> related to coins and banknotes. An important aspect of the project is to give users the tools to create and share
> content with other members of the Banknote blog community using tools such as users becoming authors of content,
> commenting, sharing posts, mailing from multiple categories or writing posts and asking questions.

## Table of Contents

* [General Info](#general-information)
* [Test Account Information](#test-account-information)
* [Technologies Used](#technologies-used)
* [Features](#features)
* [Screenshots](#screenshots)
* [Setup](#setup)
* [Usage](#usage)
* [Project Status](#project-status)
* [Room for Improvement](#room-for-improvement)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)

## General Information

### Project Purpose

This repository serves the dual purpose of skill development and the creation of a practical mailing system. The main
objectives are:

1. **Skill Development:** Enhance programming skills, explore new technologies, and gain practical experience in
   software development.

2. **Mailing System:** Create a straightforward mailing system with essential functionalities for sending and managing
   emails.

### Custom Admin Panel

As part of the project, an original administrative panel has been developed. This panel not only provides necessary
functionalities but also presents them in a visually appealing and user-friendly graphical interface. The goal is to
offer an efficient and aesthetically pleasing administrative experience.

### Website Development

The project includes the creation of a dedicated website. The website is designed to capture interest with its unique
functionalities, catering to users who might consider implementing it as a final product. The features and design are
carefully crafted to make the site stand out and serve its intended audience effectively.

### Objectives Achieved

The project has successfully achieved the following milestones:

- **Programming Skills:** Significantly enhanced programming skills through practical application and problem-solving.
- **Mailing System Implementation:** Developed a basic yet functional mailing system for handling email-related tasks.
- **Custom Admin Panel:** Created a custom administrative panel with a rich graphical interface, offering essential
  features in an organized manner.
- **Website Development:** Designed and implemented a website with distinct functionalities, aimed at attracting users
  interested in its unique offerings.

Feel free to explore the repository, contribute, or use it as a reference for your own projects. Your feedback and
suggestions are always welcome!

## Test Account Information

For test purposes, you can use the following account credentials:

- **Login:** `admin`
- **Password:** `admin`

## Technologies Used

- **asgiref (3.6.0)**: ASGI (Asynchronous Server Gateway Interface) reference implementation, a specification for
  asynchronous web servers and applications.

- **certifi (2023.5.7)**: A Python package providing Mozilla's CA Bundle for certificate authorities.

- **cffi (1.15.1)**: A C Foreign Function Interface for Python. It provides a way for Python to call functions from
  shared libraries and use C data types.

- **charset-normalizer (3.2.0)**: A Python library for encoding detection and normalization.

- **cryptography (41.0.3)**: A library for secure communication and cryptography, including various algorithms and
  protocols.

- **defusedxml (0.7.1)**: A package that helps prevent common security issues related to XML processing.

- **distlib (0.3.6)**: A library that provides low-level utilities for working with Python distributions.

- **Django (4.1.7)**: A high-level web framework for Python that encourages rapid development and clean, pragmatic
  design.

- **django-allauth (0.55.0)**: A Django package that provides a set of authentication views, forms, and models for
  handling user authentication.

- **django-ckeditor (6.5.1)**: A Django integration for CKEditor, a WYSIWYG HTML editor.

- **django-js-asset (2.0.0)**: A Django app that integrates JavaScript assets.

- **django-phone-field (1.8.1)**: A Django model and form field for phone numbers.

- **django-phonenumber-field (7.0.2)**: A Django model and form field for international phone numbers.

- **django-ranged-response (0.2.0)**: A Django app for handling range headers.

- **django-recaptcha (3.0.0)**: A Django app for integrating Google reCAPTCHA.

- **django-remember-me (0.1.1)**: A Django app for implementing "Remember Me" functionality.

- **django-richtextfield (1.6.1)**: A Django app providing a rich text field for models.

- **filelock (3.9.0)**: A library that provides a platform-independent file lock.

- **idna (3.4)**: A library for handling Internationalized Domain Names in Applications (IDNA).

- **oauthlib (3.2.2)**: A generic and reusable Python implementation of OAuth 1.0, 1.0a, and 2.0.

- **phonenumberslite (8.13.9)**: A Python library for parsing, formatting, and validating international phone numbers.

- **Pillow (9.4.0)**: A powerful library for opening, manipulating, and saving many image file formats.

- **pip (23.3.1)**: The package installer for Python.

- **platformdirs (3.1.1)**: A Python module to access platform-specific directories (such as user data and configuration
  directories).

- **pycparser (2.21)**: A Python parser for the C language, useful for parsing C code.

- **PyJWT (2.8.0)**: A Python library for encoding and decoding JSON Web Tokens.

- **python3-openid (3.2.0)**: A set of Python modules for working with OpenID.

- **requests (2.31.0)**: A popular Python library for making HTTP requests.

- **requests-oauthlib (1.3.1)**: A Python library for OAuth support in requests.

- **setuptools (60.2.0)**: A package development process library designed to facilitate packaging Python projects.

- **sqlparse (0.4.3)**: A non-validating SQL parser for Python.

- **urllib3 (2.0.4)**: A powerful HTTP library for Python.

- **virtualenv (20.20.0)**: A tool to create isolated Python environments.

- **wheel (0.37.1)**: A binary package format for distributing Python libraries.

**Versions**:

- Python Version: 3.x
- Pillow Version: 9.4.0

*Make sure to use versions compatible with your project requirements.*

## Features

List the ready features:

- Blog section of the website.
- User panel.
- Content management.
- Administration part of the website.
- Different types of newsletters and newsletters with different types of messages and how to register for them.
- And many other features and additions.

More in development

## Screenshots

_Section currently being built_

[//]: # (![Banknote Blog]&#40;./public/lingo.mov&#41;)

## Setup

In this project, everything required to run and work with this project is included in the **package.json** file

### Windows System Configuration

If you are using a Windows system, you may encounter an issue where the `allauth.account.middleware.AccountMiddleware`
needs to be added to your Django project's `MIDDLEWARE` setting in the `settings.py` file.

Open your `settings.py` file and ensure that the following line is included in the `MIDDLEWARE` list:

```python
MIDDLEWARE = [
    # other middleware classes...
    'allauth.account.middleware.AccountMiddleware',
    # other middleware classes...
]
```

## Usage

To get started with the "Banknote-blog" project, follow these steps:

1. **Clone the repository**: Clone this repository to your computer using the following command:
   `https://github.com/lukaszbajkowski/Banknote-Blog.git`
2. **Navigate to the project directory**:
   `cd lingo`
3. **Install dependencies**: Use the following command to install all the required project dependencies:
   `pip install -r requirements.txt`
4. **Make migrations**:
   `python manage.py migrate`
5. **Run server**:
   `python manage.py runserver`
6. **Open your browser** and go to [127.0.0.1:8000](127.0.0.1:8000) to use the "Banknote-blog" application.
7. **Customize the project**: You can customize the project by editing components, styles, and adding your own features
   to meet your needs.

That's it! You are now ready to start working with the "Banknote Blog" project. Good luck!

## Project Status

Current status of the project: _in progress_

## Room for Improvement

At the moment, some image files need improvement. They do not all have the same extension. The extension of the project
logo needs to be changed to a file with the extension .svg. In addition, the frames for the animations contained in the
ScrollingSection need to be created in order to provide the right fluidity for them.

Room for improvement:

- Unification of image file extensions.
- Code optimisation and repair of minor errors.

To do:

- Creation of an English language version using rosetta
- Change from sqlite database to another.
- Development of tests.

## Acknowledgements

Credit is to be given to

- The layout of this project was inspired by [MrVintage](https://mrvintage.pl)

## Contact

Created by [@lukaszbajkowski](https://github.com/lukaszbajkowski) - feel free to contact me!
