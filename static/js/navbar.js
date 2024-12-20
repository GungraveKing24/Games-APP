const body = document.querySelector("body"),
    sidebar = body.querySelector("nav"),
    toggle = body.querySelector(".toggle"),
    searchBtn = body.querySelector(".search-box"),
    modeSwitch = body.querySelector(".toggle-switch"),
    modeText = body.querySelector(".mode-text");

const mode = localStorage.getItem("mode");
const sidebarstatus = localStorage.getItem("sidebar");

if (mode === "dark") {
    body.classList.add("dark");
} else {
    body.classList.remove("dark");
}

if (sidebarstatus === "close") {
    sidebar.classList.add("close");
} else{
    sidebar.classList.remove("close");
}

function buscador(event) {
    event.preventDefault(); // Evita el comportamiento predeterminado de recargar la página
    const text = document.getElementById("searchtext").value; // Obtiene el valor del input
    if (text.trim()) { // Asegúrate de que no esté vacío
        const url = `/search?q=${encodeURIComponent(text)}`; // Construye la URL
        window.location.href = url; // Redirige al servidor
    }
    return false; // Evita el envío por defecto del formulario
}

toggle.addEventListener("click", () => {
    sidebar.classList.toggle("close");
    if (sidebar.classList.contains("close")) {
        localStorage.setItem("sidebar", "close");
    } else {
        localStorage.setItem("sidebar", "open");
    }
});

searchBtn.addEventListener("click", () => {
    sidebar.classList.remove("close");
});

modeSwitch.addEventListener("click", () => {
    body.classList.toggle("dark");

    if (body.classList.contains("dark")) {
        modeText.innerText = "Light mode";
        localStorage.setItem("mode", "dark");
        localStorage.setItem("darkmode", "True");
    } else {
        modeText.innerText = "Dark mode";
        localStorage.setItem("mode", "light");
        localStorage.setItem("darkmode", "False");
    }
});