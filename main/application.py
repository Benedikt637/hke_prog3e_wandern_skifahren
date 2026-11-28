class Application:
    def status(self):
        self.name = "Wander Routen Finder"
        self.version = "0.2.0"
        self.description = "Eine APP zum finden von Wanderrouten in der Umgebung"
        self.developers = ["Simon Trommer", "Benedikt Rosenstetter", "Tobias Reisle", "Luis Wehrmann"]
        self.product_owner = "Benedikt Rosenstetter"
        self.tags = ["streamlit", "folium", "geolocation"]

        print("")
        print("======================================================================================")
        print(f"App-Name: {self.name}")
        print(f"Version: {self.version}")
        print(f"Beschreibung: {self.description}")
        print(f"Entwickler: {self.developers}")
        print(f"Produkt Owner: {self.product_owner}")
        print(f"Tags: {self.tags}")
        print("======================================================================================")
        print("")

if __name__ == "__main__":
    app = Application()
    app.status()