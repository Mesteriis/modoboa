"""
Custom pagination tools.
"""

class Page(object):

    """Class to represent a page."""

    def __init__(self, paginator, pageid, id_start, id_stop, baseurl=None):
        """Constructor."""
        self.paginator = paginator
        self.number = pageid
        self.id_start = id_start
        self.id_stop = id_stop
        self.baseurl = baseurl

        self._has_previous = None
        self._has_next = None

    @property
    def items_per_page(self):
        """The number of items in a page. (shortcut)"""
        return self.paginator.elems_per_page

    @property
    def items(self):
        """The number of items in this page."""
        return self.id_stop - self.id_start

    @property
    def has_previous(self):
        """Tell if a previous page is available or not."""
        if self._has_previous is None:
            self._has_previous = self.number > 1
        return self._has_previous

    @property
    def previous_page_number(self):
        """Return the index of the previous page."""
        return self.number - 1 if self.has_previous else False

    @property
    def has_next(self):
        """Tell if a next page is available or not."""
        if self._has_next is None:
            self._has_next = self.id_stop < self.paginator.total
        return self._has_next

    @property
    def next_page_number(self):
        """Return the index of the next page."""
        return self.number + 1 if self.has_next else False

    @property
    def last_page(self):
        """Retrieve the id of the last page."""
        lid = self.paginator.total / self.items_per_page
        if not lid:
            return 1
        if self.paginator.total % self.items_per_page:
            lid += 1
        return lid


class Paginator(object):

    """Pagination class."""

    def __init__(self, total, elems_per_page):
        self.total = total
        self.elems_per_page = elems_per_page
        self.num_pages = total / elems_per_page
        if total % elems_per_page:
            self.num_pages += 1

    def _indexes(self, page):
        """Compute start and stop indexes."""
        id_start = self.elems_per_page * page + 1
        id_stop = id_start + self.elems_per_page - 1
        return (id_start, id_stop)

    def getpage(self, page_id):
        """Retrieve a specific page."""
        if page_id < 1:
            return None
        id_start, id_stop = self._indexes(page_id - 1)
        if id_start > self.total:
            return None
        if id_stop >= self.total:
            id_stop = self.total
        return Page(self, page_id, id_start, id_stop)
