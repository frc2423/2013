
import os

import gtk


def initialize_from_builder(this):
    '''
        Initializes the widgets and signals from a GtkBuilder XML file. Looks 
        for the following attributes in the instance you pass:
        
        ui_filename = builder filename
        ui_widgets = [list of widget names]
        ui_signals = [list of function names to connect to a signal]
        
        For each widget in ui_widgets, it will be retrieved from the builder
        object and 
        
        Returns the builder object when done
    '''
    builder = gtk.Builder()
    builder.add_from_file(os.path.join(os.path.dirname(__file__), 'data', this.ui_filename))
    
    if hasattr(this, 'ui_widgets') and this.ui_widgets is not None:
        for widget_name in this.ui_widgets:
            widget = builder.get_object(widget_name)
            if widget is None:
                raise RuntimeError("Widget '%s' is not present in '%s'" % (widget_name, this.ui_filename))
            setattr(this, widget_name, widget)
    
    if hasattr(this, 'ui_signals') and this.ui_signals is not None:
        signals = {}
        for signal_name in this.ui_signals:
            if not hasattr(this, signal_name):
                raise RuntimeError("Function '%s' is not present in '%s'" % (signal_name, this))
            signals[signal_name] = getattr(this, signal_name)
            
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
