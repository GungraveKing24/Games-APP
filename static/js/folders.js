async function fetchFolders() {
    const response = await fetch('/folders', { priority: 'high' });
    const folders = await response.json(); // Datos en formato JSON

    const gallery = document.getElementById("imageGallery");

    folders.forEach(folder => {
        const wrapper = document.createElement("div");
        wrapper.className = "bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-transform hover:scale-105";

        const link = document.createElement("a");
        link.href = `/folders/${encodeURIComponent(folder.name)}`;
        link.className = "block";

        const img = document.createElement("img");
        img.src = folder.thumbnail
            ? `/images/${encodeURIComponent(folder.name)}/${encodeURIComponent(folder.thumbnail)}`  // URL de la miniatura
            : "/static/noun-placeholder-image-261694.png";  // Imagen predeterminada
        img.alt = folder.name || "Carpeta sin nombre";
        img.className = "w-full h-40 object-cover";

        const title = document.createElement("div");
        title.className = "p-4";
        title.innerHTML = `<h2 class="text-lg font-semibold text-gray-800 dark:text-gray-200">${folder.name} (${folder.count}) </h2>`;

        // Ensamblar elementos
        link.appendChild(img);
        link.appendChild(title);
        wrapper.appendChild(link);
        gallery.appendChild(wrapper);
    });
}

fetchFolders();
