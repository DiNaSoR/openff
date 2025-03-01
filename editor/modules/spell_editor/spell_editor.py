import os
import math  # Import math for trig functions
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                           QGroupBox, QFormLayout, QLabel, QLineEdit, 
                           QPushButton, QListWidgetItem, QComboBox, QSpinBox, QMessageBox, QSizePolicy)
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
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        layout_container = QHBoxLayout()
        
        spell_list_group = QGroupBox("Spell List")
        spell_list_layout = QVBoxLayout()
        
        button_layout = QHBoxLayout()
        
        self.add_spell_button = QPushButton("Add New Spell")
        self.add_spell_button.clicked.connect(self.add_new_spell)
        button_layout.addWidget(self.add_spell_button)
        
        self.remove_spell_button = QPushButton("Remove Spell")
        self.remove_spell_button.setEnabled(False)
        self.remove_spell_button.clicked.connect(self.remove_selected_spell)
        button_layout.addWidget(self.remove_spell_button)
        
        spell_list_layout.addLayout(button_layout)
        
        self.spell_list = QListWidget()
        self.spell_list.itemClicked.connect(self.on_spell_selected)
        spell_list_layout.addWidget(self.spell_list)
        
        spell_list_group.setLayout(spell_list_layout)
        layout_container.addWidget(spell_list_group, 1)
        
        details_layout = QVBoxLayout()
        
        self.details_box = QGroupBox("Spell Details")
        details_form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        details_form_layout.addRow("Name:", self.name_edit)
        
        self.type_combo = QComboBox()
        for spell_type in sorted(self.spell_colors.keys()):
            self.type_combo.addItem(spell_type)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        details_form_layout.addRow("Type:", self.type_combo)
        
        self.power_spin = QSpinBox()
        self.power_spin.setRange(1, 100)
        self.power_spin.valueChanged.connect(self.on_field_changed)
        details_form_layout.addRow("Power:", self.power_spin)
        
        self.mp_cost_spin = QSpinBox()
        self.mp_cost_spin.setRange(1, 100)
        self.mp_cost_spin.valueChanged.connect(self.on_field_changed)
        details_form_layout.addRow("MP Cost:", self.mp_cost_spin)
        
        self.target_combo = QComboBox()
        self.target_combo.addItems(["Single Enemy", "All Enemies", "Single Ally", "All Allies", "Self"])
        self.target_combo.currentTextChanged.connect(self.on_field_changed)
        details_form_layout.addRow("Target:", self.target_combo)
        
        self.description_edit = QLineEdit()
        details_form_layout.addRow("Description:", self.description_edit)
        
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_spell)
        details_form_layout.addRow("", self.save_button)
        
        self.details_box.setLayout(details_form_layout)
        details_layout.addWidget(self.details_box)
        
        self.p5js_preview_box = QGroupBox("Interactive Spell Preview")
        p5js_preview_layout = QVBoxLayout()
        
        self.web_view = QWebEngineView()
        self.web_view.setMinimumSize(QSize(400, 300))
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        html_file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 
            '..', '..', 'static', 'js', 'spell_preview.html'
        )
        
        url = QUrl.fromLocalFile(html_file_path)
        self.web_view.load(url)
        
        p5js_preview_layout.addWidget(self.web_view, 1)
        
        self.play_animation_button = QPushButton("Play Animation")
        self.play_animation_button.clicked.connect(self.play_p5js_animation)
        p5js_preview_layout.addWidget(self.play_animation_button)
        
        self.p5js_preview_box.setLayout(p5js_preview_layout)
        details_layout.addWidget(self.p5js_preview_box, 3)
        
        self.preview_box = QGroupBox("Spell Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(QSize(300, 200))
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.preview_label)
        
        self.preview_box.setLayout(preview_layout)
        details_layout.addWidget(self.preview_box, 1)
        
        self.animation_box = QGroupBox("Spell Animation")
        animation_layout = QVBoxLayout()
        
        animation_container = QHBoxLayout()
        
        player_effect_layout = QVBoxLayout()
        player_effect_layout.addWidget(QLabel("Player/Caster Effect:"))
        self.player_effect_label = QLabel("No animation")
        self.player_effect_label.setMinimumSize(QSize(220, 220))
        self.player_effect_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.player_effect_label.setStyleSheet("border: 2px solid #333; background-color: rgba(0, 0, 0, 40);")
        player_effect_layout.addWidget(self.player_effect_label)
        animation_container.addLayout(player_effect_layout)
        
        enemy_effect_layout = QVBoxLayout()
        enemy_effect_layout.addWidget(QLabel("Enemy/Target Effect:"))
        self.enemy_effect_label = QLabel("No animation")
        self.enemy_effect_label.setMinimumSize(QSize(220, 220))
        self.enemy_effect_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.enemy_effect_label.setStyleSheet("border: 2px solid #333; background-color: rgba(0, 0, 0, 40);")
        enemy_effect_layout.addWidget(self.enemy_effect_label)
        animation_container.addLayout(enemy_effect_layout)
        
        animation_layout.addLayout(animation_container)
        self.animation_box.setLayout(animation_layout)
        details_layout.addWidget(self.animation_box, 1)
        
        layout_container.addLayout(details_layout, 2)
        
        main_layout.addLayout(layout_container)
        
        self.enable_details(False)
        
        self.web_view.loadFinished.connect(self.on_web_view_loaded)
        
    def on_web_view_loaded(self, success):
        """Called when the web view has finished loading"""
        if success:
            self.web_view.page().settings().setAttribute(
                self.web_view.page().settings().WebAttribute.JavascriptEnabled, True
            )
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
                
                if (debug.p5_loaded && debug.updateSpellData_exists) {
                    return "ready:" + JSON.stringify(debug);
                } else {
                    return "not_ready:" + JSON.stringify(debug);
                }
            })();
            """
            self.web_view.page().runJavaScript(js_check, self.on_p5js_ready_check)
            
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
            self.web_view.page().runJavaScript(js_console_monitor, lambda result: None)
        else:
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
        debug_info = {}
        try:
            if ":" in result:
                status, debug_json = result.split(":", 1)
                debug_info = json.loads(debug_json)
            else:
                status = result
        except Exception as e:
            status = result
            
        if status == "ready" or result.startswith("ready:"):
            self.play_animation_button.setEnabled(True)
            self.play_animation_button.setText("Play Animation")
            self.play_animation_button.setStyleSheet("background-color: #44cc44;")
            
            if self.current_spell:
                self.update_p5js_preview()
            
        elif status == "not_ready" or result.startswith("not_ready:"):
            self.play_animation_button.setEnabled(False)
            self.play_animation_button.setText("p5.js Not Ready")
            self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            
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
            self.play_animation_button.setEnabled(False)
            self.play_animation_button.setText("p5.js Status Unknown")
            self.play_animation_button.setStyleSheet("background-color: #cccc44;")
            
    def update_p5js_preview(self):
        """Update the p5.js preview with the current spell data"""
        if not self.current_spell:
            return
            
        try:
            spell_data = {
                'name': self.current_spell.get('name', 'Unknown Spell'),
                'type': self.current_spell.get('type', 'Fire'),
                'power': self.current_spell.get('power', 10),
                'mp_cost': self.current_spell.get('mp_cost', 5),
                'target': self.current_spell.get('target', 'Single Enemy'),
                'flash_color': self.current_spell.get('flash_color', '#e17d62')
            }
            
            json_data = json.dumps(spell_data)
            json_data = json_data.replace("'", "\\'")
            
            js_check_and_call = """
            (function() {
                try {
                    if (typeof updateSpellData === 'function') {
                        var result = updateSpellData('%s');
                        
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
                        return {
                            status: 'error',
                            code: 'function_not_found',
                            message: 'updateSpellData function not found'
                        };
                    }
                } catch(error) {
                    return {
                        status: 'error',
                        code: 'exception',
                        message: error.message,
                        stack: error.stack
                    };
                }
            })();
            """ % (json_data, spell_data['name'], spell_data['name'], spell_data['type'])
            
            self.web_view.page().runJavaScript(js_check_and_call, self.on_p5js_update_result)
            
        except Exception as e:
            pass
            
    def on_p5js_update_result(self, result):
        """Handle the result of p5.js preview update"""
        try:
            if isinstance(result, dict):
                status = result.get('status')
                if status != 'success':
                    self.play_animation_button.setStyleSheet("background-color: #cc4444;")
                else:
                    self.play_animation_button.setStyleSheet("background-color: #44cc44;")
            elif result == 'function_not_found':
                self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            elif result and isinstance(result, str) and result.startswith('error:'):
                self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            elif result != 'success' and result is not None:
                self.play_animation_button.setStyleSheet("background-color: #cccc44;")
            else:
                self.play_animation_button.setStyleSheet("background-color: #44cc44;")
        except Exception as e:
            pass
            
    def play_p5js_animation(self):
        """Manually trigger the p5.js animation playback"""
        if not self.web_view or not self.current_spell:
            return
        
        try:
            self.play_animation_button.setText("Playing...")
            self.play_animation_button.setEnabled(False)
            
            js_code = """
            (function() {
                try {
                    if (typeof playAnimation === 'function') { 
                        var result = playAnimation(); 
                        
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
                        return {
                            status: 'error',
                            code: 'function_not_found',
                            message: 'playAnimation function not found'
                        };
                    }
                } catch(error) {
                    return {
                        status: 'error',
                        code: 'exception',
                        message: error.message,
                        stack: error.stack
                    };
                }
            })();
            """ % (self.current_spell.get('name', 'Unknown Spell'))
            
            self.web_view.page().runJavaScript(js_code, self.on_animation_result)
            QTimer.singleShot(1500, lambda: self.reset_play_button())
            
        except Exception as e:
            self.reset_play_button()
    
    def reset_play_button(self):
        """Reset the play button to its normal state"""
        self.play_animation_button.setText("Play Animation")
        self.play_animation_button.setEnabled(True)
                
    def on_animation_result(self, result):
        """Callback for animation JavaScript execution results"""
        try:
            if isinstance(result, dict):
                status = result.get('status')
                if status == 'success':
                    self.play_animation_button.setStyleSheet("background-color: #44cc44;")
                else:
                    self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            elif result == 'function_not_found':
                self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            elif result and isinstance(result, str) and result.startswith('error:'):
                self.play_animation_button.setStyleSheet("background-color: #cc4444;")
            elif result != 'success' and result is not None:
                self.play_animation_button.setStyleSheet("background-color: #cccc44;")
            else:
                self.play_animation_button.setStyleSheet("background-color: #44cc44;")
        except Exception as e:
            pass
            
        QTimer.singleShot(1500, lambda: self.reset_play_button())
        
    def on_field_changed(self):
        """Handle changes to fields that should update the p5.js preview"""
        if not self.current_spell:
            return
            
        self.current_spell['power'] = self.power_spin.value()
        self.current_spell['mp_cost'] = self.mp_cost_spin.value()
        self.current_spell['target'] = self.target_combo.currentText()
        
        self.update_p5js_preview()
        
    def update_data(self):
        """Update the UI with the latest game data."""
        self.spell_list.clear()
        
        for spell in self.game_data.spells:
            self.spell_list.addItem(spell['name'])
            
        self.current_spell = None
        self.enable_details(False)
        
    def on_spell_selected(self, item):
        """Handle spell selection from the list"""
        try:
            self.remove_spell_button.setEnabled(True)
            
            spell_name = item.text()
            for spell in self.game_data.spells:
                if spell['name'] == spell_name:
                    self.current_spell = spell
                    self.load_spell_details()
                    break
                    
            if not self.current_spell:
                self.clear_animations()
                self.details_box.setEnabled(False)
                return
                
            self.name_edit.setText(self.current_spell['name'])
            self.type_combo.setCurrentText(self.current_spell['type'])
            self.power_spin.setValue(self.current_spell['power'])
            self.mp_cost_spin.setValue(self.current_spell['mp_cost'])
            self.target_combo.setCurrentText(self.current_spell['target'])
            
            self.generate_spell_preview()
            self.update_p5js_preview()
            
            self.load_spell_animations()
            
            self.details_box.setEnabled(True)
        except Exception as e:
            self.clear_animations()
            self.details_box.setEnabled(False)
        
    def on_type_changed(self, spell_type):
        """Handle change of spell type to update the preview."""
        if self.current_spell:
            self.current_spell['type'] = spell_type
            
            if spell_type in ['Heal', 'Cure']:
                index = self.target_combo.findText('Single Ally')
                if index >= 0 and self.current_spell.get('target', '') == 'Single Enemy':
                    self.target_combo.setCurrentIndex(index)
                    self.current_spell['target'] = 'Single Ally'
            
            elif spell_type in ['Fire', 'Ice', 'Lightning', 'Earth', 'Poison', 'Light']:
                index = self.target_combo.findText('Single Enemy')
                if index >= 0 and self.current_spell.get('target', '') == 'Single Ally':
                    self.target_combo.setCurrentIndex(index)
                    self.current_spell['target'] = 'Single Enemy'
                    
            elif spell_type in ['Status']:
                index = self.target_combo.findText('Single Enemy')
                if index >= 0 and self.current_spell.get('target', '') == 'Single Ally':
                    self.target_combo.setCurrentIndex(index)
                    self.current_spell['target'] = 'Single Enemy'
                    
            self.generate_spell_preview()
            self.update_p5js_preview()
            
    def clear_animations(self):
        """Clear all animations currently displaying"""
        try:
            if self.current_animation:
                if 'player' in self.current_animation and self.current_animation['player']:
                    self.current_animation['player'].stop()
                
                if 'enemy' in self.current_animation and self.current_animation['enemy']:
                    self.current_animation['enemy'].stop()
            
            self.player_effect_label.setMovie(None)
            self.player_effect_label.setText("No animation")
            self.player_effect_label.setStyleSheet("border: 2px solid #333; background-color: rgba(0, 0, 0, 40);")
            
            self.enemy_effect_label.setMovie(None)
            self.enemy_effect_label.setText("No animation")
            self.enemy_effect_label.setStyleSheet("border: 2px solid #333; background-color: rgba(0, 0, 0, 40);")
            
            self.current_animation = {}
            
        except Exception as e:
            self.current_animation = {}
            
    def load_spell_animations(self):
        """Load animations for the current spell if they exist"""
        try:
            self.clear_animations()
            
            if not self.current_spell or 'image_files' not in self.current_spell:
                return
                
            image_files = self.current_spell['image_files']
            
            if 'player_effect' in image_files:
                player_file = image_files['player_effect']
                full_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', '..', 'img', 'sp', player_file)
                
                if os.path.exists(full_path):
                    player_movie = QMovie(full_path)
                    player_movie.setScaledSize(QSize(200, 200))
                    
                    if 'flash_color' in self.current_spell:
                        color = self.current_spell['flash_color']
                        self.player_effect_label.setStyleSheet(f"border: 3px solid {color}; background-color: rgba(0, 0, 0, 40);")
                    
                    if player_movie.isValid():
                        self.player_effect_label.setMovie(player_movie)
                        player_movie.start()
                        self.current_animation['player'] = player_movie
                else:
                    pass
            
            if 'enemy_effect' in image_files:
                enemy_file = image_files['enemy_effect']
                full_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..', '..', 'img', 'sp', enemy_file)
                
                if os.path.exists(full_path):
                    enemy_movie = QMovie(full_path)
                    enemy_movie.setScaledSize(QSize(200, 200))
                    
                    if 'flash_color' in self.current_spell:
                        color = self.current_spell['flash_color']
                        self.enemy_effect_label.setStyleSheet(f"border: 3px solid {color}; background-color: rgba(0, 0, 0, 40);")
                    
                    if enemy_movie.isValid():
                        self.enemy_effect_label.setMovie(enemy_movie)
                        enemy_movie.start()
                        self.current_animation['enemy'] = enemy_movie
                else:
                    pass
            
        except Exception as e:
            self.clear_animations()
        
    def generate_spell_preview(self):
        """Generate a preview image of the spell effect."""
        if not self.current_spell:
            return
            
        spell_type = self.type_combo.currentText()
        
        pixmap = QPixmap(300, 200)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        default_colors = (QColor(200, 200, 200), QColor(255, 255, 255))
        start_color, end_color = self.spell_colors.get(spell_type, default_colors)
        
        if spell_type in ["Fire", "Ice", "Lightning", "Earth", "Poison", "Light"]:
            self.draw_offensive_spell(painter, start_color, end_color)
        elif spell_type in ["Heal", "Cure"]:
            self.draw_healing_spell(painter, start_color, end_color)
        elif spell_type == "Status":
            self.draw_status_spell(painter, start_color, end_color)
        else:
            self.draw_buff_spell(painter, start_color, end_color)
            
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(0, 0, 300, 30, 
                        Qt.AlignmentFlag.AlignCenter, self.current_spell.get('name', 'Unknown Spell'))
        
        power_text = f"Power: {self.power_spin.value()}"
        painter.drawText(0, 170, 300, 30, 
                        Qt.AlignmentFlag.AlignCenter, power_text)
        
        if 'flash_color' in self.current_spell:
            flash_color = QColor(self.current_spell['flash_color'])
            painter.setPen(QPen(flash_color, 4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(5, 5, 290, 190)
            
        painter.end()
        
        self.preview_label.setPixmap(pixmap)
        
    def draw_offensive_spell(self, painter, start_color, end_color):
        """Draw an offensive spell effect."""
        gradient = QLinearGradient(150, 50, 150, 150)
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        painter.setBrush(QBrush(gradient))
        
        painter.drawEllipse(100, 50, 100, 100)
        
        for i in range(5):
            x = 120 + i * 15
            y = 70 + i * 10
            size = 20 - i * 3
            painter.drawEllipse(x, y, size, size)
            
    def draw_healing_spell(self, painter, start_color, end_color):
        """Draw a healing spell effect."""
        gradient = QLinearGradient(150, 50, 150, 150)
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.setBrush(QBrush(gradient))
        
        for i in range(5):
            opacity = 0.8 - i * 0.15
            painter.setOpacity(opacity)
            size = 100 - i * 15
            x = int(150 - size/2)
            y = int(100 - size/2)
            size = int(size)
            painter.drawEllipse(x, y, size, size)
            
        painter.setOpacity(1.0)
        
        painter.setPen(QPen(Qt.GlobalColor.white, 3))
        painter.drawLine(140, 100, 160, 100)
        painter.drawLine(150, 90, 150, 110)
            
    def draw_buff_spell(self, painter, start_color, end_color):
        """Draw a buff spell effect."""
        gradient = QLinearGradient(150, 50, 150, 150)
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawEllipse(125, 60, 50, 50)
        painter.drawRect(135, 110, 30, 60)
        
        painter.setBrush(QBrush(gradient))
        painter.setOpacity(0.5)
        
        for i in range(3):
            size = 80 + i * 20
            x = int(150 - size/2)
            y = int(100 - size/2)
            size = int(size)
            painter.drawEllipse(x, y, size, size)
            
        painter.setOpacity(1.0)
        
    def draw_status_spell(self, painter, start_color, end_color):
        """Draw a status effect spell."""
        gradient = QLinearGradient(150, 50, 150, 150)
        gradient.setColorAt(0, start_color)
        gradient.setColorAt(1, end_color)
        
        painter.setPen(QPen(Qt.GlobalColor.transparent))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        painter.drawEllipse(125, 60, 50, 50)
        painter.drawRect(135, 110, 30, 60)
        
        painter.setPen(QPen(start_color, 3))
        painter.setOpacity(0.8)
        
        center_x, center_y = 150, 100
        radius = 60
        
        for i in range(0, 360, 45):
            angle_rad = i * math.pi / 180
            x = int(center_x + radius * 0.7 * math.cos(angle_rad))
            y = int(center_y + radius * 0.7 * math.sin(angle_rad))
            
            star_size = 15
            painter.setBrush(QBrush(end_color))
            painter.drawEllipse(x - star_size//2, y - star_size//2, star_size, star_size)
        
        font = QFont("Arial", 14, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(100, 50, 30, 30, Qt.AlignmentFlag.AlignCenter, "Z")
        painter.drawText(180, 70, 30, 30, Qt.AlignmentFlag.AlignCenter, "Z")
        painter.drawText(80, 100, 30, 30, Qt.AlignmentFlag.AlignCenter, "Z")
        
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
        new_spell_name = f"New Spell {len(self.game_data.spells) + 1}"
        
        new_spell = {
            'name': new_spell_name,
            'level': 1,
            'mp_cost': 5,
            'type': 'Fire',
            'power': 10,
            'target': 'Single Enemy',
            'effect_type': 'rd',
            'flash_color': '#e17d62',
            'description': f"A newly created {new_spell_name} spell."
        }
        
        self.game_data.spells.append(new_spell)
        
        item = QListWidgetItem(new_spell['name'])
        self.spell_list.addItem(item)
        
        self.spell_list.setCurrentItem(item)
        self.on_spell_selected(item)
        
        self.remove_spell_button.setEnabled(True)
    
    def remove_selected_spell(self):
        """Remove the currently selected spell"""
        if not self.current_spell:
            return
            
        current_row = self.spell_list.currentRow()
        if current_row < 0:
            return
            
        spell_name = self.current_spell['name']
        
        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the spell '{spell_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            self.spell_list.takeItem(current_row)
            self.game_data.spells.pop(current_row)
            self.current_spell = None
            self.clear_animations()
            self.details_box.setEnabled(False)
            
            if self.spell_list.count() == 0:
                self.remove_spell_button.setEnabled(False)
    
    def save_spell(self):
        """Save the current spell details back to the data model."""
        if not self.current_spell:
            return
            
        self.current_spell['name'] = self.name_edit.text()
        self.current_spell['type'] = self.type_combo.currentText()
        self.current_spell['power'] = self.power_spin.value()
        self.current_spell['mp_cost'] = self.mp_cost_spin.value()
        self.current_spell['target'] = self.target_combo.currentText()
        self.current_spell['description'] = self.description_edit.text()
        
        current_item = self.spell_list.currentItem()
        if current_item:
            current_item.setText(self.current_spell['name'])
        
        try:
            self.game_data.mark_as_changed()
        except:
            pass
        
        self.generate_spell_preview()
        self.update_p5js_preview()
    
    def load_spell_details(self):
        """Load the details of the currently selected spell into the UI"""
        if not self.current_spell:
            return
            
        self.name_edit.setText(self.current_spell['name'])
        self.type_combo.setCurrentText(self.current_spell['type'])
        self.power_spin.setValue(self.current_spell['power'])
        self.mp_cost_spin.setValue(self.current_spell['mp_cost'])
        self.target_combo.setCurrentText(self.current_spell['target'])
        
        if 'description' in self.current_spell:
            self.description_edit.setText(self.current_spell['description'])
        else:
            self.description_edit.setText(f"A {self.current_spell['type']} spell with power {self.current_spell['power']}.")
        
    def save_changes(self):
        """Save all changes to the game data."""
        return self.game_data.save_to_file()

    def resizeEvent(self, event):
        """Handle resize events to update the p5.js canvas size"""
        super().resizeEvent(event)
        
        # Update the p5.js canvas size when the widget is resized
        if hasattr(self, 'web_view') and self.web_view:
            # Trigger window resize event in JavaScript
            js_code = """
            if (window.dispatchEvent) {
                window.dispatchEvent(new Event('resize'));
            }
            """
            self.web_view.page().runJavaScript(js_code, lambda result: None)
