const form = document.getElementById('nameForm');
const input = document.getElementById('nameInput');
const responseMsg = document.getElementById('responseMsg');
const namesList = document.getElementById('namesList');

async function loadNames() {
  try {
    const res = await fetch('/api/names');
    const data = await res.json();
    namesList.innerHTML = '';
    data.names.forEach(n => {
      const li = document.createElement('li');
      li.textContent = n;
      namesList.appendChild(li);
    });
  } catch (err) {
    console.error('Failed to load names', err);
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const name = input.value.trim();
  if (!name) return;

  try {
    const res = await fetch('/api/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name })
    });
    const data = await res.json();

    if (res.ok) {
      responseMsg.textContent = `Saved! Hello, ${data.name}.`;
      input.value = '';
      loadNames();
    } else {
      responseMsg.textContent = `Error: ${data.error || 'something went wrong'}`;
    }
  } catch (err) {
    responseMsg.textContent = 'Error contacting server.';
  }
});

// Load existing names on page load
loadNames();
