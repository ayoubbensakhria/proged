import re
import io

from django.db import models
from django.utils.translation import ugettext_lazy as _


class Automate(models.Model):

    """
    Automates:
        * moving of documents into destination folder
        * extraction of metadata
    """

    # any match - looks for any occurrence of any word
    # provided in the document
    MATCH_ANY = 1
    # all match - looks for all occurrences of all words
    # provided in the document (order does not matter)
    MATCH_ALL = 2
    # literal match means that the text you enter must appear in
    # the document exactly as you've entered it
    MATCH_LITERAL = 3
    # reg exp match
    MATCH_REGEX = 4

    MATCHING_ALGORITHMS = (
        (MATCH_ANY, _("Any")),
        (MATCH_ALL, _("All")),
        (MATCH_LITERAL, _("Literal")),
        (MATCH_REGEX, _("Regular Expression")),
    )

    name = models.CharField(
        max_length=128,
        unique=True
    )

    # text to match
    match = models.CharField(
        max_length=256,
        blank=True
    )

    matching_algorithm = models.PositiveIntegerField(
        choices=MATCHING_ALGORITHMS,
        default=MATCH_ANY,
    )

    # shoud be matching case_sensitive? i.e. uppercase == lowercase
    is_case_sensitive = models.BooleanField(
        default=True
    )

    # name of plugin used to extract metadata, if any.
    # Must match metadata associated with dst_folder
    plugin_name = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        choices=(),
        default=None,
    )

    # Must match correct plugin (in case you wish automate metadta extract)
    dst_folder = models.ForeignKey(
        'Folder',
        on_delete=models.DO_NOTHING
    )

    # Should this page be cutted and pasted as separate document?
    # Very useful in case of bulk receipts scans
    extract_page = models.BooleanField(
        default=False
    )

    user = models.ForeignKey(
        'User',
        models.CASCADE,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    def is_a_match(self, hocr: io.BytesIO):
        # Check that match is not empty
        if self.match.strip() == "":
            return False

        search_kwargs = {}
        if self.is_case_sensitive:
            search_kwargs = {"flags": re.IGNORECASE}

        if self.matching_algorithm == Automate.MATCH_ANY:
            return self._match_any(hocr, search_kwargs)

        if self.matching_algorithm == Automate.MATCH_ALL:
            return self._match_all(hocr, search_kwargs)

        if self.matching_algorithm == Automate.MATCH_LITERAL:
            return self._match_literal(hocr, search_kwargs)

        if self.matching_algorithm == Automate.MATCH_REGEX:
            return self._match_regexp(hocr, search_kwargs)

    def apply(
        self,
        document,
        page,
        hocr,
        plugin=None
    ):
        # if self.extract_page:
        #   get destination folder id
        #   cut/paste page to destination foder
        #   get new_doc_id
        #
        # if plugin:
        #   metadata = plugin.extract(hocr)
        #   associate metadta to:
        #       # either new_doc_id
        #       # or
        #       # doc_id
        pass

    def _match_any(self, hocr, search_kwargs):
        pass

    def _match_all(self, hocr, search_kwargs):
        pass

    def _match_literal(self, hocr, search_kwargs):
        """
        Simplest match - literal match  i.e.
        exact match of the given word or string.
        """
        regexp = r"\b{}\b".format(self.match)
        result = re.search(regexp, hocr, **search_kwargs)
        return bool(result)

    def _match_regexp(self, hocr: io.BytesIO, search_kwargs):
        pass
