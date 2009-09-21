=================
Technical details
=================

.. admonition:: About this document

   This document provides technical details related to some aspects of
   Django MPTT's inner workings and its implementation of Modified
   Preorder Tree Traversal.

.. contents::
   :depth: 3

Tree structure
==============

In addition to the left and right identifiers which form the core of how
MPTT works and the parent field, Django MPTT has the following
additional fields on each tree node.

Tree id
-------

**A unique identifier assigned to each root node and inherited by all its
descendants.**

This identifier is the means by which Django MPTT implements multiple
root nodes.

Since we can use it to identify all nodes which belong to a particular
tree, the subtree headed by each root node can have its edge indicators
starting at ``1`` - as long as tree operations are constrained to the
appropriate tree id(s), we don't have to worry about overlapping of left
and right edge indicator values with those of nodes in other trees.

This approach limits the number of rows affected when making space to
insert new nodes and removing gaps left by deleted nodes.

Root node ordering
~~~~~~~~~~~~~~~~~~

This field also defines the order in which root nodes are retrieved when
you create a ``QuerySet`` using ``TreeManager``, which by default
orders the resulting ``QuerySet`` by tree id, then left edge indicator
(for depth-first ordering).

When a new root node is created, it is assigned the next-largest tree id
available, so by default root nodes (and thus their subtrees) are
displayed in the order they were created.

Movement and volatility
~~~~~~~~~~~~~~~~~~~~~~~

Since root node ordering is defined by tree id, it can also be used to
implement movement of other nodes as siblings of a target root node.

When you use the node movement API to move a node to be a sibling of a
root node, tree ids are shuffled around to acheive the new ordering
required. Given this, you should consider the tree id to be
**volatile**, so it's recommended that you don't store tree ids in your
applications to identify particular trees.

Since *every* node has a tree id, movement of a node to be a sibling of
a root node can potentially result in a large number of rows being
modified, as the further away the node you're moving is from its target
location, the larger the number of rows affected - every node with a
tree id between that of the node being moved and the target root node
will require its tree id to be modified.

Level
-----

**The level (or "depth") at which a node sits in the tree.**

Root nodes are level ``0``, their immediate children are level ``1``,
*their* immediate children are level ``2`` and so on...

This field is purely denormalisation for convenience. It avoids the need
to examine the tree structure to determine the level of a particular
node and makes queries which need to take depth into account easier to
implement using Django's ORM. For example, limiting the number of levels
of nodes which are retrieved for the whole tree or any subtree::

   # Retrieve root nodes and their immediate children only
   SomeModel.tree.filter(level__lte=1)

   # Retrieve descendants of a node up to two levels below it
   node.get_descendants().filter(level__lte=node.level + 2)


Dynamic field creation vs. explicitly defining MPTT fields
==========================================================

Model classes which do not have field names which clash with the defaults need 
not contain any details about MPTT fields at all in ``MpttMeta``.

One of the goals of this application is that authors should not have to
worry about setting up or using MPTT fields directly in order to reap
the benefits of the functionality their existence enables.

While dynamically added MPTT fields can be used in inner ``Meta``
classes and ``ModelAdmin`` classes, it is recommended that models which
will use these fields elsewhere in the class definition should implement
the fields themselves for clarity - it's already bad enough that we're
dynamically adding fields without your model definitions using fields
which don't appear to exist.

Salt to taste, your mileage may vary, etc. etc.


Running the test suite
======================

The ``mptt.tests`` package is set up as a project which holds a test
settings module and defines models for use in testing MPTT. You can run
the tests from the command-line using the ``django-admin.py`` script,
specifying that the test settings module should be used::

   django-admin.py test --settings=mptt.tests.settings

Django MPTT has been tested with SQLite, MySQL 4.1 and PostgreSQL 8.1 on
Windows.
