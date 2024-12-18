const body = document.querySelector("body"),
    sidebar = body.querySelector("nav"),
    toggle = body.querySelector(".toggle"),
    searchBtn = body.querySelector(".search-box"),
    modeSwitch = body.querySelector(".toggle-switch"),
    modeText = body.querySelector(".mode-text");

const mode = localStorage.getItem("mode");

if (mode === "dark") {
    body.classList.add("dark");
} else {
    body.classList.remove("dark");
}

toggle.addEventListener("click", () => {
    sidebar.classList.toggle("close");
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