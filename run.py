const Discord = require("discord.js");
const prefix = "";
const token = "";
const ytdl = require("ytdl-core");
const client = new Discord.Client();
const queue = new Map();
client.on("ready", () => {
  console.log("Ready!");
});
client.on("reconnecting", () => {
  console.log("Reconnecting!");
});
client.on("disconnect", () => {
  console.log("Disconnect!");
});
client.on("message", async message => {
  if (message.author.bot) return;
  if (!message.content.startsWith(prefix)) return;
  const serverQueue = queue.get(message.guild.id);
  if (message.content.startsWith(`${prefix}play`)) {
    execute(message, serverQueue);
    return;
  } else if (message.content.startsWith(`${prefix}skip`)) {
    skip(message, serverQueue);
    return;
  } else if (message.content.startsWith(`${prefix}stop`)) {
    stop(message, serverQueue);
    return;
  } else if (message.content.startsWith(`${prefix}loop`)) {
    loop(message, serverQueue);
    return;
  } else if (message.content.startsWith(`${prefix}queueloop`)) {
    queueloop(message, serverQueue);
    return;
  } else if (message.content.startsWith(`${prefix}help`)) {
    help(message);
    return;
  } else if (message.content.startsWith(`${prefix}nowplaying`)) {
    nowplaying(message, serverQueue);
    return;
  } else {
    message.channel.send("You need to enter a valid command!");
  }
});
async function execute(message, serverQueue) {
  var err = false;
  const args = message.content.split(" ");
  const voiceChannel = message.member.voice.channel;
  if (!voiceChannel) return message.channel.send("You need to be in a voice channel to play music!");
  const permissions = voiceChannel.permissionsFor(message.client.user);
  if (!permissions.has("CONNECT") || !permissions.has("SPEAK")) {
    return message.channel.send("I need the permissions to join and speak in your voice channel!");
  }
  const songInfo = await ytdl.getInfo(args[1]).catch(error => {
    err = true;
    message.channel.send("Oops, there seems to have been an error.\nPlease check the following points.\n*Is the URL correct?\n*Are you using a URL other than Youtube?\n*Is the URL shortened? \nIf the problem still persists, please wait a while and try again.")
  });
  if (err) return;
  const song = {
    title: songInfo.videoDetails.title,
    url: songInfo.videoDetails.video_url,
    totalsec: songInfo.videoDetails.lengthSeconds,
    viewcount: songInfo.videoDetails.viewCount,
    author: {
      name: songInfo.videoDetails.author.name,
      url: songInfo.videoDetails.author.channel_url,
      subscriber_count: songInfo.videoDetails.author.subscriber_count,
      verified: songInfo.videoDetails.author.verified
    },
    isPrivate: songInfo.videoDetails.isPrivate,
    likes: songInfo.videoDetails.likes,
    dislikes: songInfo.videoDetails.dislikes,
    thumbnail: songInfo.videoDetails.thumbnails[Object.keys(songInfo.videoDetails.thumbnails).length - 1].url
  };
  if (!serverQueue) {
    const queueContruct = {
      textChannel: message.channel,
      voiceChannel: voiceChannel,
      connection: null,
      songs: [],
      volume: 5,
      playing: true,
      loop: false,
      queueloop: false,
      starttimestamp: 0
    };
    queue.set(message.guild.id, queueContruct);
    queueContruct.songs.push(song);
    try {
      var connection = await voiceChannel.join();
      queueContruct.connection = connection;
      play(message.guild, queueContruct.songs[0]);
    } catch (err) {
      console.log(err);
      queue.delete(message.guild.id);
      return message.channel.send(err);
    }
  } else {
    serverQueue.songs.push(song);
    return message.channel.send(`${song.title} has been added to the queue!`);
  }
}

function skip(message, serverQueue) {
  if (!message.member.voice.channel) return message.channel.send("You have to be in a voice channel to stop the music!");
  if (!serverQueue) return message.channel.send("There is no song that I could skip!");
  serverQueue.connection.dispatcher.end();
}

function stop(message, serverQueue) {
  if (!message.member.voice.channel) return message.channel.send("You have to be in a voice channel to stop the music!");
  if (!serverQueue) return message.channel.send("There is no song that I could stop!");
  serverQueue.songs = [];
  serverQueue.connection.dispatcher.end();
  message.channel.send("See you! :wave:");
}
async function play(guild, song) {
  const serverQueue = queue.get(guild.id);
  if (!song) {
    serverQueue.voiceChannel.leave();
    queue.delete(guild.id);
    return;
  }
  const dispatcher = serverQueue.connection.play(ytdl(song.url)).on("finish", () => {
    finishsong = serverQueue.songs.shift();
    if (serverQueue.loop) {
      serverQueue.songs.unshift(finishsong);
    } else if (serverQueue.queueloop) {
      serverQueue.songs.push(finishsong);
    }
    play(guild, serverQueue.songs[0]);
  }).on("error", error => message.channel.send("Oops, there seems to have been an error.\nPlease check the following points.\n*Is the URL correct?\n*Are you using a URL other than Youtube?\n*Is the URL shortened? \nIf the problem still persists, please wait a while and try again."))
  dispatcher.setVolumeLogarithmic(serverQueue.volume / 5);
  serverQueue.textChannel.send(`Start playing: **${song.title}**`);
  serverQueue.starttimestamp = Date.now()
}

function loop(message, serverQueue) {
  if (!message.member.voice.channel) return message.channel.send("You have to be in a voice channel to stop the music!");
  if (!serverQueue) return message.channel.send("There is no song that I could loop!");
  if (serverQueue.loop) {
    serverQueue.loop = false;
    message.channel.send("Loop is Disabled!");
  } else {
    serverQueue.loop = true;
    message.channel.send("Loop is Enabled!");
  }
}

function queueloop(message, serverQueue) {
  if (!message.member.voice.channel) return message.channel.send("You have to be in a voice channel to stop the music!");
  if (!serverQueue) return message.channel.send("There is no song that I could loop!");
  if (serverQueue.queueloop) {
    serverQueue.queueloop = false;
    message.channel.send("Queue loop is Disabled!");
  } else {
    serverQueue.queueloop = true;
    message.channel.send("Queue loop is Enabled!");
  }
}

function help(message) {
  message.channel.send("🌸SakuraMusic🌸\n[Command List]\n\n¥play (URL) - Plays the song specified in the URL. Keyword search is not available.\n\n¥stop - Stops playing the song and exits the voice channel.\n\n¥skip - Switch to the next song in the queue if there is one.\n\n¥loop - Plays the current song in a loop. Run it again to cancel the loop setting.\n\n¥queueloop - plays through the songs in the queue, then returns to the beginning of the queue and continues playing. Run it again to cancel the loop setting.\n\n¥help - Brings up this message.\n\n¥nowplaying - Show the infomation about the music.");
}

function nowplaying(message, serverQueue) {
  if (!message.member.voice.channel) return message.channel.send("You have to be in a voice channel to stop the music!");
  if (!serverQueue) return message.channel.send("There is no song!");
  var timestamp = Date.now();
  var playsec = Math.floor(timestamp / 1000)- Math.floor(serverQueue.starttimestamp / 1000);
  
  function toHms(t) {
	var hms = "";
	var h = t / 3600 | 0;
	var m = t % 3600 / 60 | 0;
	var s = t % 60;

	if (h != 0) {
		hms = h + ":" + padZero(m) + ":" + padZero(s);
	} else if (m != 0) {
		hms = m + ":" + padZero(s);
	} else {
		hms = "0:" + padZero(s);
	}

	return hms;

	function padZero(v) {
		if (v < 10) {
			return "0" + v;
		} else {
			return v;
		}
	}
}
  
  var playtimetext = toHms(playsec);
  
  var musicplaytimetext = toHms(serverQueue.songs[0].totalsec)
  
  function getprogress(nowsec,allsec){
    var oneblockamount = allsec / 20;
    var nowblock = Math.floor(nowsec / oneblockamount);
    var playblock = "■";
    var noplayblock = "□";
    var progresstext = "[" + playblock.repeat(((nowblock - 1) < 0) ? "0" : nowblock - 1) + "☆" + noplayblock.repeat(20 - nowblock) + "]";
    return progresstext;
  }
  
  var nowprogresstext = getprogress(playsec, serverQueue.songs[0].totalsec);
  
  
  const embed = {
    "title": serverQueue.songs[0].title,
    "url": serverQueue.songs[0].url,
    "color": Math.floor(Math.random() * 16777214) + 1,
    "thumbnail": {
      "url": serverQueue.songs[0].thumbnail
    },
    "footer": {
      "text": "SakuraMusic"
    },
    "author": {
      "name": serverQueue.songs[0].author.name,
      "url": serverQueue.songs[0].author.url
    },
    "fields": [{
      "name": "channel",
      "value": serverQueue.songs[0].author.name
    }, {
      "name": "Play time",
      "value": playtimetext,
      "inline": true
    }, {
      "name": "Music length",
      "value": musicplaytimetext,
      "inline": true
    }, {
      "name": "Progress",
      "value": nowprogresstext
    }, {
      "name": "viewCount",
      "value": serverQueue.songs[0].viewcount,
      "inline": true
    }, {
      "name": "likes",
      "value": serverQueue.songs[0].likes,
      "inline": true
    }, {
      "name": "dislikes",
      "value": serverQueue.songs[0].dislikes,
      "inline": true
    }, {
      "name": "Channel:subscriber",
      "value": serverQueue.songs[0].author.subscriber_count,
      "inline": true
    }, {
      "name": "Channel:verified",
      "value": serverQueue.songs[0].author.verified,
      "inline": true
    }]
  };
  message.channel.send({
    embed
  });
}

client.on("voiceStateUpdate",  async (oldState, newState) => {
  if(oldState.channelID !=null && newState.channelID === null){
  var membercount = await client.channels.cache.find(channel => channel.id == oldState.channelID);
     if (membercount.members.size <= 1) {
            const serverQueue = queue.get(membercount.guild.id);
            serverQueue.songs = [];
            serverQueue.connection.dispatcher.end();
            serverQueue.textChannel.send("See you! :wave:\nHint: When the voice channel is empty, I will leave automatically.");
     }
   }
});
client.login(token);

