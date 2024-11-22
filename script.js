const path = "./Dataset/usa_jobs.csv";

set_of_work_type = new Set();
set_of_job_title = new Set();

d3.csv(path).then((data) => {
  data.map((d) => {
    const work_type = d["Work Type"];
    const job_title = d["Salary Range"];
    set_of_work_type.add(work_type);
    set_of_job_title.add(job_title);
  });
  const min_Salary = d3.min(data, (d) => d["Min Salary"]);
  const max_Salary = d3.max(data, (d) => d["Max Salary"]);
  const workTypeSelect = document.getElementById("workType");

  set_of_work_type.forEach((type) => {
    const option = document.createElement("option");
    option.value = type;
    option.text = type; 
    workTypeSelect.appendChild(option); 
  });
});

function showJobs() {
  const resume = document.getElementById("resume").value;
  const experience = document.getElementById("experience").value;
  const salary = document.getElementById("desiredSalary").value;
  const workType = document.getElementById("workType").value;
  console.log(experience + " and " + salary);
  const requestData = {
    resume: resume,
    experience: experience,
    salary: salary,
    workType: workType,
  };

 
  fetch("http://127.0.0.1:5000/api/jobs", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(requestData),
  })
    .then((response) => response.json()) 
    .then((data) => {
      const jobResultsDiv = document.getElementById("jobResults");
      jobResultsDiv.innerHTML = "";

      if (data.jobs && data.jobs.length>0) {
        const head = document.createElement("h2");
        head.textContent = "Your Top 10 Job Matches: ";
        jobResultsDiv.appendChild(head);
        jobs = data.jobs;
        let i = 1;
        jobs.forEach((job) => {
          const jobDiv = document.createElement("div");

          const jobTitle = document.createElement("h3");
          jobTitle.textContent = `${i}. ${job._source["Job Title"]}, ${job._source["Company"]}`;
          jobDiv.appendChild(jobTitle);

          const jobScore = document.createElement("h4");
          jobScore.textContent = `Match Score: ${job._source["similarity_score"]}%`;
          jobDiv.appendChild(jobScore);

          const jobSalary = document.createElement("p");
          jobSalary.textContent = `Salary: $${job._source["Min salary"]}k/yr - $${job._source["Max Salary"]}k/yr`;
          jobDiv.appendChild(jobSalary);

          const jobExperience = document.createElement("p");
          jobExperience.textContent = `Experience: ${job._source["Min Experience"]} - ${job._source["Max Experience"]} years`;
          jobDiv.appendChild(jobExperience);

          const jobBenefits = document.createElement("p");
          const benefits = job["_source"]["Benefits"];
          let trimmedBenefits = benefits.slice(2, -2);
          jobBenefits.textContent = `Benefits: ${trimmedBenefits}`;
          jobDiv.appendChild(jobBenefits);

          const jobPostingDate = document.createElement("p");
          jobPostingDate.textContent = `Posted On: ${job._source["Job Posting Date"]}`;
          jobDiv.appendChild(jobPostingDate);

          const requiredSkills = document.createElement("p");
          requiredSkills.textContent = `Required Skills: ${job._source["skills"]}`;
          jobDiv.appendChild(requiredSkills);

          const companySize = document.createElement("p");
          companySize.textContent = `Company Size: ${job._source["Company Size"]} people`;
          jobDiv.appendChild(companySize);

          const separator = document.createElement("hr");
          jobResultsDiv.appendChild(jobDiv);
          jobResultsDiv.appendChild(separator);
          i += 1;
        });
        window.scrollTo(0, window.innerHeight);
      } else {
        const head = document.createElement("h2");
        head.textContent = "Sorry, No Jobs Match Your Criteria and Resume!";
        jobResultsDiv.appendChild(head);
      }
    })
    .catch((error) => {
      alert("An error occurred while fetching the jobs.");
    });
}
