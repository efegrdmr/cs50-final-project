document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#btn-go').addEventListener('click', () => {
        let date =document.querySelector('#date').value;
        if (date != '') {
            window.location.replace('/diary/' + date);
        }
        
    });

    document.querySelector('#diaries').addEventListener('click', (event) => {
        let target = event.target;
        if (target.matches('.delete')) {
            deleteDiary(target.getAttribute('value'));
        }
        else {
            while (!target.matches('.col-auto') && !target.matches('.container') && !target.matches('row')) {
                
                target = target.parentNode;
            }
            if (target.matches('.col-auto')) {
                window.location.replace('/diary/' + target.getAttribute('value'));
            }
            
        }
    });
});

function deleteDiary(id) {
    let xhr = new XMLHttpRequest();
    xhr.open('DELETE', '/api/diary', true);

    xhr.setRequestHeader('diary_id', id);

    xhr.onload = () => {
        if (xhr.status == 200) {
            window.location.reload();
        }
    };

    xhr.send()
}