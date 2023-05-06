const d = new Date();
let month = d.getMonth() > 10 ? d.getMonth() : '0' + d.getMonth();
let date = d.getDate() > 10 ? d.getDate() : '0' + d.getDate();
let day = d.getFullYear() + '-' + month + '-' + date;
window.location.replace('/diary/' + day);
