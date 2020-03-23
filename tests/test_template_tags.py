from django.template import Context, Template
from django.test import TestCase


def render_template(content, **context_args):
    """Create a template that loads the `phrase_i18n` tags and adds the given content."""
    template = Template("{% load phrase_i18n %}" + content)
    return template.render(Context(context_args))


class TemplateTagsTest(TestCase):
    """Test all template tags."""

    def test_empty_template(self):
        self.assertEqual(render_template(""), "")

    def test_phrase_javascript(self):
        self.assertHTMLEqual(
            render_template("{% phrase_javascript %}"),
            """<script>
    window.PHRASEAPP_CONFIG = {
        projectId: '',
        autoLowercase :false,
        };
    (function() {
    var phrasejs = document.createElement('script');
    phrasejs.type = 'text/javascript';
    phrasejs.async = true;
    phrasejs.src = ['https://', 'phraseapp.com/assets/in-context-editor/2.0/app.js?', new Date().getTime()].join('');
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(phrasejs, s);     })();
    </script>""",
        )
