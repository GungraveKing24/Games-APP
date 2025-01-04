const searchsteam = document.getElementById('name');
const resultslist = document.getElementById('buscadorresults');
const imagepreview = document.getElementById('imagePreview');
const uploadBtn = document.getElementById('uploadBtn');
const searchBtnimg = document.getElementById('searchBtn');


let uploadedImage = null; // Para almacenar la imagen subida
let selectedImages = []; // Array para almacenar las URLs de las imágenes del datagrid
let currentImageIndex = 0; // Índice de la imagen actual


// Evento para manejar la carga de imágenes
uploadBtn.addEventListener('click', () => {
    // Resetear las URLs seleccionadas al subir una imagen
    selectedImages = [];
    currentImageIndex = 0;

    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*';
    input.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            // Verificar el tamaño de la imagen antes de cargarla (por ejemplo, máximo 5MB)
            const maxFileSize = 5 * 1024 * 1024; // 5MB en bytes
            if (file.size > maxFileSize) {
                alert('El archivo es demasiado grande. El tamaño máximo permitido es 5MB.');
                return;
            }

            uploadedImage = file;
            selectedImages = []; // Eliminar cualquier imagen seleccionada
            currentImageIndex = 0;
            showImage(); // Mostrar la imagen subida
        }
    });
    input.click(); // Abrir el selector de archivos
});

searchBtnimg.addEventListener('click', () => {
    if (selectedImages.length > 1) {
        currentImageIndex = (currentImageIndex + 1) % selectedImages.length; // Ciclar entre las imágenes
        showImage();
    }
});

function showImage() {
    imagepreview.innerHTML = '';
    if (uploadedImage) {
        // Si hay una imagen subida, mostrarla
        const imageUrl = URL.createObjectURL(uploadedImage); // Usar el URL del objeto binario
        imagepreview.innerHTML = `<img src="${imageUrl}" alt="Image" class="w-full h-full object-cover">`;
    } else if (selectedImages.length > 0) {
        // Si hay una imagen seleccionada (URL), mostrarla
        const imageUrl = selectedImages[currentImageIndex]; // Usar la URL seleccionada
        imagepreview.innerHTML = `<img src="${imageUrl}" alt="Image" class="w-full h-full object-cover">`;
    }
}

// Evento para manejar la búsqueda y mostrar los resultados
searchsteam.addEventListener('input', async function () {
    const query = searchsteam.value.trim();
    if (query.length <= 3) {
        resultslist.innerHTML = '';
        resultslist.style.display = 'none';
        return;
    }

    const url = `/SteamGrid/${query}`;

    try {
        const response = await fetch(url);
        if (response.ok) {
            const data = await response.json();
            resultslist.innerHTML = '';

            if (data.results && data.results.length > 0) {
                resultslist.style.display = 'block';
                data.results.forEach(result => {
                    const li = document.createElement('li');
                    li.textContent = result.name;
                    li.className = 'cursor-pointer p-2 hover:bg-gray-200 dark:hover:bg-gray-600';
                    li.addEventListener('click', () => {
                        searchsteam.value = result.name;
                        resultslist.innerHTML = '';
                        resultslist.style.display = 'none';
                        fetch(`/steamGridID/${result.id}`)
                            .then(response => response.json())
                            .then(data => {
                                if (data.results) {
                                    selectedImages = data.results.map(grid => grid.url); // Guardar todas las URLs
                                    uploadedImage = null; // Eliminar cualquier imagen subida
                                    currentImageIndex = 0;
                                    showImage(); // Mostrar la imagen seleccionada
                                }
                            })
                            .catch(error => console.error('Error fetching game details:', error));
                    });
                    resultslist.appendChild(li);
                });
            } else {
                resultslist.style.display = 'none';
            }
        } else {
            console.error('Error:', response.status);
        }
    } catch (error) {
        console.error('Error fetching results:', error);
    }
});

// Ocultar la lista si el usuario hace clic fuera del campo de búsqueda
document.addEventListener('click', function (event) {
    if (!searchsteam.contains(event.target) && !resultslist.contains(event.target)) {
        resultslist.innerHTML = ''; // Limpiar la lista
        resultslist.style.display = 'none'; // Ocultar la lista
    }
});

check.addEventListener('change', () => {
    if (check.checked) {
        check.value = 'Si';
        console.log("SI")
    } else {
        check.value = 'No';
        console.log("NO")
    }
});

// Evento para manejar el envío del formulario
document.getElementById('gameForm').addEventListener('submit', async function (event) {
    event.preventDefault(); // Evita el envío predeterminado
    const formData = new FormData(this);

    if (check.value === 'Si') {
        formData.append('replaying', 'Si');
    } else {
        formData.append('replaying', 'No');
    }

    if (uploadedImage) {
        // Si hay una imagen subida, envíala
        formData.append('imgfile', uploadedImage);
        console.log("Imagen subida enviada.");
    } else if (selectedImages.length > 0) {
        // Si hay una URL seleccionada, envíala
        formData.append('imgurl', selectedImages[currentImageIndex]);
        console.log("Imagen seleccionada enviada.");
    }
    
    try {
        const response = await fetch('/create', {
            method: 'POST',
            body: formData, // No incluir `Content-Type` explícitamente, se gestiona automáticamente
        });

        if (response.ok) {
            alert('Juego creado correctamente.');
        } else {
            alert('Error al crear el juego.');
        }
    } catch (error) {
        console.error('Error al crear el juego:', error);
    }
});