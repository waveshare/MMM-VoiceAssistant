/* Magic Mirror
 * Module: MMM-GA
 *
 * By Gaurav
 *
 */
'use strict';

var NodeHelper = require("node_helper");
var net = require('net');

module.exports = NodeHelper.create({

  initVoiceAssistant: function(payload) {
    var self = this;
    this.server = net.createServer(function(connection) {
      console.log('client connected');
      connection.setEncoding("utf8");
      connection.on('end', function() {
        console.log('client close');
      });
      connection.on("data", function(data) {
        console.log(data);
		
	  if(data == 'ON_S1'){
		self.sendSocketNotification('LISTEN', data); 
	  }else if(data == 'ON_S2'){
		self.sendSocketNotification('CONNET', data);  
	  }else{
        self.sendSocketNotification('SHOW', data);
      }
	  });
      connection.pipe(connection);
    });
    
    this.server.listen(2001, function() { 
        console.log('server is listening');
    });
  },

  socketNotificationReceived: function(notification, payload) {
    if (notification === 'INIT') {
      console.log("now initializing assistant");
      this.initVoiceAssistant(payload);
    }
  }

});
