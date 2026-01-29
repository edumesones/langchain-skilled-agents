# Requisitos de Formato SEPBLAC

## Comunicación por Indicio (CPI)

### Estructura XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ComunicacionIndicio>
  <Cabecera>
    <CodigoEntidad>XXXX</CodigoEntidad>
    <TipoComunicacion>INICIAL|COMPLEMENTARIA</TipoComunicacion>
    <FechaComunicacion>YYYY-MM-DD</FechaComunicacion>
    <ReferenciaInterna>REF-XXXXX</ReferenciaInterna>
  </Cabecera>

  <Sujeto>
    <TipoPersona>FISICA|JURIDICA</TipoPersona>
    <Identificacion>
      <TipoDocumento>DNI|NIE|CIF|PASAPORTE</TipoDocumento>
      <NumeroDocumento>XXXXXXXX</NumeroDocumento>
    </Identificacion>
    <DatosPersonales>
      <!-- Campos según tipo de persona -->
    </DatosPersonales>
  </Sujeto>

  <Operaciones>
    <Operacion>
      <Fecha>YYYY-MM-DD</Fecha>
      <Tipo>CODIGO_OPERACION</Tipo>
      <Importe>
        <Cantidad>XXXXX.XX</Cantidad>
        <Divisa>EUR</Divisa>
      </Importe>
      <Descripcion>Texto libre</Descripcion>
    </Operacion>
  </Operaciones>

  <MotivosIndicio>
    <Indicador codigo="XX">Descripción</Indicador>
  </MotivosIndicio>

  <Documentacion>
    <Documento>
      <Tipo>TIPO_DOC</Tipo>
      <Nombre>nombre_archivo.pdf</Nombre>
      <Contenido>BASE64</Contenido>
    </Documento>
  </Documentacion>
</ComunicacionIndicio>
```

### Códigos de Tipo de Operación

| Código | Descripción |
|--------|-------------|
| 01 | Transferencia nacional |
| 02 | Transferencia internacional |
| 03 | Ingreso en efectivo |
| 04 | Retirada en efectivo |
| 05 | Compraventa de valores |
| 06 | Operaciones de cambio |
| 07 | Otros |

### Códigos de Indicador de Sospecha

| Código | Indicador |
|--------|-----------|
| A01 | Operaciones sin justificación económica aparente |
| A02 | Fragmentación de operaciones |
| A03 | Utilización de personas interpuestas |
| A04 | Operaciones con países de riesgo |
| A05 | Inconsistencia con perfil del cliente |
| B01 | Structuring |
| B02 | Layering |
| B03 | Smurfing |
| C01 | Posible financiación del terrorismo |
| C02 | Posible relación con PEP |

## Requisitos Técnicos

### Tamaño Máximo
- Archivo XML: 10 MB
- Adjuntos totales: 50 MB
- Individual adjunto: 10 MB

### Formatos Adjuntos Aceptados
- PDF (preferente)
- JPG/PNG (capturas)
- XLS/XLSX (extractos)

### Codificación
- UTF-8 obligatorio
- Fechas: YYYY-MM-DD
- Importes: Punto decimal, 2 decimales
- Divisa: ISO 4217

## Respuesta SEPBLAC

### Acuse de Recibo
```xml
<AcuseRecibo>
  <Resultado>OK|ERROR</Resultado>
  <CodigoRecepcion>XXXXXX</CodigoRecepcion>
  <FechaRecepcion>YYYY-MM-DDTHH:MM:SS</FechaRecepcion>
  <Errores>
    <Error codigo="XX">Descripción</Error>
  </Errores>
</AcuseRecibo>
```

### Códigos de Error Comunes

| Código | Descripción | Acción |
|--------|-------------|--------|
| E01 | XML mal formado | Revisar estructura |
| E02 | Campo obligatorio vacío | Completar campo |
| E03 | Formato de fecha incorrecto | Usar YYYY-MM-DD |
| E04 | Documento excede tamaño | Reducir/dividir |
| E05 | Codificación incorrecta | Usar UTF-8 |
