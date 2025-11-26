# ==========================================================
#                CLASE BASE DE PRODUCTO
# ==========================================================
class Producto:
    """
    Representa un producto genérico de cualquier tienda/marca.
    Esta clase es la base para las subclases específicas (SISI,
    Rotunda, Sierramora), lo que permite usar herencia y polimorfismo.
    """

    def __init__(self, nombre, precio, link, imagen, marca):
        # Nombre del producto
        self.nombre = nombre

        # Precio ya viene normalizado/limpio desde cargar_productos.py
        self.precio = precio

        # Enlace a la página del producto
        self.link = link

        # URL de la imagen del producto
        self.imagen = imagen

        # Marca original del producto
        self.marca = marca

    def mostrar_info(self):
        """
        Devuelve una representación simple y legible del producto.
        Útil para depuración o listados rápidos.
        """
        return f"{self.nombre} - ${self.precio} - {self.marca}"

    def to_dict(self):
        """
        Convierte el producto a un diccionario serializable.
        Se usa para exportar JSON o para debug.
        """
        return {
            "nombre": self.nombre,
            "precio": self.precio,
            "link": self.link,
            "imagen": self.imagen,
            "marca": self.marca
        }


# ==========================================================
#         SUBCLASES SEGÚN MARCA (HERENCIA + POO)
# ==========================================================

class ProductoSiSi(Producto):
    """
    Representa un producto específico de la marca SISI.
    Puede tener métodos propios si en el futuro se necesitan.
    """
    def tipo(self):
        return "Lencería (SISI)"


class ProductoRotunda(Producto):
    """
    Representa un producto de Rotunda.
    Permite diferenciar comportamientos si en el futuro
    la marca requiere lógica especial.
    """
    def tipo(self):
        return "Ropa (Rotunda)"


class ProductoSierramora(Producto):
    """
    Representa un producto de Sierramora.
    Usa herencia para mantener atributos y métodos de Producto,
    pero permite extender comportamiento.
    """
    def tipo(self):
        return "Ropa (Sierramora)"

