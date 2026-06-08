class EventListener:
    def actualizar(self, datos):
        raise NotImplementedError("El suscriptor debe implementar actualizar()")
    
    #Esto representa la interfaz suscriptora Osea, cualquier clase que quiera escuchar eventos tiene que tener el metodo actualizar