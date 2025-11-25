
class Producto:
    def __init__(self, nombre, precio, link, imagen, marca):
        self.nombre = nombre
        self.precio = precio  # viene limpio ya
        self.link = link
        self.imagen = imagen
        self.marca = marca

    def mostrar_info(self):
        return f"{self.nombre} - ${self.precio} - {self.marca}"

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "precio": self.precio,
            "link": self.link,
            "imagen": self.imagen,
            "marca": self.marca
        }
class ProductoSiSi(Producto):
    def tipo(self):
        return "Lencería (SISI)"


class ProductoRotunda(Producto):
    def tipo(self):
        return "Ropa (Rotunda)"


class ProductoSierramora(Producto):
    def tipo(self):
        return "Ropa (Sierramora)"
