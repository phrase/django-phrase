# django-phrase

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

Add phrase to the list of installed apps::
```
    INSTALLED_APPS = (
        'phrase',
    )
```

Add the following template snippets to your layout file `templates/base_generic.html` or equivalent

```
    {% load phrase_i18n %}
    {% phrase_javascript %}
```

Then use `{% load phrase_i18n %}` in your templates, e.g. `demo/ice_demo/templates/index.html`

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
