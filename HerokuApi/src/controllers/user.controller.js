const userCtrl = {};
const User = require('../models/User');
const jwt = require('jsonwebtoken');


userCtrl.getUsers = async(req, res) => {
    const users = await User.find();
    res.json(users);
}

userCtrl.getUser = async(req, res) => {
    const user = await User.findById(req.params.id);
    res.json(user);
}
userCtrl.getUserByToken = async(req, res) => {
    const payload = await jwt.verify(req.params.token, 'grupodssd2021');
    if (!payload) {
        return res.status(401).send('Unauhtorized Request');
    }
    const user = await User.findById(payload._id);
    res.json(user);
}

function validarPassword(valor) {
    if (/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,20}$/.test(valor)) {
        return true
    } else {
        return false
    }

}

function validarEmail(valor) {
    const patt = new RegExp(/^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/);
    if (patt.test(valor)) {
        return true
    } else {
        return false
    }
}
userCtrl.createUser = async(req, res) => {
    const { email, password } = req.body;
    if (!validarEmail(email)) return res.status(401).send('Email incorrecto');

    const userAux = await User.findOne({ email });
    if (userAux) return res.status(401).send('El email ya existe');

    if (!validarPassword(password)) return res.status(401).send('Contraseña Incorrecta. (Mínimo 6 caracteres, al menos 1 letra y 1 número)');
    const user = new User({
        email,
        password,
    });
  
    user.password = await user.encryptPassword(password);
    await user.save();
    const token = await jwt.sign({ _id: user._id }, 'grupodssd2021');
    res.status(200).json({
        token
        
    });
}

userCtrl.editUser = async(req, res) => {
    const { id } = req.params;
    
    if (req.body.user.email === "" || !validarEmail(req.body.user.email)) return res.status(401).send('Email incorrecto');
    
    user = await User.findById(id);
    user.email = req.body.user.email;

    if (req.body.oldPasswordTry != "") {
        const match = await user.matchPassword(req.body.oldPasswordTry);
        if (!match) return res.status(401).send('Contraseña actual incorrecta');
        if (!validarPassword(req.body.newPassword)) return res.status(401).send('Contraseña nueva incorrecta. (Mínimo 6 caracteres, al menos 1 letra y 1 número)');
        if (req.body.newPassword != req.body.newPasswordRepeated) return res.status(401).send('La contraseña nueva y la confirmacion no coinciden');
        user.password = await user.encryptPassword(req.body.newPassword);
    }
    user.save();
    res.json({ 'status': "true" });
}


userCtrl.iniciarSesion = async(req, res) => {
    const { email, password } = req.body;

    const user = await User.findOne({ email });
    if (!user) return res.status(401).send('El email o contraseña incorrectas');   
    const match = await user.matchPassword(password);
    if (!match) return res.status(401).send('El email o contraseña incorrectas');   

    const token = jwt.sign({ _id: user._id }, 'grupodssd2021');
    //res.cookie('token', token, {  httpOnly: true });
    res.status(200).json({
        token
    });
}

    

userCtrl.validateToken = async(req, res) => {
    if (req.params.token == ""){
        res.status(401);
    }
    //console.log(req.params)
    const payload = jwt.verify(req.params.token, 'grupodssd2021');
    //console.log(req.params)
    if (!payload) {
        res.status(401);
    }
    return res.status(200);
}

module.exports = userCtrl;