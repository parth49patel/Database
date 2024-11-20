document.addEventListener("DOMContentLoaded", function () {
    const courseListContainer = document.querySelector(".course-list");

    // Fetch courses from the backend
    async function fetchCourses() {
        try {
            const response = await fetch('/fetch_courses');  // Endpoint to fetch courses

            // Check if the response is OK
            if (!response.ok) {
                throw new Error('Failed to fetch courses');
            }

            // Check if the response is JSON
            const contentType = response.headers.get("Content-Type");
            if (!contentType || !contentType.includes("application/json")) {
                throw new Error('Expected JSON, but got something else');
            }

            const courses = await response.json();
            console.log(courses);  // Log the courses array to inspect it

            if (Array.isArray(courses) && courses.length > 0) {
                // Dynamically create course items for each course
                courses.forEach(course => {
                    const courseItem = document.createElement('div');
                    courseItem.classList.add('course-item');

                    // Access the course properties from the array
                    courseItem.innerHTML = `
                        <h5>${course[1]}</h5> <!-- Course Name -->
                        <p><strong>Instructor:</strong> ${course[2]}</p> <!-- Instructor -->
                        <p><strong>Cost:</strong> $${course[3]}</p> <!-- Cost -->
                        <p><strong>Skills:</strong> ${course[5]}</p> <!-- Skill -->
                        <p><strong>Description:</strong> ${course[4]}</p> <!-- Description -->
                    `;

                    // Append the course item to the course list container
                    courseListContainer.appendChild(courseItem);
                });
            } else {
                courseListContainer.innerHTML = '<div class="course-item">No courses available.</div>';
            }
        } catch (error) {
            console.error("Error fetching courses:", error);
            courseListContainer.innerHTML = '<div class="course-item">Failed to load courses. Please try again later.</div>';
        }
    }

    // Call the function to fetch courses
    fetchCourses();
});
