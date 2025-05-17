import tkinter as tk
from documentation_viewer import DocumentationViewer

def main():
    # Create the main application window
    root = tk.Tk()
    root.title("Documentation Viewer Test")
    root.geometry("400x300")
    
    # Create a button to open the documentation viewer
    def open_docs():
        DocumentationViewer(root)
    
    button = tk.Button(root, text="Open Documentation", command=open_docs)
    button.pack(pady=20)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main() 