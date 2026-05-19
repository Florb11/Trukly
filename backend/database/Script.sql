DROP DATABASE IF EXISTS trukly;
CREATE DATABASE trukly;
USE trukly;

CREATE TABLE Usuario (
  id_usuario INT NOT NULL AUTO_INCREMENT,
  username VARCHAR(30) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  nombre VARCHAR(30) NOT NULL,
  apellido VARCHAR(30) NOT NULL,
  estado VARCHAR(45) NOT NULL,
  rol VARCHAR(50) NOT NULL DEFAULT 'chofer',
  PRIMARY KEY (id_usuario)
);

CREATE TABLE Administrador (
  Usuario_idUsuario INT NOT NULL,
  legajo VARCHAR(45) NOT NULL,
  PRIMARY KEY (Usuario_idUsuario),
  CONSTRAINT fk_Administrador_Usuario
    FOREIGN KEY (Usuario_idUsuario)
    REFERENCES Usuario(id_usuario)
);

CREATE TABLE Chofer (
  Usuario_idUsuario INT NOT NULL,
  licencia VARCHAR(45) NOT NULL,
  vencimientoLicencia DATE NOT NULL,
  legajo VARCHAR(30) NOT NULL,
  PRIMARY KEY (Usuario_idUsuario),
  CONSTRAINT fk_Chofer_Usuario
    FOREIGN KEY (Usuario_idUsuario)
    REFERENCES Usuario(id_usuario)
);

CREATE TABLE OperadorLogistico (
  Usuario_idUsuario INT NOT NULL,
  legajo VARCHAR(45) NOT NULL,
  sector VARCHAR(45) NOT NULL,
  PRIMARY KEY (Usuario_idUsuario),
  CONSTRAINT fk_OperadorLogistico_Usuario
    FOREIGN KEY (Usuario_idUsuario)
    REFERENCES Usuario(id_usuario)
);

CREATE TABLE Mecanico (
  Usuario_idUsuario INT NOT NULL,
  legajo VARCHAR(20) NOT NULL,
  especialidad VARCHAR(30) NOT NULL,
  PRIMARY KEY (Usuario_idUsuario),
  CONSTRAINT fk_Mecanico_Usuario
    FOREIGN KEY (Usuario_idUsuario)
    REFERENCES Usuario(id_usuario)
);

CREATE TABLE Camion (
  id_camion INT NOT NULL AUTO_INCREMENT,
  matricula VARCHAR(15) NOT NULL UNIQUE,
  marca VARCHAR(20) NOT NULL,
  modelo VARCHAR(30) NOT NULL,
  capacidad_carga DOUBLE NOT NULL,
  estado VARCHAR(20) NOT NULL,
  nroTanque INT NOT NULL,
  PRIMARY KEY (id_camion)
);

CREATE TABLE Viaje (
  id_viaje INT NOT NULL AUTO_INCREMENT,
  OperadorLogistico_Usuario_idUsuario INT NOT NULL,
  Chofer_Usuario_idUsuario INT NOT NULL,
  Camion_id_camion INT NOT NULL,
  fecha_salida DATE NOT NULL,
  fecha_llegada DATE NULL,
  origen VARCHAR(45) NOT NULL,
  destino VARCHAR(45) NOT NULL,
  estado VARCHAR(45) NOT NULL,
  observaciones VARCHAR(200) NULL,
  recorrido DOUBLE NOT NULL,
  PRIMARY KEY (id_viaje),
  CONSTRAINT fk_Viaje_OperadorLogistico
    FOREIGN KEY (OperadorLogistico_Usuario_idUsuario)
    REFERENCES OperadorLogistico(Usuario_idUsuario),
  CONSTRAINT fk_Viaje_Chofer
    FOREIGN KEY (Chofer_Usuario_idUsuario)
    REFERENCES Chofer(Usuario_idUsuario),
  CONSTRAINT fk_Viaje_Camion
    FOREIGN KEY (Camion_id_camion)
    REFERENCES Camion(id_camion)
);

CREATE TABLE Carga (
  id_carga INT NOT NULL AUTO_INCREMENT,
  descripcion VARCHAR(45) NOT NULL,
  tipo VARCHAR(45) NOT NULL,
  peso DOUBLE NOT NULL,
  estado VARCHAR(45) NOT NULL,
  Viaje_id_viaje INT NOT NULL,
  PRIMARY KEY (id_carga),
  CONSTRAINT fk_Carga_Viaje
    FOREIGN KEY (Viaje_id_viaje)
    REFERENCES Viaje(id_viaje)
);

CREATE TABLE ReporteFalla (
  id_reporte INT NOT NULL AUTO_INCREMENT,
  fecha_hora DATETIME NOT NULL,
  descripcion VARCHAR(200) NOT NULL,
  estado VARCHAR(45) NOT NULL,
  Camion_id_camion INT NOT NULL,
  Mecanico_Usuario_idUsuario INT NULL,
  Chofer_Usuario_idUsuario INT NOT NULL,
  PRIMARY KEY (id_reporte),
  CONSTRAINT fk_ReporteFalla_Camion
    FOREIGN KEY (Camion_id_camion)
    REFERENCES Camion(id_camion),
  CONSTRAINT fk_ReporteFalla_Mecanico
    FOREIGN KEY (Mecanico_Usuario_idUsuario)
    REFERENCES Mecanico(Usuario_idUsuario),
  CONSTRAINT fk_ReporteFalla_Chofer
    FOREIGN KEY (Chofer_Usuario_idUsuario)
    REFERENCES Chofer(Usuario_idUsuario)
);

CREATE TABLE RegistroIngresoSalida (
  id_registro INT NOT NULL AUTO_INCREMENT,
  fecha_hora DATETIME NOT NULL,
  tipo_registro VARCHAR(45) NOT NULL,
  observacion VARCHAR(100) NULL,
  Viaje_id_viaje INT NOT NULL,
  PRIMARY KEY (id_registro),
  CONSTRAINT fk_RegistroIngresoSalida_Viaje
    FOREIGN KEY (Viaje_id_viaje)
    REFERENCES Viaje(id_viaje)
);