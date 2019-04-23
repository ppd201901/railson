const {Client} = require('pg');
const msgpack = require('msgpack5')() // namespace our extensions
        //, a = new MyType(2, 'a')
        , encode = msgpack.encode
        , decode = msgpack.decode;


process.on('message', function (message, socket) {
    socket.on('end', function (a) {
        console.debug('finalizou');
    });
    socket.on('data', function (data) {
        //console.debug("Tamanho do pack: " + Buffer.byteLength(data, 'utf8') + " bytes");
        var msgDecode = decode(data)
        //console.debug("Tamanho original: " + Buffer.byteLength(JSON.stringify(msgDecode), 'utf8') + " bytes");

        var client = new Client({
            user: 'postgres',
            host: 'localhost',
            database: 'sd1',
            password: 'password',
            port: 5432})
        client.connect(function () {
            var sql = "insert into leitura (ds_leitura,in_processado,dt_leitura,id_dispositivo) values ($1,false,current_timestamp,1)";


            client.query(sql, [JSON.stringify(msgDecode)], (err, res) => {
                console.log(err ? err.stack : "sucesso")

                if (err) {
                    socket.write("\nErro", function () {
//                        socket.end("\nErro");
                        client.end()
                    });
                } else {
//                    socket.write("\nDados inseridos com sucesso.", function () {
                        socket.end("\nDados inseridos com sucesso.");
                        client.end()
//                    });
                }
            })
        })
    });

    socket.on('error', function (err) {
        console.debug(err);
    });
});