import json
from optparse import make_option
import os
import urllib
import urllib2

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    args = ''
    help = 'Pull all or the specified locales translation from PhraseApp'

    option_list = BaseCommand.option_list + (
        make_option('-l', '--locale', dest='locale', help='Pull only the specified locales translation'),
        make_option('-c', '--compile', action='store_true', dest='compile', default=False, help='Compile translations after pulling them'),
    )

    @staticmethod
    def _make_request(endpoint, data={}, method="GET", needs_decoding=True):
        """Helper method to query the PhraseApp API"""
        try:
            # compute parameters
            params = {'auth_token': settings.PHRASE_AUTH_TOKEN}
            params.update(data)
            if method == "GET":
                request = urllib2.Request("https://phraseapp.com/api/v1/" + endpoint + "?" + urllib.urlencode(params))
            else:
                request = urllib2.Request("https://phraseapp.com/api/v1/" + endpoint, data=urllib.urlencode(params))
            response = urllib2.urlopen(request)
            if needs_decoding:
                return json.loads(response.read())
            else:
                return response.read()
        except:
            raise CommandError("Failure during communication with PhraseApp API. Please check your PHRASE_AUTH_TOKEN setting.")

    @staticmethod
    def _pull_translation(locale):
        """Helper method downloading one locales translation from PhraseApp and updating the appropriate gettext file"""

        # retrieve it
        data = Command._make_request("translations/download.po", {'locale': locale}, needs_decoding=False)

        # locate its folder
        if len(settings.LOCALE_PATHS) == 0:
            raise CommandError("No locale paths defined. Please set LOCALE_PATHS in your Django settings.")

        locale_folder = os.path.join(settings.LOCALE_PATHS[0], locale, "LC_MESSAGES")
        if not os.path.exists(locale_folder):
            os.makedirs(locale_folder)

        # store it
        with open(os.path.join(locale_folder, "django.po"), "w+") as gettext_file:
            gettext_file.write(data)

    def handle(self, *args, **options):
        project_locales = [locale['code'] for locale in self._make_request("locales")]

        if not options['locale'] is None:
            # check if specified locale exists
            if not options['locale'] in project_locales:
                raise CommandError("Specified locale '%s' not found in project." % options['locale'])

            self._pull_translation(options['locale'])

            self.stdout.write('Successfully pulled translation for locale "%s"' % options['locale'])
        else:
            i = 1
            for locale in project_locales:
                self._pull_translation(locale)
                self.stdout.write('Successfully pulled translation for locale "%s" [%d/%d]' % (locale, i, len(project_locales)))

                i = i + 1

        if options['compile']:
            if options['locale']:
                call_command('compilemessages', locale=options['locale'])
            else:
                call_command('compilemessages')
