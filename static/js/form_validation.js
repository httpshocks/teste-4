
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('measurementForm');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            const minimo = parseFloat(document.getElementById('minimo').value);
            const maximo = parseFloat(document.getElementById('maximo').value);
            
            // Get all measurement points
            const pontos = document.querySelectorAll('[id^="ponto"]');
            pontos.forEach(ponto => {
                const valor = parseFloat(ponto.value);
                if (valor < minimo || valor > maximo) {
                    ponto.classList.add('is-invalid');
                } else {
                    ponto.classList.remove('is-invalid');
                }
            });
            
            // Form will submit regardless of validation
            return true;
        });
    }

    // Add paste event listener to measurement points container
    const pointsContainer = document.getElementById('measurementPoints');
    pointsContainer.addEventListener('paste', function(e) {
        e.preventDefault();
        
        // Get pasted data
        const clipboardData = e.clipboardData || window.clipboardData;
        const pastedData = clipboardData.getData('text');
        
        // Split data into rows (assuming one value per line)
        const values = pastedData.split(/\r\n|\n|\r/)
                               .map(val => val.trim())
                               .filter(val => val !== '');
        
        // Clear existing points
        pointsContainer.innerHTML = '';
        
        // Create new points with pasted values
        values.forEach((value, index) => {
            const pointDiv = document.createElement('div');
            pointDiv.className = 'col-md-2 mb-3 measurement-point';
            pointDiv.innerHTML = `
                <label for="ponto${index + 1}" class="form-label">Ponto ${index + 1}</label>
                <input type="number" step="0.00001" class="form-control" id="ponto${index + 1}" name="ponto${index + 1}" value="${value}" required>
            `;
            pointsContainer.appendChild(pointDiv);
        });
    });

    // Add point button handler
    document.getElementById('addPoint').addEventListener('click', function() {
        const currentPoints = pointsContainer.getElementsByClassName('measurement-point').length;
        const newPoint = currentPoints + 1;

        const pointDiv = document.createElement('div');
        pointDiv.className = 'col-md-2 mb-3 measurement-point';
        pointDiv.innerHTML = `
            <label for="ponto${newPoint}" class="form-label">Ponto ${newPoint}</label>
            <input type="number" step="0.00001" class="form-control" id="ponto${newPoint}" name="ponto${newPoint}" required>
        `;

        pointsContainer.appendChild(pointDiv);
    });

    if (form) {
        form.addEventListener('submit', function(event) {
            // Remove required attribute from point inputs
            const pointInputs = document.querySelectorAll('[id^="ponto"]');
            pointInputs.forEach(input => {
                input.removeAttribute('required');
            });

            // Check measurement points and show warnings
            const minimo = parseFloat(document.getElementById('minimo').value);
            const maximo = parseFloat(document.getElementById('maximo').value);
            const points = document.getElementsByClassName('measurement-point');

            let outOfRange = false;
            for (let i = 0; i < points.length; i++) {
                const input = points[i].querySelector('input');
                const ponto = parseFloat(input.value);
                if (ponto < minimo || ponto > maximo) {
                    input.classList.add('is-invalid');
                    outOfRange = true;
                } else {
                    input.classList.remove('is-invalid');
                }
            }

            if (outOfRange) {
                if (confirm('Alguns pontos estão fora dos limites mínimo e máximo! Deseja continuar mesmo assim?')) {
                    return true;
                } else {
                    event.preventDefault();
                }
            }

            form.classList.add('was-validated');
        });

        // Real-time validation of min/max values
        document.getElementById('minimo').addEventListener('change', validateMinMax);
        document.getElementById('maximo').addEventListener('change', validateMinMax);
        document.getElementById('nominal').addEventListener('change', validateMinMax);
    }
});

function validateMinMax() {
    const minimo = parseFloat(document.getElementById('minimo').value);
    const maximo = parseFloat(document.getElementById('maximo').value);
    const nominal = parseFloat(document.getElementById('nominal').value);

    if (minimo >= maximo) {
        document.getElementById('minimo').setCustomValidity('O valor mínimo deve ser menor que o máximo');
        document.getElementById('maximo').setCustomValidity('O valor máximo deve ser maior que o mínimo');
    } else {
        document.getElementById('minimo').setCustomValidity('');
        document.getElementById('maximo').setCustomValidity('');
    }

    if (nominal < minimo || nominal > maximo) {
        document.getElementById('nominal').classList.add('is-invalid');
    } else {
        document.getElementById('nominal').classList.remove('is-invalid');
    }
    document.getElementById('nominal').setCustomValidity('');
}
