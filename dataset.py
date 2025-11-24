import pandas as pd

# Define the questions
questions = [
    "When was this rental agreement executed?",
    "Who is the owner?",
    "What is the permanent address of the owner?",
    "Who is the tenant?",
    "What is the rent?",
    "What is the complete permanent address of the tenant?",
    "Where is the property located?",
    "What are the terms and conditions for renting the property?",
    "When does the rent commence?",
    "What is the monthly rent amount?",
    "What does the rent exclude?",
    "How should the rent be paid?",
    "What is the monthly maintenance charge for?",
    "What are the Tenant's responsibilities regarding elevator and generator costs?",
    "What bills are the Tenant responsible for during the rental period?",
    "What is the amount of the security deposit?",
    "When should the security deposit be paid?",
    "Under what conditions will the security deposit be refunded?",
    "What repairs are the Tenant responsible for?",
    "Who is responsible for major repairs?",
    "Can the Tenant make structural alterations without permission?",
    "What rights does the Owner have regarding inspection of the premises?",
    "What rules and regulations must the Tenant comply with?",
    "Who is responsible for paying taxes and other fees related to the property?",
    "What obligation does the Owner have regarding claims against the Tenant?",
    "How can the Rent Agreement be terminated before the expiry of the tenancy period?",
    "What condition must the Tenant maintain the premises in?",
    "What happens if the Tenant fails to vacate the premises?",
    "What is the process for settling disputes?",
    "What is the requirement regarding registration of the Rent Agreement?",
    "What fittings and fixtures are included in the property?"
]

# Create a DataFrame with questions and labels
data = {"question": questions, "label": [0] * len(questions)}  # Assuming all questions have the same label (0 for example)
df = pd.DataFrame(data)

# Save the dataset to a CSV file
df.to_csv("rental_agreement_questions.csv", index=False)
