async function processNormalTier1() {
    const symptoms = document.getElementById('normal-symptoms').value;
    const formData = new URLSearchParams();
    formData.append("symptoms", symptoms);
    const response = await fetch('/normal/process_tier1', {
        method: 'POST',
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData
    });
    const data = await response.json();
    if (data.symptoms) {
        document.getElementById('normal-tier1-section').classList.add('d-none');
        document.getElementById('normal-tier2-section').classList.remove('d-none');
        const form = document.getElementById('normal-tier2-form');
        form.innerHTML = '';
        Object.entries(data.tier2_questions).forEach(([symptom, questions]) => {
            const div = document.createElement('div');
            div.className = 'symptom-card';
            questions.forEach(question => {
                div.innerHTML += `
                    <div class="form-group">
                        <label>${question}</label>
                        <input type="text" class="form-control" name="${symptom}_detail" required>
                    </div>
                `;
            });
            form.appendChild(div);
        });
    }
}

async function processNormalTier2() {
    const form = document.getElementById('normal-tier2-form');
    const formData = new FormData(form);
    const response = await fetch('/normal/process_tier2', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    if (data.tier3_questions && Object.keys(data.tier3_questions).length > 0) {
        document.getElementById('normal-tier2-section').classList.add('d-none');
        document.getElementById('normal-tier3-section').classList.remove('d-none');
        const form3 = document.getElementById('normal-tier3-form');
        form3.innerHTML = '';
        Object.entries(data.tier3_questions).forEach(([trigger, questions]) => {
            questions.forEach(question => {
                const div = document.createElement('div');
                div.className = 'form-group';
                div.innerHTML = `
                    <label>${question}</label>
                    <input type="text" class="form-control" name="${trigger}" required>
                `;
                form3.appendChild(div);
            });
        });
    } else {
        getNormalDiagnosis();
    }
}

async function getNormalDiagnosis() {
    const response = await fetch('/normal/diagnose', { method: 'POST' });
    const data = await response.json();
    document.getElementById('normal-tier3-section').classList.add('d-none');
    document.getElementById('normal-results-section').classList.remove('d-none');
    const resultsDiv = document.getElementById('normal-diagnosis-results');
    resultsDiv.innerHTML = '';
    if (data.diagnoses) {
        data.diagnoses.forEach(dx => {
            const div = document.createElement('div');
            div.className = 'diagnosis-item';
            div.innerHTML = `
                <div>${dx.disease}</div>
                <div>
                    <div class="probability-bar" style="width: ${dx.probability}%"></div>
                    <small>${dx.probability}%</small>
                </div>
            `;
            resultsDiv.appendChild(div);
        });
        document.getElementById('normal-department-suggestion').innerHTML = `
            <div class="department-suggestion">
                <strong>Suggested Department:</strong> ${data.department}
            </div>
        `;
    } else {
        resultsDiv.innerHTML = `<div class="alert alert-warning">${data.message}</div>`;
    }
}

// ----- DCG MODE FUNCTIONS -----
async function processDcgTier1() {
    const symptoms = document.getElementById('dcg-symptoms').value;
    const formData = new URLSearchParams();
    formData.append("symptoms", symptoms);
    const response = await fetch('/dcg/process_tier1', {
        method: 'POST',
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData
    });
    const data = await response.json();
    if (data.symptoms) {
        document.getElementById('dcg-tier1-section').classList.add('d-none');
        document.getElementById('dcg-tier2-section').classList.remove('d-none');
        const form = document.getElementById('dcg-tier2-form');
        form.innerHTML = '';
        Object.entries(data.tier2_questions).forEach(([symptom, questions]) => {
            const div = document.createElement('div');
            div.className = 'symptom-card';
            questions.forEach(question => {
                div.innerHTML += `
                    <div class="form-group">
                        <label>${question}</label>
                        <input type="text" class="form-control" name="${symptom}_detail" required>
                    </div>
                `;
            });
            form.appendChild(div);
        });
    }
}

async function processDcgTier2() {
    const form = document.getElementById('dcg-tier2-form');
    const formData = new FormData(form);
    const response = await fetch('/dcg/process_tier2', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();
    if (data.tier3_questions && Object.keys(data.tier3_questions).length > 0) {
        document.getElementById('dcg-tier2-section').classList.add('d-none');
        document.getElementById('dcg-tier3-section').classList.remove('d-none');
        const form3 = document.getElementById('dcg-tier3-form');
        form3.innerHTML = '';
        Object.entries(data.tier3_questions).forEach(([trigger, questions]) => {
            questions.forEach(question => {
                const div = document.createElement('div');
                div.className = 'form-group';
                div.innerHTML = `
                    <label>${question}</label>
                    <input type="text" class="form-control" name="${trigger}" required>
                `;
                form3.appendChild(div);
            });
        });
    } else {
        getDcgDiagnosis();
    }
}

async function getDcgDiagnosis() {
    const response = await fetch('/dcg/diagnose', { method: 'POST' });
    const data = await response.json();
    document.getElementById('dcg-tier3-section').classList.add('d-none');
    document.getElementById('dcg-results-section').classList.remove('d-none');
    const resultsDiv = document.getElementById('dcg-diagnosis-results');
    resultsDiv.innerHTML = '';
    if (data.diagnoses) {
        data.diagnoses.forEach(dx => {
            const div = document.createElement('div');
            div.className = 'diagnosis-item';
            div.innerHTML = `
                <div>${dx.disease}</div>
                <div>
                    <div class="probability-bar" style="width: ${dx.probability}%"></div>
                    <small>${dx.probability}%</small>
                </div>
            `;
            resultsDiv.appendChild(div);
        });
        document.getElementById('dcg-department-suggestion').innerHTML = `
            <div class="department-suggestion">
                <strong>Suggested Department:</strong> ${data.department}
            </div>
        `;
    } else {
        resultsDiv.innerHTML = `<div class="alert alert-warning">${data.message}</div>`;
    }
}