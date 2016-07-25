=============
django-phrase
=============

PhraseApp_ is the translation management solution for web and mobile applications. Collaborate with your team, find professional translators and stay on top of the process.

This adapter lets you connect your Django_ application to PhraseApp and integrate the powerful In-Context-Editor_ into your apps.

.. _PhraseApp: https://phraseapp.com
.. _Django: https://www.djangoproject.com
.. _In-Context-Editor: https://phraseapp.com/docs/guides/in-context-editor

How does it work?
-----------------

django-phrase provides In-Context translating facilities to your Django app by hooking into i18n template tags.

It exposes the underlying key names to the In-Context Editor that is provided by PhraseApp.

To get started with PhraseApp you need to `sign up for a free account <https://phraseapp.com/signup>`_.


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

Add your ProjectID. You find the Project ID on the `projects overview page <https://phraseapp.com/projects>`_.

*************
PHRASE_PREFIX
*************

Change the prefix and suffix of the keys that are rendered by the In-Context Editor. Default typically works great but this can conflict with some JavaScript liberaries. Use this setting to change prefix and suffix to custom ones if necessary.

********************
Heroku and .mo Files
********************

If you are using the current global gitignore file for python https://github.com/github/gitignore/blob/master/Python.gitignore be warned that your compiled .mo files are ignored as well. That means that your translations will not appear on Heroku. If you want this not to happen or having issues with this simply comment out your *.mo ignore rule. Then run your compilemessages locally and include them into your sourcetree before pushing to Heroku.

More Information
----------------

* Signup_
* Documentation_
* Support_

.. _Signup: https://phraseapp.com/signup
.. _Documentation: https://phraseapp.com/docs
.. _Support: https://phraseapp.com/contact
