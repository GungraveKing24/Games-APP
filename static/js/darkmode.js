document.addEventListener("DOMContentLoaded", () => {
    const darkmode = localStorage.getItem("darkmode");

    if (darkmode === "True") {
        document.body.classList.add("dark");
    } else {
        document.body.classList.remove("dark");
    }
});