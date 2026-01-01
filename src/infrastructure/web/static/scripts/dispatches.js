import { setupModals } from "./utils/components.js";
// set up modals

setupModals();

// dropdown menus (broker, driver, task location)
function setSelectValueWrapper (obj) {
    function setSelectValue () {
        const hiddenInput = this.parentNode.previousElementSibling
        hiddenInput.value = obj.id;

        const visibleInput = this.parentNode.previousElementSibling.previousElementSibling
        visibleInput.value = this.textContent;

        console.log("Visible:", visibleInput.value);
        console.log("Hidden:", hiddenInput.value);

        this.parentNode.classList.add('hidden');
        this.parentNode.innerHTML = '';
    }
    return setSelectValue;
}


function filterObjectsWrapper (objectArr) {
    function filterObjects () {
        const query = this.value.toLowerCase();
        const dropdownDiv = this.nextElementSibling.nextElementSibling;
        dropdownDiv.innerHTML = '';

        if (query === '') {
            dropdownDiv.classList.add('hidden');
            return;
        }

        const filteredLocs = objectArr.filter((obj) => 
            obj.name.toLowerCase().includes(query)
        );

        if (filteredLocs.length === 0) {
            dropdownDiv.classList.add('hidden');
            return;
        }

        filteredLocs.forEach((obj) => {
            const item = document.createElement('div');
            item.textContent = obj.name;
            item.addEventListener('click', setSelectValueWrapper(obj))
            dropdownDiv.appendChild(item);
            dropdownDiv.classList.remove('hidden');
        });
    }
    return filterObjects;
}

function validateInputWrapper (objectArr) {
    function validateInput () {
        setTimeout(() => {
            const hiddenInput = this.nextElementSibling;
            const dropdownDiv = this.nextElementSibling.nextElementSibling;
            const remainingValue = this.value.trim();

            if (!objectArr.some(obj => obj.name === remainingValue)) {
                console.log("BLUR FIRED");
                this.value = '';
                hiddenInput.value = '';

                if (objectArr === locations){
                    this.value = 'TBD';
                    hiddenInput.value = 'TBD';
                }

                dropdownDiv.classList.add("hidden");
                dropdownDiv.innerHTML = '';
            }
        }, 250);
    }

    return validateInput;
}


function dropdownValues (url, objectArr) {
    fetch(`/api/${url}`)
    .then((response) => {
        if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
        }
        return response.json();
    })
    .then((data) => {
        objectArr.push(...data);
    });

    const visibleInputs = document.querySelectorAll(`.form-${url.slice(0, -1)} > input`);
    for (const vi of visibleInputs) {
        vi.addEventListener('input', filterObjectsWrapper(objectArr));
        vi.addEventListener('blur', validateInputWrapper(objectArr));
    }
    
}

let brokers = [];
let drivers = [];
let locations = [];

dropdownValues('brokers', brokers);
dropdownValues('drivers', drivers);
dropdownValues('locations', locations);


// container addition/removal
const addContainerBtn = document.getElementById('add-container-btn');
let container_counter = 2;

function deleteContainerDiv () {
    const containersDiv = document.querySelector('.form-containers');
    const containerDropdowns = document.getElementsByClassName('container-dropdown');
    if (this.previousElementSibling.getAttribute('data-index') === '2') {
        if (containersDiv.children.length === 3) {
            for (const cd of containerDropdowns) {
                cd.querySelector(`option[data-index="2"]`).textContent = '';
            }
        }
        else if (containersDiv.children.length === 4) {
            const thirdInput = containersDiv.querySelector('input[data-index="3"]')
            thirdInput.setAttribute('data-index', '2');
            for (const cd of containerDropdowns) {
                cd.querySelector(`option[data-index="2"]`).textContent = thirdInput.value;
                cd.querySelector(`option[data-index="3"]`).textContent = '';
            }
        }
    } else if (this.previousElementSibling.getAttribute('data-index') === '3') {
        for (const cd of containerDropdowns) {
            cd.querySelector(`option[data-index="3"]`).textContent = '';
        }
    }

    this.parentNode.remove(); 
}

function addContainerDiv () {
    const containersDiv = document.querySelector('.form-containers');
    if (containersDiv.children.length === 4) {
        return;
    }
    const newContainerDiv = containersDiv.firstElementChild.cloneNode(true);
    const input = newContainerDiv.firstElementChild
    input.setAttribute('data-index', `${containersDiv.children.length}`);
    input.addEventListener('blur', autoFillDropdowns);

    const removeBtn = document.createElement('button');
    removeBtn.classList.add('remove-container-btn');
    removeBtn.textContent = 'X';
    removeBtn.addEventListener('click', deleteContainerDiv);
    newContainerDiv.appendChild(removeBtn);
    input.name = `container_${container_counter}`;
    input.value = '';
    container_counter++;

    containersDiv.insertBefore(newContainerDiv, this.parentNode);
}

addContainerBtn.addEventListener('click', addContainerDiv);




// container autofill

function autoFillDropdowns () {
    const containerDropdowns = document.getElementsByClassName('container-dropdown')
    for (const cd of containerDropdowns) {
        cd.querySelector(`option[data-index="${this.getAttribute('data-index')}"]`).textContent = this.value;
    }
}

const inputContainer = document.querySelector('.input-container');
inputContainer.addEventListener('blur', autoFillDropdowns);


// task addition/removal

const addBtn = document.getElementById('add-task-btn');
let task_counter = 3;

function deleteTask () {
    this.parentNode.remove();
}

function addNewTask () {
    const tasksDiv = document.querySelector('.form-tasks');

    if (tasksDiv.children.length === 9) return;

    const closeBtn = document.createElement('button');
    closeBtn.classList.add('form-task-remove');
    closeBtn.addEventListener('click', deleteTask)

    const newTask = tasksDiv.firstElementChild.cloneNode(true);

    const allInputFields = newTask.querySelectorAll('input[name], select');
    for (const input of allInputFields) {
        input.name = input.name.replace("1", task_counter.toString());
        input.value = '';
        if (input.name.startsWith('task_priority')) {
            input.value = input.value.replace("1", task_counter.toString());
        } else if (input.name.startsWith('task_location')) {
            input.value = 'TBD';
            input.addEventListener('input', filterObjectsWrapper(locations));
            input.addEventListener('blur', validateInputWrapper(locations));
        }
    }
    task_counter++;

    newTask.insertBefore(closeBtn, newTask.children[0]);
    tasksDiv.insertBefore(newTask, addBtn.parentNode);

    return;
}

addBtn.addEventListener('click', addNewTask);


// form submission

document.getElementById('dispatch-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    const plainObject = Object.fromEntries(formData.entries());
    console.log("Plain object", plainObject);

    let data = {
        "broker_ref": plainObject["broker_ref"],
        "driver_ref": plainObject["driver_ref"],
        "containers": [],
        "plan": '',
    };
    
    let task_map = {};
    Object.keys(plainObject).forEach((key) => {
        if (key.startsWith('container')) {
            data["containers"].push(plainObject[key]);
        } else if (key.startsWith('task')) {
            const idx = key[key.length - 1];

            if (!Object.hasOwn(task_map, idx)) {
                task_map[idx] = {"appointment": {"type": "", "start_time": "", "end_time": ""}};
            }

            const firstUnderscore = key.indexOf('_');
            const lastUnderscore = key.lastIndexOf('_');
            const keyName = key.substring(firstUnderscore + 1, lastUnderscore)

            if (["type", "start_time", "end_time"].includes(keyName)) {
                task_map[idx]["appointment"][keyName] = plainObject[key];
            } else {
                task_map[idx][keyName] = plainObject[key];
            }
        }
    });

    data["plan"] = Object.values(task_map);

    const jsonPayload = JSON.stringify(data);

    fetch('/dispatches/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: jsonPayload
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(errorData => {
                throw new Error(`Server Error: ${response.status} - ${errorData.message || 'Unknown error'}`);
            });
        }
        return response.json();
    })
    .then(result => {
        showToast(`Dispatch ${result.id} created successfully!`, 'success');
        this.reset();
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert(error.message || 'A network error occurred. Please try again.');
    })
    .finally(() => {
        document.getElementById("modal-submit").disabled = false;
    })
})
