from django.db import models

import mptt

class Category(mptt.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    def __unicode__(self):
        return self.name

    def delete(self):
        super(Category, self).delete()


class Genre(mptt.Model):
    name = models.CharField(max_length=50, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

    def __unicode__(self):
        return self.name


class Insert(mptt.Model):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')


class MultiOrder(mptt.Model):
    name = models.CharField(max_length=50)
    size = models.PositiveIntegerField()
    date = models.DateField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    
    class MpttMeta:
        order_insertion_by = ['name', 'size', 'date']
    
    def __unicode__(self):
        return self.name


class Node(mptt.Model):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    
    class MpttMeta:
        left_attr = 'does'
        right_attr = 'zis'
        level_attr = 'madness'
        tree_id_attr = 'work'


class OrderedInsertion(mptt.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    
    class MpttMeta:
        order_insertion_by = ['name']
    
    def __unicode__(self):
        return self.name


class Tree(mptt.Model):
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')


class AbstractModel(mptt.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    
    class Meta:
        abstract = True

class AnotherNode(AbstractModel):
    size = models.IntegerField()


class ProxyNode(AnotherNode):
    class Meta:
        proxy = True
    
    def get_next_sibling(self):
        return 'wurble'
    

class InheritAnotherNode(AnotherNode):
    number = models.IntegerField(default=101)

class CustomInheritAnotherNode(AnotherNode):
    number = models.IntegerField(default=101)
    
    class MpttMeta:
        left_attr = 'doesnothing'
        right_attr = 'atall'

class NoParentAbstractModel(mptt.Model):
    name = models.CharField(max_length=50)
    
    class Meta:
        abstract = True

class NoParentAnotherNode(NoParentAbstractModel):
    size = models.IntegerField()
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')

class NoParentProxyNode(NoParentAnotherNode):
    class Meta:
        proxy = True
    
    def get_next_sibling(self):
        return 'wurble'

class CustomAbstractModel(mptt.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    
    class Meta:
        abstract = True
    
    class MpttMeta:
        left_attr = 'leftle'
        right_attr = 'wrongone'
        

class CustomAnotherNode(CustomAbstractModel):
    size = models.IntegerField()
    
    class MpttMeta:
        right_attr = 'rightle'


class ProxyCustomAnotherNode(CustomAnotherNode):
    class Meta:
        proxy = True
    
    class MpttMeta:
        left_attr = 'doesnothing'
        right_attr = 'atall'
    

class LoadTreeNode(mptt.LoadTreeModel):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children')
    
    def __unicode__(self):
        return self.name
    
