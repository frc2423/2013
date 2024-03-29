#
#   This file is part of KwarqsDashboard.
#
#   KwarqsDashboard is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, version 3.
#
#   KwarqsDashboard is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with KwarqsDashboard.  If not, see <http://www.gnu.org/licenses/>.
#

'''
    This file contains functions that allow you to connect a widget or set
    of widgets with a NetworkTables variable. These functions will 
    automatically update the widget as the variable is updated over the
    network. 
'''


# various network tables utility routines
from pynetworktables import ITableListener, IRemoteConnectionListener

import glib
import gobject
import pynetworktables


class RemoteListener(IRemoteConnectionListener):
    '''Calls a function when a table value is updated'''
    
    def __init__(self, connect_fn, disconnect_fn):
        '''fn must be a callable that takes (value)'''
        IRemoteConnectionListener.__init__(self)
        self.connect_fn = connect_fn
        self.disconnect_fn = disconnect_fn
        
    def attach(self, table):
        self.table = table
        table.AddConnectionListener(self, True)
        
    def detach(self):
        if hasattr(self, 'table'):
            self.table.RemoveConnectionListener(self)
        
    def Connected(self, remote):
        self.connect_fn(remote)
        
    def Disconnected(self, remote):
        self.disconnect_fn(remote)
        
class UiRemoteListener(RemoteListener):
    '''Calls a function on the UI thread when a table value is updated'''
    
    def __init__(self, connect_fn, disconnect_fn):
        '''fn must be a callable that takes (value)'''
        RemoteListener.__init__(self, connect_fn, disconnect_fn)
        
    def Connected(self, remote):
        glib.idle_add(self.connect_fn, remote)
        
    def Disconnected(self, remote):
        glib.idle_add(self.disconnect_fn, remote)
        

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
    '''Calls a function on the UI thread when a Subtable is created'''
    
    def __init__(self, fn):
        UiListener.__init__(self, fn)
        
    def attach(self, table):
        self.table = table
        table.AddSubTableListener(self)


def attach_connection_listener(table, connect_fn, disconnect_fn, remove_widget):
    '''Wait for connection notifications, removed when a widget dies'''
    
    def _on_destroy(widget):
        '''Clean up after ourselves'''
        listener.detach()
    
    listener = UiRemoteListener(connect_fn, disconnect_fn)
    listener.attach(table)
    
    remove_widget.connect('destroy', _on_destroy)
    

def attach_fn(table, key, fn, remove_widget):
    '''Attach a specific NetworkTable key to a fn, removed when a widget dies'''
    
    def _on_destroy(widget):
        '''Clean up after ourselves'''
        listener.detach()
    
    listener = UiListener(fn)
    listener.attach(table, key)
    
    remove_widget.connect('destroy', _on_destroy)


def attach_toggle(table, key, widget):
    '''Attach a specific NetworkTable key to a ToggleButton or similar'''
    
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
    
    

def attach_chooser(table, key, widget, on_choices, on_selected):
    '''Generic function to attach to a chooser variable'''
    
    def _get_choices():
        options = pynetworktables.StringArray()
        listener.table.RetrieveValue('options', options)
        return [options.get(i) for i in xrange(options.size())]
    
    def _get_selected():
        selected = listener.table.GetValue('selected')
        if selected is None:
            selected = listener.table.GetValue('default')
        return selected
                
    def _on_update(table_key, value):
        if table_key == 'options':
            on_choices(_get_choices())
            on_selected(_get_selected())
        elif table_key == 'selected':
            on_selected(value)
        elif table_key == 'default':
            if listener.table.GetValue('selected') is None:
                on_selected(value)
    
    def _on_destroy(widget):
        '''Clean up after ourselves'''
        listener.detach()
    
    listener = UiListener(_on_update)
    
    subtable = table.GetSubTable(key)
    listener.attach(subtable)
    
    widget.connect('destroy', _on_destroy)
    
    return listener


def attach_chooser_combo(table, key, widget):
    '''Attach a chooser widget to a combo box'''
    
    # TODO: need to be able to save/restore these values
    # for setting autonomous mode.. 

    def _on_choices(choices):
        widget.handler_block(changed_id)
        
        model = widget.get_model()
        model.clear()
        
        for choice in choices:
            model.append((choice,))
        
        widget.handler_unblock(changed_id)
            
    def _on_selected(value):
        for i, row in enumerate(widget.get_model()):
            if row[0] == value:
                widget.handler_block(changed_id)
                widget.set_active(i)
                widget.handler_unblock(changed_id)
                break
            
    def _on_combo_changed(widget):
        active = widget.get_active_iter()
        if active:
            selected = widget.get_model()[active][0]
            listener.table.PutString('selected', selected)

    
    listener = attach_chooser(table, key, widget, _on_choices, _on_selected)
    changed_id = widget.connect('changed', _on_combo_changed)
    
def attach_chooser_buttons(table, key, widgets):
    '''widgets is a dictionary {'option': toggle button}'''
    
    def _on_choices(choices):
        # TODO: log that the choices don't match?
        pass
    
    def _on_selected(value):
        for k, (button, id) in widgets.iteritems():
            button.handler_block(id)
            button.set_active(k == value)
            button.handler_unblock(id)
            
    def _on_toggle(widget, selected):
        listener.table.PutString('selected', selected)
    
    def _on_destroy(widget, id):
        widget.disconnect(id)
    
    # attach to widgets first
    for k, v in widgets.iteritems():
        id = v.connect('toggled', _on_toggle, k)
        v.connect('destroy', _on_destroy, id)
        widgets[k] = (v, id)
        widget = v
    
    listener = attach_chooser(table, key, widget, _on_choices, _on_selected)
