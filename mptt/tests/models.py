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

