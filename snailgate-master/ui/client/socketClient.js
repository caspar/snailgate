import socket from 'socket.io-client'

const socketClient = socket('http://localhost:5000')

socketClient.on('connect', () => { console.log('connected') })
socketClient.on('disconnect', () => { console.log('disconnect') })

export default socketClient
