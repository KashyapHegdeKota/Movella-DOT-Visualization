import tkinter as tk
from tkinter import ttk, messagebox
from split_screen_app import LiveRecordingApp
from device_setup_app import DeviceSetupApp

class HomeScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Movella DOT - Home")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Store the manager from device setup
        self.dot_manager = None
        
        # Main container
        main_frame = tk.Frame(root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="Movella DOT Visualization",
                              font=('Arial', 32, 'bold'),
                              bg='#2c3e50',
                              fg='white')
        title_label.pack(pady=50)
        
        # Subtitle
        subtitle_label = tk.Label(main_frame,
                                 text="Motion Tracking & Analysis System",
                                 font=('Arial', 16),
                                 bg='#2c3e50',
                                 fg='#ecf0f1')
        subtitle_label.pack(pady=10)
        
        # Status indicator
        self.status_frame = tk.Frame(main_frame, bg='#34495e', 
                                    relief=tk.SUNKEN, bd=2)
        self.status_frame.pack(pady=20, padx=50, fill=tk.X)
        
        self.status_label = tk.Label(self.status_frame,
                                     text="⚠️ Sensors: Not Configured",
                                     font=('Arial', 11),
                                     bg='#34495e',
                                     fg='#e67e22')
        self.status_label.pack(pady=10)
        
        # Button container
        button_frame = tk.Frame(main_frame, bg='#2c3e50')
        button_frame.pack(pady=30)
        
        # Device Setup Button (Primary action)
        self.setup_btn = tk.Button(button_frame,
                                  text="⚙️ Device Setup",
                                  font=('Arial', 16, 'bold'),
                                  bg='#e67e22',
                                  fg='white',
                                  padx=40,
                                  pady=20,
                                  command=self.open_device_setup,
                                  cursor='hand2',
                                  relief=tk.RAISED,
                                  bd=3)
        self.setup_btn.pack(pady=15)
        
        # Live Recording Button
        self.live_btn = tk.Button(button_frame,
                                 text="📹 Live Recording",
                                 font=('Arial', 16, 'bold'),
                                 bg='#27ae60',
                                 fg='white',
                                 padx=40,
                                 pady=20,
                                 command=self.open_live_recording,
                                 cursor='hand2',
                                 relief=tk.RAISED,
                                 bd=3,
                                 state='disabled')  # Disabled until setup complete
        self.live_btn.pack(pady=15)
        
        # Playback Button
        self.playback_btn = tk.Button(button_frame,
                                     text="▶️ Playback Recording",
                                     font=('Arial', 16, 'bold'),
                                     bg='#3498db',
                                     fg='white',
                                     padx=40,
                                     pady=20,
                                     command=self.open_playback,
                                     cursor='hand2',
                                     relief=tk.RAISED,
                                     bd=3)
        self.playback_btn.pack(pady=15)
        
        # Exit Button
        self.exit_btn = tk.Button(button_frame,
                                 text="❌ Exit",
                                 font=('Arial', 14),
                                 bg='#c0392b',
                                 fg='white',
                                 padx=40,
                                 pady=15,
                                 command=self.exit_app,
                                 cursor='hand2',
                                 relief=tk.RAISED,
                                 bd=3)
        self.exit_btn.pack(pady=30)
        
        # Instructions
        instructions = tk.Label(main_frame,
                               text="💡 Tip: Complete Device Setup first to enable Live Recording",
                               font=('Arial', 10, 'italic'),
                               bg='#2c3e50',
                               fg='#95a5a6')
        instructions.pack(pady=10)
        
        # Footer
        footer_label = tk.Label(main_frame,
                               text="© 2025 Movella DOT Research Project",
                               font=('Arial', 10),
                               bg='#2c3e50',
                               fg='#95a5a6')
        footer_label.pack(side=tk.BOTTOM, pady=20)
        
        # Add hover effects
        self.add_hover_effects()
        
    def add_hover_effects(self):
        """Add hover effects to buttons"""
        def on_enter(e, btn, color):
            if btn['state'] != 'disabled':
                btn['background'] = color
            
        def on_leave(e, btn, original_color):
            if btn['state'] != 'disabled':
                btn['background'] = original_color
        
        # Setup button hover
        self.setup_btn.bind("<Enter>", lambda e: on_enter(e, self.setup_btn, '#f39c12'))
        self.setup_btn.bind("<Leave>", lambda e: on_leave(e, self.setup_btn, '#e67e22'))
        
        # Live Recording button hover
        self.live_btn.bind("<Enter>", lambda e: on_enter(e, self.live_btn, '#2ecc71'))
        self.live_btn.bind("<Leave>", lambda e: on_leave(e, self.live_btn, '#27ae60'))
        
        # Playback button hover
        self.playback_btn.bind("<Enter>", lambda e: on_enter(e, self.playback_btn, '#5dade2'))
        self.playback_btn.bind("<Leave>", lambda e: on_leave(e, self.playback_btn, '#3498db'))
        
        # Exit button hover
        self.exit_btn.bind("<Enter>", lambda e: on_enter(e, self.exit_btn, '#e74c3c'))
        self.exit_btn.bind("<Leave>", lambda e: on_leave(e, self.exit_btn, '#c0392b'))
    
    def open_device_setup(self):
        self.root.withdraw()

        def done(mgr):
            self.dot_manager = mgr
            self.update_sensor_status()
            messagebox.showinfo("Success", "Device setup completed!\nYou can now start live recording.")
            self.root.deiconify()

        def cancelled():
            print("Device setup was not completed")
            self.root.deiconify()

        setup_window = tk.Toplevel(self.root)
        app = DeviceSetupApp(setup_window, on_complete=done, on_cancel=cancelled)

    
    def update_sensor_status(self):
        """Update the sensor status display"""
        if self.dot_manager:
            try:
                mapping = self.dot_manager.get_body_position_mapping()
                num_sensors = len(mapping)
                
                self.status_label.config(
                    text=f"✅ Sensors: {num_sensors} configured and ready",
                    fg='#27ae60'
                )
                
                # Enable live recording button
                self.live_btn.config(state='normal')
                
                # Show sensor details
                sensor_names = [info['label'] for info in mapping.values()]
                tooltip_text = "Configured: " + ", ".join(sensor_names)
                self.status_label.config(text=self.status_label['text'] + f"\n{tooltip_text}")
            except Exception as e:
                print(f"Error updating sensor status: {e}")
                messagebox.showerror("Error", 
                                    f"Failed to get sensor information.\n{str(e)}")
    
    def open_live_recording(self):
        """Open the live recording screen with configured manager"""
        if not self.dot_manager:
            messagebox.showwarning("Not Ready",
                                  "Please complete Device Setup first!")
            return
        
        # Verify sensors are still connected
        try:
            if not self.dot_manager.is_measurement_active():
                started = self.dot_manager.start_measurement()
                if not started:
                    response = messagebox.askyesno(
                        "Reconnect Required",
                        "Sensors need to be restarted.\n"
                        "Do you want to run device setup again?"
                    )
                    if response:
                        self.open_device_setup()
                    return
        except Exception as e:
            print(f"Warning: Could not check measurement status: {e}")
        
        # Hide home screen
        self.root.withdraw()
        
        # Create live recording window with the manager
        live_window = tk.Toplevel(self.root)
        app = LiveRecordingApp(live_window, dot_manager=self.dot_manager)
        
        def on_close():
            app.on_closing()
            self.root.deiconify()
        
        live_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def open_playback(self):
        """Open playback screen (placeholder)"""
        messagebox.showinfo("Playback",
                           "Playback feature coming soon!\n\n"
                           "This will allow you to view previously recorded sessions.")
    
    def exit_app(self):
        """Exit the application"""
        if messagebox.askokcancel("Quit", "Do you want to exit?"):
            # Cleanup manager if exists
            if self.dot_manager:
                try:
                    self.dot_manager.cleanup()
                except Exception as e:
                    print(f"Error during cleanup: {e}")
            
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    home = HomeScreen(root)
    root.mainloop()