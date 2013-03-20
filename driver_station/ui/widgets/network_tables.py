
# various network tables utility routines
from pynetworktables import ITableListener

import glib
import gobject
import pynetworktables

class Listener(ITableListener):
    '''Calls a function when a table value is updated'''
    
    def __init__(self, fn):
        '''fn must be a callable that takes (key, value)'''
        ITableListener.__init__(self)
        self.fn = fn
        
    def attach(self, table, key=None):
        self.table = table
        if key is not None:
            table.AddTableListener(key, self, True)
        else:
            table.AddTableListener(self)
        
    def detach(self):
        if hasattr(self, 'table'):
            self.table.RemoveTableListener(self)
        
    def ValueChanged(self, table, key, value, isNew):
        self.fn(key, table.GetValue(key))
    

class UiListener(Listener):
    '''Calls a function on the UI thread when a table value is updated'''
    
    def __init__(self, fn):
        '''fn must be a callable that takes (key, value)'''
        Listener.__init__(self, fn)
        
    def ValueChanged(self, table, key, value, isNew):
        glib.idle_add(self.fn, key, table.GetValue(key))

class UiSubtableListener(UiListener):
    
    def __init__(self, fn):
        UiListener.__init__(self, fn)
        
    def attach(self, table):
        self.table = table
        table.AddSubTableListener(self)


def attach_fn(table, key, fn, remove_widget):
    '''Attach a specific NetworkTable key to a fn, removed when a widget dies'''
    key = unicode(key)
    
    def _on_destroy(widget):
        '''Clean up after ourselves'''
        listener.detach()
    
    listener = UiListener(fn)
    listener.attach(table, key)
    
    remove_widget.connect('destroy', _on_destroy)


def attach_toggle(table, key, widget):
    '''Attach a specific NetworkTable key to a ToggleButton or similar'''
    
    key = unicode(key)
    
    def _on_toggled(widget):
        table.PutBoolean(key, widget.get_active())
    
    def _on_update(table_key, value):
        widget.handler_block(toggled_id)       # don't re-enter
        widget.set_active(value)
        widget.handler_unblock(toggled_id)
        
    def _on_destroy(widget):
        '''Clean up after ourselves'''
        listener.detach()
        widget.disconnect(toggled_id)
        widget.disconnect(destroy_id)
        
    # connect to the table
    listener = UiListener(_on_update)
    listener.attach(table, key)
    
    # connect to the UI element
    toggled_id = widget.connect('toggled', _on_toggled)
    destroy_id = widget.connect('destroy', _on_destroy)
    
    
    
# TODO: more generic

def attach_chooser_combo(table, key, widget):
    '''Attach a chooser widget to a combo box'''
    
    # TODO: need to be able to save/restore these values
    # for setting autonomous mode.. 
    
    key = unicode(key)
    
    def _set_selected(value):
        for i, row in enumerate(widget.get_model()):
            if row[0] == value:
                widget.handler_block(changed_id)
                widget.set_active(i)
                widget.handler_unblock(changed_id)
                break
    
    def _setup_choices(subtable):
        
        choices = pynetworktables.StringArray()
        subtable.RetrieveValue(u'options', choices)
        
        widget.handler_block(changed_id)
        
        model = widget.get_model()
        model.clear()
        
        for i in xrange(choices.size()):
            model.append((choices.get(i),))
        
        widget.handler_unblock(changed_id)
            
        _set_selected(subtable.GetString(u'selected'))
        

    def _on_subtable_update(table_key, value):
        if table_key == key:
            subtable = table.GetSubTable(table_key)
            listener.attach(subtable)
            
            _setup_choices(subtable)
                
    def _on_update(table_key, value):
        if table_key == u'choices':
            _setup_choices(listener.table)
        elif table_key == u'selected':
            _set_selected(value)
            
    def _on_combo_changed(widget):
        active = widget.get_active_iter()
        if active:
            selected = widget.get_model()[active][0]
            if hasattr(listener, 'table'):
                listener.table.PutString(u'selected', unicode(selected))

    def _on_destroy(widget):
        '''Clean up after ourselves'''
        sublistener.detach()
        listener.detach()

    # attach to buttons
    listener = UiListener(_on_update)
    
    sublistener = UiSubtableListener(_on_subtable_update)
    sublistener.attach(table)
    
    changed_id = widget.connect('changed', _on_combo_changed)
    widget.connect('destroy', _on_destroy)
    
    
    
    
# attach to a boolean
#def attach_boolean():
    # attach to a checkbox or something
    
    
# attach to a number
# -> not needed
#def attach_number():