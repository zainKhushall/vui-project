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
    const statusOutput = document.getElementById("status-output");
    const voiceActions = document.getElementById("voice-actions");
    const voiceCancelButton = document.getElementById("voice-cancel-button");
    const voiceSendButton = document.getElementById("voice-send-button");
    const stopSpeakingButton = document.getElementById("stop-speaking");

    let synth = window.speechSynthesis; // Speech synthesis instance
    let utterance; // Current speech utterance
    let recognition; // Speech recognition instance (if supported)
    let voiceInput = ""; // Stores recognized voice input

    // Check for browser support of Speech Recognition
    if ("webkitSpeechRecognition" in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        recognition.onstart = () => {
            statusOutput.textContent = "Status: Listening...";
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript.trim();
            voiceInput = transcript;
            statusOutput.textContent = `Status: Recognized - "${voiceInput}"`;
        };

        recognition.onerror = (event) => {
            statusOutput.textContent = "Status: Error in recognition";
        };

        recognition.onend = () => {
            statusOutput.textContent = "Status: Listening ended";
        };
    } else {
        micButton.style.display = "none";
        console.warn("Speech Recognition not supported in this browser.");
    }

    // Send Message to ChatGPT
    async function sendMessage(message) {
        conversationOutput.innerHTML += `<p><strong>You:</strong> ${message}</p>`;
        statusOutput.textContent = "Status: Sending message...";

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message }),
            });

            const data = await response.json();
            if (data.write !="-1")
            {
                conversationOutput.innerHTML += `<p><strong>Assistant:</strong> ${data.write}</p>`;
                statusOutput.textContent = "Status: Reply received";

                // Speak the assistant's response
                utterance = new SpeechSynthesisUtterance(data.reply);
                utterance.lang = "en-US";
                synth.speak(utterance);
            }
            else if (data.reply) {
                conversationOutput.innerHTML += `<p><strong>Assistant:</strong> ${data.reply}</p>`;
                statusOutput.textContent = "Status: Reply received";

                // Speak the assistant's response
                utterance = new SpeechSynthesisUtterance(data.reply);
                utterance.lang = "en-US";
                synth.speak(utterance);
            } else {
                conversationOutput.innerHTML += `<p><strong>Error:</strong> Failed to get a response.</p>`;
                statusOutput.textContent = "Status: Error occurred";
            }
        } catch (error) {
            console.error("Error:", error);
            conversationOutput.innerHTML += `<p><strong>Error:</strong> Unable to connect to the server.</p>`;
            statusOutput.textContent = "Status: Network Error";
        }
    }

    // Stop Speaking Button
    stopSpeakingButton.addEventListener("click", () => {
        if (synth.speaking) {
            synth.cancel(); // Stop current speech
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
            recognition.start();
            micButton.style.display = "none";
            voiceActions.style.display = "flex";
        }
    });

    // Cancel Voice Input
    voiceCancelButton.addEventListener("click", () => {
        if (recognition) recognition.stop();
        micButton.style.display = "inline";
        voiceActions.style.display = "none";
        statusOutput.textContent = "Status: Voice input cancelled";
        voiceInput = ""; // Clear voice input
    });

    // Send Voice Input
    voiceSendButton.addEventListener("click", () => {
        if (voiceInput) {
            sendMessage(voiceInput);
            voiceInput = ""; // Clear after sending
        }
        micButton.style.display = "inline";
        voiceActions.style.display = "none";
    });
    conversationOutput.scrollTop = conversationOutput.scrollHeight;
    // Request microphone access
});


