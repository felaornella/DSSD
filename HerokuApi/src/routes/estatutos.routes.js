const { Router } = require('express');
const router = Router();
const estatuto = require('../controllers/estatuto.controller');


// auth se pone entre la ruta y el controlador , lo que hace es verificar si una peticion tiene el token y es valida la peticion deberia ir en todo lo que usa un usuario logeado
const auth = require('../middleware/auth');

// RUTAS 
router.post('/file',auth, estatuto.uploadEstatuto);



module.exports = router;