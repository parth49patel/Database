document.addEventListener('DOMContentLoaded', function () {
    // Fetch the user's skills and user info
    fetch('/get-user-skills', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data) || data.length < 2) {
                console.error('Invalid or empty data received:', data);
                return;
            }

            console.log(data);
            const skills = data[0];  // First array contains skills
            const userInfo = data[1];  // Second array contains user info
            const applications = data[2];  // Third array contains applications data

            // Display user info in the .right div
            const userInfoDiv = document.querySelector('.right');
            if (userInfo && userInfo.length > 0) {
                const [fname, lname] = userInfo[0];  // Assuming there's only one entry
                userInfoDiv.innerHTML = `<strong>Name</strong>: ${fname} ${lname}`;
            } else {
                userInfoDiv.innerHTML = 'User information not available';
            }

            // Select the skills table
            const skillsTable = document.querySelector('.skills-table');

            // Loop through the skills data and add rows to the table
            skills.forEach(skillArray => {
                if (Array.isArray(skillArray) && skillArray.length === 4) {
                    const row = document.createElement('tr');

                    // Create and append Skill Name cell
                    const skillNameCell = document.createElement('td');
                    skillNameCell.textContent = skillArray[1]; // Skill Name
                    row.appendChild(skillNameCell);

                    // Create and append Proficiency cell
                    const proficiencyCell = document.createElement('td');
                    proficiencyCell.textContent = skillArray[2]; // Proficiency
                    row.appendChild(proficiencyCell);

                    // Create and append Number of Years cell
                    const yearsCell = document.createElement('td');
                    yearsCell.textContent = skillArray[3]; // Years of Experience
                    row.appendChild(yearsCell);

                    // Append the row to the skills table
                    skillsTable.appendChild(row);
                } else {
                    console.warn('Unexpected skill format:', skillArray);
                }
            });

            // Create Application Tracker table
            const applicationTable = document.querySelector('#application-table tbody');
            if (!applicationTable) {
                console.error('Application table body not found');
                return;
            }

            applications.forEach(application => {
                if (Array.isArray(application) && application.length === 5) {
                    const row = document.createElement('tr');

                    // Create and append Job Title cell
                    const jobTitleCell = document.createElement('td');
                    jobTitleCell.textContent = application[1]; // Job Title
                    row.appendChild(jobTitleCell);

                    // Create and append Company Name cell
                    const companyCell = document.createElement('td');
                    companyCell.textContent = application[2]; // Company
                    row.appendChild(companyCell);

                    // Create and append Status dropdown
                    const statusCell = document.createElement('td');
                    const statusSelect = document.createElement('select');
                    const statuses = ['Applied', 'Rejected', 'Interview', 'Offer'];

                    statuses.forEach(status => {
                        const option = document.createElement('option');
                        option.value = status;
                        option.textContent = status;
                        if (status === application[3]) { // Set the initial value
                            option.selected = true;
                        }
                        statusSelect.appendChild(option);
                    });

                    statusCell.appendChild(statusSelect);
                    row.appendChild(statusCell);

                    // Create and append Date Applied cell
                    const dateAppliedCell = document.createElement('td');
                    const dateApplied = new Date(application[4]); // Assuming application[4] is the date
                    dateAppliedCell.textContent = dateApplied.toLocaleDateString(); // Format as date
                    row.appendChild(dateAppliedCell);

                    // Create and append Delete button
                    const deleteCell = document.createElement('td');
                    const deleteButton = document.createElement('button');
                    deleteButton.textContent = 'Delete';
                    deleteButton.classList.add('btn', 'btn-danger');
                    deleteButton.addEventListener('click', function () {
                        row.remove();
                    });
                    deleteCell.appendChild(deleteButton);
                    row.appendChild(deleteCell);

                    // Append the row to the application table
                    applicationTable.appendChild(row);
                } else {
                    console.warn('Unexpected application format:', application);
                }
            });

            // Process applications to group them by month
            const applicationsByMonth = {};
            applications.forEach(application => {
                const date = new Date(application[4]);
                const month = date.toLocaleString('default', { month: 'long' }); // e.g., "January"
                applicationsByMonth[month] = (applicationsByMonth[month] || 0) + 1;
            });

            // Call the generateApplicationsGraph function with the processed data
            generateApplicationsGraph(applicationsByMonth);

        })
        .catch(err => console.error('Error fetching user data:', err));
});

// Function to generate the applications graph
function generateApplicationsGraph(applicationsByMonth) {
    const months = Object.keys(applicationsByMonth);
    const counts = months.map(month => applicationsByMonth[month]);

    // Create the graph
    const ctx = document.getElementById('applications-over-time-chart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,  // The x-axis labels (Months)
            datasets: [{
                label: 'Applications Over Time',
                data: counts,  // The y-axis values (Number of applications)
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Number of Applications'
                    },
                    ticks: {
                        beginAtZero: true,  // Start the y-axis at 0
                        stepSize: 1,  // Increase by 1 on each tick
                        callback: function(value) {
                            return Math.floor(value);  // Ensure integers on the y-axis
                        }
                    }
                }
            }
        }
    });
}


document.getElementById('export-csv').addEventListener('click', function () {
    const table = document.getElementById('application-table');
    let csvContent = '';

    // Loop through table rows and columns
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        let rowData = [];
        cols.forEach(col => {
            rowData.push(col.textContent.trim());
        });
        csvContent += rowData.join(',') + '\n';  // Add a new line after each row
    });

    // Create a link and trigger the download
    const link = document.createElement('a');
    link.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent));
    link.setAttribute('download', 'applications.csv');
    link.click();
});

function logout() {
    fetch('/logout', {
        method: 'GET',
        credentials: 'same-origin' // Include cookies for session management
    })
    .then(response => {
        if (response.redirected) {
            // Redirect user to the login page
            window.location.href = response.url;
        } else {
            console.error('Logout failed.');
        }
    })
    .catch(error => {
        console.error('Error during logout:', error);
    });
}
