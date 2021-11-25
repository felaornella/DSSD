const { Router } = require('express');
const router = Router();
const user = require('../controllers/user.controller');
const jwt = require('jsonwebtoken');

// auth se pone entre la ruta y el controlador , lo que hace es verificar si una peticion tiene el token y es valida la peticion deberia ir en todo lo que usa un usuario logeado
const auth = require('../middleware/auth');

// RUTAS
router.post('/signup', user.createUser);
router.post('/signin', user.iniciarSesion);

router.get('/verifyToken/:token', user.validateToken);




module.exports = router;