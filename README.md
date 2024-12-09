# 🚀 CV Parser & Email Generator Pro

Transform your CV processing and email outreach with our smart automation tool! ✨

## 📖 Project Overview of An automation tool :
CV Parser & Email Generator Pro is an innovative automation tool designed to streamline the recruitment process. With its advanced features, it helps users efficiently manage candidate information and enhance communication. This tool:
- Parses CVs in various formats
- Analyzes skills and experience
- Calculates match scores
- Generates personalized emails
- Provides detailed analytics

## 🎯 Quick Start Guide

### 1. 🛠️ Setup

1. Clone this awesome repository
2. Install the magic dependencies:
```bash
pip install python-dotenv openai langchain pandas
```

3. Create your `.env` file in the root directory:
```bash
OPENAI_API_KEY=your_api_key_here  # Keep it secret! 🤫
```

### 2. 📁 Prepare Your CVs

Drop all your CV files here ⬇️
```
app_parsing/data/resumes/
```

We love these formats: 📄 PDF, 📝 DOCX, ✍️ TXT

### 3. 🔄 Parse Those CVs!

1. Fire up your terminal and navigate to your project:
```bash
cd path/to/project(cv Parsing 2)
```

2. Run the parsing magic ✨:
```bash
python main.py
```

What happens next? 🎬
- All your CVs get processed automatically 🔄
- A beautiful `parsed_resumes.json` appears in `app_parsing/data/output/` 📊
- Watch the progress live in your console! 📺

After processing, the tool generates a `parsed_resumes.json` file containing structured information about each CV. The output includes key details such as:
- **Full Name**: Alex Ferro
- **Professional Title**: Talent Specialist
- **Contact Information**: Email, Phone
- **Professional Summary**: A brief executive summary of the candidate's experience.
- **Work Experience**: A list of previous job titles, companies, and employment periods.
- **Education**: Details about degrees obtained and institutions attended.

The tool provides valuable statistics and API usage details at the end too. Here’s an example of the statistics generated:

- **statistics**: cv total_processed: 1, processing_time: 0m 9s, format: .pdf
- **api_usage**: total_tokens:3814, total_cost_usd: 0.01, total_api_calls: 1

### 4. ✉️ Generate Amazing Emails

Time to create those personalized emails:
```bash
python -m app_parsing.services.email_personalizer
```

> 💡 Pro Tip: Currently using example job role data - perfect for testing! Real job descriptions coming soon.

### 5. 👀 View Your Generated Emails

Want to see those beautiful emails in readable format?
```bash
python -m app_parsing.scripts.view_email
```

Here’s an example of a formatted email generated for a candidate:

```
==================================================
Candidate: Sujit S Amin
Match Score: 84.0%
Matched Skills: 
--------------------
Subject: Exciting Senior Software Engineer opportunity at TechCorp😊
--------------------
Hey Sujit 👋

I'm impressed by your Python experience at University of Southern California. Your work in reducing scaling time on AWS is exactly what we need.

Let's discuss our Senior Software Engineer role.

Best regards,
[Recruiter Name]
==================================================
```

> 💡 Pro Tip: When selecting a file number to view, `1` corresponds to the most recent file, and the numbers represent older files as you go down the list.

### 6. 📊 Check Your Stats

For CV parsing insights:
```bash
python -m app_parsing.scripts.analysis
```

For email generation metrics:
```bash
python -m app_parsing.scripts.email_analysis
```

## 📂 Where Everything Lives

```
app_parsing/
├── data/
│   ├── resumes/        # 📥 Drop your CVs here
│   └── output/         
│       ├── emails/     # ✉️ Your generated emails
│       └── parsed_resumes.json
```

## 🎯 What You Get

- 🚀 Fast processing of all your CVs
- 📊 Detailed parsing results in JSON
- ✉️ Smart email generation
- 📈 Comprehensive analysis reports

## ⚠️ Troubleshooting

Running into issues? Let's fix that! 🛠️

1. 🔑 Double-check your OpenAI API key in .env
2. 📁 Make sure your CVs are in the right folder
3. 📄 Verify you're using supported file formats
4. 💻 Check those console messages for clues

## 🤝 Need Help?

Contact EASY DATA FACILE on easydatafacile@gmail.com for support! We're here to help! 🌟

## 💪 Features Coming Soon

- 📝 Real job description integration
- 🎨 More email templates
- Get rid of "John Doe" and other little issues

## License

This demo code is publicly available for demonstration purposes only. It is not intended for commercial use or redistribution without permission. Please contact EASY DATA FACILE at easydatafacile@gmail.com for any inquiries regarding its use.

---