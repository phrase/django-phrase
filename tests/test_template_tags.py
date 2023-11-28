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
            """
            <script>
                window.PHRASEAPP_CONFIG = {
                    accountId: '',
                    projectId: '',
                    datacenter: '',
                    autoLowercase: false,
                    origin: 'django-phrase'
                };
                (function() {
                    var phrasejs = document.createElement('script');
                    phrasejs.type = 'module';
                    phrasejs.async = true;
                    phrasejs.src = 'https://d2bgdldl6xit7z.cloudfront.net/latest/ice/index.js'
                    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(phrasejs, s);
                })();
            </script>
            """,
        )
