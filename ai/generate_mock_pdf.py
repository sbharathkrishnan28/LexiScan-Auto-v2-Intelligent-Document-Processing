from fpdf import FPDF
import datetime
import os


def generate_contract():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    today = datetime.date.today().strftime("%B %d, %Y")
    deadline = "December 31, 2026"

    lines = f"""
    CONFIDENTIAL NON-DISCLOSURE AND PROFESSIONAL SERVICES AGREEMENT

    This Agreement is entered into as of {today}, by and between:

    Party A: Nexora Technologies LLC, a Delaware corporation headquartered
             at 350 Fifth Avenue, New York, NY 10118.

    Party B: Aria Khan Consulting Group, located in Austin, Texas, USA,
             represented by Ms. Aria Khan, Principal Consultant.

    RECITALS

    WHEREAS, Nexora Technologies LLC requires specialized AI infrastructure
    services; and WHEREAS, Aria Khan Consulting Group has the expertise to
    deliver such services under the terms set forth herein:

    1. SCOPE OF WORK
    Aria Khan Consulting Group shall design and deploy a scalable NLP
    microservices architecture for Nexora Technologies LLC. The project
    shall be completed no later than {deadline}.

    2. PAYMENT TERMS
    Nexora Technologies LLC agrees to pay a total contract value of
    $248,750.00 USD, structured as follows:
    - Milestone 1 (Project Kickoff):  $75,000.00 due on June 1, 2026
    - Milestone 2 (Mid Delivery):    $98,750.00 due on September 15, 2026
    - Milestone 3 (Final Delivery):  $75,000.00 due upon acceptance
    Late payments shall accrue interest at 1.5% per month.

    3. PENALTY CLAUSE
    Should delivery be delayed beyond {deadline} due to contractor
    negligence, a penalty of $12,500.00 per month shall be deducted
    from outstanding payments.

    4. TERMINATION CLAUSE
    Either party may terminate this agreement with 30 days written notice.
    In the event of a material breach, Nexora Technologies LLC may
    terminate this contract immediately without prior notice and demand
    a refund of up to $50,000.00 for work not delivered.

    5. NON-DISCLOSURE
    Both parties agree to maintain strict confidentiality of all proprietary
    information, trade secrets, and source code exchanged under this
    Agreement for a period of five (5) years from the date of termination.

    6. GOVERNING LAW
    This Agreement shall be governed by the laws of the State of New York.
    Any disputes shall be resolved through arbitration in New York City.

    7. SIGNATORIES

    ___________________________       ___________________________
    Jordan Wells                      Aria Khan
    CEO, Nexora Technologies LLC      Principal, Aria Khan Consulting
    Date: {today}                     Date: {today}

    ___________________________
    Wei Zhang
    Legal Counsel, Nexora Technologies LLC
    """

    for line in lines.split("\n"):
        pdf.cell(0, 7, txt=line, ln=True, align="L")

    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "sample_contract.pdf"
    )
    pdf.output(out_path)
    print(f"Generated: {out_path}")


if __name__ == "__main__":
    generate_contract()
