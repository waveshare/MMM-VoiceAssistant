/* Magic Mirror
 * Module: MMM-VoiceAssistant
 *
 * By MyMX1213
 *
 */

Module.register("MMM-VoiceAssistant", {
  // Module config defaults.
  defaults: {
    header: "Voice Asistant",
    maxWidth: "100%",
    updateDelay: 500
  },

  // Define start sequence.
  start: function() {
    Log.info('Starting module: Voice Assistant Now');
    var self = this;
    this.userQuery = "";
	this.assistantActive = false;
	this.processing = false;
    //this.sendSocketNotification('INIT', 'handshake');
    this.sendSocketNotification('INIT', self.config);
  },

  getDom: function() {
    Log.log('Updating DOM for GA');
    var wrapper = document.createElement("div");
	if(this.assistantActive == true){
		if (this.processing == true) {
			wrapper.innerHTML = "<img src='MMM-VoiceAssistant/assistant_inactive.png'></img><br/>" + this.userQuery;
		}else{
			wrapper.innerHTML = "<img src='MMM-VoiceAssistant/assistant_inactive.png'></img><br/>"
		}
	}else
	{
		wrapper.innerHTML = "<img src='MMM-VoiceAssistant/assistant_active.png'></img><br/>"
	}

    return wrapper;
  },

  socketNotificationReceived: function(notification, payload) {
    var self = this;
    delay = self.config.updateDelay;
    if (notification == 'SHOW') {
		this.assistantActive = true;
		this.processing = true;
		this.userQuery = payload;
    }else if(notification == 'CONNET'){
		this.assistantActive = true;
		this.processing = false;
	}else if(notification == 'LISTEN'){
		this.assistantActive = false;
		this.processing = false;		
	}
    this.updateDom(0);
  },
});
