-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         11.5.2-MariaDB - mariadb.org binary distribution
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.6.0.6765
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para luyeri
CREATE DATABASE IF NOT EXISTS `luyeri` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;
USE `luyeri`;

-- Volcando estructura para tabla luyeri.tipos_introvertido
CREATE TABLE IF NOT EXISTS `tipos_introvertido` (
  `id_tipointro` int(11) NOT NULL AUTO_INCREMENT,
  `tipo` varchar(150) NOT NULL,
  `video` text DEFAULT NULL,
  PRIMARY KEY (`id_tipointro`),
  UNIQUE KEY `tipo` (`tipo`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Volcando datos para la tabla luyeri.tipos_introvertido: ~4 rows (aproximadamente)
INSERT INTO `tipos_introvertido` (`id_tipointro`, `tipo`, `video`) VALUES
	(1, 'Social', 'EBwVUxH6OQU'),
	(2, 'Pensativo', 'a2jkUvRtlg0'),
	(3, 'Ansioso', 'lQf7xsi8Xr8'),
	(4, 'Reservado', 'D_9VgBPNwNY');

-- Volcando estructura para tabla luyeri.usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_completo` varchar(100) NOT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `username` varchar(50) NOT NULL,
  `contraseña` char(64) NOT NULL,
  `fecha_registro` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `correo` (`correo`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Volcando datos para la tabla luyeri.usuarios: ~6 rows (aproximadamente)
INSERT INTO `usuarios` (`id_usuario`, `nombre_completo`, `correo`, `username`, `contraseña`, `fecha_registro`) VALUES
	(1, 'Juan Pérez', 'Juanpecausa@gmail.com', 'juanp', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', '2025-06-18 00:00:00'),
	(2, 'Ana López', 'AnaBecausa@gmail.com', 'anal', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', '2025-06-18 00:00:00'),
	(3, 'Carlos Vega', 'CarlosVegas@gmail.com', 'cvega', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', '2025-06-18 00:00:00'),
	(4, 'Yini Pan', 'yinipan@gmail.com', 'yipa', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', '2025-07-09 15:37:43'),
	(5, 'Luis Jimenes', 'Luischepo@hotmail.com', 'luisfer', 'ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f', '2025-07-09 15:37:43'),
	(6, 'Yoel Samaniego', 'yonielvegas', 'yonielvegas', '1234', '2025-07-09 15:37:43');

-- Volcando estructura para tabla luyeri.usuario_intentos
CREATE TABLE IF NOT EXISTS `usuario_intentos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `intentos` int(11) NOT NULL DEFAULT 0,
  `estado` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `usuario_id` (`id_usuario`),
  CONSTRAINT `usuario_intentos_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Volcando datos para la tabla luyeri.usuario_intentos: ~3 rows (aproximadamente)
INSERT INTO `usuario_intentos` (`id`, `id_usuario`, `intentos`, `estado`) VALUES
	(1, 1, 3, 0),
	(2, 2, 0, 1),
	(3, 3, 0, 1),
	(6, 6, 0, 1),
	(7, 5, 0, 1);

-- Volcando estructura para tabla luyeri.usuario_tipo
CREATE TABLE IF NOT EXISTS `usuario_tipo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_usuario` int(11) NOT NULL,
  `id_tipointro` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_tipointro` (`id_tipointro`),
  CONSTRAINT `usuario_tipo_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  CONSTRAINT `usuario_tipo_ibfk_2` FOREIGN KEY (`id_tipointro`) REFERENCES `tipos_introvertido` (`id_tipointro`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Volcando datos para la tabla luyeri.usuario_tipo: ~12 rows (aproximadamente)
INSERT INTO `usuario_tipo` (`id`, `id_usuario`, `id_tipointro`) VALUES
	(1, 1, 1),
	(2, 1, 2),
	(3, 2, 2),
	(4, 2, 3),
	(5, 2, 4),
	(6, 3, 1),
	(7, 4, 1),
	(8, 4, 3),
	(9, 4, 4),
	(10, 5, 2),
	(11, 5, 3),
	(12, 6, 4);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
