"""Transaction data generator for synthetic fintech data."""

import random
import uuid
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from faker import Faker

fake = Faker(["es_ES"])
Faker.seed(42)
random.seed(42)


# =============================================================================
# Constants
# =============================================================================

TRANSACTION_TYPES = ["TRANSFER", "PAYMENT", "WITHDRAWAL", "DEPOSIT", "FEE"]
DIRECTIONS = ["INBOUND", "OUTBOUND", "INTERNAL"]
CHANNELS = ["APP", "WEB", "ATM", "POS", "WIRE", "SEPA"]
PAYMENT_METHODS = ["INSTANT", "STANDARD", "CARD", "CASH"]
STATUSES = ["PENDING", "AUTHORIZED", "EXECUTED", "FAILED", "REVERSED"]

# Merchant Category Codes (MCC)
MCC_CATEGORIES = {
    "5411": {"name": "Grocery Stores", "risk": "low"},
    "5812": {"name": "Restaurants", "risk": "low"},
    "5541": {"name": "Gas Stations", "risk": "low"},
    "5311": {"name": "Department Stores", "risk": "low"},
    "5912": {"name": "Pharmacies", "risk": "low"},
    "5814": {"name": "Fast Food", "risk": "low"},
    "4111": {"name": "Transportation", "risk": "low"},
    "5732": {"name": "Electronics", "risk": "low"},
    "5691": {"name": "Clothing Stores", "risk": "low"},
    "5999": {"name": "Misc Retail", "risk": "medium"},
    "6011": {"name": "ATM Withdrawal", "risk": "medium"},
    "6012": {"name": "Financial Institution", "risk": "medium"},
    "7995": {"name": "Gambling", "risk": "high"},
    "5944": {"name": "Jewelry", "risk": "high"},
    "6051": {"name": "Crypto Exchange", "risk": "high"},
    "4829": {"name": "Money Transfer", "risk": "high"},
    "6538": {"name": "Remittance", "risk": "high"},
}

# Common merchants in Spain
SPANISH_MERCHANTS = [
    "Mercadona", "Carrefour", "El Corte Inglés", "Lidl", "Aldi",
    "Decathlon", "Zara", "MediaMarkt", "Amazon", "Glovo",
    "Uber", "Cabify", "Repsol", "Cepsa", "BP",
    "Burger King", "McDonald's", "Telepizza", "Starbucks",
    "IKEA", "Leroy Merlin", "Primark", "H&M",
]

# Countries by risk for transfers
LOW_RISK_COUNTRIES = ["ESP", "FRA", "DEU", "ITA", "PRT", "NLD", "BEL", "AUT", "GBR"]
MEDIUM_RISK_COUNTRIES = ["USA", "MEX", "BRA", "ARG", "COL", "MAR", "TUR", "CHN"]
HIGH_RISK_COUNTRIES = ["RUS", "IRN", "VEN", "MMR", "AFG", "SYR", "PRK"]

# Device types
DEVICE_TYPES = ["IOS", "ANDROID", "WEB", "ATM"]

# Spanish cities with coordinates
SPANISH_CITIES = {
    "Madrid": (40.4168, -3.7038),
    "Barcelona": (41.3851, 2.1734),
    "Valencia": (39.4699, -0.3763),
    "Sevilla": (37.3891, -5.9845),
    "Bilbao": (43.2630, -2.9350),
    "Málaga": (36.7213, -4.4214),
    "Zaragoza": (41.6488, -0.8891),
}


class TransactionGenerator:
    """Generator for synthetic transaction data."""

    def __init__(self, seed: int = 42):
        """Initialize the generator."""
        self.seed = seed
        random.seed(seed)
        Faker.seed(seed)
        self.fake = Faker(["es_ES"])

    def generate_transaction(
        self,
        customer_id: str,
        account_iban: str,
        customer_name: str,
        expected_monthly_expenses: float,
        expected_countries: list[str],
        risk_category: str,
        is_pep: bool,
        transaction_index: int,
    ) -> dict[str, Any]:
        """Generate a single transaction record."""
        transaction_id = str(uuid.uuid4())

        # Transaction timing
        executed_at = self.fake.date_time_between(start_date="-90d", end_date="now")
        initiated_at = executed_at - timedelta(minutes=random.randint(0, 30))
        authorized_at = initiated_at + timedelta(seconds=random.randint(1, 60))
        settled_at = executed_at + timedelta(hours=random.randint(0, 48))

        # Transaction type and direction
        tx_type = random.choices(
            TRANSACTION_TYPES,
            weights=[0.35, 0.30, 0.15, 0.15, 0.05],
        )[0]

        if tx_type == "DEPOSIT":
            direction = "INBOUND"
        elif tx_type == "WITHDRAWAL":
            direction = "OUTBOUND"
        elif tx_type == "FEE":
            direction = "OUTBOUND"
        else:
            direction = random.choice(["INBOUND", "OUTBOUND", "INTERNAL"])

        # Channel based on transaction type
        if tx_type == "WITHDRAWAL":
            channel = "ATM"
        elif tx_type == "PAYMENT":
            channel = random.choices(CHANNELS, weights=[0.3, 0.2, 0.0, 0.4, 0.0, 0.1])[0]
        else:
            channel = random.choices(CHANNELS, weights=[0.3, 0.2, 0.05, 0.1, 0.15, 0.2])[0]

        # Amount (based on customer's expected expenses)
        base_amount = expected_monthly_expenses / 30  # Daily average
        if tx_type == "PAYMENT":
            amount = round(random.uniform(5, base_amount * 3), 2)
        elif tx_type in ["TRANSFER", "DEPOSIT"]:
            amount = round(random.uniform(50, base_amount * 10), 2)
        elif tx_type == "WITHDRAWAL":
            amount = round(random.choice([20, 50, 100, 200, 300, 500]), 2)
        else:
            amount = round(random.uniform(1, 50), 2)

        currency = "EUR"

        # MCC and merchant
        mcc = random.choice(list(MCC_CATEGORIES.keys()))
        mcc_info = MCC_CATEGORIES[mcc]

        if tx_type == "PAYMENT" and channel == "POS":
            merchant_name = random.choice(SPANISH_MERCHANTS)
            merchant_country = "ESP"
        elif tx_type in ["TRANSFER", "DEPOSIT"]:
            merchant_name = None
            # Determine country based on expected countries and risk
            if random.random() < 0.85:
                merchant_country = "ESP"
            elif random.random() < 0.95:
                merchant_country = random.choice(expected_countries)
            else:
                merchant_country = random.choice(MEDIUM_RISK_COUNTRIES)
        else:
            merchant_name = None
            merchant_country = "ESP"

        # Beneficiary (for outbound transfers)
        if direction == "OUTBOUND" and tx_type == "TRANSFER":
            benef_country = merchant_country
            benef_iban = f"{benef_country[:2]}{random.randint(10, 99)}{random.randint(1000, 9999)}{random.randint(10, 99)}{random.randint(1000000000, 9999999999)}"
            benef_name = self.fake.name()
            benef_bank_bic = f"{random.choice(['BBVA', 'CAIXA', 'SANTAN', 'ING'])}ES{random.choice(['MM', 'BB', '2X'])}"
        else:
            benef_iban = None
            benef_name = None
            benef_country = None
            benef_bank_bic = None

        # Location
        city = random.choice(list(SPANISH_CITIES.keys()))
        lat, lon = SPANISH_CITIES[city]
        lat += random.uniform(-0.1, 0.1)
        lon += random.uniform(-0.1, 0.1)

        device_type = random.choice(DEVICE_TYPES) if channel in ["APP", "WEB"] else channel
        device_id = f"DEV-{uuid.uuid4().hex[:12]}" if channel in ["APP", "WEB"] else None
        ip_address = self.fake.ipv4() if channel in ["APP", "WEB"] else None
        vpn_detected = random.random() < 0.02 if ip_address else False

        # Status
        status = random.choices(STATUSES, weights=[0.02, 0.03, 0.90, 0.03, 0.02])[0]

        # Risk scoring
        risk_score = self._calculate_transaction_risk(
            amount=amount,
            merchant_country=merchant_country,
            mcc_risk=mcc_info["risk"],
            customer_risk=risk_category,
            is_pep=is_pep,
            vpn_detected=vpn_detected,
        )

        risk_signals = self._get_risk_signals(
            amount=amount,
            merchant_country=merchant_country,
            mcc_risk=mcc_info["risk"],
            vpn_detected=vpn_detected,
            risk_score=risk_score,
        )

        # AML flags
        structuring_suspected = amount > 2500 and amount < 3100 and random.random() < 0.1
        velocity_breach = random.random() < 0.02
        geographic_risk = merchant_country in HIGH_RISK_COUNTRIES
        behavioral_anomaly = risk_score > 70 and random.random() < 0.3

        return {
            # Identification
            "transaction_id": transaction_id,
            "external_reference": f"REF-{random.randint(100000000, 999999999)}",
            "parent_transaction_id": None,
            # Originator
            "originator_customer_id": customer_id,
            "originator_account_id": account_iban,
            "originator_account_iban": account_iban,
            "originator_name": customer_name,
            # Beneficiary
            "beneficiary_customer_id": None,
            "beneficiary_account_iban": benef_iban,
            "beneficiary_bank_bic": benef_bank_bic,
            "beneficiary_bank_name": None,
            "beneficiary_bank_country": benef_country,
            "beneficiary_name": benef_name,
            "beneficiary_address": None,
            # Amount
            "amount_value": amount,
            "amount_currency": currency,
            "amount_original_value": amount,
            "amount_original_currency": currency,
            "amount_exchange_rate": 1.0,
            # Timing
            "initiated_at": initiated_at,
            "authorized_at": authorized_at,
            "executed_at": executed_at,
            "settled_at": settled_at,
            "value_date": executed_at.date(),
            # Classification
            "transaction_type": tx_type,
            "direction": direction,
            "channel": channel,
            "payment_method": random.choice(PAYMENT_METHODS),
            "merchant_category_code": mcc,
            "merchant_name": merchant_name,
            "merchant_country": merchant_country,
            # Description
            "concept": self._generate_concept(tx_type, merchant_name),
            "structured_concept": None,
            "reference_number": f"REF{random.randint(100000, 999999)}",
            # Location
            "ip_address": ip_address,
            "device_id": device_id,
            "device_type": device_type,
            "geo_latitude": lat,
            "geo_longitude": lon,
            "geo_city": city,
            "geo_country": "ESP",
            "geo_accuracy_meters": random.randint(5, 100),
            "vpn_detected": vpn_detected,
            # Status
            "current_status": status,
            "status_reason": None if status == "EXECUTED" else "Processing",
            "failure_code": f"ERR{random.randint(100, 999)}" if status == "FAILED" else None,
            "failure_description": "Insufficient funds" if status == "FAILED" else None,
            # Risk assessment
            "risk_score": risk_score,
            "risk_signals": risk_signals,
            "rule_triggers": [],
            "ml_score": risk_score / 100 + random.uniform(-0.1, 0.1),
            "manual_review_required": risk_score > 70,
            # AML flags
            "structuring_suspected": structuring_suspected,
            "velocity_breach": velocity_breach,
            "geographic_risk": geographic_risk,
            "behavioral_anomaly": behavioral_anomaly,
            "pep_involved": is_pep,
            "sanctions_risk": merchant_country in HIGH_RISK_COUNTRIES,
            # Regulatory
            "travel_rule_applicable": amount > 1000 and direction == "OUTBOUND",
            "travel_rule_data_complete": True,
            "dac7_reportable": False,
            "fatca_reportable": merchant_country == "USA",
            "crs_reportable": merchant_country not in ["ESP"],
            # Metadata
            "created_at": initiated_at,
            "processing_time_ms": random.randint(50, 5000),
            "authorization_code": f"AUTH{random.randint(100000, 999999)}",
            "batch_id": None,
            "is_test": False,
        }

    def _calculate_transaction_risk(
        self,
        amount: float,
        merchant_country: str | None,
        mcc_risk: str,
        customer_risk: str,
        is_pep: bool,
        vpn_detected: bool,
    ) -> int:
        """Calculate transaction risk score."""
        score = 10

        # Amount risk
        if amount > 10000:
            score += 25
        elif amount > 5000:
            score += 15
        elif amount > 3000:
            score += 10

        # Country risk
        if merchant_country in HIGH_RISK_COUNTRIES:
            score += 30
        elif merchant_country in MEDIUM_RISK_COUNTRIES:
            score += 15

        # MCC risk
        if mcc_risk == "high":
            score += 20
        elif mcc_risk == "medium":
            score += 10

        # Customer risk
        if customer_risk == "HIGH":
            score += 15
        elif customer_risk == "MEDIUM":
            score += 5

        # PEP
        if is_pep:
            score += 20

        # VPN
        if vpn_detected:
            score += 15

        # Randomness
        score += random.randint(-5, 5)

        return max(0, min(100, score))

    def _get_risk_signals(
        self,
        amount: float,
        merchant_country: str | None,
        mcc_risk: str,
        vpn_detected: bool,
        risk_score: int,
    ) -> list[str]:
        """Get risk signals for transaction."""
        signals = []

        if amount > 10000:
            signals.append("HIGH_AMOUNT")
        if merchant_country in HIGH_RISK_COUNTRIES:
            signals.append("HIGH_RISK_COUNTRY")
        if mcc_risk == "high":
            signals.append("HIGH_RISK_MCC")
        if vpn_detected:
            signals.append("VPN_DETECTED")
        if risk_score > 70:
            signals.append("ELEVATED_RISK_SCORE")

        return signals

    def _generate_concept(self, tx_type: str, merchant_name: str | None) -> str:
        """Generate transaction concept."""
        if merchant_name:
            return f"Compra en {merchant_name}"
        elif tx_type == "TRANSFER":
            return random.choice([
                "Transferencia",
                "Pago alquiler",
                "Nomina",
                "Devolucion",
                "Regalo",
                "Prestamo personal",
            ])
        elif tx_type == "WITHDRAWAL":
            return "Retirada efectivo"
        elif tx_type == "DEPOSIT":
            return random.choice(["Ingreso efectivo", "Nomina", "Transferencia recibida"])
        else:
            return "Operacion"

    def generate_transactions(
        self,
        customers_df: pd.DataFrame,
        count: int = 100000,
    ) -> pd.DataFrame:
        """Generate transactions for given customers."""
        transactions = []

        # Sample customers with weight based on their expected transaction count
        customer_weights = customers_df["expected_transaction_count"].values
        customer_weights = customer_weights / customer_weights.sum()

        for i in range(count):
            # Select a customer
            customer_idx = random.choices(range(len(customers_df)), weights=customer_weights)[0]
            customer = customers_df.iloc[customer_idx]

            # Parse expected_countries if it's a string
            expected_countries = customer["expected_countries"]
            if isinstance(expected_countries, str):
                expected_countries = expected_countries.split(",")

            tx = self.generate_transaction(
                customer_id=customer["customer_id"],
                account_iban=customer["account_id"],
                customer_name=f"{customer['first_name']} {customer['last_name']}",
                expected_monthly_expenses=customer["expected_monthly_expenses"],
                expected_countries=expected_countries,
                risk_category=customer["risk_category"],
                is_pep=customer["is_pep"],
                transaction_index=i,
            )
            transactions.append(tx)

        df = pd.DataFrame(transactions)

        # Convert list columns to string
        list_columns = ["risk_signals", "rule_triggers"]
        for col in list_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: ",".join(x) if isinstance(x, list) else x)

        return df
