# Data Normalization Explained Simply

Certainly! Let’s delve deeper into the differences between unnormalized data, normalized data, and each of the normal forms (1NF, 2NF, 3NF). This will provide you with a clear understanding of how data organization evolves through the normalization process.

### Unnormalized Data

**Definition**: Unnormalized data refers to a raw database table format that has not gone through the normalization process. This format often contains duplicate data and non-atomic values, making it prone to inconsistencies and anomalies.

**Characteristics**:
- **Redundancy**: Same information may appear multiple times.
- **Non-atomic values**: Columns can hold multiple values.
- **No primary key**: Every record may not be uniquely identifiable.

**Example**:
| Player_ID | Items                     |
|-----------|---------------------------|
| trev73    | arrows, shields, coins     |
| trev74    | arrows, potions           |

### Normalized Data

**Definition**: Normalized data is structured data that has gone through normalization to organize it efficiently, causing the minimization of redundancy and maximizing integrity.

**Characteristics**:
- **No redundancy**: Each piece of data is stored only once.
- **Atomic values**: Each column holds only a single value.
- **Defined primary key**: Each record is uniquely identifiable.

**Example**:
| Player_ID | Item_Type | Item_Quantity |
|-----------|-----------|---------------|
| trev73    | arrows    | 10            |
| trev73    | shields   | 5             |
| trev74    | arrows    | 7             |
| trev74    | potions   | 3             |

### First Normal Form (1NF)

**Definition**: A table is in 1NF if it meets the criteria of having only atomic values, unique records, and no repeating groups.

**Key Differences from Unnormalized Data**:
- **Eliminates repeating groups**: All items are stored as separate records.
- **Ensures atomicity**: Each column value is singular and not a list.

**Example** (transformed to 1NF):
| Player_ID | Item_Type | Item_Quantity |
|-----------|-----------|---------------|
| trev73    | arrows    | 10            |
| trev73    | shields   | 5             |
| trev74    | arrows    | 7             |
| trev74    | potions   | 3             |

### Second Normal Form (2NF)

**Definition**: A table is in 2NF if it is already in 1NF and all non-key attributes are fully functionally dependent on the primary key—meaning there are no partial dependencies.

**Key Differences from 1NF**:
- **Eliminates partial dependencies**: All non-key attributes relate to the full primary key and not just part of it.

**Example** (moving to 2NF):
- Initial 1NF:
| Player_ID | Item_Type | Item_Quantity | Player_Rating |
|-----------|-----------|---------------|----------------|
| trev73    | arrows    | 10            | Advanced       |
| trev73    | shields   | 5             | Advanced       |
- **Split into separate tables**:
    - **Player Table**:
    | Player_ID | Player_Rating |
    |-----------|----------------|
    | trev73    | Advanced       |
    | trev74    | Intermediate    |

    - **Inventory Table**:
    | Player_ID | Item_Type | Item_Quantity |
    |-----------|-----------|---------------|
    | trev73    | arrows    | 10            |
    | trev73    | shields   | 5             |
    | trev74    | arrows    | 7             |
    | trev74    | potions   | 3             |

### Third Normal Form (3NF)

**Definition**: A table is in 3NF if it is in 2NF and there are no transitive dependencies among non-key attributes, meaning every non-key attribute is directly dependent only on the primary key.

**Key Differences from 2NF**:
- **Eliminates transitive dependencies**: Non-key attributes do not depend on other non-key attributes.

**Example** (moving to 3NF):
- **Initial 2NF** (with transitive dependency):
| Player_ID | Player_Rating | Player_Skill_Level |
|-----------|----------------|---------------------|
| trev73    | Advanced       | 8                   |
| trev74    | Intermediate    | 5                   |
- **Separation into distinct tables**:
    - **Player Table**:
    | Player_ID | Player_Rating |
    |-----------|----------------|
    | trev73    | Advanced       |
    | trev74    | Intermediate    |

    - **Skill Table**:
    | Player_ID | Player_Skill_Level |
    |-----------|---------------------|
    | trev73    | 8                   |
    | trev74    | 5                   |

### Summary of Differences

| Feature                   | Unnormalized             | Normalized                | 1NF                        | 2NF                         | 3NF                         |
|---------------------------|--------------------------|---------------------------|----------------------------|-----------------------------|-----------------------------|
| Redundancy                | High                     | Low                       | Moderate                   | Low                         | Very Low                    |
| Atomic Values             | No                       | Yes                       | Yes                        | Yes                         | Yes                         |
| Primary Key               | None                     | Defined                   | Defined                    | Defined                     | Defined                     |
| Repeating Groups           | Yes                      | No                        | No                         | No                          | No                          |
| Partial Dependencies       | Possible                 | None                      | Possible                   | None                        | None                        |
| Transitive Dependencies     | Possible                 | None                      | None                       | Possible                    | None                        |

Understanding the distinctions between these states will help you appreciate the significance of normalization in maintaining data integrity and efficiency in relational databases. Normalize your data to avoid anomalies and enhance query performance!

If you need to dive deeper or focus on specific aspects, let me know!

---

[Link to Video](https://youtu.be/GFQaEYEc8_8?si=dI6J3NaJMmbDQtMm)