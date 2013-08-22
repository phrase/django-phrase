import fnmatch
import httplib
import json
from optparse import make_option
import os
import urllib
import re
import sys
from subprocess import PIPE, Popen

from polib import pofile

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    args = ''
    help = ("Runs over the entire source tree of the current directory, pulls out all strings marked for translation and updates the PhraseApp keys database.\n\nYou must run this command with one of either the --locale or --all options.")

    option_list = BaseCommand.option_list + (
        make_option('--push-only','-p', action='store_true', dest='push_only', default=False, help='Only push new keys and do not delete no longer used ones'),
        make_option('--domain', '-d', dest='domain', default='django', help='The domain of the message files (default: "django").'),
        make_option('--extension', '-e', action='append', dest='extensions', help='The file extension(s) to examine (default: "html,txt", or "js" if the domain is "djangojs"). Separate multiple extensions with commas, or use -e multiple times.'),
        make_option('--symlinks', '-s', action='store_true', dest='symlinks', default=False, help='Follows symlinks to directories when examining source code and templates for translation strings.'),
        make_option('--ignore', '-i', action='append', dest='ignore_patterns', default=[], metavar='PATTERN', help='Ignore files or directories matching this glob-style pattern. Use multiple times to ignore more.'),
        make_option('--no-default-ignore', action='store_false', dest='use_default_ignore_patterns', default=True, help="Don't ignore the common glob-style patterns 'CVS', '.*' and '*~'."),
        make_option('--username', dest='phraseapp_username', help="The PhraseApp username for deleting keys."),
        make_option('--password', dest='phraseapp_password', help="The PhraseApp password for deleting keys."),
    )

    @staticmethod
    def _make_request(endpoint, data={}, method="GET", needs_decoding=True, user_auth_token=None):
        """Helper method to query the PhraseApp API"""
        # compute parameters
        params = {'auth_token': settings.PHRASE_AUTH_TOKEN} if user_auth_token is None else {'auth_token': user_auth_token, 'project_auth_token': settings.PHRASE_AUTH_TOKEN}
        params.update(data)

        # make request
        connection = httplib.HTTPSConnection("phraseapp.com")
        if method in ("POST", "PUT"):
            connection.request(method, "/api/v1/" + endpoint, None if data is None else urllib.urlencode(params), {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'})
        else:
            connection.request(method, "/api/v1/" + endpoint + "?" + urllib.urlencode(params), None, {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'})

        # parse result
        response = connection.getresponse()
        if response.status >= 200 and response.status < 300:
            response_data = response.read().decode("utf-8")

            if needs_decoding:
                if response_data == "":
                    return {}
                return json.loads(response_data)
            else:
                return response_data
        else:
            raise CommandError("Failure during communication with PhraseApp API. Please check your PHRASE_AUTH_TOKEN setting.")

    @staticmethod
    def _popen(cmd):
        """Friendly wrapper around Popen for Windows"""
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, close_fds=os.name != 'nt', universal_newlines=True)
        output, errors = p.communicate()
        return output, errors, p.returncode

    @staticmethod
    def _handle_extensions(extensions=('html',), ignored=('py',)):
        """
        Organizes multiple extensions that are separated with commas or passed by
        using --extension/-e multiple times. Note that the .py extension is ignored
        here because of the way non-*.py files are handled in make_messages() (they
        are copied to file.ext.py files to trick xgettext to parse them as Python
        files).

        For example: running 'django-admin sync_keys -e js,txt -e xhtml -a'
        would result in an extension list: ['.js', '.txt', '.xhtml']

        >>> handle_extensions(['.html', 'html,js,py,py,py,.py', 'py,.py'])
        set(['.html', '.js'])
        >>> handle_extensions(['.html, txt,.tpl'])
        set(['.html', '.tpl', '.txt'])
        """
        ext_list = []
        for ext in extensions:
            ext_list.extend(ext.replace(' ', '').split(','))
        for i, ext in enumerate(ext_list):
            if not ext.startswith('.'):
                ext_list[i] = '.%s' % ext_list[i]
        return set([x for x in ext_list if x.strip('.') not in ignored])

    @staticmethod
    def _is_ignored(path, ignore_patterns):
        """Helper function to check if the given path should be ignored or not."""
        for pattern in ignore_patterns:
            if fnmatch.fnmatchcase(path, pattern):
                return True
        return False

    @staticmethod
    def _find_files(root, ignore_patterns, symlinks=False):
        """Helper function to get all files in the given root."""
        dir_suffix = '%s*' % os.sep
        norm_patterns = [p[:-len(dir_suffix)] if p.endswith(dir_suffix) else p for p in ignore_patterns]
        all_files = []
        for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=symlinks):
            for dirname in dirnames[:]:
                if Command._is_ignored(os.path.normpath(os.path.join(dirpath, dirname)), norm_patterns):
                    dirnames.remove(dirname)
            for filename in filenames:
                if not Command._is_ignored(os.path.normpath(os.path.join(dirpath, filename)), ignore_patterns):
                    all_files.extend([(dirpath, filename)])
        all_files.sort()
        return all_files

    @staticmethod
    def _check_gettext_version():
        # We require gettext version 0.15 or newer.
        output, errors, status = Command._popen('xgettext --version')
        if status != 0:
            raise CommandError("Error running xgettext. Note that Django internationalization requires GNU gettext 0.15 or newer.")
        match = re.search(r'(?P<major>\d+)\.(?P<minor>\d+)', output)
        if match:
            xversion = (int(match.group('major')), int(match.group('minor')))
            if xversion < (0, 15):
                raise CommandError("Django internationalization requires GNU gettext 0.15 or newer. You are using version %s, please upgrade your gettext toolset." % match.group())

    @staticmethod
    def _progress_bar(data_list, element_func, width=80, progress_char='#'):
        sys.stdout.write("[%s]" % (" " * (width)))
        sys.stdout.flush()
        sys.stdout.write("\b" * (width+1))

        blocks_drawn = 0
        elements_done = 0
        elements_worked = 0
        for element in data_list:

            if element_func(element):
                elements_worked = elements_worked + 1

            elements_done = elements_done + 1

            if elements_done > (blocks_drawn * (len(data_list)/float(width))):
                sys.stdout.write(progress_char)
                sys.stdout.flush()
                blocks_drawn = blocks_drawn + 1

        sys.stdout.write("\n")

        return elements_worked

    @staticmethod
    def _process_file(file_name, dir_path, domain, extensions):
        """
        Extract translatable literals from :param file_name: for :param domain:.

        Uses the xgettext GNU gettext utility.
        """

        from django.utils.translation import templatize

        _, file_ext = os.path.splitext(file_name)
        if domain == 'djangojs' and file_ext in extensions:
            has_work_file = True

            # read input file
            with open(os.path.join(dir_path, file_name)) as fp:
                src_data = fp.read()

            # transform
            src_data = prepare_js_for_gettext(src_data)

            # write work file
            work_file = os.path.join(dir_path, '%s.c' % file_name)
            with open(work_file, "w") as fp:
                fp.write(src_data)

            gettext_language = "C"
            gettext_keywords = ['gettext_noop', 'gettext_lazy', 'gettext_lazy:1,2', 'pgettext:1c,2', 'npgettext:1c,2,3']

        elif domain == "django" and (file_ext == '.py' or file_ext in extensions):
            if file_ext in extensions:
                has_work_file =  True

                # read input
                with open(os.path.join(dir_path, file_name), "rU") as fp:
                    src_data = fp.read()

                # transform
                content = templatize(src_data, os.path.join(dir_path, file_name))

                # write work file
                work_file = os.path.join(dir_path, '%s.py' % file_name)
                with open(work_file, "w") as fp:
                    fp.write(content)
            else:
                # directly use input as work file (no transformation necessary)
                has_work_file = False

                work_file = os.path.join(dir_path, file_name)

            gettext_language = "Python"
            gettext_keywords = ['gettext_noop', 'gettext_lazy', 'ngettext_lazy:1,2', 'ugettext_noop', 'ugettext_lazy', 'ungettext_lazy:1,2', 'pgettext:1c,2', 'npgettext:1c,2,3', 'pgettext_lazy:1c,2', 'npgettext_lazy:1c,2,3']
        else:
            return []

        # run gettext
        msgs, errors, status = Command._popen('xgettext -d %s -L %s --no-wrap --no-location %s --from-code UTF-8 --add-comments=Translators -o - "%s"' % (domain, gettext_language, " ".join(["--keyword=%s" % k for k in gettext_keywords]) , work_file))

        # clean up
        if has_work_file:
            os.remove(work_file)

        # fail on error
        if errors and status != 0:
                raise CommandError("errors happened while running xgettext on %s\n%s" % (file, errors))

        # parse result and return the keys
        return [entry.msgid for entry in pofile(msgs)]

    def handle(self, *args, **options):
        # check prerequisites
        Command._check_gettext_version()

        # load options
        domain = options.get('domain')
        if domain not in ('django', 'djangojs'):
            raise CommandError("currently sync_keys only supports domains 'django' and 'djangojs'")
        extensions = options.get('extensions')
        extensions = Command._handle_extensions(extensions if extensions else (['js'] if domain == 'djangojs' else ['html', 'txt']))

        symlinks = options.get('symlinks')
        ignore_patterns = options.get('ignore_patterns', [])
        if options.get('use_default_ignore_patterns'):
            ignore_patterns += ['CVS', '.*', '*~']
        ignore_patterns = list(set(ignore_patterns))

        # iterate over all files and collect keys
        local_key_names = set()
        for dir_path, file_name in Command._find_files(".", ignore_patterns=ignore_patterns, symlinks=symlinks):
            try:
                local_key_names.update(Command._process_file(file_name, dir_path, domain=domain, extensions=extensions))
            except UnicodeDecodeError:
                stdout.write("UnicodeDecodeError: skipped file %s in %s" % (file, dirpath))

        sys.stdout.write("Found %d local keys\n" % len(local_key_names))

        # retrieve PhraseApp keys
        pa_key_data = Command._make_request("translation_keys")
        pa_key_names = [key['name'] for key in pa_key_data]
        pa_key_name_id_map = dict((key['name'], key['id']) for key in pa_key_data   )

        sys.stdout.write("Found %d PhraseApp keys\n" % len(pa_key_names))

        # retrieve PhraseApp locales and figure out dummy locale
        pa_locales = Command._make_request("locales")
        if len(pa_locales) == 0:
            raise CommandError("No locales found in PhraseApp, please create one first.")
        pa_locale = pa_locales[0]['name']

        # upload new keys
        sys.stdout.write("Creating new keys in PhraseApp\n")

        def process_new_key(key):
            if not key in pa_key_names:
                # new key -> create it
                Command._make_request("translations/store", data={'locale': pa_locale, 'key': key}, method="POST")
                return True
            else:
                return False
        new_keys = Command._progress_bar(local_key_names, process_new_key)
        sys.stdout.write("Created %d new keys in PhraseApp\n" % new_keys)

        # if not disabled, delete obsolete keys
        if not options['push_only']:
            # for this we need user credentials
            session_info = Command._make_request("sessions", data={'email': options['phraseapp_username'], 'password': options['phraseapp_password']}, method="POST")
            if not session_info['success']:
                raise CommandError("Failed to login to PhraseApp, could not delete obsolete keys")

            sys.stdout.write("Removing obsolete keys from PhraseApp\n")

            def process_old_key(key):
                if not key in local_key_names:
                    # obsolete key -> delete it
                    Command._make_request("translation_keys/%d" % pa_key_name_id_map[key], method="DELETE", user_auth_token=session_info['auth_token'])
                    return True
                else:
                    return False
            old_keys = Command._progress_bar(pa_key_names, process_old_key)

            # end user session
            Command._make_request("sessions", method="DELETE", user_auth_token=session_info['auth_token'])


            sys.stdout.write("Removed %d obsolete keys from PhraseApp\n" % old_keys)
