# ~*~ coding: utf-8 ~*~
#-
# OSMAlchemy - OpenStreetMap to SQLAlchemy bridge
# Copyright (c) 2016 Dominik George <nik@naturalnet.de>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Alternatively, you are free to use OSMAlchemy under Simplified BSD, The
# MirOS Licence, GPL-2+, LGPL-2.1+, AGPL-3+ or the same terms as Python
# itself.

""" Trigger code for live OSMAlchemy/Overpass integration. """

import datetime
import operator
from sqlalchemy import inspect
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList, BindParameter
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Query
from sqlalchemy.sql.annotation import AnnotatedColumn
from weakref import WeakSet

from .online import _get_single_element_by_id
from .util import _import_osm_xml

def _generate_triggers(osmalchemy, maxage=60*60*24):
    """ Generates the triggers for online functionality.

      osmalchemy - reference to the OSMAlchemy instance to be configured
      maxage - maximum age of objects before they are updated online, in seconds
    """

    _visited_queries = WeakSet()

    @listens_for(Query, "before_compile")
    def _query_compiling(query):
        # Get the session associated with the query:
        session = query.session

        # Prevent recursion by skipping already-seen queries
        if query in _visited_queries:
            return
        else:
            _visited_queries.add(query)

        # Check whether this query affects our model
        affected_models = set([c["type"] for c in query.column_descriptions])
        our_models = set([osmalchemy.node, osmalchemy.way,  osmalchemy.relation,
                          osmalchemy.element])
        if affected_models.isdisjoint(our_models):
            # None of our models is affected
            return

        # Check whether this query filters elements
        # Online update will only run on a specified set, not all data
        if query.whereclause is None:
            # No filters
            return

        # Define operator to string mapping
        _ops = {operator.eq: "==",
                operator.ne: "!=",
                operator.lt: "<",
                operator.gt: ">",
                operator.le: "<=",
                operator.ge: ">=",
                operator.and_: "&&",
                operator.or_: "||"}

        # Traverse whereclause recursively
        def _analyse_clause(clause, target):
            if type(clause) is BinaryExpression:
                # This is something like "latitude >= 51.0"
                left = clause.left
                right = clause.right
                op = clause.operator

                # Left part should be a column
                if type(left) is AnnotatedColumn:
                    # Get table class and field
                    model = left._annotations["parentmapper"].class_
                    field = left

                    # Only use if we are looking for this model
                    if model is target:
                        # Store field name
                        left = field.name
                    else:
                        return None
                else:
                    # Right now, we cannot cope with anything but a column on the left
                    return None

                # Right part should be a literal value
                if type(right) is BindParameter:
                    # Extract literal value
                    right = right.value
                else:
                    # Right now, we cannot cope with something else here
                    return None

                # Look for a known operator
                if op in _ops.keys():
                    # Get string representation
                    op = _ops[op]
                else:
                    # Right now, we cannot cope with other operators
                    return None

                # Return polish notation tuple of this clause
                return (op, left, right)
            elif type(clause) is BooleanClauseList:
                # This is an AND or OR operation
                op = clause.operator
                clauses = []

                # Iterate over all the clauses in this operation
                for clause in clause.clauses:
                    # Recursively analyse clauses
                    res = _analyse_clause(clause, target)
                    # None is returned for unsupported clauses or operations
                    if res is not None:
                        # Append polish notation result to clauses list
                        clauses.append(res)

                # Look for a known operator
                if op in _ops.keys():
                    # Get string representation
                    op = _ops[op]
                else:
                    # Right now, we cannot cope with anything else
                    return None

                # Return polish notation tuple of this clause
                return (op, clauses)
            else:
                # We hit an unsupported type of clause
                return None
        # Analyse where clause looking for all looked-up fields
        tree = {}
        for target in our_models.intersection(affected_models):
            tree[target.__name__] = _analyse_clause(query.whereclause, target)
