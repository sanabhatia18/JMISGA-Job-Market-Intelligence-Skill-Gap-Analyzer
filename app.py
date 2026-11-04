import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

df = pd.read_csv("india_job_market_2024-26.csv")

# --------------------------------------------------
# CORE SKILLS
# --------------------------------------------------

all_careers = df["Job_Title"].unique()

career_core_skills = {}

for career in all_careers:
    career_jobs = df[df["Job_Title"] == career]
    career_skills = []

    for skill_list in career_jobs["Skills_Required"]:
        for skill in skill_list.split(","):
            career_skills.append(skill.strip())

    career_skill_counts = pd.Series(career_skills).value_counts()
    top_skills = career_skill_counts.head(7)
    career_core_skills[career] = top_skills.index.tolist()


# --------------------------------------------------
# MARKET INFORMATION
# --------------------------------------------------

career_openings = df.groupby("Job_Title")["Openings"].sum()

average_salary = df.groupby("Job_Title")["Salary_LPA"].mean()

fresher_jobs = df[df["Experience_Level"] == "Fresher (0-1 yr)"]

fresher_openings = fresher_jobs.groupby("Job_Title")["Openings"].sum()

fresher_applicants = fresher_jobs.groupby("Job_Title")["Applicants"].sum()

fresher_competition = fresher_applicants / fresher_openings
fresher_competition = fresher_competition.round(2)


# --------------------------------------------------
# CAREER RECOMMENDATION + SKILL GAP
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        skills = request.form["skills"]

        user_skills = []

        for skill in skills.split(","):
            user_skills.append(skill.strip().lower())

        career_results = []

        for career in all_careers:
            required = career_core_skills[career]

            matched = []
            missing = []

            for skill in required:
                if skill.lower() in user_skills:
                    matched.append(skill)
                else:
                    missing.append(skill)

            match_percentage = (len(matched) / len(required)) * 100
            match_percentage = round(match_percentage, 2)

            career_results.append({
                "Career": career,
                "Match Percentage": match_percentage,
                "Total Openings": career_openings.get(career, 0),
                "Fresher Openings": fresher_openings.get(career, 0),
                "Average Salary": round(average_salary.get(career, 0), 2),
                "Fresher Competition Ratio": fresher_competition.get(career, 0),
                "Matched Skills": matched,
                "Missing Skills": missing
            })

        career_final_result = pd.DataFrame(career_results)

        career_final_result = career_final_result.sort_values(
            by="Match Percentage",
            ascending=False
        )

        top_5 = career_final_result.head(5)

        top_5_records = top_5.to_dict(orient="records")

        return render_template("index.html", results=top_5_records)

    return render_template("index.html")


# --------------------------------------------------
# WHAT-IF SIMULATOR
# --------------------------------------------------

@app.route("/whatif", methods=["POST"])
def what_if():

    skills = request.form["skills"]
    what_if_input = request.form["what_if_skills"]

    user_skills = []

    for skill in skills.split(","):
        user_skills.append(skill.strip().lower())

    what_if_skills = []

    for skill in what_if_input.split(","):
        what_if_skills.append(skill.strip().lower())

    simulated_skills = user_skills + what_if_skills

    simulation_results = []

    for career in all_careers:
        required = career_core_skills[career]

        current_matched = []

        for skill in required:
            if skill.lower() in user_skills:
                current_matched.append(skill)

        current_percentage = (len(current_matched) / len(required)) * 100
        current_percentage = round(current_percentage, 2)

        simulated_matched = []

        for skill in required:
            if skill.lower() in simulated_skills:
                simulated_matched.append(skill)

        simulated_percentage = (len(simulated_matched) / len(required)) * 100
        simulated_percentage = round(simulated_percentage, 2)

        simulation_results.append({
            "Career": career,
            "Current Match": current_percentage,
            "Simulated Match": simulated_percentage
        })

    simulation_df = pd.DataFrame(simulation_results)

    simulation_df = simulation_df.sort_values(
        by="Simulated Match",
        ascending=False
    )

    simulation_df = simulation_df.head(5)

    simulation_records = simulation_df.to_dict(orient="records")

    return render_template(
        "index.html",
        simulation_results=simulation_records
    )


# --------------------------------------------------
# CAREER COMPARISON
# --------------------------------------------------

@app.route("/compare", methods=["POST"])
def compare():

    career_1 = request.form["career_1"]
    career_2 = request.form["career_2"]
    skills = request.form["skills"]

    user_skills = []

    for skill in skills.split(","):
        user_skills.append(skill.strip().lower())

    comparison_results = []

    selected_careers = [career_1, career_2]

    for selected_career in selected_careers:

        for career in all_careers:

            if career.lower() == selected_career.lower():

                required = career_core_skills[career]

                matched = []
                missing = []

                for skill in required:
                    if skill.lower() in user_skills:
                        matched.append(skill)
                    else:
                        missing.append(skill)

                match_percentage = (len(matched) / len(required)) * 100
                match_percentage = round(match_percentage, 2)

                comparison_results.append({
                    "Career": career,
                    "Match Percentage": match_percentage,
                    "Total Openings": career_openings.get(career, 0),
                    "Fresher Openings": fresher_openings.get(career, 0),
                    "Average Salary": round(average_salary.get(career, 0), 2),
                    "Fresher Competition Ratio": fresher_competition.get(career, 0),
                    "Matched Skills": matched,
                    "Missing Skills": missing
                })

    return render_template(
        "index.html",
        comparison_results=comparison_results
    )


# --------------------------------------------------
# RUN APP
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)