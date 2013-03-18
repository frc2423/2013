
from common import settings
import ui.util

class CameraSettings(object):
    '''
        Camera debugging settings
    '''
    
    ui_widgets = [
        'adj_thresh_hue_p',
        'adj_thresh_hue_n',
        'adj_thresh_sat',
        'adj_thresh_val',
    ]
    
    ui_signals = [
        'on_adj_thresh_hue_p_value_changed',
        'on_adj_thresh_hue_n_value_changed',
        'on_adj_thresh_sat_value_changed',
        'on_adj_thresh_val_value_changed',
        
        'on_check_show_hue_p_toggled',
        'on_check_show_hue_n_toggled',
        'on_check_show_sat_toggled',
        'on_check_show_val_toggled',
        'on_check_show_bin_toggled',
        
        'on_check_show_contours_toggled',
        'on_check_show_missed_toggled',
        'on_check_show_badratio_toggled',
        'on_check_show_ratio_labels_toggled',
        'on_check_show_labels_toggled',
        'on_check_show_targets_toggled',
        
        'on_camera_refresh_clicked'
    ]
    
    def __init__(self, processor):
        self.processor = processor
        
        
    def initialize(self):
        detector = self.processor.detector
        
        self.adj_thresh_hue_p.set_value(settings.get('camera/thresh_hue_p', detector.thresh_hue_p))
        self.adj_thresh_hue_n.set_value(settings.get('camera/thresh_hue_n', detector.thresh_hue_n))
        self.adj_thresh_sat.set_value(settings.get('camera/thresh_sat', detector.thresh_sat))
        self.adj_thresh_val.set_value(settings.get('camera/thresh_val', detector.thresh_val))
    
    def _on_thresh(self, widget, name):
        v = widget.get_value()
        settings.set('camera/%s' % name, v)
        setattr(self.processor.detector, name, v)
        self.processor.refresh()
        
    on_adj_thresh_hue_p_value_changed = lambda self, w: self._on_thresh(w, 'thresh_hue_p')
    on_adj_thresh_hue_n_value_changed = lambda self, w: self._on_thresh(w, 'thresh_hue_n')
    on_adj_thresh_sat_value_changed = lambda self, w: self._on_thresh(w, 'thresh_sat')
    on_adj_thresh_val_value_changed = lambda self, w: self._on_thresh(w, 'thresh_val') 
            
    def on_check_show_hue_p_toggled(self, widget):
        self.processor.detector.show_hue = widget.get_active()
        self.processor.refresh()
        
    def on_check_show_hue_n_toggled(self, widget):
        self.processor.detector.show_hue = widget.get_active()
        self.processor.refresh()
    
    def on_check_show_sat_toggled(self, widget):
        self.processor.detector.show_sat = widget.get_active()
        self.processor.refresh()
    
    def on_check_show_val_toggled(self, widget):
        self.processor.detector.show_val = widget.get_active()
        self.processor.refresh()
        
    def on_check_show_bin_toggled(self, widget):
        self.processor.detector.show_bin = widget.get_active()
        self.processor.refresh()
        
    def on_check_show_contours_toggled(self, widget):
        self.processor.detector.show_contours = widget.get_active()
        self.processor.refresh()
        
    def on_check_show_missed_toggled(self, widget):
        self.processor.detector.show_missed = widget.get_active()
        self.processor.refresh()
        
    def on_check_show_badratio_toggled(self, widget):
        self.processor.detector.show_badratio = widget.get_active()
        self.processor.refresh()
        
    def on_check_show_ratio_labels_toggled(self, widget):
        self.processor.detector.show_ratio_labels = widget.get_active()
        self.processor.refresh()
        
    def on_check_show_labels_toggled(self, widget):
        self.processor.detector.show_labels = widget.get_active()
        self.processor.refresh()
        
    def on_check_show_targets_toggled(self, widget):
        self.processor.detector.show_targets = widget.get_active()
        self.processor.refresh()
        
    def on_camera_refresh_clicked(self, widget):
        self.processor.refresh()
        
