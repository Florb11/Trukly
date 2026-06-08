class EventManager:
    #Esto es el centro del patron:
    # guarda qué objetos estan escuchando cada evento y, cuando pasa algo, les avisa
    def __init__(self):
        self.suscriptores = {}

    # registra un suscriptor para un evento
    def suscribir(self, evento, suscriptor):
        if evento not in self.suscriptores:
            self.suscriptores[evento] = []

        self.suscriptores[evento].append(suscriptor)

    # elimina un suscriptor de un evento
    def desuscribir(self, evento, suscriptor):
        if evento in self.suscriptores:
            self.suscriptores[evento].remove(suscriptor)

    # avisa a todos los suscriptores cuando ocurre un evento
    def notificar(self, evento, datos):
        if evento not in self.suscriptores:
            return

        for suscriptor in self.suscriptores[evento]:
            suscriptor.actualizar(datos)