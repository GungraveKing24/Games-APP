const deletegame = document.getElementById('delete'), editgame = document.getElementById('edit');

deletegame.addEventListener('click', () => {
    
});

editgame.addEventListener('click', () => {
    idjuego = document.getElementById('id').value;
    window.location.href = `/edit/${idjuego}`;
});