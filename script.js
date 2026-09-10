const button = document.getElementById("planButton");

button.addEventListener("click", async () => {

    const prompt = document.getElementById("prompt").value.trim();

    const accessibility =
        document.getElementById("accessibility").checked;

    const disruption =
        document.getElementById("disruption").value;

    const loading =
        document.getElementById("loading");

    const results =
        document.getElementById("results");

    const taskList =
        document.getElementById("taskList");

    const consoleOutput =
        document.getElementById("consoleOutput");


    if (!prompt) {
        alert("Please enter your campus mission.");
        return;
    }


    loading.classList.remove("hidden");
    results.classList.add("hidden");


    try {

        const response = await fetch("/api/mission", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                prompt: prompt,

                accessibility_mode: accessibility,

                disruption: disruption

            })

        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail || "Backend error"
            );

        }


        taskList.innerHTML = "";


        data.tasks.forEach((task, index) => {

            const div =
                document.createElement("div");

            div.className = "task";


            div.innerHTML = `

                <div class="task-number">
                    STEP ${index + 1}
                </div>

                <h3>
                    ${task.title}
                </h3>

                <p>
                    📍 ${task.location}
                </p>

                <div class="task-info">

                    <span>
                        ⏱️ ${task.duration} min
                    </span>

                    <span>
                        👥 Queue: ${task.queue} min
                    </span>

                    <span>
                        🕐 ${task.open} - ${task.close}
                    </span>

                </div>

                <p>
                    💡 ${task.instruction}
                </p>

            `;


            taskList.appendChild(div);

        });


        consoleOutput.textContent =
            data.console_output;


        results.classList.remove("hidden");


        results.scrollIntoView({
            behavior: "smooth"
        });


    } catch (error) {

        alert(
            "Unable to connect to CampusFlow AI backend.\n\n" +
            error.message
        );

    } finally {

        loading.classList.add("hidden");

    }

});
