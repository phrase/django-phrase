from phrase import settings as phrase_settings
from django.utils.encoding import python_2_unicode_compatible

import logging

logger = logging.getLogger(__name__)

@python_2_unicode_compatible
class PhraseDelegate:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        logger.info("Rendering PhraseApp Key: %s" % (self.name))
        return self.__normalized_name()

    def __normalized_name(self):
        normalized = "%sphrase_%s%s" % (phrase_settings.PHRASE_PREFIX, self.__safe_name(), phrase_settings.PHRASE_SUFFIX)
        return normalized

    def __safe_name(self):
        name = self.name
        name = str(name.literal)
        name = name.replace("<", "[[[[[[html_open]]]]]]")
        name = name.replace(">", "[[[[[[html_close]]]]]]")
        return name
