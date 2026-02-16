function addBubble(user, text) { //* param user must be either "user" or "chatter" 
    const parentElement = document.getElementById("chat-window");
    const div = document.createElement("div");
    const p = document.createElement("p");

    p.textContent = text;
    div.appendChild(p);
    div.classList.add("bubble", user);

    parentElement.appendChild(div);

    parentElement.scrollTo(0, parentElement.scrollHeight);
}


const input = document.getElementById("message-input");

input.addEventListener("keypress", function (event) { //* Check for enter usage when focused on input
    if (event.key === "Enter") {
        sendMessage();
    }
});

function sendMessage() {
    if (input.value !== "") {
        addBubble("user", input.value);
        //! API Send logic here
    }
    input.value = "";
}
