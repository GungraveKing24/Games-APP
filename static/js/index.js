document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.js-steamCardWrapper'); // Seleccionar las tarjetas

    const currentyslide = localStorage.getItem('currentyslide');
    if (currentyslide) {
        window.scrollTo(0, parseInt(currentyslide));
    }
    
    window.addEventListener('scroll', () => {
        localStorage.setItem('currentyslide', scrollY);
    });

    cards.forEach(card => {
        card.addEventListener('click', () => {
            const gameId = card.dataset.id; // Obtener el ID del juego
            if (gameId) {
                window.location.href = `/details/${gameId}`; // Redirigir a la página de detalles
            }
        });
    });
});