from django import template
from django.template import (Node, Variable, TemplateSyntaxError, TokenParser, Library, TOKEN_TEXT, TOKEN_VAR)
from django.template.defaulttags import token_kwargs
from django.conf import settings
from django.utils import translation
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
    class TranslateParser(TokenParser):
        def top(self):
            value = self.value()

            # Backwards Compatiblity fix:
            # FilterExpression does not support single-quoted strings,
            # so we make a cheap localized fix in order to maintain
            # backwards compatibility with existing uses of ``trans``
            # where single quote use is supported.
            if value[0] == "'":
                m = re.match("^'([^']+)'(\|.*$)", value)
                if m:
                    value = '"%s"%s' % (m.group(1).replace('"','\\"'), m.group(2))
                elif value[-1] == "'":
                    value = '"%s"' % value[1:-1].replace('"','\\"')

            noop = False
            asvar = None
            message_context = None

            while self.more():
                tag = self.tag()
                if tag == 'noop':
                    noop = True
                elif tag == 'context':
                    message_context = parser.compile_filter(self.value())
                elif tag == 'as':
                    asvar = self.tag()
                else:
                    raise TemplateSyntaxError(
                        "Only options for 'trans' are 'noop', " \
                        "'context \"xxx\"', and 'as VAR'.")
            return value, noop, asvar, message_context

    value, noop, asvar, message_context = TranslateParser(token.contents).top()

    if phrase_settings.PHRASE_ENABLED:
        node = PhraseTranslateNode(parser.compile_filter(value), noop, asvar, message_context)
    else:
        node = TranslateNode(parser.compile_filter(value), noop, asvar, message_context)

    return node

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
        else:
            raise TemplateSyntaxError('Unknown argument for %r tag: %r.' % (bits[0], option))
        options[option] = value

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
        node = PhraseBlockTranslateNode(extra_context, singular, plural, countervar, counter, message_context)
    else:
        node = BlockTranslateNode(extra_context, singular, plural, countervar, counter, message_context)

    return node

@register.simple_tag
def phrase_javascript():
    protocol = 'https://' if phrase_settings.PHRASE_JS_USE_SSL else 'http://'
    host = phrase_settings.PHRASE_JS_HOST
    html = "\
<script>\
  var phrase_auth_token = '"+phrase_settings.PHRASE_AUTH_TOKEN+"';\
  (function() {\
    var phraseapp = document.createElement('script'); phraseapp.type = 'text/javascript'; phraseapp.async = true;\
    phraseapp.src = ['"+protocol+"', '"+host+"/assets/phrase/0.1/app.js?', new Date().getTime()].join('');\
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(phraseapp, s);\
  })();\
</script>\
"
    return html
