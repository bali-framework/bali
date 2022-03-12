from collections import defaultdict

from sqlalchemy import case
from sqlalchemy.ext.hybrid import Comparator
from sqlalchemy.util.langhelpers import dictlike_iteritems


class CaseComparator(Comparator):
    def __init__(self, whens, expression):
        super().__init__(expression)
        self.whens, self.reversed_whens = dictlike_iteritems(whens), defaultdict(list)
        for k, v in self.whens:
            self.reversed_whens[v].append(k)

    def __clause_element__(self):
        return case(self.whens, self.expression)

    def __eq__(self, other):
        return super().__clause_element__().in_(self.reversed_whens[other])
