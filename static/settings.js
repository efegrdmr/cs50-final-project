document.addEventListener('DOMContentLoaded', () => {
    habitScript();
    tabScript();
    passwordScript();
    emailScript();
    userNameScript();
    deleteAccountscript();
});

async function deleteAccountscript() {

    document.querySelector('#delete').addEventListener('click', () => {
        xhr = new XMLHttpRequest();
        xhr.open('DELETE', '/api/account', true);

        xhr.setRequestHeader('operation', 'delete_account');

        xhr.onload = () => {
            if (xhr.status == 200) {
                window.location.replace('/register')
            }
        };
        xhr.send();
    });
}

async function userNameScript() {
    const newUserName = document.querySelector('#new-user-name');

    document.querySelector('#change-user-name').addEventListener('click', () => {
        let xhr = new XMLHttpRequest();
        xhr.open('PUT', '/api/account', true);
        xhr.setRequestHeader('operation', 'change_user_name');
        xhr.setRequestHeader('new_user_name', encodeURIComponent(newUserName.value));

        xhr.onload = () => {
            if (xhr.status == 200) {
                bootsrapAlert('User name changed successfully', 'success');
                document.querySelector('#current-user').textContent = newUserName.value;
                newUserName.value = '';

            }
            else {
                bootsrapAlert(xhr.response, 'danger');
            }
        };
        
        xhr.send();
    });
}

async function emailScript() {
    const newEmail = document.querySelector('#new-email');

    document.querySelector('#change-email').addEventListener('click', () => {
        if (!(newEmail.value.includes('@') || newEmail.value.includes('.'))) {
            bootsrapAlert('thats not a proper email!', 'danger');
            return;
        }

        let xhr = new XMLHttpRequest();
        xhr.open('PUT', '/api/account', true);

        xhr.setRequestHeader('operation', 'change_email');
        xhr.setRequestHeader('new_email', encodeURIComponent(newEmail.value));

        xhr.onload = () => {
            if ( xhr.status == 200) {
                bootsrapAlert('Email changed successfully.', 'success');
                newEmail.value = '';
            }
            else {
                bootsrapAlert(xhr.response, 'danger');
                newEmail.value = '';
            }
        };
        xhr.send();
    });
}

async function passwordScript() {
    const newPassword = document.querySelector('#new-password');
    const confirmation = document.querySelector('#confirmation-password');
    
    document.querySelector('#change-password').addEventListener('click', () => {
        if (newPassword.value != confirmation.value) {
            bootsrapAlert("The password and Confirmation are not the same!", 'danger');
            return;
        }

        let xhr = new XMLHttpRequest();
        xhr.open('PUT', '/api/account', true);

        xhr.setRequestHeader('operation', 'change_password');
        xhr.setRequestHeader('new_password', newPassword.value);
        xhr.setRequestHeader('confirmation', confirmation.value);

        xhr.onload = () => {
            if (xhr.status == 200) {
                bootsrapAlert('Your password successfully changed.', 'success');
                newPassword.value = '';
                confirmation.value = '';
            }
            else {
                bootsrapAlert('Could not change your password!', 'danger');
            }
        };

        xhr.send()

    });


}

async function tabScript() {
    // make tabs functional
    const tabLinks = document.querySelectorAll('.list-group-item');
    const tabs = document.querySelectorAll('.tab-pane');
    document.querySelector('.list-group').addEventListener('click', (event) => {
        let target = event.target;
        if (target.matches('a')) {
            tabLinks.forEach((link) => {
                link.classList.remove('active');
            });
            target.classList.add('active');

            tabs.forEach((tab) => {
                tab.classList.remove('active', 'show');
            });
            let tab = document.getElementById(target.getAttribute('for'));
            tab.classList.add('active', 'show');
        }
    });
}

async function habitScript() {

    loadHabits();
    // new habit button
    document.querySelector('#new-habit').addEventListener('click', (event) => {
        newHabit();
    });

    // Update habits with enter key
    document.querySelector('#habit-table').addEventListener('keypress', (event) => {
        let target = event.target;
        if (event.keyCode == 13 && target.matches('input')) {
            updateHabit(target.getAttribute('id'), target.value);
        }
    });

    // delete habits
    document.querySelector('#habit-table').addEventListener('click', (event) => {
        target = event.target;
        if (target.matches('button')) {
            deleteHabit(target.getAttribute('id'));
        }
    });
}

function loadHabits() {
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/api/habits', true);

    xhr.onload = () => {
        if (xhr.status == 200) {
            let habits = JSON.parse(xhr.response);
            let habitTemplate = document.importNode(document.querySelector('#habit-template').content, true); 
            let habitTable = document.querySelector('#habit-table');
            habitTable.innerHTML = "";
            habits.forEach(habit => {
                habitRow = habitTemplate.cloneNode(true);
                habitRow.querySelector('input').setAttribute('value', habit[1]);
                habitRow.querySelector('input').setAttribute('id', habit[0]);
                habitRow.querySelector('button').setAttribute('id', habit[0]);
                habitTable.append(habitRow);
            });
        }
    };

    xhr.send();
}

function newHabit(habit = "") {
    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/habits', true);
    xhr.setRequestHeader('habit', encodeURIComponent(habit));

    xhr.onload = () => {
        if (xhr.status = 200) {
            loadHabits();
        }
    };

    xhr.send();
}

function updateHabit(id, habit) {
    let xhr = new XMLHttpRequest();
    xhr.open('PUT', '/api/habits', true);

    xhr.setRequestHeader('habit_id', id);
    xhr.setRequestHeader('habit', encodeURIComponent(habit));

    xhr.onload = () => {
        if (xhr.status = 200) {
            loadHabits();
        }
    };

    xhr.send()
}

function deleteHabit(id) {
    let xhr = new XMLHttpRequest();
    xhr.open('DELETE', '/api/habits', true);

    xhr.setRequestHeader('habit_id', id);

    xhr.onload = () => {
        if (xhr.status == 200) {
            loadHabits();
        }
    };

    xhr.send()
}

async function bootsrapAlert(alert, type, duration = 5000) {
    const alertContainer = document.querySelector('#alert-container');
    const alertElement = document.createElement('div');

    alertElement.classList.add('alert', 'mb-0', 'text-center', 'alert-'+type);
    alertElement.textContent = alert;
    alertContainer.appendChild(alertElement);

    setTimeout(() => {
        alertContainer.removeChild(alertContainer.firstElementChild);
    }, duration);

}