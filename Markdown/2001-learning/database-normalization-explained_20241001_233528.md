# Database Normalization Explained

## Understanding Database Normalization

Database normalization is the process of organizing data in a relational database to minimize redundancy and improve data integrity. It involves dividing large tables into smaller ones and defining relationships among them. The goal is to ensure that the data remains consistent, accurate, and not duplicated across the database.

### Why Normalize?

1. **Eliminates Redundancy**: Avoids storage of duplicate data.
2. **Enhances Data Integrity**: Helps in maintaining accuracy over time, as changes in data are made in a single place.
3. **Reduces Insertion, Update, and Deletion Anomalies**: Protects against issues that arise when inserting or changing records.

### The Normal Forms

Normalization is structured into several "normal forms" (NF), each with specific criteria.

#### First Normal Form (1NF)

A table is in 1NF if:
- Each column must contain atomic (indivisible) values.
- Each record must be unique, meaning it should have a primary key.
- There should not be any repeating groups.

**Example of violation**:
| Player_ID | Item_Type      | Item_Quantity |
|-----------|----------------|---------------|
| trev73    | arrows, shields| 10            |  

In the above table, the `Item_Type` column is not atomic since it contains multiple values.

**Corrected Version**:
| Player_ID | Item_Type | Item_Quantity |
|-----------|-----------|---------------|
| trev73    | arrows    | 10            |
| trev73    | shields   | 5             |

#### Second Normal Form (2NF)

A table is in 2NF if:
- It is in 1NF.
- All non-key attributes are fully functional dependent on the primary key; no partial dependencies are allowed.

**Example of violation**:
| Player_ID | Item_Type | Item_Quantity | Player_Rating |
|-----------|-----------|---------------|----------------|
| trev73    | arrows    | 10            | Advanced       |
| trev73    | shields   | 5             | Advanced       |

The `Player_Rating` is dependent just on `Player_ID`, leading to a partial dependency.

**Corrected Version**:
- Player Table:
| Player_ID | Player_Rating |
|-----------|----------------|
| trev73    | Advanced       |

- Inventory Table:
| Player_ID | Item_Type | Item_Quantity |
|-----------|-----------|---------------|
| trev73    | arrows    | 10            |
| trev73    | shields   | 5             |

#### Third Normal Form (3NF)

A table is in 3NF if:
- It is in 2NF.
- There are no transitive dependencies (no non-key attribute depends on another non-key attribute).

**Example of violation**:
| Player_ID | Player_Rating | Skill_Level |
|-----------|----------------|-------------|
| trev73    | Advanced       | 8           |

`Player_Rating` depends on `Skill_Level`, violating 3NF.

**Corrected Version**:
- Separate `Player_Rating` into a new table:
| Skill_Level | Player_Rating |
|-------------|----------------|
| 8           | Advanced       |

- Player Table remains the same:
| Player_ID | Skill_Level |
|-----------|-------------|
| trev73    | 8           |

#### Fourth Normal Form (4NF)

A table is in 4NF if:
- It is in 3NF.
- There are no multi-valued dependencies (independent multivalued facts cannot coexist without redundancy).

**Example of violation**:
| Model   | Color   | Style   |
|---------|---------|---------|
| Prairie | Brown   | Bungalow|
| Prairie | Brown   | Schoolhouse|

Adding a new color can lead to inconsistencies in style.

**Corrected Version**:
- Instead, separate the colors and styles:
| Model   | Color   |
|---------|---------|
| Prairie | Brown   |
| Prairie | Green   |

| Model   | Style     |
|---------|-----------|
| Prairie | Bungalow  |
| Prairie | Schoolhouse|

#### Fifth Normal Form (5NF)

A table is in 5NF if:
- It is in 4NF.
- Every non-trivial join dependency is a consequence of the candidate keys.

**Example of violation**:
Storing data that can be derived from joins between separate tables is not in 5NF.

**Corrected Version**:
Split the tables into the smallest logical parts where you can join them when needed.

### Summary of Normal Forms
1. **1NF**: Atomic values, unique records.
2. **2NF**: No partial dependencies.
3. **3NF**: No transitive dependencies.
4. **4NF**: No multi-valued dependencies.
5. **5NF**: No join dependencies.

### Sample Questions

1. Explain the importance of defining a primary key in a relational database.
2. Why is it necessary to avoid partial dependencies in the Second Normal Form?
3. What problems could arise from not implementing Third Normal Form in database design?
4. Can a table be in 3NF but not in BCNF (Boyce-Codd Normal Form)? Explain your answer with an example.
5. Describe a scenario where Fourth Normal Form is necessary.

For more in-depth understanding, you may also consider watching this video: [Database Normalization](https://youtu.be/GFQaEYEc8_8?si=dI6J3NaJMmbDQtMm).

---

Feel free to explore these concepts further, and let me know if you have any questions or need more examples!

---

[Link to Video](https://youtu.be/GFQaEYEc8_8?si=dI6J3NaJMmbDQtMm)