# Data Field Standardization Guide

This document defines the standard field names to be used across all data collection and crawling operations in the OpenData project. Consistent field naming is essential for data integration, analysis, and maintenance.

## Core Metadata Fields

These fields should be included in all datasets to provide essential context:

| Field Name     | Data Type      | Description                              | Example                               |
| -------------- | -------------- | ---------------------------------------- | ------------------------------------- |
| `id`           | String/Integer | Unique identifier for each record        | `"123"`, `42`                         |
| `source_name`  | String         | Name of the data source                  | `"MEXT Enrollment Statistics"`        |
| `source_url`   | String         | Original URL where the data was obtained | `"https://example.gov/data"`          |
| `event_time`   | DateTime       | When the data was collected (ISO format) | `"2025-05-21T14:30:00Z"`              |
| `country_code` | String         | ISO 3166-1 alpha-2 country code          | `"JP"`, `"US"`                        |
| `topic`        | String         | Primary topic category of the data       | `"education"`, `"healthcare"`         |
| `language`     | String         | ISO 639-1 language code of the content   | `"en"`, `"ja"`                        |
| `status`       | String         | Processing status of the record          | `"active"`, `"archived"`, `"pending"` |

## Location Information

Fields for standardizing geographic data:

| Field Name        | Data Type | Description                                        | Example                               |
| ----------------- | --------- | -------------------------------------------------- | ------------------------------------- |
| `location_name`   | String    | Name of location                                   | `"Tokyo"`                             |
| `location_type`   | String    | Type of location                                   | `"city"`, `"prefecture"`, `"state"`   |
| `latitude`        | Float     | Latitude coordinate                                | `35.6762`                             |
| `longitude`       | Float     | Longitude coordinate                               | `139.6503`                            |
| `region`          | String    | Region or state/province                           | `"Kanto"`                             |
| `postal_code`     | String    | Postal/ZIP code                                    | `"100-0001"`                          |
| `address`         | String    | Full address                                       | `"1-1 Example Street, Tokyo"`         |
| `meeting_address` | String    | Specific address where a meeting/event takes place | `"Conference Room A, Tokyo Building"` |

## Contact Information

Fields for standardizing contact details:

| Field Name     | Data Type | Description                                           | Example                       |
| -------------- | --------- | ----------------------------------------------------- | ----------------------------- |
| `contact_name` | String    | Name of contact person or department                  | `"Information Office"`        |
| `phone`        | String    | Phone number with country code                        | `"+81-3-1234-5678"`           |
| `email`        | String    | Email address                                         | `"contact@example.org"`       |
| `website`      | String    | Website URL                                           | `"https://example.org"`       |
| `lecturer`     | String    | Name of person conducting a lecture/presentation      | `"Prof. Yamada Taro"`         |
| `organizer`    | String    | Person or organization responsible for event/activity | `"Tokyo Science Association"` |

## Temporal Data

Fields for time-based information:

| Field Name         | Data Type | Description                               | Example                            |
| ------------------ | --------- | ----------------------------------------- | ---------------------------------- |
| `date`             | Date      | Simple date (YYYY-MM-DD)                  | `"2025-05-21"`                     |
| `start_datetime`   | DateTime  | Start time of an event (ISO format)       | `"2025-05-21T09:00:00"`            |
| `end_datetime`     | DateTime  | End time of an event (ISO format)         | `"2025-05-21T17:00:00"`            |
| `duration_minutes` | Integer   | Duration in minutes                       | `480`                              |
| `time_zone`        | String    | Time zone identifier                      | `"Asia/Tokyo"`                     |
| `frequency`        | String    | How often data is updated or event occurs | `"daily"`, `"weekly"`, `"monthly"` |
| `year`             | Integer   | Year of the data                          | `2025`                             |
| `month`            | Integer   | Month of the data                         | `5`                                |
| `day`              | Integer   | Day of the month                          | `21`                               |

## Categorical Data

Fields for categorization:

| Field Name    | Data Type        | Description           | Example                                     |
| ------------- | ---------------- | --------------------- | ------------------------------------------- |
| `category`    | String           | Primary category      | `"Computers"`                               |
| `subcategory` | String           | Secondary category    | `"Laptops"`                                 |
| `tags`        | Array of Strings | List of relevant tags | `["education", "statistics", "enrollment"]` |
| `type`        | String           | Type of the content   | `"article"`, `"data sheet"`, `"report"`     |

## Content Data

Fields for the actual content:

| Field Name        | Data Type | Description                   | Example                                     |
| ----------------- | --------- | ----------------------------- | ------------------------------------------- |
| `title`           | String    | Title of the content          | `"Annual Education Report"`                 |
| `name`            | String    | Name of the item              | `"Asus VivoBook X441NA"`                    |
| `description`     | String    | Detailed description          | `"Detailed statistical analysis of..."`     |
| `summary`         | String    | Brief summary of the content  | `"Overview of enrollment trends"`           |
| `content`         | String    | Full content text             | `"The complete article text..."`            |
| `image_url`       | String    | URL to associated image       | `"https://example.org/images/chart.png"`    |
| `file_url`        | String    | URL to associated file        | `"https://example.org/files/data.xlsx"`     |
| `target_audience` | String    | Intended audience for content | `"High school teachers and administrators"` |

## Numerical Data

Fields for numeric information:

| Field Name   | Data Type | Description                    | Example          |
| ------------ | --------- | ------------------------------ | ---------------- |
| `amount`     | Float     | Generic monetary amount        | `19.99`          |
| `price`      | Float     | Price in the original currency | `1250.00`        |
| `currency`   | String    | Currency code (ISO 4217)       | `"JPY"`, `"USD"` |
| `quantity`   | Integer   | Count or quantity              | `42`             |
| `percentage` | Float     | Percentage value               | `85.5`           |
| `rate`       | Float     | Rate of something              | `0.75`           |
| `unit`       | String    | Unit of measurement            | `"kg"`, `"m²"`   |
| `value`      | Float     | Generic numerical value        | `123.45`         |

## Education-Specific Fields

Fields specific to education data:

| Field Name         | Data Type | Description                       | Example                                  |
| ------------------ | --------- | --------------------------------- | ---------------------------------------- |
| `institution_name` | String    | Name of educational institution   | `"Tokyo University"`                     |
| `institution_type` | String    | Type of institution               | `"university"`, `"high school"`          |
| `enrollment_count` | Integer   | Number of enrolled students       | `12500`                                  |
| `graduation_rate`  | Float     | Percentage of graduating students | `92.7`                                   |
| `course_name`      | String    | Name of course                    | `"Advanced Mathematics"`                 |
| `academic_year`    | String    | Academic year                     | `"2024-2025"`                            |
| `education_level`  | String    | Level of education                | `"primary"`, `"secondary"`, `"tertiary"` |

## Event-Specific Fields

Fields specific to event data:

| Field Name           | Data Type | Description                              | Example                                |
| -------------------- | --------- | ---------------------------------------- | -------------------------------------- |
| `event_name`         | String    | Name of the event                        | `"Science Fair 2025"`                  |
| `event_type`         | String    | Type of event                            | `"conference"`, `"workshop"`           |
| `venue`              | String    | Location where event is held             | `"Tokyo International Forum"`          |
| `organizer`          | String    | Entity organizing the event              | `"Science Association"`                |
| `capacity`           | Integer   | Maximum number of attendees              | `500`                                  |
| `registration_url`   | String    | URL for event registration               | `"https://example.org/register"`       |
| `cost`               | Float     | Cost to attend                           | `1000.00`                              |
| `price`              | Float     | Price of ticket/entry (synonym for cost) | `5000.00`                              |
| `participant_limit`  | Integer   | Maximum number of participants allowed   | `100`                                  |
| `application_method` | String    | How to apply for the event               | `"Apply via website or call directly"` |
| `target_audience`    | String    | Target audience or participants          | `"Parents with children ages 5-12"`    |

## Technical Fields

Fields for technical metadata:

| Field Name         | Data Type | Description                  | Example                              |
| ------------------ | --------- | ---------------------------- | ------------------------------------ |
| `version`          | String    | Version of the data          | `"1.2.0"`                            |
| `format`           | String    | Format of the data           | `"CSV"`, `"JSON"`, `"XML"`           |
| `license`          | String    | License for the data         | `"CC-BY-4.0"`                        |
| `data_quality`     | String    | Indicator of data quality    | `"verified"`, `"raw"`                |
| `processing_level` | String    | Level of processing applied  | `"raw"`, `"cleaned"`, `"aggregated"` |
| `hash`             | String    | Hash of the original content | `"a1b2c3d4..."`                      |

## Usage Guidelines

1. Always use the standardized field names from this document
2. If a new field is needed, follow the naming conventions and update this document
3. For complex data types, use nested JSON objects
4. For arrays or lists, use plural names (e.g., `tags`, `categories`)
5. Use ISO standard formats for dates, countries, languages and currencies
6. Maintain consistency in casing (use snake_case for all field names)

## Implementation Examples

### JSON Example

```json
{
  "id": "edu-jp-2025-001",
  "source_name": "MEXT Enrollment Statistics",
  "source_url": "https://www.mext.go.jp/en/publication/statistics/title01/detail01/1373636.htm",
  "event_time": "2025-05-21T08:30:00Z",
  "country_code": "JP",
  "topic": "education",
  "language": "en",
  "status": "active",
  "title": "University Enrollment Statistics 2025",
  "year": 2025,
  "education_level": "tertiary",
  "enrollment_count": 2750000,
  "processing_level": "verified",
  "lecturer": "Prof. Yamada Taro",
  "meeting_address": "University Conference Hall, 3F",
  "organizer": "Ministry of Education",
  "price": 0,
  "participant_limit": 200,
  "application_method": "Registration required on the website",
  "target_audience": "University administrators and education researchers"
}
```

### CSV Headers Example

```
id,source_name,source_url,event_time,country_code,topic,language,status,meeting_address,lecturer,organizer,price,participant_limit,application_method,target_audience
```
