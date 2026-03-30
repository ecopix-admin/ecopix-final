const conf = { 
    apiKey: "AIzaSyCtrVliO1bmdg7r0juWz-Yj2EaEGNsz2j8", 
    databaseURL: "https://ecopix-118c6-default-rtdb.europe-west1.firebasedatabase.app", 
    projectId: "ecopix-118c6" 
};
firebase.initializeApp(conf);
const db = firebase.database();

let nick = localStorage.getItem('v_nick') || "Qonaq_" + Math.floor(Math.random()*999);
let avatar = localStorage.getItem('v_avatar') || "https://cdn-icons-png.flaticon.com/512/149/149071.png";
let room = localStorage.getItem('v_room') || "Lobby";

document.getElementById('myAvatar').src = avatar;
document.getElementById('labelNick').innerText = nick;
