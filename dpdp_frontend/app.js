// Simple client‑side logic for the DPDP Hotel Compliance PoC

document.addEventListener('DOMContentLoaded', () => {
  const consentForm = document.getElementById('consentForm');
  const formStatus = document.getElementById('formStatus');
  const evidenceList = document.getElementById('evidenceList');

  /**
   * Create an evidence entry and append it to the list.
   * In a real system this would be persisted in a database/ledger.
   * @param {string} guestName
   * @param {string} guestEmail
   */
  function addEvidenceEntry(guestName, guestEmail) {
    const timestamp = new Date().toISOString();
    const entry = document.createElement('li');
    entry.textContent = `${timestamp}: Consent recorded for ${guestName} (${guestEmail}).`;
    evidenceList.prepend(entry);
  }

  consentForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const guestName = document.getElementById('guestName').value.trim();
    const guestEmail = document.getElementById('guestEmail').value.trim();
    const checkbox = document.getElementById('consentCheckbox');

    if (!checkbox.checked) {
      formStatus.textContent = 'Error: You must provide consent.';
      formStatus.style.color = 'red';
      return;
    }

    // Simulate API call delay
    formStatus.textContent = 'Submitting…';
    formStatus.style.color = '#333';

    setTimeout(() => {
      // Simulate success response
      formStatus.textContent = 'Consent recorded successfully!';
      formStatus.style.color = 'green';
      addEvidenceEntry(guestName, guestEmail);
      consentForm.reset();
    }, 500);
  });
});
