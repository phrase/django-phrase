from django.template import (Node, Variable, TemplateSyntaxError, Library)
try:
    from django.template.base import render_value_in_context
except ImportError:
    from django.template.base import _render_value_in_context as render_value_in_context
from django.template.base import TOKEN_TEXT, TOKEN_VAR
from django.utils import six
from django.conf import settings

from phrase.utils import PhraseDelegate

class PhraseBlockTranslateNode(Node):
    def __init__(self, extra_context, singular, plural=None, countervar=None,
            counter=None, message_context=None, trimmed=None):
        self.extra_context = extra_context
        self.singular = singular
        self.plural = plural
        self.countervar = countervar
        self.counter = counter
        self.message_context = message_context
        self.trimmed = trimmed

    def render_token_list(self, tokens):
        result = []
        vars = []
        for token in tokens:
            if token.token_type == TOKEN_TEXT:
                result.append(token.contents)
            elif token.token_type == TOKEN_VAR:
                result.append('%%(%s)s' % token.contents)
                vars.append(token.contents)
        return ''.join(result), vars

    def render(self, context, nested=False):
        if self.message_context:
            message_context = self.message_context.resolve(context)
        else:
            message_context = None
        tmp_context = {}
        for var, val in self.extra_context.items():
            tmp_context[var] = val.resolve(context)
        # Update() works like a push(), so corresponding context.pop() is at
        # the end of function
        context.update(tmp_context)
        singular, vars = self.render_token_list(self.singular)
        if self.plural and self.countervar and self.counter:
            count = self.counter.resolve(context)
            context[self.countervar] = count
            plural, plural_vars = self.render_token_list(self.plural)
            if message_context:
                result = translation.npgettext(message_context, singular,
                                               plural, count)
            else:
                result = translation.ungettext(singular, plural, count)
            vars.extend(plural_vars)
        else:
            if message_context:
                result = translation.pgettext(message_context, singular)
            else:
                # result = translation.ugettext(singular)
                result = PhraseDelegate(singular, self.trimmed)
        default_value = settings.TEMPLATE_STRING_IF_INVALID
        render_value = lambda v: render_value_in_context(
            context.get(v, default_value), context)
        data = dict([(v, render_value(v)) for v in vars])
        context.pop()

        # FIX
        # try:
        #     result = result % data
        # except (KeyError, ValueError):
        #     if nested:
        #         # Either string is malformed, or it's a bug
        #         raise TemplateSyntaxError("'blocktrans' is unable to format "
        #             "string returned by gettext: %r using %r" % (result, data))
        #     with translation.override(None):
        #         result = self.render(context, nested=True)

        return result

class PhraseTranslateNode(Node):
    def __init__(self, filter_expression, noop, asvar=None,
                 message_context=None, trimmed=None):
        self.noop = noop
        self.asvar = asvar
        self.message_context = message_context
        self.filter_expression = filter_expression
        if isinstance(self.filter_expression.var, six.string_types):
            self.filter_expression.var = Variable("'%s'" %
                                                  self.filter_expression.var)
        self.trimmed = trimmed

    def render(self, context):
        self.filter_expression.var.translate = not self.noop
        if self.message_context:
            self.filter_expression.var.message_context = (
                self.message_context.resolve(context))
        output = self.filter_expression.resolve(context)
        value = render_value_in_context(output, context)
        if self.asvar:
            context[self.asvar] = PhraseDelegate(value, self.trimmed)
            return ''
        else:
            delegate = PhraseDelegate(self.filter_expression.var, self.trimmed)
            return delegate
