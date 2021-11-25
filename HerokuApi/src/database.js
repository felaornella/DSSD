const mongoose = require('mongoose');

mongoose.connect('mongodb+srv://dssd:grupodssd2021@dssd.uzrcn.mongodb.net/Dssd?retryWrites=true&w=majority', {
        useNewUrlParser: true,
        useUnifiedTopology: true
    })
    .then(db => console.log('Database is connected'))
    .catch(err => console.log(err));