document.addEventListener('DOMContentLoaded', () => {
    const date = document.querySelector('#current-date');
    date.innerHTML = day;
  
    setTimeout(loadToDo, 100);

    // for new to-do button
    document.querySelector('#new-to-do').addEventListener('click', () => {
        newToDo('new to-do', 0);
    });

    // for buttons and text in to-do list with event delegation
    document.querySelector('#to-dos').addEventListener('click', (event) => {
        const target = event.target;
        // for check button
        if (target.matches('.check-btn')) {
            let id = target.getAttribute('value');
            let isCompleted = 1;
            if (target.classList.contains('btn-success')) {
                isCompleted = 0;
            }
            updateToDo(id, null, isCompleted);
            
        }

        // for delete button
        if (target.matches('.delete-btn')) {
            deleteToDo(target.getAttribute('value'));
        }

        
    });

    // save to-dos with enter key using event delegation
    document.querySelector('#to-dos').addEventListener('keypress', (event) => {
        let target = event.target;

        if (target.matches('.form-control') && event.keyCode == 13) {
            updateToDo(target.getAttribute('id'), target.value, null);
        }
    });

    // get diary data
    getDiary()

    // save diary data regularly
    setInterval(saveDiary, 5000);
    
    
});

function deleteToDo(id) {
    let xhr = new XMLHttpRequest();
    xhr.open('DELETE', '/api/to-do', true);
    xhr.setRequestHeader('to_do_id', id);

    xhr.onload = () => {
        if (xhr.status == 200) {
            loadToDo();
        }
    };

    xhr.send()
}

function newToDo(to_do, is_completed) {
    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/to-do', true);

    xhr.setRequestHeader('to_do', encodeURIComponent(to_do));
    xhr.setRequestHeader('is_completed', is_completed);
    xhr.setRequestHeader('day', day);

    xhr.onload= () => {
        if (xhr.status == 200) {
            loadToDo();
        }
    }

    xhr.send();

}

function loadToDo() {
    // Load to-do table
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/api/to-do', true);

    xhr.setRequestHeader('to_do_id', "*");
    xhr.setRequestHeader('day',day)

    xhr.onload = () => {
        if (xhr.status == 200) {
            const responseToDos = JSON.parse(xhr.response);
            const templateRow = document.importNode(document.querySelector('template').content, true);
            const toDos = document.querySelector('#to-dos');
            toDos.innerHTML = '';

            responseToDos.forEach(data => {
                row = templateRow.cloneNode(true);
                let toDo = row.querySelector('.form-control');
                let checkBtn = row.querySelector('.check-btn');
                let deleteBtn = row.querySelector('.delete-btn');

                deleteBtn.setAttribute('value',data[0]);
                checkBtn.setAttribute('value',data[0]);
                toDo.setAttribute('value', data[1]);
                toDo.setAttribute('id', data[0]);

                if (data[2]) {
                    checkBtn.classList.add('btn-success');
                }
                else {
                    checkBtn.classList.add('btn-light');
                }

                toDos.append(row);
            });
            
        }   
    };

    xhr.send()
}


function updateToDo(id, toDo, isCompleted) {
    let xhr = new XMLHttpRequest();
    xhr.open('PUT', '/api/to-do', true);
    xhr.setRequestHeader('to_do_id', id);

    if (toDo != null) {
        xhr.setRequestHeader('to_do', encodeURIComponent(toDo));
    }

    if (isCompleted != null) {
        xhr.setRequestHeader('is_completed', isCompleted);
    }
    
    xhr.onload = () => {
        if (xhr.status == 200) {
            loadToDo();
        }
    };
    
    xhr.send();
}   

function getDiary() {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/api/diary', true);

    xhr.setRequestHeader('day', day);

    xhr.onload = () => {
        if (xhr.status == 200) {
            document.querySelector('#diary').value = xhr.response;
        }
    };
    xhr.send()
}

function saveDiary() {
    
    let diary =document.querySelector('#diary').value;
    if (diary != "") {
        let xhr = new XMLHttpRequest();
        xhr.open('PUT', '/api/diary', true);

        xhr.setRequestHeader('day', day);
        xhr.setRequestHeader('diary', encodeURIComponent(diary));
        
            
        xhr.send();
    }
}
