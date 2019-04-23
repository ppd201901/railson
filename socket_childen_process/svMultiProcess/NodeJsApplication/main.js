var child = require('child_process').fork('child.js');

var server = require('net').createServer({pauseOnConnect: true}); 
//se não passar o pauseonconect, 
//o read do cliente trava a comunicação
//antes de passar para o childprocess

server.on('connection', function (socket) {
    socket.write("\nConectado!");
    child.send('socket', socket);
    server.getConnections(function (err, count) {
        console.log("Connections: " + count);
    });
});
server.listen(5000);