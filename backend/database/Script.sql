-- ============================================================
-- BASE DE DATOS: trukly
-- ============================================================
-- CREDENCIALES DE PRUEBA:
--   admin1    / 12345678a
--   chofer1   / 12345678a
--   Operador1 / 12345678a
--   Mecanico1 / 12345678a
-- (los hashes bcrypt ya están incluidos abajo)
-- ============================================================
 
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";
SET NAMES utf8mb4;
 

DROP DATABASE IF EXISTS `trukly`;
CREATE DATABASE `trukly`
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;
 
USE `trukly`;
 


CREATE TABLE `usuario` (
  `id_usuario`   INT(11)      NOT NULL AUTO_INCREMENT,
  `username`     VARCHAR(30)  NOT NULL,
  `email`        VARCHAR(150) DEFAULT NULL,
  `password`     VARCHAR(255) NOT NULL,
  `nombre`       VARCHAR(30)  NOT NULL,
  `apellido`     VARCHAR(30)  NOT NULL,
  `estado`       VARCHAR(45)  NOT NULL,
  `rol`          VARCHAR(50)  NOT NULL DEFAULT 'chofer',
  `foto_perfil`  VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
 

CREATE TABLE `administrador` (
  `Usuario_idUsuario` INT(11)     NOT NULL,
  `legajo`            VARCHAR(45) NOT NULL,
  PRIMARY KEY (`Usuario_idUsuario`),
  CONSTRAINT `fk_Administrador_Usuario`
    FOREIGN KEY (`Usuario_idUsuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;



CREATE TABLE `chofer` (
  `Usuario_idUsuario`   INT(11)     NOT NULL,
  `licencia`            VARCHAR(45) NOT NULL,
  `vencimientoLicencia` DATE        NOT NULL,
  `legajo`              VARCHAR(30) NOT NULL,
  PRIMARY KEY (`Usuario_idUsuario`),
  CONSTRAINT `fk_Chofer_Usuario`
    FOREIGN KEY (`Usuario_idUsuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
 



CREATE TABLE `mecanico` (
  `Usuario_idUsuario` INT(11)     NOT NULL,
  `legajo`            VARCHAR(20) NOT NULL,
  `especialidad`      VARCHAR(30) NOT NULL,
  PRIMARY KEY (`Usuario_idUsuario`),
  CONSTRAINT `fk_Mecanico_Usuario`
    FOREIGN KEY (`Usuario_idUsuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
 

CREATE TABLE `operadorlogistico` (
  `Usuario_idUsuario` INT(11)     NOT NULL,
  `legajo`            VARCHAR(45) NOT NULL,
  `sector`            VARCHAR(45) NOT NULL,
  PRIMARY KEY (`Usuario_idUsuario`),
  CONSTRAINT `fk_OperadorLogistico_Usuario`
    FOREIGN KEY (`Usuario_idUsuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
 


CREATE TABLE `camion` (
  `id_camion`      INT(11)     NOT NULL AUTO_INCREMENT,
  `matricula`      VARCHAR(15) NOT NULL,
  `marca`          VARCHAR(20) NOT NULL,
  `modelo`         VARCHAR(30) NOT NULL,
  `capacidad_carga` DOUBLE     NOT NULL,
  `estado`         VARCHAR(20) NOT NULL,
  `nroTanque`      INT(11)     NOT NULL,
  PRIMARY KEY (`id_camion`),
  UNIQUE KEY `matricula` (`matricula`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
 


CREATE TABLE `viaje` (
  `id_viaje`                          INT(11)      NOT NULL AUTO_INCREMENT,
  `OperadorLogistico_Usuario_idUsuario` INT(11)    NOT NULL,
  `Chofer_Usuario_idUsuario`          INT(11)      NOT NULL,
  `Camion_id_camion`                  INT(11)      NOT NULL,
  `fecha_salida`                      DATE         NOT NULL,
  `fecha_llegada`                     DATE         DEFAULT NULL,
  `origen`                            VARCHAR(45)  NOT NULL,
  `destino`                           VARCHAR(45)  NOT NULL,
  `estado`                            VARCHAR(45)  NOT NULL,
  `observaciones`                     VARCHAR(200) DEFAULT NULL,
  `recorrido`                         DOUBLE       NOT NULL,
  PRIMARY KEY (`id_viaje`),
  KEY `fk_Viaje_OperadorLogistico` (`OperadorLogistico_Usuario_idUsuario`),
  KEY `fk_Viaje_Chofer`            (`Chofer_Usuario_idUsuario`),
  KEY `fk_Viaje_Camion`            (`Camion_id_camion`),
  CONSTRAINT `fk_Viaje_OperadorLogistico`
    FOREIGN KEY (`OperadorLogistico_Usuario_idUsuario`) REFERENCES `operadorlogistico` (`Usuario_idUsuario`),
  CONSTRAINT `fk_Viaje_Chofer`
    FOREIGN KEY (`Chofer_Usuario_idUsuario`) REFERENCES `chofer` (`Usuario_idUsuario`),
  CONSTRAINT `fk_Viaje_Camion`
    FOREIGN KEY (`Camion_id_camion`) REFERENCES `camion` (`id_camion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
 

CREATE TABLE `carga` (
  `id_carga`     INT(11)     NOT NULL AUTO_INCREMENT,
  `descripcion`  VARCHAR(45) NOT NULL,
  `tipo`         VARCHAR(45) NOT NULL,
  `peso`         DOUBLE      NOT NULL,
  `estado`       VARCHAR(45) NOT NULL,
  `Viaje_id_viaje` INT(11)   NOT NULL,
  PRIMARY KEY (`id_carga`),
  KEY `fk_Carga_Viaje` (`Viaje_id_viaje`),
  CONSTRAINT `fk_Carga_Viaje`
    FOREIGN KEY (`Viaje_id_viaje`) REFERENCES `viaje` (`id_viaje`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE `registroingresosalida` (
  `id_registro`    INT(11)      NOT NULL AUTO_INCREMENT,
  `fecha_hora`     DATETIME     NOT NULL,
  `tipo_registro`  VARCHAR(45)  NOT NULL,
  `observacion`    VARCHAR(100) DEFAULT NULL,
  `Viaje_id_viaje` INT(11)      NOT NULL,
  PRIMARY KEY (`id_registro`),
  KEY `fk_RegistroIngresoSalida_Viaje` (`Viaje_id_viaje`),
  CONSTRAINT `fk_RegistroIngresoSalida_Viaje`
    FOREIGN KEY (`Viaje_id_viaje`) REFERENCES `viaje` (`id_viaje`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
 

CREATE TABLE `reportefalla` (
  `id_reporte`                INT(11)      NOT NULL AUTO_INCREMENT,
  `fecha_hora`                DATETIME     NOT NULL,
  `descripcion`               VARCHAR(200) NOT NULL,
  `estado`                    VARCHAR(45)  NOT NULL,
  `Camion_id_camion`          INT(11)      NOT NULL,
  `Mecanico_Usuario_idUsuario` INT(11)     DEFAULT NULL,
  `Chofer_Usuario_idUsuario`  INT(11)      NOT NULL,
  `nota_reparacion`           VARCHAR(255) DEFAULT NULL,
  `fecha_resolucion`          DATETIME     DEFAULT NULL,
  PRIMARY KEY (`id_reporte`),
  KEY `fk_ReporteFalla_Camion`   (`Camion_id_camion`),
  KEY `fk_ReporteFalla_Mecanico` (`Mecanico_Usuario_idUsuario`),
  KEY `fk_ReporteFalla_Chofer`   (`Chofer_Usuario_idUsuario`),
  CONSTRAINT `fk_ReporteFalla_Camion`
    FOREIGN KEY (`Camion_id_camion`) REFERENCES `camion` (`id_camion`),
  CONSTRAINT `fk_ReporteFalla_Mecanico`
    FOREIGN KEY (`Mecanico_Usuario_idUsuario`) REFERENCES `mecanico` (`Usuario_idUsuario`),
  CONSTRAINT `fk_ReporteFalla_Chofer`
    FOREIGN KEY (`Chofer_Usuario_idUsuario`) REFERENCES `chofer` (`Usuario_idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
 

CREATE TABLE `notificacion` (
  `id_notificacion`  INT(11)      NOT NULL AUTO_INCREMENT,
  `Usuario_idUsuario` INT(11)     NOT NULL,
  `titulo`           VARCHAR(100) NOT NULL,
  `mensaje`          VARCHAR(255) NOT NULL,
  `leida`            TINYINT(1)   DEFAULT 0,
  `fecha_hora`       DATETIME     NOT NULL,
  `tipo`             VARCHAR(45)  DEFAULT NULL,
  PRIMARY KEY (`id_notificacion`),
  KEY `fk_Notificacion_Usuario` (`Usuario_idUsuario`),
  CONSTRAINT `fk_Notificacion_Usuario`
    FOREIGN KEY (`Usuario_idUsuario`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `usuario` (`id_usuario`, `username`, `email`, `password`, `nombre`, `apellido`, `estado`, `rol`) VALUES
(1,  'admin1',    'admin1@trukly.com',    '$2b$12$cxSgvwGZo8hq4taHO7vakOZDz3OsvCczKXmb65kjxwUD/qA1BWn5.', 'Admin',    'Admin',  'activo', 'admin'),
(17, 'chofer1',   'chofer1@trukly.com',   '$2b$12$ZsRkAnC7woC545bO83W81uOCoBBeibc3152U2EJbFNbZc8QeYFaE6', 'Matias',   'Perez',  'activo', 'chofer'),
(22, 'Operador1', 'operador@gmail.com',   '$2b$12$/tBoQw4fXYMMl13nnLsMFONe0vWJLaWYam0u/MonzBe2EyUoz2ffq', 'Sebastian','Lopez',  'activo', 'operador'),
(23, 'Mecanico1', 'meca1@hotmail.com',    '$2b$12$xgCsIR3OrHvg.Jgiuz59v.dPTb/tssPSmFQWRSv/VEg0HPXWNtnO2', 'Elias',    'Lopez',  'activo', 'mecanico');
 
INSERT INTO `administrador` (`Usuario_idUsuario`, `legajo`) VALUES
(1, 'ADM001');
 
INSERT INTO `chofer` (`Usuario_idUsuario`, `licencia`, `vencimientoLicencia`, `legajo`) VALUES
(17, '06-87654321C-2', '2026-11-13', 'CH002');
 
INSERT INTO `operadorlogistico` (`Usuario_idUsuario`, `legajo`, `sector`) VALUES
(22, 'OL-001', 'Logistica');
 
INSERT INTO `mecanico` (`Usuario_idUsuario`, `legajo`, `especialidad`) VALUES
(23, 'MEC001', 'Motores');
 

INSERT INTO `camion` (`id_camion`, `matricula`, `marca`, `modelo`, `capacidad_carga`, `estado`, `nroTanque`) VALUES
(1, 'DEF5678',  'Scania',   'R450',   30000, 'disponible',      1),
(2, 'GHI9012',  'Mercedes', 'Actros', 26000, 'disponible',      2),
(3, 'JKL3456',  'Iveco',    'S-Way',  24000, 'disponible',      3),
(4, 'MNO7890',  'Volvo',    'FH',     28000, 'disponible',      4),
(5, 'PQR1234',  'Volvo',    'GH',     28888, 'en mantenimiento', 5),
(9, 'STU5678',  'Volvo',    'FH2',    6000,  'en mantenimiento', 9);
 


INSERT INTO `viaje` (`id_viaje`, `OperadorLogistico_Usuario_idUsuario`, `Chofer_Usuario_idUsuario`, `Camion_id_camion`, `fecha_salida`, `fecha_llegada`, `origen`, `destino`, `estado`, `observaciones`, `recorrido`) VALUES
(20, 22, 17, 1, '2026-06-30', '2026-07-31', 'Buenos Aires', 'Rosario',    'pendiente',  'No hay observaciones para este viaje.',          299),
(21, 22, 17, 2, '2026-07-22', '2026-07-30', 'Cordoba',      'Chacabuco',  'pendiente',  'En la llegada se debe presentar la documentación.', 1200),
(22, 22, 17, 5, '2026-06-02', '2026-06-10', 'Chacabuco',    'Paraguay',   'finalizado', 'Presentar documentación en la frontera.',        1443),
(23, 22, 17, 2, '2026-06-16', '2026-06-16', 'Buenos Aires', 'Chacabuco',  'cancelado',  'Cancelado por admin. Motivo: El camión presentó problemas.', 190);
 


INSERT INTO `reportefalla` (`id_reporte`, `fecha_hora`, `descripcion`, `estado`, `Camion_id_camion`, `Mecanico_Usuario_idUsuario`, `Chofer_Usuario_idUsuario`, `nota_reparacion`, `fecha_resolucion`) VALUES
(1, '2026-06-18 04:12:41', 'Ruido en el motor',        'pendiente',   5, NULL, 17, NULL, NULL),
(2, '2026-06-18 04:12:55', 'Problema con las ruedas',  'en revision', 9, 23,   17, NULL, NULL);
 


INSERT INTO `notificacion` (`id_notificacion`, `Usuario_idUsuario`, `titulo`, `mensaje`, `leida`, `fecha_hora`, `tipo`) VALUES
(1, 22, 'Nuevo reporte de falla',   'El chofer #17 creó el reporte #1.', 1, '2026-06-18 04:12:41', 'reporte_creado'),
(2, 22, 'Nuevo reporte de falla',   'El chofer #17 creó el reporte #2.', 0, '2026-06-18 04:12:55', 'reporte_creado'),
(3, 23, 'Nueva reparación asignada','Se te asignó el reporte #2 del camión #9.', 0, '2026-06-18 04:13:27', 'reporte_asignado');
 
COMMIT;