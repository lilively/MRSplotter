from os import path
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt6.QtGui import QIcon, QAction


class CustomNavigationToolbar(NavigationToolbar):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.canvas = canvas
        self.parent = parent
       
        # Determine if we're in dark mode
        is_dark_mode = self.palette().window().color().lightness() < 128
           
        save_index = -1
        for i, action in enumerate(self.actions()):
            if action.text() == "Save" or action.toolTip() == "Save the figure":
                save_index = i
                break
        
        # Font Size Action
        self.fontSizeAction = QAction(self)
        self.fontSizeAction.setToolTip("Change Font Size")
        self.fontSizeAction.triggered.connect(self.parent.change_font_size)
        
        # Legend Action
        self.legend_action = QAction(self)
        self.legend_action.setCheckable(True)
        self.legend_action.setChecked(False)
        self.legend_action.setToolTip("Change legend visibility")
        self.legend_action.triggered.connect(self.toggle_legend)

        # Reset Action
        self.reset_action = QAction(self)
        self.reset_action.setToolTip("Reset Figure")
        self.reset_action.triggered.connect(self.parent.reset_figure)

        if save_index >= 0:
            self.insertAction(self.actions()[save_index + 1], self.fontSizeAction)
            self.insertAction(self.actions()[save_index + 2], self.legend_action)
            self.insertAction(self.actions()[save_index + 3], self.reset_action)
        else:
            self.addAction(self.fontSizeAction)
            self.addAction(self.legend_action)
            self.addAction(self.reset_action)

        # Setup icons based on theme - ONLY ONCE
        if is_dark_mode:
            self.setup_dark_mode_icons()
        else:
            self.setup_light_mode_icons()

        
    def toggle_legend(self):
        for ax in self.canvas.figure.get_axes():
            legend = ax.get_legend()
            if legend:
                # When action is checked=True, hide legend
                # When action is checked=False, show legend (icon appears pressed)
                legend.set_visible(not self.legend_action.isChecked())
        self.canvas.draw()
        
        is_checked = self.legend_action.isChecked()
        if is_checked:
            self.legend_action.setToolTip("Click to add legend")
        else:
            self.legend_action.setToolTip("Click to remove legend")
    
    
    def setup_dark_mode_icons(self):
        icon_mapping = {
        'Home': 'go-home',
        'Back': 'go-previous',
        'Forward': 'go-next',
        'Pan': 'transform-move',
        'Zoom': 'zoom-in',
        'Subplot': 'view-grid',
        'Save': 'document-save'
        }

        # Iterate through actions and replace icons
        for action in self.actions():
            text = action.text()
            if text in icon_mapping:
                try:
                    theme_icon = QIcon.fromTheme(icon_mapping[text])
                    if not theme_icon.isNull():
                        action.setIcon(theme_icon)
                        # Special handling for problematic icons in dark mode
                        if text in ['Pan', 'Subplot']:
                            action.setIconVisibleInMenu(True)
                except Exception:
                    pass  
        
        # Set font size icon
        if hasattr(self, 'fontSizeAction'):
            self.fontSizeAction.setIcon(QIcon.fromTheme("preferences-desktop-font"))
        
        # Set reset icon
        if hasattr(self, 'reset_action'):
            self.reset_action.setIcon(QIcon.fromTheme("view-refresh"))

        # Set legend icon
        if hasattr(self, 'legend_action'):
            dark_legend_path = path.join(path.dirname(path.abspath(__file__)), "resources", "edit-label-darkmode.png")
            if path.exists(dark_legend_path):
                self.legend_action.setIcon(QIcon(dark_legend_path))
            else:
                self.legend_action.setIcon(QIcon.fromTheme("view-list-details"))

        # Set Customize (edit axis) icon
        for action in self.actions():
            if action.text() == "Customize":
                axes_path = path.join(path.dirname(path.abspath(__file__)), "resources", "plot_axes_white.png")
                if path.exists(axes_path):
                    action.setIcon(QIcon(axes_path))
                break

    def setup_light_mode_icons(self):
        icon_mapping = {
            'Home': 'go-home',
            'Back': 'go-previous',
            'Forward': 'go-next',
            'Pan': 'transform-move',
            'Zoom': 'zoom-in',
            'Subplot': 'view-grid',
            'Save': 'document-save'
        }

        # Iterate through actions and replace icons
        for action in self.actions():
            text = action.text()
            if text in icon_mapping and text not in ['Pan', 'Subplot']:
                # Skip Pan and Subplot in light mode to keep default icons
                try:
                    theme_icon = QIcon.fromTheme(icon_mapping[text])
                    if not theme_icon.isNull():
                        action.setIcon(theme_icon)
                except Exception:
                    pass

        # Set font size icon
        if hasattr(self, 'fontSizeAction'):
            self.fontSizeAction.setIcon(QIcon.fromTheme("preferences-desktop-font"))
        
        # Set reset icon  
        if hasattr(self, 'reset_action'):
            self.reset_action.setIcon(QIcon.fromTheme("view-refresh"))

        # Set legend icon
        if hasattr(self, 'legend_action'):
            light_legend_path = path.join(path.dirname(path.abspath(__file__)), "resources", "edit-label.png")
            if path.exists(light_legend_path):
                self.legend_action.setIcon(QIcon(light_legend_path))
            else:
                self.legend_action.setIcon(QIcon.fromTheme("view-list-text"))

        # Set Customize (edit axis) icon
        for action in self.actions():
            if action.text() == "Customize":
                axes_path = path.join(path.dirname(path.abspath(__file__)), "resources", "plot_axes.png")
                if path.exists(axes_path):
                    action.setIcon(QIcon(axes_path))
                break

    # Add a method to update icons when theme changes
    def update_theme(self):
        is_dark_mode = self.palette().window().color().lightness() < 128
        if is_dark_mode:
            self.setup_dark_mode_icons()
        else:
            self.setup_light_mode_icons()
    
    def configure_subplots(self):
        """Direct implementation to get the original subplot configuration dialog"""
        try:
            # Use the Qt-specific subplot tool directly
            from matplotlib.backends.qt_compat import QtWidgets
            from matplotlib.backends.backend_qt5 import SubplotToolQt
            
            # Create and show the dialog
            fig = self.canvas.figure
            tool = SubplotToolQt(fig, self.parent)
            result = tool.exec()
            
            # Reconnect toolbar to the figure after configuration
            if result:
                self.canvas.draw_idle()
                # Reset figure
                self.parent.reset_figure()
                # Force toolbar to update its connection to the figure
                self.update()  
                
        except Exception as e:
            print(f"Error in configure_subplots: {e}")
            try:
                # Fall back to tight_layout if the dialog fails
                self.canvas.figure.tight_layout()
                self.canvas.draw_idle()
            except Exception as e2:
                print(f"Error in tight_layout fallback: {e2}")
                
    def save_figure(self, *args):
        try:
            # Call the original save_figure method
            super().save_figure(*args)
        except Exception as e:
            print(f"Error in save_figure: {e}")
            try:
                # Use PyQt6's own file dialog instead
                from PyQt6.QtWidgets import QFileDialog
                
                # Get default filename and supported file types
                default_filename = self.canvas.get_default_filename()
                filetypes = self.canvas.get_supported_filetypes()
                
                # Create filter string for QFileDialog
                filter_string = ";;".join([f"{name} (*.{ext})" for ext, name in filetypes.items()])
                
                # Open save dialog
                fname, selected_filter = QFileDialog.getSaveFileName(
                    self.parent,
                    "Save Figure",
                    path.expanduser(f"~/{default_filename}"),
                    filter_string
                )
                
                if fname:
                    # Save the figure with the global DPI setting
                    self.canvas.figure.savefig(fname)
                    print(f"Figure saved to {fname}")
            except Exception as e2:
                print(f"Error in QFileDialog save_figure fallback: {e2}")