# Annotation guidelines: legal area of an act

Each act gets **exactly one** of the ten labels below. Annotators A (Member 1) and B
(Member 2) work independently and must not discuss individual acts until `agree` has
been run. Member 3 adjudicates the disagreements.

## How to decide

1. Read the title and the first articles (usually *Predmet zakona* / *Predmet uređivanja*,
   i.e. what the act regulates). Open the URL if the preview is not enough.
2. Label the **subject matter the act regulates**, not the body that issues it.
   A tax rulebook issued by the Ministry of Finance and a tax rulebook issued by the
   government are both `finance_tax`.
3. **Amendments** (*Zakon o izmjenama i dopunama…*) get the label of the act they amend.
4. **Ratifications of international agreements** (*Zakon o potvrđivanju…*,
   *Odluka o ratifikaciji…*) get the label of the agreement's subject (a double-taxation
   treaty is `finance_tax`). Use `politics_international` only when the agreement is about
   diplomatic relations, defence, or membership of an international organisation.
5. If two areas fit equally, choose the one the act's **first substantive articles** are
   about, and write the runner-up in the `note` column.
6. Fill `confidence` with 1 (unsure), 2 (fairly sure) or 3 (sure).
7. Purely personal or administrative decisions (an appointment, a single property transfer)
   should have been filtered out during sampling. If one gets through, label it by its
   subject and write `administrative` in `note`.

## Labels

| Label | Covers (EUROVOC domains) | Typical acts |
|---|---|---|
| `politics_international` | Politics; International relations; European Union; International organisations | elections, parliament, government and ministries, local self-government, civil service, constitution, defence and the army, diplomacy |
| `law_justice` | Law | criminal and misdemeanour law, courts, civil and family law, property, inheritance, enforcement, notaries and lawyers, police, prisons, administrative procedure, citizenship, data protection |
| `economy_trade_business` | Economics; Trade; Business and competition | companies, bankruptcy, competition, public procurement, consumer protection, internal and foreign trade, tourism, crafts, investment, statistics |
| `finance_tax` | Finance | taxes, customs, excise, budget, banks, insurance, securities, accounting and audit, foreign exchange, public debt |
| `social_labour` | Social questions; Employment and working conditions | labour relations, employment, pensions, social welfare, health care and health insurance, veterans, disability, family benefits |
| `education_culture_science` | Education and communications; Science | schools, higher education, research, culture and heritage, media, copyright, sport, electronic communications, archives and libraries |
| `transport` | Transport | road, rail, air and maritime transport, traffic safety, vehicles, ports |
| `environment_energy` | Environment; Energy | environmental and nature protection, waste, water, climate, electricity, gas, oil, renewables |
| `agriculture_food` | Agriculture, forestry and fisheries; Agri-foodstuffs | agriculture, forests, fishing, hunting, veterinary matters, food safety, seeds and plant health |
| `industry_technology` | Production, technology and research; Industry | industry, mining, construction and spatial planning, technical standards, metrology, accreditation, product safety, explosives |

## Notes on borderline cases

- Health care, health insurance and medicines are all `social_labour` (project decision,
  so annotators don't split health acts across areas). Food safety is `agriculture_food`.
- Copyright is in `education_culture_science`, not `law_justice`.
- Spatial planning and construction permits are `industry_technology`.
- Public procurement is `economy_trade_business`; the state budget is `finance_tax`.
