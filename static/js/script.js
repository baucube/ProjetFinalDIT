document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prediction-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            fetch('/predict_api', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                const resultCard = document.getElementById('result-card');
                const gradeDisplay = resultCard.querySelector('.grade-display');
                const gaugeBar = resultCard.querySelector('.gauge-bar');
                const interpretationText = resultCard.querySelector('.interpretation-text');

                gradeDisplay.textContent = result.prediction;
                
                // Mettre à jour la jauge (note sur 20)
                const percentage = (result.prediction / 20) * 100;
                gaugeBar.style.width = percentage + '%';

                interpretationText.textContent = result.interpretation;

                resultCard.style.display = 'block';
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Une erreur est survenue lors de la prédiction.');
            });
        });
    }
});