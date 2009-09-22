import re

from django.test import TestCase

from mptt.exceptions import InvalidMove
from mptt.tests import doctests
from mptt.tests.models import Category, Genre, AnotherNode, NoParentAnotherNode, ProxyNode, NoParentProxyNode, CustomInheritAnotherNode, InheritAnotherNode, CustomAnotherNode, ProxyCustomAnotherNode

def get_tree_details(nodes):
    """Creates pertinent tree details for the given list of nodes."""
    opts = nodes[0]._meta
    return '\n'.join(['%s %s %s %s %s %s' %
                      (n.pk, getattr(n, '%s_id' % opts.parent_attr) or '-',
                       getattr(n, opts.tree_id_attr), getattr(n, opts.level_attr),
                       getattr(n, opts.left_attr), getattr(n, opts.right_attr))
                      for n in nodes])

leading_whitespace_re = re.compile(r'^\s+', re.MULTILINE)

def tree_details(text):
    """
    Trims leading whitespace from the given text specifying tree details
    so triple-quoted strings can be used to provide tree details in a
    readable format (says who?), to be compared with the result of using
    the ``get_tree_details`` function.
    """
    return leading_whitespace_re.sub('', text)

# genres.json defines the following tree structure
#
# 1 - 1 0 1 16   action
# 2 1 1 1 2 9    +-- platformer
# 3 2 1 2 3 4    |   |-- platformer_2d
# 4 2 1 2 5 6    |   |-- platformer_3d
# 5 2 1 2 7 8    |   +-- platformer_4d
# 6 1 1 1 10 15  +-- shmup
# 7 6 1 2 11 12      |-- shmup_vertical
# 8 6 1 2 13 14      +-- shmup_horizontal
# 9 - 2 0 1 6    rpg
# 10 9 2 1 2 3   |-- arpg
# 11 9 2 1 4 5   +-- trpg

class ReparentingTestCase(TestCase):
    """
    Test that trees are in the appropriate state after reparenting and
    that reparented items have the correct tree attributes defined,
    should they be required for use after a save.
    """
    fixtures = ['genres.json']

    def test_new_root_from_subtree(self):
        shmup = Genre.objects.get(id=6)
        shmup.parent = None
        shmup.save()
        self.assertEqual(get_tree_details([shmup]), '6 - 3 0 1 6')
        self.assertEqual(get_tree_details(Genre.tree.all()),
                         tree_details("""1 - 1 0 1 10
                                         2 1 1 1 2 9
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 2 1 2 7 8
                                         9 - 2 0 1 6
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5
                                         6 - 3 0 1 6
                                         7 6 3 1 2 3
                                         8 6 3 1 4 5"""))

    def test_new_root_from_leaf_with_siblings(self):
        platformer_2d = Genre.objects.get(id=3)
        platformer_2d.parent = None
        platformer_2d.save()
        self.assertEqual(get_tree_details([platformer_2d]), '3 - 3 0 1 2')
        self.assertEqual(get_tree_details(Genre.tree.all()),
                         tree_details("""1 - 1 0 1 14
                                         2 1 1 1 2 7
                                         4 2 1 2 3 4
                                         5 2 1 2 5 6
                                         6 1 1 1 8 13
                                         7 6 1 2 9 10
                                         8 6 1 2 11 12
                                         9 - 2 0 1 6
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5
                                         3 - 3 0 1 2"""))

    def test_new_child_from_root(self):
        action = Genre.objects.get(id=1)
        rpg = Genre.objects.get(id=9)
        action.parent = rpg
        action.save()
        self.assertEqual(get_tree_details([action]), '1 9 2 1 6 21')
        self.assertEqual(get_tree_details(Genre.tree.all()),
                         tree_details("""9 - 2 0 1 22
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5
                                         1 9 2 1 6 21
                                         2 1 2 2 7 14
                                         3 2 2 3 8 9
                                         4 2 2 3 10 11
                                         5 2 2 3 12 13
                                         6 1 2 2 15 20
                                         7 6 2 3 16 17
                                         8 6 2 3 18 19"""))

    def test_move_leaf_to_other_tree(self):
        shmup_horizontal = Genre.objects.get(id=8)
        rpg = Genre.objects.get(id=9)
        shmup_horizontal.parent = rpg
        shmup_horizontal.save()
        self.assertEqual(get_tree_details([shmup_horizontal]), '8 9 2 1 6 7')
        self.assertEqual(get_tree_details(Genre.tree.all()),
                         tree_details("""1 - 1 0 1 14
                                         2 1 1 1 2 9
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 2 1 2 7 8
                                         6 1 1 1 10 13
                                         7 6 1 2 11 12
                                         9 - 2 0 1 8
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5
                                         8 9 2 1 6 7"""))

    def test_move_subtree_to_other_tree(self):
        shmup = Genre.objects.get(id=6)
        trpg = Genre.objects.get(id=11)
        shmup.parent = trpg
        shmup.save()
        self.assertEqual(get_tree_details([shmup]), '6 11 2 2 5 10')
        self.assertEqual(get_tree_details(Genre.tree.all()),
                         tree_details("""1 - 1 0 1 10
                                         2 1 1 1 2 9
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 2 1 2 7 8
                                         9 - 2 0 1 12
                                         10 9 2 1 2 3
                                         11 9 2 1 4 11
                                         6 11 2 2 5 10
                                         7 6 2 3 6 7
                                         8 6 2 3 8 9"""))

    def test_move_child_up_level(self):
        shmup_horizontal = Genre.objects.get(id=8)
        action = Genre.objects.get(id=1)
        shmup_horizontal.parent = action
        shmup_horizontal.save()
        self.assertEqual(get_tree_details([shmup_horizontal]), '8 1 1 1 14 15')
        self.assertEqual(get_tree_details(Genre.tree.all()),
                         tree_details("""1 - 1 0 1 16
                                         2 1 1 1 2 9
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 2 1 2 7 8
                                         6 1 1 1 10 13
                                         7 6 1 2 11 12
                                         8 1 1 1 14 15
                                         9 - 2 0 1 6
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5"""))

    def test_move_subtree_down_level(self):
        shmup = Genre.objects.get(id=6)
        platformer = Genre.objects.get(id=2)
        shmup.parent = platformer
        shmup.save()
        self.assertEqual(get_tree_details([shmup]), '6 2 1 2 9 14')
        self.assertEqual(get_tree_details(Genre.tree.all()),
                         tree_details("""1 - 1 0 1 16
                                         2 1 1 1 2 15
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 2 1 2 7 8
                                         6 2 1 2 9 14
                                         7 6 1 3 10 11
                                         8 6 1 3 12 13
                                         9 - 2 0 1 6
                                         10 9 2 1 2 3
                                         11 9 2 1 4 5"""))

    def test_invalid_moves(self):
        # A node may not be made a child of itself
        action = Genre.objects.get(id=1)
        action.parent = action
        platformer = Genre.objects.get(id=2)
        platformer.parent = platformer
        self.assertRaises(InvalidMove, action.save)
        self.assertRaises(InvalidMove, platformer.save)

        # A node may not be made a child of any of its descendants
        platformer_4d = Genre.objects.get(id=5)
        action.parent = platformer_4d
        platformer.parent = platformer_4d
        self.assertRaises(InvalidMove, action.save)
        self.assertRaises(InvalidMove, platformer.save)

        # New parent is still set when an error occurs
        self.assertEquals(action.parent, platformer_4d)
        self.assertEquals(platformer.parent, platformer_4d)

# categories.json defines the following tree structure:
#
# 1 - 1 0 1 20    games
# 2 1 1 1 2 7     +-- wii
# 3 2 1 2 3 4     |   |-- wii_games
# 4 2 1 2 5 6     |   +-- wii_hardware
# 5 1 1 1 8 13    +-- xbox360
# 6 5 1 2 9 10    |   |-- xbox360_games
# 7 5 1 2 11 12   |   +-- xbox360_hardware
# 8 1 1 1 14 19   +-- ps3
# 9 8 1 2 15 16       |-- ps3_games
# 10 8 1 2 17 18      +-- ps3_hardware

class DeletionTestCase(TestCase):
    """
    Tests that the tree structure is maintained appropriately in various
    deletion scenrios.
    """
    fixtures = ['categories.json']

    def test_delete_root_node(self):
        # Add a few other roots to verify that they aren't affected
        Category(name='Preceding root').insert_at(Category.objects.get(id=1),
                                                  'left', commit=True)
        Category(name='Following root').insert_at(Category.objects.get(id=1),
                                                  'right', commit=True)
        s = get_tree_details(Category.tree.all())
        self.assertEqual(s,
                         tree_details("""11 - 1 0 1 2
                                         1 - 2 0 1 20
                                         2 1 2 1 2 7
                                         3 2 2 2 3 4
                                         4 2 2 2 5 6
                                         5 1 2 1 8 13
                                         6 5 2 2 9 10
                                         7 5 2 2 11 12
                                         8 1 2 1 14 19
                                         9 8 2 2 15 16
                                         10 8 2 2 17 18
                                         12 - 3 0 1 2"""),
                         'Setup for test produced unexpected result: %s' % s)

        Category.objects.get(id=1).delete()
        self.assertEqual(get_tree_details(Category.tree.all()),
                         tree_details("""11 - 1 0 1 2
                                         12 - 3 0 1 2"""))

    def test_delete_last_node_with_siblings(self):
        Category.objects.get(id=9).delete()
        self.assertEqual(get_tree_details(Category.tree.all()),
                         tree_details("""1 - 1 0 1 18
                                         2 1 1 1 2 7
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 1 1 1 8 13
                                         6 5 1 2 9 10
                                         7 5 1 2 11 12
                                         8 1 1 1 14 17
                                         10 8 1 2 15 16"""))

    def test_delete_last_node_with_descendants(self):
        Category.objects.get(id=8).delete()
        self.assertEqual(get_tree_details(Category.tree.all()),
                         tree_details("""1 - 1 0 1 14
                                         2 1 1 1 2 7
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 1 1 1 8 13
                                         6 5 1 2 9 10
                                         7 5 1 2 11 12"""))

    def test_delete_node_with_siblings(self):
        Category.objects.get(id=6).delete()
        self.assertEqual(get_tree_details(Category.tree.all()),
                         tree_details("""1 - 1 0 1 18
                                         2 1 1 1 2 7
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 1 1 1 8 11
                                         7 5 1 2 9 10
                                         8 1 1 1 12 17
                                         9 8 1 2 13 14
                                         10 8 1 2 15 16"""))

    def test_delete_node_with_descendants_and_siblings(self):
        """
        Regression test for Issue 23 - we used to use pre_delete, which
        resulted in tree cleanup being performed for every node being
        deleted, rather than just the node on which ``delete()`` was
        called.
        """
        Category.objects.get(id=5).delete()
        self.assertEqual(get_tree_details(Category.tree.all()),
                         tree_details("""1 - 1 0 1 14
                                         2 1 1 1 2 7
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         8 1 1 1 8 13
                                         9 8 1 2 9 10
                                         10 8 1 2 11 12"""))

class IntraTreeMovementTestCase(TestCase):
    pass

class InterTreeMovementTestCase(TestCase):
    pass

class PositionedInsertionTestCase(TestCase):
    pass


class BaseInheritanceTest(object):
    def setUp(self):
        root = self.model.objects.create(name='A root node', size=10)
        root = self.model.objects.get(pk=root.pk)
        n1 = self.model.objects.create(parent=root, name='First child', size=3)
        n1 = self.model.objects.get(pk=n1.pk)
        self.model.objects.create(parent=n1, name='First child of first child', size=1)
        n1 = self.model.objects.get(pk=n1.pk)
        self.model.objects.create(parent=n1, name='Second child of first child', size=4)
        root = self.model.objects.get(pk=root.pk)
        self.model.objects.create(parent=root, name='Second child', size=2)
        
        self.root = self.model.objects.get(pk=root.pk)

    def test_fields(self):
        self.assertEqual(self.root.name, 'A root node')
        self.assertEqual(self.root.size, 10)
        self.assertEqual(self.root.parent, None)
        self.assertEqual(self.root.lft, 1)
        self.assertEqual(self.root.rght, 10)
        self.assertEqual(self.root.level, 0)
        self.assertTrue(self.root.tree_id > 0)
        
    def test_creation(self):
        self.assertEqual(get_tree_details(self.model.tree.all()),
                         tree_details("""1 - 1 0 1 10
                                         2 1 1 1 2 7
                                         3 2 1 2 3 4
                                         4 2 1 2 5 6
                                         5 1 1 1 8 9"""))
    
    def test_move(self):
        """
        Test an operation just to ensure the options are working correctly.
        """
        n = self.root.get_children()[0].get_children()[1]
        n.move_to(self.root, position='last-child')
        self.assertEqual(self.root.get_children()[2], n)
        

class AnotherNodeTest(BaseInheritanceTest, TestCase):
    """
    Test a model that inherits from an abstract model with a parent field that 
    inherits from mptt.Model.
    """
    model = AnotherNode
    
class NoParentAnotherNodeTest(AnotherNodeTest):
    """
    Test a model with a parent field that inherits from an abstract model that 
    inherits from mptt.Model.
    """
    model = NoParentAnotherNode

class ProxyNodeTest(BaseInheritanceTest, TestCase):
    """
    Test a proxy model that inherits from a normal model that inherits from an 
    abstract model with a parent field that inherits from mptt.Model.
    """
    model = ProxyNode
    
    def test_overriden_method(self):
        assert self.root.get_next_sibling() == 'wurble'
    
class NoParentProxyNodeTest(ProxyNodeTest):
    """
    Test a proxy model that inherits from a normal model with a parent field 
    that inherits from an abstract model that inherits from mptt.Model.
    """
    model = NoParentProxyNode


class InheritAnotherNodeTest(BaseInheritanceTest, TestCase):
    """
    Test a normal model inheriting from another normal model which inherits 
    from an abstract model with a parent field which inherits from mptt.Model.
    """
    model = InheritAnotherNode
    
    def test_additional_field(self):
        self.assertEqual(self.root.number, 101)


class CustomInheritAnotherNodeTest(InheritAnotherNodeTest):
    """
    Test that setting MPTT options on an inherited model does nothing.
    """
    model = CustomInheritAnotherNode


class CustomAnotherNodeTest(BaseInheritanceTest, TestCase):
    """
    Test a model with MPTT options set that inherits from and overrides some 
    options on an abstract model which inherits from mptt.Model.
    """
    model = CustomAnotherNode

    def test_fields(self):
        self.assertEqual(self.root.name, 'A root node')
        self.assertEqual(self.root.size, 10)
        self.assertEqual(self.root.parent, None)
        self.assertEqual(self.root.leftle, 1)
        self.assertEqual(self.root.rightle, 10)
        self.assertEqual(self.root.level, 0)
        self.assertTrue(self.root.tree_id > 0)

class ProxyCustomAnotherNodeTest(CustomAnotherNodeTest):
    """
    Test that setting MPTT options on a proxy model does nothing.
    """
    model = ProxyCustomAnotherNode
    

