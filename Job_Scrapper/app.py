
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import re
from collections import Counter

app = Flask(__name__)

def extract_jobs():
    with open('jobs.html', 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        job_blocks = soup.find_all('div', class_='job-card')

        jobs = []
        for job in job_blocks:
            title = job.find('h3').text.strip()
            company = job.find('h4').text.strip()
            contact = job.find('p', class_='contact').text.strip()
            openings = job.find('p', class_='openings').text.strip()
            skills = job.find('ul')
            skill_list = [li.text for li in skills.find_all('li')] if skills else []

            jobs.append({
                'title': title,
                'company': company,
                'contact': contact,
                'openings': openings,
                'skills': skill_list
            })
        return jobs

def extract_keywords(text):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    return Counter(words)

@app.route('/', methods=['GET', 'POST'])
def index():
    matched_jobs = []
    if request.method == 'POST':
        resume = request.files['resume']
        resume_text = resume.read().decode('utf-8')
        resume_keywords = extract_keywords(resume_text)

        jobs = extract_jobs()

        for job in jobs:
            job_keywords = Counter([kw.lower() for kw in job['skills']])
            match_score = sum((resume_keywords & job_keywords).values())

            if match_score >= 2:
                matched_jobs.append(job)

    return render_template('index.html', jobs=matched_jobs)

if __name__ == '__main__':
    app.run(debug=True)
