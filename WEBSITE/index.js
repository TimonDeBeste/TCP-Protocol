function addUserBubble(text) {
    const parentElement = document.getElementById("chat-window");
    const div = document.createElement("div");
    const p = document.createElement("p");

    p.textContent = text;
    div.appendChild(p);
    div.classList.add("bubble", "user")

    parentElement?.appendChild(div);

    parentElement.scrollTo(0, parentElement.scrollHeight)
}

function addChatterBubble(text) {
    const parentElement = document.getElementById("chat-window");
    const div = document.createElement("div");
    const p = document.createElement("p");

    p.textContent = text;
    div.appendChild(p);
    div.classList.add("bubble", "chatter")

    parentElement?.appendChild(div);

    parentElement.scrollTo(0, parentElement.scrollHeight)
}


const input = document.getElementById("message-input");

function sendMessage() {
    if (input.value != ""){
        addUserBubble(input.value);
    }
    input.value = ""
}