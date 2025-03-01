import os
import math  # Import math for trig functions
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QPushButton, QListWidgetItem, QComboBox, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, QSize, QUrl, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush, QLinearGradient, QMovie
# Add WebEngine imports for p5.js integration
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineScript

class SpellEditorTab(QWidget):
    """Tab for editing game spells with visual elements."""
    
    def __init__(self, game_data):
        super().__init__()
        self.game_data = game_data
        self.current_spell = None
        self.current_animation = {}
        
        # Define spell type colors for visualization
        self.spell_colors = {
            "Fire": (QColor(255, 100, 0), QColor(255, 200, 0)),    # Orange to yellow
            "Ice": (QColor(100, 200, 255), QColor(200, 240, 255)),  # Light blue to white
            "Lightning": (QColor(255, 255, 0), QColor(200, 200, 255)),  # Yellow to light purple
            "Earth": (QColor(139, 69, 19), QColor(160, 120, 60)),   # Brown to tan
            "Poison": (QColor(0, 180, 0), QColor(150, 255, 150)),   # Green to light green
            "Heal": (QColor(255, 255, 255), QColor(100, 255, 100)), # White to light green
            "Cure": (QColor(200, 255, 200), QColor(255, 255, 255)), # Light green to white
            "Buff": (QColor(200, 200, 255), QColor(255, 255, 255)),  # Light blue to white
            "Light": (QColor(255, 255, 200), QColor(255, 255, 100)), # Pale yellow to bright yellow
            "Status": (QColor(200, 100, 200), QColor(255, 180, 255))  # Purple to pink
        }
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Split into horizontal layout for list and details
        layout_container = QHBoxLayout()
        
        # Spell list section
        spell_list_group = QGroupBox("Spell List")
        spell_list_layout = QVBoxLayout()
        
        # Add a new button layout for Add/Remove buttons
        button_layout = QHBoxLayout()
        
        # Add New Spell button
        self.add_spell_button = QPushButton("Add New Spell")
        self.add_spell_button.clicked.connect(self.add_new_spell)
        button_layout.addWidget(self.add_spell_button)
        
        # Remove Spell button (disabled by default)
        self.remove_spell_button = QPushButton("Remove Spell")
        self.remove_spell_button.setEnabled(False)  # Disable until a spell is selected
        self.remove_spell_button.clicked.connect(self.remove_selected_spell)
        button_layout.addWidget(self.remove_spell_button)
        
        spell_list_layout.addLayout(button_layout)
        
        # Spell list widget
        self.spell_list = QListWidget()
        self.spell_list.itemClicked.connect(self.on_spell_selected)
        spell_list_layout.addWidget(self.spell_list)
        
        spell_list_group.setLayout(spell_list_layout)
        layout_container.addWidget(spell_list_group, 1)
        
        # Right side - Spell details
        details_layout = QVBoxLayout()
        
        # Spell Details Group
        self.details_box = QGroupBox("Spell Details")
        details_form_layout = QFormLayout()
        
        # Name edit
        self.name_edit = QLineEdit()
        details_form_layout.addRow("Name:", self.name_edit)
        
        # Type combo
        self.type_combo = QComboBox()
        for spell_type in sorted(self.spell_colors.keys()):
            self.type_combo.addItem(spell_type)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        details_form_layout.addRow("Type:", self.type_combo)
        
        # Power spinbox
        self.power_spin = QSpinBox()
        self.power_spin.setRange(1, 100)
        self.power_spin.valueChanged.connect(self.on_field_changed)
        details_form_layout.addRow("Power:", self.power_spin)
        
        # MP cost spinbox
        self.mp_cost_spin = QSpinBox()
        self.mp_cost_spin.setRange(1, 100)
        self.mp_cost_spin.valueChanged.connect(self.on_field_changed)
        details_form_layout.addRow("MP Cost:", self.mp_cost_spin)
        
        # Target combo
        self.target_combo = QComboBox()
        self.target_combo.addItems(["Single Enemy", "All Enemies", "Single Ally", "All Allies", "Self"])
        self.target_combo.currentTextChanged.connect(self.on_field_changed)
        details_form_layout.addRow("Target:", self.target_combo)
        
        # Description edit
        self.description_edit = QLineEdit()
        details_form_layout.addRow("Description:", self.description_edit)
        
        # Save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_spell)
        details_form_layout.addRow("", self.save_button)
        
        self.details_box.setLayout(details_form_layout)
        details_layout.addWidget(self.details_box)
        
        # P5.js Spell Preview Group 
        self.p5js_preview_box = QGroupBox("Interactive Spell Preview")
        p5js_preview_layout = QVBoxLayout()
        
        # Create the web view for p5.js visualization
        self.web_view = QWebEngineView()
        self.web_view.setMinimumSize(QSize(400, 300))
        
        # Get the path to the HTML file
        html_file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 
            '..', '..', 'static', 'js', 'spell_preview.html'
        )
        
        # Convert the path to a URL
        url = QUrl.fromLocalFile(html_file_path)
        self.web_view.load(url)
        
        # Add the web view to the layout
        p5js_preview_layout.addWidget(self.web_view)
        
        # Add a play button to manually trigger the animation
        self.play_animation_button = QPushButton("Play Animation")
        self.play_animation_button.clicked.connect(self.play_p5js_animation)
        p5js_preview_layout.addWidget(self.play_animation_button)
        
        self.p5js_preview_box.setLayout(p5js_preview_layout)
        details_layout.addWidget(self.p5js_preview_box)
        
        # Static Spell Preview Group (keep the old implementation)
        self.preview_box = QGroupBox("Spell Preview")
        preview_layout = QVBoxLayout()
        
        # Preview canvas (QLabel with pixmap)
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(QSize(300, 200))
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.preview_label)
        
        self.preview_box.setLayout(preview_layout)
        details_layout.addWidget(self.preview_box)
        
        # Animation Group (for displaying spell animations)
        self.animation_box = QGroupBox("Spell Animation")
        animation_layout = QVBoxLayout()
        
        # Animation layout (horizontal for player and enemy effects)
        animation_container = QHBoxLayout()
        
        # Player effect layout
        player_effect_layout = QVBoxLayout()
        player_effect_layout.addWidget(QLabel("Player/Caster Effect:"))
        self.player_effect_label = QLabel("No animation")
        # Increase animation size from 150x150 to 220x220
        self.player_effect_label.setMinimumSize(QSize(220, 220))
        self.player_effect_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.player_effect_label.setStyleSheet("border: 2px solid #333; background-color: rgba(0, 0, 0, 40);")
        player_effect_layout.addWidget(self.player_effect_label)
        animation_container.addLayout(player_effect_layout)
        
        # Enemy effect layout
        enemy_effect_layout = QVBoxLayout()
        enemy_effect_layout.addWidget(QLabel("Enemy/Target Effect:"))
        self.enemy_effect_label = QLabel("No animation")
        # Increase animation size from 150x150 to 220x220
        self.enemy_effect_label.setMinimumSize(QSize(220, 220))
        self.enemy_effect_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.enemy_effect_label.setStyleSheet("border: 2px solid #333; background-color: rgba(0, 0, 0, 40);")
        enemy_effect_layout.addWidget(self.enemy_effect_label)
        animation_container.addLayout(enemy_effect_layout)
        
        animation_layout.addLayout(animation_container)
        self.animation_box.setLayout(animation_layout)
        details_layout.addWidget(self.animation_box)
        
        # Add details layout to the container
        layout_container.addLayout(details_layout, 2)
        
        # Add the container to the main layout
        main_layout.addLayout(layout_container)
        
        # Disable details until a spell is selected
        self.enable_details(False)
        
        # Connect web view signals
        self.web_view.loadFinished.connect(self.on_web_view_loaded)
        
    def on_web_view_loaded(self, success):
        """Called when the web view has finished loading"""
        print(f"Web view loaded: {success}")
        if success:
            # Add debug message
            print("🔍 DEBUG: WebView successfully loaded, checking if p5.js is ready...")
            
            # Enable JavaScript console logging
            self.web_view.page().settings().setAttribute(
                self.web_view.page().settings().WebAttribute.JavascriptEnabled, True
            )
            
            # Check if the p5.js environment is ready with more detailed diagnostics
            js_check = """
            (function() {
                var debug = {
                    p5_loaded: typeof p5 !== 'undefined',
                    updateSpellData_exists: typeof updateSpellData === 'function',
                    playAnimation_exists: typeof playAnimation === 'function',
                    canvas_exists: document.querySelector('canvas') !== null,
                    window_size: {width: window.innerWidth, height: window.innerHeight},
                    screen_size: {width: screen.width, height: screen.height}
                };
                
                console.log('DEBUG INFORMATION:', debug);
                
                if (debug.p5_loaded && debug.updateSpellData_exists) {
                    return "ready:" + JSON.stringify(debug);
                } else {
                    return "not_ready:" + JSON.stringify(debug);
                }
            })();
            """
            self.web_view.page().runJavaScript(js_check, self.on_p5js_ready_check)
            
            # Also add a JavaScript console logger to monitor p5.js activity
            js_console_monitor = """
            (function() {
                if (!window._consoleMonitorInstalled) {
                    var originalConsoleLog = console.log;
                    var originalConsoleError = console.error;
                    var originalConsoleWarn = console.warn;
                    
                    console.log = function() {
                        var args = Array.prototype.slice.call(arguments);
                        originalConsoleLog.apply(console, ["[LOG]", ...args]);
                    };
                    
                    console.error = function() {
                        var args = Array.prototype.slice.call(arguments);
                        originalConsoleError.apply(console, ["[ERROR]", ...args]);
                    };
                    
                    console.warn = function() {
                        var args = Array.prototype.slice.call(arguments);
                        originalConsoleWarn.apply(console, ["[WARN]", ...args]);
                    };
                    
                    window._consoleMonitorInstalled = true;
                    return "Console monitor installed";
                }
                return "Console monitor already installed";
            })();
            """
            self.web_view.page().runJavaScript(js_console_monitor, lambda result: print(f"Console monitor: {result}"))
        else:
            print("❌ Web view failed to load")
            # Add a visible error message in the web view area
            self.web_view.setHtml("""
                <html>
                <body style="background-color: #ff6666; color: white; font-family: Arial, sans-serif; text-align: center; padding: 20px;">
                    <h2>Web View Failed to Load</h2>
                    <p>The p5.js preview could not be loaded.</p>
                    <p>Please check the console for errors and ensure you have internet connectivity for CDN resources.</p>
                </body>
                </html>
            """)
    
    def on_p5js_ready_check(self, result):
        """Handle the result of checking if p5.js is ready"""
        print(f"🔍 DEBUG - p5.js ready check response: {result}")
        
        # Try to parse the debug information
        debug_info = {}
        try:
            if ":" in result:
                status, debug_json = result.split(":", 1)
                debug_info = json.loads(debug_json)
                print(f"🔍 DEBUG DETAILS: {json.dumps(debug_info, indent=2)}")
            else:
                status = result
        except Exception as e:
            print(f"❌ Error parsing p5.js debug info: {e}")
            status = result
            
        if status == "ready" or result.startswith("ready:"):
            print("✅ p5.js environment is READY!")
            # Update the UI to show that p5.js is ready
            self.play_animation_button.setEnabled(True)
            self.play_animation_button.setText("Play Animation")
            self.play_animation_button.setStyleSheet("background-color: #44cc44;")
            
            # Update the current spell data in the p5.js preview if available
            if self.current_spell:
                self.update_p5js_preview()
            
        elif status == "not_ready" or result.startswith("not_ready:"):
            print("⚠️ p5.js environment NOT READY yet")
            # Update the UI to show that p5.js is not ready
            self.play_animation_button.setEnabled(False)
            self.play_animation_button.setText("p5.js Not Ready")
            self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            
            # Set a delay and check again
            QTimer.singleShot(1000, lambda: self.web_view.page().runJavaScript("""
                (function() {
                    var debug = {
                        p5_loaded: typeof p5 !== 'undefined',
                        updateSpellData_exists: typeof updateSpellData === 'function',
                        playAnimation_exists: typeof playAnimation === 'function',
                        canvas_exists: document.querySelector('canvas') !== null,
                    };
                    
                    if (debug.p5_loaded && debug.updateSpellData_exists) {
                        return "ready:" + JSON.stringify(debug);
                    } else {
                        return "not_ready:" + JSON.stringify(debug);
                    }
                })();
            """, self.on_p5js_ready_check))
        else:
            print(f"❓ Unknown p5.js ready check result: {result}")
            # Handle unknown status
            self.play_animation_button.setEnabled(False)
            self.play_animation_button.setText("p5.js Status Unknown")
            self.play_animation_button.setStyleSheet("background-color: #cccc44;")
            
    def update_p5js_preview(self):
        """Update the p5.js preview with the current spell data"""
        if not self.current_spell:
            print("No current spell to update preview with")
            return
            
        try:
            print(f"🔍 DEBUG: Updating p5.js preview with spell data for: {self.current_spell['name']}")
            
            # Create a JSON representation of the spell data to pass to the p5.js sketch
            spell_data = {
                'name': self.current_spell.get('name', 'Unknown Spell'),
                'type': self.current_spell.get('type', 'Fire'),
                'power': self.current_spell.get('power', 10),
                'mp_cost': self.current_spell.get('mp_cost', 5),
                'target': self.current_spell.get('target', 'Single Enemy'),
                'flash_color': self.current_spell.get('flash_color', '#e17d62')
            }
            
            # Print out the exact data we're sending
            print(f"🔍 DEBUG: Spell data being sent: {json.dumps(spell_data, indent=2)}")
            
            # Convert to JSON string
            json_data = json.dumps(spell_data)
            
            # Escape any single quotes and other special characters
            json_data = json_data.replace("'", "\\'")
            
            # Execute JavaScript to update the p5.js sketch with enhanced error handling and debugging
            js_check_and_call = """
            (function() {
                try {
                    console.log('Attempting to update spell data with:', %s);
                    
                    if (typeof updateSpellData === 'function') {
                        var result = updateSpellData('%s');
                        console.log('Updated spell data successfully for: %s');
                        
                        // Visual confirmation by briefly flashing the canvas border
                        var canvas = document.querySelector('canvas');
                        if (canvas) {
                            canvas.style.border = '3px solid green';
                            setTimeout(function() {
                                canvas.style.border = 'none';
                            }, 500);
                        }
                        
                        return {
                            status: 'success',
                            message: 'Spell data updated for: %s',
                            details: { spell: '%s', type: '%s' }
                        };
                    } else {
                        console.error('updateSpellData function not found in the p5.js sketch');
                        return {
                            status: 'error',
                            code: 'function_not_found',
                            message: 'updateSpellData function not found'
                        };
                    }
                } catch(error) {
                    console.error('Error updating spell data:', error);
                    return {
                        status: 'error',
                        code: 'exception',
                        message: error.message,
                        stack: error.stack
                    };
                }
            })();
            """ % (json_data, json_data, spell_data['name'], spell_data['name'], spell_data['name'], spell_data['type'])
            
            self.web_view.page().runJavaScript(js_check_and_call, self.on_p5js_update_result)
            
        except Exception as e:
            print(f"❌ Error updating p5.js preview: {e}")
            import traceback
            traceback.print_exc()
            
    def on_p5js_update_result(self, result):
        """Handle the result of p5.js preview update"""
        print(f"🔍 DEBUG: p5.js update result: {result}")
        
        try:
            # Try to parse result as JSON if it's a dictionary
            if isinstance(result, dict):
                status = result.get('status')
                message = result.get('message', '')
                
                if status == 'success':
                    print(f"✅ Successfully updated the p5.js preview: {message}")
                    self.play_animation_button.setStyleSheet("background-color: #44cc44;")
                else:
                    print(f"❌ Error updating p5.js preview: {message}")
                    if 'stack' in result:
                        print(f"Stack trace: {result['stack']}")
                    self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            elif result == 'function_not_found':
                print("❌ updateSpellData function not found in the p5.js sketch")
                self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            elif result and isinstance(result, str) and result.startswith('error:'):
                print(f"❌ JavaScript error: {result}")
                self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            elif result != 'success' and result is not None:
                print(f"⚠️ Unexpected result from p5.js update: {result}")
                self.play_animation_button.setStyleSheet("background-color: #cccc44;")
            else:
                print("✅ Successfully updated the p5.js preview")
                self.play_animation_button.setStyleSheet("background-color: #44cc44;")
        except Exception as e:
            print(f"❌ Error processing p5.js update result: {e}")
            import traceback
            traceback.print_exc()
            
    def play_p5js_animation(self):
        """Manually trigger the p5.js animation playback"""
        if not self.web_view or not self.current_spell:
            print("❌ Cannot play animation: web view or spell not available")
            return
        
        print(f"🔍 DEBUG: Attempting to play animation for: {self.current_spell['name']}")
        
        try:
            # Update the button UI to indicate animation is playing
            self.play_animation_button.setText("Playing...")
            self.play_animation_button.setEnabled(False)
            
            # Ensure the JavaScript is executed properly with error handling
            js_code = """
            (function() {
                try {
                    console.log('Attempting to play animation for: %s');
                    
                    if (typeof playAnimation === 'function') { 
                        var result = playAnimation(); 
                        console.log('Animation played for: %s');
                        
                        // Visual confirmation by briefly flashing the canvas border
                        var canvas = document.querySelector('canvas');
                        if (canvas) {
                            canvas.style.border = '3px solid blue';
                            setTimeout(function() {
                                canvas.style.border = 'none';
                            }, 1000);
                        }
                        
                        return {
                            status: 'success',
                            message: 'Animation started for: %s',
                            result: result
                        };
                    } else { 
                        console.error('playAnimation function not found');
                        return {
                            status: 'error',
                            code: 'function_not_found',
                            message: 'playAnimation function not found'
                        };
                    }
                } catch(error) {
                    console.error('Error playing animation:', error);
                    return {
                        status: 'error',
                        code: 'exception',
                        message: error.message,
                        stack: error.stack
                    };
                }
            })();
            """ % (self.current_spell.get('name', 'Unknown Spell'), 
                  self.current_spell.get('name', 'Unknown Spell'),
                  self.current_spell.get('name', 'Unknown Spell'))
            
            self.web_view.page().runJavaScript(js_code, self.on_animation_result)
            print("▶️ Triggered p5.js animation playback for: " + self.current_spell.get('name', 'Unknown Spell'))
            
            # Reset button after a brief delay
            QTimer.singleShot(1500, lambda: self.reset_play_button())
            
        except Exception as e:
            print(f"❌ Error triggering animation: {e}")
            import traceback
            traceback.print_exc()
            self.reset_play_button()
    
    def reset_play_button(self):
        """Reset the play button to its normal state"""
        self.play_animation_button.setText("Play Animation")
        self.play_animation_button.setEnabled(True)
                
    def on_animation_result(self, result):
        """Callback for animation JavaScript execution results"""
        print(f"🔍 DEBUG: Animation result: {result}")
        
        try:
            # Try to parse result as JSON if it's a dictionary
            if isinstance(result, dict):
                status = result.get('status')
                message = result.get('message', '')
                
                if status == 'success':
                    print(f"✅ Animation started successfully: {message}")
                    # Update button to indicate animation is playing
                    self.play_animation_button.setStyleSheet("background-color: #44cc44;")
                else:
                    print(f"❌ Error playing animation: {message}")
                    if 'stack' in result:
                        print(f"Stack trace: {result['stack']}")
                    self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            elif result == 'function_not_found':
                print("❌ playAnimation function not found in the p5.js sketch")
                self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            elif result and isinstance(result, str) and result.startswith('error:'):
                print(f"❌ JavaScript error playing animation: {result}")
                self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            elif result != 'success' and result is not None:
                print(f"⚠️ Unexpected result from animation playback: {result}")
                self.play_animation_button.setStyleSheet("background-color: #cccc44;")
            else:
                print("✅ Animation started successfully")
                self.play_animation_button.setStyleSheet("background-color: #44cc44;")
        except Exception as e:
            print(f"❌ Error processing animation result: {e}")
            import traceback
            traceback.print_exc()
            
        # Reset button after a brief delay (if not already reset)
        QTimer.singleShot(1500, lambda: self.reset_play_button())
        
    def on_field_changed(self):
        """Handle changes to fields that should update the p5.js preview"""
        if not self.current_spell:
            return
            
        # Update the current spell with the new values (but don't save them yet)
        self.current_spell['power'] = self.power_spin.value()
        self.current_spell['mp_cost'] = self.mp_cost_spin.value()
        self.current_spell['target'] = self.target_combo.currentText()
        
        # Update the p5.js preview
        self.update_p5js_preview()
        
    def update_data(self):
        """Update the UI with the latest game data."""
        # Clear the list
        self.spell_list.clear()
        
        print("\n==== SPELL EDITOR DATA UPDATE ====")
        print(f"Loading {len(self.game_data.spells)} spells into editor")
        
        # Add spells to the list
        for spell in self.game_data.spells:
            self.spell_list.addItem(spell['name'])
            # Print details of each spell for debugging
            print(f"📋 Loaded spell: {spell['name']}")
            print(f"  - Type: {spell.get('type', 'Unknown')}")
            print(f"  - Power: {spell.get('power', 'Unknown')}")
            print(f"  - MP Cost: {spell.get('mp_cost', 'Unknown')}")
            print(f"  - Target: {spell.get('target', 'Unknown')}")
            
        # Clear the current selection
        self.current_spell = None
        self.enable_details(False)
        print("==== SPELL EDITOR UPDATE COMPLETED ====\n")
        
    def on_spell_selected(self, item):
        """Handle spell selection from the list"""
        try:
            # Enable the remove button when a spell is selected
            self.remove_spell_button.setEnabled(True)
            
            # Continue with existing functionality
            spell_name = item.text()
            for spell in self.game_data.spells:
                if spell['name'] == spell_name:
                    self.current_spell = spell
                    self.load_spell_details()
                    break
                    
            # Clear animations if no spell found
            if not self.current_spell:
                self.clear_animations()
                self.details_box.setEnabled(False)
                return
                
            print(f"\n\n==== SPELL SELECTED: {spell_name} ====")
            print("Found spell details:")
            for key, value in self.current_spell.items():
                print(f"  - {key}: {value}")
            
            # Set form values
            self.name_edit.setText(self.current_spell['name'])
            self.type_combo.setCurrentText(self.current_spell['type'])
            print(f"✅ Set type to: {self.current_spell['type']}")
            
            self.power_spin.setValue(self.current_spell['power'])
            print(f"✅ Set power to: {self.current_spell['power']}")
            
            self.mp_cost_spin.setValue(self.current_spell['mp_cost'])
            print(f"✅ Set MP cost to: {self.current_spell['mp_cost']}")
            
            self.target_combo.setCurrentText(self.current_spell['target'])
            print(f"✅ Set target to: {self.current_spell['target']}")
            
            # Generate preview
            self.generate_spell_preview()
            print("✅ Generated spell preview")
            
            # Update the p5.js preview
            self.update_p5js_preview()
            print("✅ Updated p5.js interactive preview")
            
            # Load animations if available
            self.load_spell_animations()
            
            # Enable the details panel
            self.details_box.setEnabled(True)
            print("✅ Enabled spell details panel")
            print("==== SPELL SELECTION COMPLETED ====")
        except Exception as e:
            print(f"Error in spell selection: {e}")
            self.clear_animations()
            self.details_box.setEnabled(False)
        
    def on_type_changed(self, spell_type):
        """Handle change of spell type to update the preview."""
        if self.current_spell:
            # Update the current spell with the new type
            self.current_spell['type'] = spell_type
            
            # For healing spells, suggest an appropriate target
            if spell_type in ['Heal', 'Cure']:
                index = self.target_combo.findText('Single Ally')
                if index >= 0 and self.current_spell.get('target', '') == 'Single Enemy':
                    self.target_combo.setCurrentIndex(index)
                    self.current_spell['target'] = 'Single Ally'
            
            # For offensive spells, suggest an appropriate target
            elif spell_type in ['Fire', 'Ice', 'Lightning', 'Earth', 'Poison', 'Light']:
                index = self.target_combo.findText('Single Enemy')
                if index >= 0 and self.current_spell.get('target', '') == 'Single Ally':
                    self.target_combo.setCurrentIndex(index)
                    self.current_spell['target'] = 'Single Enemy'
                    
            # For status spells, suggest an appropriate target
            elif spell_type in ['Status']:
                index = self.target_combo.findText('Single Enemy')
                if index >= 0 and self.current_spell.get('target', '') == 'Single Ally':
                    self.target_combo.setCurrentIndex(index)
                    self.current_spell['target'] = 'Single Enemy'
                    
            # Update the preview
            self.generate_spell_preview()
            
            # Update the p5.js preview
            self.update_p5js_preview()
            
    def clear_animations(self):
        """Clear all animations currently displaying"""
        try:
            # Stop any playing animations
            if self.current_animation:
                if 'player' in self.current_animation and self.current_animation['player']:
                    self.current_animation['player'].stop()
                
                if 'enemy' in self.current_animation and self.current_animation['enemy']:
                    self.current_animation['enemy'].stop()
            
            # Reset the labels
            self.player_effect_label.setMovie(None)
            self.player_effect_label.setText("No animation")
            self.player_effect_label.setStyleSheet("border: 2px solid #333; background-color: rgba(0, 0, 0, 40);")
            
            self.enemy_effect_label.setMovie(None)
            self.enemy_effect_label.setText("No animation")
            self.enemy_effect_label.setStyleSheet("border: 2px solid #333; background-color: rgba(0, 0, 0, 40);")
            
            # Clear the current animation dictionary
            self.current_animation = {}
            
        except Exception as e:
            print(f"❌ Error clearing animations: {e}")
            # Reset the current animation as a fallback
            self.current_animation = {}
            
    def load_spell_animations(self):
        """Load animations for the current spell if they exist"""
        try:
            # Clear any existing animations first
            self.clear_animations()
            
            if not self.current_spell or 'image_files' not in self.current_spell:
                print("No image files found for this spell")
                return
                
            image_files = self.current_spell['image_files']
            print(f"✅ Found image files: {image_files}")
            
            # Check for player effect animation
            if 'player_effect' in image_files:
                player_file = image_files['player_effect']
                full_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', '..', 'img', 'sp', player_file)
                
                if os.path.exists(full_path):
                    # Create and start the animation
                    player_movie = QMovie(full_path)
                    # Scale the movie to fit the larger label
                    player_movie.setScaledSize(QSize(200, 200))
                    
                    # Apply a border around the animation that matches the spell's color
                    if 'flash_color' in self.current_spell:
                        color = self.current_spell['flash_color']
                        self.player_effect_label.setStyleSheet(f"border: 3px solid {color}; background-color: rgba(0, 0, 0, 40);")
                    
                    # Set the movie to the label
                    if player_movie.isValid():
                        self.player_effect_label.setMovie(player_movie)
                        player_movie.start()
                        # Save reference to prevent garbage collection
                        self.current_animation['player'] = player_movie
                        print(f"✅ Loaded player effect animation: {player_file}")
                    else:
                        print(f"❌ Invalid player effect animation: {player_file}")
                else:
                    print(f"❌ Player effect file not found: {full_path}")
            
            # Check for enemy effect animation
            if 'enemy_effect' in image_files:
                enemy_file = image_files['enemy_effect']
                full_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', '..', 'img', 'sp', enemy_file)
                
                if os.path.exists(full_path):
                    # Create and start the animation
                    enemy_movie = QMovie(full_path)
                    # Scale the movie to fit the larger label
                    enemy_movie.setScaledSize(QSize(200, 200))
                    
                    # Apply a border around the animation that matches the spell's color
                    if 'flash_color' in self.current_spell:
                        color = self.current_spell['flash_color']
                        self.enemy_effect_label.setStyleSheet(f"border: 3px solid {color}; background-color: rgba(0, 0, 0, 40);")
                    
                    # Set the movie to the label
                    if enemy_movie.isValid():
                        self.enemy_effect_label.setMovie(enemy_movie)
                        enemy_movie.start()
                        # Save reference to prevent garbage collection
                        self.current_animation['enemy'] = enemy_movie
                        print(f"✅ Loaded enemy effect animation: {enemy_file}")
                    else:
                        print(f"❌ Invalid enemy effect animation: {enemy_file}")
                else:
                    print(f"❌ Enemy effect file not found: {full_path}")
            
            print("✅ Loaded spell animations")
            
        except Exception as e:
            print(f"❌ Error loading animations: {e}")
            self.clear_animations()
        
    def generate_spell_preview(self):
        """Generate a preview image of the spell effect."""
        if not self.current_spell:
            return
            
        # Get the spell type
        spell_type = self.type_combo.currentText()
        
        # Create a pixmap for the spell effect
        pixmap = QPixmap(300, 200)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Create a painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get the spell colors with fallback for unknown types
        default_colors = (QColor(200, 200, 200), QColor(255, 255, 255))  # Default gray to white
        start_color, end_color = self.spell_colors.get(spell_type, default_colors)
        
        # Draw based on spell type
        if spell_type in ["Fire", "Ice", "Lightning", "Earth", "Poison", "Light"]:
            # Offensive spell - draw as a projectile
            self.draw_offensive_spell(painter, start_color, end_color)
        elif spell_type in ["Heal", "Cure"]:
            # Healing spell - draw as a glow
            self.draw_healing_spell(painter, start_color, end_color)
        elif spell_type == "Status":
            # Status spell - draw as a swirl
            self.draw_status_spell(painter, start_color, end_color)
        else:  # Buff or other types
            # Buff spell - draw as an aura
            self.draw_buff_spell(painter, start_color, end_color)
            
        # Draw the spell name
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(0, 0, 300, 30, 
                        Qt.AlignmentFlag.AlignCenter, self.current_spell.get('name', 'Unknown Spell'))
        
        # Draw the spell power
        power_text = f"Power: {self.power_spin.value()}"
        painter.drawText(0, 170, 300, 30, 
                        Qt.AlignmentFlag.AlignCenter, power_text)
        
        # If the spell has a flash color, add it as a border
        if 'flash_color' in self.current_spell:
            flash_color = QColor(self.current_spell['flash_color'])
            painter.setPen(QPen(flash_color, 4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(5, 5, 290, 190)
            
        # End painting
        painter.end()
        
        # Set the pixmap
        self.preview_label.setPixmap(pixmap)
        
    def draw_offensive_spell(self, painter, start_color, end_color):
        """Draw an offensive spell effect."""
        # Create a gradient
        gradient = QLinearGradient(150, 50, 150, 150)
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        # Draw a projectile
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(QBrush(gradient))
        
        # Draw the main projectile
        painter.drawEllipse(100, 50, 100, 100)
        
        # Draw some particles
        for i in range(5):
            x = 120 + i * 15
            y = 70 + i * 10
            size = 20 - i * 3
            painter.drawEllipse(x, y, size, size)
            
    def draw_healing_spell(self, painter, start_color, end_color):
        """Draw a healing spell effect."""
        # Create a gradient
        gradient = QLinearGradient(150, 50, 150, 150)
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        # Draw a glow
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.setBrush(QBrush(gradient))
        
        # Draw concentric circles
        for i in range(5):
            opacity = 0.8 - i * 0.15
            painter.setOpacity(opacity)
            size = 100 - i * 15
            # Convert float to int for drawing functions
            x = int(150 - size/2)
            y = int(100 - size/2)
            size = int(size)
            painter.drawEllipse(x, y, size, size)
            
        # Reset opacity
        painter.setOpacity(1.0)
        
        # Draw a cross in the center
        painter.setPen(QPen(Qt.GlobalColor.white, 3))
        painter.drawLine(140, 100, 160, 100)
        painter.drawLine(150, 90, 150, 110)
            
    def draw_buff_spell(self, painter, start_color, end_color):
        """Draw a buff spell effect."""
        # Create a gradient
        gradient = QLinearGradient(150, 50, 150, 150)
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        # Draw an aura
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        
        # Draw a character silhouette
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawEllipse(125, 60, 50, 50)  # Head
        painter.drawRect(135, 110, 30, 60)    # Body
        
        # Draw the aura
        painter.setBrush(QBrush(gradient))
        painter.setOpacity(0.5)
        
        # Draw aura waves
        for i in range(3):
            size = 80 + i * 20
            # Convert float to int for drawing functions
            x = int(150 - size/2)
            y = int(100 - size/2)
            size = int(size)
            painter.drawEllipse(x, y, size, size)
            
        # Reset opacity
        painter.setOpacity(1.0)
        
    def draw_status_spell(self, painter, start_color, end_color):
        """Draw a status effect spell."""
        # Create a gradient
        gradient = QLinearGradient(150, 50, 150, 150)
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        # Draw an enemy silhouette
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawEllipse(125, 60, 50, 50)  # Head
        painter.drawRect(135, 110, 30, 60)    # Body
        
        # Draw status effect symbols
        painter.setPen(QPen(start_color, 3))
        painter.setOpacity(0.8)
        
        # Draw swirls and symbols around the target
        center_x, center_y = 150, 100
        radius = 60
        
        # Draw symbols at regular intervals around the target
        for i in range(0, 360, 45):
            angle_rad = i * math.pi / 180
            x = int(center_x + radius * 0.7 * math.cos(angle_rad))
            y = int(center_y + radius * 0.7 * math.sin(angle_rad))
            
            # Draw small stars or symbols
            star_size = 15
            painter.setBrush(QBrush(end_color))
            painter.drawEllipse(x - star_size//2, y - star_size//2, star_size, star_size)
        
        # Draw a few Z letters for sleep effect
        font = QFont("Arial", 14, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(100, 50, 30, 30, Qt.AlignmentFlag.AlignCenter, "Z")
        painter.drawText(180, 70, 30, 30, Qt.AlignmentFlag.AlignCenter, "Z")
        painter.drawText(80, 100, 30, 30, Qt.AlignmentFlag.AlignCenter, "Z")
        
        # Reset opacity
        painter.setOpacity(1.0)
        
    def enable_details(self, enabled):
        """Enable or disable the details widgets."""
        self.details_box.setEnabled(enabled)
        self.preview_box.setEnabled(enabled)
        self.p5js_preview_box.setEnabled(enabled)
        self.animation_box.setEnabled(enabled)
        self.remove_spell_button.setEnabled(enabled)
        
    def add_new_spell(self):
        """Create a new spell with default values and add it to the list"""
        # Generate a unique name for the new spell
        new_spell_name = f"New Spell {len(self.game_data.spells) + 1}"
        
        # Create a new spell with default values
        new_spell = {
            'name': new_spell_name,
            'level': 1,
            'mp_cost': 5,
            'type': 'Fire',  # Default type
            'power': 10,     # Default power
            'target': 'Single Enemy',  # Default target
            'effect_type': 'rd',  # Default effect type (red)
            'flash_color': '#e17d62',  # Default flash color (orange-red for fire)
            'description': f"A newly created {new_spell_name} spell."
        }
        
        # Add the new spell to game data
        self.game_data.spells.append(new_spell)
        
        # Add to the list widget
        item = QListWidgetItem(new_spell['name'])
        self.spell_list.addItem(item)
        
        # Select the new spell
        self.spell_list.setCurrentItem(item)
        self.on_spell_selected(item)
        
        # Enable the remove button
        self.remove_spell_button.setEnabled(True)
        
        print(f"Created new spell: {new_spell_name}")
    
    def remove_selected_spell(self):
        """Remove the currently selected spell"""
        if not self.current_spell:
            return
            
        current_row = self.spell_list.currentRow()
        if current_row < 0:
            return
            
        # Get the spell name for confirmation
        spell_name = self.current_spell['name']
        
        # Simple confirmation dialog
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the spell '{spell_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            # Remove from the list widget
            self.spell_list.takeItem(current_row)
            
            # Remove from game data
            self.game_data.spells.pop(current_row)
            
            # Clear current spell
            self.current_spell = None
            self.clear_animations()
            self.details_box.setEnabled(False)
            
            print(f"Removed spell: {spell_name}")
            
            # Disable remove button if no spells left
            if self.spell_list.count() == 0:
                self.remove_spell_button.setEnabled(False)
    
    def save_spell(self):
        """Save the current spell details back to the data model."""
        if not self.current_spell:
            return
            
        # Update spell properties
        self.current_spell['name'] = self.name_edit.text()
        self.current_spell['type'] = self.type_combo.currentText()
        self.current_spell['power'] = self.power_spin.value()
        self.current_spell['mp_cost'] = self.mp_cost_spin.value()
        self.current_spell['target'] = self.target_combo.currentText()
        self.current_spell['description'] = self.description_edit.text()
        
        # Update the list item text
        current_item = self.spell_list.currentItem()
        if current_item:
            current_item.setText(self.current_spell['name'])
        
        # Mark the game data as changed
        # This will depend on how your game_data object is implemented
        try:
            # Try to call mark_as_changed if it exists
            self.game_data.mark_as_changed()
        except:
            # Otherwise just print a message
            print("Changes saved to spell, but game_data.mark_as_changed not called")
        
        # Update the UI - regenerate preview
        self.generate_spell_preview()
        
        # Update the p5.js preview
        self.update_p5js_preview()
        
        print(f"✅ Saved changes to spell: {self.current_spell['name']}")
    
    def load_spell_details(self):
        """Load the details of the currently selected spell into the UI"""
        if not self.current_spell:
            return
            
        # Set form values
        self.name_edit.setText(self.current_spell['name'])
        self.type_combo.setCurrentText(self.current_spell['type'])
        self.power_spin.setValue(self.current_spell['power'])
        self.mp_cost_spin.setValue(self.current_spell['mp_cost'])
        self.target_combo.setCurrentText(self.current_spell['target'])
        
        # Set description if available
        if 'description' in self.current_spell:
            self.description_edit.setText(self.current_spell['description'])
        else:
            self.description_edit.setText(f"A {self.current_spell['type']} spell with power {self.current_spell['power']}.")
        
    def save_changes(self):
        """Save all changes to the game data."""
        # This would be called from the main window
        return self.game_data.save_to_file() 