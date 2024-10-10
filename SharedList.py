import threading
import pandas as pd
import os, re

class SharedList:
    def __init__(self, file_path = 'results/products_without_img.csv', for_folders_containing_less_than_5_images=False):
        self.lock = threading.Lock()
        self.file_path = file_path
        self.allData = []
        self.nb_allData = 0
        self.data = []
        self.load_data()
        if for_folders_containing_less_than_5_images :
            self.load_data_for_folders_containing_less_than_5_images()
        
    def load_data(self) :
        def create_string_list_from_columns(csv_file):
            # Lire le fichier CSV
            df = pd.read_csv(csv_file)
            # Remplacer les valeurs NaN dans 'frontOrRear' par une chaîne vide
            df['frontOrRear'] = df['frontOrRear'].fillna('')
            df = df.drop_duplicates(subset=['frontOrRear', 'products_name','Model','brand_name'], keep='first')
            # Créer une liste des chaînes de caractères en combinant les colonnes
            string_list = df.apply(lambda row: f"{row['brand_name']} || {row['Model']} || {row['products_name']} || {row['frontOrRear']}", axis=1)
            
            # Convertir en liste Python
            string_list = string_list.tolist()
            
            return string_list
        
        csv_file = self.file_path
        self.allData = create_string_list_from_columns(csv_file)
        self.nb_allData = len(self.allData)

    def nom_valide(self, chaine):
        # Supprimer les espaces au début et à la fin
        chaine = chaine.strip()
        # Remplacer les espaces multiples par un seul tiret bas
        chaine = re.sub(r'\s+', '_', chaine)
        # Supprimer les caractères non autorisés (garde les lettres, chiffres, tirets bas et points)
        chaine = re.sub(r'[^\w.-]', '_', chaine)
        return chaine
        
    def load_data_for_folders_containing_less_than_5_images(self):
        dict = {}
        for key_words in self.allData:
            dict[' '.join([self.nom_valide(kw) for kw in key_words.split(' || ') if kw.strip() != ""])] = key_words

        new_data_list = []
        
        # Chemin du dossier principal
        dossier_principal = 'images'
        i=0
        # Parcourir les sous-dossiers
        for sous_dossier in os.listdir(dossier_principal):
            chemin_sous_dossier = os.path.join(dossier_principal, sous_dossier)
            
            # Vérifier si c'est un dossier
            if os.path.isdir(chemin_sous_dossier):
                # Compter les fichiers dans le sous-dossier
                nombre_fichiers = len([f for f in os.listdir(chemin_sous_dossier) if os.path.isfile(os.path.join(chemin_sous_dossier, f))])
                
                # Vérifier si le nombre de fichiers est différent de 5
                if nombre_fichiers < 5:
                    key_words = dict.get(sous_dossier)
                    if key_words:
                        new_data_list.append(key_words)
                        i += 1

        print(f"le nombre de dossiers contient moins de 5 fichiers est {i}")
        self.allData = new_data_list
        self.nb_allData = len(self.allData)
            
    def select_data(self, start, end):
        if end < self.nb_allData:
            self.data = self.allData[start:end]
        else:
            self.data = self.allData[start:self.nb_allData]