from phrase import settings as phrase_settings
from six import python_2_unicode_compatible
from six import text_type
import logging

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class PhraseDelegate:
    def __init__(self, name, trimmed=False):
        self.name = name
        self.trimmed = trimmed

    def __str__(self):
        logger.info("Rendering Phrase Key: %s" % (self.name))
        tmp_name = self.__normalized_name()
        return tmp_name

    def __normalized_name(self):
        normalized = "%sphrase_%s%s" % (
            phrase_settings.PHRASE_PREFIX,
            self.__safe_name(),
            phrase_settings.PHRASE_SUFFIX,
        )
        return normalized

    def __safe_name(self):
        name = self.__safer_name()
        name = name.strip()
        name = name.replace("<", "[[[[[[html_open]]]]]]")
        name = name.replace(">", "[[[[[[html_close]]]]]]")
        return name

    def __safer_name(self):
        if type(self.name) is text_type:
            return text_type(self.name)
        else:
            return text_type(self.name.literal)
