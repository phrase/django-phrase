=============
django-phrase
=============

Phrase_ is the translation management solution for web and mobile applications. Collaborate with your team, find professional translators and stay on top of the process.

This adapter lets you connect your Django_ application to Phrase and integrate the powerful In-Context-Editor_ into your apps.

.. _Phrase: https://phrase.com
.. _Django: https://www.djangoproject.com
.. _In-Context-Editor: https://help.phrase.com/help/translate-directly-on-your-website

How does it work?
-----------------

django-phrase provides In-Context translating facilities to your Django app by hooking into i18n template tags.

It exposes the underlying key names to the In-Context Editor that is provided by Phrase.

To get started with Phrase you need to `sign up for a free account <https://phrase.com/signup>`_.


Installation
------------

Install the package with pip::

    pip install django-phrase

And add phrase to the list of installed apps::

    INSTALLED_APPS = (
        'phrase',
    )

You can now use the ``phrase_i18n`` template tag in your templates::

    {% load phrase_i18n %}

Note: You have to load ``phrase_i18n`` *after* you load ``ì18n`` in order to let ``phrase`` override the translation methods.

Last step: add the JavaScript snippet to your base layout file with the following tag. This should go inside the ``<head>`` section of your template file::

    {% phrase_javascript %}


Configuration
-------------

You can configure the In-Context Editor in your settings with these options::

    PHRASE_ENABLED = True
    PHRASE_ACCOUNT_ID = 'YOUR_ACCOUNT_ID'
    PHRASE_PROJECT_ID = 'YOUR_PROJECT_ID'
    PHRASE_PREFIX = '{{__'
    PHRASE_SUFFIX = '__}}'

**************
PHRASE_ENABLED
**************

Enable/Disable In-Context Editor completely and fall back to standard Django i18n handling. Always disable the In-Context Editor for production environments!

*****************
PHRASE_PROJECT_ID
*****************

Add your ProjectID. You find the Project ID on the `projects overview page <https://app.phrase.com/projects>`_.

*************
PHRASE_PREFIX
*************

Change the prefix and suffix of the keys that are rendered by the In-Context Editor. Default typically works great but this can conflict with some JavaScript liberaries. Use this setting to change prefix and suffix to custom ones if necessary.

********************
Heroku and .mo Files
********************

If you are using the current global gitignore file for python https://github.com/github/gitignore/blob/master/Python.gitignore be warned that your compiled .mo files are ignored as well. That means that your translations will not appear on Heroku. If you want this not to happen or having issues with this simply comment out your \*.mo ignore rule. Then run your compilemessages locally and include them into your sourcetree before pushing to Heroku.

More Information
----------------

* Signup_
* Documentation_
* Support_

.. _Signup: https://phrase.com/signup
.. _Documentation: https://help.phrase.com/
.. _Support: https://phrase.com/contact

## Get help / support

Please contact [support@phrase.com](mailto:support@phrase.com?subject=[GitHub]%20) and we can take more direct action toward finding a solution.


# django-phrase

![Build status](https://github.com/phrase/django-phrase/workflows/Test/badge.svg)

**django-phrase** is the official library for integrating [Phrase Strings In-Context Editor](https://support.phrase.com/hc/en-us/articles/5784095916188-In-Context-Editor-Strings) with [Django](https://www.djangoproject.com/)

## :scroll: Documentation

### Prerequisites

To use django-phrase with your application you have to:

* Sign up for a Phrase account: [https://app.phrase.com/signup](https://app.phrase.com/signup)
* Use the [Django](https://www.djangoproject.com/) framework for Python

### Demo

You can find a demo project in the `demo` folder, just run follow the `README.md` in that folder

### Installation

#### NOTE: You can not use the old version of the ICE with integration versions of >2.0.0, you have to instead use 1.x.x versions as before
#### via pip

```bash
pip install django-phrase
```

#### Configure

Add the following template snippets to your layout file `templates/base_generic.html` or equivalent

```
    {% load phrase_i18n %}
    {% phrase_javascript %}
```

And the following config to your `settings.py`

```py
    # Phrase In-Context Editor settings
    PHRASE_ENABLED = True
    PHRASE_ACCOUNT_ID = "YOUR_ACCOUNT_ID"  # Set your own account id
    PHRASE_PROJECT_ID = "YOUR_PROJECT_ID"  # Set your own project id
    PHRASE_DATACENTER = "eu"  # Choose your datacenter 'eu' | 'us'
    PHRASE_PREFIX = "{{__"
    PHRASE_SUFFIX = "__}}"
```

You can find the Project-ID in the Project overview in the PhraseApp Translation Center.
You can find the Account-ID in the Organization page in the PhraseApp Translation Center.

If this does not work for you, you can also integrate the [JavaScript snippet manually](https://help.phrase.com/help/integrate-in-context-editor-into-any-web-framework).

Old version of the ICE is not available since version 2.0.0. If you still would rather use the old version, please go back to 1.x.x versions.

#### Using the US Datacenter with ICE

In addition to the settings in your `settings.py`, set the US datacenter to enable the ICE to work with the US endpoints.
```py
    # Phrase In-Context Editor settings
    PHRASE_ENABLED = True
    PHRASE_ACCOUNT_ID = "YOUR_ACCOUNT_ID"  # Set your own account id
    PHRASE_PROJECT_ID = "YOUR_PROJECT_ID"  # Set your own project id
    PHRASE_DATACENTER = "us"  # Choose your datacenter 'eu' | 'us'
    PHRASE_PREFIX = "{{__"
    PHRASE_SUFFIX = "__}}"
```

### How does it work

When `PHRASE_ENABLED = True` this package modifies the returning values from translation functions to present a format which the ICE can read.

### Test

Run unit tests:

```bash
python manage.py test
```

## :white_check_mark: Commits & Pull Requests

We welcome anyone who wants to contribute to our codebase, so if you notice something, feel free to open a Pull Request! However, we ask that you please use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification for your commit messages and titles when opening a Pull Request.

Example: `chore: Update README`

## :question: Issues, Questions, Support

Please use [GitHub issues](https://github.com/phrase/django-phrase/issues) to share your problem, and we will do our best to answer any questions or to support you in finding a solution.

## :memo: Changelog

Detailed changes for each release are documented in the [changelog](https://github.com/phrase/django-phrase/releases).
