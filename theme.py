import tkinter as tk
from tkinter import ttk

class ThemeManager:
    # Color scheme
    COLORS = {
        'primary': '#2c3e50',      # Dark blue-gray
        'secondary': '#3498db',    # Bright blue
        'accent': '#e74c3c',       # Red
        'success': '#2ecc71',      # Green
        'warning': '#f1c40f',      # Yellow
        'error': '#e74c3c',        # Red
        'background': '#ecf0f1',   # Light gray
        'surface': '#ffffff',      # White
        'text': '#2c3e50',         # Dark blue-gray
        'text_secondary': '#7f8c8d' # Gray
    }
    
    # Fonts
    FONTS = {
        'heading': ('Helvetica', 24, 'bold'),
        'subheading': ('Helvetica', 18, 'bold'),
        'body': ('Helvetica', 12),
        'small': ('Helvetica', 10)
    }
    
    @classmethod
    def apply_theme(cls, root):
        # Configure root window
        root.configure(bg=cls.COLORS['background'])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')  # Use clam as base theme
        
        # Configure frame styles
        style.configure('Main.TFrame', background=cls.COLORS['background'])
        style.configure('Card.TFrame', background=cls.COLORS['surface'])
        
        # Configure label styles
        style.configure('Heading.TLabel',
                       font=cls.FONTS['heading'],
                       foreground=cls.COLORS['text'],
                       background=cls.COLORS['background'])
        
        style.configure('Subheading.TLabel',
                       font=cls.FONTS['subheading'],
                       foreground=cls.COLORS['text'],
                       background=cls.COLORS['background'])
        
        style.configure('Body.TLabel',
                       font=cls.FONTS['body'],
                       foreground=cls.COLORS['text'],
                       background=cls.COLORS['background'])
        
        style.configure('Secondary.TLabel',
                       font=cls.FONTS['body'],
                       foreground=cls.COLORS['text_secondary'],
                       background=cls.COLORS['background'])
        
        # Configure button styles
        style.configure('Primary.TButton',
                       font=cls.FONTS['body'],
                       background=cls.COLORS['primary'],
                       foreground='white')
        
        style.configure('Secondary.TButton',
                       font=cls.FONTS['body'],
                       background=cls.COLORS['secondary'],
                       foreground='white')
        
        style.configure('Accent.TButton',
                       font=cls.FONTS['body'],
                       background=cls.COLORS['accent'],
                       foreground='white')
        
        # Configure combobox styles
        style.configure('TCombobox',
                       font=cls.FONTS['body'],
                       background=cls.COLORS['surface'],
                       fieldbackground=cls.COLORS['surface'],
                       selectbackground=cls.COLORS['secondary'],
                       selectforeground='white')
        
        # Configure treeview styles
        style.configure('Treeview',
                       font=cls.FONTS['body'],
                       background=cls.COLORS['surface'],
                       fieldbackground=cls.COLORS['surface'],
                       foreground=cls.COLORS['text'])
        
        style.configure('Treeview.Heading',
                       font=cls.FONTS['body'],
                       background=cls.COLORS['primary'],
                       foreground='white')
        
        # Configure scrollbar styles
        style.configure('Vertical.TScrollbar',
                       background=cls.COLORS['background'],
                       troughcolor=cls.COLORS['surface'],
                       width=10,
                       arrowsize=13)
        
        # Configure entry styles
        style.configure('TEntry',
                       font=cls.FONTS['body'],
                       fieldbackground=cls.COLORS['surface'],
                       foreground=cls.COLORS['text'])
        
        # Configure checkbutton styles
        style.configure('TCheckbutton',
                       font=cls.FONTS['body'],
                       background=cls.COLORS['background'],
                       foreground=cls.COLORS['text']) 