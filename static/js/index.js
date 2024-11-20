document.addEventListener("DOMContentLoaded", function () {
    const jobListContainer = document.querySelector(".list-group");

    // Fetch jobs from the backend
    async function fetchJobs() {
        try {
            const response = await fetch('/fetch_jobs');


            // Check if the response is JSON
            if (!response.ok) {
                throw new Error('Failed to fetch jobs');
            }

            const contentType = response.headers.get("Content-Type");
            if (!contentType || !contentType.includes("application/json")) {
                throw new Error('Expected JSON, but got something else');
            }

            const jobs = await response.json();
            console.log(jobs);  // Log the jobs array to inspect it

            if (Array.isArray(jobs) && jobs.length > 0) {
                // Dynamically create list items for each job
                jobs.forEach(job => {
                    const listItem = document.createElement('li');
                    listItem.classList.add('list-group-item');

                    // Access the job properties from the array (job[0] = job_role, job[1] = company, job[2] = location)
                    listItem.innerHTML = `
                        <h5>${job[0]}</h5>  <!-- job_role -->
                        <p><strong>Company:</strong> ${job[1]}</p>  <!-- company -->
                        <p><strong>Location:</strong> ${job[2]}</p>  <!-- location -->
                    `;

                    // Append the list item to the job list container
                    jobListContainer.appendChild(listItem);
                });
            } else {
                jobListContainer.innerHTML = '<li class="list-group-item">No jobs available.</li>';
            }
        } catch (error) {
            console.error("Error fetching jobs:", error);
            jobListContainer.innerHTML = '<li class="list-group-item">Failed to load jobs. Please try again later.</li>';
        }
    }

    // Call the function to fetch jobs
    fetchJobs();
});