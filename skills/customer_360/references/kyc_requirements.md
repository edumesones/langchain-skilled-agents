# Requisitos KYC - Ley 10/2010

## Marco Normativo

Este documento detalla los requisitos de Know Your Customer (KYC) según la Ley 10/2010 de prevención del blanqueo de capitales y de la financiación del terrorismo, y su Reglamento de desarrollo (RD 304/2014).

## Niveles de Diligencia

### Diligencia Debida Simplificada (Art. 9)

**Aplicable a clientes de bajo riesgo:**
- Administraciones públicas
- Entidades financieras supervisadas UE
- Sociedades cotizadas

**Datos mínimos:**
- Identificación formal
- Propósito de la relación

### Diligencia Debida Estándar (Art. 3-6)

**Datos de Identificación Obligatorios:**

| Campo | Personas Físicas | Personas Jurídicas |
|-------|------------------|-------------------|
| Nombre completo | ✅ | ✅ (denominación social) |
| NIF/NIE/Pasaporte | ✅ | ✅ (CIF) |
| Fecha de nacimiento | ✅ | N/A |
| Nacionalidad | ✅ | País de constitución |
| Domicilio | ✅ | Domicilio social |
| Actividad profesional | ✅ | Objeto social |
| Titular real | N/A | ✅ (>25% participación) |

**Documentación Requerida:**

Para personas físicas:
- DNI/NIE/Pasaporte vigente
- Justificante de domicilio (<3 meses)
- Justificante de actividad económica

Para personas jurídicas:
- Escritura de constitución
- Poderes de representación
- Estructura de titularidad real
- Últimas cuentas anuales

### Diligencia Debida Reforzada (Art. 11)

**Obligatoria para:**
- PEPs y familiares/asociados cercanos
- Clientes de países de alto riesgo (lista UE)
- Operaciones inusuales o complejas
- Banca privada y altos patrimonios
- Corresponsalía bancaria con terceros países

**Medidas adicionales:**
- Aprobación de alta dirección para establecer relación
- Verificación reforzada de origen de fondos
- Seguimiento reforzado de la relación
- Actualización KYC más frecuente

## Campos KYC por Categoría

### Identificación Personal (OBLIGATORIO)

```json
{
  "first_name": "string - requerido",
  "last_name": "string - requerido",
  "second_last_name": "string - opcional (España)",
  "date_of_birth": "date - requerido",
  "nationality": "string ISO 3166 - requerido",
  "document_type": "enum [DNI, NIE, PASSPORT] - requerido",
  "document_number": "string - requerido",
  "document_expiry": "date - requerido",
  "document_country": "string ISO 3166 - requerido"
}
```

### Datos de Contacto (OBLIGATORIO)

```json
{
  "email": "string - requerido",
  "phone": "string - requerido",
  "address_line_1": "string - requerido",
  "city": "string - requerido",
  "postal_code": "string - requerido",
  "country": "string ISO 3166 - requerido"
}
```

### Información Económica (OBLIGATORIO)

```json
{
  "employment_status": "enum - requerido",
  "employer_name": "string - si empleado",
  "employer_sector": "string CNAE - si empleado",
  "annual_income": "number - requerido",
  "income_source": "enum - requerido",
  "expected_activity": {
    "monthly_income": "number - requerido",
    "monthly_expenses": "number - requerido",
    "transaction_frequency": "number - requerido"
  }
}
```

### PEP Status (OBLIGATORIO verificar)

```json
{
  "is_pep": "boolean - requerido",
  "pep_category": "enum [NATIONAL, FOREIGN, INTL_ORG] - si PEP",
  "pep_position": "string - si PEP",
  "is_pep_family": "boolean - requerido",
  "is_pep_associate": "boolean - requerido"
}
```

### Propósito de la Relación (OBLIGATORIO)

```json
{
  "relationship_purpose": "string - requerido",
  "expected_products": "array[string] - requerido",
  "expected_countries": "array[string] - requerido",
  "funds_origin": "string - requerido"
}
```

## Verificación de Datos

### Métodos Aceptados

| Dato | Método de Verificación | Validez |
|------|------------------------|---------|
| Identidad | Documento oficial | Hasta caducidad |
| Domicilio | Factura servicios / Padrón | 3 meses |
| Ingresos | Nóminas / IRPF | 12 meses |
| Empresa | Registro Mercantil | 6 meses |
| Titularidad real | Declaración + comprobación | 12 meses |

### Verificación Digital (Art. 12)

Permitida mediante:
- Videoidentificación con requisitos técnicos
- Certificado electrónico cualificado
- Otros medios seguros autorizados por SEPBLAC

## Frecuencia de Actualización

| Nivel de Riesgo | Frecuencia Mínima |
|-----------------|-------------------|
| Bajo | Cada 5 años |
| Medio | Cada 2 años |
| Alto | Anual |
| PEP | Cada 6 meses |

## Indicadores de Alerta KYC

- Reticencia a proporcionar información
- Documentos de dudosa autenticidad
- Inconsistencias en la información
- Cambios frecuentes de datos
- Domicilio en país de alto riesgo
- Sector económico de alto riesgo
- Estructura societaria compleja
- Titularidad real no clara

## Sanciones por Incumplimiento

| Tipo | Sanción |
|------|---------|
| Leve | Hasta 60,000 EUR |
| Grave | 60,001 - 150,000 EUR |
| Muy grave | 150,001 - 10,000,000 EUR |

Además de sanciones económicas, pueden imponerse:
- Amonestación pública
- Suspensión temporal de actividad
- Revocación de autorización
