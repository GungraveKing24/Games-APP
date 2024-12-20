const deletemodal = document.getElementById('ModalDelete');
const ModalDeleteCONFIRM = document.getElementById('ModalDeleteCONFIRM');
const ModalDeleteContent = document.getElementById('ModalDeleteContent');

async function getimages() {
    const url = '/GetImages';
    try {
        const response = await fetch(url, {
            method: 'GET',
        });
        if (response.ok) {
            const data = await response.json();
            if (data.results) {
                console.log(data.results);
                const modalContent = document.getElementById('ModalDeleteContent');
                modalContent.innerHTML = ''; // Limpiar contenido previo
                
                data.results.forEach(result => {
                    // Crear contenedor para cada imagen
                    const container = document.createElement('div');
                    container.className = 'flex items-center space-x-4 p-2';

                    // Crear elemento de imagen
                    const img = document.createElement('img');
                    img.src = result.path;
                    img.alt = result.name;
                    img.className = 'w-16 h-16 rounded border';

                    // Crear texto para el nombre
                    const name = document.createElement('span');
                    name.textContent = result.name;
                    name.className = 'text-gray-700 dark:text-gray-300';

                    // Crear botón con la ID de la imagen
                    const button = document.createElement('button');
                    button.textContent = 'Eliminar';
                    button.className = 'text-white bg-red-600 hover:bg-red-700 px-3 py-1 rounded';
                    button.dataset.id = result.id;

                    // Manejar clic en el botón para eliminar la imagen
                    button.addEventListener('click', async () => {
                        // Obtenemos el nombre de la imagen que estamos eliminando
                        console.log(`Eliminar imagen con nombre: ${result.name}`);

                        // Hacer la petición para eliminar la imagen
                        const response = await fetch(`/DeleteImage/${result.name}`, {
                            method: 'POST'
                        });

                        if (response.ok) {
                            // Eliminar la imagen del DOM
                            container.remove();
                            console.log(`Imagen ${result.name} eliminada exitosamente`);

                            // Llamar a getimages para actualizar la lista de imágenes
                            getimages();
                        } else {
                            console.error('Hubo un error al eliminar la imagen');
                        }
                    });

                    // Agregar elementos al contenedor
                    container.appendChild(img);
                    container.appendChild(name);
                    container.appendChild(button);

                    // Agregar contenedor al modal
                    modalContent.appendChild(container);
                });
            }
        } else {
            console.error('Error en la respuesta del servidor:', response.statusText);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

const toggleModalVisibility = (action) => {
    if (action === 'open') {
        deletemodal.classList.remove('hidden');
        getimages();
    } else if (action === 'close') {
        deletemodal.classList.add('hidden');
    }
};

document.getElementById('ModalDeleteBTN').addEventListener('click', () => toggleModalVisibility('open'));
document.getElementById('CloseModal').addEventListener('click', () => toggleModalVisibility('close'));
document.getElementById('ModalDeleteCANCEL').addEventListener('click', () => toggleModalVisibility('close'));
