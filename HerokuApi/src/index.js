const express = require('express');
const app = express();





module.exports = app;

require('./database');

// settings
app.set('port', process.env.PORT || 3000)
// middlewares
app.use(express.json({limit: '50mb'}));
app.use(express.urlencoded({limit: '50mb'}));


const fs = require('fs');
// routes
app.get('/', (req, res) =>{
    return res.status(200).json("Todo ok")
})
app.use('/api/users', require('./routes/user.routes'));
app.use('/api/upload', require('./routes/estatutos.routes'));


app.listen(app.get('port'));
console.log('Server on port', app.get('port'));
