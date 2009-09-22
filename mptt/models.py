"""
New instance methods for Django models which are set up for Modified
Preorder Tree Traversal.
"""

import copy
from django.db import models
from django.db.models import base
from django.db.models.query import Q
from mptt.managers import TreeManager
import operator

def _insertion_target_filters(node, order_insertion_by):
    """
    Creates a filter which matches suitable right siblings for ``node``,
    where insertion should maintain ordering according to the list of
    fields in ``order_insertion_by``.

    For example, given an ``order_insertion_by`` of
    ``['field1', 'field2', 'field3']``, the resulting filter should
    correspond to the following SQL::

       field1 > %s
       OR (field1 = %s AND field2 > %s)
       OR (field1 = %s AND field2 = %s AND field3 > %s)

    """
    fields = []
    filters = []
    for field in order_insertion_by:
        value = getattr(node, field)
        filters.append(reduce(operator.and_, [Q(**{f: v}) for f, v in fields] +
                                             [Q(**{'%s__gt' % field: value})]))
        fields.append((field, value))
    return reduce(operator.or_, filters)

def _get_ordered_insertion_target(node, parent):
    """
    Attempts to retrieve a suitable right sibling for ``node``
    underneath ``parent`` (which may be ``None`` in the case of root
    nodes) so that ordering by the fields specified by the node's class'
    ``order_insertion_by`` option is maintained.

    Returns ``None`` if no suitable sibling can be found.
    """
    right_sibling = None
    # Optimisation - if the parent doesn't have descendants,
    # the node will always be its last child.
    if parent is None or parent.get_descendant_count() > 0:
        opts = node._meta
        order_by = opts.order_insertion_by[:]
        filters = _insertion_target_filters(node, order_by)
        if parent:
            filters = filters & Q(**{opts.parent_attr: parent})
            # Fall back on tree ordering if multiple child nodes have
            # the same values.
            order_by.append(opts.left_attr)
        else:
            filters = filters & Q(**{'%s__isnull' % opts.parent_attr: True})
            # Fall back on tree id ordering if multiple root nodes have
            # the same values.
            order_by.append(opts.tree_id_attr)
        try:
            right_sibling = \
                node._default_manager.filter(filters).order_by(*order_by)[0]
        except IndexError:
            # No suitable right sibling could be found
            pass
    return right_sibling


class ModelBase(base.ModelBase):
    def __init__(cls, name, bases, attrs):
        super(ModelBase, cls).__init__(name, bases, attrs)
        default_mptt_meta = {
            'parent_attr': 'parent',
            'right_attr': 'rght',
            'left_attr': 'lft',
            'tree_id_attr': 'tree_id',
            'level_attr': 'level',
            'tree_manager_attr': 'tree',
            'order_insertion_by': None,
        }
        concrete_parent = False
        for base in bases:
            if not isinstance(base, ModelBase) or not hasattr(base, '_meta'):
                # Things without _meta aren't functional models, so they're
                # uninteresting parents.
                continue
            # Inherit MPTT metadata which differs from default and not already
            # set by a previous parent
            for attr, default in default_mptt_meta.items():
                val = getattr(base._meta, attr, default)
                if val != default:
                    setattr(cls._meta, attr, val)
            
            if not base._meta.abstract:
                concrete_parent = True
        
        for attr, default in default_mptt_meta.items():
            # Set the default metadata for attributes not set by parents
            if not hasattr(cls._meta, attr):
                setattr(cls._meta, attr, default)
        
        if concrete_parent:
            # This inherits from a concrete model, so don't add any fields or 
            # managers. Also, any MpttMeta classes will be ignored, since 
            # they won't have any effect
            return
        
        for attr, default in default_mptt_meta.items():
            if hasattr(cls, 'MpttMeta'):
                # Anything in MpttMeta overrides all
                meta_val = getattr(cls.MpttMeta, attr, None)
                if meta_val is not None:
                    setattr(cls._meta, attr, meta_val)
        
        if cls._meta.abstract or cls._meta.proxy:
            # Don't add any fields to abstract or proxy models
            return
        
        opts = cls._meta
        for attr in (opts.left_attr, opts.right_attr, 
                     opts.tree_id_attr, opts.level_attr):
            cls.add_to_class(attr, models.PositiveIntegerField(db_index=True, editable=False))
        cls.add_to_class(opts.tree_manager_attr, TreeManager(
                opts.parent_attr, opts.left_attr, opts.right_attr, 
                opts.tree_id_attr, opts.level_attr))
        setattr(cls, '_tree_manager', 
                getattr(cls, opts.tree_manager_attr))
        

class Model(models.Model):
    __metaclass__ = ModelBase
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """
        If this is a new node, sets tree fields up before it is inserted
        into the database, making room in the tree structure as neccessary,
        defaulting to making the new node the last child of its parent.

        It the node's left and right edge indicators already been set, we
        take this as indication that the node has already been set up for
        insertion, so its tree fields are left untouched.

        If this is an existing node and its parent has been changed,
        performs reparenting in the tree structure, defaulting to making the
        node the last child of its new parent.

        In either case, if the node's class has its ``order_insertion_by``
        tree option set, the node will be inserted or moved to the
        appropriate position to maintain ordering by the specified field.
        """
        
        opts = self._meta
        parent = getattr(self, opts.parent_attr)
        if not self.pk:
            # Set up this node for insertion if hasn't been done yet
            if (not getattr(self, opts.left_attr) or
                not getattr(self, opts.right_attr)):
                if opts.order_insertion_by:
                    right_sibling = _get_ordered_insertion_target(self, 
                                                                  parent)
                    if right_sibling:
                        self.insert_at(right_sibling, 'left')
                    else:
                        self.insert_at(parent, position='last-child')
                else:
                    # Default insertion
                    self.insert_at(parent, position='last-child')
        else:
            # TODO Is it possible to track the original parent so we
            #      don't have to look it up again on each save after the
            #      first?
            old_parent = getattr(self._default_manager.get(pk=self.pk),
                                 opts.parent_attr)
            if parent != old_parent:
                setattr(self, opts.parent_attr, old_parent)
                try:
                    if opts.order_insertion_by:
                        right_sibling = _get_ordered_insertion_target(self,
                                                                      parent)
                        if right_sibling:
                            self.move_to(right_sibling, 'left')
                        else:
                            self.move_to(parent, position='last-child')
                    else:
                        # Default movement
                        self.move_to(parent, position='last-child')
                finally:
                    # Make sure the self's new parent is always
                    # restored on the way out in case of errors.
                    setattr(self, opts.parent_attr, parent)
        super(Model, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        opts = self._meta
        tree_width = (getattr(self, opts.right_attr) -
                      getattr(self, opts.left_attr) + 1)
        target_right = getattr(self, opts.right_attr)
        tree_id = getattr(self, opts.tree_id_attr)
        self._tree_manager._close_gap(tree_width, target_right, tree_id)
        super(Model, self).delete(*args, **kwargs)
    
    def get_ancestors(self, ascending=False):
        """
        Creates a ``QuerySet`` containing the ancestors of this model
        instance.

        This defaults to being in descending order (root ancestor first,
        immediate parent last); passing ``True`` for the ``ascending``
        argument will reverse the ordering (immediate parent first, root
        ancestor last).
        """
        if self.is_root_node():
            return self._tree_manager.none()

        opts = self._meta
        return self._default_manager.filter(**{
            '%s__lt' % opts.left_attr: getattr(self, opts.left_attr),
            '%s__gt' % opts.right_attr: getattr(self, opts.right_attr),
            opts.tree_id_attr: getattr(self, opts.tree_id_attr),
        }).order_by('%s%s' % ({True: '-', False: ''}[ascending], opts.left_attr))

    def get_children(self):
        """
        Creates a ``QuerySet`` containing the immediate children of this
        model instance, in tree order.

        The benefit of using this method over the reverse relation
        provided by the ORM to the instance's children is that a
        database query can be avoided in the case where the instance is
        a leaf node (it has no children).
        """
        if self.is_leaf_node():
            return self._tree_manager.none()

        return self._tree_manager.filter(**{
            self._meta.parent_attr: self,
        })

    def get_descendants(self, include_self=False):
        """
        Creates a ``QuerySet`` containing descendants of this model
        instance, in tree order.

        If ``include_self`` is ``True``, the ``QuerySet`` will also
        include this model instance.
        """
        if not include_self and self.is_leaf_node():
            return self._tree_manager.none()

        opts = self._meta
        filters = {opts.tree_id_attr: getattr(self, opts.tree_id_attr)}
        if include_self:
            filters['%s__range' % opts.left_attr] = (getattr(self, opts.left_attr),
                                                     getattr(self, opts.right_attr))
        else:
            filters['%s__gt' % opts.left_attr] = getattr(self, opts.left_attr)
            filters['%s__lt' % opts.left_attr] = getattr(self, opts.right_attr)
        return self._tree_manager.filter(**filters)

    def get_descendant_count(self):
        """
        Returns the number of descendants this model instance has.
        """
        return (getattr(self, self._meta.right_attr) -
                getattr(self, self._meta.left_attr) - 1) / 2

    def get_next_sibling(self):
        """
        Returns this model instance's next sibling in the tree, or
        ``None`` if it doesn't have a next sibling.
        """
        opts = self._meta
        if self.is_root_node():
            filters = {
                '%s__isnull' % opts.parent_attr: True,
                '%s__gt' % opts.tree_id_attr: getattr(self, opts.tree_id_attr),
            }
        else:
            filters = {
                 opts.parent_attr: getattr(self, '%s_id' % opts.parent_attr),
                '%s__gt' % opts.left_attr: getattr(self, opts.right_attr),
            }

        sibling = None
        try:
            sibling = self._tree_manager.filter(**filters)[0]
        except IndexError:
            pass
        return sibling

    def get_previous_sibling(self):
        """
        Returns this model instance's previous sibling in the tree, or
        ``None`` if it doesn't have a previous sibling.
        """
        opts = self._meta
        if self.is_root_node():
            filters = {
                '%s__isnull' % opts.parent_attr: True,
                '%s__lt' % opts.tree_id_attr: getattr(self, opts.tree_id_attr),
            }
            order_by = '-%s' % opts.tree_id_attr
        else:
            filters = {
                 opts.parent_attr: getattr(self, '%s_id' % opts.parent_attr),
                '%s__lt' % opts.right_attr: getattr(self, opts.left_attr),
            }
            order_by = '-%s' % opts.right_attr

        sibling = None
        try:
            sibling = self._tree_manager.filter(**filters).order_by(order_by)[0]
        except IndexError:
            pass
        return sibling

    def get_root(self):
        """
        Returns the root node of this model instance's tree.
        """
        if self.is_root_node():
            return self

        opts = self._meta
        return self._default_manager.get(**{
            opts.tree_id_attr: getattr(self, opts.tree_id_attr),
            '%s__isnull' % opts.parent_attr: True,
        })

    def get_siblings(self, include_self=False):
        """
        Creates a ``QuerySet`` containing siblings of this model
        instance. Root nodes are considered to be siblings of other root
        nodes.

        If ``include_self`` is ``True``, the ``QuerySet`` will also
        include this model instance.
        """
        opts = self._meta
        if self.is_root_node():
            filters = {'%s__isnull' % opts.parent_attr: True}
        else:
            filters = {opts.parent_attr: getattr(self, '%s_id' % opts.parent_attr)}
        queryset = self._tree_manager.filter(**filters)
        if not include_self:
            queryset = queryset.exclude(pk=self.pk)
        return queryset

    def insert_at(self, target, position='first-child', commit=False):
        """
        Convenience method for calling ``TreeManager.insert_node`` with this
        model instance.
        """
        self._tree_manager.insert_node(self, target, position, commit)

    def is_child_node(self):
        """
        Returns ``True`` if this model instance is a child node, ``False``
        otherwise.
        """
        return not self.is_root_node()

    def is_leaf_node(self):
        """
        Returns ``True`` if this model instance is a leaf node (it has no
        children), ``False`` otherwise.
        """
        return not self.get_descendant_count()

    def is_root_node(self):
        """
        Returns ``True`` if this model instance is a root node,
        ``False`` otherwise.
        """
        return getattr(self, '%s_id' % self._meta.parent_attr) is None

    def move_to(self, target, position='first-child'):
        """
        Convenience method for calling ``TreeManager.move_node`` with this
        model instance.
        """
        self._tree_manager.move_node(self, target, position)


