
# various network tables utility routines
from pynetworktables import ITableListener, IRemoteConnectionListener

import glib
import gobject
import pynetworktables
import threading

class FakeListener(object):
    
    instance = None
    
    def __init__(self):
        self.thread = threading.Thread(target=self.thread_fn) 
        self.condition = threading.Condition()
        self.dict = {}
        self.last = {}
        
        FakeListener.instance = self
        self.do_stop = False
        
    def start(self):
        self.thread.start()
        
    def stop(self):
        with self.condition:
            self.do_stop = True
            self.condition.notify()
            
        self.thread.join()
        
    def AddTableListener(self, table, name, k, fn):
        tname = name + ' ' + k
        self.dict[tname] = (k, table, fn)
        self.last[tname] = None
        
    def thread_fn(self):
        
        while True:
            
            with self.condition:
                if self.do_stop:
                    break
                
                self.condition.wait(0.1)
                
                if self.do_stop:
                    break
                
            for tname, (k, table, fn) in self.dict.iteritems():
                value = None
                try:
                    if not table.ContainsKey(k):
                        continue
                    value = table.GetValue(k)
                except pynetworktables.TableKeyNotDefinedException:
                    # this happens on complex values
                    pass
                except Exception as e:
                    continue
                
                if k not in self.last or value != self.last[k] or value is None:
                    fn(table, k, value, True)
                    self.last[k] = value
                


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
        
    def attach(self, table, name, key=None):
        self.table = table
        if key is not None:
            FakeListener.instance.AddTableListener(table, name, key, self.ValueChanged)
            #table.AddTableListener(key, self, True)
        else:
            raise KeyError('oh hai')
            #table.AddTableListener(self)
        
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
        raise KeyError('not implemented')
        #table.AddSubTableListener(self)


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
    key = unicode(key)
    
    def _on_destroy(widget):
        '''Clean up after ourselves'''
        listener.detach()
    
    listener = UiListener(fn)
    listener.attach(table, '/', key)
    
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
    listener.attach(table, '/', key)
    
    # connect to the UI element
    toggled_id = widget.connect('toggled', _on_toggled)
    destroy_id = widget.connect('destroy', _on_destroy)
    
    

def attach_chooser(table, key, widget, on_choices, on_selected):
    '''Generic function to attach to a chooser variable'''
    
    key = unicode(key)
    last_choices = []
    
    def _get_choices():
        options = pynetworktables.StringArray()
        listener.table.RetrieveValue(u'options', options)
        return [options.get(i) for i in xrange(options.size())]
    
    def _get_selected():
        selected = listener.table.GetValue(u'selected')
        if selected is None:
            selected = listener.table.GetValue(u'default')
        return selected
                
    def _on_update(table_key, value):
        if table_key == u'options':
            choices = _get_choices()
            if choices != last_choices:
                on_choices(choices)
                on_selected(_get_selected())
                # can't assign because of scoping
                while len(last_choices) != 0:
                    last_choices.pop()
                last_choices.extend(choices)
        elif table_key == u'selected':
            on_selected(value)
        elif table_key == u'default':
            if listener.table.GetValue(u'selected') is None:
                on_selected(value)
    
    def _on_destroy(widget):
        '''Clean up after ourselves'''
        listener.detach()
    
    listener = UiListener(_on_update)
    
    subtable = table.GetSubTable(key)
    listener.attach(subtable, '/' + key + '/', u'options')
    listener.attach(subtable, '/' + key + '/', u'selected')
    listener.attach(subtable, '/' + key + '/', u'default')
    #listener.attach(subtable)
    
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
        
        print 'got me some choices'
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
            listener.table.PutString(u'selected', unicode(selected))

    
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
        listener.table.PutString(u'selected', unicode(selected))
    
    def _on_destroy(widget, id):
        widget.disconnect(id)
    
    # attach to widgets first
    for k, v in widgets.iteritems():
        id = v.connect('toggled', _on_toggle, k)
        v.connect('destroy', _on_destroy, id)
        widgets[k] = (v, id)
        widget = v
    
    listener = attach_chooser(table, key, widget, _on_choices, _on_selected)
    
    
# attach to a boolean
#def attach_boolean():
    # attach to a checkbox or something
    
    
# attach to a number
# -> not needed
#def attach_number():