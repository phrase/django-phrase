from django import template
from django.template import (Node, Variable, TemplateSyntaxError, Library)
from django.template.base import Parser as TokenParser
from django.template.base import TOKEN_TEXT, TOKEN_VAR
from django.template.defaulttags import token_kwargs
from django.conf import settings
from django.utils import translation
from django.utils.html import mark_safe
from django.templatetags.i18n import BlockTranslateNode, TranslateNode

from phrase import settings as phrase_settings
from phrase.nodes import PhraseBlockTranslateNode, PhraseTranslateNode

import logging
import re

register = template.Library()

@register.tag("trans")
def do_translate(parser, token):
    """
    This will mark a string for translation and will
    translate the string for the current language.
    Usage::
        {% trans "this is a test" %}
    This will mark the string for translation so it will
    be pulled out by mark-messages.py into the .po files
    and will run the string through the translation engine.
    There is a second form::
        {% trans "this is a test" noop %}
    This will only mark for translation, but will return
    the string unchanged. Use it when you need to store
    values into forms that should be translated later on.
    You can use variables instead of constant strings
    to translate stuff you marked somewhere else::
        {% trans variable %}
    This will just try to translate the contents of
    the variable ``variable``. Make sure that the string
    in there is something that is in the .po file.
    It is possible to store the translated string into a variable::
        {% trans "this is a test" as var %}
        {{ var }}
    Contextual translations are also supported::
        {% trans "this is a test" context "greeting" %}
    This is equivalent to calling pgettext instead of (u)gettext.
    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument" % bits[0])
    message_string = parser.compile_filter(bits[1])
    remaining = bits[2:]

    noop = False
    asvar = None
    message_context = None
    seen = set()
    invalid_context = {'as', 'noop'}

    while remaining:
        option = remaining.pop(0)
        if option in seen:
            raise TemplateSyntaxError(
                "The '%s' option was specified more than once." % option,
            )
        elif option == 'noop':
            noop = True
        elif option == 'context':
            try:
                value = remaining.pop(0)
            except IndexError:
                msg = "No argument provided to the '%s' tag for the context option." % bits[0]
                six.reraise(TemplateSyntaxError, TemplateSyntaxError(msg), sys.exc_info()[2])
            if value in invalid_context:
                raise TemplateSyntaxError(
                    "Invalid argument '%s' provided to the '%s' tag for the context option" % (value, bits[0]),
                )
            message_context = parser.compile_filter(value)
        elif option == 'as':
            try:
                value = remaining.pop(0)
            except IndexError:
                msg = "No argument provided to the '%s' tag for the as option." % bits[0]
                six.reraise(TemplateSyntaxError, TemplateSyntaxError(msg), sys.exc_info()[2])
            asvar = value
        else:
            raise TemplateSyntaxError(
                "Unknown argument for '%s' tag: '%s'. The only options "
                "available are 'noop', 'context' \"xxx\", and 'as VAR'." % (
                    bits[0], option,
                )
            )
        seen.add(option)

    if phrase_settings.PHRASE_ENABLED:
        return PhraseTranslateNode(message_string, noop, asvar, message_context)
    else:
        return TranslateNode(message_string, noop, asvar, message_context)

@register.tag("blocktrans")
def do_block_translate(parser, token):
    bits = token.split_contents()

    options = {}
    remaining_bits = bits[1:]
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option in options:
            raise TemplateSyntaxError('The %r option was specified more than once.' % option)
        if option == 'with':
            value = token_kwargs(remaining_bits, parser, support_legacy=True)
            if not value:
                raise TemplateSyntaxError('"with" in %r tag needs at least one keyword argument.' % bits[0])
        elif option == 'count':
            value = token_kwargs(remaining_bits, parser, support_legacy=True)
            if len(value) != 1:
                raise TemplateSyntaxError('"count" in %r tag expected exactly one keyword argument.' % bits[0])
        elif option == "context":
            try:
                value = remaining_bits.pop(0)
                value = parser.compile_filter(value)
            except Exception:
                msg = ('"context" in %r tag expected exactly one argument.') % bits[0]
                six.reraise(TemplateSyntaxError, TemplateSyntaxError(msg), sys.exc_info()[2])
        elif option == "trimmed":
          value = True
        else:
            raise TemplateSyntaxError('Unknown argument for %r tag: %r.' % (bits[0], option))
        options[option] = value

    trimmed = options.get("trimmed", False)

    if 'count' in options:
        countervar, counter = list(six.iteritems(options['count']))[0]
    else:
        countervar, counter = None, None
    if 'context' in options:
        message_context = options['context']
    else:
        message_context = None

    extra_context = options.get('with', {})

    singular = []
    plural = []
    while parser.tokens:
        token = parser.next_token()
        if token.token_type in (TOKEN_VAR, TOKEN_TEXT):
            singular.append(token)
        else:
            break
    if countervar and counter:
        if token.contents.strip() != 'plural':
            raise TemplateSyntaxError("'blocktrans' doesn't allow other block tags inside it")
        while parser.tokens:
            token = parser.next_token()
            if token.token_type in (TOKEN_VAR, TOKEN_TEXT):
                plural.append(token)
            else:
                break
    if token.contents.strip() != 'endblocktrans':
        raise TemplateSyntaxError("'blocktrans' doesn't allow other block tags (seen %r) inside it" % token.contents)

    if phrase_settings.PHRASE_ENABLED:
        node = PhraseBlockTranslateNode(extra_context, singular, plural, countervar, counter, message_context, trimmed)
    else:
        node = BlockTranslateNode(extra_context, singular, plural, countervar, counter, message_context, trimmed=trimmed)

    return node

@register.simple_tag
def phrase_javascript():
    if not phrase_settings.PHRASE_ENABLED:
        return ''
    html = """<script>
    window.PHRASEAPP_CONFIG = {
        projectId: '%(project_id)s',
        autoLowercase :false,
        };
    (function() {
    var phrasejs = document.createElement('script');
    phrasejs.type = 'text/javascript';
    phrasejs.async = true;
    phrasejs.src = ['%(protocol)s', '%(host)s/assets/in-context-editor/2.0/app.js?', new Date().getTime()].join('');
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(phrasejs, s); \
    })();
    </script>"""
    formatted_html = html % dict(
        project_id=phrase_settings.PHRASE_PROJECT_ID,
        protocol='https://' if phrase_settings.PHRASE_JS_USE_SSL else 'http://',
        host=phrase_settings.PHRASE_JS_HOST,
        )
    return mark_safe(formatted_html)
