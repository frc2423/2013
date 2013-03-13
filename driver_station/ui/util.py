
import os

import gtk


def initialize_from_xml(this, other=None):
    '''
        Initializes the widgets and signals from a GtkBuilder XML file. Looks 
        for the following attributes in the instance you pass:
        
        ui_filename = builder filename
        ui_widgets = [list of widget names]
        ui_signals = [list of function names to connect to a signal]
        
        For each widget in ui_widgets, it will be retrieved from the builder
        object and 
        
        other is a list of widgets to also initialize with the same file
        
        Returns the builder object when done
    '''
    builder = gtk.Builder()
    builder.add_from_file(os.path.join(os.path.dirname(__file__), 'data', this.ui_filename))
    
    objects = [this]
    if other is not None:
        objects.extend(other)
    
    for obj in objects:
        if hasattr(obj, 'ui_widgets') and obj.ui_widgets is not None:
            for widget_name in obj.ui_widgets:
                widget = builder.get_object(widget_name)
                if widget is None:
                    raise RuntimeError("Widget '%s' is not present in '%s'" % (widget_name, this.ui_filename))
                setattr(obj, widget_name, widget)
    
    signals = None
    
    for obj in objects:
        if hasattr(obj, 'ui_signals') and obj.ui_signals is not None:
            if signals is None:
                signals = {}
            for signal_name in obj.ui_signals:
                if not hasattr(obj, signal_name):
                    raise RuntimeError("Function '%s' is not present in '%s'" % (signal_name, obj))
                signals[signal_name] = getattr(obj, signal_name)
            
    if signals is not None:
        missing = builder.connect_signals(signals, None)
        if missing is not None:
            err = 'The following signals were found in %s but have no assigned handler: %s' % (this.ui_filename, str(missing))
            raise RuntimeError(err)
    
    return builder


def replace_widget(old_widget, new_widget):
    
    # TODO: This could be better
    
    parent = old_widget.get_parent()                                                                                                                                                                                                           
    packing = None                                                                                                                                                                                                                             
    position = None                                                                                                                                                                                                                            
                                                                                                                                                                                                                                               
    try:                                                                                                                                                                                                                                       
        position = parent.child_get_property(old_widget, 'position')                                                                                                                                                                           
    except:                                                                                                                                                                                                                                    
        pass                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                               
    try:                                                                                                                                                                                                                                       
        packing = parent.query_child_packing(old_widget)                                                                                                                                                                                       
    except:                                                                                                                                                                                                                                    
        pass                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                               
    parent.remove(old_widget)                                                                                                                                                                                                                  
    new_widget.unparent()                                                                                                                                                                                                                      
    parent.add(new_widget)                                                                                                                                                                                                                     
                                                                                                                                                                                                                                               
    if position is not None:                                                                                                                                                                                                                   
        parent.child_set_property(new_widget, 'position', position)                                                                                                                                                                            
                                                                                                                                                                                                                                               
    if packing is not None:                                                                                                                                                                                                                    
        parent.set_child_packing(new_widget, *packing)    
        
    return new_widget
