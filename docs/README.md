# User Stories

## Product User Stories

As an **NBA Fan,** I want to **select two players from a searchable list** so I can **set up a comparison.**
- **Acceptance Criteria:** The players list loads all active players from the ```/api/players/``` endpoint

As a **Fantasy Basketball Manager,** I want to **view a seperate Head-to-Head stats table** So i can make **data-supported decisions about which players perform better when they face certain opponents.**
- **Acceptance Criteria:** The stats shown are only from games where **both** players where active.

As a **Sports debater,** I want to **view stats from a specific season** So i can **compare a player's stats from different years (rookie season vs. MVP season)**
- **Acceptance Criteria:** The stats tables clearly display which season is being shown.

## Misuser Stories

As an **Attacker,** I want to **Pass malicious input into the parameters** so i can **corrupt the database**
- **Mitigation Criteria:** The backend validates all incoming parameters
 
As a **Malicious User,** I want to **spam the "Compare" button** so I can **trigger a DoS by overloading the backend**
- **Mitigation Criteria:** The Compare button is disabled after being clicked, preventing multiple submissions
