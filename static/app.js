const api = '/api/v1';
const headers = () => {
  const key = localStorage.getItem('apiKey') || '';
  return key ? {'X-API-Key': key} : {};
};

async function loadCollections() {
  const res = await fetch(`${api}/collections`, {headers: headers()});
  const data = await res.json();
  const sel = document.getElementById('collectionSelect');
  sel.innerHTML = '';
  data.forEach(c => {
    const o = document.createElement('option');
    o.value = c.id; o.textContent = c.name;
    sel.appendChild(o);
  });
  if (data[0]) loadDocs(data[0].id);
}

async function createCollection() {
  const name = document.getElementById('collectionName').value;
  await fetch(`${api}/collections`, {method:'POST', headers:{...headers(),'Content-Type':'application/json'}, body: JSON.stringify({name})});
  loadCollections();
}

async function loadDocs(collectionId) {
  const res = await fetch(`${api}/collections/${collectionId}/documents`, {headers: headers()});
  const docs = await res.json();
  document.getElementById('docList').innerHTML = docs.map(d => `<li>${d.filename}</li>`).join('');
}

async function uploadDoc() {
  const collectionId = document.getElementById('collectionSelect').value;
  const file = document.getElementById('docFile').files[0];
  if (!file) return;
  const form = new FormData();
  form.append('file', file);
  await fetch(`${api}/collections/${collectionId}/documents`, {method:'POST', headers: headers(), body: form});
  loadDocs(collectionId);
}

async function ask() {
  const collection_id = document.getElementById('collectionSelect').value;
  const query = document.getElementById('queryInput').value;
  const include_trace = document.getElementById('showTrace').checked;
  const res = await fetch(`${api}/react/query`, {
    method:'POST',
    headers:{...headers(),'Content-Type':'application/json'},
    body: JSON.stringify({collection_id, query, include_trace, top_k: 6}),
  });
  const data = await res.json();
  document.getElementById('chat').textContent = `${data.answer}\n\nCitations:\n${(data.citations||[]).map(c=>`${c.filename}#${c.chunk_index}`).join('\n')}`;
  document.getElementById('trace').textContent = include_trace ? JSON.stringify(data.trace || [], null, 2) : '';
}

document.getElementById('createCollectionBtn').onclick = createCollection;
document.getElementById('uploadBtn').onclick = uploadDoc;
document.getElementById('askBtn').onclick = ask;
document.getElementById('collectionSelect').onchange = e => loadDocs(e.target.value);

loadCollections();
