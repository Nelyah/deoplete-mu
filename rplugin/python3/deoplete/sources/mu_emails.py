import re

from deoplete.source.base import Base
from subprocess import check_output

COLON_PATTERN = re.compile(':\s?')
COMMA_PATTERN = re.compile('.+,\s?')
HEADER_PATTERN = re.compile('^(Bcc|Cc|From|Reply-To|To):(\s?|.+,\s?)')


def remove_accents(string):
    string = re.sub(u"[àáâãäå]", 'a', string)
    string = re.sub(u"[èéêë]", 'e', string)
    string = re.sub(u"[ìíîï]", 'i', string)
    string = re.sub(u"[òóôõö]", 'o', string)
    string = re.sub(u"[ùúûü]", 'u', string)
    string = re.sub(u"[ýÿ]", 'y', string)
    string = re.sub(u"[ÀÁÂÃÄÅ]", 'A', string)
    string = re.sub(u"[ÈÉÊË]", 'E', string)
    string = re.sub(u"[ÌÍÎÏ]", 'I', string)
    string = re.sub(u"[ÒÓÔÕÖ]", 'O', string)
    string = re.sub(u"[ÙÚÛÜ]", 'U', string)
    string = re.sub(u"[ÝŸ]", 'Y', string)

    return string


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'mu'
        self.mark = '[mu]'
        self.min_pattern_length = 2
        self.filetypes = ['mail']

        self.__cache = []

    def get_complete_position(self, context):
        colon = COLON_PATTERN.search(context['input'])
        comma = COMMA_PATTERN.search(context['input'])
        return max(colon.end() if colon is not None else -1,
                   comma.end() if comma is not None else -1)

    def gather_candidates(self, context):
        if HEADER_PATTERN.search(context['input']):
            if not self.__cache:
                self.__fill_cache()
            return self.__cache

    def __fill_cache(self):
        addresses = check_output(['mu', 'cfind']).splitlines()
        addresses = [entry.decode('UTF-8') for entry in addresses]

        for entry in addresses:
            entry = entry.split()
            email = entry[-1]
            name = ' '.join(entry[:-1])
            name = remove_accents(name)

            if name == email:
                name = ''

            self.__cache.append({
                'word':
                "{0} <{1}>".format(name, email)
            })
