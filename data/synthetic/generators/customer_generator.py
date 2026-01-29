"""Customer data generator for synthetic fintech data."""

import random
import uuid
from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd
from faker import Faker

# Initialize Faker with Spanish locale
fake = Faker(["es_ES", "es_MX"])
Faker.seed(42)
random.seed(42)


# =============================================================================
# Constants
# =============================================================================

DOCUMENT_TYPES = ["DNI", "NIE", "PASSPORT", "CIF"]
EMPLOYMENT_STATUS = ["EMPLOYED", "SELF_EMPLOYED", "UNEMPLOYED", "RETIRED", "STUDENT"]
INCOME_SOURCES = ["SALARY", "BUSINESS", "INVESTMENTS", "INHERITANCE", "PENSION", "OTHER"]
INCOME_DOCUMENTATION = ["PAYSLIP", "TAX_RETURN", "BANK_STATEMENT", "PENSION_CERTIFICATE"]
RISK_CATEGORIES = ["LOW", "MEDIUM", "HIGH", "PROHIBITED"]
PEP_CATEGORIES = ["NATIONAL", "FOREIGN", "INTL_ORG"]
ACCOUNT_TYPES = ["CURRENT", "SAVINGS", "BUSINESS"]
ACCOUNT_STATUS = ["ACTIVE", "DORMANT", "BLOCKED", "CLOSED"]
PRODUCTS = ["DEBIT_CARD", "CREDIT_CARD", "LOAN", "INVESTMENT", "INSURANCE"]
ONBOARDING_CHANNELS = ["APP", "WEB", "BRANCH", "REFERRAL"]
ADDRESS_VERIFICATION_METHODS = ["ONFIDO", "MANUAL", "UTILITY_BILL", "BANK_STATEMENT"]
LANGUAGES = ["es", "ca", "eu", "gl", "en"]

# Spanish provinces
SPANISH_PROVINCES = [
    "Madrid", "Barcelona", "Valencia", "Sevilla", "Zaragoza", "Málaga",
    "Murcia", "Palma", "Las Palmas", "Bilbao", "Alicante", "Córdoba",
    "Valladolid", "Vigo", "Gijón", "Granada", "Vitoria", "A Coruña",
    "San Sebastián", "Santander", "Pamplona", "Toledo", "Burgos", "Salamanca",
]

# High-risk sectors (CNAE codes)
HIGH_RISK_SECTORS = [
    "6810",  # Real estate
    "6420",  # Holding companies
    "6499",  # Other financial services
    "9200",  # Gambling
    "4778",  # Jewelry
    "9609",  # Personal services
]

NORMAL_SECTORS = [
    "6201",  # Software development
    "4711",  # Retail
    "5610",  # Restaurants
    "8559",  # Education
    "8610",  # Healthcare
    "4941",  # Transport
    "7022",  # Consulting
    "7311",  # Advertising
]

# Risk factors
RISK_FACTORS = [
    "High-risk sector",
    "High-risk country of origin",
    "PEP or PEP associate",
    "Complex ownership structure",
    "Cash-intensive business",
    "High transaction volumes",
    "International transfers to high-risk jurisdictions",
    "Inconsistent income documentation",
    "Previous alerts",
    "Short customer tenure",
]

# Countries by risk level
LOW_RISK_COUNTRIES = ["ESP", "FRA", "DEU", "ITA", "PRT", "NLD", "BEL", "AUT", "CHE", "GBR"]
MEDIUM_RISK_COUNTRIES = ["USA", "MEX", "BRA", "ARG", "COL", "CHL", "PER", "MAR", "TUR", "CHN"]
HIGH_RISK_COUNTRIES = ["RUS", "IRN", "PRK", "SYR", "VEN", "MMR", "AFG", "YEM", "LBY", "SDN"]


class CustomerGenerator:
    """Generator for synthetic customer data."""

    def __init__(self, seed: int = 42):
        """Initialize the generator with a seed for reproducibility."""
        self.seed = seed
        random.seed(seed)
        Faker.seed(seed)
        self.fake = Faker(["es_ES"])

    def generate_customer(self, customer_index: int) -> dict[str, Any]:
        """Generate a single customer record."""
        customer_id = str(uuid.uuid4())
        external_id = f"CUST-{100000 + customer_index:06d}"

        # Personal data
        gender = random.choice(["M", "F", None])
        if gender == "M":
            first_name = self.fake.first_name_male()
        elif gender == "F":
            first_name = self.fake.first_name_female()
        else:
            first_name = self.fake.first_name()

        last_name = self.fake.last_name()
        second_last_name = self.fake.last_name()

        # Determine nationality and risk
        nationality_roll = random.random()
        if nationality_roll < 0.85:
            nationality = "ESP"
            country_of_residence = "ESP"
        elif nationality_roll < 0.95:
            nationality = random.choice(MEDIUM_RISK_COUNTRIES)
            country_of_residence = random.choice(["ESP"] * 8 + MEDIUM_RISK_COUNTRIES[:2])
        else:
            nationality = random.choice(HIGH_RISK_COUNTRIES[:5])
            country_of_residence = "ESP"

        dob = self.fake.date_of_birth(minimum_age=18, maximum_age=85)
        age = (date.today() - dob).days // 365

        # Documents
        doc_type = "DNI" if nationality == "ESP" else random.choice(["NIE", "PASSPORT"])
        if doc_type == "DNI":
            doc_number = f"{random.randint(10000000, 99999999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
        elif doc_type == "NIE":
            doc_number = f"{'XYZ'[random.randint(0,2)]}{random.randint(1000000, 9999999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
        else:
            doc_number = f"{nationality[:2]}{random.randint(100000000, 999999999)}"

        doc_expiry = date.today() + timedelta(days=random.randint(30, 3650))

        # Contact
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(['gmail.com', 'hotmail.com', 'yahoo.es', 'outlook.com'])}"
        phone = f"+34{random.choice(['6', '7'])}{random.randint(10000000, 99999999)}"

        # Address
        province = random.choice(SPANISH_PROVINCES)
        city = province if random.random() < 0.5 else self.fake.city()

        # Employment
        if age < 22:
            employment_status = random.choice(["STUDENT", "EMPLOYED", "UNEMPLOYED"])
        elif age > 65:
            employment_status = random.choice(["RETIRED", "SELF_EMPLOYED"])
        else:
            employment_status = random.choices(
                EMPLOYMENT_STATUS,
                weights=[0.55, 0.20, 0.10, 0.05, 0.10],
            )[0]

        # Income based on employment
        if employment_status == "EMPLOYED":
            annual_income = random.randint(15000, 150000)
            income_source = "SALARY"
        elif employment_status == "SELF_EMPLOYED":
            annual_income = random.randint(20000, 300000)
            income_source = "BUSINESS"
        elif employment_status == "RETIRED":
            annual_income = random.randint(12000, 60000)
            income_source = "PENSION"
        elif employment_status == "STUDENT":
            annual_income = random.randint(0, 15000)
            income_source = random.choice(["OTHER", "SALARY"])
        else:
            annual_income = random.randint(0, 20000)
            income_source = "OTHER"

        # Employer sector
        is_high_risk_sector = random.random() < 0.1
        sector = random.choice(HIGH_RISK_SECTORS if is_high_risk_sector else NORMAL_SECTORS)

        # PEP status (1% chance)
        is_pep = random.random() < 0.01
        is_pep_associate = not is_pep and random.random() < 0.02
        pep_category = random.choice(PEP_CATEGORIES) if is_pep else None
        pep_position = self.fake.job() if is_pep else None

        # Calculate risk score
        risk_score = self._calculate_risk_score(
            nationality=nationality,
            is_pep=is_pep,
            is_pep_associate=is_pep_associate,
            is_high_risk_sector=is_high_risk_sector,
            annual_income=annual_income,
            age=age,
        )

        risk_category = self._get_risk_category(risk_score)
        risk_factors = self._get_risk_factors(
            nationality=nationality,
            is_pep=is_pep,
            is_pep_associate=is_pep_associate,
            is_high_risk_sector=is_high_risk_sector,
            risk_score=risk_score,
        )

        # Account
        account_id = f"ES{random.randint(10, 99)}{random.randint(1000, 9999)}{random.randint(10, 99)}{random.randint(1000000000, 9999999999)}"
        opening_date = self.fake.date_between(start_date="-10y", end_date="-30d")
        tenure_years = (date.today() - opening_date).days / 365

        account_status = "ACTIVE" if random.random() < 0.92 else random.choice(["DORMANT", "BLOCKED", "CLOSED"])
        products = random.sample(PRODUCTS, k=random.randint(1, 4))
        credit_limit = random.choice([0, 1000, 3000, 5000, 10000, 20000, 50000]) if "CREDIT_CARD" in products else 0

        # Expected behavior based on income
        expected_monthly_income = annual_income / 12
        expected_monthly_expenses = expected_monthly_income * random.uniform(0.5, 0.9)
        expected_transaction_count = random.randint(10, 100)
        expected_max_single_tx = annual_income * random.uniform(0.05, 0.2)

        # Onboarding
        onboarding_date = datetime.combine(opening_date, datetime.min.time())

        # Screening
        screening_result = "CLEAR" if random.random() < 0.97 else random.choice(["POTENTIAL_MATCH", "CONFIRMED_MATCH"])

        return {
            # Identification
            "customer_id": customer_id,
            "external_id": external_id,
            # Personal
            "first_name": first_name,
            "last_name": last_name,
            "second_last_name": second_last_name,
            "date_of_birth": dob,
            "nationality": nationality,
            "country_of_residence": country_of_residence,
            "gender": gender,
            # Documents
            "primary_document_type": doc_type,
            "primary_document_number": doc_number,
            "primary_document_expiry": doc_expiry,
            "primary_document_country": nationality,
            "secondary_document_type": None,
            "secondary_document_number": None,
            # Contact
            "email": email,
            "email_verified": random.random() < 0.95,
            "phone_country_code": "+34",
            "phone_number": phone,
            "phone_verified": random.random() < 0.90,
            "preferred_language": random.choices(LANGUAGES, weights=[0.85, 0.05, 0.03, 0.02, 0.05])[0],
            # Address
            "street_line_1": self.fake.street_address(),
            "street_line_2": self.fake.secondary_address() if random.random() < 0.3 else None,
            "city": city,
            "province": province,
            "postal_code": self.fake.postcode(),
            "address_country": country_of_residence,
            "address_type": "RESIDENTIAL",
            "address_verified": random.random() < 0.85,
            "address_verification_date": self.fake.date_between(start_date=opening_date, end_date="today") if random.random() < 0.85 else None,
            "address_verification_method": random.choice(ADDRESS_VERIFICATION_METHODS) if random.random() < 0.85 else None,
            # Employment
            "employment_status": employment_status,
            "employer_name": self.fake.company() if employment_status in ["EMPLOYED", "SELF_EMPLOYED"] else None,
            "employer_sector": sector if employment_status in ["EMPLOYED", "SELF_EMPLOYED"] else None,
            "job_title": self.fake.job() if employment_status == "EMPLOYED" else None,
            "employment_start_date": self.fake.date_between(start_date="-20y", end_date="-1y") if employment_status == "EMPLOYED" else None,
            "annual_income_declared": annual_income,
            "income_source": income_source,
            "income_documentation": random.choice(INCOME_DOCUMENTATION),
            # Risk profile
            "risk_score": risk_score,
            "risk_category": risk_category,
            "risk_factors": risk_factors,
            "last_risk_assessment": self.fake.date_time_between(start_date="-1y", end_date="now"),
            "next_review_date": date.today() + timedelta(days=random.randint(30, 365)),
            "edd_required": risk_category in ["HIGH", "PROHIBITED"] or is_pep,
            "edd_reason": "PEP" if is_pep else ("High risk score" if risk_category == "HIGH" else None),
            # PEP
            "is_pep": is_pep,
            "pep_category": pep_category,
            "pep_position": pep_position,
            "pep_country": nationality if is_pep else None,
            "pep_since": self.fake.date_between(start_date="-15y", end_date="-1y") if is_pep else None,
            "pep_until": None,
            "is_pep_associate": is_pep_associate,
            "pep_relationship": random.choice(["FAMILY", "CLOSE_ASSOCIATE"]) if is_pep_associate else None,
            "related_pep_id": None,
            # Screening
            "last_screening_date": self.fake.date_time_between(start_date="-30d", end_date="now"),
            "screening_result": screening_result,
            "sanction_lists_checked": ["UN", "EU", "OFAC", "UK_HMT"],
            "potential_matches": random.randint(0, 3) if screening_result == "POTENTIAL_MATCH" else 0,
            "false_positive_count": random.randint(0, 5),
            # Account
            "account_id": account_id,
            "account_type": random.choice(ACCOUNT_TYPES),
            "account_status": account_status,
            "opening_date": opening_date,
            "opening_channel": random.choice(ONBOARDING_CHANNELS),
            "products": products,
            "credit_limit": credit_limit,
            # Expected behavior
            "expected_monthly_income": expected_monthly_income,
            "expected_monthly_expenses": expected_monthly_expenses,
            "expected_transaction_count": expected_transaction_count,
            "expected_countries": ["ESP"] + (random.sample(LOW_RISK_COUNTRIES, k=random.randint(0, 3))),
            "expected_max_single_transaction": expected_max_single_tx,
            "business_relationship_purpose": "Personal banking" if random.random() < 0.8 else "Business operations",
            # Onboarding
            "onboarding_date": onboarding_date,
            "onboarding_channel": random.choice(ONBOARDING_CHANNELS),
            "onboarding_agent_id": f"AGENT-{random.randint(100, 999)}" if random.random() < 0.3 else None,
            "video_identification": random.random() < 0.7,
            "biometric_verification": random.random() < 0.8,
            "terms_accepted_version": f"v{random.randint(1, 5)}.{random.randint(0, 9)}",
            "privacy_policy_version": f"v{random.randint(1, 3)}.{random.randint(0, 9)}",
            "marketing_consent": random.random() < 0.4,
            # Metadata
            "created_at": onboarding_date,
            "updated_at": self.fake.date_time_between(start_date=onboarding_date, end_date="now"),
            "created_by": "SYSTEM",
            "last_modified_by": "SYSTEM",
            "data_quality_score": random.uniform(0.7, 1.0),
            "gdpr_consent_date": opening_date,
            "data_retention_until": opening_date + timedelta(days=3650),  # 10 years
        }

    def _calculate_risk_score(
        self,
        nationality: str,
        is_pep: bool,
        is_pep_associate: bool,
        is_high_risk_sector: bool,
        annual_income: int,
        age: int,
    ) -> int:
        """Calculate customer risk score (0-100)."""
        score = 20  # Base score

        # Nationality risk
        if nationality in HIGH_RISK_COUNTRIES:
            score += 30
        elif nationality in MEDIUM_RISK_COUNTRIES:
            score += 15

        # PEP risk
        if is_pep:
            score += 25
        elif is_pep_associate:
            score += 15

        # Sector risk
        if is_high_risk_sector:
            score += 15

        # Income risk (very high or very low)
        if annual_income > 200000:
            score += 10
        elif annual_income < 10000 and age > 25:
            score += 5

        # Add some randomness
        score += random.randint(-10, 10)

        return max(0, min(100, score))

    def _get_risk_category(self, score: int) -> str:
        """Get risk category from score."""
        if score >= 80:
            return "PROHIBITED"
        elif score >= 60:
            return "HIGH"
        elif score >= 35:
            return "MEDIUM"
        else:
            return "LOW"

    def _get_risk_factors(
        self,
        nationality: str,
        is_pep: bool,
        is_pep_associate: bool,
        is_high_risk_sector: bool,
        risk_score: int,
    ) -> list[str]:
        """Get list of risk factors."""
        factors = []

        if nationality in HIGH_RISK_COUNTRIES:
            factors.append("High-risk country of origin")
        if is_pep:
            factors.append("PEP or PEP associate")
        if is_pep_associate:
            factors.append("PEP associate")
        if is_high_risk_sector:
            factors.append("High-risk sector")
        if risk_score > 50:
            factors.append("Elevated risk score")

        return factors

    def generate_customers(self, count: int = 1000) -> pd.DataFrame:
        """Generate multiple customer records."""
        customers = [self.generate_customer(i) for i in range(count)]
        df = pd.DataFrame(customers)

        # Convert list columns to string for parquet compatibility
        list_columns = ["risk_factors", "sanction_lists_checked", "products", "expected_countries"]
        for col in list_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: ",".join(x) if isinstance(x, list) else x)

        return df
