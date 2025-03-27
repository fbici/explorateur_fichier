import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk, ImageDraw
from datetime import datetime

class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Explorateur de Fichiers")
        self.root.geometry("1000x700")
        
        # Configuration initiale
        self.app_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "MonExplorateur")
        os.makedirs(self.app_folder, exist_ok=True)
        self.current_path = self.app_folder
        self.favorites = set()
        self.history = []
        self.filter_ext = "*"  # Tous les fichiers par défaut

        # Création des icônes de base
        self.folder_icon = self.create_icon(is_folder=True)
        self.file_icon = self.create_icon(is_folder=False)
        self.back_icon = self.create_back_icon()

        # Initialisation de l'interface
        self.setup_ui()
        self.load_directory()

    def create_icon(self, is_folder=False):
        """Crée une icône simple pour les fichiers/dossiers"""
        img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        if is_folder:
            # Icône de dossier (jaune)
            draw.rectangle([8, 12, 28, 28], fill=(255, 255, 0))
            draw.polygon([(8, 12), (18, 6), (28, 12)], fill=(255, 255, 0))
        else:
            # Icône de fichier (blanc avec bordure bleue)
            draw.rectangle([8, 6, 28, 28], fill=(255, 255, 255), outline=(0, 0, 255))
        
        return ImageTk.PhotoImage(img)

    def create_back_icon(self):
        """Crée une icône de retour"""
        img = Image.new('RGBA', (32, 32), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.polygon([(20, 8), (10, 16), (20, 24)], fill=(0, 0, 255))
        return ImageTk.PhotoImage(img)

    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Cadre principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Barre latérale
        self.sidebar = tk.Frame(self.main_frame, width=200, bg="#f0f0f0")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Boutons de navigation
        tk.Button(self.sidebar, text="⭐ Favoris", command=self.show_favorites).pack(fill=tk.X, pady=5)
        tk.Button(self.sidebar, text="📁 Nouveau dossier", command=self.create_folder).pack(fill=tk.X, pady=5)
        tk.Button(self.sidebar, text="⬆️ Importer", command=self.upload_file).pack(fill=tk.X, pady=5)
        
        # Bouton Retour
        back_frame = tk.Frame(self.sidebar)
        back_frame.pack(fill=tk.X, pady=5)
        tk.Label(back_frame, image=self.back_icon).pack(side=tk.LEFT)
        tk.Button(back_frame, text="Retour", command=self.go_back).pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(self.sidebar, text="🔄 Actualiser", command=self.load_directory).pack(fill=tk.X, pady=5)

        # Filtres de fichiers
        filter_frame = tk.Frame(self.sidebar)
        filter_frame.pack(fill=tk.X, pady=10)
        tk.Label(filter_frame, text="Filtrer par type:").pack()
        
        self.filter_var = tk.StringVar(value="*")
        tk.Radiobutton(filter_frame, text="Tous les fichiers", variable=self.filter_var, value="*", command=self.apply_filter).pack(anchor=tk.W)
        tk.Radiobutton(filter_frame, text="Images", variable=self.filter_var, value=".jpg;.png;.gif", command=self.apply_filter).pack(anchor=tk.W)
        tk.Radiobutton(filter_frame, text="Textes", variable=self.filter_var, value=".txt;.csv;.json", command=self.apply_filter).pack(anchor=tk.W)
        tk.Radiobutton(filter_frame, text="Documents", variable=self.filter_var, value=".pdf;.docx;.xlsx", command=self.apply_filter).pack(anchor=tk.W)

        # Zone d'affichage principale
        self.file_frame = tk.Frame(self.main_frame)
        self.file_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Barre de chemin
        self.path_frame = tk.Frame(self.file_frame)
        self.path_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(self.path_frame, text="Chemin:").pack(side=tk.LEFT)
        self.path_entry = tk.Entry(self.path_frame)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.path_entry.bind("<Return>", lambda e: self.change_directory())
        tk.Button(self.path_frame, text="Ouvrir", command=self.change_directory).pack(side=tk.RIGHT)

        # Barre de recherche
        self.search_frame = tk.Frame(self.file_frame)
        self.search_frame.pack(fill=tk.X, padx=5, pady=5)
        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Button(self.search_frame, text="🔍 Rechercher", command=self.search_files).pack(side=tk.RIGHT)

        # Liste des fichiers
        self.tree_frame = tk.Frame(self.file_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.tree_scroll = ttk.Scrollbar(self.tree_frame)
        self.tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("size", "date"),
            show="tree headings",
            yscrollcommand=self.tree_scroll.set
        )
        self.tree_scroll.config(command=self.tree.yview)
        
        # Configuration des colonnes
        self.tree.column("#0", width=300, anchor=tk.W)
        self.tree.heading("#0", text="Nom", anchor=tk.W)
        self.tree.column("size", width=100, anchor=tk.E)
        self.tree.heading("size", text="Taille", anchor=tk.E)
        self.tree.column("date", width=150, anchor=tk.W)
        self.tree.heading("date", text="Date modif.", anchor=tk.W)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.open_item)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Menu contextuel
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Ouvrir", command=self.open_item)
        self.context_menu.add_command(label="Renommer", command=self.rename_item)
        self.context_menu.add_command(label="Supprimer", command=self.delete_item)
        self.context_menu.add_command(label="⭐ Ajouter aux favoris", command=self.add_to_favorites)
        self.context_menu.add_command(label="Propriétés", command=self.show_properties)

    def apply_filter(self):
        """Applique le filtre sélectionné"""
        self.filter_ext = self.filter_var.get()
        self.load_directory()

    def go_back(self):
        """Retourne au dossier précédent"""
        if len(self.history) > 1:  # On garde toujours le dossier courant dans l'historique
            self.history.pop()  # Enlève le dossier courant
            self.current_path = self.history.pop()  # Prend le précédent
            self.load_directory()

    def load_directory(self):
        """Charge le contenu du répertoire courant"""
        # Mise à jour de l'historique
        if not self.history or self.history[-1] != self.current_path:
            self.history.append(self.current_path)
        
        self.tree.delete(*self.tree.get_children())
        self.path_entry.delete(0, tk.END)
        self.path_entry.insert(0, self.current_path)
        
        try:
            # Ajouter le dossier parent
            parent = os.path.dirname(self.current_path)
            if self.current_path != parent:
                self.tree.insert("", 0, text="..", values=("", ""), image=self.folder_icon)

            # Lister le contenu avec filtre
            for item in sorted(os.listdir(self.current_path)):
                full_path = os.path.join(self.current_path, item)
                
                # Appliquer le filtre
                if os.path.isfile(full_path):
                    ext = os.path.splitext(item)[1].lower()
                    if self.filter_ext != "*" and ext not in self.filter_ext.split(";"):
                        continue
                
                try:
                    if os.path.isdir(full_path):
                        self.tree.insert("", tk.END, 
                                       text=item,
                                       values=("-", datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%d/%m/%Y %H:%M')),
                                       image=self.folder_icon)
                    else:
                        size = os.path.getsize(full_path)
                        size_str = f"{size/1024:.1f} Ko" if size < 1024*1024 else f"{size/(1024*1024):.1f} Mo"
                        self.tree.insert("", tk.END,
                                       text=item,
                                       values=(size_str, datetime.fromtimestamp(os.path.getmtime(full_path)).strftime('%d/%m/%Y %H:%M')),
                                       image=self.file_icon)
                except Exception as e:
                    print(f"Erreur avec {item}: {e}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le répertoire: {e}")

    def show_context_menu(self, event):
        """Affiche le menu contextuel au clic droit"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def open_item(self, event=None):
        """Ouvre un fichier ou dossier"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            name = item["text"]
            
            if name == "..":
                new_path = os.path.dirname(self.current_path)
            else:
                new_path = os.path.join(self.current_path, name)
            
            if os.path.isdir(new_path):
                self.current_path = new_path
                self.load_directory()
            else:
                try:
                    os.startfile(new_path)
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier: {e}")

    def create_folder(self):
        """Crée un nouveau dossier"""
        name = simpledialog.askstring("Nouveau dossier", "Nom du dossier:")
        if name:
            try:
                os.makedirs(os.path.join(self.current_path, name), exist_ok=True)
                self.load_directory()
                messagebox.showinfo("Succès", f"Dossier '{name}' créé avec succès!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de créer le dossier: {e}")

    def upload_file(self):
        """Importe un fichier dans le dossier courant"""
        file = filedialog.askopenfilename(title="Sélectionner un fichier à importer")
        if file:
            try:
                shutil.copy(file, self.current_path)
                self.load_directory()
                messagebox.showinfo("Succès", "Fichier importé avec succès!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'importer le fichier: {e}")

    def change_directory(self):
        """Change le répertoire courant"""
        path = self.path_entry.get()
        if os.path.isdir(path):
            self.current_path = path
            self.load_directory()
        else:
            messagebox.showerror("Erreur", "Chemin invalide")

    def search_files(self):
        """Recherche des fichiers contenant le texte saisi"""
        query = self.search_entry.get().lower()
        if not query:
            return
            
        self.tree.delete(*self.tree.get_children())
        found = False
        
        for root, dirs, files in os.walk(self.current_path):
            for name in dirs + files:
                if query in name.lower():
                    found = True
                    path = os.path.join(root, name)
                    if os.path.isdir(path):
                        self.tree.insert("", tk.END, text=name, values=("-", ""), image=self.folder_icon)
                    else:
                        size = os.path.getsize(path)
                        size_str = f"{size/1024:.1f} Ko" if size < 1024*1024 else f"{size/(1024*1024):.1f} Mo"
                        self.tree.insert("", tk.END, text=name, values=(size_str, ""), image=self.file_icon)
        
        if not found:
            messagebox.showinfo("Recherche", "Aucun résultat trouvé")

    def rename_item(self):
        """Renomme un fichier ou dossier"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            old_name = item["text"]
            
            if old_name == "..":
                return
                
            new_name = simpledialog.askstring("Renommer", "Nouveau nom:", initialvalue=old_name)
            if new_name and new_name != old_name:
                try:
                    os.rename(
                        os.path.join(self.current_path, old_name),
                        os.path.join(self.current_path, new_name)
                    )
                    self.load_directory()
                    messagebox.showinfo("Succès", f"'{old_name}' renommé en '{new_name}'")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de renommer: {e}")

    def delete_item(self):
        """Supprime un fichier ou dossier"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            name = item["text"]
            
            if name == "..":
                return
                
            full_path = os.path.join(self.current_path, name)
            if messagebox.askyesno("Confirmer", f"Supprimer '{name}' ?"):
                try:
                    if os.path.isdir(full_path):
                        shutil.rmtree(full_path)
                    else:
                        os.remove(full_path)
                    self.load_directory()
                    messagebox.showinfo("Succès", f"'{name}' supprimé avec succès")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de supprimer: {e}")

    def add_to_favorites(self):
        """Ajoute un élément aux favoris"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            name = item["text"]
            
            if name != "..":
                self.favorites.add(os.path.join(self.current_path, name))
                messagebox.showinfo("Favoris", f"'{name}' ajouté aux favoris")

    def show_favorites(self):
        """Affiche la liste des favoris"""
        self.tree.delete(*self.tree.get_children())
        
        if not self.favorites:
            messagebox.showinfo("Favoris", "Aucun favori enregistré")
            return
            
        for fav in self.favorites:
            if os.path.exists(fav):
                name = os.path.basename(fav)
                if os.path.isdir(fav):
                    self.tree.insert("", tk.END, text=name, values=("-", ""), image=self.folder_icon)
                else:
                    size = os.path.getsize(fav)
                    size_str = f"{size/1024:.1f} Ko" if size < 1024*1024 else f"{size/(1024*1024):.1f} Mo"
                    self.tree.insert("", tk.END, text=name, values=(size_str, ""), image=self.file_icon)

    def show_properties(self):
        """Affiche les propriétés d'un fichier/dossier"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            name = item["text"]
            
            if name == "..":
                return
                
            full_path = os.path.join(self.current_path, name)
            stats = os.stat(full_path)
            
            properties = f"Nom: {name}\n"
            properties += f"Chemin: {full_path}\n"
            properties += f"Type: {'Dossier' if os.path.isdir(full_path) else 'Fichier'}\n"
            
            if not os.path.isdir(full_path):
                size = os.path.getsize(full_path)
                properties += f"Taille: {size} octets ({size/1024:.1f} Ko)\n"
            
            properties += f"Créé le: {datetime.fromtimestamp(stats.st_ctime)}\n"
            properties += f"Modifié le: {datetime.fromtimestamp(stats.st_mtime)}\n"
            properties += f"Dernier accès: {datetime.fromtimestamp(stats.st_atime)}"
            
            messagebox.showinfo("Propriétés", properties)

# Lancement de l'application
if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()






