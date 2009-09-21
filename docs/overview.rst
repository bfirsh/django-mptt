===========
Django MPTT
===========

.. admonition:: About this document

   This document provides an overview of what Modified Preorder Tree
   Traversal (MPTT) and Django MPTT are.

.. contents::
   :depth: 3


What is Modified Preorder Tree Traversal?
=========================================

MPTT is a technique for storing hierarchical data in a database in a
manner which makes tree retrieval operations such as fetching complete
trees, item ancestors and item descendants very efficient.

The trade-off for this efficiency is that performing inserts and moving
items around the tree is more involved, as there's some extra work
required to keep the tree structure in a good state at all times.

Here are a few articles about MPTT to whet your appetite and provide
details about how the technique itself works:

    * `Trees in SQL`_
    * `Storing Hierarchical Data in a Database`_
    * `Managing Hierarchical Data in MySQL`_

In particular, these articles should help you understand the two most
important fields in MPTT - the left and right "edge indicators". Other
fields involved in Django MPTT's implementation of the technique are
discusssed in the technical details documentation.

.. _`Trees in SQL`: http://www.intelligententerprise.com/001020/celko.jhtml
.. _`Storing Hierarchical Data in a Database`: http://www.sitepoint.com/print/hierarchical-data-database
.. _`Managing Hierarchical Data in MySQL`: http://dev.mysql.com/tech-resources/articles/hierarchical-data.html


What is Django MPTT?
====================

Django MPTT is a reusable/standalone Django application which aims to
make it easy for you to use Modified Preorder Tree Traversal with your
own Django models in your own applications.

It takes care of the details of managing a database table as a tree
structure and provides tools for working with trees of model instances.

Feature overview
----------------

* An abstract Django model that you simply inherit from to provide MPTT 
  functionality for your models.

* The tree structure is automatically managed when you create or delete
  MPTT model instances. By default, new instances are added as the last
  child of their parent if they have one, otherwise they become the root
  of a new tree.

* The tree structure is automatically updated when you change a
  model instance's parent - by default, modified instances are moved so
  they are the last child of their new parent.

  This allows basic management of the tree using the parent field
  available to you in the ``django.contrib.admin`` application and in
  ``django.forms`` forms generated using the ``ModelForm`` class.

* To override the default insertion/reparenting positions mentioned
  above, you can specify that a particular field in your model is used
  for ordering when inserting or automatically reparenting model
  instances.

  This allows you to have each level of the tree automatically sorted by
  a field of your choice.

* The abstract model provides methods for models for changing their position 
  in the tree, retrieving their ancestors, siblings and descendants, 
  determining the number of descendants they have and other tree-related 
  operations.

* A custom ``TreeManager`` manager provides tree management operations which, 
  among other things, can be used to move any node in a tree (and its 
  descendants) to an arbitrary point elsewhere in the tree, or to insert new 
  nodes at any point in the tree.

* ``django.forms`` components for working with trees in forms.

* Utility functions for working with trees of models.

* Template tags and filters for working with trees of models in
  templates.
