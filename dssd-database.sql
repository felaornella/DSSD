-- phpMyAdmin SQL Dump
-- version 5.1.0
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 05-10-2021 a las 05:17:34
-- Versión del servidor: 10.4.18-MariaDB
-- Versión de PHP: 8.0.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `dssd`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sociedad`
--

CREATE TABLE `sociedad` (
  `id` int(11) NOT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `fechaCreacion` datetime DEFAULT NULL,
  `domicilioLegal` varchar(255) DEFAULT NULL,
  `domicilioReal` varchar(255) DEFAULT NULL,
  `correoApoderado` varchar(255) DEFAULT NULL,
  `paises` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sociedad_tiene_socios`
--

CREATE TABLE `sociedad_tiene_socios` (
  `sociedad_id` int(11) NOT NULL,
  `socio_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `socio`
--

CREATE TABLE `socio` (
  `id` int(11) NOT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `apellido` varchar(255) DEFAULT NULL,
  `porcentaje` int(11) DEFAULT NULL,
  `apoderado` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `sociedad`
--
ALTER TABLE `sociedad`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `sociedad_tiene_socios`
--
ALTER TABLE `sociedad_tiene_socios`
  ADD PRIMARY KEY (`sociedad_id`,`socio_id`),
  ADD KEY `socio_id` (`socio_id`);

--
-- Indices de la tabla `socio`
--
ALTER TABLE `socio`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `sociedad`
--
ALTER TABLE `sociedad`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `socio`
--
ALTER TABLE `socio`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `sociedad_tiene_socios`
--
ALTER TABLE `sociedad_tiene_socios`
  ADD CONSTRAINT `sociedad_tiene_socios_ibfk_1` FOREIGN KEY (`sociedad_id`) REFERENCES `sociedad` (`id`),
  ADD CONSTRAINT `sociedad_tiene_socios_ibfk_2` FOREIGN KEY (`socio_id`) REFERENCES `socio` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
