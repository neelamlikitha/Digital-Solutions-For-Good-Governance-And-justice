function sendMessage() {
    let input = document.getElementById("chatbox").value;
    let responseDiv = document.getElementById("chat-response");

    if (input.trim() === "") {
        responseDiv.innerHTML += "<p class='text-danger'>Please enter a question.</p>";
        return;
    }

    responseDiv.innerHTML += `<p class='user-message'><strong>You:</strong> ${input}</p>`;

    let response = "";
    if (input.toLowerCase().includes("hello")) {
        response = "Hello! How can I assist you today?";
    } else if (input.toLowerCase().includes("submit complaint")) {
        response = "To submit a complaint, go to the 'Complaint' page after logging in.";
    } else {
        response = "I'm not sure, but our team will get back to you soon!";
    }

    responseDiv.innerHTML += `<p class='bot-message'><strong>Bot:</strong> ${response}</p>`;
}
