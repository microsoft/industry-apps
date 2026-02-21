# Field Templates

This directory stores saved field definition templates for the Field Creator tool.

## Template Format

Templates are stored as JSON files with the following structure:

```json
{
  "name": "Template Name",
  "description": "Optional description",
  "publisherPrefix": "appbase_",
  "fields": [
    {
      "displayName": "Field Display Name",
      "type": "Text",
      "required": false,
      "maxLength": 100
    }
  ]
}
```

## Usage

Templates are managed through the Field Creator UI:
- **Save**: Create a new template from currently defined fields
- **Load**: Populate field definitions from a saved template
- **Delete**: Remove a template (cannot be undone)

## Field Types

Supported field types:
- Text, Memo, RichText, URL
- Integer, Float, Currency
- Date, DateTime, YesNo

## Notes

- Templates are stored per filename (name is sanitized)
- Publisher prefix is saved with the template for reuse
- Schema names are auto-generated when loading templates
