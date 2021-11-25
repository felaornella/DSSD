
const estatutoCtrl = {};
var crypto = require('crypto');



estatutoCtrl.uploadEstatuto = async (req, res) => {
    if(!req.body.numeroExpediente || !req.body.file || req.body.file == "" || req.body.numeroExpediente==""){
        return res.status(400).send('Invalid File');
    }

    const hash = crypto.createHash('sha256').update(req.body.file + req.body.numeroExpediente).digest("base64");
    
    //console.log(hash)
    return res.status(200).json({
        'hash': hash
    })
}










estatutoCtrl.uploadEstatuto2 = async (req, res) => {
    const { numeroExpediente, size ,extension} = req.body;
    console.log(req.body)
    if(!numeroExpediente || !size || !extension){
        return res.status(400).send('Invalid Data');
    }

    const hash = crypto.createHash('sha256').update(numeroExpediente +size + extension).digest('base64');
    
    //console.log(hash)
    return res.status(200).json({
        'hash': hash
    })
}

/*
estatutoCtrl.uploadEstatuto3 = async (req, res, next) => {
    console.log(req.files)
    console.log(req.body.numeroExpediente)
    if(!req.files || !req.files.file || req.files.file.size == 0 || req.files.file.type==null){
        return res.status(400).send('Invalid File');
    }

    const hash = crypto.createHash('sha256').update(req.files.file.name + req.body.numeroExpediente).digest('base64');
    
    //console.log(hash)
    return res.status(200).json({
        'hash': hash
    })
}
*/

module.exports = estatutoCtrl;