var crypto = require('crypto');
var remote = "http://127.0.0.1:3000/";
var async = require("async");
var CryptoJS = require("crypto-js");
var request = require('request');
var session = require('express-session');
function encrypt(text,key){
    return '' + CryptoJS.AES.encrypt(text,key);
}

function decrypt(cipher,key){
    var bytes  = CryptoJS.AES.decrypt(cipher, key);
    var plaintext = bytes.toString(CryptoJS.enc.Utf8);
    return plaintext;
}

function sha256(text) {
    return CryptoJS.SHA256("Message").toString(CryptoJS.enc.Base64);
}

var session;
module.exports = function(app) {
  app.get('/', function (req, res) {
    res.render('index', { title: 'Welcome to BitEmrs !' });
  });
  app.get('/reg', function (req, res) {
    res.render('reg', { title: 'Regisit' });
  });
  app.post('/reg', function (req, res) {
  });
  app.get('/addrec', function (req, res) {
    res.render('addrec', { title: 'Add New Record' });
  });
  app.post('/addrec', function (req, res) {
      var userid= req.body.userid;
      var key = req.body.secret;
      var data =JSON.stringify(
                {   "_id": req.body.caseid,
                    "age": req.body.age,
                    "date": req.body.date,
                    "gender": req.body.gender,
                    "weight": req.body.weight,
                    "symptom": req.body.symptom,
                    "note": req.body.note
                } );
      console.log("yuan data:"+data);
      var encrypted = encrypt(data,key);
      var send_data = {id:userid,encrypted:encrypted} 
      console.log("encrypt:"+encrypted);
      request.post({url:remote+"append/",form:send_data},function(err,httpResp,body){
      res.redirect('/');
      });

  });

  app.get('/queryrec', function (req, res) {
    res.render('queryrec', { title: 'Query Record' });
  });
  app.post('/queryrec', function (req, res) {
    var userid= req.body.userid;
    var key = req.body.secret;
    req.session.id = userid;
    req.session.key = key;
    request(remote+"login/"+userid, function (error, response, body) {
      if (!error && response.statusCode == 200) {
        var bodyJson = JSON.parse(body);
        console.log(bodyJson);
        var entries = bodyJson.entries;
        console.log(entries);
        session = req.session;
        session.listrec = entries;
        res.redirect('/listrec');
      }
    });;
  });
  app.get('/listrec', function (req, res) {
    console.log(req.session);
    var post = req.session.listrec;
    //req.session.listrec = "";
    console.log(post);
    res.render('listrec', {
        title: 'List Record',
        posts: post,
      });
  });
  app.get('/selectrec',function (req, res) {
    res.render('selectrec', { title: 'Select Record' });
  });
  app.post('/selectrec', function (req, res) {
    var userid= req.body.userid;
    var key = req.body.secret;
    var entryhash = req.body.entryhash;
    /*req.session.id = userid;
    req.session.key = key;*/
   // req.session.entryhash = entryhash;
    request(remote+"query/"+userid+"/"+entryhash, function (error, response, body) {
      if (!error && response.statusCode == 200) {
        console.log("yuan data"+body);
        var bodyJson = JSON.parse(body);
        var data = bodyJson.result.data;
        var str = "";
        console.log("data" + data);
        for( var i = 0; i < data.length; i++){
          str = str + String.fromCharCode(data[i]);
        }   
        console.log(str);
        var decrypted = decrypt(str,key);
        var plaintext = JSON.parse(decrypted);
        console.log("decrypt: "+decrypted);
        session = req.session;
        session.inforec = plaintext;
        res.redirect('/inforec');
      }
    });;
    /*request(remote+"query/"+userid+"/"+entry, function (err,qRes,qBody) {
          var qbodyJson;
          try { 
              qbodyJson = JSON.parse(qBody);
              console.log(qbodyJson);
              if (qbodyJson.result) {
                      try {
                          var decrypted = decrypt(qbodyJson.result,key);
                          var plainText = JSON.parse(decrypted);
                          callback(null,plainText);
                      } catch(e) {
                          console.log(e);
                          callback(url+" Bad data decrypted: "+ decrypt(qbodyJson.encryptedData,Key),null);
                      }
                      } else {
                      callback(url+ " Entry not found: " + qBody,null);
                      }
          } catch(e) {
              console.log(e);
              callback(url+" Entry not found: "+ qBody,null);
          }
      });*/
  });
  app.get('/inforec', function (req, res) {
    console.log(req.session);
    var post = req.session.inforec;
    //req.session.listrec = "";
    /*console.log(post);
    res.send(post);*/
    res.render('inforec', {
        title: 'Record Information',
        //posts: post,
        id: post._id,
        gender: post.gender,
        age: post.age,
        weight: post.weight,
        date: post.date,
        symptom: post.symptom,
        note: post.note,
      });
  });

  app.get('/deleterec',function (req, res) {
    res.render('deleterec', { title: 'Delete Record' });
  });

  app.post('/deleterec', function (req, res) {
    var userid= req.body.userid;
    var entryhash = req.body.entryhash;
    request(remote+"delete/"+userid+"/"+entryhash, function (error, response, body) {
         res.redirect('/');
    });;
  });
};