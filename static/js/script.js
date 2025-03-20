// document.addEventListener("DOMContentLoaded", () => {
//     const textInput = document.getElementById("text-input");
//     const speakButton = document.getElementById("speak-button");
//     const conversationOutput = document.getElementById("conversation-output");
//     const statusOutput = document.getElementById("status-output");
//     const stopSpeakingButton = document.getElementById("stop-speaking");

//     let isSpeaking = false;
//     let synth = window.speechSynthesis; // Speech synthesis instance
//     let utterance; // Current speech utterance


//     // Toggle Speak/Send Button
//     speakButton.addEventListener("click", async () => {
//         const userText = textInput.value.trim();
//         if (userText) {
//             conversationOutput.innerHTML += `<p><strong>You:</strong> ${userText}</p>`;
//             statusOutput.textContent = "Status: Sending message...";
            
//             try {
//                 // Send user message to Flask backend
//                 const response = await fetch("/chat", {
//                     method: "POST",
//                     headers: {
//                         "Content-Type": "application/json",
//                     },
//                     body: JSON.stringify({ message: userText }),
//                 });

//                 const data = await response.json();
//                 if (data.reply) {
//                     conversationOutput.innerHTML += `<p><strong>Assistant:</strong> ${data.reply}</p>`;
//                     statusOutput.textContent = "Status: Reply received";

//                     // Speak the assistant's response
//                     utterance = new SpeechSynthesisUtterance(data.reply);
//                     utterance.lang = "en-US";
//                     utterance.rate = 1; // Adjust speech rate if needed
//                     synth.speak(utterance);
//                 } else {
//                     conversationOutput.innerHTML += `<p><strong>Error:</strong> Failed to get a response.</p>`;
//                     statusOutput.textContent = "Status: Error occurred";
//                 }
//             } catch (error) {
//                 console.error("Error:", error);
//                 conversationOutput.innerHTML += `<p><strong>Error:</strong> Unable to connect to the server.</p>`;
//                 statusOutput.textContent = "Status: Network Error";
//             }
//         }
//         textInput.value = "";
//     });

//     // Send Message on Enter Key
//     textInput.addEventListener("keypress", (e) => {
//         if (e.key === "Enter" && isSpeaking) {
//             e.preventDefault();
//             speakButton.click();
//         }
//     });

//     // Stop Speaking Button
//     stopSpeakingButton.addEventListener("click", () => {
//         if (synth.speaking) {
//             synth.cancel(); // Stop current speech
//             statusOutput.textContent = "Status: Speech stopped";
//         }
//     });

//     // Additional Button Interactions
//     document.getElementById("start-listening").addEventListener("click", () => {
//         statusOutput.textContent = "Status: Listening...";
//     });

//     // document.getElementById("stop-speaking").addEventListener("click", () => {
//     //     statusOutput.textContent = "Status: Process Ended";
//     // });

//     document.getElementById("upload-file").addEventListener("click", () => {
//         statusOutput.textContent = "Status: Uploading PDF...";
//     });
// });





document.addEventListener("DOMContentLoaded", () => {
    const textInput = document.getElementById("text-input");
    const micButton = document.getElementById("mic-button");
    const sendButton = document.getElementById("send-button");
    const conversationOutput = document.getElementById("conversation-output");
    const conversationFrame = document.getElementById("conversational-frame");
    const statusOutput = document.getElementById("status-output");
    const voiceActions = document.getElementById("voice-actions");
    const voiceCancelButton = document.getElementById("voice-cancel-button");
    const voiceSendButton = document.getElementById("voice-send-button");
    const stopSpeakingButton = document.getElementById("stop-speaking");

    let synth = window.speechSynthesis; // Speech synthesis instance
    let audio = null;
    let utterance; // Current speech utterance
    let recognition; // Speech recognition instance (if supported)
    let voiceInput = ""; // Stores recognized voice input
    let isRecognizing = false;

    // Check for browser support of Speech Recognition
    if ("webkitSpeechRecognition" in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        recognition.onstart = () => {
            statusOutput.textContent = "Status: Listening...";
        };

        // recognition.onresult = (event) => {
        //     const transcript = event.results[0][0].transcript.trim();
        //     voiceInput = transcript;
        //     statusOutput.textContent = `Status: Recognized - "${voiceInput}"`;
        // };
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript.trim();
            voiceInput = transcript;
            statusOutput.textContent = `Status: Recognized - "${voiceInput}"`;
            
            // Enable send button only now
            voiceSendButton.disabled = false;
            recognition.stop();
        };

        recognition.onerror = (event) => {
            statusOutput.textContent = "Status: Error in recognition";
        };

        // recognition.onend = () => {
        //     statusOutput.textContent = "Status: Listening ended";
        // };
        recognition.onend = () => {
            isRecognizing = false;
            statusOutput.textContent = "Status: Listening ended";
        };
    } else {
        micButton.style.display = "none";
        console.warn("Speech Recognition not supported in this browser.");
    }

    // Send Message to ChatGPT
    async function sendMessage(message) {
        const filename = document.getElementById("filename").value;  // Get filename from hidden input
        conversationOutput.innerHTML += `<p><strong>You:</strong> ${message}</p>`;
        scrollToBottom();
        statusOutput.textContent = "Status: Sending message...";
    
        try {
            const response = await fetch(`/chat?filename=${filename}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message }),
            });
    
            const data = await response.json();
            if (data.reply) {
                conversationOutput.innerHTML += `<p><strong>Assistant:</strong> ${data.reply}</p>`;
                statusOutput.textContent = "Status: Reply received";
                scrollToBottom();
                playPollyAudio(data.reply);
            } else {
                conversationOutput.innerHTML += `<p><strong>Error:</strong> Failed to get a response.</p>`;
                statusOutput.textContent = "Status: Error occurred";
                scrollToBottom();
            }
        } catch (error) {
            console.error("Error:", error);
            conversationOutput.innerHTML += `<p><strong>Error:</strong> Unable to connect to the server.</p>`;
            statusOutput.textContent = "Status: Network Error";
            scrollToBottom();
        }
    }

    // Stop Speaking Button
    // stopSpeakingButton.addEventListener("click", () => {
    //     if (synth.speaking) {
    //         synth.cancel(); // Stop current speech
    //         statusOutput.textContent = "Status: Speech stopped";
    //     }
    // });

    stopSpeakingButton.addEventListener("click", () => {
        if (audio) {
            audio.pause();  // Stop playback
            audio.currentTime = 0;  // Reset to start
            statusOutput.textContent = "Status: Speech stopped";
        }
    });

    // Send Button Clicked
    sendButton.addEventListener("click", () => {
        const userText = textInput.value.trim();
        if (userText) {
            sendMessage(userText);
            textInput.value = "";
        }
    });

    // Press Enter to Send
    textInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            sendButton.click();
        }
    });

    // Start Listening with Mic
    micButton.addEventListener("click", () => {
        if (recognition) {
            voiceInput = "";
            recognition.start();
            micButton.style.display = "none";
            voiceActions.style.display = "flex";
            sendButton.style.display = "none";
        }
    });

    // Cancel Voice Input
    voiceCancelButton.addEventListener("click", () => {
        if (recognition) recognition.stop();
        micButton.style.display = "inline";
        voiceActions.style.display = "none";
        statusOutput.textContent = "Status: Voice input cancelled";
        voiceInput = ""; // Clear voice input
        sendButton.style.display = "flex";
    });

    // Send Voice Input
    voiceSendButton.addEventListener("click", () => {
        if (voiceInput) {
            sendMessage(voiceInput);
        }
        voiceInput = ""; // Clear after sending
        micButton.style.display = "inline";
        voiceActions.style.display = "none";
        sendButton.style.display = "flex";
    });

    // Trigger sendMessage(voiceInput) with Enter key during voice input
    document.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && voiceActions.style.display === "flex") {
            e.preventDefault();
            if (voiceInput) {
                sendMessage(voiceInput);
                voiceInput = "";
                micButton.style.display = "inline";
                voiceActions.style.display = "none";
            }
        }
    });

    function scrollToBottom() {
        console.log("Scrolling to bottom...");
        conversationFrame.scrollTop = conversationFrame.scrollHeight;
    }

    function playPollyAudio(text) {
        fetch("/synthesize", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        })
        .then(response => response.blob())
        .then(blob => {
            if (audio) {
                audio.pause(); // Stop any ongoing audio
                audio.currentTime = 0; // Reset playback position
            }
    
            const audioUrl = URL.createObjectURL(blob);
            audio = new Audio(audioUrl);
            audio.play();
    
            audio.onended = () => {
                statusOutput.textContent = "Status: Speech finished";
            };
        })
        .catch(error => console.error("Error:", error));
    }
    // Request microphone access

    document.getElementById('end-chat-button').addEventListener('click', function() {
        console.log("end conv clicked")
        const filename = document.getElementById('filename').value;
        if (filename) {
            window.location.href = `/questionnaire/${filename}`;
        } else {
            alert("Filename not found. Cannot proceed to questionnaire.");
        }
    });
});


