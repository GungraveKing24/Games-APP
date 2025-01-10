document.addEventListener("DOMContentLoaded", () => {
    const videoUpload = document.getElementById("videoUpload");
    const folderName = document.getElementById("folderName").value; // Variable del servidor Flask

    videoUpload.addEventListener("change", async (event) => {
        const file = event.target.files[0];

        if (file) {
            alert("Subiendo el archivo, por favor espera...");
            console.log(videoUpload, folderName);
            const formData = new FormData();
            formData.append("video", file);

            try {
                const response = await fetch(`/upload_video/${folderName}`, {
                    method: "POST",
                    body: formData,
                });

                if (response.ok) {
                    const result = await response.json();
                    alert("Archivo subido exitosamente.");
                    location.reload(); // Recargar la página para mostrar el video
                } else {
                    alert("Error al subir el archivo: " + response.statusText);
                }
            } catch (error) {
                console.error("Error en la subida:", error);
                alert("Hubo un problema al subir el archivo.");
            }
        }
    });
});
