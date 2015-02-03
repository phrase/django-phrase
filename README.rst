=============
django-phrase
=============

PhraseApp_ makes it easy and fast to localize you mobile app or website.

This adapter lets you connect your Django_ application to PhraseApp and integrate the powerful In-Context-Editor_ into your apps.

.. _PhraseApp: https://phraseapp.com
.. _Django: https://www.djangoproject.com
.. _In-Context-Editor: https://phraseapp.com/features/context-view

How does it work?
-----------------

django-phrase provides In-Context translating facilities to your Django app by hooking into `i18n template tags`_.

It exposes the underlying key names to the javascript editor that is provided by PhraseApp.

To get started with PhraseApp you need to `sign up for a free account <https://phraseapp.com/signup>`_.


Installation
------------

Install the package with pip::

    pip install django-phrase

And add phrase to the list of installed apps::

    INSTALLED_APPS = (
        'phrase',
    )

Usage for In-Context Translation
--------------------------------

You can now use the ``phrase_i18n`` template tag in your templates::

    {% load phrase_i18n %}

Note: You have to load ``phrase_i18n`` *after* you load ``ì18n`` in order to let phrase override the translation methods.

Last step: add the javascript snippet to your base layout file with the folling tag. This should go inside the ``<head>`` section of your template file::

    {% phrase_javascript %}


Usage for Production & Continuous Integration Environments
----------------------------------------------------------

In production or continuous integration environments the In-Context facility are not suitable, instead the app provides two management commands, 
allowing you the sync the keys found in the app with PhraseApp and downloading & compiling existing translations from PhraseApp.

*********************
./manage.py sync_keys
*********************

Allows you to sync the keys found in the app with the PhraseApp translation key database. It uses the same logic as ``makemessages`` to locate all keys 
in your app (and therefore takes the same parameters). By providing the `-p` option it will only add new keys to PhraseApp while without it obsolete keys will be removed.

*****************************
./manage.py pull_translations
*****************************

Allows you to download and compile (by passing the `-c` option) translations from PhraseApp and make them readily available to your app.

Configuration
-------------

You can configure PhraseApp in your settings with these default options::

    PHRASE_ENABLED = True
    PHRASE_AUTH_TOKEN = 'YOUR_AUTH_TOKEN'
    PHRASE_PREFIX = '{{__'
    PHRASE_SUFFIX = '__}}'

**************
PHRASE_ENABLED
**************

Enable/Disable In-Context-Editing completely and fall back to standard Django i18n handling. Disable PhraseApp for production environments at any time!

*****************
PHRASE_AUTH_TOKEN
*****************

Add your project auth token. You find your project auth token on the `project overview page <https://phraseapp.com/projects>`_.

*************
PHRASE_PREFIX
*************

Change the prefix and suffix of the keys that are rendered by PhraseApp. Default typically works great but this can conflict with some JavaScript liberaries. Use this setting to change prefix and suffix to custom ones if necessary.

********************
Heroku and .mo Files
********************

If you are using the current global gitignore file for python https://github.com/github/gitignore/blob/master/Python.gitignore be warned that your compiled .mo files are ignored as well. That means that your translations will not appear on Heroku. If you want this not to happen or having issues with this simply comment out your *.mo ignore 
rule. Then run your compilemessages locally and include them into your sourcetree before pushing to Heroku.

More Information
----------------

* Signup_
* Documentation_
* Support_

.. _i18n template tags: https://docs.djangoproject.com/en/1.5/topics/i18n/translation/#internationalization-in-template-code
.. _Signup: https://phraseapp.com/docs
.. _Documentation: https://phraseapp.com/docs
.. _Support: https://phraseapp.com/support
