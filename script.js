var reset = document.getElementById("reset");
reset.addEventListener("click", function () {
  window.location.reload();
});

(async () => {
  let AudioContext = window.AudioContext || window.webkitAudioContext;

  URL = window.URL || window.webkitURL;

  var gumStream; //stream from getUserMedia()
  var rec; //Recorder.js object
  var input; //MediaStreamAudioSourceNode we'll be recording

  // shim for AudioContext when it's not avb.

  var audioContext; //audio context to help us record

  var recordButton = document.getElementById("record");
  var stopButton = document.getElementById("stop");

  //add events to those 2 buttons
  recordButton.addEventListener("click", startRecording);
  stopButton.addEventListener("click", stopRecording);

  function startRecording() {
    console.log("recordButton clicked");

    /*
		Simple constraints object, for more advanced audio features see
		https://addpipe.com/blog/audio-constraints-getusermedia/
	*/

    var constraints = { audio: true, video: false };

    /*
    	Disable the record button until we get a success or fail from getUserMedia() 
	*/

    recordButton.disabled = true;
    stopButton.disabled = false;

    /*
    	We're using the standard promise based getUserMedia() 
    	https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
	*/

    navigator.mediaDevices
      .getUserMedia(constraints)
      .then(function (stream) {
        console.log(
          "getUserMedia() success, stream created, initializing Recorder.js ..."
        );

        document.querySelector("#msg").style.visibility = "visible";

        /*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device
		*/
        audioContext = new AudioContext();
        console.log("HELLO");
        //update the format

        /*  assign to gumStream for later use  */
        gumStream = stream;

        /* use the stream */
        input = audioContext.createMediaStreamSource(stream);
        console.log("HsdfhsdjELLO");

        /* 
			Create the Recorder object and configure to record mono sound (1 channel)
			Recording 2 channels  will double the file size
		*/
        rec = new Recorder(input, { numChannels: 1 });
        console.log("HsdfhsdjELLO");

        //start the recording process
        rec.record();

        console.log("Recording started");
      })
      .catch(function (err) {
        //enable the record button if getUserMedia() fails
        recordButton.disabled = false;
        stopButton.disabled = true;
      });
  }

  function stopRecording() {
    console.log("stopButton clicked");
    document.querySelector("#msg").style.visibility = "hidden";
    //disable the stop button, enable the record too allow for new recordings
    stopButton.disabled = true;
    recordButton.disabled = false;

    //reset button just in case the recording is stopped while paused

    //tell the recorder to stop the recording
    rec.stop();

    //stop microphone access
    gumStream.getAudioTracks()[0].stop();

    //create the wav blob and pass it on to createDownloadLink
    rec.exportWAV(createDownloadLink);
  }

  function createDownloadLink(blob) {
    const audioUrl = URL.createObjectURL(blob);
    temp_wav = blob;
    // console.log('BLOB ', blob);
    // console.log('URI ', audioUrl);
    document.querySelector("#audio").setAttribute("src", audioUrl);
  }

  // Upload File //
  var audioFile = document.getElementById("audio-file");

  var audio = document.getElementById("audio");

  var fileButton = document.getElementById("submit_audio");

  var successMsg = document.getElementById("success-msg");

  fileButton.addEventListener("click", async function () {
    successMsg.classList.add("hidden");
    console.log(audio.src);
    console.log(audioFile.files);
    console.log(audio.src || audioFile.files);
  });
})();
