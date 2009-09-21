=====================
Django MPTT CHANGELOG
=====================

.. contents::

Trunk Changes
=============

Sun 12th Sep, 2008
------------------

* Extracted new ``TreeNodeChoiceField`` and ``TreeNodePositionField``
  form fields from ``MoveNodeForm``.

Thu 4th Sep, 2008
-----------------

* Updated forms for Django 1.0 compatibility, as ``django.newforms`` is
  no more.

* Fixed tests.

Mon 11th Aug, 2008
------------------

* (brosner) Updated signal handling to be compatible with Django 1.0.

Mon 12th May, 2008
------------------

* Added ``position_choices`` argument to ``mptt.forms.MoveNodeForm``.

Fri 25th Jan, 2008
------------------

* BACKWARDS-INCOMPATIBLE CHANGE - the ``order_insertion_by`` argument
  to ``mptt.register`` must now be a list or other iterable of field
  names.

Tue 22nd Jan, 2008
------------------

* Tests were moved so they're not run when applications which use Django
  MPTT are tested.

Thu 17th Jan, 2008
------------------

* The ``pre_save`` signal receiver now checks for the presence of a
  ``raw`` argument, for the benefit of anyone who needs to use fixtures
  with Django MPTT and is willing to apply the small patch in
  http://code.djangoproject.com/ticket/5422 to their own checkout of
  Django.

Version 0.2.1
=============

Quick fix for installation with ``setup.py``.

Version 0.2
===========

Packaged from revision 88 in Subversion.

Tue 15th Jan, 2008
------------------

* Added ``order_insertion_by`` argument to ``mptt.register`` and
  implemented automatic ordering in ``pre_save`` when this argument was
  given for the ``Model`` class of the node being saved.

* Updated ``signals.pre_save()`` to use ``Model.insert_at()``.

* Added an ``insert_at()`` convenience method to ``Model`` instances.

* Added an ``insert_node()`` method to ``TreeManager`` for positioning
  of nodes which haven't yet been inserted into the database.

Sat 12th Jan, 2008
------------------

* BACKWARDS-INCOMPATIBLE CHANGE - model registration is now handled by
  ``mptt.register`` instead of ``mptt.models.treeify``.

* An exception is now raised if you call ``treeify`` on the same
  ``Model`` class twice.

Thu 10th Jan, 2008
------------------

* Documented ``MoveNodeForm`` in ``docs/forms.txt``.

* Added a ``target_select_size`` argument to ``MoveNodeForm``.

* Added a ``root_node()`` method to ``TreeManager``.

* Added ``get_root()`` method to ``Model`` instances.

* The ``tree_info`` template filter now accepts an optional argument to
  specify other tree structure information which should be made
  available.

* Added a ``tree_path`` template filter.

Wed 9th Jan, 2008
-----------------

* Split documentation into multiple files.

* Created ``mptt.forms``, with ``MoveNodeForm``.

* Removed ``mptt.queries`` - the functionality it could be used to
  manually implement is now provided by a new ``add_related_count()``
  method in ``TreeManager``.

* Tree attributes are now held to ``Model`` class' ``Options``
  (i.e. ``_meta``). This allowed a lot of refactoring, as these
  attributes no longer need to be passed around or taken from the
  class' ``TreeManager``.

* Added a ``root_nodes()`` method to ``TreeManager``.

Tue 8th Jan, 2008
-----------------

* ``TreeManager.move_node()`` now calls
  ``transaction.commit_unless_managed()`` before it returns.

* Documented the ``mptt.utils`` and ``mptt.queries`` modules.

* Split related item count queries out into ``mptt.queries``, with
  functions to create them given MPTT ``Model`` and related ``Model``
  information.

* Added a ``drilldown_tree_for_node`` template tag.

Mon 7th Jan, 2008
-----------------

* Added ``get_children()`` and ``is_leaf_node()`` methods to ``Model``
  instances.

Sun 6th Jan, 2008
-----------------

* Added some technical details about the tree structure to the
  documentation.

Sat 5th Jan, 2008
-----------------

* Finished implementing moving of nodes to be siblings of roots.

* Added ``get_next_sibling()`` and ``get_previous_sibling()`` methods
  to ``Model`` instances.

Fri 4th Jan, 2008
-----------------

* Made ``InvalidMove`` exceptions more granular - they now report on an
  invalid move being attempted with the target node itself or with one
  of its descendants.

* Started implementing moving of nodes to be siblings of roots. This is
  a special case due to our use of a tree id, so it's detected and dealt
  with as early as possible in ``move_node()``.

  As a result, none of the other node movement implementation methods
  have to check for this special case - they can be sure they'll never
  have to handle a root sibling move when ``move_node`` is being used.

* BACKWARDS-INCOMPATIBLE CHANGE - Simplified the node movement API -
  ``move_node()`` is now ``TreeManager``'s only public means of moving a
  node, as it can figure out what to do based on the node and target
  given.

  This simplifies implementation somewhat, as the methods which actually
  do the moving can trust their caller with the types of nodes which
  were given when it matters.

* Added ``is_root_node()`` and ``is_child_node()`` methods to ``Model``
  instances.

Version 0.1
===========

Packaged from revision 37 in Subversion.

Fri 4th Jan, 2008
-----------------

* Added a ``tree_info`` template filter and a ``full_tree_for_model``
  template tag.

Thu 3rd Jan, 2008
-----------------

* Updated documentation with latest changes, a high level overview of
  features and more details about node movement. Moved detailed
  information about MPTT setup internals to the end of the document.

* Reworked exceptions - ``InvalidMove`` is now raised when an invalid
  move is attempted.

* Added a ``move_to()`` convenience method to ``Model`` instances.

* Implemented the ``position`` argument for ``make_child_node()`` and
  ``move_node()`` in ``TreeManager``. The node movement API can now be
  used to move any node to an arbitrary point in any tree.

* Implemented the ``position`` argument for
  ``TreeManager.move_to_new_tree()``.

* Implemented a ``position`` argument for
  ``TreeManager.move_within_tree()``. The node being moved can now be
  made a sibling, first child or last child of the target node.

* Added a ``move_node()`` method to ``TreeManager``, to take care of
  automatically calling the appropriate node movement manager method.

* Combined a number of SQL queries into single queries using ``CASE``
  operators to reduce the overall number of queries required to move
  tree nodes around.

Wed 2nd Jan, 2008
-----------------

* Fixed a bug in ``TreeManager.move_within_tree()`` when no level change
  is required.

* Fixed a bug in ``TreeManager.move_within_tree()`` - it now takes into
  account whether or not the new parent's right value is greater than
  that of the node which is being moved.

* Added tests for manually moving nodes using the ``TreeManager``
  methods.

* Extracted logic for moving a ``Model`` instance to a different parent
  within its current tree from ``mptt.signals.pre_save()`` into the
  ``move_within_tree()`` method in ``TreeManager``.

* Extracted logic for moving a ``Model`` instance from one tree to
  another from ``mptt.signals.pre_save()`` into the
  ``move_to_new_tree()`` method in ``TreeManager``.

* Extracted some similar move-node-to-tree queries in ``TreeManager``'s
  ``make_child_node()`` and ``make_root_node()`` methods out into a new
  ``_inter_tree_move()`` method.

Tue 1st Jan, 2008
-----------------

* Extracted logic for turning a ``Model`` instance which is the root
  node of a tree into a child of a given parent node in another tree
  from ``mptt.signals.pre_save()`` into the ``make_child_node()`` method
  in ``TreeManager``.

* Extracted logic for turning a ``Model`` instance which is a child node
  into the root node of a new tree from ``mptt.signals.pre_save`` into
  the ``make_root_node()`` method in ``TreeManager``.

* Removed ``mptt.signals._get_next_tree_id``; added a
  ``get_next_tree_id()`` method to ``TreeManager`` to replace it.

* Extracted some similar space-management queries out into the
  ``close_gap()`` and ``create_space()`` methods in ``TreeManager``.

* Implemented reparenting when a child node is assigned a different
  parent in the same tree.

* Implemented reparenting when a child node is assigned a parent in a
  different tree.

Mon 31st Dec, 2007
------------------

* Implemented reparenting when a root node is transformed into a child
  node by being assigned a parent.

Sun 30th Dec, 2007
------------------

* Implemented reparenting when a ``Model`` instance is transformed into
  a root node by having its parent removed.

* Added tests for creation, ``Model`` instance methods and deletion.

* Added a ``get_siblings()`` method to ``Model`` instances.
