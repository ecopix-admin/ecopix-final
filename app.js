let myPeer;
let activeCall;
let timer;
let editIndex = -1;

// 1. Sabit ID və Peer Başlatma
const savedID = localStorage.getItem('az_id') || 'az-' + Math.floor(100000 + Math.random() * 900000);
localStorage.setItem('az_id', savedID);

function startPeer() {
    myPeer = new Peer(savedID);
    myPeer.on('open', id => document.getElementById('my-status').innerText = "ID: " + id);
    myPeer.on('call', call => {
        if(confirm("Gələn zəngi qəbul edirsiniz?")) {
            navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(stream => {
                document.getElementById('call-ui').style.display = 'flex';
                call.answer(stream);
                manageCall(call);
            });
        }
    });
}
startPeer();

// 2. Şəkil Yükləmə (Base64 formatında yaddaşa vurur)
function uploadMyImg(input) {
    if (input.files && input.files[0]) {
        let reader = new FileReader();
        reader.onload = e => {
            document.getElementById('my-p-img').src = e.target.result;
            localStorage.setItem('my_photo', e.target.result);
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// 3. Kontakt Sistemi (+ düyməsi və Redaktə)
function renderContacts() {
    const list = document.getElementById('contact-list');
    let contacts = JSON.parse(localStorage.getItem('az_contacts') || '[]');
    list.innerHTML = '';
    contacts.forEach((c, index) => {
        list.innerHTML += `
            <div class="card">
                <div class="avatar"><img src="${c.img || 'https://via.placeholder.com/50'}"></div>
                <div class="info"><b>${c.name}</b><br><small>${c.id}</small></div>
                <button class="btn-red" onclick="editContact(${index})"><i class="fas fa-edit"></i></button>
                <button class="btn-red" style="background:var(--accent)" onclick="initiateCall('${c.id}', '${c.name}')"><i class="fas fa-phone"></i></button>
            </div>`;
    });
}

function openModal() {
    editIndex = -1;
    document.getElementById('modal-title').innerText = "Kontakt Əlavə Et";
    document.getElementById('c-name').value = '';
    document.getElementById('c-id').value = '';
    document.getElementById('modal-bg').style.display = 'block';
    document.getElementById('modal').style.display = 'block';
}

function editContact(index) {
    let contacts = JSON.parse(localStorage.getItem('az_contacts') || '[]');
    editIndex = index;
    document.getElementById('modal-title').innerText = "Redaktə Et";
    document.getElementById('c-name').value = contacts[index].name;
    document.getElementById('c-id').value = contacts[index].id;
    document.getElementById('modal-bg').style.display = 'block';
    document.getElementById('modal').style.display = 'block';
}

function saveContact() {
    let name = document.getElementById('c-name').value;
    let id = document.getElementById('c-id').value;
    if(!name || !id) return alert("Bütün xanaları doldurun!");

    let contacts = JSON.parse(localStorage.getItem('az_contacts') || '[]');
    if(editIndex > -1) contacts[editIndex] = {name, id};
    else contacts.push({name, id, img: ''});

    localStorage.setItem('az_contacts', JSON.stringify(contacts));
    closeModal();
    renderContacts();
}

function closeModal() {
    document.getElementById('modal-bg').style.display = 'none';
    document.getElementById('modal').style.display = 'none';
}

// 4. Səhifə Keçidləri
function setPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
    event.currentTarget.classList.add('active');
}

window.onload = () => {
    renderContacts();
    let myPhoto = localStorage.getItem('my_photo');
    if(myPhoto) document.getElementById('my-p-img').src = myPhoto;
};
