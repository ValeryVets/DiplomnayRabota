const overlay = document.querySelector("#overlay");
const tutorName = document.querySelector("#tutor-name");
const tutorEmail = document.querySelector("#tutor-email");
const tutorage = document.querySelector("#tutor-age");
const tutorphone = document.querySelector("#tutor-phone");
const tutorsubject = document.querySelector("#tutor-subject");
const tutorqualification = document.querySelector("#tutor-qualification");
const tutor_bio = document.querySelector("#tutor-bio");

window.onload = function() {
    var checkboxes = document.querySelectorAll('.checkbox-div input[type="checkbox"]');
    var checkboxes1 = document.querySelectorAll('.checkbox input[type="checkbox"]');
    checkboxes1.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            var startTimeInput1 = this.parentNode.querySelector('.start');
            var endTimeInput1 = this.parentNode.querySelector('.duration');
            if (this.checked) {
                startTimeInput1.style.visibility = 'visible';
                endTimeInput1.style.visibility = 'visible';
            } else {
                startTimeInput1.style.visibility = 'hidden';
                endTimeInput1.style.visibility = 'hidden';
            }
        });
    });


    checkboxes.forEach(function(checkbox) {
        // restore checkbox state from localStorage when the page loads
        var storedCheckboxState = localStorage.getItem(`checkbox_state_${checkbox.value}`);
        if (storedCheckboxState) {
            checkbox.checked = storedCheckboxState === 'true';
        }

        var startTimeInput = checkbox.parentNode.querySelector('.start-time');
        var endTimeInput = checkbox.parentNode.querySelector('.end-time');

        // make time inputs visible or hidden based on checkbox state
        if (checkbox.checked) {
            startTimeInput.style.visibility = 'visible';
            endTimeInput.style.visibility = 'visible';
        } else {
            startTimeInput.style.visibility = 'hidden';
            endTimeInput.style.visibility = 'hidden';
        }

        // restore time inputs from localStorage when the page loads
        var storedStartTime = localStorage.getItem(`start_time_${checkbox.value}`);
        var storedEndTime = localStorage.getItem(`end_time_${checkbox.value}`);
        if (storedStartTime) {
            startTimeInput.value = storedStartTime;
        }
        if (storedEndTime) {
            endTimeInput.value = storedEndTime;
        }

        checkbox.addEventListener('change', function() {
            if (this.checked) {
                startTimeInput.style.visibility = 'visible';
                endTimeInput.style.visibility = 'visible';
            } else {
                startTimeInput.style.visibility = 'hidden';
                endTimeInput.style.visibility = 'hidden';
            }
            // save checkbox state to localStorage when it changes
            localStorage.setItem(`checkbox_state_${this.value}`, this.checked);
        });

        // save time inputs to localStorage when they change
        startTimeInput.addEventListener('input', function() {
            localStorage.setItem(`start_time_${checkbox.value}`, this.value);
        });
        endTimeInput.addEventListener('input', function() {
            localStorage.setItem(`end_time_${checkbox.value}`, this.value);
        });
    });
};


async function showCard(tutorId) {
    const response = await fetch(`/api/tutor/${tutorId}/`);
    const data = await response.json();

    document.getElementById('tutor_id').value = tutorId;

    tutorName.innerText = data.name;
    tutorEmail.innerText = data.email;
    tutorage.innerText = data.age;
    tutorphone.innerText = data.phone;
    tutorsubject.innerText = data.subject;
    tutorqualification.innerText = data.qualification;
    tutor_bio.innerText = data.bio;

    if (data.avatar) {
        avatar.src = data.avatar;
    } else {
        // установить источник на стандартное изображение, если у репетитора нет аватара
        avatar.src = "/static/avatar.jpg";
    }


    overlay.style.display = "block";
}



document.body.addEventListener('click', function(e) {
    if (e.target.id === 'card-container') {
        hideCard();
    }
});

function hideCard() {
    overlay.style.display = "none";
    enrollForm.style.display = "none";
    tutorContent.style.width = "500px";
}

var enrollButton = document.getElementById("enrollButton");
var enrollForm = document.getElementById("enrollForm");
var tutorContent = document.getElementById("tutorContent");

enrollButton.onclick = function(event) {
    event.stopPropagation();
    enrollForm.style.display = "flex";
    enrollForm.style.width = "50%";
    tutorContent.style.width = "50%";
}

